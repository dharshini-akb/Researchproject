import os
import joblib
import numpy as np
import pandas as pd

WORKSPACE_DIR = r"d:\finalresearchproject"
DATA_DIR = os.path.join(WORKSPACE_DIR, "data")
MODELS_DIR = os.path.join(WORKSPACE_DIR, "models")

df_final = pd.read_csv(os.path.join(DATA_DIR, "final_real_patient_hpo_dataset.csv"))
disease_id_map = {"White-Sutton Syndrome": 0, "Xia-Gibbs Syndrome": 1, "KBG Syndrome": 2}
df_final['target'] = df_final['Disease'].map(disease_id_map)
df_final['profile_key'] = df_final['target'].astype(str) + "_" + df_final['Sex'].fillna("UNKNOWN") + "_" + df_final['HPO_IDs'].fillna("")

from sklearn.model_selection import train_test_split
groups = df_final.groupby('profile_key')
group_summaries = []
for key, group in groups:
    group_summaries.append({'profile_key': key, 'target': group['target'].iloc[0]})
df_groups = pd.DataFrame(group_summaries)

train_keys, temp_keys = train_test_split(
    df_groups['profile_key'], test_size=0.4, random_state=42, stratify=df_groups['target']
)
df_temp_groups = df_groups[df_groups['profile_key'].isin(temp_keys)]
val_keys, test_keys = train_test_split(
    df_temp_groups['profile_key'], test_size=0.5, random_state=42, stratify=df_temp_groups['target']
)

df_train = df_final[df_final['profile_key'].isin(train_keys)].copy().reset_index(drop=True)
df_test = df_final[df_final['profile_key'].isin(test_keys)].copy().reset_index(drop=True)

train_hpo_terms = set()
for idx, row in df_train.iterrows():
    h_ids = str(row['HPO_IDs']).strip().split('|')
    for h in h_ids:
        if h.strip() and h.strip() != "nan":
            train_hpo_terms.add(h.strip())
hpo_vocab = sorted(list(train_hpo_terms))

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

X_test = pd.concat([encode_hpos(df_test), encode_sex(df_test)], axis=1)
y_test = df_test['target']

model_state = joblib.load(os.path.join(MODELS_DIR, "rf_model_expanded.joblib"))
model = model_state["calibrated_model"]

y_prob = model.predict_proba(X_test)

# Let's print the probabilities for Class 2 (KBG)
df_probs = pd.DataFrame({
    'Patient_ID': df_test['Patient_ID'],
    'True_Class': y_test,
    'Prob_KBG': y_prob[:, 2],
    'Prob_WS': y_prob[:, 0],
    'Prob_XG': y_prob[:, 1]
})

print("Class 2 (KBG) probabilities sorted:")
print(df_probs.sort_values(by='Prob_KBG', ascending=False).to_string())
