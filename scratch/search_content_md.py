with open(r"C:\Users\DHARSHINI KAVITHA\.gemini\antigravity-ide\brain\39aa88c2-d338-4e3e-8fab-794c75f64210\.system_generated\steps\153\content.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Total lines in content.md:", len(lines))
keywords = ["table", "supplement", "zip", "xlsx"]
for idx, line in enumerate(lines):
    if any(k in line.lower() for k in keywords):
        print(f"Line {idx+1}: {line.strip()[:120]}")
