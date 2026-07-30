import os
import json
from config import system_config

def main():
    res_path = os.path.join(system_config.REPORTS_DIR, "scientific_validation_results.json")
    with open(res_path, "r") as f:
        data = json.load(f)
        
    print("=== LEAKAGE STATISTICS ===")
    print(json.dumps(data["leakage_statistics"], indent=2))
    
    print("\n=== RANDOM FOREST CROSS VALIDATION ===")
    print(json.dumps(data["rf_cross_validation"], indent=2))
    
    print("\n=== TABNET OPTIMIZED RESULT ===")
    print(json.dumps(data["tabnet_optimized"], indent=2))
    
    # Check top features globally
    print("\n=== RF TOP GLOBAL FEATURES (CLASS 0) ===")
    rf_g = data["global_importance_rf"]["0"]
    sorted_g = sorted(rf_g.items(), key=lambda x: x[1], reverse=True)[:5]
    for k, v in sorted_g:
        print(f"  - {k}: {v:.5f}")

if __name__ == "__main__":
    main()
