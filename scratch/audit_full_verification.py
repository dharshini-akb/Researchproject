import os
import sys
import json
import math
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import train_test_split, StratifiedKFold, GroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import label_binarize
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, precision_recall_fscore_support,
    confusion_matrix, roc_auc_score, average_precision_score, brier_score_loss
)
import joblib

WORKSPACE_DIR = r"d:\finalresearchproject"
DATA_DIR = os.path.join(WORKSPACE_DIR, "data")
REPORTS_DIR = os.path.join(WORKSPACE_DIR, "reports")
MODELS_DIR = os.path.join(WORKSPACE_DIR, "models")

print("================================================================================")
print("COMPREHENSIVE INDEPENDENT RE-VERIFICATION PASS")
print("================================================================================")

# 1. LOAD MASTER DATASET
df = pd.read_csv(os.path.join(DATA_DIR, "expanded_real_patient_hpo_dataset.csv"))
print("\n--- 1. DATASET PROPERTIES ---")
raw_rows = len(df)
unique_pids = df['Patient_ID'].nunique()
dup_pids = df['Patient_ID'].duplicated().sum()
kbg_count = int((df['Disease'] == 'KBG Syndrome').sum())
ws_count = int((df['Disease'] == 'White-Sutton Syndrome').sum())
xg_count = int((df['Disease'] == 'Xia-Gibbs Syndrome').sum())

print(f"RAW ROWS = {raw_rows}")
print(f"UNIQUE PATIENTS = {unique_pids}")
print(f"KBG = {kbg_count}")
print(f"WHITE-SUTTON = {ws_count}")
print(f"XIA-GIBBS = {xg_count}")
print(f"Duplicate Patient_IDs = {dup_pids}")

# Phenotype profile uniqueness
df['hpo_set'] = df['HPO_IDs'].apply(lambda x: tuple(sorted([h.strip() for h in str(x).split('|') if h.strip()])))
df['profile_str'] = df['Disease'] + "_" + df['Sex'].fillna("UNKNOWN") + "_" + df['hpo_set'].astype(str)
unique_profiles = df['profile_str'].nunique()
print(f"Unique phenotypic profiles = {unique_profiles} / {len(df)}")
print(f"Duplicate phenotypic profiles = {len(df) - unique_profiles}")

# Missing values
print(f"Missing values by column:\n{df.isnull().sum()}")
# Check aggregate rows
agg_pids = df[df['Patient_ID'].str.contains("total|summary|cohort|aggregate", case=False, na=False)]
print(f"Aggregate rows detected: {len(agg_pids)}")

# 2. EXCLUSION LOG
print("\n--- 2. EXCLUSION LOG (59 CANDIDATES) ---")
df_excl = pd.read_csv(os.path.join(DATA_DIR, "excluded_duplicate_patients_log.csv"))
print(f"Total rows in exclusion log: {len(df_excl)}")
print(f"Excluded by Disease:\n{df_excl['Disease'].value_counts()}")
print(f"Excluded by Reason:\n{df_excl['Reason'].value_counts()}")
print(f"Arithmetic check: 385 (final) + 59 (excluded) = {385 + len(df_excl)} total candidate records evaluated.")

# 3. PUBLICATION INVENTORY & DISCREPANCY AUDIT
print("\n--- 3. PUBLICATION INVENTORY ---")
df_pub = pd.read_csv(os.path.join(REPORTS_DIR, "publication_inventory.csv"))
print(f"Rows in publication inventory table: {len(df_pub)}")
print(df_pub[['Publication', 'Disease', 'Total_Patients_Extracted', 'Status']])
print(f"Sum of patients in inventory: {df_pub['Total_Patients_Extracted'].sum()}")

# 4. PATIENT-LEVEL PROVENANCE MANIFEST
print("\n--- 4. PATIENT-LEVEL PROVENANCE ---")
df_prov = pd.read_csv(os.path.join(REPORTS_DIR, "expanded_cohort_provenance_manifest.csv"))
print(f"Total rows in provenance manifest: {len(df_prov)}")
print(f"Missing values in provenance manifest:\n{df_prov.isnull().sum()}")

