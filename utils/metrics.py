import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    roc_curve,
    auc
)
from sklearn.preprocessing import label_binarize

def compute_multiclass_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    num_classes: int = 3
) -> Dict[str, Any]:
    """
    Computes standard evaluation metrics for multiclass classification.
    """
    accuracy = accuracy_score(y_true, y_pred)
    
    # Compute precision, recall, f1 overall (macro and weighted)
    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, average='macro', zero_division=0
    )
    precision_weighted, recall_weighted, f1_weighted, _ = precision_recall_fscore_support(
        y_true, y_pred, average='weighted', zero_division=0
    )
    
    # Per-class metrics
    p_class, r_class, f1_class, support_class = precision_recall_fscore_support(
        y_true, y_pred, labels=list(range(num_classes)), zero_division=0
    )
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=list(range(num_classes)))
    
    # Calculate ROC and AUC per class
    # Binarize labels for ROC computation
    y_true_bin = label_binarize(y_true, classes=list(range(num_classes)))
    
    # If 2 classes, label_binarize returns a single column. Standardize to 2 columns for multiclass code simplicity
    if num_classes == 2 and y_true_bin.shape[1] == 1:
        y_true_bin = np.hstack((1 - y_true_bin, y_true_bin))
        
    roc_curves = {}
    macro_auc = 0.0
    
    for i in range(num_classes):
        # Handle cases where class has no positive samples in split
        if len(np.unique(y_true_bin[:, i])) < 2:
            fpr, tpr = np.array([0.0, 1.0]), np.array([0.0, 1.0])
            class_auc = 0.0
        else:
            fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_prob[:, i])
            class_auc = auc(fpr, tpr)
            
        roc_curves[i] = {
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "auc": float(class_auc)
        }
        macro_auc += class_auc
        
    macro_auc /= num_classes
    
    metrics = {
        "accuracy": float(accuracy),
        "precision_macro": float(precision_macro),
        "recall_macro": float(recall_macro),
        "f1_macro": float(f1_macro),
        "precision_weighted": float(precision_weighted),
        "recall_weighted": float(recall_weighted),
        "f1_weighted": float(f1_weighted),
        "per_class": {
            i: {
                "precision": float(p_class[i]),
                "recall": float(r_class[i]),
                "f1": float(f1_class[i]),
                "support": int(support_class[i])
            }
            for i in range(num_classes)
        },
        "confusion_matrix": cm.tolist(),
        "roc_auc": roc_curves,
        "macro_auc": float(macro_auc)
    }
    
    return metrics
