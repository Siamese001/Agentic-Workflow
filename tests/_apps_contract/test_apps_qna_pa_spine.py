"""Contract tests: apps_qna PA spine hardening — W5 P5.1.

Plan: .windsurf/plans/apps-qna-pa-spine-hardening-498d20.md W4
Parent: apps-rg-spine-hardening-deferred-wave-2f8b1d W5
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCANNER = REPO_ROOT / "ops_scripts" / "ci" / "check_apps_rg_pa_boundary.py"
QNA_AIRLOCKS = REPO_ROOT / "apps_qna" / "airlocks"
QNA_LLM_CLIENT = REPO_ROOT / "apps_qna" / "integrations" / "llm_client.py"
QNA_DISPATCH = REPO_ROOT / "apps_qna" / "engines" / "dispatch" / "provider_dispatch.py"
QNA_INTENT = REPO_ROOT / "apps_qna" / "integrations" / "intent_classifier.py"
QNA_JUDGE = REPO_ROOT / "apps_qna" / "engines" / "judges" / "interview_card_quality_judge.py"


def _load_scanner_source() -> str:
    return SCANNER.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# W2 — Scanner coverage
# ---------------------------------------------------------------------------


def test_scanner_allowlist_contains_qna_llm_client() -> None:
    """apps_qna/integrations/llm_client.py (sanctioned shim) must be in ALLOWLIST_FILES."""
    src = _load_scanner_source()
    assert "apps_qna/integrations/llm_client.py" in src, (
        "llm_client.py shim must be in ALLOWLIST_FILES — it re-exports from infrastructure/sdks_mcps"
    )


def test_scanner_conditional_v1_baseline_contains_qna_dispatch() -> None:
    """provider_dispatch.py must be in CONDITIONAL_V1_BASELINE."""
    src = _load_scanner_source()
    assert "apps_qna/engines/dispatch/provider_dispatch.py" in src, (
        "provider_dispatch.py uses direct anthropic.Anthropic() (lazy, env-gated); must be baselined"
    )


def test_scanner_conditional_v1_baseline_contains_qna_intent() -> None:
    """intent_classifier.py must be in CONDITIONAL_V1_BASELINE."""
    src = _load_scanner_source()
    assert "apps_qna/integrations/intent_classifier.py" in src, (
        "intent_classifier.py uses direct SDK calls (lazy, env-gated); must be baselined"
    )


def test_scanner_conditional_v1_baseline_contains_qna_judge() -> None:
    """interview_card_quality_judge.py must be in CONDITIONAL_V1_BASELINE."""
    src = _load_scanner_source()
    assert "apps_qna/engines/judges/interview_card_quality_judge.py" in src, (
        "interview_card_quality_judge.py uses direct anthropic SDK (lazy); must be baselined"
    )


def test_scanner_conditional_v1_baseline_contains_qna_provider_adapter() -> None:
    """provider_adapter.py must be in CONDITIONAL_V1_BASELINE."""
    src = _load_scanner_source()
    assert "apps_qna/integrations/provider_adapter.py" in src, (
        "provider_adapter.py has lazy direct SDK calls (env-gated); must be baselined"
    )


def test_scanner_has_apps_qna_iter_function() -> None:
    """Scanner must have _iter_apps_qna_files() to scan apps_qna surface."""
    src = _load_scanner_source()
    assert "_iter_apps_qna_files" in src, (
        "Scanner must define _iter_apps_qna_files() to cover apps_qna PA surface"
    )


def test_scanner_no_apps_qna_flag_present() -> None:
    """Scanner must expose --no-apps-qna CLI flag for targeted runs."""
    src = _load_scanner_source()
    assert "--no-apps-qna" in src, (
        "Scanner must have --no-apps-qna flag so apps_rg-only runs are still possible"
    )


# ---------------------------------------------------------------------------
# W3 — Airlocks exist
# ---------------------------------------------------------------------------


def test_airlocks_directory_exists() -> None:
    """apps_qna/airlocks/ directory must exist."""
    assert QNA_AIRLOCKS.is_dir(), "apps_qna/airlocks/ must exist (W3 deliverable)"


def test_airlock_init_imports_otel_spans() -> None:
    """apps_qna/airlocks/__init__.py must import airlock_span."""
    init = QNA_AIRLOCKS / "__init__.py"
    assert init.exists(), "airlocks/__init__.py must exist"
    src = init.read_text(encoding="utf-8")
    assert "airlock_span" in src


def test_template_input_airlock_exists_and_has_validate_function() -> None:
    """template_input.py airlock must exist and export validate_template_inputs()."""
    gate = QNA_AIRLOCKS / "template_input.py"
    assert gate.exists(), "template_input.py must exist for build_time_compiler route"
    src = gate.read_text(encoding="utf-8")
    assert "def validate_template_inputs" in src, "validate_template_inputs() must be defined"


def test_user_question_airlock_exists_and_has_validate_function() -> None:
    """user_question.py airlock must exist and export validate_user_question()."""
    gate = QNA_AIRLOCKS / "user_question.py"
    assert gate.exists(), "user_question.py must exist for R4_SINGLE_ACTION route"
    src = gate.read_text(encoding="utf-8")
    assert "def validate_user_question" in src, "validate_user_question() must be defined"


def test_otel_spans_module_exists() -> None:
    """_otel_spans.py must exist in apps_qna/airlocks/."""
    otel = QNA_AIRLOCKS / "_otel_spans.py"
    assert otel.exists(), "_otel_spans.py must exist (OTEL span helper)"


def test_otel_spans_uses_apps_qna_tracer() -> None:
    """_otel_spans.py must use apps_qna.airlocks tracer name (not apps_rg)."""
    otel = QNA_AIRLOCKS / "_otel_spans.py"
    src = otel.read_text(encoding="utf-8")
    assert "apps_qna.airlocks" in src, "_otel_spans.py tracer must be namespaced to apps_qna"


# ---------------------------------------------------------------------------
# W1 — llm_client.py is a sanctioned shim (no direct construction)
# ---------------------------------------------------------------------------


def test_llm_client_shim_imports_from_infrastructure() -> None:
    """apps_qna/integrations/llm_client.py must import from infrastructure.sdks_mcps."""
    assert QNA_LLM_CLIENT.exists(), "llm_client.py must exist"
    src = QNA_LLM_CLIENT.read_text(encoding="utf-8")
    assert "infrastructure.sdks_mcps" in src, (
        "llm_client.py must re-export from infrastructure.sdks_mcps (sanctioned path)"
    )


def test_llm_client_shim_has_no_direct_construction() -> None:
    """llm_client.py must not construct Anthropic() or OpenAI() directly."""
    src = QNA_LLM_CLIENT.read_text(encoding="utf-8")
    assert "Anthropic(" not in src or "create_anthropic_client" in src, (
        "llm_client.py must not construct Anthropic() directly — use infrastructure.sdks_mcps"
    )


def test_dispatch_direct_sdk_is_lazy_import() -> None:
    """provider_dispatch.py SDK call must be inside a lazy import guard (not top-level)."""
    assert QNA_DISPATCH.exists()
    src = QNA_DISPATCH.read_text(encoding="utf-8")
    # Lazy import pattern: `import anthropic` inside a function body
    assert "def _call_anthropic" in src or "def _call_" in src, (
        "provider_dispatch.py SDK call must be inside a function (lazy import)"
    )
    tree = ast.parse(src)
    top_level_anthropic = False
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            src_piece = ast.unparse(node)
            if "anthropic" in src_piece:
                top_level_anthropic = True
    assert not top_level_anthropic, (
        "anthropic import in provider_dispatch.py must not be top-level — must be lazy inside function"
    )
