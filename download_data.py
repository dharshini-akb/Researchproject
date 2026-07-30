import os
import urllib.request
from config import system_config
from utils import logger

log = logger.get_logger("download_data")

def download_file(url: str, dest_path: str):
    log.info(f"Downloading {url} to {dest_path}...")
    try:
        # Define a user-agent to prevent download blocking
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            with open(dest_path, 'wb') as out_file:
                out_file.write(response.read())
        log.info(f"Successfully downloaded {os.path.basename(dest_path)}")
    except Exception as e:
        log.error(f"Failed to download {url}: {e}")
        raise

def main():
    raw_dir = system_config.RAW_DATA_DIR
    os.makedirs(raw_dir, exist_ok=True)
    
    hpoa_url = "https://github.com/obophenotype/human-phenotype-ontology/releases/latest/download/phenotype.hpoa"
    hpo_url = "https://github.com/obophenotype/human-phenotype-ontology/releases/latest/download/hp.obo"
    
    hpoa_dest = os.path.join(raw_dir, "phenotype.hpoa")
    hpo_dest = os.path.join(raw_dir, "hp.obo")
    
    # Download phenotype.hpoa
    download_file(hpoa_url, hpoa_dest)
    
    # Download hp.obo
    download_file(hpo_url, hpo_dest)
    
    print("Download task completed.")

if __name__ == "__main__":
    main()
