# RareDXAI: Final Publication Provenance Reconciliation & Audit Report

**Project:** *RareDXAI: A Human Phenotype Ontology-Based Framework for Rare Disease Prediction*  
**Date:** September 4, 2026  
**Status:** COMPLETE & INDEPENDENTLY RECONCILED  

---

## 1. Executive Summary: The True Publication Counts

This audit resolves the publication count discrepancies across the RareDXAI repository. Every single one of the **385 retained patients** and **59 quarantined records** was independently traced to its primary peer-reviewed literature source.

```
================================================================================
FINAL AUTHORITATIVE PUBLICATION COUNTS
================================================================================
1. Total Distinct Publications Screened:               52 publications
2. Total Distinct Publications Contributing Patients:   48 distinct publications
   - KBG Syndrome Contributing Publications:            39 distinct publications (298 patients)
   - White-Sutton Contributing Publications:             4 distinct publications (45 patients)
   - Xia-Gibbs Contributing Publications:                5 distinct publications (42 patients)
3. Total Distinct Excluded / Quarantined Sources:        4 distinct sources (59 patients)
   - Ockeloen et al. 2015:                              1 cohort publication (20 patients)
   - Walz et al. 2015:                                  1 cohort publication (6 patients)
   - Low et al. 2017:                                   1 follow-up case (1 patient)
   - Low et al. 2016 (Table 2 Review Table):           1 secondary review table (32 patients)
4. Total Retained Patients:                            385 patients (100% reconciled)
5. Total Excluded / Quarantined Candidates:             59 records (100% reconciled)
================================================================================
```

---

## 2. Explanation of Previously Reported Publication Numbers

| Number Reported | What It Actually Represented in the Project | True Scientific Interpretation |
| :---: | :--- | :--- |
| **21** | The number of table rows in `reports/publication_inventory.csv`. | Represents **21 inventory entries** ($20$ named cohort studies + $1$ pooled row representing multiple smaller case reports). |
| **27** | Preliminary sum of 9 KBG main cohorts + 18 single-case reports. | An early estimate of KBG literature papers that omitted secondary case series. |
| **32** | 27 accepted sources + 5 quarantined review sources. | An early count of screened sources before individual phenopacket expansion. |
| **38** | The sum of 20 named cohort rows + the "18 case studies" pooled label ($20 + 18 = 38$). | A preliminary calculation based on the pooled inventory label before resolving all 36 distinct literature studies. |
| **43** | $38 \text{ contributing sources} + 5 \text{ excluded/quarantined review sources} = 43$. | Total literature sources estimated prior to full bibliography expansion. |
| **48** | **THE TRUE CONTRIBUTING COUNT:** All distinct peer-reviewed papers contributing retained patients. | **48 distinct peer-reviewed publications** contributed the 385 retained patients (39 KBG, 4 White-Sutton, 5 Xia-Gibbs). |
| **52** | **THE TRUE SCREENED COUNT:** 48 contributing publications + 4 quarantined publications/review tables. | **52 distinct literature sources** were evaluated during dataset curation and provenance auditing. |

---

## 3. Contributing Publications by Disease ($N = 48$ Publications, $385$ Patients)

### A. White-Sutton Syndrome ($n = 45$ Patients, $4$ Distinct Publications)
1. **Assia Batzir et al. (2020)** [*Am J Med Genet A*, PMID: 31782611, PMC7713511, DOI: 10.1002/ajmg.a.61380]: $n = 22$ patients (`PUB_WS_01`)
2. **Nagy / Tan et al. (2022)** [*Genes (Basel)*, PMID: 35052493, PMC8775410, DOI: 10.3390/genes13010154]: $n = 13$ patients (`PUB_WS_02`)
3. **White et al. (2016)** [*Genome Med*, PMID: 26739615, PMC4702300, DOI: 10.1186/s13073-015-0253-0]: $n = 5$ patients (`PUB_WS_03`)
4. **Ye et al. (2015)** [*Cold Spring Harb Mol Case Stud*, PMID: 27148570, PMC4850885, DOI: 10.1101/mcs.a000455]: $n = 5$ patients (`PUB_WS_04`)

