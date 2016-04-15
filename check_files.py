#!/usr/bin/env python3

import sys
import os

file_name = os.path.basename(sys.argv[0])

excluded_files = [
    file_name, # Das eigene Script sollte immer ausgeschlossen werden
    ".travis.yml"
]

