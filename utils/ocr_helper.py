import os
import re
import json
import sys
import easyocr
import numpy as np
from config import system_config
from utils import logger

# Ensure stdout/stderr uses UTF-8 encoding on Windows to prevent charmap encoding errors
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

log = logger.get_logger("ocr_helper")

# Cache the EasyOCR reader instance
_reader = None

def get_ocr_reader():
    global _reader
    if _reader is None:
        log.info("Initializing EasyOCR Reader (verbose=False)...")
        # Disable GPU if PyTorch CUDA is not available
        import torch
        use_gpu = torch.cuda.is_available()
        _reader = easyocr.Reader(['en'], gpu=use_gpu, verbose=False)
    return _reader

def clean_extracted_text(text: str) -> str:
    """
    Removes common metadata headers (e.g. name, date, doctor, phone) from the OCR text.
    """
    lines = text.split('\n')
    cleaned_lines = []
    
    ignore_patterns = [
        r"(patient\s+name|name)\s*:\s*.*",
        r"(doctor|physician|clinician)\s*:\s*.*",
        r"(date|dob)\s*:\s*.*",
        r"(phone|tel|mobile)\s*:\s*.*",
        r"(hospital|clinic|medical\s+center)\s*:\s*.*",
        r"(bill|invoice|registration|reg|case|id)\s+(number|no|#)\s*:\s*.*",
        r"\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b",
        r"\b\d{10}\b",
    ]
    
    for line in lines:
        temp = line.strip()
        if not temp:
            continue
            
        is_meta = False
        for pattern in ignore_patterns:
            if re.search(pattern, temp, re.IGNORECASE):
                is_meta = True
                break
                
        if not is_meta:
            cleaned_lines.append(temp)
            
    return "\n".join(cleaned_lines)

def load_hpo_synonyms(vocab_path: str = None, obo_path: str = None):
    """
    Loads vocab and hp.obo to return a dictionary mapping HPO ID -> { 'name': str, 'keywords': list }.
    """
    if vocab_path is None:
        vocab_path = os.path.join(system_config.PREPROC_ARTIFACTS_DIR, "hpo_feature_vocabulary.json")
    if obo_path is None:
        obo_path = os.path.join(system_config.RAW_DATA_DIR, "hp.obo")
        
    if not os.path.exists(vocab_path):
        log.error("Vocabulary file not found.")
        return {}
        
    with open(vocab_path, "r", encoding="utf-8") as f:
        vocab = set(json.load(f))
        
    hpo_synonyms = {}
    
    if not os.path.exists(obo_path):
        log.warning("hp.obo not found. Synonym matching falls back to basic name mapping.")
        return {}
        
    with open(obo_path, "r", encoding="utf-8") as f:
        in_term = False
        term_id = None
        term_name = None
        synonyms = []
        alt_ids = []
        
        for line in f:
            line = line.strip()
            if line == "[Term]":
                if in_term and term_id:
                    matched_id = None
                    if term_id in vocab:
                        matched_id = term_id
                    else:
                        for a_id in alt_ids:
                            if a_id in vocab:
                                matched_id = a_id
                                break
                    if matched_id:
                        hpo_synonyms[matched_id] = {
                            "name": term_name,
                            "keywords": list(set([term_name.lower()] + [s.lower() for s in synonyms]))
                        }
                in_term = True
                term_id = None
                term_name = None
                synonyms = []
                alt_ids = []
            elif in_term:
                if line.startswith("id:"):
                    term_id = line.split("id:")[1].strip()
                elif line.startswith("name:"):
                    term_name = line.split("name:")[1].strip()
                elif line.startswith("alt_id:"):
                    alt_ids.append(line.split("alt_id:")[1].strip())
                elif line.startswith("synonym:"):
                    match = re.search(r'"([^"]+)"', line)
                    if match:
                        synonyms.append(match.group(1))
                        
        # Add the last term
        if in_term and term_id:
            matched_id = None
            if term_id in vocab:
                matched_id = term_id
            else:
                for a_id in alt_ids:
                    if a_id in vocab:
                        matched_id = a_id
                        break
            if matched_id:
                hpo_synonyms[matched_id] = {
                    "name": term_name,
                    "keywords": list(set([term_name.lower()] + [s.lower() for s in synonyms]))
                }
                
    # Fill in any missing vocab terms
    from preprocessing import data_loader
    hpo_map = data_loader.parse_hpo_obo(obo_path)
    for v_id in vocab:
        if v_id not in hpo_synonyms:
            name = hpo_map.get(v_id, "Unknown phenotypic feature")
            hpo_synonyms[v_id] = {
                "name": name,
                "keywords": [name.lower()]
            }
            
    return hpo_synonyms

