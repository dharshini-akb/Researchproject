import os
import glob
import shutil

downloads_dir = r"C:\Users\DHARSHINI KAVITHA\Downloads"
dest = r"d:\finalresearchproject\scratch\ijms-23-05912-s001.zip"

print("Searching in Downloads...")
pattern = os.path.join(downloads_dir, "*5912*.zip")
files = glob.glob(pattern)
if files:
    print("Found in Downloads:", files)
    shutil.copy2(files[0], dest)
    print("Copied to:", dest)
else:
    print("Not found in Downloads. Listing files in Downloads:")
    if os.path.exists(downloads_dir):
        for f in os.listdir(downloads_dir):
            if "zip" in f.lower() or "ijms" in f.lower():
                print(f)

