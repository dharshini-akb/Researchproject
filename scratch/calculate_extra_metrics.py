import os
import json
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_curve, auc, roc_auc_score
from sklearn.preprocessing import label_binarize

from config import system_config
from models.random_forest import RandomForestModel

def load_test_data():
    base_dir = os.path.join(system_config.PROCESSED_DATA_DIR, "model_ready", "hpo_plus_sex")
    X_test = pd.read_csv(os.path.join(base_dir, "X_test.csv"))
    y_test = pd.read_csv(os.path.join(base_dir, "y_test.csv"))["target"]
    return X_test, y_test

def main():
    X_test, y_test = load_test_data()
    y_true = y_test.values
    
    rf_path = os.path.join(system_config.ARTIFACTS_DIR, "rf_model.joblib")
    rf_model = RandomForestModel()
    rf_model.load(rf_path)
    
    rf_preds = rf_model.predict(X_test)
    rf_probs = rf_model.predict_proba(X_test)
    
    num_classes = 3
    cm = confusion_matrix(y_true, rf_preds, labels=list(range(num_classes)))
    
    print("Confusion Matrix:")
    print(cm)
    
    # 1. Specificity per class
    # Specificity = TN / (TN + FP)
    specificities = []
    for i in range(num_classes):
        tp = cm[i, i]
        fn = sum(cm[i, j] for j in range(num_classes) if j != i)
        fp = sum(cm[j, i] for j in range(num_classes) if j != i)
        tn = sum(cm[j, k] for j in range(num_classes) for k in range(num_classes) if j != i and k != i)
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        specificities.append(spec)
        print(f"Class {i} Specificity: {spec:.4f} (TN={tn}, FP={fp})")
    
    macro_spec = np.mean(specificities)
    print(f"Macro Specificity: {macro_spec:.4f}")
    
    # 2. AUROC and AUPRC per class
    # Binarize labels
    y_true_bin = label_binarize(y_true, classes=list(range(num_classes)))
    
    aurocs = []
    auprcs = []
    
    for i in range(num_classes):
        # AUROC
        # If class only has one unique value in y_true_bin[:, i], roc_auc_score fails
        if len(np.unique(y_true_bin[:, i])) < 2:
            class_auc = 1.0
        else:
            class_auc = roc_auc_score(y_true_bin[:, i], rf_probs[:, i])
        aurocs.append(class_auc)
        
        # AUPRC (Area under Precision-Recall Curve)
        precision, recall, _ = precision_recall_curve(y_true_bin[:, i], rf_probs[:, i])
        class_pr_auc = auc(recall, precision)
        auprcs.append(class_pr_auc)
        
        print(f"Class {i} - AUROC: {class_auc:.4f}, AUPRC: {class_pr_auc:.4f}")
        
    macro_auroc = np.mean(aurocs)
    macro_auprc = np.mean(auprcs)
    
    print(f"Macro AUROC: {macro_auroc:.4f}")
    print(f"Macro AUPRC: {macro_auprc:.4f}")

if __name__ == "__main__":
    main()
