#!/usr/bin/env python3
# scripts/sovereign_promoter_2025.py — FINAL ETERNAL VERSION (Dec 2025)
# UPDATED: Supports .py, .json, AND .md files.
# Drop any file anywhere → commit → it is instantly moved to the correct sovereign folder

import shutil
import subprocess
import sys
import re
import json
from pathlib import Path

SOVEREIGN_ROOTS = {
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "schemas",
    "prompt_governance",
    "observability",
    "config",
    "docs",  # Added docs root
}

# Files that ALWAYS promote regardless of score
FORCE_PROMOTE_PATTERN = re.compile(
    r"signal_quality_pipeline|validation_gates|preflight|creative_brief|transaction_manager|schema_transform",
    re.I,
)

# Destination map — highest priority first
DESTINATION_RULES = [
    # ... (Same rules, they work for MD content too) ...
    (
        r"signal_quality_pipeline|validation_gates|preflight|creative_brief|transaction_manager|schema_transform",
        "apps_shared/rag/hardening",
    ),
    (
        r"rag.*pipeline|rag.*hardening|signal.*quality|self.?critique|fact.?check|claim.*verif|hyde|reranker|guardrail|citation|provenance",
        "apps_shared/rag/hardening",
    ),
    (r"retriev|embed|vector|index|search|lookup|chunk|passage", "apps_shared/rag/retrieval"),
    (
        r"planner|orchestrator|route|delegate|schedule|coordinate|workflow|loop|agent.*loop|synthesis",
        "agentic_core/planning",
    ),
    (r"tool.*call|invoke.*tool|execute.*action|dispatch|perform|use.*tool", "agentic_core/execution/tools"),
    (r"schema|contract|pydantic.*model|request|response|dto|json", "schemas"),
    (r"prompt.*govern|system.*prompt|safety.*rail|jailbreak|redteam|red.?team|prompt", "prompt_governance"),
    (r"metric|trace|span|observ|log.*structured|otel|opentelemetry|monitoring", "observability"),
    (r"config|setting|feature.*flag|env|toggle|runtime.*config|secrets", "config"),
    (r"readme|guide|doc|manual|setup|install", "docs"), # Catch-all for generic docs
]


def is_sovereign_grade(content: str, filename: str) -> tuple[bool, str]:
    # --- MARKDOWN HANDLING ---
    if filename.lower().endswith(".md"):
        if len(content.strip()) > 10:  # Basic check: is it non-empty?
            return True, "valid-md"
        return False, "empty-md"

    # --- JSON HANDLING ---
    if filename.lower().endswith(".json"):
        try:
            json.loads(content)
            return True, "valid-json"
        except json.JSONDecodeError:
            return False, "invalid-json-syntax"

    # --- PYTHON HANDLING ---
    score = 0
    reasons = []

    if "from __future__ import annotations" in content:
        score += 4
        reasons.append("annotations")
    if re.search(r"@dataclass\s*\(.*frozen=True", content, re.DOTALL):
        score += 4
        reasons.append("frozen")
    if "class " in content and "Protocol" in content:
        score += 5
        reasons.append("Protocol")
    if "Enum(" in content and "auto()" in content:
        score += 3
        reasons.append("Enum")
    if "Literal[" in content:
        score += 3
        reasons.append("Literal")
    if content.count("->") > content.count("\n") * 0.4:
        score += 3
        reasons.append("dense-types")

    core_terms = len(
        re.findall(
            r"\b(RAG|HyDE|reranker|guardrail|self.?critique|fact.?check|claim|source.?tier|orchestrator|planner|mcp|sdk|signal.?quality)\b",
            content,
            re.I,
        )
    )
    if core_terms >= 2:
        score += 4
        reasons.append(f"{core_terms}-core")

    if re.search(r"\bprint\(|pdb\. |breakpoint\(|PENDING|ATTENTION|XXX", content):
        return False, "dirty"
    
    if core_terms >= 5:
        return True, f"structural-pass:{core_terms}-core"

    return score >= 7, f"score={score} [{', '.join(reasons)}]"


def choose_destination(content: str, filename: str) -> Path:
    lower = (content + "\n" + filename).lower()
    for pattern, dest in DESTINATION_RULES:
        if re.search(pattern, lower):
            return Path(dest)
    
    # Default Routing
    if filename.lower().endswith(".md"):
        return Path("docs")
    if filename.lower().endswith(".json"):
        return Path("config") # Safe default for data
        
    return Path("apps_shared/core") 


def main() -> None:
    moved = False
    files_to_process = []
    
    # 1. CLI Args
    files_to_process.extend(Path(arg) for arg in sys.argv[1:])

    # 2. Staged Files
    archive_dir = Path("archive_code")
    if archive_dir.is_dir():
        # UPDATED: Glob .py, .json, .md
        files_to_process.extend(archive_dir.glob("*.py"))
        files_to_process.extend(archive_dir.glob("*.json"))
        files_to_process.extend(archive_dir.glob("*.md"))
    
    processed_paths = set() 
    
    for src in files_to_process:
        if src in processed_paths:
            continue
        processed_paths.add(src)
        
        if not src.is_file() or src.suffix not in {".py", ".json", ".md"}:
            continue

        if "scripts" in src.parts or src.parent.name == "scripts":
            continue
        if src.parts[0] in {"runtime", "shared"} and src.parent.name not in {"apps_shared", "archive_code"}:
            continue

        if any(root in src.parts for root in SOVEREIGN_ROOTS):
            continue

        content = src.read_text(errors="ignore")
        
        if FORCE_PROMOTE_PATTERN.search(src.name):
            sovereign, reason = True, "force-promote:historical-resume-gen"
        else:
            sovereign, reason = is_sovereign_grade(content, src.name)
        
        if not sovereign:
            if src.parent.name == "archive_code":
                print(f"Archive file rejected -> {src.name}  (reason:{reason}) - Deleted from staging.")
                src.unlink()
            continue

        dest_dir = choose_destination(content, src.name)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / src.name

        for parent in [dest_dir] + list(dest_dir.parents):
            if parent.name in SOVEREIGN_ROOTS:
                break
            init = parent / "__init__.py"
            # Only create __init__.py for directories containing .py files
            if not init.exists() and dest_path.suffix == ".py":
                init.touch()

        shutil.move(str(src), str(dest_path))

        subprocess.run(["git", "add", str(dest_path)], capture_output=True)
        subprocess.run(["git", "rm", "--cached", str(src)], capture_output=True)

        print(f"Auto-promoted -> {dest_path}  ({reason})")
        moved = True

    if archive_dir.is_dir() and not list(archive_dir.iterdir()):
        archive_dir.rmdir()
        print("Cleaned up empty /archive_code/ staging directory.")

    sys.exit(0)


if __name__ == "__main__":
    main()
