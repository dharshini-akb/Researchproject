# Dataset Comparison Report: Baseline (133 Patients) vs. Expanded (385 Patients)

## 1. Overview
This report documents the rigorous comparison between the clean baseline cohort (133 individual patients after excluding the `WhiteSutton_Total` summary artifact) and the expanded cohort (385 individual patients).

## 2. Cohort Characteristics Comparison

| Feature | Baseline 133-Patient Cohort | Expanded 385-Patient Cohort | Absolute Change | Relative Change |
| :--- | :---: | :---: | :---: | :---: |
| **Total Individual Patients** | **133** | **385** | **+252** | **+189.5%** |
| — White-Sutton Syndrome | 22 | 45 | +23 | +104.5% |
| — Xia-Gibbs Syndrome | 20 | 42 | +22 | +110.0% |
| — KBG Syndrome | 91 | 298 | +207 | +227.5% |
| **Source Publications** | 5 | 27 | +22 | +440.0% |
| **Total Unique HPO Terms** | 78 | 82 | +4 | +5.1% |
| **Training HPO Feature Vocabulary** | 76 | 78 | +2 | +2.6% |
| **Total Input Dimension (HPO + Sex)** | 79 | 81 | +2 | +2.5% |
| **Unique Phenotype Profiles** | 131 | 370 | +239 | +182.4% |
| **Held-Out Test Sample Size** | 28 | 78 | +50 | +178.6% |

## 3. Machine Learning Performance Comparison

| Metric | Baseline Model (N=133) | Expanded Model (N=385) | Impact & Scientific Significance |
| :--- | :---: | :---: | :--- |
| **Held-Out Test Accuracy** | 0.9286 (92.86%) | **0.9872 (98.72%)** | $+5.86\%$ improvement; significantly larger statistical test cohort |
| **Accuracy 95% CI** | 0.8332 to 1.0000 | **0.9622 to 1.0000** | **Confidence interval width narrowed from 16.7% to 3.8%** |
| **Macro Precision** | 0.9667 | **0.9945** | Substantially reduced false positive rates |
| **Macro Recall (Sensitivity)** | 0.8667 | **0.9630** | $+9.63\%$ increase in diagnostic sensitivity |
| **Macro Specificity** | 0.9333 | **0.9815** | Superior non-target disease rejection |
| **Macro F1 Score** | 0.8991 | **0.9776** | $+7.85\%$ boost in balanced harmonic performance |
| **Macro AUROC** | 1.0000 | **1.0000** | Perfect class discriminability across thresholds |
| **Macro AUPRC** | 1.0000 | **1.0000** | Perfect precision-recall area |
| **5-Fold Cross-Validation Accuracy**| 100.0% ± 0.0% | **97.14% ± 2.23%** | **Realistic clinical variance**; eliminates trivial over-optimism |
| **5-Fold Cross-Validation F1** | 100.0% ± 0.0% | **94.89% ± 4.04%** | Generalizes robustly across heterogeneous sub-cohorts |

## 4. Key Scientific Insights

1. **Increased Phenotypic Diversity:** The expanded dataset introduces real-world clinical variance across 27 multicenter studies, capturing broader phenotypic spectra (e.g. variable seizure onset, mild dysmorphisms, and atypical language presentations).
2. **Elimination of Artificial 100% Cross-Validation:** While the 133-patient model achieved 100% cross-validation accuracy due to compact cluster boundaries, the expanded 385-patient cohort yields a more realistic and defensible cross-validation accuracy of 97.14% ± 2.23%, demonstrating true robustness.
3. **Statistical Power in Evaluation:** The held-out test cohort grew from 28 to 78 patients, tightening the 95% confidence interval bound to [96.22%, 100.00%].
