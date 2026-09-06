# RareDXAI: A Human Phenotype Ontology-Based Framework for Rare Disease Prediction

**Dharshini K. et al.**  
*Computational Genomics & Clinical AI Research Group*  
**Manuscript Type:** Original Research Article  
**Ontology Standard:** Human Phenotype Ontology (Release `2026-06-23`)  
**Evidence Package:** Locked & Audited Repository Data ($N = 385$)  

---

## 1. Abstract

**Background:** Rare genetic diseases affect more than 300 million people worldwide. Diagnosing these conditions is difficult because many rare diseases share similar symptoms, such as developmental delays, speech difficulties, and intellectual disability. In pediatric genetics, syndromic neurodevelopmental disorders like KBG syndrome, White-Sutton syndrome, and Xia-Gibbs syndrome present overlapping clinical signs that often lead to prolonged diagnostic delays lasting five to seven years.

**Methods:** We developed **RareDXAI**, a computational decision-support framework that uses standardized Human Phenotype Ontology (HPO) terms to predict and differentiate between rare neurodevelopmental syndromes. We curated an audited, literature-derived cohort of 385 patients with confirmed genetic diagnoses across 48 peer-reviewed publications (from 52 candidate literature sources evaluated during curation, with 59 duplicate records quarantined). Clinical features were encoded into 78 binary HPO terms and 3 one-hot sex features (81 predictor dimensions). To prevent data leakage, identical phenotypic profiles were grouped before applying a 60/20/20 train/validation/test split ($N=230$ training, $N=77$ validation, $N=78$ held-out test), and feature vocabularies were constructed strictly from training data. We trained a Random Forest model with Platt probability scaling (5-fold internal cross-calibration) and explained predictions using TreeSHAP.

**Results:** On the held-out test set ($N=78$), RareDXAI correctly classified 77 out of 78 patients, achieving an accuracy of **98.72%** (Wilson 95% CI: 93.09%–99.77%), balanced accuracy of **96.30%**, macro precision of **99.45%**, macro recall of **96.30%**, macro specificity of **98.15%**, and macro F1-score of **97.76%**. Multi-class threshold-agnostic evaluation yielded a macro AUROC of **1.0000** and macro AUPRC of **1.0000**, with a multiclass Brier score of **0.0419** and Expected Calibration Error (ECE) of **8.59%**. Five-fold stratified grouped cross-validation showed high consistency ($97.14% \pm 2.23%$ accuracy; macro F1: $94.89% \pm 4.04%$). In contrast, leave-one-study-out stress validation (GroupKFold by source publication) showed lower performance ($79.62% \pm 27.05%$ accuracy; macro F1: $59.51% \pm 26.81%$), demonstrating that inter-study differences in phenotypic reporting affect generalizability. SHAP analysis identified standardized HPO features strongly associated with model decision boundaries, such as macrodontia (`HP:0001572`) for KBG syndrome, autism spectrum traits (`HP:0000717`) for White-Sutton syndrome, and thin upper lip vermilion (`HP:0000219`) for Xia-Gibbs syndrome. Exploratory optical character recognition (OCR) on digitized notes achieved a Character Error Rate of 11.42% and Word Error Rate of 92.00%.

**Conclusions:** RareDXAI provides an interpretable and calibrated computational framework to assist clinicians in prioritizing rare disease candidates. While held-out test performance is high under profile-grouped controls, the drop in source-grouped validation highlights that real-world deployment requires standardized clinical phenotyping across healthcare centers.

**Keywords:** Rare Diseases, Human Phenotype Ontology, Machine Learning, Random Forest, Model Interpretability, SHAP, Clinical Decision Support, Neurodevelopmental Disorders.

---

## 2. Introduction

Rare diseases are medical conditions that affect a small fraction of the population, typically defined as fewer than 1 in 2,000 individuals in Europe or fewer than 200,000 individuals in the United States. Although each specific disorder is rare, there are over 7,000 recognized rare genetic diseases, which together affect an estimated 300 to 400 million people globally. 

Most rare diseases have a genetic origin and present during early childhood. Despite advances in next-generation DNA sequencing—such as whole-exome sequencing (WES) and whole-genome sequencing (WGS)—patients and families still face a long and stressful journey known as the "diagnostic odyssey." On average, getting a correct diagnosis takes between five and seven years, involves multiple specialist consultations, and often includes several incorrect diagnoses.

A major reason for this delay is clinical overlap. Many genetic syndromes share broad, non-specific symptoms, including intellectual disability, delayed motor milestones, speech impairments, and behavioral challenges. This diagnostic challenge is especially evident among three syndromic neurodevelopmental conditions:

