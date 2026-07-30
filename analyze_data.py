import os
import pandas as pd
from collections import Counter
from config import system_config
from utils import logger

log = logger.get_logger("analyze_data")

def main():
    hpoa_path = os.path.join(system_config.RAW_DATA_DIR, "phenotype.hpoa")
    log.info(f"Loading phenotype.hpoa from {hpoa_path}...")
    
    # Read the TSV file, skipping lines starting with '#'
    df = pd.read_csv(hpoa_path, sep="\t", comment="#")
    
    print("\n=== DATASET OVERVIEW ===")
    print("Columns:", list(df.columns))
    print("Total rows:", len(df))
    
    # 1. Total diseases
    # The disease ID is usually under column 'database_id'
    db_id_col = 'database_id' if 'database_id' in df.columns else df.columns[0]
    total_diseases = df[db_id_col].nunique()
    print("Total unique diseases:", total_diseases)
    
    # 2. Disease identifier types (e.g. OMIM, ORPHA, DECIPHER, MONDO)
    # They are prefixes in the database_id column
    prefixes = df[db_id_col].apply(lambda x: str(x).split(":")[0])
    prefix_counts = prefixes.value_counts()
    print("\nDisease identifier types and counts:")
    for prefix, count in prefix_counts.items():
        print(f"  - {prefix}: {count} annotations")
        
    # 3. Total HPO terms
    hpo_col = 'hpo_id' if 'hpo_id' in df.columns else 'HPO_ID'
    total_hpos = df[hpo_col].nunique()
    print("\nTotal unique HPO terms:", total_hpos)
    
    # 4. Missing values
    print("\nMissing values per column:")
    for col in df.columns:
        missing = df[col].isna().sum()
        print(f"  - {col}: {missing} missing ({missing/len(df)*100:.2f}%)")
        
    # 5. Duplicate entries
    # Duplicates defined as duplicate rows of (database_id, hpo_id)
    duplicates = df.duplicated(subset=[db_id_col, hpo_col]).sum()
    print(f"\nDuplicate entries (same database_id and hpo_id): {duplicates} ({duplicates/len(df)*100:.2f}%)")
    
    # 6. Number of annotations per disease
    annotations_per_disease = df[db_id_col].value_counts()
    print("\nAnnotations per disease stats:")
    print(annotations_per_disease.describe())
    
    # Let's see some top annotated diseases
    print("\nTop 15 most annotated diseases:")
    # We can also map disease names if 'disease_name' column exists
    name_col = 'disease_name' if 'disease_name' in df.columns else 'name'
    top_diseases = df.groupby([db_id_col, name_col]).size().sort_values(ascending=False).head(30)
    for (db_id, name), count in top_diseases.items():
        print(f"  - {db_id} | {name}: {count} annotations")

if __name__ == "__main__":
    main()
