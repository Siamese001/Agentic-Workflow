#!/usr/bin/env python3
# scripts/sovereign_promoter_2025.py — FINAL PERMISSIVE VERSION (Dec 2025)
# Supports .py, .json, .md
# "Capture First, Polish Later": Archive files are always promoted, never rejected.

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
    "docs",
}

# Files that ALWAYS promote regardless of score
FORCE_PROMOTE_PATTERN = re.compile(
    r"signal_quality_pipeline|validation_gates|preflight|creative_brief|transaction_manager|schema_transform",
    re.I,
)

# Destination map — highest priority first
DESTINATION_RULES = [
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
    (r"readme|guide|doc|manual|setup|install", "docs"),
]

def analyze_file_content(content: str, filename: str) -> tuple[int, list, bool]:
    """
    Returns: (score, reasons, is_dirty)
    """
    score = 0
    reasons = []
    is_dirty = False

    # --- MARKDOWN HANDLING ---
    if filename.lower().endswith(".md"):
        if len(content.strip()) > 10:
            return 10, ["valid-md"], False
        return 0, ["empty-md"], False

    # --- JSON HANDLING ---
    if filename.lower().endswith(".json"):
        try:
            json.loads(content)
            return 10, ["valid-json"], False
        except json.JSONDecodeError:
            return 0, ["invalid-json-syntax"], False

    # --- PYTHON HANDLING ---
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

    # Check for dirty code
    if re.search(r"\bprint\(|pdb\. |breakpoint\(|PENDING|ATTENTION|XXX", content):
        is_dirty = True
        reasons.append("dirty")

    return score, reasons, is_dirty

def choose_destination(content: str, filename: str) -> Path:
    lower = (content + "\n" + filename).lower()
    for pattern, dest in DESTINATION_RULES:
        if re.search(pattern, lower):
            return Path(dest)
    
    # Defaults
    if filename.lower().endswith(".md"):
        return Path("docs")
    if filename.lower().endswith(".json"):
        return Path("config")
    # Default fallback for unclassified Python
    return Path("apps_shared/core")

def main() -> None:
    files_to_process = []
    
    # 1. CLI Args
    files_to_process.extend(Path(arg) for arg in sys.argv[1:])

    # 2. Staged Files (Archive Code)
    archive_dir = Path("archive_code")
    is_archive_mode = False
    
    # If explicitly running on archive_code content
    if archive_dir.is_dir():
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

        # Determine if this file is from the staging area
        is_staged_file = (archive_dir.resolve() in src.resolve().parents) or (src.parent.name == "archive_code")

        # Skip sovereign roots and system folders
        if "scripts" in src.parts or src.parent.name == "scripts":
            continue
        if src.parts[0] in {"runtime", "shared"} and src.parent.name not in {"apps_shared", "archive_code"}:
            continue
        if any(root in src.parts for root in SOVEREIGN_ROOTS):
            continue

        content = src.read_text(errors="ignore")
        score, reasons, is_dirty = analyze_file_content(content, src.name)
        
        # --- PROMOTION LOGIC ---
        should_promote = False
        promotion_reason = ""

        # Rule 1: Force Promote Pattern
        if FORCE_PROMOTE_PATTERN.search(src.name):
            should_promote = True
            promotion_reason = "force-promote:historical"
        
        # Rule 2: High Score (Standard Sovereign Grade)
        elif score >= 7 and not is_dirty:
            should_promote = True
            promotion_reason = f"sovereign-grade:score={score}"

        # Rule 3: Structural Pass (Core Terms)
        elif any("core" in r for r in reasons) and not is_dirty:
            should_promote = True
            promotion_reason = "structural-pass"

        # Rule 4: PERMISSIVE ARCHIVE MODE (The Fix)
        # If it comes from archive_code, we promote it regardless of score/dirtiness.
        # We capture the logic now and clean it later.
        elif is_staged_file:
            should_promote = True
            if is_dirty:
                promotion_reason = "legacy-import:dirty (needs cleanup)"
            else:
                promotion_reason = f"legacy-import:low-score={score}"

        if not should_promote:
            if is_staged_file:
                # This branch technically shouldn't be reached due to Rule 4, 
                # unless the file is empty/unreadable.

                src.unlink()
            continue

        # Execute Move
        dest_dir = choose_destination(content, src.name)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / src.name

        # Auto-create __init__.py only for python trees
        for parent in [dest_dir] + list(dest_dir.parents):
            if parent.name in SOVEREIGN_ROOTS:
                break
            init = parent / "__init__.py"
            if not init.exists() and dest_path.suffix == ".py":
                init.touch()

        shutil.move(str(src), str(dest_path))

        subprocess.run(["git", "add", str(dest_path)], capture_output=True)
        subprocess.run(["git", "rm", "--cached", str(src)], capture_output=True)

    # Cleanup staging if empty
    if archive_dir.is_dir() and not list(archive_dir.iterdir()):
        archive_dir.rmdir()

    sys.exit(0)

if __name__ == "__main__":
    main()
