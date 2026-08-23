with open(r"C:\Users\DHARSHINI KAVITHA\.gemini\antigravity-ide\brain\34b3184a-a459-43d0-ad14-fdd55ef0bbf9\.system_generated\steps\15\content.md", "r", encoding="utf-8") as f:
    text = f.read()

print("Number of '|' characters:", text.count('|'))
print("Contains 'PT1' or similar?")
import re
print("PT[0-9]+ matches:", len(re.findall(r"\bPT\d+\b", text)))
# print unique matches of PTxx
print("Unique PTxx matches:", set(re.findall(r"\bPT\d+\b", text)))

# Let's search for 'Patient' or 'individual' or 'subject' with numbers
print("Patient[s] matches:", len(re.findall(r"\bpatient\b", text, re.IGNORECASE)))
print("Individual[s] matches:", len(re.findall(r"\bindividual\b", text, re.IGNORECASE)))
print("Subject[s] matches:", len(re.findall(r"\bsubject\b", text, re.IGNORECASE)))
