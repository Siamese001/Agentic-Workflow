"""Shared Cursor governance tier measurement (W0 SSOT for always-on budget).

Tier-1 (Cursor-native): ``.cursor/rules/*.mdc`` with ``alwaysApply: true`` + ``AGENTS.md``.
Windsurf legacy ``trigger: always_on`` ``.md`` files are reported separately (not summed into Tier-1).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

THRESHOLD_BYTES = 51_200
REPO_ROOT = Path(__file__).resolve().parents[2]
CURSOR_RULES_DIR = REPO_ROOT / ".cursor" / "rules"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
WINDSURF_RULES_DIR = REPO_ROOT / ".cursor" / "rules"
INVENTORY_PATH = REPO_ROOT / "docs" / "reports" / "cursor" / "governance_tier_inventory.json"

ALWAYS_APPLY_RE = re.compile(r"alwaysApply:\s*true", re.IGNORECASE)
TRIGGER_RE = re.compile(r"^trigger:\s*(\w+)", re.MULTILINE)

OPTION_A_ALWAYS_APPLY = frozenset(
    {
        "000-agentic-core-operating-contract.mdc",
        "001-cursor-runtime-seam-execution.mdc",
        "002-pass-blocked-proof-contract.mdc",
        "003-cursor-author-gate-hitl.mdc",
    }
)
OPTION_A_TRANSITIONAL_EXTRAS: frozenset[str] = frozenset()


@dataclass(frozen=True)
class FileBytes:
    rel_path: str
    bytes: int


def _file_bytes(path: Path) -> int:
    return len(path.read_bytes())


def scan_cursor_always_apply_mdc() -> list[FileBytes]:
    rows: list[FileBytes] = []
    if not CURSOR_RULES_DIR.is_dir():
        return rows
    for path in sorted(CURSOR_RULES_DIR.glob("*.mdc")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if ALWAYS_APPLY_RE.search(text):
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            rows.append(FileBytes(rel_path=rel, bytes=_file_bytes(path)))
    return rows


def scan_agents_md() -> FileBytes | None:
    if not AGENTS_MD.is_file():
        return None
    return FileBytes(
        rel_path=str(AGENTS_MD.relative_to(REPO_ROOT)).replace("\\", "/"),
        bytes=_file_bytes(AGENTS_MD),
    )


def scan_windsurf_always_on_md() -> list[FileBytes]:
    rows: list[FileBytes] = []
    if not WINDSURF_RULES_DIR.is_dir():
        return rows
    for path in sorted(WINDSURF_RULES_DIR.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        match = TRIGGER_RE.search(text)
        if match and match.group(1) == "always_on":
            rel = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            rows.append(FileBytes(rel_path=rel, bytes=_file_bytes(path)))
    return rows


def tier1_cursor_total() -> tuple[int, list[FileBytes]]:
    mdc_rows = scan_cursor_always_apply_mdc()
    agents = scan_agents_md()
    total = sum(r.bytes for r in mdc_rows)
    if agents is not None:
        total += agents.bytes
    all_rows = list(mdc_rows)
    if agents is not None:
        all_rows.append(agents)
    return total, all_rows


def build_inventory(*, policy_option: str = "A", wave: str = "W0") -> dict:
    mdc_rows = scan_cursor_always_apply_mdc()
    agents = scan_agents_md()
    windsurf_rows = scan_windsurf_always_on_md()
    tier1_total, tier1_paths = tier1_cursor_total()
    windsurf_total = sum(r.bytes for r in windsurf_rows)
    always_apply_names = sorted(Path(r.rel_path).name for r in mdc_rows)
    always_apply_set = frozenset(always_apply_names)
    missing_option_a = sorted(OPTION_A_ALWAYS_APPLY - always_apply_set)
    transitional_present = sorted(always_apply_set & OPTION_A_TRANSITIONAL_EXTRAS)
    unexpected_vs_a = sorted(
        always_apply_set - OPTION_A_ALWAYS_APPLY - OPTION_A_TRANSITIONAL_EXTRAS
    )
    tier1_status = "PASS" if tier1_total <= THRESHOLD_BYTES else "FAIL"
    plans_dir = REPO_ROOT / ".cursor" / "plans"
    active_plan_count = (
        len([p for p in plans_dir.iterdir() if p.is_file()]) if plans_dir.is_dir() else 0
    )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "plan_id": "cursor-governance-two-tier-b4e8f2",
        "wave": wave,
        "policy_option_selected": policy_option,
        "policy_option_a_target_always_apply": sorted(OPTION_A_ALWAYS_APPLY),
        "policy_option_a_transitional_extras_pending_w1": sorted(OPTION_A_TRANSITIONAL_EXTRAS),
        "tier_1_cursor_native": {
            "measured_paths": [r.rel_path for r in tier1_paths],
            "files": [{"path": r.rel_path, "bytes": r.bytes} for r in tier1_paths],
            "total_bytes": tier1_total,
            "approx_tokens": tier1_total // 4,
            "threshold_bytes": THRESHOLD_BYTES,
            "status": tier1_status,
            "headroom_bytes": THRESHOLD_BYTES - tier1_total,
        },
        "agents_md_bytes": agents.bytes if agents else 0,
        "always_apply_mdc_count": len(mdc_rows),
        "always_apply_mdc_names": always_apply_names,
        "option_a_alignment": {
            "missing_from_disk": missing_option_a,
            "transitional_extras_present": transitional_present,
            "unexpected_extras": unexpected_vs_a,
            "w1_pending_demotion": transitional_present,
        },
        "windsurf_legacy_always_on": {
            "reported_separately": True,
            "summed_into_tier_1": False,
            "total_bytes": windsurf_total,
            "approx_tokens": windsurf_total // 4,
            "file_count": len(windsurf_rows),
            "files": [{"path": r.rel_path, "bytes": r.bytes} for r in windsurf_rows],
        },
        "active_plans_top_level_count": active_plan_count,
        "explicit_non_claims": [
            "W1-W5 not executed",
            "no semantic rule consolidation performed",
            "docs/archive/windsurf/legacy-tree not deleted",
            "runtime RAG not touched",
            "agentic_core untouched",
            "two-tier consolidation not complete",
        ],
    }


def write_inventory(path: Path | None = None, *, wave: str = "W0") -> Path:
    target = path or INVENTORY_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = build_inventory(wave=wave)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return target
