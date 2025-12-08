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
import sys
import argparse

# Self-defined
from .core import GoogleDriveTools


#%% Build Parser
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gdrive-tools",
        description="Google Drive upload/download tools with settings.yaml support."
    )

    # ----- Commands -----
    parser.add_argument(
        "--settings",
        default="settings.yaml",
        help="Path to settings.yaml. Default: settings.yaml"
    )
    parser.add_argument(
        "-c","--cred",
        help=(
            "Override path to Google OAuth credentials JSON file.",
            "If omitted, uses settings.google_api.credentials_path."
        )
    )
    parser.add_argument(
        "-l","--log",
        help=(
            "Override path to log file.", 
            "If omitted, uses settings.log.",
            "If set to 'off', logs will be printed to standard output."
        )
    )
    parser.add_argument(
        "-p","--proxy",
        help=(
            "Override proxy server address.", 
            "If omitted, uses settings.proxy.", 
            "If set to 'off', no proxy will be used (direct connection). ",
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
        required=True,
        help=(
            "One or more local file paths to upload. "
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
        required=True,
        dest="file_id",
        help=(
            "One or more Google Drive file IDs to download. "
            "e.g., -f 1AbCdEfGhIjK "
            "or  -f id1 id2 id3"
        )
    )
    download_parser.add_argument(
        "-o", "--out-dir",
        dest="out_dir",
        help=(
            "Local directory to save downloaded files. "
            "If omitted, the current working directory will be used. "
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

    # ---------- Step1. Get Settings and Initialize GoogleDriveTools ----------
    # ----- step 1.1 get base settings from settings.yaml -----
    gdt_args = {'settings_path': args.settings}
    print('cred:', args.cred)
    if args.cred:
        gdt_args['cred_file'] = args.cred
    print('log:', args.log)
    if args.log:
        if args.log.lower() == "off":
            gdt_args['log_file'] = None
        else:
            gdt_args['log_file'] = args.log
    print('proxy:', args.proxy)
    if args.proxy:
        if args.proxy.lower() == "off":
            gdt_args['proxy'] = None
        else:
            gdt_args['proxy'] = args.proxy
    
"""
    ## step 1.2 initialize tools with settings.yaml
    gdt = GoogleDriveTools(**gdt_args)

    # ## step 1.2 override settings if CLI args provided
    # if args.cred:
    #     try:
    #         gdt.settings.google_drive.credentials_file = args.cred
    #     except AttributeError:
    #         gdt.logger.warning("CLI --cred provided, but settings.google_drive.credentials_file not found.")

    # if args.log:
    #     # e.g., settings.log.path 或 upload.log
    #     if args.log.lower() == "stdout":
    #         # 具体如何重建 logger，看你 core.py 里怎么写的
    #         gdt.logger.info("CLI --log=stdout provided, logging will go to stdout if supported.")
    #         # 这里可以选择调用你在 core 里写的重建 logger 的函数
    #     else:
    #         try:
    #             gdt.settings.log.path = args.log
    #         except AttributeError:
    #             try:
    #                 gdt.settings.upload.log = args.log
    #             except AttributeError:
    #                 gdt.logger.warning("CLI --log provided, but no matching log path in settings.")
    # if args.proxy:
    #     # "disable" 的特殊逻辑
    #     if args.proxy.lower() == "disable":
    #         try:
    #             gdt.settings.proxy = None
    #         except AttributeError:
    #             gdt.logger.warning("CLI --proxy=disable provided, but settings.proxy.proxy_server not found.")
    #     else:
    #         try:
    #             gdt.settings.proxy = args.proxy
    #         except AttributeError:
    #             gdt.logger.warning("CLI --proxy provided, but settings.proxy.proxy_server not found.")

    # Step 2. Handle Sub-Commands
    ## step 2.1 upload
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
        # Print summary to stdout
        for src, fid in results:
            print(f"Uploaded: {src} -> fileId={fid}")

    elif args.command == "download":
        # args.file_id: list[str]
        # args.out_dir: str or None
        file_ids = args.file_id
        out_dir = args.out_dir
        results = gdt.download(
            file_id=file_ids,
            save_local_dir=out_dir
        )

        # results 可能含有 None（下载失败的情况）
        for fid, path in zip(file_ids, results):
            if path is None:
                print(f"Download failed: fileId={fid}", file=sys.stderr)
            else:
                print(f"Downloaded: fileId={fid} -> {path}")

    else:
        # 理论上不会到这里，因为 subparsers 设置了 required=True
        parser.error("Unknown command.")
        return 1

    return 0
"""


if __name__ == "__main__":
    raise SystemExit(main())
# %%
