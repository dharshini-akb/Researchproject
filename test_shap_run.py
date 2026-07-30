import os
import pandas as pd
from config import system_config
from models.random_forest import RandomForestModel
from models.tabnet import TabNetModel
from explainability.shap_explainer import RareDiseaseExplainer

def test():
    base_dir = os.path.join(system_config.PROCESSED_DATA_DIR, "model_ready", "hpo_plus_sex")
    X_train = pd.read_csv(os.path.join(base_dir, "X_train.csv"))
    X_test = pd.read_csv(os.path.join(base_dir, "X_test.csv"))
    
    # 1. Load models
    rf_path = os.path.join(system_config.ARTIFACTS_DIR, "rf_model.joblib")
    rf_model = RandomForestModel()
    rf_model.load(rf_path)
    
    tabnet_path = os.path.join(system_config.ARTIFACTS_DIR, "tabnet_model.pt")
    tabnet_model = TabNetModel()
    tabnet_model.load(tabnet_path)
    
    # 2. Initialize Explainer
    explainer = RareDiseaseExplainer()
    # Initialize with a small subset of X_train as background
    explainer.initialize_rf_explainer(rf_model, X_train.head(50))
    
    # Explain single sample
    sample_df = X_test.head(1)
    
    # RF
    rf_explanation = explainer.explain_patient_rf(sample_df)
    print("Random Forest Local Explanation classes:", list(rf_explanation.keys()))
    print("RF Class 0 top 5 features:")
    sorted_features = sorted(rf_explanation[0].items(), key=lambda x: abs(x[1]), reverse=True)
    for feat, val in sorted_features[:5]:
        print(f"  - {feat}: {val:.4f}")
        
    # TabNet
    tabnet_explanation = explainer.explain_patient_tabnet(tabnet_model, sample_df)
    print("\nTabNet top 5 attention features:")
    sorted_tabnet = sorted(tabnet_explanation.items(), key=lambda x: x[1], reverse=True)
    for feat, val in sorted_tabnet[:5]:
        print(f"  - {feat}: {val:.4f}")

if __name__ == "__main__":
    test()
