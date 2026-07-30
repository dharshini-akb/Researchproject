import os
import json
import pandas as pd
from config import system_config
from utils import logger, metrics
from models.random_forest import RandomForestModel
from models.tabnet import TabNetModel

log = logger.get_logger("evaluate")

def load_test_data() -> tuple:
    base_dir = os.path.join(system_config.PROCESSED_DATA_DIR, "model_ready", "hpo_plus_sex")
    X_test = pd.read_csv(os.path.join(base_dir, "X_test.csv"))
    y_test = pd.read_csv(os.path.join(base_dir, "y_test.csv"))["target"]
    return X_test, y_test

def main():
    log.info("Starting model evaluation and comparative analysis...")
    X_test, y_test = load_test_data()
    
    # 1. Load Random Forest
    rf_path = os.path.join(system_config.ARTIFACTS_DIR, "rf_model.joblib")
    rf_model = RandomForestModel()
    rf_model.load(rf_path)
    
    # 2. Load TabNet
    tabnet_path = os.path.join(system_config.ARTIFACTS_DIR, "tabnet_model.pt")
    tabnet_model = TabNetModel()
    tabnet_model.load(tabnet_path)
    
    # 3. Evaluate RF
    rf_preds = rf_model.predict(X_test)
    rf_probs = rf_model.predict_proba(X_test)
    rf_metrics = metrics.compute_multiclass_metrics(y_test.values, rf_preds, rf_probs)
    
    # 4. Evaluate TabNet
    tabnet_preds = tabnet_model.predict(X_test)
    tabnet_probs = tabnet_model.predict_proba(X_test)
    tabnet_metrics = metrics.compute_multiclass_metrics(y_test.values, tabnet_preds, tabnet_probs)
    
    # Compare and choose winner
    winner = "Random Forest"
    if tabnet_metrics["f1_macro"] > rf_metrics["f1_macro"]:
        winner = "TabNet"
    elif tabnet_metrics["f1_macro"] == rf_metrics["f1_macro"]:
        # Tie breaker: accuracy
        if tabnet_metrics["accuracy"] > rf_metrics["accuracy"]:
            winner = "TabNet"
            
    comparison = {
        "metadata": {
            "num_test_samples": len(y_test),
            "winner_model": winner
        },
        "models": {
            "Random Forest": {
                "accuracy": rf_metrics["accuracy"],
                "precision_macro": rf_metrics["precision_macro"],
                "recall_macro": rf_metrics["recall_macro"],
                "f1_macro": rf_metrics["f1_macro"],
                "macro_auc": rf_metrics["macro_auc"],
                "confusion_matrix": rf_metrics["confusion_matrix"],
                "roc_auc": rf_metrics["roc_auc"],
                "per_class": rf_metrics["per_class"]
            },
            "TabNet": {
                "accuracy": tabnet_metrics["accuracy"],
                "precision_macro": tabnet_metrics["precision_macro"],
                "recall_macro": tabnet_metrics["recall_macro"],
                "f1_macro": tabnet_metrics["f1_macro"],
                "macro_auc": tabnet_metrics["macro_auc"],
                "confusion_matrix": tabnet_metrics["confusion_matrix"],
                "roc_auc": tabnet_metrics["roc_auc"],
                "per_class": tabnet_metrics["per_class"]
            }
        }
    }
    
    comparison_path = os.path.join(system_config.REPORTS_DIR, "model_comparison.json")
    with open(comparison_path, "w") as f:
        json.dump(comparison, f, indent=4)
        
    log.info(f"Successfully generated comparison report at {comparison_path}")
    log.info(f"Winner model: {winner}")
    print(f"Model comparison evaluation finished. Winner: {winner}")

if __name__ == "__main__":
    main()
