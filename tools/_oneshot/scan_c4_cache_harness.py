"""Scan repo for C4 (Cache & Harness) markers."""
import os, re
from pathlib import Path

ROOT = Path(r"c:\Git\Agentic-Workflow-FRESH")
pats = {
    "prompt_cache": re.compile(r"(?i)\b(prompt[_ ]?cach\w+|cache_control|ephemeral.cache|<system.reminder>)"),
    "subagent": re.compile(r"(?i)\bsub[_ ]?agent\w*\b"),
    "skills_dir": re.compile(r"\.(windsurf|claude)[/\\]skills[/\\]"),
    "hooks": re.compile(r"\.(windsurf|claude)[/\\]hooks"),
    "three_phase": re.compile(r"(?i)gather.*context.*act.*verify|three.phase.loop|gather.{0,30}act.{0,30}verify"),
    "tool_token_budget": re.compile(r"(?i)\b(tool[_ ]?response[_ ]?(token[_ ]?budget|max[_ ]?tokens)|truncat\w+_tool|25000.*token)"),
    "compaction": re.compile(r"(?i)\b(compact\w+|scratchpad|NOTES\.md|todo[_ ]?offload)\b"),
    "agent_sdk": re.compile(r"(?i)\b(claude[_ ]?agent[_ ]?sdk|agent[_ ]?harness|agent[ _]?primitives?)"),
    "skill_md": re.compile(r"^---\s*$.*?^description:", re.M | re.S),
}
SKIP = ("_archive", "archives", "node_modules", ".venv", "venv", "__pycache__", ".git")
counts = {k: 0 for k in pats}
samples = {k: [] for k in pats}

for dp, dns, fs in os.walk(ROOT):
    if any(s in dp for s in SKIP):
        dns[:] = []
        continue
    for f in fs:
        if not f.endswith((".py", ".md", ".json", ".yaml", ".toml")):
            continue
        p = Path(dp) / f
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")[:80000]
        except Exception:
            continue
        for k, pat in pats.items():
            if pat.search(text):
                counts[k] += 1
                if len(samples[k]) < 3:
                    samples[k].append(str(p.relative_to(ROOT)).replace("\\", "/"))

for k in pats:
    print(f"{k:20s} files={counts[k]:5d}  e.g. {samples[k][:3]}")