# Check fields for all 385 patients
has_pid = df_prov['Patient_ID'].notnull().all()
has_disease = df_prov['Disease'].notnull().all()
has_source = df_prov['Source_Publication'].notnull().all()
has_hpos = df_prov['HPO_IDs'].notnull().all()
has_ref = df_prov['Provenance_Reference'].notnull().all()
print(f"All 385 have Patient_ID: {has_pid}")
print(f"All 385 have Disease: {has_disease}")
print(f"All 385 have Source: {has_source}")
print(f"All 385 have HPO_IDs: {has_hpos}")
print(f"All 385 have Provenance Reference: {has_ref}")

# 5. SPLIT AUDIT & RE-GENERATION
print("\n--- 5. SPLITS AUDIT ---")
disease_id_map = {
    "White-Sutton Syndrome": 0, "White-Sutton syndrome": 0,
    "Xia-Gibbs Syndrome": 1, "Xia-Gibbs syndrome": 1,
    "KBG Syndrome": 2, "KBG syndrome": 2
}
df['target'] = df['Disease'].map(disease_id_map)
df['group_key'] = df['target'].astype(str) + "_" + df['Sex'].fillna("UNKNOWN") + "_" + df['HPO_IDs'].fillna("")

groups = df.groupby('group_key')
group_summaries = [{'group_key': k, 'target': g['target'].iloc[0]} for k, g in groups]
df_groups = pd.DataFrame(group_summaries)

train_keys, temp_keys = train_test_split(
    df_groups['group_key'],
    test_size=0.4,
    random_state=42,
    stratify=df_groups['target']
)
df_temp_groups = df_groups[df_groups['group_key'].isin(temp_keys)]
val_keys, test_keys = train_test_split(
    df_temp_groups['group_key'],
    test_size=0.5,
    random_state=42,
    stratify=df_temp_groups['target']
)

df_train = df[df['group_key'].isin(train_keys)].copy().reset_index(drop=True)
df_val = df[df['group_key'].isin(val_keys)].copy().reset_index(drop=True)
df_test = df[df['group_key'].isin(test_keys)].copy().reset_index(drop=True)

print(f"Train N = {len(df_train)}")
print(f"Val N = {len(df_val)}")
print(f"Test N = {len(df_test)}")
print(f"Total = {len(df_train) + len(df_val) + len(df_test)}")

# Check overlap across splits
pid_tr = set(df_train['Patient_ID'])
pid_v = set(df_val['Patient_ID'])
pid_te = set(df_test['Patient_ID'])
print(f"Patient_ID overlap Train & Val: {len(pid_tr & pid_v)}")
print(f"Patient_ID overlap Train & Test: {len(pid_tr & pid_te)}")
print(f"Patient_ID overlap Val & Test: {len(pid_v & pid_te)}")

prof_tr = set(df_train['profile_str'])
prof_v = set(df_val['profile_str'])
prof_te = set(df_test['profile_str'])
print(f"Phenotype profile overlap Train & Val: {len(prof_tr & prof_v)}")
print(f"Phenotype profile overlap Train & Test: {len(prof_tr & prof_te)}")
print(f"Phenotype profile overlap Val & Test: {len(prof_v & prof_te)}")

print("\nDisease breakdown per split:")
print("Train:\n", df_train['Disease'].value_counts())
print("Val:\n", df_val['Disease'].value_counts())
print("Test:\n", df_test['Disease'].value_counts())

print("\nSex breakdown per split:")
print("Train:\n", df_train['Sex'].value_counts())
print("Val:\n", df_val['Sex'].value_counts())
print("Test:\n", df_test['Sex'].value_counts())

# 6. HPO FEATURE CONSTRUCTION
print("\n--- 6. HPO FEATURES AUDIT ---")
all_hpos = set([h.strip() for s in df['HPO_IDs'] for h in str(s).split('|') if h.strip()])
train_hpos = set([h.strip() for s in df_train['HPO_IDs'] for h in str(s).split('|') if h.strip()])
val_hpos = set([h.strip() for s in df_val['HPO_IDs'] for h in str(s).split('|') if h.strip()])
test_hpos = set([h.strip() for s in df_test['HPO_IDs'] for h in str(s).split('|') if h.strip()])

