import urllib.request
import zipfile
import os

urls = [
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9180463/bin/ijms-23-05912-s001.zip",
    "https://www.ncbi.nlm.nih.gov/articles/instance/9180463/bin/ijms-23-05912-s001.zip"
]

dest_zip = r"d:\finalresearchproject\scratch\ijms-23-05912-s001.zip"
extract_dir = r"d:\finalresearchproject\scratch\pmc9180463_supp"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9'
}

for url in urls:
    print("Trying URL:", url)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data = response.read()
        print("Downloaded. Size:", len(data))
        with open(dest_zip, 'wb') as out_file:
            out_file.write(data)
        
        # Try to unzip
        with zipfile.ZipFile(dest_zip, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print("Success! Extracted to:", extract_dir)
        print("Files:", os.listdir(extract_dir))
        break
    except Exception as e:
        print("Failed for", url, ":", e)
