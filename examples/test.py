#%% Import Packages
# Basic
import os
import sys

# Change path to this file's parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
print('Changing working directory to:', parent_dir)
os.chdir(parent_dir)
sys.path.append(parent_dir)  # Ensure parent directory is in sys.path

# GDriveTools
from gdrivetools import GoogleDriveTools

# %%
gdt = GoogleDriveTools(settings_path="./settings.yaml",
                       proxy="socks5://127.0.0.1:1080",
                       log=None)

# %%
# results_up = gdt.upload2(local_file=["/Users/quyue/Downloads/gd_test", "ReadMe.md"],
#             # folder_id=None,
#             folder_id='10juIaCK-9zZj7M3cdAcDMcc6PXOuecXA',
#             folder_id = '1SIOPpcTCYmCgD0HxGIx_Kp7QPY_7glkv'
#             )

# %%
a = gdt.download2(['10juIaCK-9zZj7M3cdAcDMcc6PXOuecXA'], 
                  save_local_dir='./downloads_test', 
                  chunksize=1024*1024)

# %% 
