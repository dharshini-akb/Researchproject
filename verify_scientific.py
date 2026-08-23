import os
import json
import torch
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from config import system_config
from utils import logger, metrics
from models.random_forest import RandomForestModel
from models.tabnet import TabNetModel, TabNetCore
from explainability.shap_explainer import RareDiseaseExplainer
import preprocessing.data_loader as data_loader
from preprocessing.preprocess import clean_data

log = logger.get_logger("verify_scientific")

def run_leakage_checks(X_train, X_val, X_test):
    """
    Checks if there is any overlap in features or duplicate patient profiles across splits.
    """
    log.info("Running train-val-test data leakage verification...")
    
    # 1. Overlap of row vectors (duplicate profiles)
    train_tuples = set(tuple(x) for x in X_train.values)
    val_tuples = set(tuple(x) for x in X_val.values)
    test_tuples = set(tuple(x) for x in X_test.values)
    
    train_val_overlap = len(train_tuples.intersection(val_tuples))
    train_test_overlap = len(train_tuples.intersection(test_tuples))
    val_test_overlap = len(val_tuples.intersection(test_tuples))
    
    log.info(f"Unique profile counts - Train: {len(train_tuples)}, Val: {len(val_tuples)}, Test: {len(test_tuples)}")
    log.info(f"Symptom profile overlaps - Train-Val: {train_val_overlap}, Train-Test: {train_test_overlap}, Val-Test: {val_test_overlap}")
    
    # 2. Check duplicate exact matches (identical rows in combined)
    combined = pd.concat([X_train, X_val, X_test])
    num_duplicates_total = combined.duplicated().sum()
    
    # Check if dimensions match
    dim_match = X_train.shape[1] == X_val.shape[1] == X_test.shape[1]
    
    return {
        "train_val_overlap_profiles": train_val_overlap,
        "train_test_overlap_profiles": train_test_overlap,
        "val_test_overlap_profiles": val_test_overlap,
        "total_duplicate_profiles_across_dataset": int(num_duplicates_total),
        "dimensions_match_across_splits": bool(dim_match),
        "feature_count": X_train.shape[1]
    }

def run_rf_cross_validation(df_full_train_raw):
    """
    Performs 5-fold Stratified Cross Validation for Random Forest and reports metrics,
    fitting the HPO vocabulary and feature vectorization *inside* each training fold.
    """
    log.info("Running 5-fold Stratified Cross-Validation on Random Forest with inside-fold preprocessing...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    # Map target
    y = df_full_train_raw['disease_id'].map(system_config.DISEASE_MAP)
    
    accs, precs, recs, f1s = [], [], [], []
    sex_categories = ['MALE', 'FEMALE', 'UNKNOWN_SEX']
    sex_mapping = {cat: idx for idx, cat in enumerate(sex_categories)}
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(df_full_train_raw, y)):
        df_fold_train = df_full_train_raw.iloc[train_idx].reset_index(drop=True)
        df_fold_val = df_full_train_raw.iloc[val_idx].reset_index(drop=True)
        y_fold_train = y.iloc[train_idx].reset_index(drop=True)
        y_fold_val = y.iloc[val_idx].reset_index(drop=True)
        
        # Fit vocabulary on training fold only
        active_terms = set()
        for idx, row in df_fold_train.iterrows():
            hpo_str = str(row['hpo_ids']).strip()
            if hpo_str and hpo_str != "nan":
                active_terms.update(hpo_str.split('|'))
        hpo_vocab = sorted(list(active_terms))
        
        # Encode HPOs
        def encode_hpos(df_split, vocab):
            encoded = []
            for idx, row in df_split.iterrows():
                patient_hpos = set(str(row['hpo_ids']).strip().split('|'))
                vec = [1 if term in patient_hpos else 0 for term in vocab]
                encoded.append(vec)
            return pd.DataFrame(encoded, columns=vocab)
            
        def encode_sex(df_split):
            encoded_sex = []
            for idx, row in df_split.iterrows():
                sex_val = str(row['sex']).strip().upper()
                vec = [0] * len(sex_categories)
                if sex_val in sex_mapping:
                    vec[sex_mapping[sex_val]] = 1
                else:
                    vec[sex_mapping['UNKNOWN_SEX']] = 1
                encoded_sex.append(vec)
            return pd.DataFrame(encoded_sex, columns=[f"sex_{cat}" for cat in sex_categories])
            
        X_fold_train_hpo = encode_hpos(df_fold_train, hpo_vocab)
        X_fold_val_hpo = encode_hpos(df_fold_val, hpo_vocab)
        X_fold_train_sex = encode_sex(df_fold_train)
        X_fold_val_sex = encode_sex(df_fold_val)
        
        X_fold_train = pd.concat([X_fold_train_hpo, X_fold_train_sex], axis=1)
        X_fold_val = pd.concat([X_fold_val_hpo, X_fold_val_sex], axis=1)
        
        # Initialize and fit calibrated RF on the training fold
        rf = RandomForestClassifier(**system_config.RF_PARAMS)
        calibrated = CalibratedClassifierCV(estimator=rf, method='sigmoid', cv=3)
        calibrated.fit(X_fold_train, y_fold_train)
        
        preds = calibrated.predict(X_fold_val)
        
        p, r, f, _ = precision_recall_fscore_support(y_fold_val, preds, average='macro', zero_division=0)
        
        accs.append(accuracy_score(y_fold_val, preds))
        precs.append(p)
        recs.append(r)
        f1s.append(f)
        
    return {
        "accuracy_mean": float(np.mean(accs)),
        "accuracy_std": float(np.std(accs)),
        "precision_mean": float(np.mean(precs)),
        "precision_std": float(np.std(precs)),
        "recall_mean": float(np.mean(recs)),
        "recall_std": float(np.std(recs)),
        "f1_mean": float(np.mean(f1s)),
        "f1_std": float(np.std(f1s))
    }