SPELLING_CORRECTIONS = {
    "deleyed": "delayed",
    "bchanoral": "behavioral",
    "chtef": "chief",
}

CLINICAL_SYNONYMS = {
    "child not speaking clearly": ("HP:0000750", "Delayed speech and language development"),
    "delayed speech": ("HP:0000750", "Delayed speech and language development"),
    "speech delay": ("HP:0000750", "Delayed speech and language development"),
    
    "muscle tone decreased": ("HP:0001252", "Hypotonia"),
    "decreased muscle tone": ("HP:0001252", "Hypotonia"),
    "hypotonia": ("HP:0001252", "Hypotonia"),
    
    "poor eye contact": ("HP:0012760", "Reduced social responsiveness"),
    "prefers to be alone": ("HP:0012760", "Reduced social responsiveness"),
    "social interaction abnormality": ("HP:0012760", "Reduced social responsiveness"),
    "reduced social responsiveness": ("HP:0012760", "Reduced social responsiveness"),
    
    "behavioral issues": ("HP:0000729", "Autistic behavior"),
    "behavioral abnormality": ("HP:0000729", "Autistic behavior"),
    "autistic behavior": ("HP:0000729", "Autistic behavior"),
}

PROTECTED_IGNORE_WORDS = {
    "male", "female", "years", "months", "address", "hospital", "doctor",
    "department", "uhid", "date", "patient", "name", "age", "sex", "city",
    "state", "country", "phone", "email", "registration", "id", "pediatrics",
    "chief", "complaints", "clinical", "notes"
}

NEGATION_KEYWORDS = {"no", "not", "absent", "negative", "denies", "none", "without"}

