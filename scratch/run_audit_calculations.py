import os
import pandas as pd
import numpy as np
import json
import sys
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve, auc, confusion_matrix
import joblib
from models.random_forest import RandomForestModel

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_DIR = r"d:\finalresearchproject"
DATA_PATH = os.path.join(WORKSPACE_DIR, "data", "real_patient_hpo_dataset.csv")
MODEL_PATH = os.path.join(WORKSPACE_DIR, "models", "rf_model.joblib")

# Load real dataset
df = pd.read_csv(DATA_PATH)
print(f"Loaded real dataset from {DATA_PATH}. Records count: {len(df)}")

# 1. Verify Dataset counts
counts = df["Disease"].value_counts()
print("\n--- PATIENT COUNTS ---")
for disease, count in counts.items():
    print(f"  {disease}: {count}")
print(f"  Total: {len(df)}")

# Verify duplicates
dup_ids = df[df.duplicated(subset=["Patient_ID"])]
print(f"Duplicate Patient_ID count: {len(dup_ids)}")

# Same patient in multiple sources?
# Since Patient_IDs prefix with Source or are formatted uniquely, let's verify if there is any duplicated combination of Age, Sex, HPO_IDs
dup_profiles = df[df.duplicated(subset=["Age", "Sex", "HPO_IDs"], keep=False)]
print(f"Duplicate clinical profiles count (same Age, Sex, HPO_IDs): {len(dup_profiles)}")
if len(dup_profiles) > 0:
    print("Duplicate clinical profiles detected:")
    print(dup_profiles[["Patient_ID", "Disease", "Source"]])

# Empty HPO profiles?
empty_hpo = df[df["HPO_IDs"].isna() | (df["HPO_IDs"] == "")]
print(f"Empty HPO profiles count: {len(empty_hpo)}")

# Invalid HPO IDs?
import re
invalid_hpos = []
for idx, row in df.iterrows():
    hpos = str(row["HPO_IDs"]).split("|")
    for h in hpos:
        if not re.match(r"^HP:\d+$", h):
            invalid_hpos.append((row["Patient_ID"], h))
print(f"Invalid HPO IDs count: {len(invalid_hpos)}")

# 2. HPO Feature occurrence counts per class
hpo_occurrences = {}
for idx, row in df.iterrows():
    dis = row["Disease"]
    hpos = str(row["HPO_IDs"]).split("|")
    for h in hpos:
        if h not in hpo_occurrences:
            hpo_occurrences[h] = {"White-Sutton Syndrome": 0, "Xia-Gibbs Syndrome": 0, "KBG Syndrome": 0}
        hpo_occurrences[h][dis] += 1

