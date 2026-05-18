"""W5 — apps_rg R1B RCA Decision Tests.

Validates the W5 RCA outcome for GAP-09 (apps_rg R1B quarantine decision).

Decision: KEEP_QUARANTINED_DEPRECATED
- apps_rg/cache/r1b_adapter.py remains quarantined and deprecated.
- Generic R1B path via package_driven_l0_binding is used instead.
- apps_rg cache profile flipped to live_wiring_deferred: false.

Plan: chroma-graphrag-core-wiring-gaps-b3f7a1 W5
RCA: docs/architecture/rca/RCA_apps_rg_r1b_adapter_L4_import_violation.md
"""

from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parents[2]

# Key paths
RCA_DOC = REPO_ROOT / "docs" / "architecture" / "rca" / "RCA_apps_rg_r1b_adapter_L4_import_violation.md"
QUARANTINED_ADAPTER = REPO_ROOT / "apps_rg" / "cache" / "r1b_adapter.py"
APPS_RG_CACHE_PROFILE = REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "cache_profiles.yaml"
APPS_RG_ROUTE_PROFILE = REPO_ROOT / "apps_rg" / "config" / "domain_contract" / "route_profiles.yaml"
APPS_LIC_CACHE_PROFILE = REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "cache_profiles.yaml"
APPS_LIC_ROUTE_PROFILE = REPO_ROOT / "apps_lic" / "config" / "domain_contract" / "route_profiles.yaml"
L0_BINDING = REPO_ROOT / "agentic_core" / "L0_routing" / "package_driven_l0_binding.py"

# W5 RCA decision constants
_EXPECTED_WIRING_GATE = "CLEARED_BY_W1_GENERIC_R1B_CACHE_WIRING"
_EXPECTED_DECISION = "KEEP_QUARANTINED_DEPRECATED"


# ---------------------------------------------------------------------------
# W5-1: RCA document
# ---------------------------------------------------------------------------

def test_apps_rg_r1b_rca_doc_exists() -> None:
    """W5-1: RCA document must exist at the canonical path."""
    assert RCA_DOC.exists(), (
        f"RCA document missing: {RCA_DOC}"
    )


def test_apps_rg_r1b_rca_decision_recorded() -> None:
    """W5-2: RCA document must record the KEEP_QUARANTINED_DEPRECATED decision."""
    content = RCA_DOC.read_text(encoding="utf-8")
    assert _EXPECTED_DECISION in content, (
        f"RCA doc must contain decision '{_EXPECTED_DECISION}'"
    )
    assert "KEEP_QUARANTINED_DEPRECATED" in content
    assert "obsolete" in content.lower() or "deprecated" in content.lower(), (
        "RCA must state adapter is obsolete/deprecated"
    )


# ---------------------------------------------------------------------------
# W5-3: Generic R1B path availability
# ---------------------------------------------------------------------------

def test_apps_rg_generic_r1b_path_available() -> None:
    """W5-3: Generic R1B path must be present in package_driven_l0_binding."""
    source = L0_BINDING.read_text(encoding="utf-8")
    assert "_read_semantic_cache_profile" in source, (
        "Generic _read_semantic_cache_profile() must exist in L0 binding"
    )
    assert "check_d2_semantic_cache" in source, (
        "check_d2_semantic_cache() call must exist in L0 binding"
    )


