"""One-shot rewrite of `docs/reference/<x>` references after tier-split (plan a3c9f1).

Walks the repo, applies a fixed mapping of old→new paths, and rewrites in place.
Skips archives, .git, build artifacts, and the moved files themselves (they
already use the new paths internally for their own back-links if any).

Usage:
    python tools/one_shot/rewrite_tier_split_refs.py [--dry-run]
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Old path -> new path. Order matters: longer / more-specific first so we don't
# match a substring of a later entry.
REWRITES: list[tuple[str, str]] = [
    # Stale version references → forward to current canonical (v34 is the
    # latest committed; v35 is being authored).
    ("docs/reference/agentic_process_mapping_v30.md", "docs/reference/_notes/agentic_process_mapping_v34.md"),
    ("docs/reference/agentic_process_mapping_v33.md", "docs/reference/_notes/agentic_process_mapping_v34.md"),
    ("docs/reference/agentic_process_mapping_exec.md", "docs/reference/_notes/agentic_system_process_map_exec.md"),
    # Tier B notes (root .md files)
    ("docs/reference/agentic_system_process_map_exec.md", "docs/reference/_notes/agentic_system_process_map_exec.md"),
    ("docs/reference/agentic_process_mapping_v34.md", "docs/reference/_notes/agentic_process_mapping_v34.md"),
    ("docs/reference/agentic_process_mapping_v35.md", "docs/reference/_notes/agentic_process_mapping_v35.md"),
    ("docs/reference/00Y_April2026_Gap_Closure_Reconciliation.md", "docs/reference/_notes/00Y_April2026_Gap_Closure_Reconciliation.md"),
    ("docs/reference/00Z_Source_Alignment_Best_Practices.md", "docs/reference/_notes/00Z_Source_Alignment_Best_Practices.md"),
    ("docs/reference/GAP_CLOSED_TEST_REPORT.md", "docs/reference/_notes/GAP_CLOSED_TEST_REPORT.md"),
    # Tier B reports
    ("docs/reference/PARENT_THINNING_ZERO_LOSS_REPORT.md", "docs/reference/_notes/reports/PARENT_THINNING_ZERO_LOSS_REPORT.md"),
    ("docs/reference/WINDOWS_EXPLORER_SAFE_TEST_REPORT.md", "docs/reference/_notes/reports/WINDOWS_EXPLORER_SAFE_TEST_REPORT.md"),
    ("docs/reference/ZIP_FINAL_VALIDATION.md", "docs/reference/_notes/reports/ZIP_FINAL_VALIDATION.md"),
    ("docs/reference/WINDOWS_PATH_MAP.md", "docs/reference/_notes/reports/WINDOWS_PATH_MAP.md"),
    # Tier C primer folders (must be longer-match-first; trailing slash form)
    ("docs/reference/AST Dependency Graphs (ADG)/", "docs/reference/_primers/AST Dependency Graphs (ADG)/"),
    ("docs/reference/Ingestion Pipeline/", "docs/reference/_primers/Ingestion Pipeline/"),
    ("docs/reference/Transformer Templates/", "docs/reference/_primers/Transformer Templates/"),
    ("docs/reference/98_Contextual_Refinement_Model_Primers/", "docs/reference/_primers/98_Contextual_Refinement_Model_Primers/"),
    ("docs/reference/Python/", "docs/reference/_primers/Python/"),
    ("docs/reference/Testing/", "docs/reference/_primers/Testing/"),
    ("docs/reference/Redis/", "docs/reference/_primers/Redis/"),
    ("docs/reference/MCP/", "docs/reference/_primers/MCP/"),
    ("docs/reference/prompting/", "docs/reference/_primers/prompting/"),
    ("docs/reference/CI/", "docs/reference/_primers/CI/"),
    # Tier C primer .md / .pdf at root
    ("docs/reference/Base Agent Hierarchy v2.md", "docs/reference/_primers/Base Agent Hierarchy v2.md"),
    ("docs/reference/Context Window Degradation.md", "docs/reference/_primers/Context Window Degradation.md"),
    ("docs/reference/DuckDB.md", "docs/reference/_primers/DuckDB.md"),
    ("docs/reference/Durable Mutation - L2 cannot write L4.md", "docs/reference/_primers/Durable Mutation - L2 cannot write L4.md"),
    ("docs/reference/Exit Criteria X1-X2-X3.md", "docs/reference/_primers/Exit Criteria X1-X2-X3.md"),
    ("docs/reference/Import Flow.md", "docs/reference/_primers/Import Flow.md"),
    ("docs/reference/JIT Elevator Shaft v2.md", "docs/reference/_primers/JIT Elevator Shaft v2.md"),
    ("docs/reference/LLM as a Judge.md", "docs/reference/_primers/LLM as a Judge.md"),
    ("docs/reference/MRO Mixins v2.md", "docs/reference/_primers/MRO Mixins v2.md"),
    ("docs/reference/nvm vs. npm vs. npx.md", "docs/reference/_primers/nvm vs. npm vs. npx.md"),
    ("docs/reference/Runtime Gates vs L5 vs Exit.md", "docs/reference/_primers/Runtime Gates vs L5 vs Exit.md"),
    ("docs/reference/Similarity Metrics and Use Cases.md", "docs/reference/_primers/Similarity Metrics and Use Cases.md"),
    ("docs/reference/Telemetry Generation vs. Utilization.md", "docs/reference/_primers/Telemetry Generation vs. Utilization.md"),
    ("docs/reference/practices-for-governing-agentic-ai-systems.pdf", "docs/reference/_primers/practices-for-governing-agentic-ai-systems.pdf"),
    ("docs/reference/the-future-of-ai-in-the-insurance-industry.pdf", "docs/reference/_primers/the-future-of-ai-in-the-insurance-industry.pdf"),
]

# Don't recurse into these.
SKIP_DIRS = {
    ".git",
    "archives",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".pytest_cache",
    ".mypy_cache",
    "_archive",
    "_smoke_v1_coerce_e9aa09",
}

# Already-moved files don't need rewriting (their location is correct;
# their *content* might still cite old paths to peers, but we want the
# rewrite to apply there too — so include _notes/ and _primers/).
INCLUDE_EXTS = {".md", ".py", ".json", ".yaml", ".yml", ".txt"}


def should_skip_dir(p: Path) -> bool:
    return any(part in SKIP_DIRS for part in p.parts)


def main() -> int:
    dry = "--dry-run" in sys.argv
    changed: list[tuple[str, int]] = []
    scanned = 0

    for path in REPO.rglob("*"):
        if not path.is_file():
            continue
        if should_skip_dir(path.relative_to(REPO)):
            continue
        if path.suffix.lower() not in INCLUDE_EXTS:
            continue
        # Don't rewrite the rewriter itself or the plan that documents the move.
        rel = path.relative_to(REPO).as_posix()
        if rel.endswith("rewrite_tier_split_refs.py"):
            continue
        if rel.endswith("docs-reference-tier-split-a3c9f1.md"):
            continue
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new_text = text
        hits = 0
        for old, new in REWRITES:
            if old in new_text:
                count = new_text.count(old)
                new_text = new_text.replace(old, new)
                hits += count
        if hits and new_text != text:
            changed.append((rel, hits))
            if not dry:
                path.write_text(new_text, encoding="utf-8", newline="\n")

    print(f"scanned: {scanned} files")
    print(f"{'WOULD CHANGE' if dry else 'changed'}: {len(changed)} files, "
          f"{sum(h for _, h in changed)} replacements")
    for rel, hits in sorted(changed, key=lambda x: -x[1])[:30]:
        print(f"  {hits:3d}  {rel}")
    if len(changed) > 30:
        print(f"  ... and {len(changed) - 30} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
