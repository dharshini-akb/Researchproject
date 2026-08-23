import os
import glob

search_paths = [
    r"C:\Users\DHARSHINI KAVITHA\AppData\Local\Temp\*",
    r"C:\Users\DHARSHINI KAVITHA\Downloads\*",
    r"C:\Users\DHARSHINI KAVITHA\*",
]

print("Searching for *s001.zip or *5912*...")
for pattern in search_paths:
    for path in glob.glob(pattern):
        # check if it is a directory and search inside it
        if os.path.isdir(path):
            try:
                for sub in os.listdir(path):
                    if "5912" in sub or "s001.zip" in sub:
                        print("Found inside directory:", os.path.join(path, sub))
            except Exception:
                pass
        else:
            if "5912" in path or "s001.zip" in path:
                print("Found file:", path)
