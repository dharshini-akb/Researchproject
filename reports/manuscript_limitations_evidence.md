# RareDXAI: Evidence-Based Manuscript Limitations

**Project:** *RareDXAI: A Human Phenotype Ontology-Based Framework for Rare Disease Prediction*  
**Date:** September 4, 2026  

---

## 10 Evidence-Based Scientific Limitations

Every limitation documented below is supported by direct empirical findings from the RareDXAI repository:

### 1. Moderate Sample Size Inherent to Ultra-Rare Disorders ($N = 385$)
- **Empirical Evidence:** While $N=385$ represents one of the largest assembled machine learning cohorts for these specific conditions, rare disease sample sizes remain small relative to common disease benchmarks.
- **Manuscript Implication:** Statistical estimates, particularly per-class recall for White-Sutton ($n=9$ in test set) and Xia-Gibbs ($n=9$ in test set), carry wider confidence bounds than KBG syndrome ($n=60$).

### 2. Natural Class Imbalance Reflecting Published Literature Volume
- **Empirical Evidence:** KBG syndrome comprises $77.40\%$ ($298/385$) of the cohort, while White-Sutton ($11.69\%$) and Xia-Gibbs ($10.91\%$) have smaller representations.
- **Manuscript Implication:** Class imbalance was managed via balanced class weighting in Random Forest bootstrapping and macro-averaged metrics, but reflects underlying publication frequency rather than true epidemiological prevalence.

### 3. Source-Grouped Performance Attenuation Under Leave-One-Study-Out Stress Testing
- **Empirical Evidence:** GroupKFold cross-validation by source publication yielded an accuracy of **$79.62\% \pm 27.05\%$** (Macro F1 = $59.51\% \pm 26.81\%$), compared to $97.14\% \pm 2.23\%$ under profile-grouped CV.
- **Manuscript Implication:** Demonstrates that individual medical genetics papers often emphasize specific sub-phenotypes or distinct clinical signs. When an entire publication is withheld, performance drops on studies that introduced isolated terms.

### 4. Retrospective Literature-Derived Cohort Selection Bias
- **Empirical Evidence:** All 385 patients trace to published case reports and multicenter genetics studies.
- **Manuscript Implication:** Published literature tends to report more severe, classical, or syndromic phenotypes. Mild or atypical presentations seen in primary care may be underrepresented.

### 5. Absence of Prospective External Electronic Health Record (EHR) Validation
- **Empirical Evidence:** Validation was performed on locked held-out test splits ($N=78$) and internal 5-fold cross-validation.
- **Manuscript Implication:** The framework is not yet validated in prospective real-world clinical workflows or uncurated EHR hospital databases.

### 6. Inter-Publication Phenotype Documentation Heterogeneity
- **Empirical Evidence:** Unmentioned phenotypes are encoded as $0$ (absence/not reported) in binary feature vectorization.
- **Manuscript Implication:** Distinguishing true biological absence of a clinical sign from clinical under-reporting in a publication remains a challenge in retrospective phenotyping.

### 7. Fixed Training HPO Feature Vocabulary and Out-of-Vocabulary (OOV) Terms
- **Empirical Evidence:** 78 HPO terms were fitted on the training split, resulting in 4 OOV terms in the test set (`HP:0002121`, `HP:0001156`, `HP:0001508`, `HP:0002126`) that were masked out during vectorization.
- **Manuscript Implication:** Rare, isolated terms unobserved during training cannot contribute to inference without ontology expansion or semantic similarity embeddings.

### 8. Exploratory Status of Upstream OCR Document Ingestion
- **Empirical Evidence:** EasyOCR achieved a Word Error Rate (WER) of **$92.00\%$** and Character Error Rate (CER) of **$11.42\%$** on noisy clinical scans, causing a $20\%$ concept mapping omission rate ($2/10$ test phrases unmapped).
- **Manuscript Implication:** OCR is an auxiliary ingestion utility and requires human-in-the-loop review or fuzzy concept dictionary matching before downstream classification.

### 9. Closed-Set Multi-Class Prediction Scope (3 Syndromes)
- **Empirical Evidence:** The model classifies between KBG, White-Sutton, and Xia-Gibbs syndromes.
- **Manuscript Implication:** In an unconstrained clinical setting with thousands of potential rare diseases, the system functions as a focused differential decision aid among overlapping syndromic mimics rather than an open-ended general diagnostic tool.

### 10. Generalization Estimates Dependent on Patient-Level Profile Partitioning
- **Empirical Evidence:** Grouping identical HPO profiles prevents cross-split profile leakage, yielding a robust test accuracy of $98.72\%$ and 5-fold CV accuracy of $97.14\%$.
- **Manuscript Implication:** Generalization to entirely novel clinical centers with divergent phenotyping vocabularies requires continuous ontological mapping updates.
