import os
import glob
import shutil

brain_dir = r"C:\Users\DHARSHINI KAVITHA\.gemini\antigravity-ide\brain\39aa88c2-d338-4e3e-8fab-794c75f64210"
print("Searching for zip files in brain directory:", brain_dir)

found = []
for root, dirs, files in os.walk(brain_dir):
    for f in files:
        if f.endswith(".zip") or "5912" in f:
            full_path = os.path.join(root, f)
            print(f"Found file: {full_path} (Size: {os.path.getsize(full_path)} bytes)")
            found.append(full_path)

if found:
    # Copy the largest zip to scratch (if multiple)
    zip_files = [x for x in found if x.endswith(".zip")]
    if zip_files:
        best = max(zip_files, key=os.path.getsize)
        dest = r"d:\finalresearchproject\scratch\ijms-23-05912-s001.zip"
        shutil.copy2(best, dest)
        print("Copied best zip to:", dest)
