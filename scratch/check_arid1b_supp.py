with open("scratch/pmc_6752273.xml", "r", encoding="utf-8") as f:
    text = f.read()

import re
print("Supplementary material tags in ARID1B paper:", len(re.findall(r"<supplementary-material", text)))
for m in re.finditer(r"<supplementary-material", text):
    print(text[m.start():m.start()+600])