def train_optimized_tabnet(X_train, y_train, X_val, y_val, X_test, y_test):
    """
    Retrains TabNet with optimized hyperparameters.
    """
    log.info("Optimizing and retraining TabNet...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    input_dim = X_train.shape[1]
    
    # Optimized hyperparams
    opt_params = {
        "n_d": 8,
        "n_a": 8,
        "n_steps": 4,
        "gamma": 1.5,
        "lambda_sparse": 1e-3,
        "learning_rate": 0.005,
        "batch_size": 16,
        "virtual_batch_size": 4,
        "epochs": 250,
        "weight_decay": 1e-3
    }
    
    # Rebuild model
    model = TabNetCore(
        input_dim=input_dim,
        output_dim=3,
        n_d=opt_params["n_d"],
        n_a=opt_params["n_a"],
        n_steps=opt_params["n_steps"],
        gamma=opt_params["gamma"],
        virtual_batch_size=opt_params["virtual_batch_size"]
    ).to(device)
    
    X_train_t = torch.tensor(X_train.values, dtype=torch.float32).to(device)
    y_train_t = torch.tensor(y_train.values, dtype=torch.long).to(device)
    X_val_t = torch.tensor(X_val.values, dtype=torch.float32).to(device)
    y_val_t = torch.tensor(y_val.values, dtype=torch.long).to(device)
    X_test_t = torch.tensor(X_test.values, dtype=torch.float32).to(device)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=opt_params["learning_rate"], weight_decay=opt_params["weight_decay"])
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=15)
    criterion = torch.nn.CrossEntropyLoss()
    
    best_val_loss = float('inf')
    patience = 35
    patience_counter = 0
    best_model_state = None
    
    batch_size = opt_params["batch_size"]
    
    for epoch in range(opt_params["epochs"]):
        model.train()
        permutation = torch.randperm(X_train_t.size()[0])
        epoch_loss = 0.0
        
        for i in range(0, X_train_t.size()[0], batch_size):
            optimizer.zero_grad()
            indices = permutation[i:i+batch_size]
            bx, by = X_train_t[indices], y_train_t[indices]
            
            logits, _, sparsity_loss = model(bx)
            loss = criterion(logits, by) + opt_params["lambda_sparse"] * sparsity_loss
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(by)
            
        epoch_loss /= len(X_train_t)
        
        # Val evaluate
        model.eval()
        with torch.no_grad():
            val_logits, _, _ = model(X_val_t)
            val_loss = criterion(val_logits, y_val_t).item()
            val_preds = val_logits.argmax(dim=-1)
            val_acc = (val_preds == y_val_t).float().mean().item()
            
        scheduler.step(val_loss)
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            best_model_state = model.state_dict()
        else:
            patience_counter += 1
            if patience_counter >= patience:
                log.info(f"Early stopping triggered at epoch {epoch+1}")
                break
                
    # Load best weights
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
        
    model.eval()
    with torch.no_grad():
        test_logits, _, _ = model(X_test_t)
        test_probs = torch.softmax(test_logits, dim=-1).cpu().numpy()
        test_preds = test_probs.argmax(axis=-1)
        
    # Evaluate
    acc = accuracy_score(y_test.values, test_preds)
    p, r, f, _ = precision_recall_fscore_support(y_test.values, test_preds, average='macro', zero_division=0)
    
    # Save optimized model
    opt_state = {
        "model_state_dict": model.state_dict(),
        "feature_names": list(X_train.columns),
        "params": opt_params
    }
    torch.save(opt_state, os.path.join(system_config.ARTIFACTS_DIR, "tabnet_model_optimized.pt"))
    
    return {
        "accuracy": float(acc),
        "precision_macro": float(p),
        "recall_macro": float(r),
        "f1_macro": float(f),
        "params": opt_params,
        "predictions": test_preds.tolist()
    }