hpo_vocab = sorted(list(train_hpos))
print(f"Total HPO terms in complete dataset: {len(all_hpos)}")
print(f"Training-only HPO vocabulary size: {len(hpo_vocab)}")
print(f"Val unique HPO terms: {len(val_hpos)}, Val OOV terms: {len(val_hpos - train_hpos)} ({val_hpos - train_hpos})")
print(f"Test unique HPO terms: {len(test_hpos)}, Test OOV terms: {len(test_hpos - train_hpos)} ({test_hpos - train_hpos})")

def encode_hpos(df_split):
    encoded = []
    for idx, row in df_split.iterrows():
        patient_hpos = set(str(row['HPO_IDs']).strip().split('|'))
        vec = [1 if term in patient_hpos else 0 for term in hpo_vocab]
        encoded.append(vec)
    return pd.DataFrame(encoded, columns=hpo_vocab)

sex_categories = ["MALE", "FEMALE", "UNKNOWN_SEX"]
sex_mapping = {cat: idx for idx, cat in enumerate(sex_categories)}
def encode_sex(df_split):
    encoded = []
    for idx, row in df_split.iterrows():
        s = str(row['Sex']).strip().upper()
        if s not in sex_mapping:
            s = "UNKNOWN_SEX"
        vec = [0] * len(sex_categories)
        vec[sex_mapping[s]] = 1
        encoded.append(vec)
    return pd.DataFrame(encoded, columns=[f"sex_{c}" for c in sex_categories])

X_train = pd.concat([encode_hpos(df_train), encode_sex(df_train)], axis=1)
X_val = pd.concat([encode_hpos(df_val), encode_sex(df_val)], axis=1)
X_test = pd.concat([encode_hpos(df_test), encode_sex(df_test)], axis=1)

y_train = df_train['target'].values
y_val = df_val['target'].values
y_test = df_test['target'].values

print(f"Input feature matrix shape - Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
print(f"Confirmed feature count = {X_train.shape[1]} (78 HPO + 3 Sex = 81)")

# 7. MODEL EVALUATIONS DIRECTLY
print("\n--- 7 & 8. RE-RUN & EVALUATE ALL MODELS DIRECTLY ON HELD-OUT TEST (N=78) ---")
models = {
    "Calibrated Random Forest": CalibratedClassifierCV(
        estimator=RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight="balanced"),
        method='sigmoid', cv=5
    ),
    "Standard Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight="balanced"),
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Support Vector Machine (RBF)": SVC(probability=True, random_state=42),
    "Decision Tree": DecisionTreeClassifier(max_depth=10, random_state=42),
    "K-Nearest Neighbors (k=5)": KNeighborsClassifier(n_neighbors=5),
    "Naive Bayes": GaussianNB()
}

try:
    from xgboost import XGBClassifier
    models["XGBoost"] = XGBClassifier(n_estimators=100, max_depth=6, random_state=42, eval_metric='mlogloss')
except ImportError:
    pass

model_results = []
y_test_bin = label_binarize(y_test, classes=[0, 1, 2])

for name, clf in models.items():
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    
    # Probabilities
    if hasattr(clf, "predict_proba"):
        y_prob = clf.predict_proba(X_test)
    elif hasattr(clf, "decision_function"):
        df_val_score = clf.decision_function(X_test)
        # Softmax
        exp_s = np.exp(df_val_score - np.max(df_val_score, axis=1, keepdims=True))
        y_prob = exp_s / np.sum(exp_s, axis=1, keepdims=True)
    else:
        y_prob = None
        
    acc = accuracy_score(y_test, y_pred)
    bal_acc = balanced_accuracy_score(y_test, y_pred)
    prec_m, rec_m, f1_m, _ = precision_recall_fscore_support(y_test, y_pred, average='macro', zero_division=0)
    
    # Specificity
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2])
    total_sum = int(np.sum(cm))
    specs = []
    for i in range(3):
        tp = int(cm[i, i])
        fp = int(np.sum(cm[:, i]) - tp)
        fn = int(np.sum(cm[i, :]) - tp)
        tn = int(total_sum - tp - fp - fn)
        spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 1.0
        specs.append(spec)
    macro_spec = np.mean(specs)
    
    # AUROC / AUPRC
    if y_prob is not None:
        macro_auroc = roc_auc_score(y_test_bin, y_prob, average='macro', multi_class='ovr')
        macro_auprc = average_precision_score(y_test_bin, y_prob, average='macro')
        # Multi-class Brier score: mean of sum of squared differences over classes
        brier = np.mean(np.sum((y_prob - y_test_bin)**2, axis=1))
    else:
        macro_auroc, macro_auprc, brier = np.nan, np.nan, np.nan
        
    model_results.append({
        "Model": name,
        "Accuracy": acc,
        "Balanced_Acc": bal_acc,
        "Macro_Precision": prec_m,
        "Macro_Recall": rec_m,
        "Macro_F1": f1_m,
        "Macro_Specificity": macro_spec,
        "Macro_AUROC": macro_auroc,
        "Macro_AUPRC": macro_auprc,
        "Brier_Score": brier,
        "Confusion_Matrix": cm.tolist()
    })

