import os
import sys
import json
import random

# Setup workspace directory configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import system_config
from utils import logger, ocr_helper

log = logger.get_logger("evaluate_pipeline_error")

REPORTS_DIR = os.path.join(system_config.WORKSPACE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# List of true phenotypic clinical symptom phrases and their expected HPO ID mappings
EVAL_SUITE = [
    ("delayed speech", "HP:0000750"),
    ("hypotonia", "HP:0001252"),
    ("poor eye contact", "HP:0012760"),
    ("intellectual disability", "HP:0001249"),
    ("seizures", "HP:0001250"),
    ("microcephaly", "HP:0000252"),
    ("autistic behavior", "HP:0000729"),
    ("motor delay", "HP:0001270"),
    ("cleft palate", "HP:0000175"),
    ("developmental delay", "HP:0001263"),
]

def introduce_ocr_noise(text: str, noise_level: float = 0.15) -> str:
    """
    Simulates OCR character transcription noise (deletions, substitutions, insertions).
    """
    chars = list(text)
    n_mutations = int(max(1, len(chars) * noise_level))
    for _ in range(n_mutations):
        idx = random.randint(0, len(chars) - 1)
        mutation_type = random.choice(["delete", "substitute", "insert"])
        
        if mutation_type == "delete" and len(chars) > 2:
            chars.pop(idx)
        elif mutation_type == "substitute":
            chars[idx] = random.choice("abcdefghijklmnopqrstuvwxyz")
        elif mutation_type == "insert":
            chars.insert(idx, random.choice("abcdefghijklmnopqrstuvwxyz"))
            
    return "".join(chars)

def evaluate_mapping_performance():
    vocab_path = os.path.join(system_config.PREPROC_ARTIFACTS_DIR, "hpo_feature_vocabulary.json")
    obo_path = os.path.join(system_config.RAW_DATA_DIR, "hp.obo")
    
    # Load synonyms mappings
    hpo_synonyms = ocr_helper.load_hpo_synonyms(vocab_path, obo_path)
    
    clean_success = 0
    clean_failed_cases = []
    
    noisy_success = 0
    noisy_failed_cases = []
    
    random.seed(42)
    
    log.info("Auditing pipeline: testing clean clinical statements (HPO Mapping capability)...")
    for phrase, target_hpo in EVAL_SUITE:
        # Run standard advanced NLP OCR mapping on a mock document line
        mapped_terms, _, _, _, _ = ocr_helper.extract_and_map_ocr_text(phrase, hpo_synonyms)
        
        if target_hpo in mapped_terms:
            clean_success += 1
        else:
            clean_failed_cases.append({
                "phrase": phrase,
                "expected_hpo": target_hpo,
                "detected": list(mapped_terms.keys())
            })
            
    log.info("Auditing pipeline: testing noisy statements (OCR robustness)...")
    for phrase, target_hpo in EVAL_SUITE:
        noisy_phrase = introduce_ocr_noise(phrase)
        mapped_terms, _, _, _, _ = ocr_helper.extract_and_map_ocr_text(noisy_phrase, hpo_synonyms)
        
        if target_hpo in mapped_terms:
            noisy_success += 1
        else:
            noisy_failed_cases.append({
                "clean_phrase": phrase,
                "noisy_phrase": noisy_phrase,
                "expected_hpo": target_hpo,
                "detected": list(mapped_terms.keys())
            })
            
    total = len(EVAL_SUITE)
    clean_accuracy = clean_success / total
    noisy_accuracy = noisy_success / total
    
    # Analyze error attribution
    hpo_mapping_errors = len(clean_failed_cases)
    # OCR errors are cases where it succeeded on clean but failed on noisy
    ocr_attributable_errors = 0
    for case in noisy_failed_cases:
        if case["clean_phrase"] not in [c["phrase"] for c in clean_failed_cases]:
            ocr_attributable_errors += 1
            
    audit_results = {
        "summary": {
            "total_test_phrases": total,
            "clean_text_mapping_accuracy": clean_accuracy,
            "noisy_text_mapping_accuracy": noisy_accuracy,
            "hpo_dictionary_mapping_errors": hpo_mapping_errors,
            "ocr_induced_mapping_errors": ocr_attributable_errors
        },
        "clean_failed_cases": clean_failed_cases,
        "noisy_failed_cases": noisy_failed_cases
    }
    
    audit_path = os.path.join(REPORTS_DIR, "pipeline_error_audit.json")
    with open(audit_path, "w") as f:
        json.dump(audit_results, f, indent=4)
        
    log.info("=== PIPELINE ERROR AUDIT ===")
    log.info(f"HPO Dictionary Mapping Accuracy: {clean_accuracy:.2%}")
    log.info(f"OCR Typo Resilient NLP Accuracy: {noisy_accuracy:.2%}")
    log.info(f"Errors due to HPO vocabulary gaps: {hpo_mapping_errors}")
    log.info(f"Errors due to OCR transcription noise: {ocr_attributable_errors}")
    log.info(f"Saved audit report to {audit_path}")
    print("Pipeline error audit execution completed successfully.")

if __name__ == "__main__":
    evaluate_mapping_performance()
