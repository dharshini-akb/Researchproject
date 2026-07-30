# Rare Disease Prediction System using Human Phenotype Ontology (HPO)

An AI-powered web application and research framework designed to predict selected rare genetic diseases from patient phenotype symptom profiles.

---

## 🧬 Project Overview
This project benchmarks classical machine learning (Random Forest) against deep learning (TabNet) and six baseline classifiers (SVM, Logistic Regression, Decision Tree, Naive Bayes, KNN, XGBoost) to classify patients into three rare syndromic cohorts:
1. **White-Sutton syndrome** (`OMIM:616364`)
2. **Xia-Gibbs syndrome** (`OMIM:615829`)
3. **Cornelia de Lange syndrome 1** (`OMIM:122470`)

Predictions are resolved globally and locally using Shapley Additive exPlanations (SHAP) and neural attention masks.

---

## 📁 Workspace Directory Structure
```text
d:\finalresearchproject\
├── assets/                       # Stylesheets and logo images
│   ├── styles.css                # Custom CSS theme for Streamlit
│   └── medical_illustration.png  # Genotyping landing illustration
├── components/                   # Reusable Streamlit UI code
│   ├── cards.py                  # Medical probability cards
│   └── charts.py                 # Plotly CM, ROC, and comparison plots
├── config/                       # Settings
│   └── system_config.py          # Paths, thresholds, parameters
├── data/                         # Data directory
│   ├── raw/                      # phenotype.hpoa, hp.obo, and CSV records
│   ├── processed/                # Cleaned cohort files and vocabs
│   └── splits/                   # Manifests (train, validation, test)
├── explainability/               # SHAP interpretation code
│   └── shap_explainer.py         # SHAP TreeExplainer & TabNet wrappers
├── models/                       # Model classes and serialized models
│   ├── base_model.py             # Abstract base model class
│   ├── random_forest.py          # Calibrated Random Forest wrapper
│   └── tabnet.py                 # PyTorch TabNet architecture
├── pages/                        # Multi-page Streamlit views
│   ├── 1_Disease_Prediction.py   # Symptom selection and inference panel
│   ├── 2_Explainability.py       # SHAP and attention charts page
│   ├── 3_Model_Comparison.py     # Metrics charts and CM/ROC comparison
│   ├── 4_Dataset_Information.py  # Data ontology, split sizes, Mermaid flow
│   └── 5_About_Project.py        # Lit review and future work
├── reports/                      # Benchmarking results and logs
│   ├── app.log                   # Application logs
│   ├── baseline_benchmarks.json  # Baseline classifier metrics
│   ├── model_comparison.json     # Primary RF vs TabNet comparison
│   └── scientific_validation_results.json # Data leakage & CV stats
├── training/                     # Orchestration scripts
│   ├── train_rf.py               # Retrains Random Forest model
│   ├── train_tabnet.py           # Retrains TabNet model
│   └── evaluate.py               # Evaluates and compares performance
├── main.py                       # Home landing page entrypoint
├── requirements.txt              # Project dependencies
└── README.md                     # Documentation
```

---

## 🚀 Getting Started

### 1. Installation
Clone the repository and install the dependencies listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Download Official Datasets & Preprocess
Run the download script and execute data ingestion:
```bash
python download_data.py
python -m preprocessing.generate_cohort
python -m preprocessing.preprocess
```

### 3. Train and Benchmark Models
Retrain the model binaries and generate comparison logs:
```bash
python -m training.train_rf
python -m training.train_tabnet
python -m training.evaluate
python -m verify_scientific
python -m benchmark_baselines
python -m generate_plots
```

### 4. Run the Streamlit Dashboard
Launch the local web dashboard:
```bash
streamlit run main.py
```

---

## 📊 Summary of Benchmarks
- **Random Forest**: **100% Accuracy & F1 Score** on held-out test split, 100% Stratified Cross-Validation score.
- **Baselines (XGBoost, SVM, NB, LR, DT, KNN)**: **100% Accuracy** (linearly separable multi-hot features).
- **TabNet**: **33.3% Accuracy** (collapsed to majority class in low-data regimes).
