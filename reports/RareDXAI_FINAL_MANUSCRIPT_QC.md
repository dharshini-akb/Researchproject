# RareDXAI: Final Scientific Quality Control & Verification Audit Report

**Project:** *RareDXAI: A Human Phenotype Ontology-Based Framework for Rare Disease Prediction*  
**Date:** September 6, 2026  
**Audited Status:** 100% VERIFIED & COMPLIANT  

---

## 1. Quality Control Verification Checklist

| # | Verification Item | Authoritative Repository Standard | Verified Manuscript Implementation | Status |
| :-: | :--- | :--- | :--- | :---: |
| **1** | **Exact Required Section Order** | Abstract $\rightarrow$ Intro $\rightarrow$ Lit Survey $\rightarrow$ Math $\rightarrow$ Methods $\rightarrow$ Results $\rightarrow$ Conclusion $\rightarrow$ References | Followed strictly; limitations integrated naturally inside Section 6.8 | **PASSED** |
| **2** | **Total Patient Cohort** | $N = 385$ verified patients with molecular variant confirmation | Exactly $N = 385$ (KBG: $298$, WS: $45$, XG: $42$) | **PASSED** |
| **3** | **Syndrome Proportions** | KBG: 77.40%, White-Sutton: 11.69%, Xia-Gibbs: 10.91% | Verified in Table 3, Figure 4, and text | **PASSED** |
| **4** | **Cohort Demographics (Sex)** | Male: 203 (52.7%), Female: 165 (42.9%), Unknown: 17 (4.4%) | Verified in Table 3 and demographic analysis | **PASSED** |
| **5** | **Included Publications** | Exactly 48 peer-reviewed publications | Verified in Table 2, Figure 3, and text | **PASSED** |
| **6** | **Evaluated Literature Sources** | Exactly 52 literature sources evaluated during curation | Verified in Table 2, Figure 3, and text | **PASSED** |
| **7** | **Quarantined Candidate Records** | 4 sources (59 candidate records) quarantined under protocol | Breakdown: Low 2016 (32), Ockeloen (20), Walz (6), Low 2017 (1) | **PASSED** |
| **8** | **HPO Feature Space** | 82 cohort HPO terms, 78 training terms, 3 sex features = 81 ML dims | Verified in Methods and model matrices | **PASSED** |
| **9** | **Data Partitioning (60/20/20)** | Profile-grouped split: Train $N=230$, Val $N=77$, Held-out Test $N=78$ | Verified in Methods, Table 4, and results | **PASSED** |
| **10**| **Out-of-Vocabulary (OOV) Terms**| 4 test OOV terms masked during transformation, 0 val OOV terms | Documented with exact HPO IDs (`HP:0002121`, etc.) | **PASSED** |
| **11**| **Held-Out Test Accuracy** | 98.72% (77/78 correct, Wilson 95% CI: 93.09%–99.77%) | Verified in Table 4, Table 5, Figure 6 | **PASSED** |
| **12**| **Held-Out Test Metrics** | Balanced Acc: 96.30%, Precision: 99.45%, Recall: 96.30%, F1: 97.76% | Verified in Table 4, Table 5, Figure 6 | **PASSED** |
| **13**| **Per-Class Metrics** | WS F1: 0.9412 (8/9), XG F1: 1.0000 (9/9), KBG F1: 0.9917 (60/60) | Verified in Table 5 and confusion matrix (Figure 5) | **PASSED** |
| **14**| **Misclassified Case Analysis** | `WhiteSutton_PT19` (KBG: 47.04%, WS: 46.51%, XG: 6.45%) | Framed as probability uncertainty in atypical case | **PASSED** |
| **15**| **Probability Calibration** | Multiclass Brier: 0.0419, Mean OvR Brier: 0.0140, ECE: 8.59% | Verified in Table 4, Table 5, Figure 9 | **PASSED** |
| **16**| **Threshold Discrimination** | Macro AUROC = 1.0000, Macro AUPRC = 1.0000 | Verified in Table 4, Table 5, Figure 10 | **PASSED** |
| **17**| **Profile-Grouped 5-Fold CV** | Accuracy: 97.14% ± 2.23%, Macro F1: 94.89% ± 4.04% | Verified in Results, Figure 7 | **PASSED** |
| **18**| **Source-Grouped Stress Validation**| Accuracy: 79.62% ± 27.05%, Macro F1: 59.51% ± 26.81% | Documented transparently in Results, Figure 7 | **PASSED** |
| **19**| **Model Selection Rationale** | Selected for probability calibration (Brier 0.0419) and TreeSHAP | Not claimed as highest nominal accuracy | **PASSED** |
| **20**| **SHAP Terminology Safety** | "Features strongly associated with model decision boundaries" | Non-causal framing strictly enforced | **PASSED** |
| **21**| **Exploratory OCR Evaluation** | CER: 11.42%, WER: 92.00%, Clean: 100%, Noisy: 80% | Explicitly labeled as exploratory upstream utility | **PASSED** |
| **22**| **Closed-Set Scope Clarification** | Differentiates among 3 syndromes; not a general rare disease tool | Clearly stated in Intro, Methods, Results, Limitations | **PASSED** |
| **23**| **Leakage Language Safety** | "To reduce the risk of phenotype-profile leakage..." | Zero instances of "zero leakage" or "leakage-free" | **PASSED** |
| **24**| **Literature Curation Phrasing** | "Structured curation of literature" (52 sources evaluated) | Zero instances of "PRISMA" or "systematic review" | **PASSED** |
| **25**| **Terminology Accuracy** | "Classification Performance" used throughout (no "Diagnostic Accuracy") | Verified in Section 6 and Table 5 | **PASSED** |
| **26**| **Literature Survey Grouping** | 3 clear groups: Ontology, Mined Datasets (Phenopacket Store), AI matching | Phenopacket Store highlighted as closest precedent | **PASSED** |
| **27**| **Bibliographic Verification** | 15 peer-reviewed studies (2020–2026) verified with DOIs | Exact authors, titles, and venues verified | **PASSED** |
| **28**| **Table Numbering Consistency** | Tables 1–6 correctly numbered and cited in text | Table captions above tables | **PASSED** |
| **29**| **Figure Numbering Consistency** | Figures 1–10 correctly numbered and cited in text | Figure captions below figures | **PASSED** |
| **30**| **Visual Quality Standards** | 300 DPI high-resolution figures, readable fonts, no clipping | All 10 figures embedded from repository data | **PASSED** |
| **31**| **Syndrome Visual Safety** | Representative illustrative panel with disclaimer caption | Open-access medical illustration format | **PASSED** |
| **32**| **Editable Word Document** | `RareDXAI_Research_Manuscript_FINAL.docx` fully editable | Generated with python-docx, styled headings/tables | **PASSED** |
| **33**| **Publication PDF Preview** | `RareDXAI_Research_Manuscript_FINAL.pdf` generated | Two-pass dynamic page numbering and running headers | **PASSED** |

---

## 2. Deliverables Summary

- **Editable Microsoft Word Document**: [`reports/RareDXAI_Research_Manuscript_FINAL.docx`](file:///d:/finalresearchproject/reports/RareDXAI_Research_Manuscript_FINAL.docx)
- **Complete Markdown Document**: [`reports/RareDXAI_Research_Manuscript_FINAL.md`](file:///d:/finalresearchproject/reports/RareDXAI_Research_Manuscript_FINAL.md)
- **Publication PDF Document**: [`reports/RareDXAI_Research_Manuscript_FINAL.pdf`](file:///d:/finalresearchproject/reports/RareDXAI_Research_Manuscript_FINAL.pdf)
- **Quality Control Audit Report**: [`reports/RareDXAI_FINAL_MANUSCRIPT_QC.md`](file:///d:/finalresearchproject/reports/RareDXAI_FINAL_MANUSCRIPT_QC.md)
