<h1 align="center">Google Drive Upload Tools</h1>

<p align="center">
 Created on 2025/12<br>
Tags: GoogleDrive, Upload, OAuth, Python, Proxy, Automation</p>

<p align="right">
  <strong>曲岳 Yue Qu</strong>
</p>

## Table of Contents
- [:pushpin: 1. Overview](#overview)
- [:package: 2. Installation](#installation)
- [:shield: 3. Get Google Drive API Credentials](#credentials)
- [:gear: 4. Configuration File: settings.yaml](#configuration)
- [:outbox_tray: 5. Upload Files to Google Drive](#upload)
- [:key: 6. OAuth Authentication](#oauth)
- [:globe_with_meridians: 7. Proxy Support](#proxy)


<a id="overview"></a>

# :pushpin: 1. Overview
This tool allows you to upload files to Google Drive using the Google Drive API with Python.
It supports:
- Single-file or multi-file uploading
- Custom target filenames
- Upload to a target Google Drive folder
- Optional proxy support (HTTP / SOCKS4 / SOCKS5)
- Automatic OAuth token handling
- Resumeable upload via Google Drive API
- Full logging support
- YAML-based configuration + CLI override

This tool is suitable for batch uploading scripts, large-file uploads, or automation workflows.

<a id="installation"></a>

##  :package: 2. Installation
Please install the required packages before running the code:

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib pysocks pyyaml
```

<a id="credentials"></a>

## :shield: 3. Get Google Drive API Credentials
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
proxy:

# Proxy server used for Google Drive upload (optional).
# Supported formats:
#   - 127.0.0.1:1080
#   - http://127.0.0.1:1080
#   - socks4://127.0.0.1:1080
#   - socks5://127.0.0.1:1080
# If null, no proxy is used.
proxy_server: socks://127.0.0.1:1080


# ============================================================
# Upload Settings
# ============================================================
upload:

# Local file path or list of local files to upload.
# Examples:
#   - "data.zip"
#   - ["a.txt", "b.txt"]
# If null, must be provided by CLI argument -n / --name.
local_file: file_path

# The filename(s) to be used in Google Drive.
# If null, Google Drive will use the local filename(s) by default.
# Must match the length of local_file if both are lists.
save_file_name: null

# The target folder ID in Google Drive.
# If null, uploads to the root directory ("My Drive").
save_folder_id: null

# Log file name.
# If null, log messages are printed to console only.
log: null
```
    
You may modify this YAML to set default behavior.

<a id="upload"></a>

## :outbox_tray: 5. Upload Files to Google Drive
We can run the `upload.py` script with different command line arguments for uploading files to Google Drive.

1. Basic command:
    ```bash
    python upload.py -n file.txt
    ```

2. Upload multiple files:
    ```bash
    python upload.py -n file1.txt file2.txt file3.txt
    ```

3. Upload into a specific Drive folder:
    ```bash
    python upload.py -n file.txt -i your_folder_id
    ```
    
    > **How to get a Google Drive folder ID**: 
    Open the target folder in Google Drive and look at the URL. The part after /folders/ is the folder ID.
    > Example: https://drive.google.com/drive/folders/1i93YFUQK5fbJUss_3rhwOyuAkMQgZjJk?dmr=1&ec=wgc-drive-globalnav-goto
    > In this case, the **folder ID** is: 1i93YFUQK5fbJUss_3rhwOyuAkMQgZjJk

4. Use a proxy:
    ```bash
    python upload.py -n file.txt --proxy socks5://127.0.0.1:1080
    ```

5. Specify a different credentials file:
    ```bash
    python upload.py -n file.txt --cred ./Json/my_credentials.json
    ```

6. Enable logging to a file:
    ```bash
    python upload.py -n file.txt --log upload.log
    ```

7. Command-Line Argumentsz: 

    | Argument | Description | Default | Default in settings.yaml |
    |---|---|---|---|
    | -n, <br>--name | One or more local files to upload | None | upload.local_file=file_path |
    | -s, <br>--save_file_name | One or more filenames to use in Google Drive, If None, uses local filenames | None | upload.save_file_name=null |
    | -i, <br>--save_folder_id | Destination folder ID in Google Drive, If None, uploads to root directory | None | upload.save_folder_id=null |
    | -p, <br>--proxy | Proxy server address, e.g., http://127.0.0.1:1080 if None, direct connection is used | None | proxy.proxy_server=socks://127.0.0.1:1080 |
    | -c, <br>--cred | Path to Google OAuth credentials JSON file, If None, uses default credentials file in settings.yaml| None | google_drive.credentials_file=./Json/credentials.json |
    | -l, <br>--log | Log file name, If None, logs to console only | None | upload.log=null |

    Example: Upload two files with custom names
    ```bash
    python upload.py \
    -n settings.yaml ReadMe.md \
    -s settings_backup.yaml readme_backup.md \
    -i 1i93YFUQK5fbJUss_3rhwOyuAkMQgZjJk \
    --proxy socks5://127.0.0.1:1080 \
    --log upload.log
    ```

<a id="oauth"></a>

## :key: 6. OAuth Authentication
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

## :globe_with_meridians: 7. Proxy Support
Due to network restrictions, you may need to use a proxy server to access Google Drive. This tool supports HTTP and SOCKS proxies.
Supported formats:
	•	http://127.0.0.1:1080
	•	socks4://127.0.0.1:1080
	•	socks5://127.0.0.1:1080
	•	127.0.0.1:1080 (defaults to http)
	•	socks://127.0.0.1:1080 (defaults to socks5)

Proxy settings may come from:
	•	command: --proxy
	•	setting.yaml: proxy.proxy_server