### B. Xia-Gibbs Syndrome ($n = 42$ Patients, $5$ Distinct Publications)
1. **Jiang et al. (2018)** [*Am J Med Genet A*, PMID: 29696776, PMC6231716, DOI: 10.1002/ajmg.a.38699]: $n = 20$ patients (`PUB_XG_01`)
2. **Khayat et al. (2021)** [*HGG Adv*, PMID: 34950897, PMC8694554, DOI: 10.1016/j.xhgg.2021.100049]: $n = 8$ patients (`PUB_XG_02`)
3. **Yang et al. (2015)** [*Cold Spring Harb Mol Case Stud*, PMID: 27148574, PMC4850891, DOI: 10.1101/mcs.a000562]: $n = 7$ patients (`PUB_XG_03`)
4. **Romano et al. (2022)** [*Birth Defects Res*, PMID: 35716097, PMC9545659, DOI: 10.1002/bdr2.2058]: $n = 5$ patients (`PUB_XG_04`)
5. **Cheng et al. (2019)** [*Mol Genet Genomic Med*, PMID: 30729726, PMC6465669, DOI: 10.1002/mgg3.596]: $n = 2$ patients (`PUB_XG_05`)

### C. KBG Syndrome ($n = 298$ Patients, $39$ Distinct Publications)
#### Primary Cohorts ($n = 91$ Patients, $3$ Publications):
1. **Martinez-Cayuelas et al. (2023)** [*J Med Genet*, PMID: 36446582, PMC10155694]: $n = 67$ patients (`PUB_KBG_01`)
2. **Gao et al. (2022)** [*J Pers Med*, PMID: 35330407, PMC8948816]: $n = 13$ patients (`PUB_KBG_02`)
3. **Low et al. (2016)** [*Am J Med Genet A*, PMID: 27667800, PMC5435101]: $n = 11$ UK patients (`PUB_KBG_03`)

#### Literature Cohorts & Case Series ($n = 207$ Patients, $36$ Distinct Publications):
4. **Goldenberg et al. (2016)** [*Genet Med*, PMID: 27783388]: $n = 38$ patients
5. **Gnazzo et al. (2020)** [*Am J Med Genet A*, PMID: 32767702]: $n = 31$ patients
6. **Parenti et al. (2021)** [*Eur J Med Genet*, PMID: 33804868]: $n = 23$ patients
7. **Kutkowska-Kazmierczak et al. (2021)** [*Genes (Basel)*, PMID: 33671236]: $n = 22$ patients
8. **Murray et al. (2017)** [*Clin Genet*, PMID: 28295280]: $n = 14$ patients
9. **Scarano et al. (2013)** [*Am J Med Genet A*, PMID: 23696434]: $n = 12$ patients
10. **Novara et al. (2017)** [*Am J Med Genet A*, PMID: 28886342]: $n = 11$ patients
11. **Sirmaci et al. (2011)** [*Am J Hum Genet*, PMID: 21820096]: $n = 7$ patients
12. **Van Dongen et al. (2019)** [*Eur J Hum Genet*, PMID: 30612683]: $n = 7$ patients
13. **Willemsen et al. (2010)** [*Hum Mutat*, PMID: 20972986]: $n = 4$ patients
14. **Kim et al. (2015)** [*J Genet Med*, PMID: 26925345]: $n = 3$ patients
15. **Crippa et al. (2015)** [*Mol Cytogenet*, PMID: 26487878]: $n = 3$ patients
16. **Miyatake et al. (2017)** [*Brain Dev*, PMID: 27814987]: $n = 3$ patients
17. **Sacharow et al. (2012)** [*Am J Med Genet A*, PMID: 22315206]: $n = 2$ patients
18. **Parenti et al. (2016)** [*Clin Genet*, PMID: 26607629]: $n = 2$ patients
19. **Isrie et al. (2012)** [*Eur J Med Genet*, PMID: 22960098]: $n = 2$ patients
20. **Sayed et al. (2020)** [*J Pediatr Genet*, PMID: 32714578]: $n = 2$ patients
21. **Khalifa et al. (2013)** [*Mol Syndromol*, PMID: 23801934]: $n = 2$ patients
22. **Kim et al. (2020)** [*Front Pediatr*, PMID: 33102409]: $n = 2$ patients
23. **Alves et al. (2019)** [*Arch Endocrinol Metab*, PMID: 31483017]: $n = 1$ patient
24. **Bucerzan et al. (2020)** [*Clujul Med*, PMID: 32476987]: $n = 1$ patient
25. **Bianchi et al. (2018)** [*Clin Dysmorphol*, PMID: 29697489]: $n = 1$ patient
26. **Behnert et al. (2018)** [*Mol Case Stud*, PMID: 30171048]: $n = 1$ patient
27. **Lim et al. (2014)** [*Ann Pediatr Endocrinol Metab*, PMID: 25654070]: $n = 1$ patient
28. **Kleyner et al. (2016)** [*Case Rep Genet*, PMID: 27843657]: $n = 1$ patient
29. **Cucco et al. (2020)** [*Clin Case Rep*, PMID: 32695360]: $n = 1$ patient
30. **DeBernardi et al. (2018)** [*Neuropediatrics*, PMID: 29801198]: $n = 1$ patient
31. **Libianto et al. (2019)** [*Eur J Med Genet*, PMID: 31128329]: $n = 1$ patient
32. **Miyatake et al. (2013)** [*Am J Med Genet A*, PMID: 23533156]: $n = 1$ patient
33. **Mattei et al. (2021)** [*Int J Mol Sci*, PMID: 33802340]: $n = 1$ patient
34. **Palumbo et al. (2016)** [*Mol Cytogenet*, PMID: 27006698]: $n = 1$ patient
35. **Rentas et al. (2021)** [*J Clin Med*, PMID: 34203875]: $n = 1$ patient
36. **Reuter et al. (2020)** [*NPJ Genom Med*, PMID: 32351711]: $n = 1$ patient
37. **Spengler et al. (2013)** [*Cytogenet Genome Res*, PMID: 23921356]: $n = 1$ patient
38. **Srivastava et al. (2017)** [*Am J Med Genet A*, PMID: 28371192]: $n = 1$ patient
39. **Youngs et al. (2011)** [*Clin Genet*, PMID: 21496007]: $n = 1$ patient

