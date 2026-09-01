# Streamlit Deployment Readiness Audit

This document presents a deployment-readiness audit for the **Rare Disease Prediction System** Streamlit application, assessing its compatibility, dependencies, data requirements, and paths for public cloud deployment (such as Streamlit Community Cloud or Hugging Face Spaces).

---

## 1. Streamlit Entry File
- **Entry File:** [main.py](file:///d:/finalresearchproject/main.py)
- **Status:** Valid. It serves as the primary landing page and configures global layouts, sidebars, and navigation to sub-pages located in the `pages/` directory.

---

## 2. Hard-coded Paths Audit
The following hard-coded paths beginning with `d:\finalresearchproject` or `C:\` were detected in the application source code:

| File | Line | Hard-coded String | Impact on Deployment |
| :--- | :--- | :--- | :--- |
| [`config/system_config.py`](file:///d:/finalresearchproject/config/system_config.py) | 4 | `WORKSPACE_DIR = r"d:\finalresearchproject"` | **Critical.** Will cause absolute paths to resolve incorrectly on any other OS or system, crashing the app on startup. |
| [`utils/logger.py`](file:///d:/finalresearchproject/utils/logger.py) | 22 | `log_dir = r"d:\finalresearchproject\reports"` | **Critical.** Will throw write permission or directory non-existence errors on Linux cloud instances. |

> [!IMPORTANT]
> Both paths must be resolved to relative path configurations or system environment variables (e.g., dynamically locating the workspace using `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`) before deployment.

---

## 3. Required Runtime Assets (Models, Ontologies, & Data)
The following files are required for the application to function correctly at runtime:

### Models (in `models/`)
- [`models/rf_model.joblib`](file:///d:/finalresearchproject/models/rf_model.joblib) (814.8 KB) - Primary Random Forest classifier.
- [`models/tabnet_model.pt`](file:///d:/finalresearchproject/models/tabnet_model.pt) (73.4 KB) - TabNet tabular deep learning model state dict.
- [`models/custom_ocr/best_ocr_model.pt`](file:///d:/finalresearchproject/models/custom_ocr/best_ocr_model.pt) (12.8 MB) - CRNN custom handwriting OCR state dict.

### Ontologies and Metadata
- [`data/raw/hp.obo`](file:///d:/finalresearchproject/data/raw/hp.obo) (11.2 MB) - Required at runtime by `pages/1_Disease_Prediction.py` and `pages/7_Patient_Record_Image_Prediction.py` for autocomplete labels and synonyms. Without it, symptom mapping will show "Unknown phenotypic feature".
- [`data/processed/metadata/hpo_feature_vocabulary.json`](file:///d:/finalresearchproject/data/processed/metadata/hpo_feature_vocabulary.json) (877 bytes) - Maps clinical inputs to the model's vocabulary.

### Evaluation & Analytics Data (in `data/` and `reports/`)
- [`data/processed/model_ready/hpo_plus_sex/X_train.csv`](file:///d:/finalresearchproject/data/processed/model_ready/hpo_plus_sex/X_train.csv) (4.2 KB) - Required for SHAP background distribution on `pages/2_Explainability.py`.
- [`data/processed/model_ready/hpo_plus_sex/X_test.csv`](file:///d:/finalresearchproject/data/processed/model_ready/hpo_plus_sex/X_test.csv) (1.8 KB) - Required for demo case selections.
- [`data/processed/model_ready/hpo_plus_sex/y_test.csv`](file:///d:/finalresearchproject/data/processed/model_ready/hpo_plus_sex/y_test.csv) (50 bytes) - Required for showing actual labels in demo cases.
- [`reports/ocr_evaluation_metrics.json`](file:///d:/finalresearchproject/reports/ocr_evaluation_metrics.json) (270 bytes) - Displays baseline vs. custom OCR performance in `pages/7_Patient_Record_Image_Prediction.py`.
- [`reports/pipeline_error_audit.json`](file:///d:/finalresearchproject/reports/pipeline_error_audit.json) (672 bytes) - Displays error-attribution telemetry in `pages/7_Patient_Record_Image_Prediction.py`.

### Non-Runtime Files (Safe to Exclude / Ignore)
- `data/final_real_patient_hpo_dataset.csv`
- `data/real_patient_hpo_dataset.csv`
- `data/raw/phenotype.hpoa`
- All files in `scratch/` and `unused_pages/`

---

## 4. Dependency & Requirements Analysis
The existing `requirements.txt` is incomplete. The table below outlines the status of libraries imported by the runtime pages:

| Import / Module | Package Name | Declared in `requirements.txt`? | Role in App |
| :--- | :--- | :--- | :--- |
| `streamlit` | `streamlit` | Yes (`>=1.30.0`) | Web framework UI |
| `plotly.graph_objects` | `plotly` | Yes (`>=5.18.0`) | Visualization graphs |
| `sklearn` | `scikit-learn` | Yes (`>=1.3.0`) | Random Forest model |
| `shap` | `shap` | Yes (`>=0.44.0`) | Explainability waterfall plots |
| `torch`, `torch.nn` | `torch` | Yes (`>=2.0.0`) | TabNet & Custom OCR inference |
| `reportlab` | `reportlab` | Yes (`>=4.0.0`) | PDF generation |
| `easyocr` | `easyocr` | **No** | Default OCR engine |
| `cv2` | `opencv-python-headless` | **No** | Image crop/manipulation |
| `PIL` | `Pillow` | **No** | Image handling |
| `torchvision` | `torchvision` | **No** | Required dependency of EasyOCR |

> [!WARNING]
> Deploying the application with the current `requirements.txt` will cause the application to crash immediately when navigating to the **Patient Record Image Prediction** page due to a `ModuleNotFoundError` for `easyocr`, `cv2`, `PIL`, or `torchvision`.

---

## 5. Security & Secrets Check
- **API Keys & Secrets:** None found in the code.
- **Passwords & Tokens:** None found.
- All credential risk is **Low**.

---

## 6. Deployment Limits & Large Files
GitHub and Streamlit Community Cloud have file size limits (usually 50-100MB per file).
- The largest files in the repository are:
  1. `data/raw/phenotype.hpoa` (35.6 MB) - *Not needed at runtime.*
  2. `models/custom_ocr/best_ocr_model.pt` (12.8 MB) - *Needed at runtime.*
  3. `data/raw/hp.obo` (11.2 MB) - *Needed at runtime.*
- None of these exceed GitHub's 100MB file limit or Streamlit's resource thresholds, meaning **no Git LFS is required**.

---

## 7. Audit Verdict
**Verdict:** **READY WITH FIXES**

### Critical Action Items Before Deployment
1. **Fix path configuration:** Modify `config/system_config.py` and `utils/logger.py` to use relative path logic.
2. **Update dependencies:** Add `easyocr`, `opencv-python-headless`, `Pillow`, and `torchvision` to `requirements.txt`.
