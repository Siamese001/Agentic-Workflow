"""REQ-415: Provider substitution negative control.

check_llm_sdk_imports.py must catch direct SDK imports outside the gateway seam.
providers_anthropic_client_util.py must NOT appear in ALLOWED_PATHS after W1.3.
Enforcement layers: AST (CI guard) + Runtime (gateway delegation).
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.governance


def test_allowlist_excludes_anthropic_util():
    """providers_anthropic_client_util.py must not be in ALLOWED_PATHS after W1.3."""
    from ops_scripts.ci import check_llm_sdk_imports

    assert "apps_rg/utils/providers_anthropic_client_util.py" not in check_llm_sdk_imports.ALLOWED_PATHS, (
        "anthropic_util must be removed from ALLOWED_PATHS after gateway delegation (W1.3)"
    )


def test_blocked_sdk_import_detected(tmp_path):
    """CI guard must return exit code 1 for a file with a blocked SDK import."""
    bad_file = tmp_path / "bad_module.py"
    bad_file.write_text("import anthropic\n")

    from ops_scripts.ci import check_llm_sdk_imports

    original_scan_roots = check_llm_sdk_imports.SCAN_ROOTS
    original_repo_root = check_llm_sdk_imports.REPO_ROOT
    try:
        check_llm_sdk_imports.REPO_ROOT = tmp_path.parent
        check_llm_sdk_imports.SCAN_ROOTS = [tmp_path.name]
        rc = check_llm_sdk_imports.main()
    finally:
        check_llm_sdk_imports.SCAN_ROOTS = original_scan_roots
        check_llm_sdk_imports.REPO_ROOT = original_repo_root

    assert rc == 1, "CI guard must return exit code 1 for blocked SDK import"


def test_clean_file_passes_sdk_check(tmp_path):
    """CI guard must return exit code 0 for a file with no blocked imports."""
    clean_file = tmp_path / "clean_module.py"
    clean_file.write_text("def hello():\n    return 'hello'\n")

    from ops_scripts.ci import check_llm_sdk_imports

    original_scan_roots = check_llm_sdk_imports.SCAN_ROOTS
    original_repo_root = check_llm_sdk_imports.REPO_ROOT
    try:
        check_llm_sdk_imports.REPO_ROOT = tmp_path.parent
        check_llm_sdk_imports.SCAN_ROOTS = [tmp_path.name]
        rc = check_llm_sdk_imports.main()
    finally:
        check_llm_sdk_imports.SCAN_ROOTS = original_scan_roots
        check_llm_sdk_imports.REPO_ROOT = original_repo_root

    assert rc == 0, "CI guard must return exit code 0 for clean file"


def test_sovereign_gateway_is_sole_allowed_openai_seam():
    """SovereignLLMGateway.py must remain the only allowed seam for openai SDK."""
    from ops_scripts.ci import check_llm_sdk_imports

    allowed = check_llm_sdk_imports.ALLOWED_PATHS
    assert "agentic_core/L2_execution/enforcement/SovereignLLMGateway.py" in allowed, (
        "SovereignLLMGateway.py must remain in ALLOWED_PATHS as the gateway seam"
    )
    openai_seams = [p for p in allowed if "openai" in p.lower()]
    assert len(openai_seams) <= 1, f"Only one openai seam allowed; found: {openai_seams}"