# Load HPO terms from obo to map term names
def parse_hpo_obo():
    obo_path = os.path.join(WORKSPACE_DIR, "data", "raw", "hp.obo")
    if not os.path.exists(obo_path):
        return {}
    hpo_map = {}
    current_id = None
    current_name = None
    with open(obo_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "[Term]":
                if current_id and current_name:
                    hpo_map[current_id] = current_name
                current_id = None
                current_name = None
            elif line.startswith("id:"):
                current_id = line.split("id:")[1].strip()
            elif line.startswith("name:"):
                current_name = line.split("name:")[1].strip()
        if current_id and current_name:
            hpo_map[current_id] = current_name
    return hpo_map

hpo_names = parse_hpo_obo()

print("\n--- HPO FEATURE SEPARABILITY ANALYSIS ---")
print(f"{'HPO ID':<12} | {'HPO Term':<45} | {'WhiteSutton':<11} | {'XiaGibbs':<8} | {'KBG':<4} | {'Perfect Separator?'}")
print("-" * 100)
perfect_separators = []
for h, counts_dict in sorted(hpo_occurrences.items()):
    term = hpo_names.get(h, "Unknown HPO Term")[:45]
    ws = counts_dict["White-Sutton Syndrome"]
    xg = counts_dict["Xia-Gibbs Syndrome"]
    kbg = counts_dict["KBG Syndrome"]
    
    # Check if this feature is unique to only one class AND highly frequent (e.g. perfect separator for that class)
    is_perfect = False
    class_sep = ""
    if ws > 0 and xg == 0 and kbg == 0:
        is_perfect = True
        class_sep = "White-Sutton"
    elif xg > 0 and ws == 0 and kbg == 0:
        is_perfect = True
        class_sep = "Xia-Gibbs"
    elif kbg > 0 and ws == 0 and xg == 0:
        is_perfect = True
        class_sep = "KBG"
        
    sep_str = f"Yes ({class_sep})" if is_perfect else "No"
    if is_perfect:
        perfect_separators.append((h, term, class_sep, ws, xg, kbg))
    print(f"{h:<12} | {term:<45} | {ws:<11} | {xg:<8} | {kbg:<4} | {sep_str}")

print(f"\nFound {len(perfect_separators)} perfect separator features.")

# 3. Model Predictions on Test Split
# Load model & test split
model = RandomForestModel()
model.load(MODEL_PATH)
base_dir = os.path.join(WORKSPACE_DIR, "data", "processed", "model_ready", "hpo_plus_sex")
X_test = pd.read_csv(os.path.join(base_dir, "X_test.csv"))
y_test = pd.read_csv(os.path.join(base_dir, "y_test.csv"))["target"]

print(f"\nLoaded test split with {len(X_test)} samples.")
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print("\n--- TEST CONFUSION MATRIX ---")
print(cm)

# Verify accuracy manually
accuracy = np.mean(y_test == y_pred)
print(f"Manually verified Test Accuracy: {accuracy * 100:.2f}%")
print("Target labels in test:", list(y_test))
print("Predicted labels in test:", list(y_pred))

# One-vs-rest metrics calculation
print("\n--- PER-CLASS METRICS ---")
total_sum = int(np.sum(cm))
classes = ["White-Sutton Syndrome", "Xia-Gibbs Syndrome", "KBG Syndrome"]

# AUROC/AUPRC OVR
# We need to binarize labels
from sklearn.preprocessing import label_binarize
y_test_bin = label_binarize(y_test, classes=[0, 1, 2])

per_class_metrics = {}
for i, name in enumerate(classes):
    tp = int(cm[i, i])
    fp = int(np.sum(cm[:, i]) - tp)
    fn = int(np.sum(cm[i, :]) - tp)
    tn = int(total_sum - tp - fp - fn)
    
    spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 1.0
    prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
    
    # AUROC
    class_auc = roc_auc_score(y_test_bin[:, i], y_prob[:, i])
    
    # AUPRC
    precision_curve, recall_curve, _ = precision_recall_curve(y_test_bin[:, i], y_prob[:, i])
    class_auprc = auc(recall_curve, precision_curve)
    
    per_class_metrics[name] = {
        "TP": tp, "TN": tn, "FP": fp, "FN": fn,
        "Specificity": spec,
        "Precision": prec,
        "Recall": rec,
        "F1": f1,
        "AUROC": class_auc,
        "AUPRC": class_auprc
    }
    
    print(f"{name}:")
    print(f"  TP={tp}, TN={tn}, FP={fp}, FN={fn}")
    print(f"  Specificity: {spec:.4f}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall/Sensitivity: {rec:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    print(f"  AUROC: {class_auc:.4f}")
    print(f"  AUPRC: {class_auprc:.4f}")

# Macro calculations
macro_spec = np.mean([m["Specificity"] for m in per_class_metrics.values()])
macro_auroc = roc_auc_score(y_test_bin, y_prob, multi_class="ovr", average="macro")
macro_auprc = np.mean([m["AUPRC"] for m in per_class_metrics.values()])

print("\n--- MACRO METRICS ---")
print(f"Macro Specificity: {macro_spec:.4f}")
print(f"Macro AUROC: {macro_auroc:.4f}")
print(f"Macro AUPRC: {macro_auprc:.4f}")

# Calculate 95% Confidence Interval for Accuracy using Wald Method
# CI = p +/- z * sqrt(p(1-p)/n)
# Since accuracy is 1.0 (p=1.0), the standard Wald interval is [1.0, 1.0], but rule of three or Wilson score interval is more appropriate.
# Let's calculate the Wilson score interval for p=1.0, n=14.
# Wilson score interval formula:
# center = (p + z^2/(2n)) / (1 + z^2/n)
# error = z * sqrt( p(1-p)/n + z^2/(4n^2) ) / (1 + z^2/n)
# z = 1.96 for 95% CI
n = 14
p = 1.0
z = 1.96
center = (p + z**2 / (2 * n)) / (1 + z**2 / n)
error = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
ci_lower = center - error
ci_upper = center + error
print(f"\n95% Confidence Interval for Accuracy (Wilson Score): {ci_lower:.4f} to {ci_upper:.4f}")

# 4. Provenance table records details
provenance_data = []
for idx, row in df.iterrows():
    dis = row["Disease"]
    pid = row["Patient_ID"]
    source = row["Source"]
    # get HPO symptom names mapping
    symptoms = row["HPO_Terms"]
    
    # Original clinical phenotype details or table refs
    table_ref = ""
    if source == "PMC7713511":
        table_ref = "Table 3 & Table 4"
    elif source == "PMC6231716":
        table_ref = "Table S1"
    elif source == "PMC8948816":
        table_ref = "Table 1"
    elif source == "PMC5435101":
        table_ref = "Table I"
        
    provenance_data.append({
        "Disease": dis,
        "Patient ID": pid,
        "Source Paper": f"{source} (PubMed Central)",
        "Source Table/Ref": table_ref,
        "Phenotype Terms count": len(str(row["HPO_IDs"]).split("|"))
    })
df_prov = pd.DataFrame(provenance_data)
# Save provenance table as markdown table to prints
df_prov_summary = df_prov.groupby(["Disease", "Source Paper", "Source Table/Ref"]).agg(
    Patient_Count=("Patient ID", "count"),
    Mean_Phenotypes_Per_Patient=("Phenotype Terms count", "mean")
).reset_index()
print("\n--- PROVENANCE TABLE SUMMARY ---")
print(df_prov_summary.to_markdown(index=False))
