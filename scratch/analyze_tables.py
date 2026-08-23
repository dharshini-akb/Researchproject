import os
import sys

# Reconfigure stdout to use utf-8
sys.stdout.reconfigure(encoding='utf-8')

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
        content = f.read()
    
    # Let's find occurrences of table titles and print the surrounding 1000 characters
    for m in ["Table 1", "Table 2", "Table 3", "Table 4", "Table 5", "Table 6", "TABLE 1", "TABLE I", "Table I"]:
        idx = 0
        while True:
            idx = content.find(m, idx)
            if idx == -1:
                break
            print(f"\n--- Found '{m}' at char {idx} ---")
            print(content[idx:idx+1500])
            idx += len(m)
