# -*- encoding: utf-8 -*-
'''
@Time     :   2025/12/01 23:17:20
@Author   :   QuYue
@File     :   python_manual.py
@Email    :   quyue1541@gmail.com
@Desc:    :   python_manual
'''


#%% Import Packages
# Basic
import os
import sys

# Path
# change path to this file's parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
os.chdir(parent_dir)
sys.path.append(parent_dir)  # Ensure parent directory is in sys.path

# GDriveTools
from gdrivetools import GoogleDriveTools


#%% Quickstart
if __name__ == "__main__":
    # Step 1. Initialize GDriveTools without settings.yaml file
    """
    Initialize GoogleDriveTools.
    def __init__(self, settings_path: str | None = None, *,
        # Manual override parameters:
        cred_file=None,
        proxy=None,
        log=None):
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
        log : str | None   
            Log file path.
            log = None (use setting.log) | "off" (use stdout) | other string (override setting.log).
            e.g., "log.txt"
        show_settings : bool
            Whether to print loaded settings to console. Default: False.
    """
    gdt = GoogleDriveTools(cred_file="./Json/credentials.json", 
                           proxy="socks5://127.0.0.1:1080",
                           log=None)

    # Step 2. Upload files
    """
    def upload(self,
               local_file=None,
               save_file_name=None,
               folder_id=None
               chunksize=1024*1024*100) -> list[tuple[str, str]]:
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
    local_file  = './examples/python_manual.py' # If you want to upload one file, use a string.
    local_files = ['./examples/python_manual.py', './settings.yaml'] # If you want to upload multiple files, use a list of strings.
    results_up  = gdt.upload(local_file=local_files, chunksize=1024*1024*10)

    # Step 3. Download files
    """
    def download(self,
                 file_id: str | list[str] | None = None,
                 save_local_dir: str | None = None,
                 chunksize=1024*1024*100) -> list[str]:
        Download one or multiple files from Google Drive.

        Parameters
        ----------
        file_id : str or list[str] or None
            One file ID or a list of file IDs. If None, use settings.download.file_id.
        save_local_dir : str or list[str] or None
            Local directory to save file(s). If None, use csettings.download.save_local_dir.
        chunksize : int or None
            Chunk size for resumable download in bytes. If None, use settings.download.chunksize.

        Returns
        -------
        list[str]
            A list of local file paths of the downloaded files.
    """
    file_id = results_up[0][1] # If you want to download one file, use a string.
    file_ids = [res[1] for res in results_up] # If you want to download multiple files, use a list of strings.
    results_down = gdt.download(file_id=file_ids, save_local_dir='./downloads', chunksize=1024*1024*10)


# %%