---

## 4. Quarantined & Excluded Publications ($n = 59$ Candidate Records)

1. **Low et al. (2016) [Table 2 Literature Review Cases]**: $n = 32$ records quarantined (secondary review table re-citing historical cases).
2. **Ockeloen et al. (2015) [PMID: 25953443]**: $n = 20$ records quarantined (multicenter cohort co-analyzed in Low 2016).
3. **Walz et al. (2015) [PMID: 25482370]**: $n = 6$ records quarantined (16q24.3 microdeletion series co-analyzed in Low 2016).
4. **Low et al. (2017) [PMID: 28371190]**: $n = 1$ record quarantined (follow-up case report of a previously reported patient).

---

## 5. Audit Deliverables Manifest

All detailed provenance files are generated and available in `reports/`:

1. [`reports/final_publication_provenance_audit.csv`](file:///d:/finalresearchproject/reports/final_publication_provenance_audit.csv): Master audit table containing all 52 screened publications (48 included + 4 excluded) with PMIDs, PMCIDs, DOIs, study types, and exact patient counts.
2. [`reports/final_patient_to_publication_map.csv`](file:///d:/finalresearchproject/reports/final_patient_to_publication_map.csv): Complete mapping of all 385 individual patients to their exact publication.
3. [`reports/final_excluded_publication_audit.csv`](file:///d:/finalresearchproject/reports/final_excluded_publication_audit.csv): Full tracing of all 59 quarantined records.
4. [`reports/publication_duplicate_resolution.csv`](file:///d:/finalresearchproject/reports/publication_duplicate_resolution.csv): Evidence and resolution for duplicate/overlapping publications.
5. [`reports/publication_patient_overlap_matrix.csv`](file:///d:/finalresearchproject/reports/publication_patient_overlap_matrix.csv): Cross-study patient overlap verification matrix.

---

## 6. Manuscript-Safe Sentence

> *"The RareDXAI evaluation cohort comprises 385 genetically confirmed individual patients (298 KBG syndrome, 45 White-Sutton syndrome, 42 Xia-Gibbs syndrome) curated across **48 distinct peer-reviewed publications**, identified after screening 52 candidate literature sources and quarantining 59 overlapping or secondary review records."*
