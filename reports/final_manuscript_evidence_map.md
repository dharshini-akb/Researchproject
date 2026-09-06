# RareDXAI: Final Manuscript Evidence Map

**Project:** *RareDXAI: A Human Phenotype Ontology-Based Framework for Rare Disease Prediction*  
**Date:** September 4, 2026  
**Status:** COMPLETE, AUDITED & READY FOR WRITING  

---

## 1. Introduction Evidence & Citations

| Manuscript Topic / Statement | Primary Evidence & Repository Source | Supporting File / Reference |
| :--- | :--- | :--- |
| **Diagnostic Odyssey in Rare Diseases** | Diagnostic delays in syndromic neurodevelopmental disorders; need for standardized computational phenotyping | Literature citations (*Am J Med Genet A*, *Genet Med*) |
| **Human Phenotype Ontology (HPO)** | Standardized clinical vocabulary from `hp.obo` (Release `2026-06-23`, Format 1.2) | [`data/raw/hp.obo`](file:///d:/finalresearchproject/data/raw/hp.obo) |
| **Target Syndromic Mimics** | KBG syndrome (*ANKRD11*), White-Sutton syndrome (*POGZ*), and Xia-Gibbs syndrome (*AHDC1*) | Clinical cohort files in `data/` |
| **Contributions of RareDXAI** | (1) Curated multicenter 385-patient cohort; (2) Leakage-controlled HPO vectorization; (3) Calibrated Random Forest; (4) SHAP decision attribution | [`reports/manuscript_results_master.md`](file:///d:/finalresearchproject/reports/manuscript_results_master.md) |

---

## 2. Methods Evidence & Implementation Traceability

| Methodological Component | Technical Specification & Parameters | Authoritative Repository Code |
| :--- | :--- | :--- |
| **Literature Screening & Provenance** | 52 sources screened; 48 peer-reviewed publications included; 59 duplicate/review rows quarantined | [`reports/final_publication_provenance_audit.csv`](file:///d:/finalresearchproject/reports/final_publication_provenance_audit.csv) |
| **Patient Phenotype Standardization** | Canonical mapping from clinical text to HPO term IDs using `hp.obo` release `2026-06-23` | [`preprocessing/preprocess.py`](file:///d:/finalresearchproject/preprocessing/preprocess.py) |
| **Partitioning & Leakage Control** | Grouped-by-profile stratified splitting (60% Train: $N=230$, 20% Val: $N=77$, 20% Test: $N=78$); profile isolation | `scratch/run_full_expansion_pipeline.py` |
| **Feature Space Construction** | 78 binary HPO terms (fitted on training partition only) + 3 one-hot sex categories = 81 ML features | `scratch/audit_full_verification.py` |
| **Model Development & Calibration** | Random Forest (100 estimators, max depth 10, balanced class weights) + Platt scaling (5-fold internal CV) | [`training/train_rf.py`](file:///d:/finalresearchproject/training/train_rf.py) |
| **Comparative Baselines** | TabNet, SVM (RBF), Logistic Regression (L2), XGBoost, Decision Tree, Naive Bayes, KNN | [`reports/baseline_benchmarks.json`](file:///d:/finalresearchproject/reports/baseline_benchmarks.json) |
| **Explainability Framework** | SHAP TreeExplainer on Random Forest feature matrix | [`explainability/shap_explainer.py`](file:///d:/finalresearchproject/explainability/shap_explainer.py) |
| **Exploratory OCR Ingestion** | EasyOCR text extraction and rule-based medical concept mapping dictionary | [`utils/ocr_helper.py`](file:///d:/finalresearchproject/utils/ocr_helper.py) |

---

## 3. Results Evidence & Statistical Benchmarks

| Results Subsection | Key Numerical Finding | Primary Evidence Source |
| :--- | :--- | :--- |
| **Cohort & Phenotypic Scope** | $N=385$ patients (KBG: $298$, WS: $45$, XG: $42$); $370$ unique profiles; $82$ unique HPO terms across dataset | [`data/expanded_real_patient_hpo_dataset.csv`](file:///d:/finalresearchproject/data/expanded_real_patient_hpo_dataset.csv) |
| **Held-Out Test Set Performance** | Accuracy = **$98.72\%$** ($77/78$ correct, Wilson 95% CI: **$93.09\% \text{ to } 99.77\%$**), Macro F1 = **$0.9776$**, AUROC = **$1.0000$** | [`reports/expansion_scientific_audit_results.json`](file:///d:/finalresearchproject/reports/expansion_scientific_audit_results.json) |
| **Per-Class Discriminative Metrics** | WS F1 = **$0.9412$** ($8/9$ recall), XG F1 = **$1.0000$** ($9/9$ recall), KBG F1 = **$0.9917$** ($60/60$ recall) | `scratch/audit_full_verification.py` |
| **Internal Cross-Validation** | 5-Fold Stratified CV: Accuracy = **$97.14\% \pm 2.23\%$**, Macro F1 = **$94.89\% \pm 4.04\%$** | [`reports/expansion_scientific_audit_results.json`](file:///d:/finalresearchproject/reports/expansion_scientific_audit_results.json) |
| **Source-Grouped Stress Validation** | GroupKFold on Source: Accuracy = **$79.62\% \pm 27.05\%$**, Macro F1 = **$59.51\% \pm 26.81\%$** | `scratch/audit_full_verification.py` |
| **Probability Calibration** | Multiclass Brier score = **$0.0419$** (Mean OvR Brier = **$0.0140$**), $\text{ECE} = \mathbf{8.59\%}$ | `scratch/audit_full_verification.py` |
| **Phenotypic Decision Attribution** | Cardinal associations: Macrodontia (`HP:0001572`) for KBG; Autism (`HP:0000717`) for WS; Thin upper lip (`HP:0000219`) & Hypotonia (`HP:0001252`) for XG | [`explainability/shap_explainer.py`](file:///d:/finalresearchproject/explainability/shap_explainer.py) |
| **Exploratory OCR Ingestion** | EasyOCR CER = **$11.42\%$**, WER = **$92.00\%$**; Clean concept mapping = **$100.0\%$**, Noisy = **$80.0\%$** | [`reports/ocr_evaluation_metrics.json`](file:///d:/finalresearchproject/reports/ocr_evaluation_metrics.json) |

---

## 4. Discussion Evidence & Limitations

| Discussion Theme | Key Argument & Scientific Rationale | Supporting Report |
| :--- | :--- | :--- |
| **Clinical Decision Support Utility** | Standardized HPO vectorization provides objective decision aids in overlapping neurodevelopmental mimics | [`reports/manuscript_claim_safety_audit.md`](file:///d:/finalresearchproject/reports/manuscript_claim_safety_audit.md) |
| **Inter-Center Annotation Variance** | Performance reduction in source-grouped validation ($79.62\%$) highlights the challenge of variable phenotyping depth across clinics | [`reports/manuscript_limitations_evidence.md`](file:///d:/finalresearchproject/reports/manuscript_limitations_evidence.md) |
| **Study Limitations** | Retrospective curation, natural class imbalance, closed-set prediction scope (3 diseases) | [`reports/manuscript_limitations_evidence.md`](file:///d:/finalresearchproject/reports/manuscript_limitations_evidence.md) |

---

## 5. Manuscript Tables Plan Summary

1. **Table 1:** Cohort Demographics and Clinical Characteristics (Source: [`data/expanded_real_patient_hpo_dataset.csv`](file:///d:/finalresearchproject/data/expanded_real_patient_hpo_dataset.csv))
2. **Table 2:** Literature Provenance and Source Attribution (Source: [`reports/final_publication_provenance_audit.csv`](file:///d:/finalresearchproject/reports/final_publication_provenance_audit.csv))
3. **Table 3:** Comparative Model Benchmark Performance on Held-Out Test Set (Source: [`reports/expansion_scientific_audit_results.json`](file:///d:/finalresearchproject/reports/expansion_scientific_audit_results.json))
4. **Table 4:** Per-Class Diagnostic Performance Breakdown for Calibrated Random Forest (Source: `scratch/audit_full_verification.py`)
5. **Table 5:** Top HPO Phenotypic Features Strongly Associated with Decision Boundaries (Source: [`explainability/shap_explainer.py`](file:///d:/finalresearchproject/explainability/shap_explainer.py))

---

## 6. Manuscript Figures Plan Summary

1. **Figure 1:** RareDXAI End-to-End System Architecture (Ingestion $\rightarrow$ Vectorization $\rightarrow$ Prediction & SHAP)
2. **Figure 2:** PRISMA-Style Literature Screening and Cohort Provenance Flowchart (52 sources $\rightarrow$ 48 included $\rightarrow$ 385 patients)
3. **Figure 3:** Multi-class ROC and Precision-Recall Curves on Held-Out Test Partition (AUROC = 1.000, AUPRC = 1.000)
4. **Figure 4:** Held-Out Test Confusion Matrix and Error Distribution Heatmap ($77/78$ correct)
5. **Figure 5:** Global and Class-Specific SHAP Decision Importance Plots
6. **Figure 6:** Multi-Class Probability Calibration and Reliability Curves (Brier = 0.0419)

---

## 7. Supplementary Materials Manifest

- **Supplementary File S1:** Complete Patient-by-Patient Provenance Manifest ([`reports/expanded_cohort_provenance_manifest.csv`](file:///d:/finalresearchproject/reports/expanded_cohort_provenance_manifest.csv))
- **Supplementary File S2:** Complete Patient-to-Publication Mapping ([`reports/final_patient_to_publication_map.csv`](file:///d:/finalresearchproject/reports/final_patient_to_publication_map.csv))
- **Supplementary File S3:** Quarantined Records and Exclusion Log ([`reports/final_excluded_publication_audit.csv`](file:///d:/finalresearchproject/reports/final_excluded_publication_audit.csv))
- **Supplementary File S4:** Publication Duplicate Resolution and Overlap Matrix ([`reports/publication_duplicate_resolution.csv`](file:///d:/finalresearchproject/reports/publication_duplicate_resolution.csv), [`reports/publication_patient_overlap_matrix.csv`](file:///d:/finalresearchproject/reports/publication_patient_overlap_matrix.csv))
- **Supplementary File S5:** Machine-Readable Scientific Benchmarking Metrics ([`reports/expansion_scientific_audit_results.json`](file:///d:/finalresearchproject/reports/expansion_scientific_audit_results.json))
