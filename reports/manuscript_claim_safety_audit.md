# RareDXAI: Manuscript Claim Safety Audit & Phrasing Guide

**Project:** *RareDXAI: A Human Phenotype Ontology-Based Framework for Rare Disease Prediction*  
**Date:** September 4, 2026  

---

## Claim Safety & Scientific Phrasing Audit

To ensure the manuscript adheres to high scientific standards, potential overclaims in prior project notes have been audited and replaced with defensible phrasing:

| # | Topic / Area | Potentially Excessive / Unsubstantiated Claim | Recommended Scientifically Defensible Phrasing |
| :-: | :--- | :--- | :--- |
| **1** | **Diagnostic Scope** | *"Provides a definitive automated diagnostic system for rare diseases."* | *"Provides a phenotype-driven computational decision-support framework to assist clinical prioritization among syndromic neurodevelopmental disorders."* |
| **2** | **Clinical Validation** | *"Clinically validated and ready for real-world EHR deployment."* | *"Evaluated on an audited multicenter retrospective cohort of 385 genetically confirmed patients across 48 peer-reviewed publications."* |
| **3** | **Accuracy Claims** | *"Achieves 100% diagnostic accuracy in clinical practice."* | *"Achieved 98.72% accuracy (77/78 correct, Wilson 95% CI: 93.09%–99.77%) on a locked held-out test cohort, and 97.14% ± 2.23% in 5-fold cross-validation."* |
| **4** | **Data Leakage** | *"Zero data leakage across the entire project pipeline."* | *"Leakage-control procedures were implemented via patient-level separation, grouping of identical phenotypic profiles, and training-only feature vocabulary construction."* |
| **5** | **Explainability & SHAP**| *"Identified features that cause each rare disease."* | *"Identified standardized Human Phenotype Ontology (HPO) terms strongly associated with model decision boundaries."* |
| **6** | **Calibration** | *"Produces exact clinical diagnostic risk percentages."* | *"Produces calibrated multiclass probability distributions (Brier score = 0.0419) to convey relative model confidence."* |
| **7** | **OCR Pipeline** | *"Automated end-to-end OCR directly diagnoses patients from uncurated scans."* | *"Exploratory OCR ingestion was implemented as an upstream utility to extract clinical concepts, subject to subsequent standardized ontology verification."* |
| **8** | **Disease Generalization**| *"Generalizes to all 7,000+ known rare diseases."* | *"Demonstrates proof-of-concept utility on three clinically overlapping syndromic neurodevelopmental conditions: KBG, White-Sutton, and Xia-Gibbs syndromes."* |
| **9** | **Cross-Center Transfer**| *"Proven to generalize perfectly across independent hospitals without performance drop."* | *"Evaluated under source-grouped cross-validation, revealing how inter-publication annotation differences impact generalization performance (79.62% ± 27.05%)."* |
| **10**| **Novelty** | *"The first and only AI system capable of diagnosing rare genetic syndromes."* | *"A Human Phenotype Ontology-based framework integrating standardized phenotype vectorization, probability calibration, and local feature attribution for rare disease classification."* |
