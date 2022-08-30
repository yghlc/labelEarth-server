#!/usr/bin/env python
# Filename: backdata.py 
"""
introduction:

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 29 August, 2022
"""

import os,sys
from datetime import datetime
import glob
import shutil
import filecmp

back_files = ['labelEarthServer_db.json','admin.json','imageObjects.json','image.json','user.json','userinput.json']

def is_two_file_different(file1,file2):
    # deep comparison: where the content of the files are compared.
    # True if the files are the same, False otherwise.
    result = filecmp.cmp(file1, file2, shallow=False)
    return not result   # return not the same (different)

def get_latest_bak(file_name):
    file_pattern = os.path.join('./', 'bak*'+file_name)
    file_list = glob.glob(file_pattern)
    if len(file_list) < 1:
        return None
    else:
        return sorted(file_list)[-1]  # the newest one

def get_save_bak_name(file_name):
    date_str = datetime.now().strftime('%Y%m%d')
    for idx in range(100):
        bak_name = 'bak'+date_str+ '_' + str(idx).zfill(2) + '_' + file_name
        if os.path.isfile(bak_name):
            continue
        return bak_name

def main():
    # check if files are different
    for file in back_files:
        bak = get_latest_bak(file)
        if bak is None or is_two_file_different(bak,file):
            # backup
            new_bak = get_save_bak_name(file)
            shutil.copy(file, new_bak)


if __name__ == '__main__':
    main()