df_res = pd.DataFrame(model_results)
print(df_res[['Model', 'Accuracy', 'Balanced_Acc', 'Macro_Precision', 'Macro_Recall', 'Macro_F1', 'Macro_Specificity', 'Macro_AUROC', 'Brier_Score']].to_string())

# Detailed audit of Calibrated Random Forest confusion matrix
cal_rf = models["Calibrated Random Forest"]
y_pred_cal = cal_rf.predict(X_test)
y_prob_cal = cal_rf.predict_proba(X_test)
cm_cal = confusion_matrix(y_test, y_pred_cal, labels=[0, 1, 2])
print("\n--- CALIBRATED RANDOM FOREST DETAILED METRICS ---")
print("Confusion Matrix:")
print("                 Predicted WS  Predicted XG  Predicted KBG")
print(f"Actual WS        {cm_cal[0,0]:<12} {cm_cal[0,1]:<12} {cm_cal[0,2]:<12}")
print(f"Actual XG        {cm_cal[1,0]:<12} {cm_cal[1,1]:<12} {cm_cal[1,2]:<12}")
print(f"Actual KBG       {cm_cal[2,0]:<12} {cm_cal[2,1]:<12} {cm_cal[2,2]:<12}")

total_test = len(y_test)
correct_test = int(np.sum(np.diag(cm_cal)))
incorrect_test = total_test - correct_test
print(f"Total Test Patients: {total_test}")
print(f"Number Correct: {correct_test}")
print(f"Number Incorrect: {incorrect_test}")
print(f"Exact Accuracy: {correct_test}/{total_test} = {correct_test/total_test:.6f}")

for i, dname in enumerate(["White-Sutton", "Xia-Gibbs", "KBG Syndrome"]):
    tp = cm_cal[i, i]
    fp = np.sum(cm_cal[:, i]) - tp
    fn = np.sum(cm_cal[i, :]) - tp
    tn = total_test - tp - fp - fn
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
    c_auroc = roc_auc_score(y_test_bin[:, i], y_prob_cal[:, i])
    c_auprc = average_precision_score(y_test_bin[:, i], y_prob_cal[:, i])
    print(f"  {dname}: Precision={prec:.4f} ({tp}/{tp+fp}), Recall={rec:.4f} ({tp}/{tp+fn}), Specificity={spec:.4f} ({tn}/{tn+fp}), F1={f1:.4f}, AUROC={c_auroc:.4f}, AUPRC={c_auprc:.4f}, Support={tp+fn}")

# 9. 95% CONFIDENCE INTERVAL CALCULATION
print("\n--- 9. 95% CONFIDENCE INTERVAL AUDIT (77/78 = 0.987179) ---")
k = 77
n = 78
p = k / n

# Method 1: Normal Approximation (Wald)
z = 1.96
wald_err = z * math.sqrt((p * (1 - p)) / n)
wald_lower = max(0.0, p - wald_err)
wald_upper = min(1.0, p + wald_err)
print(f"1. Normal Approximation (Wald): [{wald_lower:.4f}, {wald_upper:.4f}] ({wald_lower*100:.2f}% to {wald_upper*100:.2f}%)")

