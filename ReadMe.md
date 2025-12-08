<h1 align="center">Google Drive Upload Tools</h1>

<p align="center">
 Created on 2025/12<br>
Tags: GoogleDrive, Upload, OAuth, Python, Proxy, Automation</p>

<p align="right">
  <strong>曲岳 Yue Qu</strong>
</p>

## Table of Contents
<!-- - [:pushpin: 1. Overview](#overview)
- [:package: 2. Install Python Dependencies](#installation)
- [:shield: 3. Get Google Drive API Credentials](#credentials)
- [:gear: 4. Configuration File: settings.yaml](#configuration)
- [:outbox_tray: 5. Python API Usage (Method 1)](#python_usage)
    - [:gear: 5.1. Initialize GoogleDriveTools](#pu_init)
    - [:arrow_up: 5.2. Upload File(s) to Google Drive](#pu_upload)
    - [:arrow_down: 5.3. Download File(s) from Google Drive](#pu_download)
    - [:file_folder: 5.4. Full Examples](#pu_example)
- [:outbox_tray: 6. CLI Usage (Method 2)](#cli_usage)
    - [:package: 6.1. Install the CLI Tool](#cu_init)
    - [:gear: 6.2. CLI Parameters](#cu_p)
    - [:arrow_up: 6.3. Upload File(s) to Google Drive](#cu_upload)
    - [:arrow_down: 6.4. Download File(s) from Google Drive](#cu_download)
    - [:file_folder: 6.5. Full CLI Examples](#cu_example)
- [:key: 7. OAuth Authentication](#oauth)
- [:globe_with_meridians: 8. Proxy Support](#proxy) -->

- [:pushpin: 1. Overview](#overview)
- [:package: 2. Install Python Dependencies](#installation)
- [:key: 3. Get Google Drive API Credentials](#credentials)
- [:gear: 4. Configuration File: settings.yaml](#configuration)
- [:snake: 5. Python API Usage (Method 1)](#python_usage)
    - [:gear: 5.1. Initialize GoogleDriveTools](#pu_init)
    - [:arrow_up: 5.2. Upload File(s) to Google Drive](#pu_upload)
    - [:arrow_down: 5.3. Download File(s) from Google Drive](#pu_download)
    - [:file_folder: 5.4. Full Python Examples](#pu_example)
- [:computer: 6. CLI Usage (Method 2)](#cli_usage)
    - [:package: 6.1. Install the CLI Tool](#cu_init)
    - [:gear: 6.2. CLI Parameters](#cu_p)
    - [:arrow_up: 6.3. Upload File(s) to Google Drive](#cu_upload)
    - [:arrow_down: 6.4. Download File(s) from Google Drive](#cu_download)
    - [:file_folder: 6.5. Full CLI Examples](#cu_example)
- [:shield: 7. OAuth Authentication](#oauth)
- [:globe_with_meridians: 8. Proxy Support](#proxy)

<a id="overview"></a>

# :pushpin: 1. Overview

**gdrive-tools** is a robust, developer-friendly Python library and CLI utility for interacting with Google Drive.  
This tool allows you to upload and download files to Google Drive using the Google Drive API.

Built for research environments, servers, and automation workflows, `gdrive-tools` integrates:

- ✔️ Python API for programmatic uploads/downloads  
- ✔️ CLI interface for quick terminal operations  
- ✔️ `settings.yaml` configuration for reproducible setups  
- ✔️ HTTP / HTTPS / SOCKS proxies for restricted network environments  
- ✔️ Automatic token management via OAuth2  
- ✔️ Full logging support
- ✔️ Resumable uploads/downloads for large files


<a id="installation"></a>

##  :package: 2. Install Python Dependencies
This tool requires Python 3.6+. Please install the required packages via pip:

```bash
pip install google-auth-httplib2==0.1.0 google-api-python-client==1.7.8 httplib2==0.15.0 google-auth==1.12.0 google-auth-oauthlib==0.3.0 PyYAML>=6.0.1 PySocks>=1.7.1
```
Alternatively, you can install from requirements.txt:

```bash
pip install -r requirements.txt
```

<a id="credentials"></a>

## :key: 3. Get Google Drive API Credentials
Get Credentials Json File from Google Cloud Console for Google Drive API
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
![alt text](/Images/Projects.png)
3. Navigate to "APIs & Services" > "Credentials".
![alt text](/Images/Credentials.png)
4. Create OAuth 2.0 Client IDs credentials. (Attention: You must use OAuth Client ID, not API Key)
We can choose "Desktop app" as the application type.
![alt text](/Images/OAuth.png)
5. Download the Json file and place it in the 'Json' folder. Then Rename it to 'credentials.json'.

<a id="configuration"></a>

## :gear: 4. Configuration File: settings.yaml
Default settings are stored in settings.yaml:

```yaml

# ============================================================
# Google Drive API Settings
# ============================================================
google_drive:

  # Path to your Google OAuth client credentials JSON file.
  # Download from Google Cloud → API & Services → Credentials.
  credentials_file: ./Json/credentials.json

  # Whether to save the OAuth access token to disk.
  # If True, token.json is created and reused on next runs.
  save_token: True

  # Path to store the generated OAuth token (token.json).
  # Only used when save_token=True.
  save_token_file: ./Json/token.json

  # OAuth scopes required by the script.
  # "drive.file" allows uploading and modifying your own files.
  oauth_scope:
    - https://www.googleapis.com/auth/drive.file


# ============================================================
# Proxy Settings
# ============================================================
  # Proxy server used for Google Drive upload (optional).
  # Supported formats:
  #   - 127.0.0.1:1080
  #   - http://127.0.0.1:1080
  #   - socks4://127.0.0.1:1080
  #   - socks5://127.0.0.1:1080
  # If null, no proxy is used.
proxy: null # socks://127.0.0.1:1080

# ============================================================
# Log Settings
# ============================================================
  # Log file name.
  # If null, log messages are printed to console only.
log: null


# ============================================================
# Upload Settings
# ============================================================
upload:
  # Local file path or list of local files to upload.
  # Examples:
  #   - "data.zip"
  #   - ["a.txt", "b.txt"]
  # If null, must be provided by CLI argument -n / --name.
  local_file: ['settings.yaml', 'requirements.txt']

  # The filename(s) to be used in Google Drive.
  # If null, Google Drive will use the local filename(s) by default.
  # Must match the length of local_file if both are lists.
  save_file_name: null

  # The target folder ID in Google Drive.
  # If null, uploads to the root directory ("My Drive").
  save_folder_id: null

  # Chunk size for resumable upload in bytes.
  # Default chunk size 10MB (1024*1024*10).
  chunksize: 10485760


# ============================================================
# Download Settings
# ============================================================
download:

  # Local directory to save downloaded files.
  # If null, files are saved to the './download'.
  save_local_dir: './download'

  # The file id(s) to download from Google Drive.
  # Examples:
  #   - "1A2B3C4D5E6F7G8H9I0J"
  #   - ["1A2B3C4D5E6F7G8H9I0J", "0J9I8H7G6F5E4D3C2B1A"]
  # Must match the length of save_local_file if both are lists.
  file_id: file_id

  # Chunk size for resumable download in bytes.
  # Default chunk size 10MB (1024*1024*10).
  chunksize: 10485760
```
    
You may modify this YAML to set default behavior.

<a id="python_usage"></a>

## :snake: 5. Python API Usage (Method 1)
We can use the `gdrivetools` module in our own Python scripts to upload files to Google Drive.

<a id="pu_init"></a>
### :gear: 5.1. Initialize GoogleDriveTools
First, we need to initialize the `GoogleDriveTools` class. We can provide settings via a `settings.yaml` file or directly via parameters. But at least one of `settings_path` or `cred_file` must be provided.

|Parameter|Description|Type|Default|Example|
|-|-|-|-|-|
|settings_path|Path to settings.yaml file. `If None, use default settings and 'cred_file' must be provided.`|String, None|None|"./settings.yaml"|
|cred_file|Google API credentials file (get it from Google Cloud Console). `If setting_path = None, must be provided here.` If cred_file = None,use setting.google_drive.credentials_file.|String, None|None|"./Json/credentials.json"|
|proxy|Proxy server for HTTP requests. If proxy = None, use setting.proxy. If proxy= "off", direct connection.|String, None|None|"http://127.0.0.1:1080" "socks4://127.0.0.1:1080" "socks5://127.0.0.1:1080"|
|log|Log file path. If log = None, use setting.log. If log = "off", use stdout.|String, None|None|"log.txt"|

- Initialize GDriveTools with settings.yaml file
```python
from gdrivetools import GoogleDriveTools
gdt = GoogleDriveTools(settings_path="./settings.yaml",
                        proxy="socks5://127.0.0.1:1080")
```

- Initialize GDriveTools without settings.yaml file
```python
from gdrivetools import GoogleDriveTools
gdt = GoogleDriveTools(cred_file="./Json/credentials.json",
                        proxy="socks5://127.0.0.1:1080",
                        log=None)
```

<a id="pu_upload"></a>
### :arrow_up: 5.2. Upload File(s) to Google Drive
We can use the `upload` method to upload single or multiple files to Google Drive.
|Parameter|Description|Type|Default|Example|
|-|-|-|-|-|
|local_file|Path or list of paths. If local_file = None, use settings.upload.local_file.|String,List[String], None|None| ["a.txt", "b.txt"]|
|save_file_name|File name(s) to use on Drive. If save_file_name = None, use local filenames.|String, List[String], None|None|["file_a.txt", "file_b.txt"]|
|folder_id|Drive folder ID. If folder_id = None, upload to settings.upload.save_folder_id. `If still None, upload to root directory`.|String, None|None|"1i93YFUQK5fbJUss_3rhwOyuAkMQgZjJk"|
|chunksize|Chunk size for resumable upload in bytes. If chunksize = None, use settings.upload.chunksize.|Int, None|None|1024\*1024\*10 (10MB)| 


```python
# Single file upload
local_file  = './examples/python_settings.py' # If you want to upload one file, use a string.
# Multiple files upload
local_file = ['./examples/python_settings.py', './settings.yaml'] # If you want to upload multiple files, use a list of strings.
results_up  = gdt.upload(local_file=local_file, chunksize=1024*1024*10)
```

The results_up is a list of file name and uploaded file IDs on Google Drive.
```python
print(results_up)
# Example output: [(file_name, file_id), ...]
#[('./examples/python_settings.py', '1MKjr4gVlVQb31zCfQT5mUX9P_09Y6Ebp'),
# ('./settings.yaml', '1_80mElG05jfpNoiyRju1dmv_dOL9ocwG')]
```

<a id="pu_download"></a>
### :arrow_down: 5.3. Download File(s) from Google Drive
We can use the `download` method to download single or multiple files from Google Drive.
|Parameter|Description|Type|Default|Example|
|-|-|-|-|-|
|file_id|One file ID or a list of file IDs in Google Drive. If file_id = None, use settings.download.file_id.|String, List[String], None|None|["1A2B3C4D5E6F7G8H9I0J", "0J9I8H7G6F5E4D3C2B1A"]|
|save_local_dir|Local directory to save file(s). If save_local_dir = None, use settings.download.save_local_dir.|String, List[String], None|None|"./download"|
|chunksize|Chunk size for resumable download in bytes. If chunksize = None, use settings.download.chunksize.|Int, None|None|1024\*1024\*10 (10MB)|

```python
# Single file download
file_id = results_up[0][1] # If you want to download one file, use a string.
# Multiple files download
file_id = [res[1] for res in results_up] # If you want to download multiple files, use a list of strings.
results_down = gdt.download(file_id=file_id, save_local_dir='./downloads', chunksize=1024*1024*10)
# Example output: [file_name, ...]
# ['./downloads/python_settings.py', './downloads/settings.yaml']

```

> **How to get a Google Drive folder ID**: 
Open the target folder in Google Drive and look at the URL. The part after /folders/ is the folder ID.
> Example: https://drive.google.com/drive/folders/1i93YFUQK5fbJUss_3rhwOyuAkMQgZjJk?dmr=1&ec=wgc-drive-globalnav-goto


<a id="pu_example"></a>
### :file_folder: 5.4. Full Python Examples
The full examples can be found in `examples/python_manual.py` and `examples/python_settings.py`.

<a id="cli_usage"></a>
## :computer: 6. CLI Usage (Method 2)
We can also use the command line interface (CLI) to upload file(s) and download file(s).

<a id="cu_init"></a>
### :package: 6.1. Install the CLI Tool
First, install the tool via pip. There are two installation methods:
1. Development mode Installation. It lets you modify source code and use the tool without reinstalling.
    ```bash
    pip install -e .
    ```
2. Normal Installation (not recommended, as you need to reinstall after code changes).
    ```bash
    pip install .
    ```
You must run this command in the root directory of the project, where pyproject.toml is located.


After installation, the CLI command becomes available:
```bash
gdrive-tools --help
```

<a id="cu_p"></a>
### :gear: 6.2. CLI Parameters
usage: gdrive-tools [-h] [-s SETTINGS] [-c CRED] [-l LOG] [-p PROXY] {upload,download} ...

| Argument | Description | Default |
|---|---|---|
|-s, <br>--settings | Path to settings YAML file. <br>If omitted, uses 'settings.yaml'. <br>If the file does not exist or set to 'off', default settings will be used. | settings.yaml |
|-c, <br>--cred | Path to Google OAuth credentials JSON file. <br>If omitted, uses settings.google_api.credentials_path. | settings.google_drive.credentials_file |
|-l, <br>--log | Path to log file. <br>If omitted, uses settings.log. <br>If set to 'off', logs will be printed to standard output. | settings.txt |
|-p, <br>--proxy | Proxy server address. <br>If omitted, uses settings.proxy. <br>If set to 'off', no proxy will be used (direct connection). <br>Format: [type://]host:port. Type can be in [http, socks4, socks5]. <br> e.g., 127.0.0.1:1080, http://127.0.0.1:1080, socks5://127.0.0.1:1080| http://127.0.0.1:1080|

<a id="cu_upload"></a>
### :arrow_up: 6.3. Upload File(s) to Google Drive
We can use the `upload` subcommand to upload files to Google Drive.
| Argument | Description | Default |
|---|---|---|
|-n, <br>--name | One or more local files to upload. <br>If omitted, uses settings.upload.local_file. | settings.upload.local_file |
|-s, <br>--save_file_name | One or more filenames to use in Google Drive. <br>If omitted, uses local filenames. | settings.upload.save_file_name |
|-i, <br>--save_folder_id | Destination folder ID in Google Drive. <br>If omitted, uploads to settings.upload.save_folder_id or the Drive root directory. | settings.upload.save_folder_id |


- Get help for upload command
    ```bash
    gdrive-tools upload --help
    ```
- Example: Upload file(s)
    ```bash
    gdrive-tools upload -n file.txt
    gdrive-tools upload -n file1.txt file2.txt file3.txt
    ```
- Example: Upload with custom names
    ```bash
    gdrive-tools upload -n file1.txt file2.txt -s upload_file1.txt upload_file2.txt
    ```
- Example: Upload into a specific Drive folder
    ```bash
    gdrive-tools upload -n file.txt -i your_folder_id
    ```
- Example: Use a proxy
    ```bash
    gdrive-tools -p socks5://127.0.0.1:1080 upload -n file.txt
    ```
- Example: Specify a different settings file
    ```bash
    gdrive-tools -s ./settings.yaml upload -n file.txt
    ```

<a id="cu_download"></a>
### :arrow_down: 6.4. Download File(s) from Google Drive
We can use the `download` subcommand to download files from Google Drive.
| Argument | Description | Default |
|---|---|---|
|-f, <br>--file_id | One or more Google Drive file IDs to download <br>If omitted, uses settings.download.file_id. | settings.download.file_id |
|-o, <br>--out_dir | Local directory to save downloaded files. <br>If omitted, use settings.download.save_local_dir. <br>Directory will be created automatically if it does not exist. | settings.download.save_local_dir |

- Get help for download command
    ```bash
    gdrive-tools download --help
    ```
- Example: Download file(s)
    ```bash
    gdrive-tools download -f 1AbCdEfGhIjK
    gdrive-tools download -f id1 id2 id3
    ```
- Example: Specify output directory
    ```bash
    gdrive-tools download -f 1AbCdEfGhIjK -o ./downloads
    ```
- Example: Use a proxy
    ```bash
    gdrive-tools -p socks5://127.0.0.1:1080 download -f 1AbCdEfGhIjK
    ```

<a id="cu_example"></a>
### :file_folder: 6.5. Full CLI Examples
Upload 
```bash
gdrive-tools \
-s ./settings.yaml \
-c ./Json/credentials.json \
-p http://127.0.0.1:1080 \
-l log.txt
upload \
-n settings.yaml ReadMe.md \
-s settings_backup.yaml readme_backup.md \
-i 1i93YFUQK5fbJUss_3rhwOyu
```
Download
```bash
gdrive-tools \
-s ./settings.yaml \
-c ./Json/credentials.json \
-p http://127.0.0.1:1080 \
-l log.txt
download \
-f 1AbCdEfGhIjK 0J9I8H7G6
-o ./downloads

```

<a id="oauth"></a>

## :shield: 7. OAuth Authentication
1. First Run
    The first time you run the script, it will prompt you to authorize access to your Google Drive account. The script will:
	1.	read credentials JSON
	2.	open a browser
	3.	ask for Google authorization
	4.	save token.json automatically to './Json/token.json' if `save_token` is True in settings.yaml. In future runs, the script will reuse this token for authentication. However, if the token expires or is invalid, you will need to re-authorize.

2. Future runs
    If the token is valid, the script uses it directly.

3. Auto-refresh
    Expired tokens are automatically refreshed if a refresh token exists.

<a id="proxy"></a>

## :globe_with_meridians: 8. Proxy Support
Due to network restrictions, you may need to use a proxy server to access Google Drive. This tool supports HTTP and SOCKS proxies.
Supported formats:
	•	http://127.0.0.1:1080
	•	socks4://127.0.0.1:1080
	•	socks5://127.0.0.1:1080
	•	127.0.0.1:1080 (defaults to http)
	•	socks://127.0.0.1:1080 (defaults to socks5)

Proxy settings may come from:
    1. settings.yaml `proxy` field
    2. CLI `-p/--proxy` argument
    3. `GoogleDriveTools` class `proxy` parameter