def extract_and_map_text(text: str, hpo_synonyms: dict):
    """
    Completely redesigned OCR-to-HPO pipeline:
    1. Document Structure Detection
    2. Section Filtering (only process clinical sections)
    3. Ignore demographic/administrative fields
    4. Clinical Entity Extraction (Ignore protected words list)
    5. Clinical Phrase Normalization
    6. HPO Mapping (Search only normalized concepts)
    7. Collect Rejections for verification panel.
    """
    import difflib
    raw_lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # ----------------- SECTION DEFINITIONS -----------------
    clinical_sections = {
        "chief complaints", "clinical notes", "history of present illness", 
        "symptoms", "neurological findings", "developmental findings", 
        "behavioural findings", "physical examination", "clinical findings",
        "developmental history", "behavioural assessment"
    }
    
    ignored_sections = {
        "patient information", "administrative information", "past history",
        "assessment", "diagnosis", "advice", "prescription", "medications",
        "doctor", "hospital", "department", "billing", "demographics"
    }
    
    demographic_keys = {
        "age", "sex", "address", "city", "state", "country", "blood group", 
        "height", "weight", "dob", "gender"
    }
    
    administrative_keys = {
        "patient name", "name", "doctor name", "doctor", "hospital name", 
        "hospital", "department", "uhid", "registration number", "registration", 
        "phone", "email", "date", "bill", "invoice", "case id", "id"
    }
    
    # ----------------- PIPELINE EXECUTION -----------------
    ignored_demographics = []
    ignored_administrative = []
    rejected_non_clinical = []
    clinical_entities = []
    
    current_section = "general" # State machine tracking active section context
    
    for line in raw_lines:
        line_lower = line.lower()
        
        # Check if line is a section header
        is_header = False
        clean_header = re.sub(r'[^\w\s]', '', line_lower).strip()
        
        if clean_header in clinical_sections:
            current_section = "clinical"
            is_header = True
        elif clean_header in ignored_sections:
            current_section = "ignored"
            is_header = True
            
        if is_header:
            rejected_non_clinical.append({
                "phrase": line,
                "reason": "Section header (ignored/administrative)",
                "target": "Ignored"
            })
            continue
            
        # Segment key-value metadata fields
        is_metadata = False
        # Match pattern "Key : Value"
        match_kv = re.match(r'^([^:]+)\s*:\s*(.*)$', line)
        if match_kv:
            key_part = match_kv.group(1).strip().lower()
            val_part = match_kv.group(2).strip()
            
            # Check key against demographic keywords
            is_dem = any(dk in key_part for dk in demographic_keys) or (key_part == "age" or key_part == "sex")
            if is_dem:
                ignored_demographics.append(line)
                is_metadata = True
                rejected_non_clinical.append({
                    "phrase": line,
                    "reason": "Demographic key-value field",
                    "target": "Ignored"
                })
                
            # Check key against administrative keywords
            if not is_metadata:
                is_adm = any(ak in key_part for ak in administrative_keys)
                if is_adm:
                    ignored_administrative.append(line)
                    is_metadata = True
                    rejected_non_clinical.append({
                        "phrase": line,
                        "reason": "Administrative key-value field",
                        "target": "Ignored"
                    })
                    
        if is_metadata:
            continue
            
        # Check if line contains demographic/administrative keywords globally
        cleaned_words = set(re.sub(r'[^\w\s]', ' ', line_lower).split())
        if cleaned_words and cleaned_words.issubset(PROTECTED_IGNORE_WORDS):
            rejected_non_clinical.append({
                "phrase": line,
                "reason": "Demographic / Administrative ignored terms",
                "target": "Ignored"
            })
            continue
            
        # Check if current active section is a valid clinical section
        if current_section != "clinical" and current_section != "general":
            rejected_non_clinical.append({
                "phrase": line,
                "reason": "Non-clinical document section",
                "target": "Ignored"
            })
            continue
            
        # Negation Detection
        is_negated = False
        neg_word = None
        for neg in NEGATION_KEYWORDS:
            if re.search(r'\b' + re.escape(neg) + r'\b', line_lower):
                is_negated = True
                neg_word = neg
                break
                
        if is_negated:
            rejected_non_clinical.append({
                "phrase": line,
                "reason": f"Negated clinical finding (detected '{neg_word}')",
                "target": "Rejected"
            })
            continue
            
        # Valid clinical entity candidate extracted
        clinical_entities.append(line)
        
    # ----------------- CLINICAL PHRASE NORMALIZATION & HPO MAPPING -----------------
    import difflib
    
    # Build a lookup index of all synonyms (HPO + Clinical synonyms)
    exact_synonym_map = {} # lowercase_kw -> list of (hpo_id, name)
    
    # 1. Add standard HPO synonyms
    for hpo_id, info in hpo_synonyms.items():
        name = info["name"]
        for kw in info["keywords"]:
            kw_clean = kw.lower().strip()
            if kw_clean not in exact_synonym_map:
                exact_synonym_map[kw_clean] = []
            exact_synonym_map[kw_clean].append((hpo_id, name))
            
    # 2. Add clinical synonyms
    for clin_phrase, (hpo_id, name) in CLINICAL_SYNONYMS.items():
        clin_clean = clin_phrase.lower().strip()
        if clin_clean not in exact_synonym_map:
            exact_synonym_map[clin_clean] = []
        if (hpo_id, name) not in exact_synonym_map[clin_clean]:
            exact_synonym_map[clin_clean].append((hpo_id, name))
            
    # Determine maximum synonym length (in words)
    max_synonym_len = 1
    for kw in exact_synonym_map.keys():
        w_count = len(kw.split())
        if w_count > max_synonym_len:
            max_synonym_len = w_count
            
    mapped_terms = {}
    unmatched_lines = []
    
    # Print header for debug output
    print("\n--- PHRASE-BASED EXTRACTION PIPELINE DEBUG OUTPUT ---")
    log.info("Running phrase-based extraction...")
    
    for orig_line in clinical_entities:
        # Strict pre-matching demographic and administrative context filter
        demographic_admin_words = {
            "male", "female", "years", "months", "address", "hospital", "doctor",
            "department", "uhid", "date", "patient", "name", "age", "sex", "city",
            "state", "country", "phone", "email", "registration", "id", "pediatrics",
            "height", "weight", "gender", "dob"
        }
        orig_words = set(re.sub(r'[^\w\s]', ' ', orig_line.lower()).split())
        contains_demo_admin = orig_words.intersection(demographic_admin_words)
        
        if contains_demo_admin:
            rejected_non_clinical.append({
                "phrase": orig_line,
                "reason": "Rejected match: clinical mapping contains demographic/administrative context",
                "target": "Rejected Match"
            })
            continue
            
        # Normalize: lowercase, remove punctuation, spelling corrections, and split into tokens
        line_lower = orig_line.lower()
        cleaned = re.sub(r'[^\w\s]', ' ', line_lower)
        words = cleaned.split()
        corrected_words = [SPELLING_CORRECTIONS.get(w, w) for w in words]
        
        if not corrected_words:
            continue
            
        # Generate contiguous n-grams (1 to max_synonym_len)
        line_ngrams = []
        for n in range(1, min(max_synonym_len, len(corrected_words)) + 1):
            for i in range(len(corrected_words) - n + 1):
                ngram_tokens = corrected_words[i : i + n]
                ngram_str = " ".join(ngram_tokens).strip()
                if ngram_str:
                    line_ngrams.append(ngram_str)
                    
        # Debug Output for generated n-grams
        print(f"\nOriginal clinical phrase: '{orig_line}'")
        print(f"Generated n-grams ({len(line_ngrams)} total): {line_ngrams}")
        
        line_exact_matches = []
        line_fuzzy_matches = []
        line_unmatched = []
        
        for ngram in line_ngrams:
            # 1. Exact match lookup
            if ngram in exact_synonym_map:
                for hpo_id, name in exact_synonym_map[ngram]:
                    # Post-matching failsafe check for HP:0000050
                    if hpo_id == "HP:0000050":
                        rejected_non_clinical.append({
                            "phrase": orig_line,
                            "reason": "Strict rejection: HP:0000050 blocked from demographic OCR line",
                            "target": "Rejected Match"
                        })
                        continue
                        
                    match_info = {
                        "hpo_id": hpo_id,
                        "name": name,
                        "matched_synonym": ngram,
                        "confidence": 100,
                        "type": "Exact"
                    }
                    line_exact_matches.append(match_info)
            else:
                # 2. Fuzzy match lookup
                best_match_kw = None
                best_ratio = 0.0
                for kw in exact_synonym_map.keys():
                    # Optimization: Skip comparing strings with large length differences
                    if abs(len(kw) - len(ngram)) > max(5, int(len(ngram) * 0.3)):
                        continue
                    ratio = difflib.SequenceMatcher(None, ngram, kw).ratio()
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_match_kw = kw
                        
                if best_match_kw and best_ratio >= 0.8:
                    confidence = int(best_ratio * 100)
                    for hpo_id, name in exact_synonym_map[best_match_kw]:
                        # Post-matching failsafe check for HP:0000050
                        if hpo_id == "HP:0000050":
                            rejected_non_clinical.append({
                                "phrase": orig_line,
                                "reason": "Strict rejection: HP:0000050 blocked from demographic OCR line",
                                "target": "Rejected Match"
                            })
                            continue
                            
                        match_info = {
                            "hpo_id": hpo_id,
                            "name": name,
                            "matched_synonym": best_match_kw,
                            "confidence": confidence,
                            "type": "Fuzzy"
                        }
                        line_fuzzy_matches.append(match_info)
                else:
                    line_unmatched.append(ngram)
                    
        # Deduplicate and register matches into global mapped_terms
        # Filter duplicates: keep the highest confidence match for each HPO ID
        all_line_matches = line_exact_matches + line_fuzzy_matches
        
        # Display debug output lists
        print(f"Exact matches: {[m['hpo_id'] + ' (' + m['name'] + ')' for m in line_exact_matches]}")
        print(f"Fuzzy matches: {[m['hpo_id'] + ' (' + m['name'] + ', ratio=' + str(m['confidence']) + '%)' for m in line_fuzzy_matches]}")
        print(f"Unmatched phrases: {line_unmatched}")
        
        if all_line_matches:
            for match in all_line_matches:
                hpo_id = match["hpo_id"]
                name = match["name"]
                confidence = match["confidence"]
                matched_synonym = match["matched_synonym"]
                
                if hpo_id not in mapped_terms or confidence > mapped_terms[hpo_id]["confidence"]:
                    mapped_terms[hpo_id] = {
                        "name": name,
                        "matched_phrase": orig_line,
                        "matched_synonym": matched_synonym,
                        "confidence": confidence
                    }
        else:
            unmatched_lines.append(orig_line)
            
    print("----------------------------------------------------\n")
    return mapped_terms, unmatched_lines, ignored_demographics, ignored_administrative, rejected_non_clinical


