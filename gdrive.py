# -*- encoding: utf-8 -*-
'''
@Time     :   2025/11/24 17:11:42
@Author   :   QuYue
@File     :   gdrive.py
@Email    :   quyue1541@gmail.com
@Desc:    :   gdrive
'''

#%% Import Packages

import sys
from .core import GoogleDriveTools


def main(argv: list[str] | None = None) -> int:
    """
    Entry point for the gdrive-tools CLI.

    Parameters
    ----------
    argv : list[str] or None
        Command-line arguments excluding the program name.
        If None, sys.argv[1:] will be used.

    Returns
    -------
    int
        Exit code (0 for success, non-zero for failure).
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()
    args = parser.parse_args(argv)

    # ---- Initialize tools with settings.yaml ----
    # 这里假设你的 GoogleDriveTools 构造函数至少有 settings_path 参数
    # 如果你在 core.py 里给 __init__ 加了 log/cred/proxy 参数，可以在这里一起传进去
    gdt = GoogleDriveTools(settings_path=args.settings)

    # ---- Apply CLI overrides to settings (if provided) ----
    # 注意：这里是直接改 gdt.settings，保证和 settings.yaml 合并逻辑一致
    if args.cred:
        # e.g., settings.google_api.credentials_path
        try:
            gdt.settings.google_api.credentials_path = args.cred
        except AttributeError:
            # 如果你的字段名是 google_drive.credentials_file，可以改成下面这行
            # gdt.settings.google_drive.credentials_file = args.cred
            gdt.logger.warning("CLI --cred provided, but settings.google_api.credentials_path not found.")

    if args.log:
        # e.g., settings.log.path 或 upload.log
        if args.log.lower() == "stdout":
            # 具体如何重建 logger，看你 core.py 里怎么写的
            gdt.logger.info("CLI --log=stdout provided, logging will go to stdout if supported.")
            # 这里可以选择调用你在 core 里写的重建 logger 的函数
        else:
            try:
                gdt.settings.log.path = args.log
            except AttributeError:
                try:
                    gdt.settings.upload.log = args.log
                except AttributeError:
                    gdt.logger.warning("CLI --log provided, but no matching log path in settings.")

    if args.proxy:
        # "disable" 的特殊逻辑
        if args.proxy.lower() == "disable":
            try:
                gdt.settings.proxy.proxy_server = None
            except AttributeError:
                gdt.logger.warning("CLI --proxy=disable provided, but settings.proxy.proxy_server not found.")
        else:
            try:
                gdt.settings.proxy.proxy_server = args.proxy
            except AttributeError:
                gdt.logger.warning("CLI --proxy provided, but settings.proxy.proxy_server not found.")

    # 如果你的 GoogleDriveTools 里有类似 “重新根据 settings 初始化 logger / proxy / service” 的方法，
    # 比如 gdt.reload_from_settings()，可以在这里调用：
    # gdt.reload_from_settings()

    # ---- Handle sub-commands ----
    if args.command == "upload":
        # args.name: list[str]
        # args.save_name: list[str] or None
        # args.folder_id: str or None
        results = gdt.upload(
            local_file=args.name,
            save_file_name=args.save_name,
            folder_id=args.folder_id,
        )
        # results: list[(local_path, file_id)]
        for src, fid in results:
            print(f"Uploaded: {src} -> fileId={fid}")

    elif args.command == "download":
        # args.file_id: list[str]
        # args.out_dir: str or None
        results = gdt.download(
            file_id=args.file_id,
            save_local_dir=args.out_dir,
        )
        # 假设 download 返回 list[str | None]
        for fid, path in zip(args.file_id, results):
            if path is None:
                print(f"Download failed: fileId={fid}", file=sys.stderr)
            else:
                print(f"Downloaded: fileId={fid} -> {path}")

    else:
        # 理论上不会到这里，因为 subparsers 设置了 required=True
        parser.error("No command specified.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())