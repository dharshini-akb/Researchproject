# RareDXAI: Manuscript Figure Plan

**Project:** *RareDXAI: A Human Phenotype Ontology-Based Framework for Rare Disease Prediction*  
**Date:** September 4, 2026  

---

## Recommended Primary Manuscript Figures

### Figure 1: RareDXAI System Architecture & End-to-End Workflow
**Target Section:** Methods – *System Architecture & Prediction Framework*  
**Description:** High-level schematic illustrating the three-tier framework: (A) Clinical document ingestion & exploratory OCR concept mapping; (B) Standardized Human Phenotype Ontology (HPO) feature encoding with demographic indicators; (C) Calibrated Random Forest predictive engine producing multiclass probability distributions and SHAP feature attributions.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   (A) CLINICAL DATA INGESTION                                    │
│  [ Published Clinical Genetics Literature / Electronic Case Reports (PDF / Image / Phenopacket) ]│
│                                                │                                                 │
│                        ▼ (Upstream OCR / Text Entity Ingestion)                                  │
│               [ Extracted Clinical Text & Standardized HPO Concept Mappings ]                    │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   (B) ONTOLOGY VECTORIZATION                                     │
│  [ Binary Phenotype Matrix: 78 Training HPO Terms + 3 One-Hot Sex Categories = 81 ML Predictors ]│
│                                                │                                                 │
│                     ▼ (Zero-Leakage Grouped-by-Profile Stratified Split)                         │
│                    [ Train: 60% (N=230) | Val: 20% (N=77) | Test: 20% (N=78) ]                   │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                (C) PREDICTION & EXPLAINABILITY                                   │
│            [ Calibrated Random Forest Classifier with 5-Fold Internal Platt Scaling ]            │
│                                                │                                                 │
│        ┌───────────────────────────────────────┴───────────────────────────────────────┐          │
│        ▼                                                                               ▼          │
│ [ Calibrated Disease Probabilities ]                           [ SHAP Decision Attributions ]     │
│ - KBG Syndrome:         94.2%                                  - HP:0001572 (Macrodontia): +0.384 │
│ - White-Sutton Syndrome: 4.1%                                  - HP:0001155 (Hand Anom):   +0.145 │
│ - Xia-Gibbs Syndrome:    1.7%                                  - HP:0001252 (Hypotonia):   -0.082 │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Figure 2: Literature Identification, Screening, and Cohort Provenance Flowchart (PRISMA-Style)
**Target Section:** Results – *Patient Provenance & Quarantine Curation*  
**Description:** Participant and publication flow diagram documenting the screening of 52 candidate literature sources, the exclusion of 4 sources (59 candidate records), and the final assembly of the 385-patient cohort across 48 included publications.

```
                              [ Literature Identification ]
                        52 Literature Sources Evaluated Across
                             KBG, White-Sutton, Xia-Gibbs
                               (444 Candidate Records)
                                          │
                                          ▼
                   ┌──────────────────────────────────────────────┐
                   │           Quarantine & Exclusion Audit       │
                   │  - Low et al. 2016 (Table 2 Review): 32 cases│
                   │  - Ockeloen et al. 2015:             20 cases│
                   │  - Walz et al. 2015:                  6 cases│
                   │  - Low et al. 2017:                   1 case │
                   │  Total Excluded: 4 Sources (59 Records)      │
                   └──────────────────────────────────────────────┘
                                          │
                                          ▼
                              [ Verified Retained Cohort ]
                                 48 Included Publications
                               (N = 385 Individual Patients)
                                          │
                   ┌──────────────────────┼──────────────────────┐
                   ▼                      ▼                      ▼
            [ KBG Syndrome ]     [ White-Sutton Synd. ]   [ Xia-Gibbs Synd. ]
             39 Publications         4 Publications         5 Publications
             n = 298 Patients        n = 45 Patients        n = 42 Patients
                   │                      │                      │
                   └──────────────────────┼──────────────────────┘
                                          │
                                          ▼
                   ┌──────────────────────────────────────────────┐
                   │     Zero-Leakage Grouped Stratified Split    │
                   └──────────────────────────────────────────────┘
                                          │
                  ┌───────────────────────┼───────────────────────┐
                  ▼                       ▼                       ▼
          [ Training Set ]        [ Validation Set ]       [ Held-Out Test Set ]
            N = 230 (60%)            N = 77 (20%)             N = 78 (20%)
        - HPO Vocab (78 terms)   - Hyperparameter Check   - LOCKED EVALUATION
        - Calibration CV Loops                            - Accuracy: 98.72%
                                                          - Macro-F1: 0.9776
```

---

### Figure 3: Multiclass ROC and Precision-Recall Curves (Held-Out Test Set, $N=78$)
**Target Section:** Results – *Discriminative Performance Across Decision Thresholds*  
**Supporting Assets:** [`assets/pr_curve.html`](file:///d:/finalresearchproject/assets/pr_curve.html)  
**Description:** (A) Multi-class One-vs-Rest Receiver Operating Characteristic (ROC) curves demonstrating $\text{AUROC} = 1.000$ across all three disease targets. (B) Precision-Recall curves showing $\text{AUPRC} = 1.000$ for White-Sutton, Xia-Gibbs, and KBG syndromes.

---

### Figure 4: Held-Out Test Confusion Matrix and Per-Class Predictive Accuracy
**Target Section:** Results – *Classification Precision & Error Audit*  
**Description:** Visual heatmap of the $3 \times 3$ confusion matrix on the locked test cohort ($N=78$), detailing the 77 correctly classified cases and the single atypical White-Sutton case misclassified as KBG syndrome.

```text
                             PREDICTED CLASS
                      White-Sutton    Xia-Gibbs    KBG Syndrome
                    ┌──────────────┬─────────────┬──────────────┐
       White-Sutton │      8       │      0      │      1       │  Recall: 88.89%
                    ├──────────────┼─────────────┼──────────────┤
ACTUAL  Xia-Gibbs   │      0       │      9      │      0       │  Recall: 100.0%
CLASS               ├──────────────┼─────────────┼──────────────┤
       KBG Syndrome │      0       │      0      │      60      │  Recall: 100.0%
                    └──────────────┴─────────────┴──────────────┘
                      Prec: 100.0%   Prec: 100.0%   Prec: 98.36%
```

---

### Figure 5: Global and Disease-Specific SHAP Phenotypic Importance Plots
**Target Section:** Results – *Model Interpretability & Feature Attribution*  
**Supporting Code:** [`explainability/shap_explainer.py`](file:///d:/finalresearchproject/explainability/shap_explainer.py)  
**Description:** Summary beeswarm and mean absolute SHAP value bar charts showing the top clinical phenotypic indicators influencing model predictions for KBG syndrome (e.g., macrodontia, hand anomalies), White-Sutton syndrome (e.g., autism spectrum disorder, motor delay), and Xia-Gibbs syndrome (e.g., thin upper lip vermilion, hypotonia, sleep apnea).

---

### Figure 6: Probability Calibration and Reliability Curves
**Target Section:** Results – *Probability Calibration & Decision Reliability*  
**Supporting Code:** `scratch/audit_full_verification.py`  
**Description:** Reliability diagram comparing predicted probabilities against empirical disease fractions, demonstrating low multiclass Brier score ($0.0419$) and Expected Calibration Error ($\text{ECE} = 8.59\%$).
