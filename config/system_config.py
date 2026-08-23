import os

# Base paths
WORKSPACE_DIR = r"d:\finalresearchproject"
DATA_DIR = os.path.join(WORKSPACE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
SPLITS_DIR = os.path.join(DATA_DIR, "splits")
REPORTS_DIR = os.path.join(WORKSPACE_DIR, "reports")
ASSETS_DIR = os.path.join(WORKSPACE_DIR, "assets")

# Output artifact directories
ARTIFACTS_DIR = os.path.join(WORKSPACE_DIR, "models")  # Store serialized model binaries here
PREPROC_ARTIFACTS_DIR = os.path.join(PROCESSED_DATA_DIR, "metadata")

# Disease mappings
DISEASE_MAP = {
    "OMIM:616364": 0, # White-Sutton Syndrome
    "OMIM:615829": 1, # Xia-Gibbs Syndrome
    "OMIM:148050": 2  # KBG Syndrome
}

DISEASE_NAMES = {
    0: "White-Sutton Syndrome",
    1: "Xia-Gibbs Syndrome",
    2: "KBG Syndrome"
}

DISEASE_OMIMS = {
    0: "OMIM:616364",
    1: "OMIM:615829",
    2: "OMIM:148050"
}

# Configuration configurations for feature types
# CONFIG_A: HPO symptoms only
# CONFIG_B: HPO symptoms + Sex (one-hot)
DEFAULT_FEATURE_CONFIG = "CONFIG_B"

# Threshold for confidence
DEFAULT_CONFIDENCE_THRESHOLD = 0.50

# Random Forest parameters
RF_PARAMS = {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42,
    "class_weight": "balanced"
}

# TabNet/Deep Learning parameters
TABNET_PARAMS = {
    "input_dim": None,          # Set dynamically based on vocabulary size + sex columns
    "output_dim": 3,            # 3 diseases
    "n_d": 16,                  # Width of the decision prediction layer
    "n_a": 16,                  # Width of the attention embedding layer
    "n_steps": 3,               # Number of steps in the architecture
    "gamma": 1.3,               # Sparsity coefficient
    "n_shared": 2,              # Number of shared GLU decision blocks
    "n_independent": 2,         # Number of independent GLU decision blocks
    "lambda_sparse": 1e-4,      # Sparsity regularization coefficient
    "learning_rate": 0.01,
    "batch_size": 32,
    "epochs": 150,
    "seed": 42
}
