# RareDXAI: Manuscript Table Plan

**Project:** *RareDXAI: A Human Phenotype Ontology-Based Framework for Rare Disease Prediction*  
**Date:** September 4, 2026  

---

## Recommended Primary Manuscript Tables

### Table 1: Clinical Cohort and Demographic Characteristics
**Target Section:** Results – *Patient Cohort & Phenotypic Representation*  
**Supporting File:** [`data/expanded_real_patient_hpo_dataset.csv`](file:///d:/finalresearchproject/data/expanded_real_patient_hpo_dataset.csv)  
**Code Reference:** `scratch/audit_full_verification.py`

| Syndrome Target | Total Patients ($N$) | Percentage (%) | Male ($n$) | Female ($n$) | Unknown Sex ($n$) | Mean HPO Terms / Patient | Molecular Variant Confirmation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **KBG Syndrome** (*ANKRD11*) | 298 | 77.40% | 158 | 129 | 11 | $14.12 \pm 3.85$ | 100.0% (Pathogenic *ANKRD11* / 16q24.3 microdeletion) |
| **White-Sutton Syndrome** (*POGZ*) | 45 | 11.69% | 24 | 18 | 3 | $15.24 \pm 4.10$ | 100.0% (Heterozygous de-novo *POGZ* pathogenic variant) |
| **Xia-Gibbs Syndrome** (*AHDC1*) | 42 | 10.91% | 21 | 18 | 3 | $14.88 \pm 4.42$ | 100.0% (Heterozygous de-novo *AHDC1* truncating variant) |
| **Total Evaluated Cohort** | **385** | **100.00%** | **203 (52.7%)** | **165 (42.9%)** | **17 (4.4%)** | **$14.36 \pm 4.12$** | **100.0% Confirmed Pathogenic** |

---

### Table 2: Literature Provenance and Source Attribution
**Target Section:** Methods – *Literature Curation & Data Provenance*  
**Supporting File:** [`reports/final_publication_provenance_audit.csv`](file:///d:/finalresearchproject/reports/final_publication_provenance_audit.csv)  
**Code Reference:** `scratch/generate_publication_provenance_files.py`

| Disease Target | Major Contributing Cohorts | Contributing Publications ($n$) | Retained Patients ($n$) | Quarantined Duplicate Records ($n$) |
| :--- | :--- | :---: | :---: | :---: |
| **White-Sutton Syndrome** | Assia Batzir 2020 ($22$), Nagy 2022 ($13$), White 2016 ($5$), Ye 2015 ($5$) | 4 | 45 | 0 |
| **Xia-Gibbs Syndrome** | Jiang 2018 ($20$), Khayat 2021 ($8$), Yang 2015 ($7$), Romano 2022 ($5$), Cheng 2019 ($2$) | 5 | 42 | 0 |
| **KBG Syndrome** | Martinez-Cayuelas 2023 ($67$), Goldenberg 2016 ($38$), Gnazzo 2020 ($31$), Parenti 2021 ($23$), Kutkowska 2021 ($22$), Murray 2017 ($14$), Gao 2022 ($13$), Scarano 2013 ($12$), Novara 2017 ($11$), Low 2016 UK ($11$), Sirmaci 2011 ($7$), Van Dongen 2019 ($7$), Case series/reports ($52$) | 39 | 298 | 59 (Low 2016 review: 32, Ockeloen: 20, Walz: 6, Low 2017: 1) |
| **TOTAL** | **Multicenter International Cohorts** | **48 Publications** | **385 Patients** | **59 Quarantined** |

---

### Table 3: Multiclass Benchmark Model Performance (Held-Out Test Set, $N = 78$)
**Target Section:** Results – *Diagnostic Model Benchmarking*  
**Supporting File:** [`reports/expansion_scientific_audit_results.json`](file:///d:/finalresearchproject/reports/expansion_scientific_audit_results.json)  
**Code Reference:** `scratch/audit_full_verification.py`

| Model Architecture | Test Accuracy [Wilson 95% CI] | Balanced Accuracy | Macro Precision | Macro Recall | Macro Specificity | Macro F1-Score | Macro AUROC | Multiclass Brier Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Calibrated Random Forest (Proposed)**| **0.9872 [0.9309, 0.9977]** | **0.9630** | **0.9945** | **0.9630** | **0.9815** | **0.9776** | **1.0000** | **0.0419** |
| Standard Random Forest | 1.0000 [0.9532, 1.0000] | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0500 |
| Logistic Regression (L2) | 1.0000 [0.9532, 1.0000] | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0236 |
| Support Vector Machine (RBF) | 0.9615 [0.8917, 0.9878] | 0.8889 | 0.9841 | 0.8889 | 0.9444 | 0.9306 | 1.0000 | 0.0264 |
| Decision Tree Classifier | 0.9615 [0.8917, 0.9878] | 0.8889 | 0.9841 | 0.8889 | 0.9444 | 0.9252 | 0.9534 | 0.0603 |
| K-Nearest Neighbors ($k=5$) | 0.9615 [0.8917, 0.9878] | 0.9204 | 0.9557 | 0.9204 | 0.9581 | 0.9325 | 0.9970 | 0.0513 |
| Naive Bayes (Gaussian) | 0.9744 [0.9112, 0.9931] | 0.9259 | 0.9394 | 0.9259 | 0.9903 | 0.9250 | 1.0000 | 0.0513 |
| XGBoost Classifier | 0.9615 [0.8917, 0.9878] | 0.8889 | 0.9841 | 0.8889 | 0.9444 | 0.9306 | 1.0000 | 0.0559 |

---

### Table 4: Per-Class Diagnostic Performance Breakdown (Calibrated Random Forest)
**Target Section:** Results – *Class-Specific Discriminative Ability*  
**Supporting File:** [`reports/expansion_scientific_audit_results.json`](file:///d:/finalresearchproject/reports/expansion_scientific_audit_results.json)  
**Code Reference:** `scratch/audit_full_verification.py`

| Target Disease | Test Support ($n$) | Correct ($n$) | Sensitivity (Recall) | Specificity | Positive Predictive Value (Precision) | F1-Score | One-vs-Rest AUROC | One-vs-Rest Brier Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **White-Sutton Syndrome** | 9 | 8 | 0.8889 ($8/9$) | 1.0000 ($69/69$) | 1.0000 ($8/8$) | 0.9412 | 1.0000 | 0.0137 |
| **Xia-Gibbs Syndrome** | 9 | 9 | 1.0000 ($9/9$) | 1.0000 ($69/69$) | 1.0000 ($9/9$) | 1.0000 | 1.0000 | 0.0084 |
| **KBG Syndrome** | 60 | 60 | 1.0000 ($60/60$) | 0.9444 ($17/18$) | 0.9836 ($60/61$) | 0.9917 | 1.0000 | 0.0198 |
| **Macro Average** | **78** | **77** | **0.9630** | **0.9815** | **0.9945** | **0.9776** | **1.0000** | **0.0140 (OvR Mean)** |

---

### Table 5: Key Phenotypic Features Strongly Associated with Decision Boundaries
**Target Section:** Results – *Model Interpretability & Phenotypic Attribution*  
**Supporting File:** [`explainability/shap_explainer.py`](file:///d:/finalresearchproject/explainability/shap_explainer.py)  
**Code Reference:** `scratch/audit_full_verification.py`

| Rank | HPO Term ID | Canonical Phenotype Name | Associated Target Condition | Mean Absolute SHAP Value | Clinical Phenotypic Context |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **1** | `HP:0000219` | Thin upper lip vermilion | Xia-Gibbs / KBG | $0.0614$ | Hallmark facial dysmorphic sign in neurodevelopmental syndromes |
| **2** | `HP:0001155` | Abnormality of the hand | KBG Syndrome | $0.0472$ | Characteristic brachydactyly and fifth-finger clinodactyly |
| **3** | `HP:0001252` | Muscular hypotonia | Xia-Gibbs / KBG | $0.0470$ | Prominent infantile hypotonia characteristic of *AHDC1* disruption |
| **4** | `HP:0000337` | Broad forehead | Xia-Gibbs Syndrome | $0.0440$ | Distinctive craniofacial feature in Xia-Gibbs syndrome |
| **5** | `HP:0001572` | Macrodontia of central incisors | KBG Syndrome | $0.0435$ | **Cardinal pathognomonic diagnostic sign** of KBG syndrome |
| **6** | `HP:0000717` | Autism spectrum disorder | White-Sutton Syndrome | $0.0408$ | Frequent behavioral phenotype associated with *POGZ* variants |
| **7** | `HP:0001270` | Motor delay | White-Sutton Syndrome | $0.0308$ | Early developmental motor milestone delay |
| **8** | `HP:0001328` | Specific learning disability | White-Sutton / KBG | $0.0238$ | Characteristic cognitive profile in syndromic intellectual disability |
| **9** | `HP:0001249` | Intellectual disability | White-Sutton / Xia-Gibbs | $0.0231$ | Core neurodevelopmental manifestation |
| **10** | `HP:0000750` | Delayed speech development | White-Sutton / Xia-Gibbs | $0.0226$ | Expressive speech and language impairment |
