#!/usr/bin/env python3
# scripts/promoter_with_output.py - Modified version with verbose output

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
    (r"resume|cv|profile|candidate|job|application|work.?history", "apps_rg"),
    (r"outreach|message|email|campaign|contact|lead", "apps_lic"),
    (r"test|spec|example|demo|sample", "apps_shared/examples"),
    (r"doc|readme|guide|tutorial", "docs"),
    (r".*RES\.py", "apps_rg/resume_generation"),
    (r".*\.json", "schemas"),
    (r".*\.md", "docs"),
    ("", "apps_shared/core"),
]

def analyze_file_content(content: str, filename: str) -> tuple[int, list[str], bool]:
    """Simple scoring logic - returns (score, reasons, is_dirty)"""
    score = 5
    reasons = []
    is_dirty = False
    
    if len(content) < 100:
        score -= 2
        reasons.append("too-short")
    
    if "TODO" in content or "FIXME" in content:
        is_dirty = True
        reasons.append("has-todos")
    
    if "import" in content:
        score += 1
        reasons.append("has-imports")
    
    if "class" in content:
        score += 1
        reasons.append("has-classes")
    
    if "def" in content:
        score += 1
        reasons.append("has-functions")
    
    return min(10, max(0, score)), reasons, is_dirty

def choose_destination(content: str, filename: str) -> Path:
    """Choose destination based on filename patterns"""
    for pattern, dest in DESTINATION_RULES:
        if re.search(pattern, filename, re.I):
            return Path(dest)
    return Path("apps_shared/core")

def _should_promote_file(src: Path, score: int, reasons: List[str], is_dirty: bool, is_staged_file: bool) -> Tuple[bool, str]:
    """Determine if a file should be promoted and why."""
    if FORCE_PROMOTE_PATTERN.search(src.name):
        return True, "force-promote:historical"
    elif score >= 7 and not is_dirty:
        return True, f"sovereign-grade:score={score}"
    elif any("core" in r for r in reasons) and not is_dirty:
        return True, "structural-pass"
    elif is_staged_file:
        if is_dirty:
            return True, "legacy-import:dirty (needs cleanup)"
        else:
            return True, f"legacy-import:low-score={score}"
    return False, ""

def _should_skip_file(src: Path, archive_dir: Path) -> Optional[str]:
    """Check if a file should be skipped and return the reason."""
    if not src.is_file() or src.suffix not in {".py", ".json", ".md"}:
        return "Invalid file type"
    
    # Skip system folders
    if "scripts" in src.parts or src.parent.name == "scripts":
        return "In scripts folder"
    if src.parts[0] in {"runtime", "shared"} and src.parent.name not in {"apps_shared", "archive_code"}:
        return "In runtime/shared"
    if any(root in src.parts for root in SOVEREIGN_ROOTS):
        return "Already in sovereign directory"
    
    return None

def _scan_archive_directory(archive_dir: Path) -> List[Path]:
    """Scan archive directory for files to process."""
    if not archive_dir.is_dir():
        print("❌ archive_code directory not found!")
        return []
    
    py_files = list(archive_dir.glob("*.py"))
    json_files = list(archive_dir.glob("*.json"))
    md_files = list(archive_dir.glob("*.md"))
    
    files = py_files + json_files + md_files
    print(f"📁 Found {len(py_files)} .py files, {len(json_files)} .json files, {len(md_files)} .md files")
    print(f"📊 Total files to process: {len(files)}")
    return files

def _process_single_file(src: Path, archive_dir: Path, promoted_files: List, rejected_files: List) -> None:
    """Process a single file for promotion."""
    print(f"\n🔎 Processing: {src.name}")
    
    skip_reason = _should_skip_file(src, archive_dir)
    if skip_reason:
        print(f"  ⏭️  Skipped: {skip_reason}")
        return
    
    is_staged_file = (archive_dir.resolve() in src.resolve().parents) or (src.parent.name == "archive_code")
    content = src.read_text(errors="ignore")
    score, reasons, is_dirty = analyze_file_content(content, src.name)
    
    print(f"  📈 Score: {score}/10")
    print(f"  📝 Reasons: {', '.join(reasons)}")
    print(f"  🧹 Dirty: {is_dirty}")
    
    should_promote, promotion_reason = _should_promote_file(src, score, reasons, is_dirty, is_staged_file)
    
    if not should_promote:
        print(f"  ❌ REJECTED")
        rejected_files.append(src.name)
        return
    
    _execute_promotion(src, content, promotion_reason, promoted_files)

def _execute_promotion(src: Path, content: str, promotion_reason: str, promoted_files: List) -> None:
    """Execute file promotion to destination directory."""
    dest_dir = choose_destination(content, src.name)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / src.name
    
    print(f"  ✅ PROMOTED to: {dest_dir}")
    print(f"  📋 Reason: {promotion_reason}")
    
    for parent in [dest_dir] + list(dest_dir.parents):
        if parent.name in SOVEREIGN_ROOTS:
            break
        init = parent / "__init__.py"
        if not init.exists() and dest_path.suffix == ".py":
            init.touch()
    
    shutil.move(str(src), str(dest_path))
    promoted_files.append((src.name, str(dest_dir), promotion_reason))
    
    try:
        subprocess.run(["git", "add", str(dest_path)], capture_output=True, check=False)
        subprocess.run(["git", "rm", "--cached", str(src)], capture_output=True, check=False)
    except (FileNotFoundError, subprocess.SubprocessError, OSError):
        pass

def _print_summary(promoted_files: List, rejected_files: List, archive_dir: Path) -> None:
    """Print promotion summary."""
    print("\n" + "="*60)
    print("📊 PROMOTION SUMMARY")
    print("="*60)
    print(f"✅ Files Promoted: {len(promoted_files)}")
    print(f"❌ Files Rejected: {len(rejected_files)}")
    
    if promoted_files:
        print("\n✅ PROMOTED FILES:")
        for name, dest, reason in promoted_files:
            print(f"  • {name} → {dest} ({reason})")
    
    if rejected_files:
        print("\n❌ REJECTED FILES:")
        for name in rejected_files:
            print(f"  • {name}")
    
    if archive_dir.is_dir() and not list(archive_dir.iterdir()):
        archive_dir.rmdir()
        print(f"\n🧹 Cleaned up empty archive_code directory")

def main() -> None:
    """Main function to promote files from archive_code to appropriate directories."""
    archive_dir = Path("archive_code")
    print(f"🔍 Scanning archive_code directory: {archive_dir}")
    
    files_to_process = _scan_archive_directory(archive_dir)
    if not files_to_process:
        return
    
    processed_paths = set()
    promoted_files = []
    rejected_files = []
    
    for src in files_to_process:
        if src in processed_paths:
            continue
        processed_paths.add(src)
        _process_single_file(src, archive_dir, promoted_files, rejected_files)
    
    _print_summary(promoted_files, rejected_files, archive_dir)

if __name__ == "__main__":
    main()
