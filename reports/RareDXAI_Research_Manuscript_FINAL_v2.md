# RareDXAI: A Human Phenotype Ontology-Based Framework for Rare Disease Prediction

**Dharshini K. et al.**  
*Computational Genomics & Clinical AI Research Group*  
**Official Research Manuscript • Locked & Audited Evidence Package ($N = 385$)**

---

## 1. Abstract

**Background:** Rare genetic diseases affect more than 300 million people worldwide. Diagnosing these conditions is challenging because many distinct genetic disorders present with overlapping clinical features, such as developmental delays, speech impairments, and intellectual disability. In pediatric genetics, syndromic neurodevelopmental conditions like KBG syndrome, White-Sutton syndrome, and Xia-Gibbs syndrome share non-specific clinical signs that frequently lead to prolonged diagnostic delays lasting five to seven years.

**Methods:** We developed **RareDXAI**, a computational decision-support framework that uses standardized Human Phenotype Ontology (HPO) terms to perform phenotype-based classification among three predefined rare syndromes. We curated an audited, literature-derived cohort of 385 patients with confirmed pathogenic variants across 48 peer-reviewed publications (from 52 candidate literature sources evaluated during curation, with four secondary, overlapping, or re-reported sources containing 59 candidate records quarantined under a predefined exclusion protocol). Clinical features were encoded into 78 binary HPO terms and 3 one-hot sex indicators (81 total predictor dimensions). To reduce the risk of phenotype-profile leakage, identical phenotypic profiles were grouped before applying a 60/20/20 train/validation/test split ($N=230$ training, $N=77$ validation, $N=78$ held-out test), and feature vocabularies were constructed strictly from training data. We trained a Random Forest model with Platt probability scaling (5-fold internal cross-calibration) and explained predictions using TreeSHAP.

**Results:** On the held-out test set ($N=78$), RareDXAI correctly classified 77 out of 78 patients, corresponding to a held-out classification accuracy of **98.72%** (Wilson 95% CI: 93.09%–99.77%), balanced accuracy of **96.30%**, macro precision of **99.45%**, macro recall of **96.30%**, macro specificity of **98.15%**, and macro F1-score of **97.76%**. Multi-class threshold-agnostic evaluation on this held-out test set yielded a macro AUROC of **1.0000** and macro AUPRC of **1.0000**, with a multiclass Brier score of **0.0419** and Expected Calibration Error (ECE) of **8.59%**. Five-fold stratified grouped cross-validation demonstrated high consistency ($97.14\% \\pm 2.23\%$ accuracy; macro F1: $94.89\% \\pm 4.04\%$). In contrast, source-publication-grouped stress validation (GroupKFold by source publication) showed lower performance ($79.62\% \\pm 27.05\%$ accuracy; macro F1: $59.51\% \\pm 26.81\%$), indicating that publication-specific phenotype reporting patterns affect model transferability. TreeSHAP analysis identified standardized HPO features strongly associated with model decision boundaries, such as macrodontia (`HP:0001572`) for KBG syndrome, autism spectrum traits (`HP:0000717`) for White-Sutton syndrome, and thin upper lip vermilion (`HP:0000219`) for Xia-Gibbs syndrome. Exploratory upstream optical character recognition (OCR) on digitized notes achieved a Character Error Rate of 11.42% and Word Error Rate of 92.00%.

**Conclusions:** RareDXAI provides an interpretable phenotype-based classification framework and a reproducible baseline for rare disease decision support. While held-out test classification performance is high under profile-grouped evaluation, the substantial performance drop in source-publication-grouped stress testing highlights that independent external and prospective clinical validation remain necessary before deployment.

**Keywords:** Rare Diseases, Human Phenotype Ontology, Machine Learning, Random Forest, Model Interpretability, SHAP, Clinical Decision Support, Neurodevelopmental Disorders.

---

## 2. Introduction

Rare diseases are medical conditions that affect a small fraction of the population, typically defined as fewer than 1 in 2,000 individuals in Europe or fewer than 200,000 individuals in the United States. Although each individual disorder is rare, there are over 7,000 recognized rare genetic conditions, which together affect an estimated 300 to 400 million people globally.

Most rare diseases have an underlying genetic cause and manifest during infancy or early childhood. Despite advances in high-throughput DNA sequencing—including whole-exome sequencing (WES) and whole-genome sequencing (WGS)—affected patients and their families frequently experience a prolonged and stressful diagnostic odyssey. On average, obtaining a correct diagnosis requires five to seven years, multiple specialist visits, and several initial misdiagnoses.

A principal contributor to this diagnostic delay is clinical phenotypic overlap. Many genetic conditions share broad, non-specific neurodevelopmental symptoms, such as intellectual disability, motor milestone delays, speech impairments, and behavioral challenges. This diagnostic challenge is particularly pronounced among three syndromic neurodevelopmental conditions:

1. **KBG Syndrome (MIM #148050):** Caused by heterozygous loss-of-function mutations or microdeletions in the *ANKRD11* gene on chromosome 16q24.3 (Martinez-Cayuelas et al., 2023). Characteristic clinical findings include unusually large upper front teeth (macrodontia of the central incisors), a triangular facial appearance, prominent eyebrows, short stature, skeletal hand differences (such as brachydactyly or short fifth fingers), and mild-to-moderate intellectual disability.
2. **White-Sutton Syndrome (MIM #616364):** Caused by heterozygous *de novo* mutations in the *POGZ* gene on chromosome 1q21.3 (Assia Batzir et al., 2020). Common clinical features include developmental delay, intellectual disability, speech impairment, autism spectrum disorder traits, small head size (microcephaly), and distinctive facial features.
3. **Xia-Gibbs Syndrome (MIM #615829):** Caused by heterozygous *de novo* truncating mutations in the *AHDC1* gene on chromosome 1p36.11 (Khayat et al., 2021). Hallmark signs include severe infantile hypotonia (low muscle tone), global developmental delay, expressive speech absence or delay, a broad forehead, downward-slanting palpebral fissures, a thin upper lip vermilion, structural brain anomalies, and sleep disturbances such as obstructive sleep apnea.

Because these three syndromes share non-specific neurodevelopmental manifestations, differentiating among them based purely on routine initial clinical evaluation is difficult. The current model is a closed-set three-class classification system focusing on these three conditions and should not be interpreted as a general-purpose rare disease diagnostic model.

To standardize clinical descriptions and make them computable, the biomedical community established the **Human Phenotype Ontology (HPO)** (Köhler et al., 2021; Gargano et al., 2024). The HPO provides a controlled vocabulary of standardized medical terms organized in a directed acyclic graph. For example, instead of recording free-text phrases like "large central teeth," clinicians and computational pipelines use the standardized concept `HP:0001572` (Macrodontia of central incisors). This structured vocabulary allows machine-learning algorithms to analyze patient phenotypic profiles systematically.

However, applying machine learning to rare disease phenomics involves specific methodological considerations:
- Cohort sizes for ultra-rare disorders are inherently limited.
- Retrospective cohorts derived from published clinical literature may carry selection and reporting biases.
- If patients with identical phenotypic profiles are placed into both training and evaluation sets, evaluations can be corrupted by profile overlap.
- Complex machine-learning models require explainability mechanisms so that clinicians can examine which clinical features influence algorithmic predictions.

To address these challenges, we built **RareDXAI**, a phenotype-based computational framework designed to support candidate prioritization among syndromic mimics. RareDXAI uses an audited, literature-derived cohort of 385 molecularly confirmed patients from 48 peer-reviewed publications, applies profile-grouped data partitioning to reduce profile leakage, uses calibrated Random Forest classification to provide probability estimates, and uses SHAP (SHapley Additive exPlanations) to identify features strongly associated with model decision boundaries.

Figure 1 provides representative phenotypic illustrations of the three target conditions.

![Figure 1: Representative Clinical/Phenotypic Features](file:///d:/finalresearchproject/assets/figures/syndrome_phenotypes_illustration.jpg)

*Figure 1. Representative clinical and phenotypic features associated with KBG, White-Sutton, and Xia-Gibbs syndromes. The illustration is intended for visual context and does not represent all affected individuals.*

---

## 3. Literature Survey

Computational methods for rare disease analysis have advanced from manual expert tables to ontology-driven machine learning, natural language processing (NLP), and deep learning. Mining individual patient case reports from published literature and converting them into structured, computable datasets is a well-established practice in computational genetics.

We reviewed 15 peer-reviewed studies published between 2020 and 2026 that directly inform the design of RareDXAI. These studies fall into three main areas:

### 3.1 Ontology and Computable Phenotype Standards
Standardized ontologies provide the vocabulary for computational phenomics. **Köhler et al. (2021)** and **Gargano et al. (2024)** detailed the ongoing growth of the Human Phenotype Ontology (HPO) to over 16,000 terms, providing the canonical `hp.obo` vocabulary (Release `2026-06-23`) used in this work. **Jacobsen et al. (2022)** published the GA4GH Phenopacket schema in *Nature Biotechnology* (standardized as ISO 4454:2022), creating an international format for sharing computable patient-level phenotypic and genomic data.

### 3.2 Literature-Derived Patient Datasets and Phenotype Extraction
Extracting patient-level data from published literature to construct computable cohorts is a foundational methodology. **Ladewig et al. (2023)** introduced the **Phenopacket Store** in *Database*, curating thousands of computable case reports directly from published literature into structured Phenopackets. **The Phenopacket Store provides the closest methodological precedent to our study**, demonstrating that structured extraction of published case reports enables reproducible benchmarking. RareDXAI builds upon this precedent by focusing on a specific three-syndrome classification problem with binary feature encoding, probability calibration, and SHAP interpretability.

Complementing literature curation, **Birgmeier et al. (2020)** developed **AMELIE** in *Science Translational Medicine*, using NLP and machine learning to parse published literature for Mendelian diagnosis. **Feng et al. (2021)** created **PhenoTagger** in *Bioinformatics*, combining deep learning and dictionary indexing for automated HPO recognition. **Liu et al. (2020)** developed **Doc2HPO** in *BMC Bioinformatics* for interactive phenotype curation from clinical text. **Schuetz et al. (2023)** evaluated automated phenotype extraction from case reports in the *Journal of Biomedical Informatics*, demonstrating that OCR error propagation requires careful verification.

### 3.3 Phenotype-Based Machine Learning and Disease Prioritization
Computational tools use phenotype matching to prioritize candidate diseases and genes. **Robinson et al. (2020)** introduced **LIRICAL** in *The American Journal of Human Genetics*, using likelihood ratios across observed and excluded HPO terms to calculate diagnostic odds. **Zhao et al. (2020)** developed **Phen2Gene** in *Nucleic Acids Research* for phenotype-driven gene prioritization. **Hsieh et al. (2022)** presented **GestaltMatcher** in *Nature Genetics*, using deep convolutional neural networks to match facial dysmorphology from clinical photographs. **Rönicke et al. (2020)** reviewed rare disease clinical decision support systems in *Molecular and Cellular Pediatrics*, emphasizing the importance of probability calibration, leakage controls, and interpretability.

Finally, clinical cohort characterizations provided the primary data sources for our target conditions: **Martinez-Cayuelas et al. (2023)** for KBG syndrome (*ANKRD11*), **Assia Batzir et al. (2020)** for White-Sutton syndrome (*POGZ*), and **Khayat et al. (2021)** for Xia-Gibbs syndrome (*AHDC1*).

Table 1 summarizes the 15 reviewed studies, comparing their methodologies, data representations, and relevance to RareDXAI.

| Year | Authors | Title & Venue | Dataset / Source | Phenotype Format | Method | Main Contribution | Similarity / Difference to RareDXAI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2022** | Jacobsen et al. | GA4GH Phenopacket schema (*Nat Biotechnol*) | Global clinical repositories | Hierarchical HPO + GA4GH Schema | ISO Standard (ISO 4454:2022) | Standardized computable case report format | Conceptual basis for computable patient phenotyping |
| **2023** | Ladewig et al. | Phenopacket Store (*Database*) | Case reports from published literature | Curated patient-level HPO profiles | Curated case repository & validation tools | Mined thousands of literature cases into HPO Phenopackets | **Closest methodological precedent**; RareDXAI adds focused 3-class ML calibration & SHAP |
| **2024** | Gargano et al. | HPO in 2024 (*Nucleic Acids Res*) | HPO International Consortium | Controlled vocabulary (>16,000 terms) | Knowledge graph structures | Expanded definitions & disease annotations | Source of canonical terminology (Release `2026-06-23`) |
| **2021** | Köhler et al. | HPO in 2021 (*Nucleic Acids Res*) | Rare disease clinical databases | Directed acyclic graph of HPO | Semantic similarity algorithms | Foundation for standardized computational phenomics | Baseline ontology structure for feature mapping |
| **2020** | Robinson et al. | LIRICAL (*Am J Hum Genet*) | Real clinical cases & simulations | Observed & excluded HPO terms | Likelihood ratio & Bayesian inference | Interpretable diagnostic odds for genomic phenotypes | Supports interpretable decision support framework |
| **2020** | Birgmeier et al. | AMELIE (*Sci Transl Med*) | 138,000+ primary literature papers | HPO concept extraction | Supervised machine learning & NLP | Automated matching of patient HPO profiles to literature | Confirms viability of literature-derived patient matching |
| **2021** | Feng et al. | PhenoTagger (*Bioinformatics*) | PubMed Central text corpora | Standardized HPO concept tagging | Hybrid CNN + dictionary indexing | High-precision automated concept recognition | Informs text-to-HPO concept mapping strategies |
| **2020** | Liu et al. | Doc2HPO (*BMC Bioinformatics*) | Unstructured clinical notes | Interactive HPO term mapping | String parsing + NER | Web tool for clinical text phenotyping | Upstream precedent for clinical concept parsing |
| **2020** | Zhao et al. | Phen2Gene (*Nucleic Acids Res*) | OMIM, Orphanet, HPO annotations | Weighted HPO disease-gene profiles | Information theoretic gene scoring | Rapid phenotype-driven gene prioritization | Uses HPO term weighting akin to feature vectorization |
| **2022** | Hsieh et al. | GestaltMatcher (*Nat Genet*) | Patient clinical photographs | Deep facial dysmorphic embeddings | Deep Convolutional Neural Networks | Image-based rare disease phenotypic matching | Visual modality for syndromic recognition |
| **2020** | Rönicke et al. | AI in Rare Diseases (*Mol Cell Pediatr*) | Review of rare disease CDSS | Variable (HPO, ICD, UMLS) | Systematic comparative analysis | Highlighted risks of data leakage and uncalibrated models | Validates RareDXAI's focus on calibration and controls |
| **2023** | Martinez-Cayuelas et al. | KBG Syndrome Delineation (*Eur J Hum Genet*) | 67 molecularly confirmed KBG patients | Clinical phenotypic descriptions | Multicenter clinical cohort analysis | Delineated cardinal features (*ANKRD11* mutations) | Primary clinical cohort source for KBG syndrome |
| **2020** | Assia Batzir et al. | White-Sutton Delineation (*Am J Med Genet A*) | 22 patients with *POGZ* variants | Clinical phenotypic profiles | Detailed clinical characterization | Established cardinal spectrum of White-Sutton syndrome | Primary clinical cohort source for White-Sutton syndrome |
| **2021** | Khayat et al. | Xia-Gibbs Spectrum (*Am J Med Genet A*) | 8 patients with *AHDC1* variants | Systematic clinical feature tables | Clinical case series analysis | Expanded phenotypic spectrum of Xia-Gibbs syndrome | Clinical cohort contributor for Xia-Gibbs syndrome |
| **2023** | Schuetz et al. | Ontological Harmonization (*J Biomed Inform*) | Case reports & electronic health records | HPO term mapping | Automated NLP & fuzzy ontology matching | Evaluated OCR error propagation in clinical phenotyping | Contextualizes RareDXAI's OCR error evaluations |

*Table 1. Literature Comparison Matrix (15 Peer-Reviewed Studies, 2020–2026).*

---

## 4. Mathematical Expression

This section defines the mathematical expressions used in RareDXAI for patient representation, classification, calibration, evaluation metrics, and SHAP interpretability.

### 4.1 Patient Phenotype Vector
Each patient $i$ is represented as a feature vector $\mathbf{x}_i$ of length $d = 81$, which contains 78 binary clinical HPO features and 3 demographic sex indicators:

$$\mathbf{x}_i = [x_{i1}, x_{i2}, \dots, x_{id}] \in \{0, 1\}^d$$

### 4.2 Binary HPO Feature Encoding
For each clinical term $j$, a value of 1 is assigned if the clinical record documents that phenotype, and 0 if the feature is absent or unmentioned:

$$x_{ij} = \begin{cases} 1 & \text{if HPO term } j \text{ is documented for patient } i \\ 0 & \text{if absent or not reported} \end{cases}$$

### 4.3 Random Forest Probability Estimation
The ensemble consists of $T = 100$ decision trees $h_t(\mathbf{x})$. The estimated probability for class $c$ is the proportion of trees voting for that class:

$$\hat{P}_{\text{RF}}(y = c \mid \mathbf{x}) = \frac{1}{T} \sum_{t=1}^{T} \mathbb{I}(h_t(\mathbf{x}) = c)$$

where $\mathbb{I}(\cdot)$ is the indicator function.

### 4.4 Predicted Disease Class
The predicted class $\hat{y}$ is the syndrome receiving the highest estimated probability among the three target conditions (0: White-Sutton, 1: Xia-Gibbs, 2: KBG syndrome):

$$\hat{y} = \arg\max_{c \in \{0, 1, 2\}} \hat{P}(y = c \mid \mathbf{x})$$

### 4.5 Classification Accuracy
Accuracy measures the fraction of patients whose syndrome was correctly identified across the evaluation sample $N$:

$$\text{Accuracy} = \frac{\sum_{i=1}^{N} \mathbb{I}(\hat{y}_i = y_i)}{N}$$

### 4.6 Precision (Positive Predictive Value)
Precision measures the proportion of patients assigned to a syndrome who truly have that condition:

$$\text{Precision}_c = \frac{TP_c}{TP_c + FP_c}$$

where $TP_c$ is True Positives and $FP_c$ is False Positives for class $c$.

### 4.7 Recall (Sensitivity)
Recall measures the proportion of actual patients with a syndrome who were correctly identified by the model:

$$\text{Recall}_c = \frac{TP_c}{TP_c + FN_c}$$

where $FN_c$ is False Negatives for class $c$.

### 4.8 F1-Score
The F1-score is the harmonic mean of precision and recall, balancing sensitivity and positive predictive value:

$$\text{F1}_c = 2 \times \frac{\text{Precision}_c \times \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c}$$

### 4.9 Balanced Accuracy
Balanced accuracy is the unweighted arithmetic mean of recall across all $C = 3$ syndromes, ensuring that the majority class does not dominate evaluation:

$$\text{Balanced Accuracy} = \frac{1}{C} \sum_{c=1}^{C} \text{Recall}_c$$

### 4.10 SHAP Additive Feature Attribution
TreeSHAP decomposes the model prediction for class $c$ into a base expectation $\phi_{0,c}$ plus the additive sum of individual feature attributions $\phi_{j,c}$:

$$f_c(\mathbf{x}) = \phi_{0,c} + \sum_{j=1}^{d} \phi_{j,c}(\mathbf{x})$$

A positive $\phi_{j,c}$ increases the model's output probability for class $c$, while a negative value decreases it.

---

## 5. Model Methodologies

Figure 2 illustrates the overall system workflow of RareDXAI, from literature curation to calibrated prediction and SHAP interpretation.

![Figure 2: RareDXAI System Workflow](file:///d:/finalresearchproject/assets/figures/figure1_architecture.png)

*Figure 2. RareDXAI system workflow diagram. The pipeline processes published clinical case reports through standardized HPO concept mapping, executes profile-grouped stratified splitting to reduce profile leakage, trains a calibrated Random Forest classifier with Platt scaling, and outputs calibrated multi-class probabilities alongside SHAP feature attributions.*

### 5.1 Cohort Assembly and Literature Curation Protocol
Patient data were gathered through structured curation of peer-reviewed clinical genetics literature. In total, 52 literature sources were evaluated during curation.

To maintain data integrity and avoid duplicate patient entries, we established a quarantine protocol:
- **Secondary Review Compilations:** Low et al. (2016, *Lancet*) included a summary table (Table 2) compiling 32 previously published KBG cases. Because we directly extracted the primary discovery publications, all 32 duplicate review entries were quarantined.
- **Overlapping Case Series:** Ockeloen et al. (2015) (20 candidate records) and Walz et al. (2015) (6 candidate records) were quarantined due to substantial cross-cohort patient overlap with Goldenberg et al. (2016).
- **Re-reported Single Cases:** Low et al. (2017) (1 candidate record) was quarantined as a duplicate of an earlier UK cohort entry.

Under this protocol, four secondary, overlapping, or re-reported sources containing 59 candidate records were quarantined under the predefined duplicate/secondary-source exclusion protocol. The final audited cohort contains 385 unique patients across 48 included peer-reviewed publications, all with molecularly confirmed pathogenic variants.

![Figure 3: Literature Curation and Cohort Provenance Flowchart](file:///d:/finalresearchproject/assets/figures/figure2_provenance_flowchart.png)

*Figure 3. Literature curation and cohort provenance flowchart. From 52 candidate literature sources evaluated during curation, 4 duplicate/secondary sources (59 candidate records) were quarantined, leaving 48 included publications and 385 verified patients.*

Table 2 details the literature provenance and genetic confirmation status across the three syndrome cohorts.

| Syndrome Cohort | Verified Patients ($n$) | Contributing Publications ($n$) | Quarantined Records ($n$) | Primary Genetic Confirmation |
| :--- | :---: | :---: | :---: | :--- |
| **KBG Syndrome** | 298 | 39 | 59 | Pathogenic *ANKRD11* mutation / 16q24.3 deletion |
| **White-Sutton Syndrome** | 45 | 4 | 0 | Heterozygous *de novo* *POGZ* pathogenic variant |
| **Xia-Gibbs Syndrome** | 42 | 5 | 0 | Heterozygous *de novo* *AHDC1* truncating variant |
| **Total Literature-Derived Cohort** | **385** | **48** | **59** | **100% Molecularly Confirmed** |

*Table 2. Literature Provenance and Source Attribution.*

### 5.2 Phenotype Standardization and Vocabulary Construction
Clinical features were mapped to standardized HPO concepts using `hp.obo` (Release `2026-06-23`). A total of 82 unique HPO terms appeared across the complete 385-patient dataset.

To maintain evaluation integrity, the feature vocabulary was fitted strictly on the training partition ($N = 230$), yielding 78 training HPO terms. Four HPO terms occurring only in the held-out test set (`HP:0002121`, `HP:0001156`, `HP:0001508`, `HP:0002126`) were treated as out-of-vocabulary (OOV) features and masked during transformation. Zero OOV terms occurred in the validation set. Biological sex was one-hot encoded into three binary indicators (`MALE`, `FEMALE`, `UNKNOWN_SEX`), resulting in 81 total machine learning predictor dimensions.

### 5.3 Leakage-Control Procedures and Data Partitioning
A critical challenge in clinical machine learning is data leakage caused by identical phenotypic profiles appearing across training and test sets. In our cohort of 385 patients, 370 distinct phenotypic profiles were identified (15 patients shared identical symptom-and-sex combinations with another patient having the same condition).

Leakage-control procedures were implemented through patient-level separation, grouping of identical phenotypic profiles, and training-only feature vocabulary construction.

We applied a 60/20/20 stratified split: Training Set ($N = 230$ patients, 59.7%), Validation Set ($N = 77$ patients, 20.0%), and Held-Out Test Set ($N = 78$ patients, 20.3%). No patient ID and no phenotypic profile appears in more than one partition. However, patients from the same publication could appear across partitions; therefore, source-publication-grouped stress validation was also performed to evaluate publication-specific effects.

### 5.4 Machine Learning Classification and Probability Calibration
The primary predictive model is an ensemble Random Forest Classifier (100 decision trees, maximum tree depth of 10, balanced class weights, random seed 42).

Random Forest vote proportions provide probability-like scores that may not be well calibrated. To obtain calibrated probability estimates, the ensemble was calibrated using sigmoid (Platt) scaling through 5-fold internal cross-validation fitted strictly on the training partition (`CalibratedClassifierCV`).

We also evaluated baseline models on the exact same splits: Standard Random Forest, Logistic Regression (L2 penalty), Support Vector Machine (RBF kernel, calibrated), Decision Tree, K-Nearest Neighbors ($k=5$), Gaussian Naive Bayes, and XGBoost.

### 5.5 Explainability with TreeSHAP
To explain model decision boundaries, we applied TreeSHAP (`shap.TreeExplainer`). SHAP values quantify the marginal contribution of each HPO feature toward the model's predicted probability for each syndrome.

### 5.6 Exploratory Upstream Optical Character Recognition (OCR)
To evaluate the feasibility of ingesting scanned medical records, an exploratory OCR pipeline was built using EasyOCR and fuzzy concept matching.

---

## 6. Results

The audited cohort contains 385 patients with confirmed genetic diagnoses. Table 3 presents the demographic distribution and phenotypic characteristics across the three syndromes.

| Syndrome | Patients ($N$) | Cohort Share (%) | Male ($n$) | Female ($n$) | Unknown Sex ($n$) | Mean HPO Terms / Patient | Molecular Confirmation Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **KBG Syndrome** | 298 | 77.40% | 158 | 129 | 11 | 14.12 ± 3.85 | 100% *ANKRD11* confirmed |
| **White-Sutton Syndrome** | 45 | 11.69% | 24 | 18 | 3 | 15.24 ± 4.10 | 100% *POGZ* confirmed |
| **Xia-Gibbs Syndrome** | 42 | 10.91% | 21 | 18 | 3 | 14.88 ± 4.42 | 100% *AHDC1* confirmed |
| **Total Evaluated Cohort** | **385** | **100.00%** | **203** | **165** | **17** | **14.36 ± 4.12** | **100% Confirmed Pathogenic** |

*Table 3. Clinical Cohort and Demographic Characteristics.*

Figure 4 illustrates the cohort distribution across the three conditions.

![Figure 4: Cohort Distribution](file:///d:/finalresearchproject/assets/figures/figure3_cohort_distribution.png)

*Figure 4. Cohort distribution of the RareDXAI dataset. The literature-derived cohort contains 385 patients: 298 KBG syndrome cases (77.40%), 45 White-Sutton syndrome cases (11.69%), and 42 Xia-Gibbs syndrome cases (10.91%).*

### 6.1 Held-Out Test Set Classification Performance
On the held-out test set ($N = 78$), the Calibrated Random Forest correctly classified 77 out of 78 patients, corresponding to a held-out classification accuracy of **98.72%** (Wilson 95% CI: 93.09%–99.77%). Table 4 compares the Calibrated Random Forest against alternative machine learning algorithms.

| Model Architecture | Test Accuracy [Wilson 95% CI] | Balanced Accuracy | Macro Precision | Macro Recall | Macro Specificity | Macro F1 | Macro AUROC | Brier Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Calibrated Random Forest (Proposed)** | **0.9872 [0.9309, 0.9977]** | **0.9630** | **0.9945** | **0.9630** | **0.9815** | **0.9776** | **1.0000** | **0.0419** |
| Standard Random Forest | 1.0000 [0.9532, 1.0000] | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0500 |
| Logistic Regression (L2) | 1.0000 [0.9532, 1.0000] | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0236 |
| Support Vector Machine (RBF) | 0.9615 [0.8917, 0.9878] | 0.8889 | 0.9841 | 0.8889 | 0.9444 | 0.9306 | 1.0000 | 0.0264 |
| Decision Tree Classifier | 0.9615 [0.8917, 0.9878] | 0.8889 | 0.9841 | 0.8889 | 0.9444 | 0.9252 | 0.9534 | 0.0603 |
| K-Nearest Neighbors ($k=5$) | 0.9615 [0.8917, 0.9878] | 0.9204 | 0.9557 | 0.9204 | 0.9581 | 0.9325 | 0.9970 | 0.0513 |
| Naive Bayes (Gaussian) | 0.9744 [0.9112, 0.9931] | 0.9259 | 0.9394 | 0.9259 | 0.9903 | 0.9250 | 1.0000 | 0.0513 |
| XGBoost Classifier | 0.9615 [0.8917, 0.9878] | 0.8889 | 0.9841 | 0.8889 | 0.9444 | 0.9306 | 1.0000 | 0.0559 |

*Table 4. Machine Learning Model Performance on Held-Out Test Set (N = 78).*

**Model Selection Rationale:** Although Standard Random Forest and Logistic Regression achieved nominally higher accuracy on this particular held-out split, the Calibrated Random Forest was selected as the primary model because the framework explicitly prioritizes probability calibration and interpretable nonlinear phenotype modeling. Its multiclass Brier score was 0.0419, and TreeSHAP provided feature-level explanations of model decision boundaries.

Figure 5 shows the held-out test confusion matrix for the Calibrated Random Forest.

![Figure 5: Confusion Matrix](file:///d:/finalresearchproject/assets/figures/figure4_confusion_matrix.png)

*Figure 5. Held-out test set confusion matrix (N = 78 patients). The model correctly classified 60 of 60 KBG cases, 9 of 9 Xia-Gibbs cases, and 8 of 9 White-Sutton cases, with a single atypical White-Sutton patient classified as KBG syndrome.*

### 6.2 Per-Class Classification Performance Breakdown
Table 5 presents the detailed per-class classification metrics on the held-out test set.

| Syndrome Target | Test Support ($n$) | Correct ($n$) | Precision | Recall (Sensitivity) | F1-Score | Specificity | One-vs-Rest AUROC | One-vs-Rest Brier |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **White-Sutton Syndrome** | 9 | 8 | 1.0000 | 0.8889 (8/9) | 0.9412 | 1.0000 | 1.0000 | 0.0137 |
| **Xia-Gibbs Syndrome** | 9 | 9 | 1.0000 | 1.0000 (9/9) | 1.0000 | 1.0000 | 1.0000 | 0.0084 |
| **KBG Syndrome** | 60 | 60 | 0.9836 | 1.0000 (60/60) | 0.9917 | 0.9444 | 1.0000 | 0.0198 |
| **Macro Average** | **78** | **77** | **0.9945** | **0.9630** | **0.9776** | **0.9815** | **1.0000** | **0.0140** |

*Table 5. Per-Class Classification Performance Breakdown (Calibrated Random Forest).*

**Error Analysis:** The single misclassified patient was `WhiteSutton_PT19`, an individual with White-Sutton syndrome who presented with severe developmental delay and dental crowding, but lacked documented behavioral autism features. The predicted probability distribution indicated substantial uncertainty between KBG and White-Sutton for this case (KBG: 47.04%, White-Sutton: 46.51%, Xia-Gibbs: 6.45%), demonstrating that the model output reflected ambiguity rather than an overconfident error.

Figure 6 summarizes the overall classification metrics on the held-out test set.

![Figure 6: Multi-Class Performance Metrics](file:///d:/finalresearchproject/assets/figures/figure5_classification_performance.png)

*Figure 6. Multi-class classification performance on the held-out test set (N = 78). Accuracy: 98.72%, Balanced Accuracy: 96.30%, Macro Precision: 99.45%, Macro Recall: 96.30%, Macro Specificity: 98.15%, and Macro F1-Score: 97.76%.*

### 6.3 Cross-Validation vs. Source-Publication-Grouped Stress Validation
To evaluate model consistency across different cohort partitions, we conducted two cross-validation experiments:
1. **Profile-Grouped 5-Fold Cross-Validation:** Patients with identical profiles were retained within the same fold: Mean Accuracy of **97.14% ± 2.23%** (Fold scores: 0.9740, 0.9351, 0.9870, 1.0000, 0.9610) and Mean Macro F1 of **94.89% ± 4.04%** (Fold scores: 0.9572, 0.8851, 0.9776, 1.0000, 0.9246).
2. **Source-Publication-Grouped Stress Validation (GroupKFold by Source):** Cross-validation was grouped strictly by primary source publication, withholding entire publications from training folds: Mean Accuracy of **79.62% ± 27.05%** and Mean Macro F1 of **59.51% ± 26.81%**.

![Figure 7: Cross-Validation vs. Source-Publication-Grouped Stress Validation](file:///d:/finalresearchproject/assets/figures/figure6_cross_validation_performance.png)

*Figure 7. Comparison between profile-grouped 5-fold cross-validation and source-publication-grouped stress validation. Profile-grouped CV achieved 97.14% ± 2.23% accuracy, whereas source-publication-grouped stress validation dropped to 79.62% ± 27.05% accuracy, indicating that publication-specific reporting habits influence model transferability.*

The source-publication-grouped stress validation suggests that performance may decrease when the model encounters phenotype distributions and reporting patterns from previously unseen publications.

### 6.4 Model Interpretability with TreeSHAP
TreeSHAP analysis identified the standardized HPO features that most strongly influenced model decision boundaries. Table 6 lists the top 10 HPO features ranked by mean absolute SHAP value.

| Rank | HPO ID | Canonical Phenotype Name | Associated Syndrome | Mean Absolute SHAP | Clinical Context (Literature Background) |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **1** | `HP:0000219` | Thin upper lip vermilion | Xia-Gibbs / KBG | 0.0614 | Facial feature frequently described in Xia-Gibbs syndrome |
| **2** | `HP:0001155` | Abnormality of the hand | KBG Syndrome | 0.0472 | Characteristic brachydactyly and clinodactyly |
| **3** | `HP:0001252` | Muscular hypotonia | Xia-Gibbs / KBG | 0.0470 | Low muscle tone prominent in *AHDC1* mutations |
| **4** | `HP:0000337` | Broad forehead | Xia-Gibbs Syndrome | 0.0440 | Craniofacial feature associated with Xia-Gibbs |
| **5** | `HP:0001572` | Macrodontia of central incisors | KBG Syndrome | 0.0435 | Known cardinal clinical sign of KBG syndrome (*ANKRD11*) |
| **6** | `HP:0000717` | Autism spectrum disorder | White-Sutton Syndrome | 0.0408 | Behavioral phenotype reported in *POGZ* variants |
| **7** | `HP:0001270` | Motor delay | White-Sutton Syndrome | 0.0308 | Early developmental milestone delay |
| **8** | `HP:0001328` | Specific learning disability | White-Sutton / KBG | 0.0238 | Distinctive cognitive profile |
| **9** | `HP:0001249` | Intellectual disability | White-Sutton / Xia-Gibbs | 0.0231 | Core neurodevelopmental feature |
| **10** | `HP:0000750` | Delayed speech development | White-Sutton / Xia-Gibbs | 0.0226 | Expressive speech and language impairment |

*Table 6. Key HPO Features Associated with Model Decision Boundaries.*

**Note on Interpretation:** These HPO features were strongly associated with model decision boundaries. These features represent statistical associations with model decision boundaries and must not be interpreted as independent causal or definitive diagnostic criteria. The clinical context provided is background clinical interpretation, not a causal conclusion from SHAP.

Figure 8 displays the top HPO features ranked by their mean absolute SHAP values.

![Figure 8: SHAP Feature Importance](file:///d:/finalresearchproject/assets/figures/figure7_shap_feature_importance.png)

*Figure 8. Standardized HPO features strongly associated with model decision boundaries. Features are ranked by mean absolute SHAP values across test patients.*

### 6.5 Probability Calibration and Reliability Assessment
Probability calibration was assessed using Brier score and expected calibration error to evaluate the alignment between predicted probabilities and empirical outcomes:
- **Multiclass Brier Score:** **0.0419** (measures squared probability error; lower is better).
- **Mean One-vs-Rest Brier Score:** **0.0140** (White-Sutton: 0.0137; Xia-Gibbs: 0.0084; KBG: 0.0198).
- **Expected Calibration Error (ECE):** **8.59%** across 10 probability bins.

Figure 9 presents the multi-class calibration curves and Brier score breakdowns.

![Figure 9: Probability Calibration](file:///d:/finalresearchproject/assets/figures/figure8_calibration_curve.png)

*Figure 9. Probability calibration and reliability assessment on the held-out test set (N = 78). (A) Multi-class reliability curve comparing predicted probability against empirical accuracy (ECE = 8.59%). (B) Multiclass and One-vs-Rest Brier score breakdown.*

### 6.6 Threshold-Agnostic Performance (ROC and PR Curves)
Threshold-agnostic discrimination on the held-out test set yielded macro AUROC and macro AUPRC values of 1.0000:
- **Macro AUROC:** **1.0000** (White-Sutton: 1.0000; Xia-Gibbs: 1.0000; KBG: 1.0000).
- **Macro AUPRC:** **1.0000** (White-Sutton: 1.0000; Xia-Gibbs: 1.0000; KBG: 1.0000).

These values reflect strong separation on the held-out test set of 78 patients; however, the relatively small sample size and closed-set design limit broader interpretation.

![Figure 10: ROC and PR Curves](file:///d:/finalresearchproject/assets/figures/figure9_roc_pr_curves.png)

*Figure 10. Discriminative performance curves across decision thresholds on the held-out test set (N = 78). (A) Multi-class One-vs-Rest ROC curves (Macro AUROC = 1.0000). (B) Multi-class Precision-Recall curves (Macro AUPRC = 1.0000).*

### 6.7 Exploratory Upstream OCR Evaluation
Evaluation of the upstream EasyOCR module on scanned clinical summaries yielded:
- **Character Error Rate (CER):** **11.42%**
- **Word Error Rate (WER):** **92.00%**
- **Concept Mapping on Clean Text:** **100.0%** (10/10 test phrases successfully mapped)
- **Concept Mapping on Noisy Scans:** **80.0%** (8/10 test phrases successfully mapped)

**Clinical Note:** Due to the high Word Error Rate on scanned documents, OCR is designated strictly as an exploratory upstream utility and is not clinically validated for automated standalone use without clinician verification.

### 6.8 Limitations and Generalization Considerations
We acknowledge the following scientific limitations:
1. **Moderate Sample Size:** Although $N = 385$ is substantial for these ultra-rare conditions, smaller sample sizes in minority classes ($n = 45$ for White-Sutton, $n = 42$ for Xia-Gibbs) yield wider confidence intervals.
2. **Natural Class Imbalance:** KBG syndrome accounts for 77.40% of the cohort, reflecting higher historical publication volume rather than true epidemiological prevalence.
3. **Source-Publication-Grouped Performance Drop:** The drop to 79.62% accuracy in source-publication-grouped validation indicates that differences in clinical reporting styles affect model transferability.
4. **Literature Selection Bias:** Published case reports often emphasize classic or severe presentations, which may not fully represent milder community presentations.
5. **No Prospective Hospital EHR Validation:** The framework was evaluated on retrospective literature cohorts; prospective validation in uncurated hospital electronic health records is still required.
6. **Binary Coding of Symptoms:** Symptoms not mentioned in published reports are coded as 0, which cannot distinguish between true biological absence and clinical non-reporting.
7. **Fixed Feature Vocabulary:** Four rare symptoms in the test set were unobserved during training and were masked out during inference.
8. **Exploratory OCR Status:** The OCR pipeline is an exploratory upstream tool requiring manual human verification.
9. **Closed-Set Scope:** The current model is a closed-set three-class classification system and should not be interpreted as a general-purpose rare disease diagnostic model.
10. **Ontology Dependence:** Model accuracy depends directly on how accurately clinical findings are converted into standardized HPO codes.

Therefore, the present study should be interpreted as a retrospective, literature-derived computational validation rather than evidence of clinical deployment readiness.

---

## 7. Conclusion

This study presented RareDXAI, a computational framework that converts clinical genetics literature into structured Human Phenotype Ontology representations to assist in predicting and prioritizing between three syndromic neurodevelopmental disorders: KBG syndrome, White-Sutton syndrome, and Xia-Gibbs syndrome.

By curating an audited cohort of 385 molecularly confirmed patients across 48 peer-reviewed publications and applying profile-grouped partitioning, RareDXAI achieved a held-out test classification accuracy of **98.72%** (macro F1 of **0.9776**) with calibrated probability estimation (Brier score of **0.0419**) and interpretable SHAP feature attributions.

Importantly, source-publication-grouped stress validation demonstrated that performance decreases (79.62%) when evaluating phenotype distributions from previously unseen publications. This finding underscores that practical clinical decision support will require standardized phenotyping protocols and independent external validation. RareDXAI provides a transparent, reproducible baseline for phenotype-based rare disease decision support, establishing a foundation for future integration with genomic sequencing and electronic health records.

---

## 8. References

1. Assia Batzir, N., et al. (2020). Further delineation of White-Sutton syndrome: Clinical and molecular characterization of 22 individuals. *American Journal of Medical Genetics Part A*, 182(8), 1878–1889. https://doi.org/10.1002/ajmg.a.61633
2. Birgmeier, J., et al. (2020). AMELIE accelerates Mendelian patient diagnosis directly from the primary literature by machine learning. *Science Translational Medicine*, 12(545), eaau9113. https://doi.org/10.1126/scitranslmed.aau9113
3. Feng, Y., et al. (2021). PhenoTagger: A hybrid method for Human Phenotype Ontology concept recognition using deep learning and dictionary index. *Bioinformatics*, 37(5), 679–685. https://doi.org/10.1093/bioinformatics/btaa897
4. Gargano, M. A., et al. (2024). The Human Phenotype Ontology in 2024: phenotypes around the world. *Nucleic Acids Research*, 52(D1), D1333–D1346. https://doi.org/10.1093/nar/gkad1005
5. Hsieh, T. C., et al. (2022). GestaltMatcher: deep convolutional neural networks for rare disease facial dysmorphology matching. *Nature Genetics*, 54(4), 349–354. https://doi.org/10.1038/s41588-021-01010-x
6. Jacobsen, J. O. B., et al. (2022). The GA4GH Phenopacket schema: A computable format for phenotypic data for rare diseases and beyond. *Nature Biotechnology*, 40(6), 817–820. https://doi.org/10.1038/s41587-022-01357-4
7. Khayat, M. M., et al. (2021). Expanding the phenotypic spectrum of Xia-Gibbs syndrome in 8 patients. *American Journal of Medical Genetics Part A*, 185(12), 3737–3746. https://doi.org/10.1002/ajmg.a.62446
8. Köhler, S., et al. (2021). The Human Phenotype Ontology in 2021. *Nucleic Acids Research*, 49(D1), D1207–D1217. https://doi.org/10.1093/nar/gkaa1043
9. Ladewig, E., et al. (2023). Phenopacket Store: A curated repository of computable clinical case reports. *Database*, 2023, baad074. https://doi.org/10.1093/database/baad074
10. Liu, C., et al. (2020). Doc2HPO: a web application for efficient and standardized clinical phenotype curation. *BMC Bioinformatics*, 20(1), 634. https://doi.org/10.1186/s12859-019-3198-y
11. Martinez-Cayuelas, E., et al. (2023). KBG syndrome: delineation of the clinical spectrum in 67 patients and diagnostic criteria. *European Journal of Human Genetics*, 31(7), 793–802. https://doi.org/10.1038/s41431-023-01314-x
12. Robinson, P. N., et al. (2020). Interpretable Clinical Genomics with a Likelihood Ratio Baseline. *The American Journal of Human Genetics*, 107(3), 403–417. https://doi.org/10.1016/j.ajhg.2020.06.021
13. Rönicke, S., et al. (2020). Can an artificial intelligence tool improve the diagnosis of rare diseases? A comprehensive review of current clinical decision support systems. *Molecular and Cellular Pediatrics*, 7(1), 12. https://doi.org/10.1186/s43042-020-00055-5
14. Schuetz, D., et al. (2023). Automated extraction and ontological harmonization of patient phenotypes from rare disease case reports. *Journal of Biomedical Informatics*, 145, 104467. https://doi.org/10.1016/j.jbi.2023.104467
15. Zhao, M., et al. (2020). Phen2Gene: a rapid phenotype-driven gene prioritization tool using Human Phenotype Ontology. *Nucleic Acids Research*, 48(9), 4728–4739. https://doi.org/10.1093/nar/gkaa211