# Method 2: Wilson Score Interval
denominator = 1 + (z**2)/n
centre_adjusted = (p + (z**2)/(2*n)) / denominator
adjusted_err = (z * math.sqrt((p*(1 - p)/n) + (z**2)/(4*(n**2)))) / denominator
wilson_lower = centre_adjusted - adjusted_err
wilson_upper = min(1.0, centre_adjusted + adjusted_err)
print(f"2. Wilson Score Interval: [{wilson_lower:.4f}, {wilson_upper:.4f}] ({wilson_lower*100:.2f}% to {wilson_upper*100:.2f}%)")

# Method 3: Clopper-Pearson Exact Interval (Beta distribution)
cp_lower = stats.beta.ppf(0.025, k, n - k + 1)
cp_upper = stats.beta.ppf(0.975, k + 1, n - k)
print(f"3. Clopper-Pearson Exact Interval: [{cp_lower:.4f}, {cp_upper:.4f}] ({cp_lower*100:.2f}% to {cp_upper*100:.2f}%)")

# Method 4: Agresti-Coull Interval
n_tilde = n + z**2
p_tilde = (k + (z**2)/2) / n_tilde
ac_err = z * math.sqrt(p_tilde * (1 - p_tilde) / n_tilde)
ac_lower = max(0.0, p_tilde - ac_err)
ac_upper = min(1.0, p_tilde + ac_err)
print(f"4. Agresti-Coull Interval: [{ac_lower:.4f}, {ac_upper:.4f}] ({ac_lower*100:.2f}% to {ac_upper*100:.2f}%)")

# Method 5: Non-parametric Bootstrap (10,000 resamples)
np.random.seed(42)
boot_accs = []
y_true_arr = y_test
y_pred_arr = y_pred_cal
for _ in range(10000):
    idx = np.random.choice(n, size=n, replace=True)
    boot_accs.append(accuracy_score(y_true_arr[idx], y_pred_arr[idx]))
boot_lower = np.percentile(boot_accs, 2.5)
boot_upper = np.percentile(boot_accs, 97.5)
print(f"5. Bootstrap 10,000 resamples: [{boot_lower:.4f}, {boot_upper:.4f}] ({boot_lower*100:.2f}% to {boot_upper*100:.2f}%)")

# 10. CROSS-VALIDATION INDEPENDENT AUDIT
print("\n--- 10. 5-FOLD CROSS VALIDATION PER-FOLD AUDIT ---")
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_accs, cv_f1s, cv_precs, cv_recs = [], [], [], []

for fold, (t_idx, v_idx) in enumerate(skf.split(df, df['target'])):
    f_tr = df.iloc[t_idx].reset_index(drop=True)
    f_va = df.iloc[v_idx].reset_index(drop=True)
    
    # Feature vocabulary fitted strictly inside training fold
    f_vocab = sorted(list(set([h.strip() for h_s in f_tr['HPO_IDs'] for h in str(h_s).split('|') if h.strip()])))
    
    def enc_h(df_s):
        vecs = []
        for _, r in df_s.iterrows():
            p_h = set(str(r['HPO_IDs']).split('|'))
            vecs.append([1 if t in p_h else 0 for t in f_vocab])
        return pd.DataFrame(vecs, columns=f_vocab)
        
    X_f_tr = pd.concat([enc_h(f_tr), encode_sex(f_tr)], axis=1)
    X_f_va = pd.concat([enc_h(f_va), encode_sex(f_va)], axis=1)
    y_f_tr = f_tr['target'].values
    y_f_va = f_va['target'].values
    
    f_rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
    f_cal = CalibratedClassifierCV(estimator=f_rf, method='sigmoid', cv=5)
    f_cal.fit(X_f_tr, y_f_tr)
    
    f_pred = f_cal.predict(X_f_va)
    f_acc = accuracy_score(y_f_va, f_pred)
    f_prec, f_rec, f_f1, _ = precision_recall_fscore_support(y_f_va, f_pred, average='macro', zero_division=0)
    
    cv_accs.append(f_acc)
    cv_f1s.append(f_f1)
    cv_precs.append(f_prec)
    cv_recs.append(f_rec)
    print(f"  Fold {fold+1} (N={len(y_f_va)}): Accuracy = {f_acc:.4f} ({accuracy_score(y_f_va, f_pred, normalize=False)}/{len(y_f_va)}), Macro F1 = {f_f1:.4f}, Precision = {f_prec:.4f}, Recall = {f_rec:.4f}")

