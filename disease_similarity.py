import os
import pandas as pd
from config import system_config

def main():
    hpoa_path = os.path.join(system_config.RAW_DATA_DIR, "phenotype.hpoa")
    df = pd.read_csv(hpoa_path, sep="\t", comment="#")
    
    # Target diseases
    target_omims = ["OMIM:616364", "OMIM:615829", "OMIM:148050"]
    
    print("=== ANNOTATION DETAILS FOR PREVIOUS TARGET DISEASES ===")
    for omim in target_omims:
        sub = df[df['database_id'] == omim]
        if not sub.empty:
            name = sub['disease_name'].iloc[0]
            print(f"{omim} | {name}: {len(sub)} annotations")
        else:
            print(f"{omim}: NOT FOUND in phenotype.hpoa")
            
    # Compute HPO symptom overlap between these three diseases
    symptom_sets = {}
    for omim in target_omims:
        sub = df[df['database_id'] == omim]
        if not sub.empty:
            symptom_sets[omim] = set(sub['hpo_id'].dropna())
            
    if len(symptom_sets) == 3:
        omims = list(symptom_sets.keys())
        def jaccard(set1, set2):
            return len(set1.intersection(set2)) / len(set1.union(set2))
            
        print("\n=== JACCARD PHENOTYPIC SIMILARITY OVERLAPS ===")
        j_01 = jaccard(symptom_sets[omims[0]], symptom_sets[omims[1]])
        j_02 = jaccard(symptom_sets[omims[0]], symptom_sets[omims[2]])
        j_12 = jaccard(symptom_sets[omims[1]], symptom_sets[omims[2]])
        
        print(f"Jaccard({omims[0]}, {omims[1]}): {j_01:.3f} ({len(symptom_sets[omims[0]].intersection(symptom_sets[omims[1]]))} common symptoms)")
        print(f"Jaccard({omims[0]}, {omims[2]}): {j_02:.3f} ({len(symptom_sets[omims[0]].intersection(symptom_sets[omims[2]]))} common symptoms)")
        print(f"Jaccard({omims[1]}, {omims[2]}): {j_12:.3f} ({len(symptom_sets[omims[1]].intersection(symptom_sets[omims[2]]))} common symptoms)")
        
        # Check overall intersection
        intersection_all = symptom_sets[omims[0]].intersection(symptom_sets[omims[1]]).intersection(symptom_sets[omims[2]])
        print(f"\nTriple intersection (symptoms common to all three): {len(intersection_all)}")
        print("Example common symptoms:", list(intersection_all)[:10])

if __name__ == "__main__":
    main()
