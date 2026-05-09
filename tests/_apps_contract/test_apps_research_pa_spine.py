"""Contract tests: apps_research PA spine hardening — W5 P5.2.

Plan: apps-research-pa-spine-hardening-a28ea8
Parent: apps-pa-spine-w5-remaining-7e820f
"""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER = REPO_ROOT / "ops_scripts" / "ci" / "check_apps_rg_pa_boundary.py"
RESEARCH_AIRLOCKS = REPO_ROOT / "apps_research" / "airlocks"
RESEARCH_LLM_CLIENT = REPO_ROOT / "apps_research" / "integrations" / "llm_client.py"
RESEARCH_BRIEF_ENGINE = REPO_ROOT / "apps_research" / "engines" / "company_brief_engine.py"


def _load_scanner_source() -> str:
    return SCANNER.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# W2 — Scanner coverage
# ---------------------------------------------------------------------------


def test_scanner_allowlist_contains_research_llm_client() -> None:
    """apps_research/integrations/llm_client.py (sanctioned shim) must be in ALLOWLIST_FILES."""
    src = _load_scanner_source()
    assert "apps_research/integrations/llm_client.py" in src


def test_scanner_conditional_v1_baseline_contains_brief_engine() -> None:
    """company_brief_engine.py must be in CONDITIONAL_V1_BASELINE."""
    src = _load_scanner_source()
    assert "apps_research/engines/company_brief_engine.py" in src


def test_scanner_has_apps_research_iter_function() -> None:
    """Scanner must have _iter_apps_research_files() to scan apps_research surface."""
    src = _load_scanner_source()
    assert "_iter_apps_research_files" in src


def test_scanner_no_apps_research_flag_present() -> None:
    """Scanner must expose --no-apps-research CLI flag."""
    src = _load_scanner_source()
    assert "--no-apps-research" in src


# ---------------------------------------------------------------------------
# W3 — Airlocks exist
# ---------------------------------------------------------------------------


def test_airlocks_directory_exists() -> None:
    assert RESEARCH_AIRLOCKS.is_dir(), "apps_research/airlocks/ must exist"


def test_airlock_init_imports_otel_spans() -> None:
    init = RESEARCH_AIRLOCKS / "__init__.py"
    assert init.exists()
    assert "airlock_span" in init.read_text(encoding="utf-8")


def test_research_query_airlock_exists_and_has_validate_function() -> None:
    gate = RESEARCH_AIRLOCKS / "research_query.py"
    assert gate.exists(), "research_query.py must exist for R3_SIMPLE_GROUNDED_READ route"
    assert "def validate_research_query" in gate.read_text(encoding="utf-8")


def test_otel_spans_module_exists() -> None:
    assert (RESEARCH_AIRLOCKS / "_otel_spans.py").exists()


def test_otel_spans_uses_apps_research_tracer() -> None:
    src = (RESEARCH_AIRLOCKS / "_otel_spans.py").read_text(encoding="utf-8")
    assert "apps_research.airlocks" in src


# ---------------------------------------------------------------------------
# W1 — llm_client.py is a sanctioned shim
# ---------------------------------------------------------------------------


def test_llm_client_shim_imports_from_infrastructure() -> None:
    assert RESEARCH_LLM_CLIENT.exists()
    src = RESEARCH_LLM_CLIENT.read_text(encoding="utf-8")
    assert "infrastructure.sdks_mcps" in src or "infrastructure" in src


def test_brief_engine_uses_sanctioned_shim_not_raw_openai() -> None:
    """company_brief_engine.py must import OpenAI via apps_research.integrations.llm_client."""
    src = RESEARCH_BRIEF_ENGINE.read_text(encoding="utf-8")
    assert "apps_research.integrations.llm_client" in src, (
        "company_brief_engine must import via sanctioned llm_client shim"
    )
    # Top-level raw openai import is forbidden; lazy import inside function is permitted
    tree = ast.parse(src)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            unparsed = ast.unparse(node)
            assert "openai" not in unparsed or "llm_client" in unparsed, (
                "Top-level raw openai import in company_brief_engine.py is forbidden"
            )
