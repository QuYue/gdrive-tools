# -*- encoding: utf-8 -*-
'''
@Time     :   2025/11/18 17:26:53
@Author   :   QuYue
@File     :   core.py
@Email    :   quyue1541@gmail.com
@Desc:    :   core
'''

#%% Import Packages
# Basic
import os
import sys
import io
import logging
import socket
import yaml
import socks
import httplib2

# Google API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Self-defined
from .utils import AttrDict, human_size


#%% GoogleDriveTools
class GoogleDriveTools:
    """
    High-level wrapper around Google Drive API for uploading and downloading
    files using settings.yaml and optional proxy.
    """

    def __init__(self, settings_path: str | None = None, *,
        # Manual override parameters:
        cred_file=None,
        proxy=None,
        remote=None,
        log=None,
        show_settings: bool = False):
        """
        Initialize GoogleDriveTools.

        Parameters
        ----------
        settings_path : str | None
            Path to settings.yaml file. If None, use default settings and 'cred_file' must be provided.

        Manual override parameters (optional)
        ------------------------------------
        cred_file : str | None 
            Google API credentials file (get it from Google Cloud Console). If setting_path is None, must be provided here.
            cred_file = None (use setting.google_drive.credentials_file) |  str (override setting.google_drive.credentials_file)
        proxy : str | None  
            Proxy server for HTTP requests.
            proxy = None (use setting.proxy) | "off" (direct connection) | other string (override setting.proxy).
            e.g., "http://127.0.0.1:1080", "socks4://127.0.0.1:1080", "socks5://127.0.0.1:1080".
        remote : bool | None
            Whether to use remote OAuth authentication (manual URL copy) instead of local server. If None, use setting.google_drive.remote.
        log : str | None   
            Log file path.
            log = None (use setting.log) | "off" (use stdout) | other string (override setting.log).
            e.g., "log.txt"
        show_settings : bool
            Whether to print loaded settings to console. Default: False.
        """
        if show_settings:
            print("========== Google Drive Tools CLI ==========")

        # ---------- Step 1. Load settings ----------
        if settings_path is not None:
            self.settings = self.load_settings(settings_path, inplaces=False)
            if show_settings:
                print(f"===== settings: {settings_path}")
        else:
            # No settings.yaml → create an empty config structure
            self.settings = AttrDict({
                    "google_drive": AttrDict({
                        "credentials_file": None,
                        "save_token": True,
                        "save_token_file": './Json/token.json',
                        "remote": False,
                        "oauth_scope": ["https://www.googleapis.com/auth/drive.file"]
                    }),
                    "proxy": None,
                    "log": None,
                    "upload": AttrDict({
                        "local_file": None,
                        "save_file_name": None,
                        "save_folder_id": None,
                        "chunksize": 10485760,  # 10 MB
                    }),
                    "download": AttrDict({
                        "save_local_dir": './download',
                        "file_id": None,    
                        "chunksize": 10485760,  # 10 MB 
                    })
                })
            if show_settings:
                print("settings: off (without settings yaml file)")
        
        
        # ---------- Step 2. Apply manual overrides ----------
        if cred_file is not None:
            self.settings.google_drive.credentials_file = cred_file
        if show_settings:
            print('===== cred_file:', self.settings.google_drive.credentials_file)
        if proxy is not None:
            # proxy = None (use setting.proxy) | "off" (override to direct connection) |  else override by proxy
            if proxy.lower() == "off":
                proxy = None
            self.settings.proxy = proxy
        if show_settings:
            if self.settings.proxy is None:
                print('===== proxy: off (direct connection)')
            else:
                print('===== proxy:', self.settings.proxy)
        if remote is not None:
            self.settings.google_drive.remote = remote
        if log is not None:
            # log = None (use setting.log) | "off" (override to stdout) |  else override by log_file
            if log.lower() == "off":
                log = None
            self.settings.log = log
        if show_settings:
            if self.settings.log is None:
                print('===== log: off (stdout)')
            else:
                print('===== log:', self.settings.log)
        self.logger = self.set_logger(self.settings.log, inplaces=False)
        # check
        if self.settings.google_drive.credentials_file is None:
            raise ValueError("Google Drive credentials_file must be specified in 'settings.yaml' or via cred_file parameter.")

        # ---------- Step 3. Set Proxy ----------
        socket.setdefaulttimeout(60)
        self.set_proxy(self.settings.proxy)

        # ---------- Step 4. Build Drive service ----------
        self.service = self._build_drive_service()
        
    def load_settings(self, path: str, inplaces: bool = True) -> AttrDict:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if inplaces:
            self.settings = AttrDict(data)
            return self.settings
        else:
            return AttrDict(data)
        
    def set_logger(self, log_file=None, inplaces=True) -> logging.Logger:
        logger = logging.getLogger("gdrive")
        logger.setLevel(logging.INFO)
        # Clear existing handlers
        if logger.hasHandlers():
            logger.handlers.clear()
        # Create log folder if needed
        if log_file:
            log_folder = os.path.dirname(log_file)
            if log_folder and not os.path.exists(log_folder):
                os.makedirs(log_folder, exist_ok=True)

        # Handlers
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        if log_file:
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            # Redirect stdout & stderr to log file
            logf = open(log_file, "a", encoding="utf-8")
            sys.stdout = logf
            sys.stderr = logf
        else:
            sh = logging.StreamHandler(sys.stdout)
            sh.setFormatter(formatter)
            logger.addHandler(sh)
        if inplaces:
            self.logger = logger
            return self.logger
        else:
            return logger

    def set_proxy(self, proxy_str: str | None):
        # Set up proxy for HTTP requests
        # ---------- step 1. clear all environment proxies to avoid interference ----------
        for key in [
            "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY",
            "http_proxy", "https_proxy", "no_proxy",
            "ALL_PROXY", "all_proxy"]:
            os.environ.pop(key, None)
        # ---------- step 2. Set proxy from settings ----------
        self.proxy = None
        if proxy_str:
            self.proxy = self._build_proxy_info(proxy_str)
            if self.proxy:
                # ---------- step 3. Set os environment ----------
                if self.proxy['ptype'] in ("http", "https"):
                    os.environ["HTTP_PROXY"]  = f"http://{self.proxy['host']}:{self.proxy['port']}"
                    os.environ["HTTPS_PROXY"] = f"http://{self.proxy['host']}:{self.proxy['port']}"
                elif self.proxy['ptype'] in ("socks", "socks5"):
                    os.environ["ALL_PROXY"] = f"socks5://{self.proxy['host']}:{self.proxy['port']}"
                elif self.proxy['ptype'] == "socks4":
                    os.environ["ALL_PROXY"] = f"socks4://{self.proxy['host']}:{self.proxy['port']}"
                self.logger.info("Using proxy %s://%s:%s",
                                self.proxy["ptype"], self.proxy["host"], self.proxy["port"])
        else:
            self.logger.info("No proxy configured. Using direct connection.")
        
    def _build_proxy_info(self, proxy_str: str | None):
        # Build httplib2.ProxyInfo from proxy_str
        if not proxy_str:
            return None

        SOCKS_MAP = {
            "http": socks.HTTP,
            "https": socks.HTTP,
            "socks4": socks.SOCKS4,
            "socks5": socks.SOCKS5,
        }
        ptype, host, port = parse_proxy(proxy_str)
        proxy_type = SOCKS_MAP.get(ptype, socks.HTTP)

        info = httplib2.ProxyInfo(
            proxy_type=proxy_type,
            proxy_host=host,
            proxy_port=port)
        
        return {
            "ptype": ptype,
            "host": host,
            "port": port,
            "info": info,
        }
    
    def restart_drive_service(self, remove_token: bool = False):
        # Rebuild Google Drive API service
        if remove_token:
            token_path = self.settings.google_drive.save_token_file
            if os.path.exists(token_path):
                os.remove(token_path)
                self.logger.info("Removed token file: %s", token_path)
        self.service = self._build_drive_service()


    def _build_drive_service(self):
        # Build Google Drive API service
        # ---------- step 1. Load settings ----------
        gd = self.settings.google_drive
        scopes = gd.oauth_scope
        credentials_path = gd.credentials_file
        token_path = gd.save_token_file
        save_token = bool(gd.save_token)
        remote = gd.remote if hasattr(gd, 'remote') else False
        creds = None

        # ---------- step 2. Get OAuth token ----------
        # load existing OAuth token from token file (if enabled)
        if save_token and os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, scopes)
                self.logger.info("Loaded token from %s", token_path)
            except Exception as e:
                self.logger.warning("Failed to load token, will re-auth: %s", e)
                creds = None

        # if no valid credential, attempt refresh or re-authenticate
        if not creds or not creds.valid:
            #  refresh token 
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.logger.info("Token refreshed successfully.")
                except Exception as e:
                    self.logger.error("Token refresh failed: %s", e)
                    creds = None
            # re-authorize using credentials.json
            if not creds:
                if not os.path.exists(credentials_path):
                    self.logger.error(
                        "Credentials file %s not found. "
                        "Download it from Google Cloud Console.", credentials_path)
                    raise FileNotFoundError(credentials_path)
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
                if not remote:
                    self.logger.info("Start OAuth authorization (local login)...")
                    creds = flow.run_local_server(port=0)
                else:
                    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # allow http://localhost callback
                    self.logger.info("Start OAuth authorization (remote login)...")
                    flow.redirect_uri = "http://localhost"
                    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
                    print("Please go to this URL to authorize the application:", auth_url)
                    redirected_url = input("Paste redirected URL here: ").strip()
                    if "code=" not in redirected_url:
                        raise ValueError("Invalid redirected URL. 'code=' parameter not found.")
                    flow.fetch_token(authorization_response=redirected_url)
                    creds = flow.credentials
                self.logger.info("OAuth authorization completed.")

            # Save the token for the next run
            if save_token:
                with open(token_path, "w", encoding="utf-8") as f:
                    f.write(creds.to_json())
                self.logger.info("Token saved to %s", token_path)

        # ---------- step 3. Build HTTP client: with or without proxy ----------
        if self.proxy:
            base_http = httplib2.Http(timeout=120, proxy_info=self.proxy["info"])
            self.logger.info("Using proxy connection: %s://%s:%s.",
                            self.proxy["ptype"], self.proxy["host"], self.proxy["port"])
        else:
            base_http = httplib2.Http(timeout=120)
            self.logger.info("Using direct connection.")
        authed_http = AuthorizedHttp(creds, http=base_http)
        # Disable HTTP 308 redirect handling to avoid issues with some proxies
        base_http.redirect_codes = base_http.redirect_codes - {308}

        service = build("drive", "v3", http=authed_http, cache_discovery=False)
        self.logger.info("Google Drive service built successfully.")
        return service

    # ---------- public: upload ----------
    def upload(self,
               local_file=None,
               save_file_name=None,
               folder_id=None,
               chunksize=None) -> list[tuple[str, str]]:
        """
        Upload one or multiple files to Google Drive.
        Parameters
        ----------
        local_file : str or list[str] or None
            Path or list of paths. If None, use settings.upload.local_file.
        save_file_name : str or list[str] or None
            Name(s) to use on Drive. If None, use local filenames.
        folder_id : str or None
            Drive folder ID. If None, upload to root or settings.upload.save_folder_id.
        chunksize : int or None
            Chunk size for resumable upload in bytes. If None, use settings.upload.chunksize.
            
        Returns 
        -------
        List of (local_path, file_id)
        """
        # Defaults from settings
        if local_file is None:
            local_file = self.settings.upload.local_file
        if folder_id is None:
            folder_id = self.settings.upload.save_folder_id
        if save_file_name is None:
            save_file_name = self.settings.upload.save_file_name
        if chunksize is None:
            chunksize = self.settings.upload.chunksize

        # Normalize to list (local_file)
        if isinstance(local_file, (str, os.PathLike)):
            local_files_list = [str(local_file)]
        else:
            local_files_list = list(local_file)

        # Normalize to list (save_file_name)
        if save_file_name is None:
            save_names_list =  [os.path.basename(f) for f in local_files_list]
        elif isinstance(save_file_name, (str, os.PathLike)):
            save_names_list = [str(save_file_name)]
        else:
            save_names_list = list(save_file_name)

        # Check
        # Check save names length
        if len(save_names_list) != len(local_files_list):
            raise ValueError("save_file_name must be None, or a list of the same length as local_file.")
        # Check local files exist
        for local_file in local_files_list:
            if not os.path.exists(local_file):
                raise FileNotFoundError(f"Local file not found: {local_file}")

        # Upload files
        results = []
        for n in range(len(local_files_list)):
            self.logger.info("Upload Progress: [ %d / %d ]", n+1, len(local_files_list))
            local_file = local_files_list[n]
            save_file_name = save_names_list[n]
            file_id = self._upload_single(local_file, save_file_name, folder_id, chunksize=chunksize)
            results.append((local_file, file_id))
        return results

    def _upload_single(self, 
                       local_file: str,
                       save_file_name: str | None,
                       folder_id: str | None,
                       chunksize=1024*1024*100) -> str:
        # If local_file exists
        if not os.path.exists(local_file):
            raise FileNotFoundError(f"Local file not found: {local_file}")
        # Prepare save file
        if save_file_name is None:
            save_file_name = os.path.basename(local_file)
        file_metadata = {"name": save_file_name}
        if folder_id:
            file_metadata["parents"] = [folder_id]
        
        # Upload file
        media = MediaFileUpload(local_file, resumable=True, chunksize=int(chunksize))
        file_size_bytes = os.path.getsize(local_file)
        self.logger.info("Uploading %s -> %s ...", local_file, save_file_name)
        request = self.service.files().create(
            body=file_metadata,
            media_body=media,
            supportsTeamDrives=True,
            fields="id",
        )
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                uploaded = int(status.progress() * file_size_bytes)
                self.logger.info(
                    "Uploading file: %.2f%% (%s / %s)",
                    status.progress() * 100,
                    human_size(uploaded),
                    human_size(file_size_bytes),
                )
        self.logger.info("Uploading file: 100.00%% (%s / %s)", human_size(file_size_bytes), human_size(file_size_bytes))
        file_id = response.get("id")
        self.logger.info("Upload finished. File Id=%s", file_id)
        return file_id

    # ---------- public: download ----------
    def download(self,
                 file_id: str | list[str] | None = None,
                 save_local_dir: str | None = None,
                 chunksize=None) -> list[str]:
        """
        Download one or multiple files from Google Drive.

        Parameters
        ----------
        file_id : str or list[str] or None
            One file ID or a list of file IDs. If None, use settings.download.file_id.
        save_local_dir : str or list[str] or None
            Local directory to save file(s). If None, use settings.download.save_local_dir.
        chunksize : int or None
            Chunk size for resumable download in bytes. If None, use settings.download.chunksize.

        Returns
        -------
        list[str]
            A list of local file paths of the downloaded files.
        """
        # Defaults from settings
        if file_id is None:
            try:
                file_id = self.settings.download.file_id
            except Exception:
                raise ValueError("file_id is None and settings.download.file_id not found.")
        if save_local_dir is None:
            save_local_dir = self.settings.download.save_local_dir
        if chunksize is None:
            chunksize = self.settings.download.chunksize

        # Normalize file_id to list
        if isinstance(file_id, str):
            file_id_list = [file_id]
        else:
            file_id_list = list(file_id)

        # Check
        # Check save_local_dir exists
        if (save_local_dir is not None) and (not os.path.exists(save_local_dir)):
            os.makedirs(save_local_dir, exist_ok=True)

        # Download files
        results = []
        for n in range(len(file_id_list)):
            self.logger.info("Download Progress: [ %d / %d ]", n+1, len(file_id_list))
            file_id = file_id_list[n]
            local_path = self._download_single(file_id, save_local_dir, chunksize=int(chunksize))
            results.append(local_path)
        return results
    
    def _download_single(self,
                         file_id: str,
                         save_local_dir: str | None = None,
                         chunksize=1024*1024*100) -> str:
        # Check file exists on Drive 
        try:
            meta = self.service.files().get(fileId=file_id, fields="name,size").execute()
        except Exception as e:
            self.logger.error("Failed to get metadata for file_id=%s: %s", file_id, e)
            return None

        if not meta:
            self.logger.error("File ID %s not found on Google Drive.", file_id)
            return None
        
        # Prepare 
        file_name = meta.get("name", file_id)
        size_str = meta.get("size")
        file_size_bytes = int(size_str) if size_str is not None else 0
        if save_local_dir is None:
            save_local_dir = ''
        local_path = os.path.join(save_local_dir, file_name)
        self.logger.info("Downloading %s <- %s (id=%s) ...",
                         local_path, file_name, file_id)
        # Download file
        try:
            request = self.service.files().get_media(fileId=file_id)
            with io.FileIO(local_path, "wb") as fh:
                downloader = MediaIoBaseDownload(fh, request, chunksize=chunksize)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status is not None:
                        downloaded = int(status.progress() * file_size_bytes)
                        if file_size_bytes > 0:
                            self.logger.info(
                                "Downloading file: %.2f%% (%s / %s)",
                                status.progress() * 100, 
                                human_size(downloaded),
                                human_size(file_size_bytes))
                        else:
                            self.logger.info(
                                "Downloading file: %.2f%%",
                                status.progress() * 100)
        except Exception as e:
            self.logger.error("Download failed for file_id=%s: %s", file_id, e)
            # If download fails, it may leave an incomplete/empty file, which can be optionally removed
            try:
                if os.path.exists(local_path) and os.path.getsize(local_path) == 0:
                    os.remove(local_path)
            except Exception:
                pass
            return None
        self.logger.info("Download finished: %s", local_path)
        return local_path
    
    def create_folder(self,
                      folder_name: str,
                      parent_folder_id: str | None = None) -> str:
        """
        Create a folder on Google Drive.

        Parameters
        ----------
        folder_name : str
            Name of the folder to create.
        parent_folder_id : str or None
            ID of the parent folder. If None, create in root.

        Returns
        -------
        str
            The ID of the created folder.
        """
        file_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        if parent_folder_id:
            file_metadata["parents"] = [parent_folder_id]

        folder = self.service.files().create(
            body=file_metadata,
            fields="id"
        ).execute()
        folder_id = folder.get("id")
        self.logger.info("Folder created: %s (ID: %s)", folder_name, folder_id)
        return folder_id
    
    def _check_local_files(self, file_list, check_info=None):
        # Check local files exist
        info = {"File_num": 0, "Folder_num": 0, "Total_size": 0}
        for local_file in file_list:
            if not os.path.exists(local_file):
                raise FileNotFoundError(f"Local file not found: {local_file}")
            if os.path.isfile(local_file):
                info["File_num"] += 1
                info["Total_size"] += os.path.getsize(local_file)
            elif os.path.isdir(local_file):
                info["Folder_num"] += 1
                sub_files_list = [os.path.join(local_file, f) for f in os.listdir(local_file)]
                sub_info = self._check_local_files(sub_files_list)
                info["File_num"] += sub_info["File_num"]
                info["Folder_num"] += sub_info["Folder_num"]
                info["Total_size"] += sub_info["Total_size"]
        if check_info is not None:
            check_info.update(info)
        else:
            check_info = info
        return check_info
    
    
    def _upload_files(self, local_file_list, folder_id, folder_name=None, chunksize=None, upload_results=None):
        # Defaults from settings
        if chunksize is None:
            chunksize = self.settings.upload.chunksize
        if folder_name is None:
            if folder_id is None:
                folder_name = "root"
            else:
                try:
                    meta = self.service.files().get(fileId=folder_id, fields="name").execute()
                    folder_name = meta.get("name", folder_id)
                except Exception:
                    folder_name = None
        if upload_results is None:
            upload_results = {"folder_id": folder_id, 'folder_name': folder_name, "content": []}

        # Upload files
        for local_file in local_file_list:
            if not os.path.exists(local_file):
                raise FileNotFoundError(f"Local file not found: {local_file}")
            if os.path.isfile(local_file):
                file_name = os.path.basename(local_file)
                file_id = self._upload_single(local_file, file_name, folder_id, chunksize=chunksize)
                upload_results['content'].append({"file_name": os.path.basename(local_file), "file_id": file_id})
            elif os.path.isdir(local_file):
                folder_name = os.path.basename(local_file)
                new_folder_id = self.create_folder(folder_name, parent_folder_id=folder_id)
                sub_files_list = [os.path.join(local_file, f) for f in os.listdir(local_file)]
                sub_upload_results = self._upload_files(sub_files_list, new_folder_id, folder_name=folder_name, chunksize=chunksize)
                upload_results['content'].append(sub_upload_results)
        return upload_results
    
    def upload2(self,
                local_file=None,
                folder_id=None,
                chunksize=None) -> list[tuple[str, str]]:
        """
        upload files or folders to google drive
        
        :param self: 说明
        """
        # Defaults from settings
        if local_file is None:
            local_file = self.settings.upload.local_file
        if folder_id is None:
            folder_id = self.settings.upload.save_folder_id
        if chunksize is None:
            chunksize = self.settings.upload.chunksize

        # Normalize to list (local_file)
        if isinstance(local_file, (str, os.PathLike)):
            local_file_list = [str(local_file)]
        else:
            local_file_list = list(local_file)
        
        # Check
        check_info = self._check_local_files(local_file_list)
        self.logger.info("Total need to upload: %d files, %d folders, ( %s )",
                         check_info["File_num"], check_info["Folder_num"],
                         human_size(check_info["Total_size"]))
            
        # Upload
        upload_results = self._upload_files(local_file_list, folder_id, chunksize=chunksize)
        return upload_results
    
    def _check_remote_files(self, file_id_list, check_info=None):
        # Check remote files exist
        info = {"File_num": 0, "Folder_num": 0, "Total_size": 0}

        for file_id in file_id_list:
            try:
                meta = self.service.files().get(fileId=file_id, fields="name,mimeType,size").execute()
                if_file = '.folder' not in meta.get("mimeType")
            except:
                if_file = False

            if if_file:
                # is a file
                info["File_num"] += 1
                size_str = meta.get("size")
                if size_str is not None:
                    info["Total_size"] += int(size_str)
            else:
                # is a folder
                info["Folder_num"] += 1
                children = self._list_children(file_id)
                sub_file_ids = [f[0] for f in children]
                sub_info = self._check_remote_files(sub_file_ids)
                info["File_num"] += sub_info["File_num"]
                info["Folder_num"] += sub_info["Folder_num"]
                info["Total_size"] += sub_info["Total_size"]
        if check_info is not None:
            check_info.update(info)
        else:
            check_info = info
        return check_info
    
    def _list_children(self, folder_id: str):
        page_token = None
        files_id = []
        while True:
            resp = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields="nextPageToken, files(id,name,mimeType,size)",
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            ).execute()

            for f in resp.get("files", []):
                files_id.append([f["id"], f["name"], f["mimeType"], f.get("size")])

            page_token = resp.get("nextPageToken")
            if not page_token:
                break
        return files_id
    
    def _download_files(self, remote_file_list, local_dir, folder_id=None, chunksize=None, download_results=None):
        # Defaults from settings
        if chunksize is None:
            chunksize = self.settings.download.chunksize
        if local_dir is None:
            local_dir = './'
        if download_results is None:
            download_results = {"folder_name": local_dir, "folder_id": folder_id, "content": []}
        # Download files
        if not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)
        for file_id in remote_file_list:
            connect = False
            try:
                meta = self.service.files().get(fileId=file_id, fields="name,mimeType").execute()
                if_file = '.folder' not in meta.get("mimeType")
                connect = True
            except:
                if_file = False
            
            if if_file:
                # is a file
                local_path = self._download_single(file_id, local_dir, chunksize=chunksize)
                download_results['content'].append({"file_name": os.path.basename(local_path), "file_id": file_id})
            else:
                # is a folder
                if not connect:
                    folder_name = file_id
                else:
                    folder_name = meta.get("name", file_id)
                new_local_dir = os.path.join(local_dir, folder_name)
                children = self._list_children(file_id)
                sub_file_ids = [f[0] for f in children]
                sub_download_results = self._download_files(sub_file_ids, new_local_dir, folder_id=file_id, chunksize=chunksize)
                download_results['content'].append(sub_download_results)
        return download_results

            
    def download2(self,
                  file_id: str | list[str] | None = None,
                  save_local_dir: str | None = None,
                  chunksize=None) -> list[str]:
        """
        download files or folders from google drive
        
        :param self: 说明
        """
        # Defaults from settings
        if file_id is None:
            file_id = self.settings.download.file_id
        if save_local_dir is None:
            save_local_dir = self.settings.download.save_local_dir
        if chunksize is None:
            chunksize = self.settings.download.chunksize

        # Normalize file_id to list
        if isinstance(file_id, str):
            file_id_list = [file_id]
        else:
            file_id_list = list(file_id)

        # Check
        # Check save_local_dir exists
        if (save_local_dir is not None) and (not os.path.exists(save_local_dir)):
            os.makedirs(save_local_dir, exist_ok=True)

        # Check remote files
        check_info = self._check_remote_files(file_id_list)
        self.logger.info("Total need to download: %d files, %d folders, ( %s )",
                         check_info["File_num"], check_info["Folder_num"],
                         human_size(check_info["Total_size"]))
        # Download files
        download_results = self._download_files(file_id_list, save_local_dir, chunksize=int(chunksize))
        return download_results
        

def parse_proxy(proxy_str: str,
                default_port: int = 1080,
                default_type: str = "http") -> tuple[str, str, int]:
    """
    Parse proxy string and return (proxy_type, host, port).
    Supported formats:
        - "127.0.0.1:1080"
        - "http://127.0.0.1:1080"
        - "socks5://127.0.0.1:1080"
        - "socks4://127.0.0.1:1080"
        - "127.0.0.1"
        - "localhost"
    """
    proxy = proxy_str.strip()
    proxy_type = default_type.lower()

    # Check proxy type
    if "://" in proxy:
        proto, proxy = proxy.split("://", 1)
        proxy_type = proto.lower()

    # normalize acceptable type values
    if proxy_type not in ["http", "https", "socks", "socks4", "socks5"]:
        proxy_type = default_type
    # "socks" should be treated as "socks5"
    if proxy_type == "socks":
        proxy_type = "socks5"

    # Extract host and port
    if ":" in proxy:
        host, port = proxy.split(":", 1)
        port = int(port)
    else:
        host = proxy
        port = default_port

    return proxy_type, host, port