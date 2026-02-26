"""Tests for Phase 5 AST scanner gap closure.

Phase 5: AST scanner gap closure (3 scanners).
Verifies check_embedding_instantiation, check_layer_write_sovereignty, and
the extended check_llm_sdk_imports (embedding SDKs added) all produce
deterministic OK/FAIL results on synthetic inputs.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[4]
CI_DIR = REPO_ROOT / "ops_scripts" / "ci"


def _run_scanner(name: str) -> tuple[int, str]:
    """Run a CI scanner script and return (exit_code, stdout)."""
    result = subprocess.run(
        [sys.executable, str(CI_DIR / name)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout + result.stderr


class TestEmbeddingInstantiationScanner:
    def test_scanner_exits_zero_on_clean_repo(self):
        code, output = _run_scanner("check_embedding_instantiation.py")
        assert code == 0, f"Scanner reported violations:\n{output}"

    def test_scanner_ok_message_present(self):
        code, output = _run_scanner("check_embedding_instantiation.py")
        assert "OK:" in output

    def test_scanner_detects_blocked_constructor(self, tmp_path):
        """Unit-level: _find_violations detects OpenAIEmbedder() call."""
        import ast

        from ops_scripts.ci.check_embedding_instantiation import _find_violations

        source = "x = OpenAIEmbedder(api_key='k')\n"
        path = tmp_path / "bad_file.py"
        path.write_text(source, encoding="utf-8")
        violations = _find_violations(path, "test/bad_file.py")
        assert len(violations) == 1
        assert "OpenAIEmbedder" in violations[0]

    def test_scanner_allows_non_blocked_call(self, tmp_path):
        from ops_scripts.ci.check_embedding_instantiation import _find_violations

        source = "x = SomeOtherClass()\n"
        path = tmp_path / "clean_file.py"
        path.write_text(source, encoding="utf-8")
        violations = _find_violations(path, "test/clean_file.py")
        assert violations == []

    def test_scanner_detects_attribute_style_call(self, tmp_path):
        from ops_scripts.ci.check_embedding_instantiation import _find_violations

        source = "x = module.LocalFAISSStore(path='/data')\n"
        path = tmp_path / "bad2.py"
        path.write_text(source, encoding="utf-8")
        violations = _find_violations(path, "test/bad2.py")
        assert len(violations) == 1
        assert "LocalFAISSStore" in violations[0]


class TestLayerWriteSovereigntyScanner:
    def test_scanner_exits_zero_on_clean_repo(self):
        code, output = _run_scanner("check_layer_write_sovereignty.py")
        assert code == 0, f"Scanner reported violations:\n{output}"

    def test_scanner_ok_message_present(self):
        code, output = _run_scanner("check_layer_write_sovereignty.py")
        assert "OK:" in output


class TestLLMSdkImportScanner:
    def test_embedding_sdks_in_blocked_list(self):
        from ops_scripts.ci.check_llm_sdk_imports import BLOCKED_TOP_LEVEL

        assert "faiss" in BLOCKED_TOP_LEVEL
        assert "sentence_transformers" in BLOCKED_TOP_LEVEL
        assert "tiktoken" in BLOCKED_TOP_LEVEL

    def test_factory_seam_in_allowed_paths(self):
        from ops_scripts.ci.check_llm_sdk_imports import ALLOWED_PATHS

        assert "system_learning/engines/embedding_service_factory.py" in ALLOWED_PATHS

    def test_blocked_function_identifies_faiss(self):
        import ast

        from ops_scripts.ci.check_llm_sdk_imports import _blocked

        source = "import faiss\n"
        tree = ast.parse(source)
        import_node = tree.body[0]
        result = _blocked(import_node)
        assert result == "faiss"

    def test_blocked_function_identifies_sentence_transformers(self):
        import ast

        from ops_scripts.ci.check_llm_sdk_imports import _blocked

        source = "from sentence_transformers import SentenceTransformer\n"
        tree = ast.parse(source)
        import_node = tree.body[0]
        result = _blocked(import_node)
        assert result == "sentence_transformers"
