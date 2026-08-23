import os
import re

files = {
    "White-Sutton": r"C:\Users\DHARSHINI KAVITHA\.gemini\antigravity-ide\brain\34b3184a-a459-43d0-ad14-fdd55ef0bbf9\.system_generated\steps\15\content.md",
    "Xia-Gibbs": r"C:\Users\DHARSHINI KAVITHA\.gemini\antigravity-ide\brain\34b3184a-a459-43d0-ad14-fdd55ef0bbf9\.system_generated\steps\17\content.md",
    "CdLS": r"C:\Users\DHARSHINI KAVITHA\.gemini\antigravity-ide\brain\34b3184a-a459-43d0-ad14-fdd55ef0bbf9\.system_generated\steps\19\content.md"
}

for name, path in files.items():
    print(f"\n=================== {name} ===================")
    if not os.path.exists(path):
        print(f"File not found: {path}")
        continue
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    print(f"Total lines: {len(lines)}")
    headers = [line.strip() for line in lines if line.strip().startswith("#")]
    print("Headers:")
    for h in headers[:15]:
        print(f"  {h}")
    # Search for table references
    tables = [line.strip() for line in lines if "table" in line.lower() and line.strip().startswith(("#", "###", "####", "|"))]
    print("Table-related lines:")
    for t in tables[:15]:
        print(f"  {t}")
