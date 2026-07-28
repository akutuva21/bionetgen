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
                        if "open" in line and not "opendir" in line:
                            # look for open FILEHANDLE, $file
                            m = re.search(r'\bopen\s+([A-Za-z0-9_]+)\s*,\s*([^,]+?)\s*($|or|\|\|)', line)
                            if m:
                                arg2 = m.group(2).strip()
                                if not arg2.startswith("'<") and not arg2.startswith("'>"):
                                    print(f"{path}:{i+1}: {line.strip()}")
            except:
                pass
    return found

find_2arg_open()
