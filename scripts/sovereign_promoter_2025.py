#!/usr/bin/env python3
# scripts/sovereign_promoter_2025.py — FINAL ETERNAL VERSION (Dec 2025)
# Drop any file anywhere → commit → it is instantly moved to the correct sovereign folder
# New folders are auto-created. No human ever touches structure again.
#
# MODIFICATION: Added logic to automatically process and promote files
# staged in the /archive_code/ temporary directory.

import shutil
import subprocess
import sys
import re
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
}

# Files that ALWAYS promote regardless of score (historical resume-gen port)
FORCE_PROMOTE_PATTERN = re.compile(
    r"signal_quality_pipeline|validation_gates|preflight|creative_brief|transaction_manager|schema_transform",
    re.I,
)

# Destination map — highest priority first
DESTINATION_RULES = [
    # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
    # historical RESUME-GEN PORT — THESE BELONG TO THE CANON FOREVER
    # ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
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
    (r"schema|contract|pydantic.*model|request|response|dto", "schemas"),
    (r"prompt.*govern|system.*prompt|safety.*rail|jailbreak|redteam|red.?team", "prompt_governance"),
    (r"metric|trace|span|observ|log.*structured|otel|opentelemetry|monitoring", "observability"),
    (r"config|setting|feature.*flag|env|toggle|runtime.*config|secrets", "config"),
]


def is_sovereign_grade(content: str) -> tuple[bool, str]:
    score = 0
    reasons = []

    if "from __future__ import annotations" in content:
        score += 4
        reasons.append("annotations")
    # Corrected check for @dataclass(frozen=True) which spans multiple lines often
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
    # Heuristic: More than 40% of lines contain a type hint (->)
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

    # --- Structural Pass Bypass (New Logic) ---
    # Check for "dirty" code first (this MUST NOT be bypassed)
    if re.search(r"\bprint\(|pdb\. |breakpoint\(|PENDING|ATTENTION|XXX", content):
        return False, "dirty"
    
    # Bypass: If it's very core-term-heavy, it's structurally important enough to be promoted.
    if core_terms >= 5:
        return True, f"structural-pass:{core_terms}-core"
    
    # Original Rule: Must hit the score threshold.
    return score >= 7, f"score={score} [{', '.join(reasons)}]"


def choose_destination(content: str, filename: str) -> Path:
    lower = (content + "\n" + filename).lower()
    for pattern, dest in DESTINATION_RULES:
        if re.search(pattern, lower):
            return Path(dest)
    return Path("apps_shared/core")  # safe default


def main() -> None:
    moved = False
    
    # --- MODIFICATION START ---
    files_to_process = []
    
    # 1. Files passed as arguments (standard promotion flow)
    files_to_process.extend(Path(arg) for arg in sys.argv[1:])

    # 2. Files staged in the /archive_code/ folder (new logic for incremental merge)
    archive_dir = Path("archive_code")
    if archive_dir.is_dir():
        files_to_process.extend(archive_dir.glob("*.py"))
    
    # Use a set to handle duplicates in the list of paths to process
    processed_paths = set() 
    
    # Iterate over the collected paths
    for src in files_to_process:
        if src in processed_paths:
            continue
        processed_paths.add(src)
        
        if not src.is_file() or src.suffix != ".py":
            continue

        # ETERNAL SCRIPT PROTECTION — NEVER TOUCH scripts/ or runtime glue
        if "scripts" in src.parts or src.parent.name == "scripts":
            continue
        # The check below allows files in 'archive_code' to be processed
        if src.parts[0] in {"runtime", "shared"} and src.parent.name not in {"apps_shared", "archive_code"}:
            continue

        # Skip files already under sovereign roots
        if any(root in src.parts for root in SOVEREIGN_ROOTS):
            continue

        content = src.read_text(errors="ignore")
        
        # Force-promote historical resume-gen files regardless of score
        if FORCE_PROMOTE_PATTERN.search(src.name):
            sovereign, reason = True, "force-promote:historical-resume-gen"
        else:
            sovereign, reason = is_sovereign_grade(content)
        
        if not sovereign:
            # If code is not Sovereign Grade AND it came from the staging area, delete it.
            if src.parent.name == "archive_code":
                print(f"Archive file rejected -> {src.name}  (reason:{reason}) - Deleted from staging.")
                src.unlink() # Delete the rejected file from the staging area
            continue

        dest_dir = choose_destination(content, src.name)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / src.name

        # Auto-create __init__.py chain from dest_dir up to the sovereign root
        for parent in [dest_dir] + list(dest_dir.parents):
            if parent.name in SOVEREIGN_ROOTS:
                break
            init = parent / "__init__.py"
            if not init.exists():
                init.touch()

        shutil.move(str(src), str(dest_path))

        # Keep git index in sync so pre-commit still sees the moved file
        subprocess.run(["git", "add", str(dest_path)], capture_output=True)
        subprocess.run(["git", "rm", "--cached", str(src)], capture_output=True)

        print(f"Auto-promoted -> {dest_path}  ({reason})")
        moved = True

    # Clean up the archive_code folder if empty after promotion and rejection.
    if archive_dir.is_dir() and not list(archive_dir.iterdir()):
        archive_dir.rmdir()
        print("Cleaned up empty /archive_code/ staging directory.")
    # --- MODIFICATION END ---
    
    # Always exit 0 so pre-commit continues; Light Canon will now skip moved files
    sys.exit(0)


if __name__ == "__main__":
    main()