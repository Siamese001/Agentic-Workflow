"""RCA: trace exactly which keywords from the bank match the resume text."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps_rg.types.skill_extractor_node_types import SkillExtractorNode
from apps_rg.reasoning.ContentQualityAgent import ContentQualityAgent  # for _resume_to_profile_text

# Load canonical master_resume (legacy `your_resume_updated.json` retired 2026-04-30).
_CANONICAL_MASTER = Path(__file__).resolve().parents[2] / "apps_shared" / "data" / "master_resume.json"
resume = json.loads(_CANONICAL_MASTER.read_text(encoding="utf-8"))

# Build the same profile_text that ContentQualityAgent builds
class FakeAgent:
    pass

# Replicate _resume_to_profile_text inline so we don't need to instantiate the agent
profile_text = ""
if "summary" in resume:
    profile_text += f" {resume['summary']}"
if "experience" in resume:
    for exp in resume["experience"]:
        if isinstance(exp, dict):
            profile_text += f" {exp.get('title', '')} {exp.get('description', '')}"
            for bullet in exp.get("bullets", []):
                profile_text += f" {bullet}"
if "skills" in resume:
    if isinstance(resume["skills"], list):
        profile_text += " " + " ".join(str(s) for s in resume["skills"])

text_lower = profile_text.lower()
print(f"profile_text length: {len(profile_text)} chars")
print(f"profile_text contains 'graphrag': {'graphrag' in text_lower}")
print(f"profile_text contains 'rag': {'rag' in text_lower}")
print(f"profile_text contains 'agentic': {'agentic' in text_lower}")
print(f"profile_text contains 'llm': {'llm' in text_lower}")
print()

# Now run the actual matcher
node = SkillExtractorNode()

matched_tech = {}
for category, skills in node.technical_skills.items():
    hits = [s for s in skills if s in text_lower]
    if hits:
        matched_tech[category] = hits

matched_soft = [s for s in node.soft_skills if s in text_lower]

matched_domain = {}
for industry, skills in node.domain_skills.items():
    hits = [s for s in skills if s in text_lower]
    if hits:
        matched_domain[industry] = hits

matched_tools = {}
for cat, tools in node.tool_skills.items():
    hits = [t for t in tools if t in text_lower]
    if hits:
        matched_tools[cat] = hits

print("=== TECHNICAL HITS ===")
for cat, hits in matched_tech.items():
    print(f"  {cat}: {hits}")
print(f"\n=== SOFT HITS ===\n  {matched_soft}")
print(f"\n=== DOMAIN HITS ===")
for cat, hits in matched_domain.items():
    print(f"  {cat}: {hits}")
print(f"\n=== TOOL HITS ===")
for cat, hits in matched_tools.items():
    print(f"  {cat}: {hits}")

total = sum(len(v) for v in matched_tech.values()) + len(matched_soft) + sum(len(v) for v in matched_domain.values()) + sum(len(v) for v in matched_tools.values())
print(f"\n=== TOTAL MATCHED: {total} ===")

# Now check what the matcher actually returns when called the same way ContentQualityAgent calls it
print("\n=== ACTUAL MATCHER OUTPUT (as ContentQualityAgent calls it) ===")
output = node(profile_text, {})
ext = output.extraction_result
print(f"  technical_skills ({len(ext.technical_skills)}): {ext.technical_skills}")
print(f"  soft_skills ({len(ext.soft_skills)}): {ext.soft_skills}")
print(f"  domain_skills ({len(ext.domain_skills)}): {ext.domain_skills}")
print(f"  tool_skills ({len(ext.tool_skills)}): {ext.tool_skills}")
print(f"  confidence: {ext.confidence_score}")
