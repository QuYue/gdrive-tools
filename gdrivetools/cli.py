#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command-line interface for GoogleDriveTools.

Usage examples
--------------

# Upload one file
gdrive-tools upload -n data.zip

# Upload multiple files
gdrive-tools upload -n a.txt b.txt

# Upload with custom save names and folder ID
gdrive-tools upload -n a.txt b.txt -s a_drive.txt b_drive.txt -i <folder_id>

# Download one file by file_id
gdrive-tools download -f 1AbCdEfGhIjK

# Download multiple files into a specific directory
gdrive-tools download -f id1 id2 id3 -o ./downloads
"""

#%% Import Packages
# Basic
import os
import sys
import argparse

# Self-defined
from .core import GoogleDriveTools
from .utils import AttrDict


#%% Build Parser
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gdrive-tools",
        description="Google Drive upload/download tools with settings.yaml support."
    )

    # ----- Commands -----
    parser.add_argument(
        "-s", "--settings",
        default="settings.yaml",
        help=(
            "Override path to settings YAML file."
            "If omitted, uses 'settings.yaml'."
            "If the file does not exist or set to 'off', default settings will be used."
        )
    )
    parser.add_argument(
        "-c", "--cred",
        help=(
            "Override path to Google OAuth credentials JSON file."
            "If omitted, uses settings.google_api.credentials_path."
        )
    )
    parser.add_argument(
        "-l", "--log",
        help=(
            "Override path to log file."
            "If omitted, uses settings.log."
            "If set to 'off', logs will be printed to standard output."
        )
    )
    parser.add_argument(
        "-p", "--proxy",
        help=(
            "Override proxy server address."
            "If omitted, uses settings.proxy."
            "If set to 'off', no proxy will be used (direct connection). "
            "Format: [type://]host:port. Type can be in [http, socks4, socks5]. "
            "e.g., 127.0.0.1:1080 | http://127.0.0.1:1080 | socks5://127.0.0.1:1080"
        )
    )
    # ----- Subcommands -----
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Sub-commands: upload, download"
    )

    # ---------- Upload subcommand ----------
    upload_parser = subparsers.add_parser(
        "upload",
        help="Upload one or multiple files to Google Drive."
    )
    upload_parser.add_argument(
        "-n", "--name",
        nargs="+",
        help=(
            "One or more local file paths to upload. "
            "If omitted, uses settings.upload.local_file. "
            "e.g., -n data.zip "
            "or -n a.txt b.txt"
        )
    )
    upload_parser.add_argument(
        "-s", "--save-name",
        nargs="+",
        dest="save_name",
        help=(
            "Optional custom filenames to use in Google Drive. "
            "If omitted, Drive uses local filenames. "
            "e.g., -s upload_a.txt upload_b.txt"
        )
    )
    upload_parser.add_argument(
        "-i", "--folder-id",
        dest="folder_id",
        help=(
            "Google Drive folder ID to store uploaded files. "
            "If omitted, uses settings.upload.save_folder_id or the Drive root directory. "
            "e.g., -i 1i93YFUQK5fbJUss_3rhwOyuAkMQgZjJk"
        )
    )

    # ---------- Download subcommand ----------
    download_parser = subparsers.add_parser(
        "download",
        help="Download one or multiple files from Google Drive."
    )
    download_parser.add_argument(
        "-f", "--file-id",
        nargs="+",
        dest="file_id",
        help=(
            "One or more Google Drive file IDs to download. "
            "If omitted, uses settings.download.file_id. "
            "e.g., -f 1AbCdEfGhIjK "
            "or  -f id1 id2 id3"
        )
    )
    download_parser.add_argument(
        "-o", "--out-dir",
        dest="out_dir",
        help=(
            "Local directory to save downloaded files. "
            "If omitted, uses settings.download.save_local_dir. "
            "Directory will be created automatically if it does not exist. "
            "e.g., -o ./downloads"
        )
    )
    # Return the constructed parser
    return parser


#%% Main Function
def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()
    args = parser.parse_args(argv)
    gdt_args = {}
"""
    # ---------- Step1. Get Settings and Initialize GoogleDriveTools ----------
    # ----- step 1.1 get base settings from settings.yaml -----
    # settings
    if args.settings.lower() == "off":
        settings = None
    else:
        settings = args.settings
    gdt_args = {'settings_path': settings}
    # cred
    if args.cred:
        gdt_args['cred_file'] = args.cred
    # log
    if args.log:
        gdt_args['log'] = args.log
    # proxy
    if args.proxy:
        gdt_args['proxy'] = args.proxy

    # ----- step 1.2 initialize GoogleDriveTools -----
    gdt = GoogleDriveTools(**gdt_args, show_settings=True)

    # ---------- Step 2. Handle Sub-Commands ----------
    # ----- step 2.1 upload ----- 
    if args.command == "upload":
        # args.name: list[str]
        # args.save_name: list[str] or None
        # args.folder_id: str or None
        local_files = args.name
        save_names = args.save_name
        folder_id = args.folder_id
        # Call upload
        results = gdt.upload(
            local_file=local_files,
            save_file_name=save_names,
            folder_id=folder_id
        )
    elif args.command == "download":
        # args.file_id: list[str]
        # args.out_dir: str or None
        file_ids = args.file_id
        out_dir = args.out_dir
        results = gdt.download(
            file_id=file_ids,
            save_local_dir=out_dir
        )
    else:
        # 理论上不会到这里，因为 subparsers 设置了 required=True
        parser.error("Unknown command.")
        return 1

    return 0
"""

#%% Run Main
if __name__ == "__main__":
    raise SystemExit(main())