print(f"\nMean CV Accuracy = {np.mean(cv_accs):.6f} (Standard Deviation = {np.std(cv_accs):.6f})")
print(f"Mean CV Macro F1  = {np.mean(cv_f1s):.6f} (Standard Deviation = {np.std(cv_f1s):.6f})")

# 12. SOURCE-LEVEL DISTRIBUTION ACROSS SPLITS & SOURCE-GROUPED CROSS-VALIDATION
print("\n--- 12. SOURCE PUBLICATION COMPOSITION ACROSS SPLITS ---")
# Group sources
df['source_group'] = df['Source'].apply(lambda x: str(x).split('(')[0].strip())
print("Source Distribution across Splits:")
for sname in df['source_group'].unique():
    c_tr = (df_train['Source'].str.contains(sname, case=False, na=False)).sum()
    c_va = (df_val['Source'].str.contains(sname, case=False, na=False)).sum()
    c_te = (df_test['Source'].str.contains(sname, case=False, na=False)).sum()
    print(f"  Source '{sname}': Train={c_tr}, Val={c_va}, Test={c_te}, Total={c_tr+c_va+c_te}")

# Evaluate GroupKFold by Source Publication to assess prospective multicenter generalization
print("\n--- SOURCE-GROUPED CROSS-VALIDATION (GroupKFold on Source) ---")
# Merge small sources so every group has at least some patients
gkf = GroupKFold(n_splits=5)
# Use primary publication as group
src_groups = df['source_group'].astype('category').cat.codes
gkf_accs, gkf_f1s = [], []
for fold, (t_idx, v_idx) in enumerate(gkf.split(df, df['target'], groups=src_groups)):
    f_tr = df.iloc[t_idx].reset_index(drop=True)
    f_va = df.iloc[v_idx].reset_index(drop=True)
    f_vocab = sorted(list(set([h.strip() for h_s in f_tr['HPO_IDs'] for h in str(h_s).split('|') if h.strip()])))
    
    def enc_h(df_s):
        vecs = []
        for _, r in df_s.iterrows():
            p_h = set(str(r['HPO_IDs']).split('|'))
            vecs.append([1 if t in p_h else 0 for t in f_vocab])
        return pd.DataFrame(vecs, columns=f_vocab)
        
    X_f_tr = pd.concat([enc_h(f_tr), encode_sex(f_tr)], axis=1)
    X_f_va = pd.concat([enc_h(f_va), encode_sex(f_va)], axis=1)
    y_f_tr = f_tr['target'].values
    y_f_va = f_va['target'].values
    
    f_rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')
    f_cal = CalibratedClassifierCV(estimator=f_rf, method='sigmoid', cv=3)
    f_cal.fit(X_f_tr, y_f_tr)
    f_pred = f_cal.predict(X_f_va)
    gkf_accs.append(accuracy_score(y_f_va, f_pred))
    _, _, g_f1, _ = precision_recall_fscore_support(y_f_va, f_pred, average='macro', zero_division=0)
    gkf_f1s.append(g_f1)
    print(f"  Source Group Fold {fold+1} (N={len(y_f_va)}): Accuracy = {accuracy_score(y_f_va, f_pred):.4f}, Macro F1 = {g_f1:.4f}")

print(f"Mean Source-Grouped CV Accuracy: {np.mean(gkf_accs):.4f} ± {np.std(gkf_accs):.4f}")
print(f"Mean Source-Grouped CV Macro F1: {np.mean(gkf_f1s):.4f} ± {np.std(gkf_f1s):.4f}")

# 13. SHAP INDEPENDENT CALCULATION
print("\n--- 13. SHAP VALUES INDEPENDENT CALCULATION ---")
import shap
raw_rf = cal_rf.calibrated_classifiers_[0].estimator
explainer = shap.TreeExplainer(raw_rf)
shap_vals = explainer.shap_values(X_test)

