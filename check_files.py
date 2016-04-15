#!/usr/bin/env python3

import sys
import os
from pprint import pprint

file_name = os.path.basename(sys.argv[0])

excluded_files = [
    file_name, # Das eigene Script sollte immer ausgeschlossen werden
    ".travis.yml",
    ".gitignore",
    "README.md",
    ".git",
    ".idea",# wird nur für die Entwicklung gebraucht
]

excluded_files = ["./" + f for f in excluded_files]

files_for_check = []
root_dir = '.'
for dir_name, subdir_list, file_list in os.walk(root_dir):
    if dir_name in excluded_files:
        if len(subdir_list) > 0:
            del subdir_list[:]
        continue
    for f_name in file_list:
        f_name = dir_name + '/' + f_name
        if f_name not in excluded_files:
            files_for_check.append(f_name)
