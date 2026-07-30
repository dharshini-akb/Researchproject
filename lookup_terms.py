import os
from preprocessing import data_loader

def main():
    hpo_map = data_loader.parse_hpo_obo()
    top_terms = [
        "HP:0001321", "HP:0008743", "HP:0000574", "HP:0001612", "HP:0010862",
        "HP:0012389", "HP:0000307", "HP:0000316", "HP:0002194", "HP:0000194"
    ]
    for term in top_terms:
        print(f"{term}: {hpo_map.get(term, 'Unknown')}")

if __name__ == "__main__":
    main()