def test_apps_rg_cache_profile_live_wiring_decision_correct() -> None:
    """W5-4: apps_rg cache profile must have live_wiring_deferred: false and correct wiring_gate."""
    data = yaml.safe_load(APPS_RG_CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data.get("semantic_cache", {})
    assert sc.get("enabled") is True, "apps_rg semantic_cache.enabled must be true"
    assert sc.get("live_wiring_deferred") is False, (
        f"apps_rg live_wiring_deferred must be false after W5 flip, got {sc.get('live_wiring_deferred')!r}"
    )
    assert sc.get("wiring_gate") == _EXPECTED_WIRING_GATE, (
        f"apps_rg wiring_gate must be '{_EXPECTED_WIRING_GATE}', got {sc.get('wiring_gate')!r}"
    )


# ---------------------------------------------------------------------------
# W5-5: Quarantine guard still active
# ---------------------------------------------------------------------------

def test_apps_rg_r1b_adapter_w7_active_not_quarantined() -> None:
    """W7: apps_rg/cache/r1b_adapter.py is the active ROLE_TARGET_RUN implementation (quarantine cleared)."""
    assert QUARANTINED_ADAPTER.exists(), "R1B adapter file must exist"
    import apps_rg.cache.r1b_adapter as mod  # noqa: F401

    assert hasattr(mod, "check_r1b_for_apps_rg")
    assert hasattr(mod, "AppsRgR1BCacheAdapter")


def test_apps_rg_r1b_adapter_no_direct_l4_import() -> None:
    """W5-6: Quarantined adapter source must not contain a live L4_state import statement.

    The quarantine guard (RuntimeError) fires before any import executes.
    The file is allowed to *mention* L4_state in comments and docstrings,
    but must not contain an executable ``import`` or ``from … import`` line
    referencing L4_state.
    """
    source = QUARANTINED_ADAPTER.read_text(encoding="utf-8")
    # Extract only executable lines: strip blank lines, docstring bodies,
    # and comment lines.  We use a simple state-machine: skip lines inside
    # triple-quoted strings (docstrings).
    executable_lines: list[str] = []
    in_docstring = False
    for raw in source.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        # Toggle triple-quote docstring state
        if stripped.startswith('"""') or stripped.startswith("'''"):
            # A line that opens AND closes on the same line is a one-liner
            # docstring — still not executable.
            in_docstring = not in_docstring
            continue
        if in_docstring:
            continue
        if stripped.startswith("#"):
            continue
        executable_lines.append(stripped)
    l4_imports = [
        ln for ln in executable_lines
        if "L4_state" in ln and ("import" in ln)
    ]
    assert not l4_imports, (
        f"Quarantined adapter must not contain live L4_state imports: {l4_imports}"
    )


def test_apps_rg_r1b_adapter_not_imported_by_generic_l0_path() -> None:
    """W5-7: Generic L0 binding must not import from apps_rg.cache.r1b_adapter."""
    source = L0_BINDING.read_text(encoding="utf-8")
    assert "r1b_adapter" not in source, (
        "package_driven_l0_binding.py must not import apps_rg.cache.r1b_adapter"
    )
    assert "apps_rg.cache" not in source, (
        "package_driven_l0_binding.py must not import from apps_rg.cache"
    )


# ---------------------------------------------------------------------------
# W5-8: apps_rg semantic cache live
# ---------------------------------------------------------------------------

def test_apps_rg_semantic_cache_enabled_true() -> None:
    """W5-8: apps_rg semantic_cache.enabled must be true (R1B eligible)."""
    data = yaml.safe_load(APPS_RG_CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data.get("semantic_cache", {})
    assert sc.get("enabled") is True, (
        "apps_rg semantic_cache.enabled must be true for generic R1B to activate"
    )


def test_apps_rg_semantic_cache_live_wiring_deferred_false_if_generic_path_selected() -> None:
    """W5-9: apps_rg live_wiring_deferred must be false — generic path selected."""
    data = yaml.safe_load(APPS_RG_CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data.get("semantic_cache", {})
    assert sc.get("live_wiring_deferred") is False, (
        "apps_rg live_wiring_deferred must be false (generic path selected in W5)"
    )


# ---------------------------------------------------------------------------
# W5-10/11: apps_lic boundary invariants (must not change)
# ---------------------------------------------------------------------------

def test_apps_lic_semantic_cache_still_disabled() -> None:
    """W5-10: apps_lic semantic_cache.enabled must remain false (GAP-08 non-goal)."""
    data = yaml.safe_load(APPS_LIC_CACHE_PROFILE.read_text(encoding="utf-8"))
    sc = data.get("semantic_cache", {})
    assert sc.get("enabled") is False, (
        f"apps_lic semantic_cache.enabled must remain false, got {sc.get('enabled')!r}"
    )


def test_apps_lic_r1b_absent_from_route_order() -> None:
    """W5-11: apps_lic route evaluation order must not include R1B_SEMANTIC_CACHE."""
    data = yaml.safe_load(APPS_LIC_ROUTE_PROFILE.read_text(encoding="utf-8"))
    # apps_lic route profile is a YAML list of profile dicts
    if isinstance(data, list):
        profile = data[0] if data else {}
    elif isinstance(data, dict):
        profile = data if "route_evaluation_order" in data else next(iter(data.values()), {})
    else:
        profile = {}
    route_ids = [r.get("route_id", "") for r in profile.get("route_evaluation_order", [])]
    assert "R1B_SEMANTIC_CACHE" not in route_ids, (
        f"apps_lic route order must not include R1B_SEMANTIC_CACHE, found: {route_ids}"
    )


# ---------------------------------------------------------------------------
# W5-12/13/14: Regression guards
# ---------------------------------------------------------------------------

def test_w1_r1b_tests_still_pass() -> None:
    """W5-12: W1 R1B cache wiring tests must still pass (no regression from W5 profile flip)."""
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/_apps_contract/test_w1_core_r1b_cache_wiring.py",
            "-q", "--tb=short", "--no-header",
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"W1 R1B tests regressed after W5 profile flip:\n{result.stdout}\n{result.stderr}"
    )


def test_w4_graph_rag_tests_still_pass() -> None:
    """W5-13: W4 graph RAG tests must still pass (W5 must not touch C0.3)."""
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/_apps_contract/test_w4_graph_rag_execution.py",
            "-q", "--tb=short", "--no-header",
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"W4 graph RAG tests regressed after W5:\n{result.stdout}\n{result.stderr}"
    )


def test_no_ingestion_changed_in_w5() -> None:
    """W5-14: W5 must not have introduced ingestion pipeline content.

    W5 original: asserted chroma_ingest_pipeline.py does NOT exist (W6 scope).
    W6 update: the file now exists — created by W6 as expected. The W5 invariant
    is that apps_rg-touched files do NOT reference sentence-transformers.
    """
    ingestion_pipeline = REPO_ROOT / "tools" / "ingestion" / "chroma_ingest_pipeline.py"
    # W6 created this file — confirm it is W6-scoped (contains W6 marker)
    if ingestion_pipeline.exists():
        content = ingestion_pipeline.read_text(encoding="utf-8")
        assert "process_docs" in content, (
            "chroma_ingest_pipeline.py must target process_docs collection (W6 invariant)"
        )
        assert "BAAI/bge-m3" in content, (
            "chroma_ingest_pipeline.py must use BAAI/bge-m3 (W6 invariant)"
        )
    # W5 core invariant: apps_rg-touched files must not reference sentence-transformers
    for path in (QUARANTINED_ADAPTER, APPS_RG_CACHE_PROFILE):
        if path.suffix == ".py":
            source = path.read_text(encoding="utf-8")
            assert "sentence_transformers" not in source and "SentenceTransformer" not in source, (
                f"{path.name} must not reference sentence-transformers (W6 scope, not W5)"
            )
