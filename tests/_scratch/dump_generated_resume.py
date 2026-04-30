import json
import pathlib

g = json.loads(
    pathlib.Path("apps_rg/scripts/generated_resume_20260429_191634.json").read_text(encoding="utf-8")
)
print("headline:", g["headline"])
print()
print("summary[:400]:")
print(g["summary"][:400])
print()
print("skills_count:", len(g["skills"]))
print("first_5_skills:", g["skills"][:5])
print()
print("experience_count:", len(g["experience"]))
for e in g["experience"]:
    print(f"  - {e.get('company','?')} | {e.get('title','?')} | {e.get('duration', e.get('dates','?'))}")
    print(f"      keys={list(e.keys())}")
print()
print("competencies_keys:", list(g["competencies"].keys()))
print()
print("metadata:", g["metadata"])
