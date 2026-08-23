import urllib.request
import zipfile
import os

url = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9180463/bin/ijms-23-05912-s001.zip"
dest_zip = r"d:\finalresearchproject\scratch\ijms-23-05912-s001.zip"
extract_dir = r"d:\finalresearchproject\scratch\pmc9180463_supp"

print("Downloading:", url)
try:
    # Use headers to avoid 403 Forbidden
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    with urllib.request.urlopen(req) as response, open(dest_zip, 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    print("Downloaded. Size:", len(data))
    
    # Extract
    with zipfile.ZipFile(dest_zip, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print("Extracted to:", extract_dir)
    print("Files in extract_dir:", os.listdir(extract_dir))
except Exception as e:
    print("Error:", e)
