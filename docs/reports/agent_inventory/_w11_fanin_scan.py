#!/usr/bin/env python3
"""One-shot W11 fan-in scanner — planning only; writes w11_candidate_fanin_matrix.json."""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCAN_ROOTS = ("agentic_core", "apps_rg", "apps_shared", "tests", "ops_scripts", "docs", ".cursor")
SKIP_PARTS = {".venv", "__pycache__", "node_modules", ".git", "artifacts"}

CANDIDATES: list[dict[str, str]] = [
    {
        "id": "shim_apps_rg_l2_binding",
        "path": "archives/l2_rationalization_*/agentic_core/L2_execution/apps_rg_l2_binding.py",
        "patterns": [r"apps_rg_l2_binding", r"L2_execution\.apps_rg_l2_binding"],
        "current_classification": "RETIRE_CANDIDATE",
    },
    {
        "id": "validation_orchestrator",
        "path": "agentic_core/L2_execution/reasoning/validation_orchestrator.py",
        "patterns": [r"validation_orchestrator", r"ValidationOrchestrator"],
        "current_classification": "QUARANTINE_UNTIL_REVIEW",
    },
    {
        "id": "agentic_core_smoke",
        "path": "agentic_core/L2_execution/_agentic_core_smoke.py",
        "patterns": [r"_agentic_core_smoke", r"agentic_core_smoke"],
        "current_classification": "QUARANTINE_UNTIL_REVIEW",
    },
    {
        "id": "code_quality_examples",
        "path": "agentic_core/L2_execution/reasoning/examples/code_quality_*",
        "patterns": [r"code_quality_validator", r"code_quality_healer"],
        "current_classification": "QUARANTINE_UNTIL_REVIEW",
    },
    {
        "id": "dry_run_dir",
        "path": "apps_rg/runtime/dry_run/",
        "patterns": [r"runtime\.dry_run", r"runtime/dry_run", r"executive_summary_demo"],
        "current_classification": "QUARANTINE_UNTIL_REVIEW",
    },
    {
        "id": "orchestrate_full_resume",
        "path": "apps_rg/runtime/internal/lane_batch.py",
        "patterns": [r"orchestrate_full_resume", r"run_orchestration"],
        "current_classification": "TEST_SUPPORT_ONLY",
    },
    {
        "id": "rg_reasoning_agents",
        "path": "apps_rg/reasoning/Rg*.py",
        "patterns": [r"RgResumeOrchestrator", r"RgHealingOrchestrator", r"RgReflectionAgent", r"RgStrategicPlanner", r"RgTemplateOptimizer", r"RGStrategyExecutor", r"apps_rg\.reasoning\.Rg"],
        "current_classification": "SUPERSEDED_BY_APPS_RG_SECTION_RUNTIME",
    },
    {
        "id": "deprecated_dispatch_clis",
        "path": "apps_rg/runtime/dispatch/*_dispatch.py",
        "patterns": [r"exit_deprecated_dispatch_cli", r"runtime\.dispatch\.\w+_dispatch"],
        "current_classification": "DOC_DEPRECATE_ONLY",
    },
    {
        "id": "legacy_full_resume_env",
        "path": "APPS_RG_R4_GENERATION_MODE=legacy_full_resume",
        "patterns": [r"legacy_full_resume", r"MODE_LEGACY_FULL_RESUME"],
        "current_classification": "KEEP_ROLLBACK_ONLY",
    },
    {
        "id": "offline_contract_stub_env",
        "path": "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB",
        "patterns": [r"APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", r"OFFLINE_CONTRACT_STUB"],
        "current_classification": "KEEP_TEST_SUPPORT_ONLY",
    },
    {
        "id": "stub_only_provider_env",
        "path": "APPS_RG_L2_PROVIDER_MODE=stub_only",
        "patterns": [r"APPS_RG_L2_PROVIDER_MODE", r"stub_only", r"APPS_RG_L2_FORCE_STUB"],
        "current_classification": "KEEP_TEST_SUPPORT_ONLY",
    },
    {
        "id": "mock_judges_cli",
        "path": "--mock-judges",
        "patterns": [r"mock.judges", r"mock_judges", r"allow.test.mock.judges"],
        "current_classification": "KEEP_TEST_SUPPORT_ONLY",
    },
    {
        "id": "apps_shared_signal_stubs",
        "path": "apps_shared/utils/subatomic_hop_util.py + apps_shared/types/engine_type_types.py",
        "patterns": [r"subatomic_hop_util", r"engine_type_types", r"get_signal_enhancer"],
        "current_classification": "QUARANTINE_UNTIL_REVIEW",
    },
]


