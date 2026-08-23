# Final Real-Patient Model Validation Report

This report presents the validation results of the Random Forest model trained on the expanded, fully verified real patient dataset (134 records).

## Dataset Provenance

- **Original Patients**: 67 (White-Sutton: 23, Xia-Gibbs: 20, KBG: 24)
- **New Verified Patients**: 67 (All KBG newly recruited cases from PMID 36446582)
- **Excluded Duplicates**: 0
- **Unresolved/Previously Published Candidates**: 266 (Excluded and saved for review)
- **Final Verified Dataset Size**: 134 real patient profiles

## Patient Split Distribution

- **Training Split**: 79 patients
- **Validation Split**: 27 patients
- **Test Split**: 28 patients

*Note: Splitting was stratified and grouped by unique HPO-Sex profiles to prevent any cross-split profile leakage.*

## Leakage Audit & Preprocessing
- HPO Feature vocabulary was generated on the **Training Set ONLY** (vocabulary size: 76 terms).
- Preprocessing and scaling thresholds were computed dynamically on the training partitions only.
- Validation and Test sets contained HPO terms not included in the feature vocabulary, which were correctly ignored during vectorization to simulate real-world clinical deployment.

## Test Performance Metrics (New 134-Patient Model)

- **Accuracy**: 0.9286 (95% CI: 0.8332 to 1.0240)
- **Macro Precision**: 0.9667
- **Macro Recall / Sensitivity**: 0.8667
- **Macro Specificity**: 0.9333
- **Macro F1 Score**: 0.8991
- **Macro AUROC**: 1.0000
- **Macro AUPRC**: 1.0000

### Confusion Matrix
```
[[3, 0, 2], [0, 5, 0], [0, 0, 18]]
```

### Per-Class Performance
| Class / Disease | Specificity | AUROC | AUPRC | Support |
| --- | --- | --- | --- | --- |
| 0 (White-Sutton) | 1.0000 | 1.0000 | 1.0000 | 5 |
| 1 (Xia-Gibbs) | 1.0000 | 1.0000 | 1.0000 | 5 |
| 2 (KBG Syndrome) | 0.8000 | 1.0000 | 1.0000 | 18 |

## 5-Fold Cross-Validation Metrics
- **Fold 1**: 1.0000
- **Fold 2**: 1.0000
- **Fold 3**: 1.0000
- **Fold 4**: 1.0000
- **Fold 5**: 1.0000
- **Mean CV Accuracy**: 1.0000 ± 0.0000

## Comparison: Old 67-Patient Model vs. New 134-Patient Model

| Metric | Old 67-patient model | New 134-patient model |
| --- | --- | --- |
| **Accuracy** | 1.0000 | 0.9286 |
| **Macro Precision** | 1.0000 | 0.9667 |
| **Macro Recall** | 1.0000 | 0.8667 |
| **Macro Specificity** | 1.0000 | 0.9333 |
| **Macro F1 Score** | 1.0000 | 0.8991 |
| **Macro AUROC** | 1.0000 | 1.0000 |
| **Macro AUPRC** | 1.0000 | 1.0000 |

## Scientific Interpretation & Limitations

1. **Impact of Cohort Expansion**:
   - The accuracy changed from 1.0000 to 0.9286. This variation occurs because the model trained on the original 67-patient set was prone to overestimating generalization metrics due to the extremely small sample size and lack of phenotypic diversity.
   - The new 134-patient model incorporates 67 new independent patient profiles, introducing realistic clinical variability and heterogeneity which results in more robust, honest performance metrics.

2. **Limitations & External Validation**:
   - Although the model achieves high metrics, **this does not prove clinical perfection** nor does it mean it is **clinically validated**.
   - The final cohort of 134 patients is still small and represents a retrospective clinical dataset. 
   - A true clinical validation would require prospective testing in an independent, external healthcare system.

## Data Leakage Audit
- No overlap of patient IDs across splits.
- No identical phenotype-sex profiles allowed to cross splits.
- Out-of-vocabulary HPO terms are safely ignored during feature vectorization in validation/testing/CV folds.
