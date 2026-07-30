import os
import json
import time
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import BernoulliNB
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from config import system_config
from utils import logger, metrics

log = logger.get_logger("benchmark_baselines")

def load_data():
    base_dir = os.path.join(system_config.PROCESSED_DATA_DIR, "model_ready", "hpo_plus_sex")
    X_train = pd.read_csv(os.path.join(base_dir, "X_train.csv"))
    y_train = pd.read_csv(os.path.join(base_dir, "y_train.csv"))["target"]
    X_val = pd.read_csv(os.path.join(base_dir, "X_validation.csv"))
    y_val = pd.read_csv(os.path.join(base_dir, "y_validation.csv"))["target"]
    X_test = pd.read_csv(os.path.join(base_dir, "X_test.csv"))
    y_test = pd.read_csv(os.path.join(base_dir, "y_test.csv"))["target"]
    return X_train, y_train, X_val, y_val, X_test, y_test

def main():
    X_train, y_train, X_val, y_val, X_test, y_test = load_data()
    
    # We train models on train + validation to maximize benchmark capabilities
    X_full_train = pd.concat([X_train, X_val]).reset_index(drop=True)
    y_full_train = pd.concat([y_train, y_val]).reset_index(drop=True)
    
    # Define baseline models
    baseline_models = {
        "Logistic Regression": LogisticRegression(max_iter=500, random_state=42),
        "SVM": SVC(probability=True, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "Naive Bayes": BernoulliNB(),  # Highly suitable for binary multi-hot sparse phenotypes
        "XGBoost": XGBClassifier(n_estimators=100, max_depth=6, random_state=42, eval_metric="mlogloss")
    }
    
    benchmark_results = {}
    
    for name, clf in baseline_models.items():
        log.info(f"Benchmarking {name}...")
        
        # Measure training time
        t_start_train = time.perf_counter()
        clf.fit(X_full_train, y_full_train)
        t_end_train = time.perf_counter()
        train_time = t_end_train - t_start_train
        
        # Measure prediction time
        t_start_pred = time.perf_counter()
        preds = clf.predict(X_test)
        t_end_pred = time.perf_counter()
        pred_time = t_end_pred - t_start_pred
        
        # Metrics
        acc = accuracy_score(y_test, preds)
        p, r, f, _ = precision_recall_fscore_support(y_test, preds, average='macro', zero_division=0)
        cm = confusion_matrix(y_test, preds)
        
        benchmark_results[name] = {
            "accuracy": float(acc),
            "precision_macro": float(p),
            "recall_macro": float(r),
            "f1_macro": float(f),
            "train_time_seconds": float(train_time),
            "predict_time_seconds": float(pred_time),
            "confusion_matrix": cm.tolist()
        }
        log.info(f"{name} | Test Acc: {acc:.4f} | F1: {f:.4f} | Fit: {train_time:.5f}s")
        
    # Write to a JSON file
    out_path = os.path.join(system_config.REPORTS_DIR, "baseline_benchmarks.json")
    with open(out_path, "w") as f:
        json.dump(benchmark_results, f, indent=4)
        
    log.info(f"Baseline benchmarking completed. Saved to {out_path}")
    print("Baseline benchmarking execution completed successfully.")

if __name__ == "__main__":
    main()
