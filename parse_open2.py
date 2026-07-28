import os
import re

def find_2arg_open():
    found = False
    for root, dirs, files in os.walk('bng2/Perl2/'):
        for file in files:
            if not file.endswith('.pm') and not file.endswith('.pl') and not file.endswith('.t'):
                continue
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        # look for open something
                        # where there is only one comma inside the parens
                        if "open" in line and not "opendir" in line:
                            m = re.search(r'open\s*\(([^()]+)\)', line)
                            if m:
                                args = m.group(1).split(',')
                                if len(args) == 2:
                                    print(f"{path}:{i+1}: {line.strip()}")
                                    found = True
            except:
                pass
    return found

find_2arg_open()
