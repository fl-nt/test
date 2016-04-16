#!/usr/bin/env python3

import sys
import os
import re
import ipaddress

MIN_KEY_LENGTH = 64
MAX_KEY_LENGTH = 64

FAILURE_MESSAGE_KEY_LENGTH = "Key \"%s\" in file \"%s\":%d has wrong length"
FAILURE_MESSAGE_MULTI_KEYS = "Key \"%s\" in file \"%s\":%d is another key in file"

FAILURE_MESSAGE_MULTI_REMOTS = "Remote \"%s:%d\" in file \"%s\":%d is another remote in file"
FAILURE_MESSAGE_WRONG_HOST = "Remote host \"%s\" in file \"%s\":%d is neither a host nor a IP address"
FAILURE_MESSAGE_WRONG_PORT = "Remote port \"%d\" in file \"%s\":%d port is not valid"

FAILURE_MESSAGE_UNKNOWN_PATTERN = "Line %d in file \"%s\" has unknown format: %s"

FAILURE_MESSAGE_NO_KEY = "File \"%s\" has no key"

ldh_re = re.compile('^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$', re.IGNORECASE)


key_re = re.compile('^key "([a-f0-9]+)";$')
remote_re = re.compile('^remote "([^"]+)" port ([0-9]{1,5});$')

def validate_fqdn(dn):
    if dn.endswith('.'):
        dn = dn[:-1]
    if len(dn) < 1 or len(dn) > 253:
        return False
    return all(ldh_re.match(x) for x in dn.split('.'))

def validate_IP(ip):
    try:
        ipaddress.ip_address(ip)
    except:
        return False
    return True

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

failures = []

for file_name in files_for_check:
    has_remote = False
    has_key = False
    line_counter = 0
    with open(file_name, "r") as lines:
        for line in lines:
            line_counter += 1
            line = line.strip()
            if line == "" or line.startswith('#'):
                continue

            key_match = key_re.match(line)
            remote_match = remote_re.match(line)

            if key_match:
                key = key_match.group(1)
                if has_key:
                    failures.append(FAILURE_MESSAGE_MULTI_KEYS % (key, file_name, line_counter))
                has_key = True
                if len(key) < MIN_KEY_LENGTH or len(key) > MAX_KEY_LENGTH:
                    failures.append(FAILURE_MESSAGE_KEY_LENGTH % (key, file_name, line_counter))

            elif remote_match:
                host = remote_match.group(1)
                port = int(remote_match.group(2))
                if has_remote:
                    failures.append(FAILURE_MESSAGE_MULTI_REMOTS % (host, port, file_name, line_counter))
                has_remote = True

                if not validate_fqdn(host) and not validate_IP(host):
                    failures.append(FAILURE_MESSAGE_WRONG_HOST % (host, file_name, line_counter))

                if port < 1 or port > 65535:
                    failures.append(FAILURE_MESSAGE_WRONG_PORT % (port, file_name, line_counter))
            else:
                failures.append(FAILURE_MESSAGE_UNKNOWN_PATTERN % (line_counter, file_name, line))

    if not has_key:
        failures.append(FAILURE_MESSAGE_NO_KEY % (file_name))


print('\n'.join(failures), file=sys.stderr)

if len(failures) > 0:
    sys.exit(1)
