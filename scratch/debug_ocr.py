import os
import json
import re
from config import system_config
from utils import ocr_helper

def main():
    vocab_path = os.path.join(system_config.PREPROC_ARTIFACTS_DIR, "hpo_feature_vocabulary.json")
    obo_path = os.path.join(system_config.RAW_DATA_DIR, "hp.obo")
    hpo_synonyms = ocr_helper.load_hpo_synonyms(vocab_path, obo_path)
    
    print(f"Loaded {len(hpo_synonyms)} synonym maps.")
    
    # Let's print some sample entries
    sample_keys = list(hpo_synonyms.keys())[:5]
    for k in sample_keys:
        print(f"  {k}: {hpo_synonyms[k]}")
        
    note = """
    Patient Name: John Doe
    Age: 5 years
    Sex: Male
    Chief Complaints:
    - The child has developmental delay and speech delay.
    - We noticed microcephaly and hypotonia during examination.
    - Patient shows autistic behavior.
    """
    
    raw_lines = [line.strip() for line in note.split('\n') if line.strip()]
    print("\nRaw lines:")
    for line in raw_lines:
        print(f"  {line}")
        
    mapped, unmatched, ignored_dem, ignored_adm, rejected = ocr_helper.extract_and_map_text(note, hpo_synonyms)
    
    print(f"\nMapped: {mapped}")
    print(f"Unmatched: {unmatched}")
    print(f"Ignored Demographics: {ignored_dem}")
    print(f"Ignored Administrative: {ignored_adm}")
    print(f"Rejected: {rejected}")

if __name__ == "__main__":
    main()