def main():
    # Load dataset
    base_dir = os.path.join(system_config.PROCESSED_DATA_DIR, "model_ready", "hpo_plus_sex")
    X_train = pd.read_csv(os.path.join(base_dir, "X_train.csv"))
    y_train = pd.read_csv(os.path.join(base_dir, "y_train.csv"))["target"]
    
    X_val = pd.read_csv(os.path.join(base_dir, "X_validation.csv"))
    y_val = pd.read_csv(os.path.join(base_dir, "y_validation.csv"))["target"]
    
    X_test = pd.read_csv(os.path.join(base_dir, "X_test.csv"))
    y_test = pd.read_csv(os.path.join(base_dir, "y_test.csv"))["target"]
    
    # 1. Leakage
    leakage_stats = run_leakage_checks(X_train, X_val, X_test)
    
    # 2. RF cross validation
    # Load raw patient records and manifests to prepare un-vectorized train+validation subsets
    df_raw = data_loader.load_patient_records()
    df_cleaned = clean_data(df_raw)
    df_train_manifest, df_val_manifest, _ = data_loader.load_splits_manifests()
    train_val_manifest = pd.concat([df_train_manifest, df_val_manifest]).reset_index(drop=True)
    df_full_train_raw = df_cleaned[df_cleaned['case_id'].isin(train_val_manifest['case_id'])].reset_index(drop=True)
    rf_cv_results = run_rf_cross_validation(df_full_train_raw)
    
    # 3. TabNet Optimization
    tabnet_opt_results = train_optimized_tabnet(X_train, y_train, X_val, y_val, X_test, y_test)
    
    # 4. SHAP & Explainability details
    rf_model = RandomForestModel()
    rf_model.load(os.path.join(system_config.ARTIFACTS_DIR, "rf_model.joblib"))
    
    explainer = RareDiseaseExplainer()
    explainer.initialize_rf_explainer(rf_model, X_train)
    
    # Global feature importances
    global_importances = explainer.get_global_importance_rf(X_train)
    
    # Local explanations: one sample from each class
    local_samples = {}
    for c in range(3):
        # find first sample of class c in test
        idx = y_test[y_test == c].index[0]
        sample_df = X_test.iloc[[idx]]
        local_samples[c] = explainer.explain_patient_rf(sample_df)
        
    validation_results = {
        "leakage_statistics": leakage_stats,
        "rf_cross_validation": rf_cv_results,
        "tabnet_optimized": tabnet_opt_results,
        "global_importance_rf": global_importances,
        "local_explanations_rf": local_samples
    }
    
    # Save validation metadata
    out_path = os.path.join(system_config.REPORTS_DIR, "scientific_validation_results.json")
    with open(out_path, "w") as f:
        json.dump(validation_results, f, indent=4)
        
    log.info(f"Scientific verification run complete. Saved metadata to {out_path}")
    print("Scientific verification script run completed successfully.")

if __name__ == "__main__":
    main()