def extract_and_map_ocr_text(text: str, hpo_synonyms: dict):
    """
    Advanced Medical NLP pipeline for OCR symptom extraction.
    1. Normalizes OCR text (lowercase, preserves medical abbreviations, normalizes whitespace).
    2. Sentence segmentation (splits by period, newline, semicolon, bullet points, etc.).
    3. Handles negation context detection.
    4. Categorizes and filters out demographic/administrative information.
    5. Extracts candidate n-grams (1 to max synonym length).
    6. Maps candidate n-grams to HPO IDs using exact matching, synonym dictionary, and character TF-IDF cosine similarity.
    7. Removes duplicate HPO IDs.
    """
    import difflib
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    # ----------------- SECTION DEFINITIONS -----------------
    clinical_sections = {
        "chief complaints", "clinical notes", "history of present illness", 
        "symptoms", "neurological findings", "developmental findings", 
        "behavioural findings", "physical examination", "clinical findings",
        "developmental history", "behavioural assessment"
    }
    
    ignored_sections = {
        "patient information", "administrative information", "past history",
        "assessment", "diagnosis", "advice", "prescription", "medications",
        "doctor", "hospital", "department", "billing", "demographics"
    }
    
    demographic_keys = {
        "age", "sex", "address", "city", "state", "country", "blood group", 
        "height", "weight", "dob", "gender"
    }
    
    administrative_keys = {
        "patient name", "name", "doctor name", "doctor", "hospital name", 
        "hospital", "department", "uhid", "registration number", "registration", 
        "phone", "email", "date", "bill", "invoice", "case id", "id"
    }
    
    # Split text into lines/sentences based on newlines, periods, semicolons
    raw_sentences = []
    for segment in re.split(r'[.\n;\?!•\-\*]+', text):
        clean_segment = segment.strip()
        if clean_segment:
            raw_sentences.append(clean_segment)
            
    ignored_demographics = []
    ignored_administrative = []
    rejected_non_clinical = []
    clinical_sentences = []
    
    current_section = "general"
    
    for sentence in raw_sentences:
        sent_lower = sentence.lower()
        
        # Check section header
        clean_header = re.sub(r'[^\w\s]', '', sent_lower).strip()
        if clean_header in clinical_sections:
            current_section = "clinical"
            rejected_non_clinical.append({
                "phrase": sentence,
                "reason": "Clinical Section Header",
                "target": "Ignored"
            })
            continue
        elif clean_header in ignored_sections:
            current_section = "ignored"
            rejected_non_clinical.append({
                "phrase": sentence,
                "reason": "Ignored Section Header",
                "target": "Ignored"
            })
            continue
            
        # Key-Value metadata check
        is_metadata = False
        match_kv = re.match(r'^([^:]+)\s*:\s*(.*)$', sentence)
        if match_kv:
            key_part = match_kv.group(1).strip().lower()
            
            is_dem = any(dk in key_part for dk in demographic_keys) or (key_part == "age" or key_part == "sex")
            if is_dem:
                ignored_demographics.append(sentence)
                is_metadata = True
                rejected_non_clinical.append({
                    "phrase": sentence,
                    "reason": "Demographic Field",
                    "target": "Ignored"
                })
                
            is_adm = any(ak in key_part for ak in administrative_keys)
            if not is_metadata and is_adm:
                ignored_administrative.append(sentence)
                is_metadata = True
                rejected_non_clinical.append({
                    "phrase": sentence,
                    "reason": "Administrative Field",
                    "target": "Ignored"
                })
                
        if is_metadata:
            continue
            
        # Global word check for demographic/administrative text
        cleaned_words = set(re.sub(r'[^\w\s]', ' ', sent_lower).split())
        if cleaned_words and cleaned_words.issubset(PROTECTED_IGNORE_WORDS):
            rejected_non_clinical.append({
                "phrase": sentence,
                "reason": "Administrative/Demographic Keywords",
                "target": "Ignored"
            })
            continue
            
        if current_section == "ignored":
            rejected_non_clinical.append({
                "phrase": sentence,
                "reason": "In Ignored Section",
                "target": "Ignored"
            })
            continue
            
        clinical_sentences.append(sentence)
        
    # Build exact & synonym mapping index
    exact_synonym_map = {} # lowercase_kw -> list of (hpo_id, name)
    
    # 1. HPO Synonyms
    for hpo_id, info in hpo_synonyms.items():
        name = info["name"]
        for kw in info["keywords"]:
            kw_clean = kw.lower().strip()
            if kw_clean not in exact_synonym_map:
                exact_synonym_map[kw_clean] = []
            exact_synonym_map[kw_clean].append((hpo_id, name))
            
    # 2. Clinical Synonyms
    for clin_phrase, (hpo_id, name) in CLINICAL_SYNONYMS.items():
        clin_clean = clin_phrase.lower().strip()
        if clin_clean not in exact_synonym_map:
            exact_synonym_map[clin_clean] = []
        if (hpo_id, name) not in exact_synonym_map[clin_clean]:
            exact_synonym_map[clin_clean].append((hpo_id, name))
            
    # Max synonym length
    max_synonym_len = 1
    for kw in exact_synonym_map.keys():
        w_count = len(kw.split())
        if w_count > max_synonym_len:
            max_synonym_len = w_count
            
    # Setup TF-IDF Vectorizer for Semantic Similarity (Stage 3)
    synonym_list = list(exact_synonym_map.keys())
    tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
    tfidf_matrix = tfidf.fit_transform(synonym_list)
    
    mapped_terms = {}
    unmatched_lines = []
    
    # Keep track of debug outputs
    extracted_clinical_entities = []
    
    negation_keywords = {"no", "not", "absent", "denies", "none", "without", "negative", "never"}
    
    print("\n--- ADVANCED MEDICAL NLP OCR PIPELINE DEBUG ---")
    log.info("Running Advanced Medical NLP OCR extraction...")
    
    for sentence in clinical_sentences:
        sent_lower = sentence.lower().strip()
        
        # Negation Detection
        # Check if any negation keyword is present in the sentence
        is_negated = False
        neg_word = None
        for neg in negation_keywords:
            if re.search(r'\b' + re.escape(neg) + r'\b', sent_lower):
                is_negated = True
                neg_word = neg
                break
                
        # Normalize sentence text: keep only alphanumeric and space (to preserve medical abbreviations)
        # We strip punctuation but keep alphanumeric tokens intact
        cleaned_sent = re.sub(r'[^\w\s]', ' ', sent_lower)
        tokens = [SPELLING_CORRECTIONS.get(w, w) for w in cleaned_sent.split() if w]
        
        if not tokens:
            continue
            
        # Generate contiguous n-grams from 1 up to max_synonym_len
        ngrams = []
        for n in range(1, min(max_synonym_len, len(tokens)) + 1):
            for i in range(len(tokens) - n + 1):
                ngram_str = " ".join(tokens[i : i + n]).strip()
                if ngram_str:
                    ngrams.append(ngram_str)
                    
        print(f"\nSentence: '{sentence}'")
        if is_negated:
            print(f"  [NEGATION DETECTED via '{neg_word}'] - Skipping HPO mapping for this sentence.")
            rejected_non_clinical.append({
                "phrase": sentence,
                "reason": f"Negated sentence (detected '{neg_word}')",
                "target": "Rejected"
            })
            continue
            
        print(f"  N-grams: {ngrams}")
        
        sentence_matches = []
        
        for ngram in ngrams:
            # Stage 1 & 2: Exact and Synonym Lookup
            if ngram in exact_synonym_map:
                for hpo_id, name in exact_synonym_map[ngram]:
                    if hpo_id == "HP:0000050":
                        continue
                    sentence_matches.append({
                        "hpo_id": hpo_id,
                        "name": name,
                        "matched_phrase": ngram,
                        "confidence": 100,
                        "method": "Exact/Synonym"
                    })
            else:
                # Stage 3: Semantic Cosine Similarity Fallback using character-level TF-IDF
                ngram_vector = tfidf.transform([ngram])
                sims = cosine_similarity(ngram_vector, tfidf_matrix)[0]
                best_idx = np.argmax(sims)
                best_score = sims[best_idx]
                
                if best_score >= 0.75:
                    matched_synonym = synonym_list[best_idx]
                    confidence = int(best_score * 100)
                    for hpo_id, name in exact_synonym_map[matched_synonym]:
                        if hpo_id == "HP:0000050":
                            continue
                        sentence_matches.append({
                            "hpo_id": hpo_id,
                            "name": name,
                            "matched_phrase": matched_synonym,
                            "confidence": confidence,
                            "method": f"Semantic TF-IDF (score={best_score:.2f}, match='{matched_synonym}')"
                        })
                        
        if sentence_matches:
            # Register matches and track for debug panel
            for match in sentence_matches:
                hpo_id = match["hpo_id"]
                name = match["name"]
                confidence = match["confidence"]
                matched_phrase = match["matched_phrase"]
                
                entity_desc = f"{name} ({hpo_id}) via '{matched_phrase}' [{match['method']}]"
                if entity_desc not in extracted_clinical_entities:
                    extracted_clinical_entities.append(entity_desc)
                    
                if hpo_id not in mapped_terms or confidence > mapped_terms[hpo_id]["confidence"]:
                    mapped_terms[hpo_id] = {
                        "name": name,
                        "matched_phrase": sentence,
                        "matched_synonym": matched_phrase,
                        "confidence": confidence
                    }
            print(f"  Matches: {[m['hpo_id'] + ' (' + m['name'] + ')' for m in sentence_matches]}")
        else:
            unmatched_lines.append(sentence)
            print("  No HPO match found.")
            
    print("\n--- END DEBUG ---\n")
    
    # Store clinical entities in metadata log for the UI
    import streamlit as st
    st.session_state["extracted_clinical_entities"] = extracted_clinical_entities
    
    return mapped_terms, unmatched_lines, ignored_demographics, ignored_administrative, rejected_non_clinical