# Parse hp.obo to get names
obo_path = os.path.join(WORKSPACE_DIR, "data", "raw", "hp.obo")
hpo_names = {}
if os.path.exists(obo_path):
    c_id, c_name = None, None
    with open(obo_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "[Term]":
                if c_id and c_name:
                    hpo_names[c_id] = c_name
                c_id, c_name = None, None
            elif line.startswith("id:"):
                c_id = line.split("id:")[1].strip()
            elif line.startswith("name:"):
                c_name = line.split("name:")[1].strip()
        if c_id and c_name:
            hpo_names[c_id] = c_name

feature_names = list(X_test.columns)
# shap_vals is list of [N, num_features] for classes 0, 1, 2 or array of shape [N, num_features, 3]
if isinstance(shap_vals, list):
    class_shaps = shap_vals
else:
    class_shaps = [shap_vals[:, :, c] for c in range(3)]

dnames = ["White-Sutton", "Xia-Gibbs", "KBG Syndrome"]
top_shap_summary = {}
for c_idx, c_name in enumerate(dnames):
    mean_abs_s = np.mean(np.abs(class_shaps[c_idx]), axis=0)
    top_indices = np.argsort(mean_abs_s)[::-1][:10]
    print(f"\nTop 10 Features associated with predictions for {c_name} (Class {c_idx}):")
    top_list = []
    for rank, idx in enumerate(top_indices):
        feat = feature_names[idx]
        val = mean_abs_s[idx]
        h_name = hpo_names.get(feat, feat)
        print(f"  {rank+1}. {feat} ({h_name}): mean |SHAP| = {val:.4f}")
        top_list.append({"rank": rank+1, "feature": feat, "name": h_name, "mean_shap": float(val)})
    top_shap_summary[c_name] = top_list

# Global importance
global_mean_abs = np.mean([np.mean(np.abs(class_shaps[c]), axis=0) for c in range(3)], axis=0)
top_global_idx = np.argsort(global_mean_abs)[::-1][:10]
print("\nTop 10 Overall Global SHAP Features:")
for rank, idx in enumerate(top_global_idx):
    feat = feature_names[idx]
    val = global_mean_abs[idx]
    h_name = hpo_names.get(feat, feat)
    print(f"  {rank+1}. {feat} ({h_name}): mean |SHAP| = {val:.4f}")

# 14. CALIBRATION & BRIER SCORE
print("\n--- 14. CALIBRATION & BRIER SCORE AUDIT ---")
# Brier score per class and overall multi-class
brier_overall = np.mean(np.sum((y_prob_cal - y_test_bin)**2, axis=1))
print(f"Multiclass Brier Score (Sum of Squared Residuals): {brier_overall:.6f}")
for i, dname in enumerate(dnames):
    b_class = brier_score_loss(y_test_bin[:, i], y_prob_cal[:, i])
    print(f"  {dname} One-vs-Rest Brier Score: {b_class:.6f}")

# Expected Calibration Error (ECE)
def calculate_ece(y_true, y_prob_matrix, n_bins=10):
    confidences = np.max(y_prob_matrix, axis=1)
    predictions = np.argmax(y_prob_matrix, axis=1)
    accuracies = (predictions == y_true).astype(float)
    
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        bin_lower, bin_upper = bin_boundaries[i], bin_boundaries[i + 1]
        in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
        prop_in_bin = np.mean(in_bin)
        if prop_in_bin > 0:
            acc_in_bin = np.mean(accuracies[in_bin])
            conf_in_bin = np.mean(confidences[in_bin])
            ece += np.abs(acc_in_bin - conf_in_bin) * prop_in_bin
    return ece

ece_val = calculate_ece(y_test, y_prob_cal)
print(f"Multi-class Expected Calibration Error (ECE, 10 bins): {ece_val:.6f}")

# 15. OCR EVALUATION VERIFICATION
print("\n--- 15. OCR PIPELINE METRICS AUDIT ---")
ocr_path = os.path.join(REPORTS_DIR, "ocr_evaluation_metrics.json")
with open(ocr_path, "r") as f:
    ocr_metrics = json.load(f)
print(f"Contents of ocr_evaluation_metrics.json:\n{json.dumps(ocr_metrics, indent=2)}")

ocr_pipe_path = os.path.join(REPORTS_DIR, "pipeline_error_audit.json")
with open(ocr_pipe_path, "r") as f:
    ocr_pipe = json.load(f)
print(f"Contents of pipeline_error_audit.json:\n{json.dumps(ocr_pipe, indent=2)}")
