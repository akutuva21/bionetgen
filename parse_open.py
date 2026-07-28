import os
import re

def find_2arg_open():
    found = False
    for root, dirs, files in os.walk('bng2/Perl2/'):
        for file in files:
            if not file.endswith('.pm') and not file.endswith('.pl'):
                continue
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if "open" in line and not "3-argument" in line and not "opendir" in line:
                        # simple regex for two arguments
                        # open(FH, $file) or open FH, $file
                        # we'll exclude obvious 3 arg
                        m = re.search(r'open\s*\(\s*([^,]+?)\s*,\s*([^,]+?)\s*\)', line)
                        if m:
                            arg2 = m.group(2).strip()
                            if arg2 not in ["'>'", "'<'", "\">\"", "\"<\"", "'>|'", "'-|'"]:
                                print(f"{path}:{i+1}: {line.strip()}")
                                found = True
    return found

find_2arg_open()