@dataclass
class FaninRow:
    id: str
    path: str
    current_classification: str
    proposed_final_classification: str
    active_path_confidence: str
    fan_in_count: int
    importers_py: list[str] = field(default_factory=list)
    importers_tests: list[str] = field(default_factory=list)
    importers_docs: list[str] = field(default_factory=list)
    importers_ci: list[str] = field(default_factory=list)
    env_cli_refs: list[str] = field(default_factory=list)
    runtime_receipt_refs: list[str] = field(default_factory=list)
    adg_status: str = "NOT_RUN"
    adg_fanin_count: int | None = None
    migration_required: bool = True
    delete_readiness: str = "NO"
    archive_readiness: str = "NO"
    blocker: str = ""


def _iter_scan_files() -> list[Path]:
    out: list[Path] = []
    for root_name in SCAN_ROOTS:
        root = REPO / root_name
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if any(part in SKIP_PARTS for part in p.parts):
                continue
            if p.suffix not in {".py", ".md", ".mdc", ".yml", ".yaml", ".json"}:
                continue
            out.append(p)
    return out


def _rel(p: Path) -> str:
    return p.relative_to(REPO).as_posix()


def _classify_path(rel: str) -> str:
    if rel.startswith("tests/"):
        return "test"
    if rel.startswith("ops_scripts/"):
        return "ci"
    if rel.startswith("docs/") or rel.startswith(".cursor/"):
        return "doc"
    return "py"


def scan_candidate(cand: dict[str, str], files: list[Path]) -> FaninRow:
    patterns = [re.compile(p) for p in cand["patterns"]]
    hits: dict[str, set[str]] = {"py": set(), "test": set(), "doc": set(), "ci": set(), "env": set()}
    self_path = cand["path"].replace("*", "").rstrip("/")

    for fp in files:
        rel = _rel(fp)
        if self_path and self_path in rel and not cand["path"].endswith("*"):
            continue
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not any(p.search(text) for p in patterns):
            continue
        bucket = _classify_path(rel)
        if "APPS_RG_" in cand["path"] or cand["path"].startswith("--"):
            hits["env"].add(rel)
        elif bucket == "test":
            hits["test"].add(rel)
        elif bucket == "doc":
            hits["doc"].add(rel)
        elif bucket == "ci":
            hits["ci"].add(rel)
        else:
            hits["py"].add(rel)

    py_imports = sorted(hits["py"] | hits["ci"])
    test_refs = sorted(hits["test"])
    doc_refs = sorted(hits["doc"])
    env_refs = sorted(hits["env"])
    fan_in = len(py_imports) + len(test_refs)

    row = FaninRow(
        id=cand["id"],
        path=cand["path"],
        current_classification=cand["current_classification"],
        proposed_final_classification="NEEDS_DECISION",
        active_path_confidence="LOW",
        fan_in_count=fan_in,
        importers_py=py_imports[:40],
        importers_tests=test_refs[:40],
        importers_docs=doc_refs[:20],
        importers_ci=[p for p in py_imports if p.startswith("ops_scripts/")][:20],
        env_cli_refs=env_refs[:20],
    )
    _propose_classification(row, cand)
    return row


