import re

files = {
    "White-Sutton": r"C:\Users\DHARSHINI KAVITHA\.gemini\antigravity-ide\brain\34b3184a-a459-43d0-ad14-fdd55ef0bbf9\.system_generated\steps\15\content.md",
    "Xia-Gibbs": r"C:\Users\DHARSHINI KAVITHA\.gemini\antigravity-ide\brain\34b3184a-a459-43d0-ad14-fdd55ef0bbf9\.system_generated\steps\17\content.md",
    "CdLS": r"C:\Users\DHARSHINI KAVITHA\.gemini\antigravity-ide\brain\34b3184a-a459-43d0-ad14-fdd55ef0bbf9\.system_generated\steps\19\content.md"
}

for name, path in files.items():
    print(f"\n=================== {name} ===================")
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    
    # Check if there is any mention of patient-level details
    print("Does text contain Patient 1? ", bool(re.search(r"patient\s+1\b", text, re.I)))
    print("Does text contain Patient 2? ", bool(re.search(r"patient\s+2\b", text, re.I)))
    print("Does text contain PT1? ", bool(re.search(r"\bPT1\b", text)))
    print("Does text contain PT2? ", bool(re.search(r"\bPT2\b", text)))
    print("Does text contain Table I? ", bool(re.search(r"\btable\s+I\b", text, re.I)))
    print("Does text contain Table 1? ", bool(re.search(r"\btable\s+1\b", text, re.I)))
    print("Does text contain Table 2? ", bool(re.search(r"\btable\s+2\b", text, re.I)))