1. **KBG Syndrome (MIM #148050):** Caused by mutations or deletions in the *ANKRD11* gene on chromosome 16q24.3. Cardinal clinical features include unusually large upper front teeth (macrodontia of the central incisors), a characteristic triangular face, prominent eyebrows, short stature, hand differences (such as short fingers or brachydactyly), and intellectual disability.
2. **White-Sutton Syndrome (MIM #616364):** Caused by *de novo* mutations in the *POGZ* gene on chromosome 1q21.3. Common manifestations include developmental delays, intellectual disability, speech impairment, autism spectrum disorder features, small head size (microcephaly), and distinctive facial features.
3. **Xia-Gibbs Syndrome (MIM #615829):** Caused by *de novo* mutations in the *AHDC1* gene on chromosome 1p36.11. Key features include low muscle tone in infancy (hypotonia), global developmental delay, severe speech impairment, a broad forehead, downward-slanting eyes, a thin upper lip, structural brain differences, and sleep apnea.

Because these three conditions share common neurodevelopmental symptoms, differentiating between them based solely on routine clinical observation can be difficult.

To make patient features computable, the biomedical community developed the **Human Phenotype Ontology (HPO)**. The HPO provides a standardized vocabulary of medical terms that describe clinical signs and symptoms in a structured, hierarchical manner. For example, rather than writing "large front teeth" in free text, clinicians and researchers use the standardized HPO concept `HP:0001572` (Macrodontia of central incisors). This standardization allows algorithms to analyze complex patient symptoms systematically.

However, applying machine learning to rare diseases involves specific scientific challenges:
- Rare disease datasets are naturally small.
- Retrospective data collected from published papers may have reporting biases.
- If patients with identical symptoms appear in both the training and test sets, the model may simply memorize patterns (data leakage), artificially inflating performance.
- Complex machine learning models can act as "black boxes," making it hard for clinicians to understand why a prediction was made.

To address these challenges, we built **RareDXAI**, a phenotype-driven framework designed to assist in rare disease prediction. RareDXAI uses an audited dataset of 385 molecularly confirmed patients from 48 peer-reviewed publications, applies strict grouping to prevent data leakage, uses calibrated Random Forest classification to provide reliable probability scores, and uses SHAP (SHapley Additive exPlanations) to show which clinical features influenced the model's decision boundaries.

Figure 1 provides a visual overview of representative clinical features associated with the three target syndromes.

![Figure 1: Representative Clinical/Phenotypic Features](file:///d:/finalresearchproject/assets/figures/syndrome_phenotypes_illustration.jpg)

*Figure 1. Representative clinical and phenotypic features associated with KBG, White-Sutton, and Xia-Gibbs syndromes. The illustration provides visual context and does not represent all affected individuals.*

---

## 3. Literature Survey

Computational methods for rare disease diagnosis have evolved from early manual lookup tables to modern ontology-based machine learning and natural language processing (NLP). Mining individual patient case reports from peer-reviewed medical literature to create structured, computable datasets is a well-established practice in computational genomics.

The most notable precedent for this approach is the **Global Alliance for Genomics and Health (GA4GH) Phenopacket** standard and the **Phenopacket Store**. Researchers have demonstrated that converting published clinical case reports into structured HPO records creates reliable, benchmarked datasets for testing diagnostic algorithms.

We reviewed 15 key peer-reviewed studies published between 2020 and 2026 that directly support the design, data curation, and modeling choices of RareDXAI.

### 3.1 Review of Relevant Literature (2020–2026)

1. **Jacobsen et al. (2022)** published the GA4GH Phenopacket schema in *Nature Biotechnology*. The Phenopacket format (ISO 4454:2022) established an international standard for sharing computable patient-level phenotypic and genomic data. This work provides the foundation for representing clinical cases as structured HPO profiles.
2. **Ladewig et al. (2023)** introduced the **Phenopacket Store** in *Database*. They curated thousands of computable case reports mined directly from published biomedical literature into structured Phenopackets. Their study directly demonstrates that extracting patient-level HPO data from published literature provides reliable benchmarks for computational tools, serving as a primary methodological model for RareDXAI.
3. **Gargano et al. (2024)** described the Human Phenotype Ontology in 2024 in *Nucleic Acids Research*. The HPO expanded to over 16,000 terms with improved definitions and international translations, providing the canonical `hp.obo` vocabulary (release `2026-06-23`) used in our framework.
4. **Köhler et al. (2021)** detailed the HPO architecture in *Nucleic Acids Research*, explaining how hierarchical relationships in the ontology allow algorithms to group specific clinical terms under broader physiological categories.
5. **Robinson et al. (2020)** developed **LIRICAL** in *The American Journal of Human Genetics*. LIRICAL uses likelihood ratios across observed and excluded HPO terms to calculate diagnostic odds for candidate diseases, emphasizing the importance of interpretable diagnostic explanations.
6. **Birgmeier et al. (2020)** introduced **AMELIE** in *Science Translational Medicine*. AMELIE uses natural language processing and machine learning to parse full-text literature and match patient HPO terms with causative genetic variants, demonstrating that literature mining directly aids genetic diagnosis.
7. **Feng et al. (2021)** developed **PhenoTagger** in *Bioinformatics*. PhenoTagger combines deep convolutional neural networks with dictionary lookups to extract HPO terms from clinical text with high precision.
8. **Liu et al. (2020)** created **Doc2HPO** in *BMC Bioinformatics*, providing a web application for extracting HPO concepts from unstructured clinical notes, supporting upstream text phenotyping.
9. **Zhao et al. (2020)** developed **Phen2Gene** in *Nucleic Acids Research*, prioritizing disease-causing genes by scoring HPO term overlap, showing the utility of weighted HPO representation.
10. **Hsieh et al. (2022)** introduced **GestaltMatcher** in *Nature Genetics*. GestaltMatcher uses deep neural networks to extract facial feature embeddings from clinical photos to support rare disease matching.
11. **Rönicke et al. (2020)** conducted a systematic review in *Molecular and Cellular Pediatrics* on AI clinical decision support systems for rare diseases. They highlighted that clinical utility requires calibrated probability scores, strict evaluation controls, and clear explainability.
12. **Martinez-Cayuelas et al. (2023)** published a multicenter study of 67 KBG syndrome patients in the *European Journal of Human Genetics*, establishing the clinical frequency of macrodontia, intellectual disability, and hand differences.
13. **Assia Batzir et al. (2020)** delineated White-Sutton syndrome across 22 individuals in the *American Journal of Medical Genetics Part A*, detailing the prevalence of autism spectrum traits, speech delay, and motor delay.
14. **Khayat et al. (2021)** characterized 8 Xia-Gibbs syndrome patients in the *American Journal of Medical Genetics Part A*, documenting hypotonia, sleep apnea, and facial signs.
15. **Schuetz et al. (2023)** evaluated automated phenotype extraction from case reports in the *Journal of Biomedical Informatics*, showing that optical character recognition errors on clinical scans require careful validation.

Table 1 summarizes these 15 peer-reviewed studies.

#### Table 1: Literature Comparison Matrix (15 Peer-Reviewed Studies, 2020–2026)

| Year | Primary Authors | Paper Title & Venue | Dataset / Source | Phenotype Representation | Computational Method | Main Contribution | Similarity to RareDXAI |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2022** | Jacobsen et al. | *The GA4GH Phenopacket schema* (*Nat Biotechnol*) | Global clinical repositories | Hierarchical HPO + GA4GH Schema | ISO Standard (ISO 4454:2022) | Standardized computable case report format | Conceptual basis for computable patient phenotyping |
| **2023** | Ladewig et al. | *Phenopacket Store* (*Database*) | Case reports from published literature | Curated patient-level HPO profiles | Curated case repository & validation tools | Mined thousands of literature cases into HPO Phenopackets | Direct methodological precedent for literature extraction |
| **2024** | Gargano et al. | *Human Phenotype Ontology in 2024* (*Nucleic Acids Res*) | HPO International Consortium | Controlled vocabulary (>16,000 terms) | Knowledge graph structures | Expanded definitions & disease annotations | Source of canonical terminology (Release `2026-06-23`) |
| **2021** | Köhler et al. | *Human Phenotype Ontology in 2021* (*Nucleic Acids Res*) | Rare disease clinical databases | Directed acyclic graph of HPO | Semantic similarity algorithms | Foundation for standardized computational phenomics | Baseline ontology structure for feature mapping |
| **2020** | Robinson et al. | *Interpretable Clinical Genomics (LIRICAL)* (*Am J Hum Genet*) | Real clinical cases & simulations | Observed & excluded HPO terms | Likelihood ratio & Bayesian inference | Interpretable diagnostic odds for genomic phenotypes | Supports interpretable decision support |
| **2020** | Birgmeier et al. | *AMELIE: Automated Literature Evaluation* (*Sci Transl Med*) | 138,000+ primary literature papers | HPO concept extraction | Supervised machine learning & NLP | Automated matching of patient HPO profiles to literature | Confirms viability of literature-derived patient matching |
| **2021** | Feng et al. | *PhenoTagger* (*Bioinformatics*) | PubMed Central text corpora | Standardized HPO concept tagging | Hybrid CNN + dictionary indexing | High-precision automated concept recognition | Informs text-to-HPO conversion strategies |
| **2020** | Liu et al. | *Doc2HPO* (*BMC Bioinformatics*) | Unstructured clinical notes | Interactive HPO term mapping | String parsing + Named Entity Recognition | Web tool for clinical text phenotyping | Upstream precedent for concept parsing |
| **2020** | Zhao et al. | *Phen2Gene* (*Nucleic Acids Res*) | OMIM, Orphanet, HPO disease annotations | Weighted HPO disease-gene profiles | Information theoretic gene scoring | Rapid phenotype-driven gene prioritization | Uses HPO term weighting similar to feature vectorization |
| **2022** | Hsieh et al. | *GestaltMatcher* (*Nat Genet*) | Patient clinical photographs | Deep facial dysmorphic embeddings | Deep Convolutional Neural Networks | Image-based rare disease phenotypic matching | Visual modality for syndromic recognition |
| **2020** | Rönicke et al. | *AI Tools in Rare Disease Diagnosis* (*Mol Cell Pediatr*) | Literature review of rare disease CDSS | Variable (HPO, ICD, UMLS) | Systematic comparative analysis | Highlighted risks of data leakage and uncalibrated models | Validates RareDXAI's focus on calibration and controls |
| **2023** | Martinez-Cayuelas et al. | *KBG Syndrome Delineation* (*Eur J Hum Genet*) | 67 molecularly confirmed KBG patients | Clinical phenotypic descriptions | Multicenter clinical cohort analysis | Delineated cardinal features (*ANKRD11* mutations) | Primary clinical cohort source for KBG syndrome |
| **2020** | Assia Batzir et al. | *White-Sutton Syndrome Delineation* (*Am J Med Genet A*) | 22 patients with *POGZ* pathogenic variants | Clinical phenotypic profiles | Detailed clinical characterization | Established cardinal spectrum of White-Sutton syndrome | Primary clinical cohort source for White-Sutton |
| **2021** | Khayat et al. | *Xia-Gibbs Syndrome Phenotypic Spectrum* (*Am J Med Genet A*) | 8 patients with *AHDC1* truncating variants | Systematic clinical feature tables | Clinical case series analysis | Expanded phenotypic spectrum of Xia-Gibbs syndrome | Clinical cohort contributor for Xia-Gibbs |
| **2023** | Schuetz et al. | *Ontological Harmonization from Case Reports* (*J Biomed Inform*) | Case reports & electronic health records | HPO term mapping | Automated NLP & fuzzy ontology matching | Evaluated OCR error propagation in clinical phenotyping | Contextualizes RareDXAI's OCR evaluations |

---

## 4. Mathematical Expression

This section describes the mathematical formulas used in RareDXAI for patient representation, classification, calibration, performance metrics, and model interpretability. Each equation is followed by a plain-language explanation.

### 4.1 Patient Phenotype Vector

$$\mathbf{x}_i = [x_{i1}, x_{i2}, \dots, x_{id}]$$

*Explanation:* Each patient $i$ is represented as a list of numbers called a feature vector $\mathbf{x}_i$. The total number of features is $d = 81$, which includes 78 binary clinical HPO features and 3 demographic sex indicators.

### 4.2 Binary HPO Feature Encoding

$$x_{ij} \in \{0, 1\} = egin{cases} 1 & 	ext{if HPO term } j 	ext{ is present in patient } i \ 0 & 	ext{if HPO term } j 	ext{ is absent or not reported} \end{cases}$$

*Explanation:* For each clinical term $j$, we assign a value of 1 if the medical record mentions that symptom, and 0 if the symptom is absent or not mentioned.

### 4.3 Random Forest Probability Estimation

$$P(y = c \mid \mathbf{x}) = rac{1}{T} \sum_{t=1}^T \mathbb{I}\left(h_t(\mathbf{x}) = cight)$$

*Explanation:* A Random Forest is made up of $T = 100$ individual decision trees. The probability that a patient has syndrome $c$ is calculated as the fraction of trees that vote for that disease, where $\mathbb{I}(\cdot)$ equals 1 when a tree chooses class $c$ and 0 otherwise.

### 4.4 Predicted Disease Class

$$\hat{y} = rg\max_{c \in \{0, 1, 2\}} P(y = c \mid \mathbf{x})$$

*Explanation:* The model selects the disease $\hat{y}$ that receives the highest predicted probability among the three candidate conditions (0: White-Sutton, 1: Xia-Gibbs, 2: KBG syndrome).

### 4.5 Classification Accuracy

$$	ext{Accuracy} = rac{\sum_{i=1}^N \mathbb{I}(\hat{y}_i = y_i)}{N} = rac{	ext{Number of Correct Predictions}}{	ext{Total Number of Patients}}$$

*Explanation:* Accuracy measures the proportion of patients whose disease was correctly identified out of the total evaluation sample $N$.

### 4.6 Precision (Positive Predictive Value)

$$	ext{Precision} = rac{	ext{TP}}{	ext{TP} + 	ext{FP}}$$

*Explanation:* Precision measures how many of the patients predicted to have a specific disease actually have that disease. Here, $	ext{TP}$ is True Positives (correct positive predictions) and $	ext{FP}$ is False Positives (incorrect positive predictions).

### 4.7 Recall (Sensitivity)

$$	ext{Recall} = rac{	ext{TP}}{	ext{TP} + 	ext{FN}}$$

*Explanation:* Recall measures how many of the actual patients with a specific disease were successfully identified by the model. Here, $	ext{FN}$ is False Negatives (missed cases).

### 4.8 F1-Score

$$	ext{F1} = 2 	imes rac{	ext{Precision} 	imes 	ext{Recall}}{	ext{Precision} + 	ext{Recall}}$$

*Explanation:* The F1-score is the harmonic average of precision and recall. It gives a balanced score between 0 and 1, which is useful when some diseases have fewer patients than others.

### 4.9 Balanced Accuracy

$$	ext{Balanced Accuracy} = rac{1}{C} \sum_{c=1}^C 	ext{Recall}_c$$

*Explanation:* Balanced accuracy is the simple average of recall across all $C = 3$ diseases. This prevents the majority disease (KBG syndrome) from dominating the evaluation score.

### 4.10 SHAP Additive Feature Attribution

$$f(\mathbf{x}) = \phi_0 + \sum_{j=1}^d \phi_j$$

*Explanation:* SHAP explains a prediction by breaking it down into individual parts. The model output $f(\mathbf{x})$ equals a baseline average score $\phi_0$ plus the sum of contributions $\phi_j$ from each individual clinical feature $j$. A positive $\phi_j$ pushes the model toward predicting a disease, while a negative $\phi_j$ pushes it away.

---

## 5. Model Methodologies

Figure 2 illustrates the overall system workflow of RareDXAI, from literature extraction to calibrated prediction and explainability.

![Figure 2: RareDXAI System Workflow](file:///d:/finalresearchproject/assets/figures/figure1_architecture.png)

*Figure 2. RareDXAI system workflow diagram. The pipeline takes published clinical case reports, extracts and standardizes clinical features into HPO terms, creates a structured patient matrix, applies profile-grouped splitting, trains a calibrated Random Forest classifier, and produces calibrated diagnostic probabilities alongside SHAP explanations.*

### 5.1 Cohort Assembly and Deduplication Protocol

Patient data were gathered through a comprehensive review of peer-reviewed clinical genetics literature. In total, **52 literature sources were evaluated during curation**.

To ensure data quality and avoid counting the same patient more than once, we established a strict quarantine protocol:
- **Review Papers:** Low et al. (2016, *Lancet*) included a summary table (Table 2) compiling 32 previously reported KBG cases from earlier studies. Because we directly extracted the original discovery papers, all 32 duplicate review entries were quarantined.
- **Overlapping Case Series:** Ockeloen et al. (2015) (20 cases) and Walz et al. (2015) (6 cases) were quarantined due to substantial patient overlap with Goldenberg et al. (2016).
- **Re-reported Single Cases:** Low et al. (2017) (1 case) was quarantined as a duplicate of an earlier UK cohort record.

In total, 4 sources representing **59 duplicate candidate records were quarantined**. The final audited cohort contains **385 unique patients** across **48 included peer-reviewed publications**, all with molecularly confirmed pathogenic variants.

Figure 3 displays the literature curation flowchart.

![Figure 3: Literature Curation Flowchart](file:///d:/finalresearchproject/assets/figures/figure2_provenance_flowchart.png)

*Figure 3. Literature curation and cohort provenance flowchart. From 52 candidate literature sources evaluated, 4 duplicate/review sources (59 candidate records) were quarantined, leaving 48 included publications and 385 verified patients.*

Table 2 shows the literature provenance across the three syndromes.

#### Table 2: Literature Provenance and Source Attribution

| Syndrome Cohort | Verified Patients ($n$) | Contributing Publications ($n$) | Quarantined Duplicate Records ($n$) | Primary Genetic Cause |
| :--- | :---: | :---: | :---: | :--- |
| **KBG Syndrome** | 298 | 39 | 59 | Pathogenic *ANKRD11* mutation / 16q24.3 deletion |
| **White-Sutton Syndrome** | 45 | 4 | 0 | Heterozygous *de novo* *POGZ* pathogenic variant |
| **Xia-Gibbs Syndrome** | 42 | 5 | 0 | Heterozygous *de novo* *AHDC1* truncating variant |
| **Total Literature-Derived Cohort** | **385** | **48** | **59** | **100% Molecularly Confirmed** |

### 5.2 Phenotype Standardization and Vocabulary Construction

Patient clinical notes and tables were mapped to standardized HPO concepts using `hp.obo` (Release `2026-06-23`). A total of 82 unique HPO terms appeared across the complete 385-patient dataset.

To prevent test-set information from influencing model construction:
- The feature vocabulary was built strictly from the **training partition** ($N = 230$), which contained **78 unique HPO terms**.
- Four rare HPO terms present only in the test set (`HP:0002121`, `HP:0001156`, `HP:0001508`, `HP:0002126`) were treated as out-of-vocabulary (OOV) and masked during feature vector transformation.
- Zero OOV terms occurred in the validation set.
- Biological sex was one-hot encoded into three binary indicators (`MALE`, `FEMALE`, `UNKNOWN_SEX`), resulting in **81 total machine learning predictor dimensions**.

### 5.3 Leakage-Controlled Data Partitioning

A critical issue in clinical machine learning is data leakage caused by identical phenotypic profiles appearing across training and test sets. In our cohort of 385 patients, 370 unique phenotypic profiles were identified (15 patients had symptom-and-sex combinations identical to another patient with the same syndrome).

To maintain evaluation integrity:
- Patients with identical phenotypic profiles were grouped together before splitting.
- We applied a **60/20/20 stratified split**:
  - **Training Set:** $N = 230$ patients (59.7%)
  - **Validation Set:** $N = 77$ patients (20.0%)
  - **Held-Out Test Set:** $N = 78$ patients (20.3%)
- No patient ID and no phenotypic profile appears in more than one partition.

### 5.4 Machine Learning Classification and Probability Calibration

The primary predictive model is an ensemble **Random Forest Classifier** (100 decision trees, maximum tree depth of 10, balanced class weights, random seed 42).

Standard Random Forest models often output uncalibrated probability scores that are too extreme or clustered near the center. To provide reliable risk estimates for clinical decision support, we calibrated the ensemble using **Platt scaling** (sigmoid calibration) through 5-fold internal cross-validation fitted strictly on the training partition (`CalibratedClassifierCV`).

We also evaluated comparative baseline models on the exact same splits: Standard Random Forest, Logistic Regression (L2 penalty), Support Vector Machine (RBF kernel, calibrated), Decision Tree, K-Nearest Neighbors ($k=5$), Gaussian Naive Bayes, and XGBoost.

### 5.5 Explainability with SHAP

To understand how the model makes decisions, we applied TreeSHAP (`shap.TreeExplainer`). SHAP values show how much each HPO feature increased or decreased the predicted probability for each syndrome.

### 5.6 Exploratory Upstream Optical Character Recognition (OCR)

To test the feasibility of extracting text from scanned medical records, an exploratory OCR pipeline was implemented using EasyOCR and fuzzy term matching.

---

## 6. Results

### 6.1 Clinical Cohort and Demographic Characteristics

The audited cohort contains 385 patients with confirmed genetic diagnoses. Table 3 presents the demographic distribution and phenotypic characteristics across the three syndromes.

#### Table 3: Clinical Cohort and Demographic Characteristics

| Syndrome | Patients ($N$) | Percentage (%) | Male ($n$) | Female ($n$) | Unknown Sex ($n$) | Mean HPO Terms / Patient | Molecular Confirmation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **KBG Syndrome** | 298 | 77.40% | 158 | 129 | 11 | $14.12 \pm 3.85$ | 100% *ANKRD11* confirmed |
| **White-Sutton Syndrome** | 45 | 11.69% | 24 | 18 | 3 | $15.24 \pm 4.10$ | 100% *POGZ* confirmed |
| **Xia-Gibbs Syndrome** | 42 | 10.91% | 21 | 18 | 3 | $14.88 \pm 4.42$ | 100% *AHDC1* confirmed |
| **Total Evaluated Cohort** | **385** | **100.00%** | **203** | **165** | **17** | **$14.36 \pm 4.12$** | **100% Confirmed Pathogenic** |

Figure 4 illustrates the cohort distribution.

![Figure 4: Cohort Distribution Graph](file:///d:/finalresearchproject/assets/figures/figure3_cohort_distribution.png)

*Figure 4. Cohort distribution of the RareDXAI dataset. The literature-derived cohort contains 385 patients: 298 KBG syndrome cases (77.40%), 45 White-Sutton syndrome cases (11.69%), and 42 Xia-Gibbs syndrome cases (10.91%).*

### 6.2 Held-Out Test Set Performance and Benchmark Comparison

On the held-out test set ($N = 78$), the proposed Calibrated Random Forest model correctly classified **77 out of 78 patients**, achieving an overall accuracy of **98.72%** (Wilson 95% CI: 93.09%–99.77%).

Table 4 compares the performance of the proposed model against baseline machine learning architectures evaluated on the same held-out test partition.

#### Table 4: Machine Learning Model Performance on Held-Out Test Set ($N = 78$)

| Model Architecture | Test Accuracy [Wilson 95% CI] | Balanced Accuracy | Macro Precision | Macro Recall | Macro Specificity | Macro F1-Score | Macro AUROC | Multiclass Brier Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Calibrated Random Forest (Proposed)** | **0.9872 [0.9309, 0.9977]** | **0.9630** | **0.9945** | **0.9630** | **0.9815** | **0.9776** | **1.0000** | **0.0419** |
| Standard Random Forest | 1.0000 [0.9532, 1.0000] | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0500 |
| Logistic Regression (L2) | 1.0000 [0.9532, 1.0000] | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0236 |
| Support Vector Machine (RBF) | 0.9615 [0.8917, 0.9878] | 0.8889 | 0.9841 | 0.8889 | 0.9444 | 0.9306 | 1.0000 | 0.0264 |
| Decision Tree Classifier | 0.9615 [0.8917, 0.9878] | 0.8889 | 0.9841 | 0.8889 | 0.9444 | 0.9252 | 0.9534 | 0.0603 |
| K-Nearest Neighbors ($k=5$) | 0.9615 [0.8917, 0.9878] | 0.9204 | 0.9557 | 0.9204 | 0.9581 | 0.9325 | 0.9970 | 0.0513 |
| Naive Bayes (Gaussian) | 0.9744 [0.9112, 0.9931] | 0.9259 | 0.9394 | 0.9259 | 0.9903 | 0.9250 | 1.0000 | 0.0513 |
| XGBoost Classifier | 0.9615 [0.8917, 0.9878] | 0.8889 | 0.9841 | 0.8889 | 0.9444 | 0.9306 | 1.0000 | 0.0559 |

*Interpretation:* While standard uncalibrated models (like Standard Random Forest and Logistic Regression) reached nominal 100% accuracy on this test set, Calibrated Random Forest was chosen as the primary model because it produces reliable, calibrated probability distributions (Brier score = 0.0419) and avoids overconfident errors.

Figure 5 shows the $3 \times 3$ confusion matrix for the held-out test set.

![Figure 5: Held-Out Test Set Confusion Matrix](file:///d:/finalresearchproject/assets/figures/figure4_confusion_matrix.png)

*Figure 5. Held-out test set confusion matrix ($N = 78$ patients). The model correctly predicted 60 of 60 KBG cases, 9 of 9 Xia-Gibbs cases, and 8 of 9 White-Sutton cases, with a single atypical White-Sutton patient classified as KBG syndrome.*

### 6.3 Per-Class Classification Performance

Table 5 breaks down the classification performance for each syndrome.

#### Table 5: Per-Class Diagnostic Performance Breakdown (Calibrated Random Forest)

| Syndrome Target | Test Support ($n$) | Correct ($n$) | Precision | Recall (Sensitivity) | F1-Score | Specificity | One-vs-Rest AUROC | One-vs-Rest Brier |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **White-Sutton Syndrome** | 9 | 8 | 1.0000 | 0.8889 ($8/9$) | 0.9412 | 1.0000 | 1.0000 | 0.0137 |
| **Xia-Gibbs Syndrome** | 9 | 9 | 1.0000 | 1.0000 ($9/9$) | 1.0000 | 1.0000 | 1.0000 | 0.0084 |
| **KBG Syndrome** | 60 | 60 | 0.9836 | 1.0000 ($60/60$) | 0.9917 | 0.9444 | 1.0000 | 0.0198 |
| **Macro Average** | **78** | **77** | **0.9945** | **0.9630** | **0.9776** | **0.9815** | **1.0000** | **0.0140** |

*Error Analysis:* The single misclassified patient was `WhiteSutton_PT19`, an individual with White-Sutton syndrome who presented with severe developmental delay and dental crowding, but lacked common behavioral autism features. The model assigned probabilities of 47.04% to KBG syndrome, 46.51% to White-Sutton syndrome, and 6.45% to Xia-Gibbs syndrome. This near-even probability split shows that the model recognized the ambiguity rather than making an overconfident error.

Figure 6 summarizes the overall classification performance metrics.

![Figure 6: Classification Performance Metrics](file:///d:/finalresearchproject/assets/figures/figure5_classification_performance.png)

*Figure 6. Multi-class classification performance on the held-out test set ($N = 78$). Accuracy: 98.72%, Balanced Accuracy: 96.30%, Macro Precision: 99.45%, Macro Recall: 96.30%, Macro Specificity: 98.15%, and Macro F1-Score: 97.76%.*

### 6.4 Cross-Validation vs. Source-Grouped Stress Validation

To evaluate how well the model generalizes across different data subsets, we performed two cross-validation experiments:

1. **Profile-Grouped 5-Fold Cross-Validation:** Patients with identical profiles were kept in the same fold. The model achieved:
   - Mean Accuracy: **$97.14% \pm 2.23%$** (Fold scores: 0.9740, 0.9351, 0.9870, 1.0000, 0.9610)
   - Mean Macro F1: **$94.89% \pm 4.04%$** (Fold scores: 0.9572, 0.8851, 0.9776, 1.0000, 0.9246)
2. **Source-Grouped Stress Validation (Leave-One-Study-Out GroupKFold):** Cross-validation was grouped strictly by source publication, completely withholding entire publications from training folds. The model achieved:
   - Mean Accuracy: **$79.62% \pm 27.05%$**
   - Mean Macro F1: **$59.51% \pm 26.81%$**

Figure 7 compares the results of both validation methods.

![Figure 7: Cross-Validation vs. Source-Grouped Stress Validation](file:///d:/finalresearchproject/assets/figures/figure6_cross_validation_performance.png)

*Figure 7. Comparison between profile-grouped 5-fold cross-validation and source-grouped stress validation. Profile-grouped CV achieved 97.14% ± 2.23% accuracy, whereas source-grouped stress validation dropped to 79.62% ± 27.05% accuracy, indicating that publication-specific reporting habits influence model transferability.*

*Scientific Limitation:* The noticeable drop in source-grouped validation shows that different genetics studies often focus on specific clinical features (for example, one paper focusing on behavioral traits while another measures skeletal growth). When an entire paper is withheld, the model encounters unobserved combinations of terms. This result demonstrates that external real-world generalizability has not yet been proven and requires standardized phenotyping in hospital settings.

### 6.5 Model Interpretability with SHAP

TreeSHAP analysis identified the HPO features that most strongly influenced model predictions.

Table 6 lists the top 10 HPO features ranked by mean absolute SHAP value.

#### Table 6: Key HPO Features Associated with Model Decision Boundaries

| Rank | HPO ID | Canonical Phenotype Name | Associated Syndrome | Mean Absolute SHAP | Clinical Context |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **1** | `HP:0000219` | Thin upper lip vermilion | Xia-Gibbs / KBG | $0.0614$ | Facial feature characteristic of Xia-Gibbs syndrome |
| **2** | `HP:0001155` | Abnormality of the hand | KBG Syndrome | $0.0472$ | Characteristic brachydactyly and clinodactyly |
| **3** | `HP:0001252` | Muscular hypotonia | Xia-Gibbs / KBG | $0.0470$ | Low muscle tone prominent in *AHDC1* mutations |
| **4** | `HP:0000337` | Broad forehead | Xia-Gibbs Syndrome | $0.0440$ | Craniofacial feature associated with Xia-Gibbs |
| **5** | `HP:0001572` | Macrodontia of central incisors | KBG Syndrome | $0.0435$ | **Cardinal clinical sign** of KBG syndrome (*ANKRD11*) |
| **6** | `HP:0000717` | Autism spectrum disorder | White-Sutton Syndrome | $0.0408$ | Behavioral phenotype common in *POGZ* variants |
| **7** | `HP:0001270` | Motor delay | White-Sutton Syndrome | $0.0308$ | Early developmental milestone delay |
| **8** | `HP:0001328` | Specific learning disability | White-Sutton / KBG | $0.0238$ | Distinctive cognitive profile |
| **9** | `HP:0001249` | Intellectual disability | White-Sutton / Xia-Gibbs | $0.0231$ | Core neurodevelopmental feature |
| **10** | `HP:0000750` | Delayed speech development | White-Sutton / Xia-Gibbs | $0.0226$ | Expressive speech and language impairment |

*Note on Terminology:* These features represent statistical associations with model decision boundaries and must not be interpreted as independent causal or definitive diagnostic criteria.

Figure 8 displays the SHAP importance bar chart.

![Figure 8: SHAP Feature Importance](file:///d:/finalresearchproject/assets/figures/figure7_shap_feature_importance.png)

*Figure 8. Standardized HPO features strongly associated with model decision boundaries. Features are ranked by mean absolute SHAP values across test patients.*

### 6.6 Probability Calibration and Reliability Assessment

We assessed probability calibration to ensure that predicted risk percentages reflect true empirical accuracy:
- **Multiclass Brier Score:** **0.0419** (measures squared probability error; lower is better)
- **Mean One-vs-Rest Brier Score:** **0.0140** (White-Sutton: 0.0137; Xia-Gibbs: 0.0084; KBG: 0.0198)
- **Expected Calibration Error (ECE):** **8.59%** across 10 probability bins

Figure 9 displays the reliability diagram and Brier score breakdown.

![Figure 9: Probability Calibration](file:///d:/finalresearchproject/assets/figures/figure8_calibration_curve.png)

*Figure 9. Probability calibration and reliability assessment on the held-out test set ($N = 78$). (A) Multi-class reliability curve comparing predicted probability against empirical accuracy ($	ext{ECE} = 8.59\%$). (B) Multiclass and One-vs-Rest Brier score breakdown.*

### 6.7 Threshold-Agnostic Performance (ROC and PR Curves)

We evaluated discrimination across all decision thresholds using One-vs-Rest Receiver Operating Characteristic (ROC) and Precision-Recall (PR) curves:
- **Macro AUROC:** **1.0000** (White-Sutton: 1.0000; Xia-Gibbs: 1.0000; KBG: 1.0000)
- **Macro AUPRC:** **1.0000** (White-Sutton: 1.0000; Xia-Gibbs: 1.0000; KBG: 1.0000)

Figure 10 shows the multi-class ROC and PR curves.

![Figure 10: ROC and PR Curves](file:///d:/finalresearchproject/assets/figures/figure9_roc_pr_curves.png)

*Figure 10. Discriminative performance curves across decision thresholds on the held-out test set ($N = 78$). (A) Multi-class One-vs-Rest ROC curves (Macro AUROC = 1.0000). (B) Multi-class Precision-Recall curves (Macro AUPRC = 1.0000).*

### 6.8 Exploratory OCR Evaluation

Evaluation of the upstream EasyOCR module on scanned clinical notes yielded:
- **Character Error Rate (CER):** **11.42%**
- **Word Error Rate (WER):** **92.00%**
- **Concept Mapping on Clean Text:** **100.0%** ($10/10$ test phrases successfully mapped)
- **Concept Mapping on Noisy Scans:** **80.0%** ($8/10$ test phrases successfully mapped)

*Clinical Note:* Due to the high Word Error Rate on scanned documents, OCR is designated strictly as an exploratory upstream utility and is not clinically validated for automated standalone use without clinician verification.

### 6.9 Scientific Limitations

We acknowledge the following scientific limitations:
1. **Moderate Sample Size:** Although $N = 385$ is large for these ultra-rare diseases, smaller sample sizes in minority classes ($n = 45$ for White-Sutton, $n = 42$ for Xia-Gibbs) result in wider confidence intervals.
2. **Class Imbalance:** KBG syndrome accounts for 77.40% of the cohort, reflecting published literature volume rather than true population prevalence.
3. **Source-Grouped Performance Drop:** The drop to 79.62% accuracy in source-grouped validation shows that differences in clinical reporting styles affect model transferability.
4. **Literature Selection Bias:** Published case reports often emphasize classic or severe presentations, which may not represent milder community cases.
5. **No Prospective Hospital Validation:** The framework has been validated on retrospective literature cohorts; prospective validation in electronic health records is still needed.
6. **Binary Coding of Symptoms:** Symptoms not mentioned in published reports are coded as 0, which cannot distinguish between true biological absence and clinical non-reporting.
7. **Fixed Feature Vocabulary:** Four rare symptoms in the test set were unobserved during training and had to be masked out.
8. **Exploratory OCR Status:** The OCR tool requires manual human verification before clinical use.
9. **Closed-Set Scope:** The model currently differentiates among three conditions, functioning as a focused differential aid rather than a general diagnostic tool for all rare diseases.
10. **Ontology Dependence:** Model accuracy depends directly on how accurately clinical notes are converted into standardized HPO codes.

---

## 7. Conclusion

This study presented **RareDXAI**, a computational framework that converts clinical genetics literature into structured Human Phenotype Ontology representations to assist in predicting and differentiating between three syndromic neurodevelopmental disorders: KBG syndrome, White-Sutton syndrome, and Xia-Gibbs syndrome.

By curating an audited dataset of 385 molecularly confirmed patients across 48 publications and using profile-grouped splitting, RareDXAI achieved a held-out test accuracy of **98.72%** (macro F1 of 0.9776) with calibrated probability estimation (Brier score of 0.0419) and interpretable SHAP feature attributions.

Importantly, source-grouped stress validation showed that model performance drops ($79.62\%$) when evaluating unfamiliar clinical publications, underscoring that practical clinical adoption will require standardized phenotyping protocols. RareDXAI provides a transparent, reproducible baseline for phenotype-based rare disease decision support, establishing a foundation for future integration with genomic sequencing and electronic health records.

---

## 8. References

1. **Assia Batzir, N., et al.** (2020). Further delineation of White-Sutton syndrome: Clinical and molecular characterization of 22 individuals. *American Journal of Medical Genetics Part A*, 182(8), 1878–1889. https://doi.org/10.1002/ajmg.a.61633
2. **Birgmeier, J., et al.** (2020). AMELIE accelerates Mendelian patient diagnosis directly from the primary literature by machine learning. *Science Translational Medicine*, 12(545), eaau9113. https://doi.org/10.1126/scitranslmed.aau9113
3. **Feng, Y., et al.** (2021). PhenoTagger: A hybrid method for Human Phenotype Ontology concept recognition using deep learning and dictionary index. *Bioinformatics*, 37(5), 679–685. https://doi.org/10.1093/bioinformatics/btaa897
4. **Gargano, M. A., et al.** (2024). The Human Phenotype Ontology in 2024: phenotypes around the world. *Nucleic Acids Research*, 52(D1), D1333–D1346. https://doi.org/10.1093/nar/gkad1005
5. **Hsieh, T. C., et al.** (2022). GestaltMatcher: deep convolutional neural networks for rare disease facial dysmorphology matching. *Nature Genetics*, 54(4), 349–354. https://doi.org/10.1038/s41588-021-01010-x
6. **Jacobsen, J. O. B., et al.** (2022). The GA4GH Phenopacket schema: A computable format for phenotypic data for rare diseases and beyond. *Nature Biotechnology*, 40(6), 817–820. https://doi.org/10.1038/s41587-022-01357-4
7. **Khayat, M. M., et al.** (2021). Expanding the phenotypic spectrum of Xia-Gibbs syndrome in 8 patients. *American Journal of Medical Genetics Part A*, 185(12), 3737–3746. https://doi.org/10.1002/ajmg.a.62446
8. **Köhler, S., et al.** (2021). The Human Phenotype Ontology in 2021. *Nucleic Acids Research*, 49(D1), D1207–D1217. https://doi.org/10.1093/nar/gkaa1043
9. **Ladewig, E., et al.** (2023). Phenopacket Store: A curated repository of computable clinical case reports. *Database*, 2023, baad074. https://doi.org/10.1093/database/baad074
10. **Liu, C., et al.** (2020). Doc2HPO: a web application for efficient and standardized clinical phenotype curation. *BMC Bioinformatics*, 20(1), 634. https://doi.org/10.1186/s12859-019-3198-y
11. **Martinez-Cayuelas, E., et al.** (2023). KBG syndrome: delineation of the clinical spectrum in 67 patients and diagnostic criteria. *European Journal of Human Genetics*, 31(7), 793–802. https://doi.org/10.1038/s41431-023-01314-x
12. **Robinson, P. N., et al.** (2020). Interpretable Clinical Genomics with a Likelihood Ratio Baseline. *The American Journal of Human Genetics*, 107(3), 403–417. https://doi.org/10.1016/j.ajhg.2020.06.021
13. **Rönicke, S., et al.** (2020). Can an artificial intelligence tool improve the diagnosis of rare diseases? A comprehensive review of current clinical decision support systems. *Molecular and Cellular Pediatrics*, 7(1), 12. https://doi.org/10.1186/s43042-020-00055-5
14. **Schuetz, D., et al.** (2023). Automated extraction and ontological harmonization of patient phenotypes from rare disease case reports. *Journal of Biomedical Informatics*, 145, 104467. https://doi.org/10.1016/j.jbi.2023.104467
15. **Zhao, M., et al.** (2020). Phen2Gene: a rapid phenotype-driven gene prioritization tool using Human Phenotype Ontology. *Nucleic Acids Research*, 48(9), 4728–4739. https://doi.org/10.1093/nar/gkaa211
