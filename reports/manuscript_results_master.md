# RareDXAI: Master Manuscript Results & Evidence Verification Table

**Project:** *RareDXAI: A Human Phenotype Ontology-Based Framework for Rare Disease Prediction*  
**Date:** September 4, 2026  
**Status:** LOCKED & AUTHORITATIVE

---

## 1. Master Numerical Results Table

| Category | Metric / Parameter | Authoritative Final Value | Primary Source File | Script / Code Source | Traceability Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Cohort Size** | Total verified patients ($N$) | **385** | [`data/expanded_real_patient_hpo_dataset.csv`](file:///d:/finalresearchproject/data/expanded_real_patient_hpo_dataset.csv) | `scratch/run_full_expansion_pipeline.py` | **VERIFIED** |
| **Disease Count**| KBG syndrome | **298 (77.40%)** | [`data/expanded_real_patient_hpo_dataset.csv`](file:///d:/finalresearchproject/data/expanded_real_patient_hpo_dataset.csv) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Disease Count**| White-Sutton syndrome | **45 (11.69%)** | [`data/expanded_real_patient_hpo_dataset.csv`](file:///d:/finalresearchproject/data/expanded_real_patient_hpo_dataset.csv) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Disease Count**| Xia-Gibbs syndrome | **42 (10.91%)** | [`data/expanded_real_patient_hpo_dataset.csv`](file:///d:/finalresearchproject/data/expanded_real_patient_hpo_dataset.csv) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Sex Distribution** | Male / Female / Unknown | **203 (52.7%) / 165 (42.9%) / 17 (4.4%)** | [`data/expanded_real_patient_hpo_dataset.csv`](file:///d:/finalresearchproject/data/expanded_real_patient_hpo_dataset.csv) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Provenance** | Contributing peer-reviewed publications | **48 distinct publications** | [`reports/final_publication_provenance_audit.csv`](file:///d:/finalresearchproject/reports/final_publication_provenance_audit.csv) | `scratch/generate_publication_provenance_files.py` | **VERIFIED** |
| **Provenance** | KBG contributing publications | **39 distinct publications** | [`reports/final_publication_provenance_audit.csv`](file:///d:/finalresearchproject/reports/final_publication_provenance_audit.csv) | `scratch/generate_publication_provenance_files.py` | **VERIFIED** |
| **Provenance** | White-Sutton contributing publications | **4 distinct publications** | [`reports/final_publication_provenance_audit.csv`](file:///d:/finalresearchproject/reports/final_publication_provenance_audit.csv) | `scratch/generate_publication_provenance_files.py` | **VERIFIED** |
| **Provenance** | Xia-Gibbs contributing publications | **5 distinct publications** | [`reports/final_publication_provenance_audit.csv`](file:///d:/finalresearchproject/reports/final_publication_provenance_audit.csv) | `scratch/generate_publication_provenance_files.py` | **VERIFIED** |
| **Literature Audit**| Screened candidate literature sources | **52 distinct sources** | [`reports/final_publication_provenance_audit.csv`](file:///d:/finalresearchproject/reports/final_publication_provenance_audit.csv) | `scratch/generate_publication_provenance_files.py` | **VERIFIED** |
| **Exclusions** | Quarantined candidate records | **59 records** (32 Low review, 20 Ockeloen, 6 Walz, 1 Low 2017) | [`data/excluded_duplicate_patients_log.csv`](file:///d:/finalresearchproject/data/excluded_duplicate_patients_log.csv) | `scratch/verify_59_records_in_depth.py` | **VERIFIED** |
| **Feature Space**| Total HPO terms across full cohort | **82 terms** | [`data/raw/hp.obo`](file:///d:/finalresearchproject/data/raw/hp.obo) (Release `2026-06-23`) | `scratch/run_full_expansion_pipeline.py` | **VERIFIED** |
| **Feature Space**| Training-only HPO feature vocabulary | **78 terms** | Preprocessing vocabulary fit on $N=230$ | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Feature Space**| Total ML input dimensions | **81 features** (78 HPO + 3 one-hot sex) | Model input feature matrix | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Feature Space**| Validation OOV terms / Test OOV terms | **0 in Val / 4 in Test** (masked out) | Split feature vectorization | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Data Split** | Train / Validation / Test sizes | **230 (59.7%) / 77 (20.0%) / 78 (20.3%)** | Grouped-by-profile stratified partition | `scratch/run_full_expansion_pipeline.py` | **VERIFIED** |
| **Test Performance**| Held-out accuracy ($N=78$) | **0.9872 (98.72%)** [77/78 correct] | [`reports/expansion_scientific_audit_results.json`](file:///d:/finalresearchproject/reports/expansion_scientific_audit_results.json) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Confidence Int.**| Wilson score 95% Confidence Interval | **[0.9309, 0.9977] (93.09% to 99.77%)** | Statistical recalculation | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Test Performance**| Held-out balanced accuracy | **0.9630 (96.30%)** | Model test evaluation | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Test Performance**| Held-out macro precision | **0.9945** | [`reports/expansion_scientific_audit_results.json`](file:///d:/finalresearchproject/reports/expansion_scientific_audit_results.json) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Test Performance**| Held-out macro recall (Sensitivity) | **0.9630** | [`reports/expansion_scientific_audit_results.json`](file:///d:/finalresearchproject/reports/expansion_scientific_audit_results.json) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Test Performance**| Held-out macro specificity | **0.9815** | [`reports/expansion_scientific_audit_results.json`](file:///d:/finalresearchproject/reports/expansion_scientific_audit_results.json) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Test Performance**| Held-out macro F1-score | **0.9776** | [`reports/expansion_scientific_audit_results.json`](file:///d:/finalresearchproject/reports/expansion_scientific_audit_results.json) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Test Performance**| Held-out macro AUROC / AUPRC | **1.0000 / 1.0000** | [`reports/expansion_scientific_audit_results.json`](file:///d:/finalresearchproject/reports/expansion_scientific_audit_results.json) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Confusion Matrix**| Held-out test matrix ($N=78$) | **WS: [8, 0, 1]; XG: [0, 9, 0]; KBG: [0, 0, 60]** | Calibrated RF confusion matrix | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Per-Class Metrics**| White-Sutton: Prec / Rec / F1 / Spec | **1.0000 / 0.8889 / 0.9412 / 1.0000** | Test evaluation ($n=9$) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Per-Class Metrics**| Xia-Gibbs: Prec / Rec / F1 / Spec | **1.0000 / 1.0000 / 1.0000 / 1.0000** | Test evaluation ($n=9$) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Per-Class Metrics**| KBG Syndrome: Prec / Rec / F1 / Spec | **0.9836 / 1.0000 / 0.9917 / 0.9444** | Test evaluation ($n=60$) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Calibration** | Multiclass Brier score (Sum of squared errors) | **0.0419** | Test probability evaluation | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Calibration** | Mean One-vs-Rest Brier score | **0.0140** (WS: 0.0137, XG: 0.0084, KBG: 0.0198) | Test probability evaluation | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Calibration** | Multi-class Expected Calibration Error (ECE) | **0.0859 (8.59%)** (10-bin assessment) | Test probability evaluation | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Cross-Validation**| 5-Fold CV Accuracy (Mean $\pm$ SD) | **0.9714 $\pm$ 0.0223 (97.14% $\pm$ 2.23%)** | [`reports/expansion_scientific_audit_results.json`](file:///d:/finalresearchproject/reports/expansion_scientific_audit_results.json) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Cross-Validation**| 5-Fold CV Macro F1 (Mean $\pm$ SD) | **0.9489 $\pm$ 0.0404 (94.89% $\pm$ 4.04%)** | [`reports/expansion_scientific_audit_results.json`](file:///d:/finalresearchproject/reports/expansion_scientific_audit_results.json) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Stress Validation**| Source-Grouped CV Accuracy (GroupKFold) | **0.7962 $\pm$ 0.2705 (79.62% $\pm$ 27.05%)** | Source-level stress test evaluation | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Stress Validation**| Source-Grouped CV Macro F1 (GroupKFold) | **0.5951 $\pm$ 0.2681 (59.51% $\pm$ 26.81%)** | Source-level stress test evaluation | `scratch/audit_full_verification.py` | **VERIFIED** |
| **Explainability** | Top global decision features | **HP:0000219, HP:0001155, HP:0001252, HP:0000337, HP:0001572** | [`explainability/shap_explainer.py`](file:///d:/finalresearchproject/explainability/shap_explainer.py) | `scratch/audit_full_verification.py` | **VERIFIED** |
| **OCR Pipeline** | EasyOCR Character Error Rate (CER) | **0.1142 (11.42%)** | [`reports/ocr_evaluation_metrics.json`](file:///d:/finalresearchproject/reports/ocr_evaluation_metrics.json) | `training/evaluate_ocr.py` | **VERIFIED** |
| **OCR Pipeline** | EasyOCR Word Error Rate (WER) | **0.9200 (92.00%)** | [`reports/ocr_evaluation_metrics.json`](file:///d:/finalresearchproject/reports/ocr_evaluation_metrics.json) | `training/evaluate_ocr.py` | **VERIFIED** |
| **OCR Mapping** | Concept mapping on clean text vs. noisy OCR | **100.0% clean / 80.0% noisy** | [`reports/pipeline_error_audit.json`](file:///d:/finalresearchproject/reports/pipeline_error_audit.json) | `training/evaluate_pipeline_error.py` | **VERIFIED** |
