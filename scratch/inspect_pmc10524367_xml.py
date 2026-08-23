with open("scratch/pmc_10524367.xml", "r", encoding="utf-8") as f:
    text = f.read()

print("File size:", len(text))
import re
print("Table wraps:", len(re.findall(r"<table-wrap", text)))
print("Supplementary material tags:", len(re.findall(r"<supplementary-material", text)))
print("Mentions of Table S1 or similar:")
for m in re.finditer(r"Table\s+S\d+", text, re.I):
    print("  ", text[m.start()-50:m.end()+100].replace("\n", " "))