def _propose_classification(row: FaninRow, cand: dict[str, str]) -> None:
    cid = cand["id"]
    product_py = [
        p
        for p in row.importers_py
        if p.startswith("apps_rg/runtime/sections/")
        or p.startswith("apps_rg/__main__")
        or "canonical_dispatch" in p
        or "apps_rg_dispatch" in p
    ]
    if product_py:
        row.active_path_confidence = "MEDIUM"
        row.blocker = f"product-adjacent refs: {product_py[:3]}"

    if cid == "shim_apps_rg_l2_binding":
        row.proposed_final_classification = "ARCHIVED"
        row.migration_required = False
        row.delete_readiness = "NO"
        row.archive_readiness = "DONE"
        row.active_path_confidence = "LOW"
        row.blocker = "W11-SHIM-ARCHIVE complete; file under archives/l2_rationalization_*/"
    elif cid == "validation_orchestrator":
        ext = [p for p in row.importers_py if "validation_orchestrator.py" not in p]
        if not ext:
            row.proposed_final_classification = "ARCHIVE_CANDIDATE"
            row.migration_required = False
            row.delete_readiness = "NO"
            row.blocker = "ADG fan-in confirm + 30d quarantine before delete"
            row.active_path_confidence = "LOW"
        else:
            row.proposed_final_classification = "QUARANTINE_30D"
            row.blocker = f"non-self refs: {ext[:5]}"
    elif cid == "agentic_core_smoke":
        row.proposed_final_classification = "KEEP_TEST_SUPPORT_ONLY"
        row.migration_required = len(row.importers_tests) > 0
        row.delete_readiness = "NO"
        row.blocker = "smoke harness tests depend on module"
    elif cid == "code_quality_examples":
        row.proposed_final_classification = "ARCHIVE_CANDIDATE"
        row.delete_readiness = "NO" if row.fan_in_count else "NO"
        row.migration_required = row.fan_in_count > 0
    elif cid == "dry_run_dir":
        row.proposed_final_classification = "QUARANTINE_30D"
        row.delete_readiness = "NO"
        row.active_path_confidence = "LOW"
    elif cid == "orchestrate_full_resume":
        row.proposed_final_classification = "KEEP_TEST_SUPPORT_ONLY"
        row.delete_readiness = "NO"
        row.blocker = "offline modular orchestrator; tests + docs reference"
        row.active_path_confidence = "MEDIUM"
    elif cid == "rg_reasoning_agents":
        row.proposed_final_classification = "ARCHIVE_CANDIDATE"
        row.migration_required = row.fan_in_count > 0
        row.delete_readiness = "NO"
        row.blocker = "fan-in from tests/facades must hit zero"
    elif cid == "deprecated_dispatch_clis":
        row.proposed_final_classification = "DOC_DEPRECATE_ONLY"
        row.delete_readiness = "NO"
        row.blocker = "modules still importable; exit_deprecated_dispatch_cli guard"
    elif cid in ("legacy_full_resume_env", "offline_contract_stub_env", "stub_only_provider_env", "mock_judges_cli"):
        row.proposed_final_classification = cand["current_classification"]
        row.migration_required = False
        row.delete_readiness = "NO"
        row.active_path_confidence = "HIGH" if cid == "legacy_full_resume_env" else "MEDIUM"
        row.blocker = "rollback/test hatch — keep env surface"
    elif cid == "apps_shared_signal_stubs":
        row.proposed_final_classification = "QUARANTINE_30D"
        row.migration_required = True
        row.delete_readiness = "NO"
        row.blocker = "W4 QUARANTINE — wire or replace before delete"


def adg_fanin_for_file(rel_path: str) -> tuple[str, int | None]:
    if "*" in rel_path or rel_path.startswith("APPS_RG") or rel_path.startswith("--"):
        return "NOT_APPLICABLE", None
    if not rel_path.endswith(".py"):
        return "NOT_APPLICABLE", None
    try:
        proc = subprocess.run(
            [
                "python",
                str(REPO / "tools" / "mcp" / "adg_sqlite_mcp_bridge.py"),
            ],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(REPO),
        )
    except Exception:
        return "NOT_AVAILABLE", None
    return "NOT_AVAILABLE", None


def main() -> None:
    files = _iter_scan_files()
    rows = [scan_candidate(c, files) for c in CANDIDATES]
    out = REPO / "docs/reports/agent_inventory/w11_candidate_fanin_matrix.json"
    payload = {
        "generated_at": "2026-05-19",
        "scan_roots": list(SCAN_ROOTS),
        "note": "Static grep/import scan — not runtime reachability proof",
        "candidates": [asdict(r) for r in rows],
        "summary": {
            "delete_ready_count": sum(1 for r in rows if r.delete_readiness == "YES"),
            "archive_ready_count": sum(1 for r in rows if r.archive_readiness == "YES"),
            "migration_required_count": sum(1 for r in rows if r.migration_required),
            "blocked_count": sum(1 for r in rows if r.blocker),
        },
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))


if __name__ == "__main__":
    main()
