# RareDXAI Dataset Expansion & Scientific Quality Audit Report

**Date:** September 4, 2026  
**Final Expanded Cohort Size:** $N = 385$ verified individual patients  
**Baseline Cohort Size:** $N = 133$ genuine individual patients (after removing the `WhiteSutton_Total` aggregate artifact)  
**Ontology Version:** Human Phenotype Ontology (`hp.obo` release `2026-06-23`)  

---

## 1. Executive Expansion Summary

| Metric | Baseline Dataset | Expanded Dataset | Net Change |
| :--- | :---: | :---: | :---: |
| **Total Genuine Patients** | **133** | **385** | **+252 (+189.5%)** |
| — White-Sutton Syndrome | 22 | 45 | +23 (+104.5%) |
| — Xia-Gibbs Syndrome | 20 | 42 | +22 (+110.0%) |
| — KBG Syndrome | 91 | 298 | +207 (+227.5%) |
| **Unique Phenotypic Profiles** | 131 | 370 | +239 |
| **Total Unique HPO Terms** | 78 | 82 | +4 terms |
| **Training HPO Vocabulary** | 76 | 78 | +2 features |
| **Total ML Features (HPO + Sex)**| 79 | 81 | +2 features |
| **Held-Out Test Sample Size** | 28 | 78 | +50 patients (+178.6%) |
| **Test Accuracy (95% CI)** | 0.9286 (0.833 - 1.000) | **0.9872 (0.962 - 1.000)** | Higher statistical power |
| **5-Fold CV Accuracy (Mean ± SD)**| 1.0000 ± 0.0000 | **0.9714 ± 0.0223** | Realistic clinical heterogeneity |

---

## 2. Provenance and Literature Sources

Every patient record in the expanded dataset was curated from peer-reviewed medical genetics literature:

### White-Sutton Syndrome ($N = 45$)
1. **Assia Batzir et al. (2020)** [*Am J Med Genet A*, PMC7713511, DOI: 10.1002/ajmg.a.61380]: $n = 22$ individual cases.
2. **Nagy / Tan et al. (2022)** [*Genes (Basel)*, PMC8775410, DOI: 10.3390/genes13010154]: $n = 13$ individual cases.
3. **White et al. (2016)** [*Genome Med*, PMC4702300, DOI: 10.1186/s13073-015-0253-0]: $n = 5$ individual cases.
4. **Ye et al. (2015)** [*Cold Spring Harb Mol Case Stud*, PMC4850885, DOI: 10.1101/mcs.a000455]: $n = 5$ individual cases.

### Xia-Gibbs Syndrome ($N = 42$)
1. **Jiang et al. (2018)** [*Am J Med Genet A*, PMC6231716, DOI: 10.1002/ajmg.a.38699]: $n = 20$ individual cases.
2. **Khayat et al. (2021)** [*HGG Adv*, PMC8694554, DOI: 10.1016/j.xhgg.2021.100049]: $n = 8$ individual cases.
3. **Yang et al. (2015)** [*Cold Spring Harb Mol Case Stud*, PMC4850891, DOI: 10.1101/mcs.a000562]: $n = 7$ individual cases.
4. **Romano et al. (2022)** [*Birth Defects Res*, PMC9545659, DOI: 10.1002/bdr2.2058]: $n = 5$ individual cases.
5. **Cheng et al. (2019)** [*Mol Genet Genomic Med*, PMC6465669, DOI: 10.1002/mgg3.596]: $n = 2$ individual cases.

### KBG Syndrome ($N = 298$)
1. **Martinez-Cayuelas et al. (2023)** [*J Med Genet*, PMID: 36446582]: $n = 67$ newly recruited cases.
2. **Gao et al. (2022)** [*J Pers Med*, PMC8948816]: $n = 13$ cases.
3. **Low et al. (2016)** [*Am J Med Genet A*, PMC5435101]: $n = 11$ cases.
4. **Goldenberg et al. (2016)** [*Genet Med*, PMID: 27783388]: $n = 38$ cases.
5. **Gnazzo et al. (2020)** [*Am J Med Genet A*, PMID: 32767702]: $n = 31$ cases.
6. **Parenti et al. (2021)** [PMID: 33804868]: $n = 23$ cases.
7. **Kutkowska-Kaźmierczak et al. (2021)** [PMID: 33671236]: $n = 22$ cases.
8. **Scarano et al. (2013)** [PMID: 23696434]: $n = 12$ cases.
9. **Novara et al. (2017)** [PMID: 28886342]: $n = 11$ cases.
10. **Sirmaci et al. (2011)** [PMID: 21820096]: $n = 7$ cases.
11. **Van Dongen et al. (2019)** [PMID: 30612683]: $n = 7$ cases.
12. **Other published case reports/series**: $n = 56$ independent cases across 18 publications.

---

## 3. Duplicate Prevention & Quarantined Cohorts ($n = 59$)

To avoid double-counting patients appearing across multiple reviews or multicenter cohorts:
* **27 cases** from Low et al. (2016 literature review) were quarantined because they potentially overlapped with the baseline Low et al. PMC5435101 cohort.
* **20 cases** from Ockeloen et al. (2015) and **6 cases** from Walz et al. (2015) were quarantined because their clinical and genetic data were already aggregated within the Low 2016 multicenter study.
* **6 variant review rows** with incomplete individual phenotype listings were excluded.
* Full exclusion logs are recorded in `data/excluded_duplicate_patients_log.csv`.

---

## 4. Machine Learning Splits & Validation Results

* **Split Protocol:** Grouped-by-profile Stratified Splitting (60% Train: $N=230$, 20% Val: $N=77$, 20% Test: $N=78$).
* **Leakage Control:** HPO feature vocabulary (78 terms) fitted **exclusively** on the training split.
* **Model:** Calibrated Random Forest (100 estimators, max depth 10, balanced class weights, Platt scaling calibration with 5-fold internal CV).

### Held-Out Test Evaluation ($N = 78$ patients):
* **Accuracy:** **0.9872 (98.72%)** [95% CI: 0.9622 to 1.0000]
* **Macro Precision:** **0.9945**
* **Macro Recall (Sensitivity):** **0.9630**
* **Macro Specificity:** **0.9815**
* **Macro F1 Score:** **0.9776**
* **Macro AUROC:** **1.0000**
* **Macro AUPRC:** **1.0000**

### Confusion Matrix on Held-Out Test Split:
```text
                 Predicted WS  Predicted XG  Predicted KBG
Actual WS        8             0             1
Actual XG        0             9             0
Actual KBG       0             0             60
```
* Single misclassification: 1 White-Sutton patient presented with atypical overlapping features and was assigned to KBG.

### 5-Fold Stratified Cross-Validation:
* **Accuracy:** **97.14% ± 2.23%**
* **Macro F1:** **94.89% ± 4.04%**

---

## 5. Artifact Directory Inventory

1. `data/original_133_patient_dataset_backup.csv`: Clean baseline dataset.
2. `data/expanded_real_patient_hpo_dataset.csv`: Final 385-patient unified dataset.
3. `data/newly_added_patients_only.csv`: 252 newly extracted patient records.
4. `data/excluded_duplicate_patients_log.csv`: 59 quarantined duplicate cases.
5. `reports/expanded_cohort_provenance_manifest.csv`: Detailed patient-by-patient provenance log.
6. `reports/expansion_scientific_audit_results.json`: Complete machine-readable benchmarking metrics.
7. `models/rf_model_expanded_385.joblib`: Serialized trained model and calibration wrapper.
