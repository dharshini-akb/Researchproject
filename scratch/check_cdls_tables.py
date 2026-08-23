with open(r"C:\Users\DHARSHINI KAVITHA\.gemini\antigravity-ide\brain\34b3184a-a459-43d0-ad14-fdd55ef0bbf9\.system_generated\steps\19\content.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "TABLE I" in line or "Table I" in line:
        print(f"Line {idx+1}: {line.strip()}")
        # print next 20 lines
        for j in range(1, 25):
            if idx + j < len(lines):
                print(f"  + {idx+j+1}: {lines[idx+j].strip()}")
