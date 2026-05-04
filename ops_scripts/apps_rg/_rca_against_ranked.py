"""RCA: run validate_skills against the RANKED output (what ContentQualityAgent actually sees)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from apps_rg.types.skill_extractor_node_types import SkillExtractorNode

# Load the latest RANKED output
candidates = sorted(Path(__file__).parent.glob("generated_resume_*.json"))
ranked = json.loads(candidates[-1].read_text(encoding="utf-8"))
print(f"Using ranked output: {candidates[-1].name}")
print(f"Top-level keys: {list(ranked.keys())}")
print(f"skills section: {ranked.get('skills')!r}")

# Replicate _resume_to_profile_text
profile_text = ""
if "summary" in ranked:
    profile_text += f" {ranked['summary']}"
if "experience" in ranked:
    for exp in ranked["experience"]:
        if isinstance(exp, dict):
            profile_text += f" {exp.get('title', '')} {exp.get('description', '')}"
            for bullet in exp.get("bullets", []):
                profile_text += f" {bullet}"
if "skills" in ranked:
    if isinstance(ranked["skills"], list):
        profile_text += " " + " ".join(str(s) for s in ranked["skills"])

print(f"\nprofile_text length: {len(profile_text)}")
print(f"first 500 chars: {profile_text[:500]!r}")
print(f"contains 'graphrag': {'graphrag' in profile_text.lower()}")
print(f"contains 'agentic': {'agentic' in profile_text.lower()}")
print(f"contains 'rag': {'rag' in profile_text.lower()}")

node = SkillExtractorNode()
output = node(profile_text, {})
ext = output.extraction_result
total = len(ext.technical_skills) + len(ext.soft_skills) + len(ext.domain_skills) + len(ext.tool_skills)
print(f"\n=== EXTRACTION RESULT ===")
print(f"  technical ({len(ext.technical_skills)}): {ext.technical_skills}")
print(f"  soft ({len(ext.soft_skills)}): {ext.soft_skills}")
print(f"  domain ({len(ext.domain_skills)}): {ext.domain_skills}")
print(f"  tool ({len(ext.tool_skills)}): {ext.tool_skills}")
print(f"  total: {total}")
print(f"  confidence: {ext.confidence_score}")
print(f"\n=== VALIDATION VERDICT ===")
print(f"  total_skills < 5: {total < 5}")
print(f"  confidence < 0.6: {ext.confidence_score < 0.6}")
