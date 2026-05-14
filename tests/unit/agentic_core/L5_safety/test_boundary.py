"""W4 boundary source scan tests for the L5 certification package.

Validates that the entire agentic_core/L5_safety/certification/ and
agentic_core/L5_safety/contracts/ subtree is free of:
  - App-specific literals (apps_rg, apps_lic, apps_research, apps_qna, resume, CV)
  - Provider SDK imports (openai, anthropic, boto3, httpx, requests)
  - Runtime disposition tokens (GateVerdict, CommitRequest, UWG, X3, etc.)
  - Network / filesystem write patterns (urllib.request.urlopen, socket, open())
  - Forbidden W5 scope tokens (no L5CertificationReady, no W5 interface stubs)

No production code is modified.  All tests are read-only source scans.
"""
from __future__ import annotations

import ast
import pathlib
import re

import pytest

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
_CERT_DIR = _REPO_ROOT / "agentic_core" / "L5_safety" / "certification"
_CONTRACT_DIR = _REPO_ROOT / "agentic_core" / "L5_safety" / "contracts"
_EXCEPTIONS_FILE = _REPO_ROOT / "agentic_core" / "L5_safety" / "exceptions.py"

_ALL_L5_SOURCES: list[pathlib.Path] = sorted(
    list(_CERT_DIR.glob("*.py")) + list(_CONTRACT_DIR.glob("*.py")) + [_EXCEPTIONS_FILE]
)

# W4 scope: only the files directly authored/modified in W1-W4 of this plan.
_W4_SCOPE_SOURCES: list[pathlib.Path] = [
    _CERT_DIR / "l5_packet_producer.py",
    _CERT_DIR / "egress_certifier.py",
    _CERT_DIR / "__init__.py",
    _CONTRACT_DIR / "l5_certification_contracts.py",
    _CONTRACT_DIR / "_base.py",
    _EXCEPTIONS_FILE,
]

# Vocabulary file intentionally DEFINES the tokens — exclude from token scan.
_VOCAB_FILE = _CONTRACT_DIR / "_vocab.py"


def _read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


