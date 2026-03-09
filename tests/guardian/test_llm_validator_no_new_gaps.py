"""Guardian test: no new un-allowlisted LLM calls in validation/scoring paths.

Runs the AST scanner and asserts the allowlist count has not grown.
Fails CI when any new LLM-validator call is detected outside the approved list.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER = REPO_ROOT / "ops_scripts" / "ci" / "scan_llm_validator_calls.py"
ALLOWLIST = REPO_ROOT / "ops_scripts" / "ci" / "llm_validator_allowlist.json"

sys.path.insert(0, str(REPO_ROOT / "ops_scripts" / "ci"))


def _import_scanner():
    import importlib.util

    spec = importlib.util.spec_from_file_location("scan_llm_validator_calls", SCANNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_scanner_and_allowlist_exist() -> None:
    assert SCANNER.exists(), f"Scanner missing: {SCANNER}"
    assert ALLOWLIST.exists(), f"Allowlist missing: {ALLOWLIST}"


def test_allowlist_schema() -> None:
    import json

    data = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
    assert "allowed_llm_validators" in data, "Allowlist missing 'allowed_llm_validators' key"
    entries = data["allowed_llm_validators"]
    assert isinstance(entries, list), "'allowed_llm_validators' must be a list"
    for entry in entries:
        for required_key in ("file", "func", "gap_id", "hardened", "justification"):
            assert required_key in entry, f"Entry missing key '{required_key}': {entry}"
        assert isinstance(entry["hardened"], bool), f"'hardened' must be bool in: {entry}"


def test_no_new_llm_validator_calls() -> None:
    """AST scan: zero un-allowlisted LLM calls in validation paths."""
    scanner = _import_scanner()
    allowlist = scanner._load_allowlist(ALLOWLIST)

    all_hits = []
    scan_roots = ["agentic_core", "apps_lic", "apps_rg", "apps_shared", "system_learning"]
    for root_name in scan_roots:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for py_file in root.rglob("*.py"):
            if "__pycache__" in py_file.parts:
                continue
            all_hits.extend(scanner.scan_file(py_file))

    new_hits = [h for h in all_hits if f"{h.file}::{h.func_name}" not in allowlist]

    if new_hits:
        lines = [
            f"  {h.file}:{h.line}  func={h.func_name}  call={h.call_expr}  [{h.gap_hint}]" for h in new_hits
        ]
        msg = (
            f"Found {len(new_hits)} NEW un-allowlisted LLM call(s) in validation paths.\n"
            "Add to ops_scripts/ci/llm_validator_allowlist.json with human reviewer sign-off "
            "OR refactor to remove the LLM dependency.\n\n" + "\n".join(lines)
        )
        pytest.fail(msg)


def test_ml_import_count_does_not_grow() -> None:
    """ML library imports outside approved seams must not increase."""
    scanner = _import_scanner()

    ml_hits = []
    scan_roots = ["agentic_core", "apps_lic", "apps_rg", "apps_shared", "system_learning"]
    for root_name in scan_roots:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for py_file in root.rglob("*.py"):
            if "__pycache__" in py_file.parts:
                continue
            ml_hits.extend(scanner.check_ml_imports(py_file))

    CEILING = 20
    if len(ml_hits) > CEILING:
        lines = [f"  {h.file}:{h.line}  {h.call_expr}" for h in ml_hits]
        pytest.fail(
            f"ML library imports ({len(ml_hits)}) exceeded ceiling ({CEILING}). "
            f"New ML imports require explicit approval.\n" + "\n".join(lines)
        )


def test_allowlist_entries_reference_real_files() -> None:
    """Every allowlist entry must point to a file that exists in the repo."""
    import json

    data = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
    missing = []
    for entry in data.get("allowed_llm_validators", []):
        fpath = REPO_ROOT / entry["file"]
        if not fpath.exists():
            missing.append(entry["file"])

    if missing:
        pytest.fail(
            f"{len(missing)} allowlist entry/entries point to non-existent files:\n"
            + "\n".join(f"  {f}" for f in missing)
        )
