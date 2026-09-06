import xml.etree.ElementTree as ET
import glob
import os

print("=== XML FILES IN SCRATCH ===")
for xml_file in sorted(glob.glob("scratch/pmc_*.xml")):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        title_el = root.find(".//article-title")
        title = "".join(title_el.itertext()).strip() if title_el is not None else "No title"
        
        pmid_el = root.find(".//article-id[@pub-id-type='pmid']")
        pmid = "".join(pmid_el.itertext()).strip() if pmid_el is not None else "No PMID"
        
        pmc_el = root.find(".//article-id[@pub-id-type='pmc']")
        pmc = "".join(pmc_el.itertext()).strip() if pmc_el is not None else "No PMC"
        
        doi_el = root.find(".//article-id[@pub-id-type='doi']")
        doi = "".join(doi_el.itertext()).strip() if doi_el is not None else "No DOI"
        
        # pub date
        years = [y.text for y in root.findall(".//pub-date/year") if y.text]
        year = years[0] if years else "No year"
        
        # Authors
        authors = []
        for contrib in root.findall(".//contrib[@contrib-type='author']"):
            surname = contrib.find(".//surname")
            given = contrib.find(".//given-names")
            if surname is not None:
                s = surname.text or ""
                g = given.text if given is not None else ""
                authors.append(f"{s} {g}".strip())
        
        first_author = authors[0] if authors else "Unknown"
        author_str = f"{first_author} et al." if len(authors) > 1 else first_author
        
        # Journal
        j_el = root.find(".//journal-title")
        journal = "".join(j_el.itertext()).strip() if j_el is not None else "No journal"
        
        print(f"File: {xml_file}")
        print(f"  Title: {title}")
        print(f"  Authors: {author_str} (Total: {len(authors)}) -> First 3: {', '.join(authors[:3])}")
        print(f"  Journal: {journal}, Year: {year}")
        print(f"  PMID: {pmid}, PMC: {pmc}, DOI: {doi}")
        print("-" * 50)
    except Exception as e:
        print(f"Error reading {xml_file}: {e}")