def _rel(p: pathlib.Path) -> str:
    return str(p.relative_to(_REPO_ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scan_for_literal(sources: list[pathlib.Path], literal: str) -> list[str]:
    """Return relative paths of files that contain the literal string."""
    return [_rel(p) for p in sources if literal in _read(p)]


def _scan_for_import(sources: list[pathlib.Path], module_name: str) -> list[str]:
    """Return relative paths of files that import module_name at any import level."""
    hits: list[str] = []
    for p in sources:
        try:
            tree = ast.parse(_read(p))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == module_name or alias.name.startswith(module_name + "."):
                        hits.append(_rel(p))
                        break
            elif isinstance(node, ast.ImportFrom):
                if node.module and (
                    node.module == module_name
                    or node.module.startswith(module_name + ".")
                ):
                    hits.append(_rel(p))
                    break
    return hits


# ---------------------------------------------------------------------------
# App-specific literals must not appear in any L5 certification source
# ---------------------------------------------------------------------------


class TestNoAppLiterals:
    @pytest.mark.parametrize("literal", [
        "apps_rg",
        "apps_lic",
        "apps_research",
        "apps_qna",
        "apps_eval",
        "apps_rfp",
        "apps_underwriting",
    ])
    def test_no_app_literal_in_w4_scope_sources(self, literal: str):
        hits = _scan_for_literal(_W4_SCOPE_SOURCES, literal)
        assert not hits, (
            f"App-specific literal {literal!r} found in W4-scope sources: {hits}"
        )

    def test_no_resume_literal_in_certification_sources(self):
        cert_sources = [p for p in _W4_SCOPE_SOURCES if "certification" in str(p)]
        hits = [
            _rel(p) for p in cert_sources
            if "resume" in _read(p).lower()
        ]
        assert not hits, (
            f"Literal 'resume' found in certification sources (case-insensitive): {hits}"
        )

    def test_no_cv_standalone_literal_in_w4_scope_sources(self):
        hits = [
            _rel(p) for p in _W4_SCOPE_SOURCES
            if " CV " in _read(p)
        ]
        assert not hits, (
            f"Standalone ' CV ' literal found in W4-scope sources: {hits}"
        )


# ---------------------------------------------------------------------------
# Provider SDK must not be imported anywhere in L5 certification sources
# ---------------------------------------------------------------------------


class TestNoProviderSdkImports:
    @pytest.mark.parametrize("module_name", [
        "openai",
        "anthropic",
        "boto3",
        "httpx",
        "requests",
        "aiohttp",
        "urllib3",
    ])
    def test_no_sdk_import_in_l5_sources(self, module_name: str):
        hits = _scan_for_import(_ALL_L5_SOURCES, module_name)
        assert not hits, (
            f"Provider SDK import {module_name!r} found in L5 safety sources: {hits}"
        )

    def test_no_sdk_literal_in_contract_sources(self):
        contract_sources = list(_CONTRACT_DIR.glob("*.py"))
        for sdk in ("openai", "anthropic", "boto3", "httpx"):
            hits = _scan_for_literal(contract_sources, sdk)
            assert not hits, (
                f"Provider SDK literal {sdk!r} found in contract sources: {hits}"
            )


# ---------------------------------------------------------------------------
# Runtime disposition tokens must not appear in L5 certification sources
# ---------------------------------------------------------------------------


class TestNoRuntimeDispositionTokens:
    """Scan W4-scope certification and contract files (excluding _vocab.py which
    legitimately DEFINES these tokens as its controlled vocabulary)."""

    @pytest.mark.parametrize("token", [
        "GateVerdict",
        "CommitRequest",
        "X3",
        "allow_l2_execution",
        "allow_model_call",
        "allow_tool_call",
        "require_HITL",
        "downstream_disposition",
        "L5_CERTIFICATION_READY",
    ])
    def test_forbidden_token_not_in_w4_scope_sources(self, token: str):
        # Exclude _vocab.py — it legitimately defines the forbidden token list.
        sources = [p for p in _W4_SCOPE_SOURCES if p != _VOCAB_FILE]
        hits = _scan_for_literal(sources, token)
        assert not hits, (
            f"Forbidden runtime disposition token {token!r} found in W4-scope sources "
            f"(excluding _vocab.py): {hits}"
        )

    def test_packet_status_tokens_only_in_vocab_and_contracts(self):
        """Gap-status tokens are allowed in _vocab.py and l5_certification_contracts.py
        (as constants) but must NOT appear in the certification/ runtime code."""
        gap_tokens = [
            "L5_REQUIRES_RECLEARANCE",
            "L5_PARTIAL",
        ]
        cert_runtime = [
            p for p in _W4_SCOPE_SOURCES
            if "certification" in str(p) and p.name not in ("__init__.py",)
        ]
        for token in gap_tokens:
            hits = _scan_for_literal(cert_runtime, token)
            assert not hits, (
                f"Gap-status token {token!r} must not appear in certification runtime "
                f"sources: {hits}"
            )


# ---------------------------------------------------------------------------
# No network / filesystem write patterns in L5 certification sources
# ---------------------------------------------------------------------------


class TestNoNetworkFilesystemPatterns:
    @pytest.mark.parametrize("pattern", [
        "urllib.request.urlopen",
        "urlopen(",
        "socket.connect",
        "send(",
        "recv(",
        ".post(",
        "fetch(",
        "open(",
        "pathlib.Path(",
        "shutil",
        "subprocess",
        "tempfile",
        "os.remove",
        "os.unlink",
        "os.makedirs",
        "os.mkdir",
    ])
    def test_no_network_filesystem_pattern_in_certification_sources(self, pattern: str):
        cert_sources = [
            p for p in _W4_SCOPE_SOURCES
            if "certification" in str(p)
        ]
        hits = _scan_for_literal(cert_sources, pattern)
        assert not hits, (
            f"Network/filesystem pattern {pattern!r} found in certification sources: {hits}"
        )


# ---------------------------------------------------------------------------
# No W5 scope tokens — proof that W5 has NOT been accidentally introduced
# ---------------------------------------------------------------------------


class TestNoW5ScopeTokens:
    """Prove that W4 hardening did NOT introduce any W5 scope changes."""

    @pytest.mark.parametrize("token", [
        "W5",
        "phase_5",
        "w5_",
        "certify_child",
        "child_certifier_registry",
        "ChildCertifierRegistry",
        "certifier_dispatch",
    ])
    def test_no_w5_token_in_certification_sources(self, token: str):
        cert_sources = list(_CERT_DIR.glob("*.py"))
        hits = _scan_for_literal(cert_sources, token)
        assert not hits, (
            f"W5 scope token {token!r} found in certification sources: {hits}. "
            "W4 must not introduce W5 interface stubs."
        )


# ---------------------------------------------------------------------------
# Verify L5_safety package structure integrity (no unexpected modules)
# ---------------------------------------------------------------------------


class TestL5SafetyPackageStructure:
    def test_certification_package_exports_required_names(self):
        """The certification package must export the three W1-W3 public names."""
        import agentic_core.L5_safety.certification as cert_pkg

        required = {"EgressCertifier", "MetadataOnlyEgressCertifier", "L5PacketProducer"}
        actual_public = {n for n in dir(cert_pkg) if not n.startswith("_")}
        missing = required - actual_public
        assert not missing, (
            f"Required public names missing from certification package: {missing}."
        )

    def test_w4_scope_certification_files_exist(self):
        """All W4-scope certification files must be present on disk."""
        required_files = ["__init__.py", "l5_packet_producer.py", "egress_certifier.py"]
        for filename in required_files:
            path = _CERT_DIR / filename
            assert path.exists(), f"Expected certification file missing: {path}"

    def test_w4_scope_contract_files_exist(self):
        """All W4-scope contract files must be present on disk."""
        required_files = [
            "__init__.py", "_base.py", "_vocab.py", "l5_certification_contracts.py"
        ]
        for filename in required_files:
            path = _CONTRACT_DIR / filename
            assert path.exists(), f"Expected contract file missing: {path}"

    def test_exceptions_file_is_import_clean(self):
        source = _EXCEPTIONS_FILE.read_text(encoding="utf-8")
        for forbidden in ("import os", "import sys", "import re", "GateVerdict"):
            assert forbidden not in source, (
                f"exceptions.py contains unexpected import/token {forbidden!r}"
            )
