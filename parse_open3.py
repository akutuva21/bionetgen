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
                        # count commas inside outer open(...)
                        m = re.search(r'\bopen\s*\((.*)\)', line)
                        if m:
                            inner = m.group(1)
                            # count commas not inside quotes (simple approximation)
                            # if it has < 2 commas, it's a 2-arg open
                            if inner.count(',') < 2:
                                print(f"{path}:{i+1}: {line.strip()}")
            except:
                pass
    return found

find_2arg_open()
