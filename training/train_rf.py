import os
import json
import pandas as pd
from config import system_config
from utils import logger, metrics
from models.random_forest import RandomForestModel

log = logger.get_logger("train_rf")

def load_data(config_name: str = "hpo_plus_sex") -> tuple:
    """
    Loads train, validation, and test datasets for the given configuration folder name.
    """
    base_dir = os.path.join(system_config.PROCESSED_DATA_DIR, "model_ready", config_name)
    log.info(f"Loading data from {base_dir}")
    
    X_train = pd.read_csv(os.path.join(base_dir, "X_train.csv"))
    y_train = pd.read_csv(os.path.join(base_dir, "y_train.csv"))["target"]
    
    X_val = pd.read_csv(os.path.join(base_dir, "X_validation.csv"))
    y_val = pd.read_csv(os.path.join(base_dir, "y_validation.csv"))["target"]
    
    X_test = pd.read_csv(os.path.join(base_dir, "X_test.csv"))
    y_test = pd.read_csv(os.path.join(base_dir, "y_test.csv"))["target"]
    
    return X_train, y_train, X_val, y_val, X_test, y_test

def main():
    # We will train on HPO + Sex (CONFIG_B) by default
    config_type = "hpo_plus_sex"
    log.info(f"Starting Random Forest training pipeline for {config_type}...")
    
    # Load dataset
    X_train, y_train, X_val, y_val, X_test, y_test = load_data(config_type)
    
    # Initialize wrapper
    rf_model = RandomForestModel()
    
    # Fit and calibrate
    rf_model.fit(X_train, y_train, X_val, y_val)
    
    # Predict on test set
    log.info("Evaluating Random Forest on Test set...")
    y_pred = rf_model.predict(X_test)
    y_prob = rf_model.predict_proba(X_test)
    
    # Calculate metrics
    eval_metrics = metrics.compute_multiclass_metrics(
        y_true=y_test.values,
        y_pred=y_pred,
        y_prob=y_prob,
        num_classes=3
    )
    
    log.info(f"Random Forest Test Accuracy: {eval_metrics['accuracy']:.4f}")
    log.info(f"Random Forest Test F1 Macro: {eval_metrics['f1_macro']:.4f}")
    
    # Save model
    model_save_path = os.path.join(system_config.ARTIFACTS_DIR, "rf_model.joblib")
    rf_model.save(model_save_path)
    
    # Save metrics JSON
    metrics_save_path = os.path.join(system_config.REPORTS_DIR, "rf_metrics.json")
    os.makedirs(os.path.dirname(metrics_save_path), exist_ok=True)
    with open(metrics_save_path, "w") as f:
        json.dump(eval_metrics, f, indent=4)
        
    log.info(f"Saved Random Forest metrics to {metrics_save_path}")
    print("Random Forest training pipeline completed successfully.")

if __name__ == "__main__":
    main()
