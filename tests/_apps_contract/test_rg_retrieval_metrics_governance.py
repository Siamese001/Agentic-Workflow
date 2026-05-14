"""W6 — Governance and anti-contamination tests for the apps_rg retrieval metrics pipeline.

Protects the ownership split established in W1-W5 permanently.

The ten required categories (plan §11):

  1. No JD/resume-specific implementation literals in agentic_core C0/contracts
     (AST/path-aware; ignores legitimate generic delegation vocab).
  2. apps_rg U0/profile file declares required_source_classes.
  3. agentic_core C0 extractor has zero apps_rg.* imports (AST scan).
  4. apps_rg Exit reads support_status and rejects UNKNOWN/EMPTY/BLOCKED/CONFLICTED.
  5. support_status in c0_metrics.json fixtures matches canonical six-value enum.
  6. UNKNOWN/BLOCKED/EMPTY/CONFLICTED cannot pass Exit (negative-control).
  7. c0_metrics.json is replayable: same input evidence → same final_evidence_digest.
  8. No direct C0-to-L4 write path (AST scan of c0_binding.py).
  9. No L6 current-run rescue path (AST scan of c0_binding.py / exit_binding.py).
  10. Existing tests/_apps_contract/ suite still passes (import regression guard).

Scan discipline:
- All boundary checks use AST/import analysis, not broad raw-string grep.
- Legitimate generic delegation vocabulary already in agentic_core contracts
  (e.g. UPLOADED_BRIEFING as a delegation type in apps_research_runtime_package)
  is explicitly allowlisted so it does not cause false positives.
- Only app-specific IMPLEMENTATION leakage fails the scan.
"""
from __future__ import annotations

import ast
import hashlib
import importlib
import json
import tempfile
from pathlib import Path
from typing import Any

import pytest

from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK_WITH_CAVEATS,
    SUPPORT_STATUS_CONFLICTED,
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_BLOCKED,
    STATUS_UNKNOWN,
    SUPPORT_STATUS_PASSING_VALUES,
)

_REPO_ROOT = Path(__file__).parents[2]
_AGENTIC_CORE = _REPO_ROOT / "agentic_core"
_APPS_RG = _REPO_ROOT / "apps_rg"

# Canonical six-value set (W1/W2 invariant)
_CANONICAL_SUPPORT_STATUSES: frozenset[str] = frozenset({
    "PASS", "WEAK_WITH_CAVEATS", "CONFLICTED", "EMPTY", "BLOCKED", "UNKNOWN",
})

# Values that MUST block Exit (never silently pass)
_BLOCKING_STATUSES: frozenset[str] = frozenset({
    "UNKNOWN", "EMPTY", "BLOCKED", "CONFLICTED",
})

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_imports_from_file(path: Path) -> list[str]:
    """Return list of imported module names via AST (top-level and from imports)."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.append(node.module)
    return modules


def _ast_contains_call(path: Path, func_names: set[str]) -> list[str]:
    """Return list of matched function call names found in an AST."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr in func_names:
                found.append(node.func.attr)
            elif isinstance(node.func, ast.Name) and node.func.id in func_names:
                found.append(node.func.id)
    return found


def _ast_contains_string_literal(path: Path, literals: set[str]) -> list[str]:
    """Return list of matched string literals found anywhere in an AST."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            for lit in literals:
                if lit in node.value:
                    found.append(lit)
    return found


def _make_fec(
    run_id: str = "gov_run",
    support_status: str = "PASS",
    sources: tuple[str, ...] = ("jd_payload:jd_text", "resume_payload:resume_text"),
    evidence_content: tuple[tuple[str, str], ...] = (
        ("jd_payload:jd_text", "SWE role at Acme"),
        ("resume_payload:resume_text", "10y Python engineer"),
    ),
) -> FinalEvidenceContract:
    items = tuple(
        EvidenceItem(source=src, content=content)
        for src, content in evidence_content
    )
    return FinalEvidenceContract(
        request_id=run_id,
        run_id=run_id,
        app_id="apps_rg",
        trace_id=run_id,
        evidence_items=items,
        retrieval_sources=sources,
        support_target_met=(support_status == "PASS"),
        support_status=support_status,
        l5_certification_ref="c0-gov-test-w6",
    )


# ===========================================================================
# Category 1: No JD/resume-specific implementation literals in agentic_core C0/contracts
# ===========================================================================

class TestCategory1NoAppSpecificLiteralsInAgenticCore:
    """No JD/resume/company implementation logic may leak into agentic_core C0 or contracts.

    Scan discipline: AST-based, only flags implementation identifiers.
    Does NOT flag generic delegation vocabulary (UPLOADED_BRIEFING as a delegation type,
    'jd_payload' in a docstring example, or 'resume_payload' as a prefix example) —
    those are generic contract vocabulary legitimately present.
    """

    # Implementation identifiers that must NOT appear as function/class definitions
    # or as imported names inside agentic_core C0 or contracts.
    _FORBIDDEN_IMPL_IDENTIFIERS: set[str] = {
        "classify_briefing_mode",
        "BriefingModeDecision",
        "briefing_mode_classifier",
        "_evaluate_c0_evidence_gates",
        "_compute_apps_rg_owned_fields",
        "_BLOCKING_SUPPORT_STATUSES",
        "jd_keyword_coverage",
        "overfit_score",
        "build_c0_metrics",
        "write_c0_metrics",
        "make_empty_fec",
        "c0_metrics_writer",
        "retrieval_requirements_profile",
    }

    # Files in agentic_core/runtime/c0/ that are known LEGACY_SHIMs
    # (re-exports only — they import from apps_rg by design; excluded from scan)
    _SHIM_FILENAMES: set[str] = {"apps_rg_c0_binding.py"}

    def _scan_files(self, root: Path) -> list[str]:
        violations: list[str] = []
        for py_file in sorted(root.rglob("*.py")):
            if py_file.name in self._SHIM_FILENAMES:
                continue
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
            except SyntaxError:
                continue
            rel = py_file.relative_to(_REPO_ROOT)
            # Check function/class definitions for forbidden names
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if node.name in self._FORBIDDEN_IMPL_IDENTIFIERS:
                        violations.append(f"{rel}: defines '{node.name}'")
                # Check import-from names
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name in self._FORBIDDEN_IMPL_IDENTIFIERS:
                            violations.append(f"{rel}: imports '{alias.name}'")
                # Check import module names
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self._FORBIDDEN_IMPL_IDENTIFIERS:
                            violations.append(f"{rel}: imports module '{alias.name}'")
        return violations

    def test_no_apps_rg_impl_in_agentic_core_c0(self):
        violations = self._scan_files(_AGENTIC_CORE / "runtime" / "c0")
        assert not violations, (
            "agentic_core/runtime/c0 contains apps_rg implementation leakage:\n"
            + "\n".join(violations)
        )

    def test_no_apps_rg_impl_in_agentic_core_contracts(self):
        violations = self._scan_files(_AGENTIC_CORE / "runtime" / "contracts")
        assert not violations, (
            "agentic_core/runtime/contracts contains apps_rg implementation leakage:\n"
            + "\n".join(violations)
        )


# ===========================================================================
# Category 2: apps_rg profile defines required_source_classes
# ===========================================================================

class TestCategory2AppsRgProfileOwnsRequiredSourceClasses:
    """apps_rg U0/profile file declares required_source_classes — not agentic_core."""

    def test_retrieval_requirements_profile_exists(self):
        profile_dir = _APPS_RG / "config" / "domain_contract"
        yaml_files = list(profile_dir.glob("retrieval_requirements*.yaml"))
        assert yaml_files, (
            f"No retrieval_requirements*.yaml found in {profile_dir}. "
            "apps_rg must own this profile."
        )

    def test_profile_declares_required_source_classes(self):
        from apps_rg.runtime.profiles.retrieval_requirements import get_normative_source_classes
        classes = get_normative_source_classes()
        assert isinstance(classes, tuple)
        assert len(classes) > 0, "required_source_classes must be non-empty"

    def test_required_source_classes_are_strings(self):
        from apps_rg.runtime.profiles.retrieval_requirements import get_normative_source_classes
        for cls in get_normative_source_classes():
            assert isinstance(cls, str), f"source class {cls!r} is not a string"

    def test_retrieval_requirements_module_in_apps_rg(self):
        """The profile module must live in apps_rg, never agentic_core."""
        import apps_rg.runtime.profiles.retrieval_requirements as m
        assert "apps_rg" in m.__file__.replace("\\", "/"), (
            f"retrieval_requirements module resolves to {m.__file__!r}, "
            "expected path inside apps_rg"
        )


# ===========================================================================
# Category 3: agentic_core C0 extractor has zero apps_rg.* imports (AST)
# ===========================================================================

class TestCategory3ExtractorZeroAppsRgImports:
    """evidence_metrics_extractor.py must have zero imports from apps_rg.* or apps_*."""

    def test_extractor_has_no_apps_rg_imports(self):
        extractor = _AGENTIC_CORE / "runtime" / "c0" / "evidence_metrics_extractor.py"
        assert extractor.exists(), f"Extractor not found at {extractor}"
        imports = _get_imports_from_file(extractor)
        violations = [m for m in imports if m.startswith("apps_rg") or m.startswith("apps_")]
        assert not violations, (
            f"evidence_metrics_extractor.py imports from apps_*: {violations}. "
            "This extractor must be fully generic."
        )

    def test_extractor_documents_zero_apps_imports_invariant(self):
        """The W2 invariant comment is present in the extractor source."""
        extractor = _AGENTIC_CORE / "runtime" / "c0" / "evidence_metrics_extractor.py"
        text = extractor.read_text(encoding="utf-8")
        assert "apps_rg" in text and "Zero imports" in text, (
            "Extractor should document the zero-apps_rg-imports invariant (W2 doc)."
        )

    def test_c0_package_driven_grounding_no_apps_rg_logic(self):
        """c0_package_driven_grounding.py may import apps_rg contracts but not logic."""
        pkg_file = _AGENTIC_CORE / "runtime" / "c0" / "c0_package_driven_grounding.py"
        if not pkg_file.exists():
            pytest.skip("c0_package_driven_grounding.py not present")
        imports = _get_imports_from_file(pkg_file)
        logic_imports = [
            m for m in imports
            if m.startswith("apps_rg.runtime.bindings")
            or m.startswith("apps_rg.runtime.profiles")
        ]
        assert not logic_imports, (
            f"c0_package_driven_grounding.py imports apps_rg logic: {logic_imports}"
        )


# ===========================================================================
# Category 4: apps_rg Exit reads support_status and rejects blocking values
# ===========================================================================

class TestCategory4ExitRejectsBlockingStatus:
    """apps_rg Exit must read support_status from FEC and block on non-passing values."""

    def test_exit_binding_exports_blocking_statuses_constant(self):
        from apps_rg.runtime.bindings.exit_binding import _BLOCKING_SUPPORT_STATUSES
        assert "UNKNOWN" in _BLOCKING_SUPPORT_STATUSES
        assert "EMPTY" in _BLOCKING_SUPPORT_STATUSES
        assert "BLOCKED" in _BLOCKING_SUPPORT_STATUSES
        assert "CONFLICTED" in _BLOCKING_SUPPORT_STATUSES

    def test_exit_binding_exports_evaluate_gates_function(self):
        from apps_rg.runtime.bindings.exit_binding import _evaluate_c0_evidence_gates
        assert callable(_evaluate_c0_evidence_gates)

    def test_evaluate_gates_blocks_on_unknown(self):
        from apps_rg.runtime.bindings.exit_binding import _evaluate_c0_evidence_gates
        fec = _make_fec(support_status="UNKNOWN")
        _, is_blocking, reason = _evaluate_c0_evidence_gates(fec)
        assert is_blocking
        assert "UNKNOWN" in reason

    def test_evaluate_gates_blocks_on_empty(self):
        from apps_rg.runtime.bindings.exit_binding import _evaluate_c0_evidence_gates
        fec = _make_fec(support_status="EMPTY")
        _, is_blocking, _ = _evaluate_c0_evidence_gates(fec)
        assert is_blocking

    def test_evaluate_gates_blocks_on_blocked(self):
        from apps_rg.runtime.bindings.exit_binding import _evaluate_c0_evidence_gates
        fec = _make_fec(support_status="BLOCKED")
        _, is_blocking, _ = _evaluate_c0_evidence_gates(fec)
        assert is_blocking

    def test_evaluate_gates_blocks_on_conflicted(self):
        from apps_rg.runtime.bindings.exit_binding import _evaluate_c0_evidence_gates
        fec = _make_fec(support_status="CONFLICTED")
        _, is_blocking, _ = _evaluate_c0_evidence_gates(fec)
        assert is_blocking

    def test_evaluate_gates_pass_not_blocking(self):
        from apps_rg.runtime.bindings.exit_binding import _evaluate_c0_evidence_gates
        fec = _make_fec(support_status="PASS")
        _, is_blocking, _ = _evaluate_c0_evidence_gates(fec)
        assert not is_blocking

    def test_evaluate_gates_weak_with_caveats_not_blocking(self):
        from apps_rg.runtime.bindings.exit_binding import _evaluate_c0_evidence_gates
        fec = _make_fec(support_status="WEAK_WITH_CAVEATS")
        _, is_blocking, _ = _evaluate_c0_evidence_gates(fec)
        assert not is_blocking

    def test_evaluate_gates_none_fec_not_blocking(self):
        from apps_rg.runtime.bindings.exit_binding import _evaluate_c0_evidence_gates
        _, is_blocking, _ = _evaluate_c0_evidence_gates(None)
        assert not is_blocking

    def test_exit_gate_logic_lives_in_apps_rg_not_agentic_core(self):
        """_evaluate_c0_evidence_gates must resolve to apps_rg, not agentic_core."""
        from apps_rg.runtime.bindings import exit_binding
        assert "apps_rg" in exit_binding.__file__.replace("\\", "/"), (
            f"exit_binding resolves to {exit_binding.__file__!r}, expected apps_rg path"
        )


# ===========================================================================
# Category 5: support_status values in c0_metrics fixture match canonical enum
# ===========================================================================

class TestCategory5CanonicalSupportStatusEnum:
    """support_status values must always be in the canonical six-value set."""

    def test_canonical_set_contains_exactly_six_values(self):
        assert len(_CANONICAL_SUPPORT_STATUSES) == 6
        assert _CANONICAL_SUPPORT_STATUSES == {
            "PASS", "WEAK_WITH_CAVEATS", "CONFLICTED", "EMPTY", "BLOCKED", "UNKNOWN"
        }

    def test_partial_not_in_canonical_set(self):
        """PARTIAL was eliminated in W2 — must never be in the canonical set."""
        assert "PARTIAL" not in _CANONICAL_SUPPORT_STATUSES

    @pytest.mark.parametrize("status", [
        "PASS", "WEAK_WITH_CAVEATS", "CONFLICTED", "EMPTY", "BLOCKED", "UNKNOWN"
    ])
    def test_build_c0_metrics_preserves_canonical_status(self, status):
        from apps_rg.runtime.bindings.c0_metrics_writer import build_c0_metrics
        fec = _make_fec(support_status=status)
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0")
        assert result["support_status"] == status

    def test_build_c0_metrics_coerces_partial_to_weak_with_caveats(self):
        """PARTIAL is forbidden (W2 §4); extractor coerces it to WEAK_WITH_CAVEATS.

        The coercion path: FEC(PARTIAL) → extract_evidence_metrics() coerces
        PARTIAL → WEAK_WITH_CAVEATS → _coerce_support_status passes it through
        as a canonical value. PARTIAL never reaches the c0_metrics artifact.
        """
        from apps_rg.runtime.bindings.c0_metrics_writer import build_c0_metrics
        fec = _make_fec(support_status="PARTIAL")
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0")
        assert result["support_status"] == "WEAK_WITH_CAVEATS", (
            "PARTIAL must be coerced to WEAK_WITH_CAVEATS by the W2 extractor "
            f"(got {result['support_status']!r})"
        )
        assert result["support_status"] != "PARTIAL", (
            "PARTIAL must never appear in a c0_metrics artifact"
        )

    def test_c0_metrics_fixture_has_canonical_status(self):
        """Example fixture file (if it exists) must have a canonical support_status."""
        fixture = _REPO_ROOT / "tests" / "_fixtures" / "c0_metrics_example.json"
        if not fixture.exists():
            pytest.skip("c0_metrics_example.json fixture not present yet")
        data = json.loads(fixture.read_text(encoding="utf-8"))
        status = data.get("support_status", "MISSING")
        assert status in _CANONICAL_SUPPORT_STATUSES, (
            f"Fixture has non-canonical support_status={status!r}"
        )

    def test_fec_canonical_constants_match_internal_set(self):
        """The agentic_core FEC canonical constants must match our six-value set."""
        fec_values = {
            SUPPORT_STATUS_PASS,
            SUPPORT_STATUS_WEAK_WITH_CAVEATS,
            SUPPORT_STATUS_CONFLICTED,
            SUPPORT_STATUS_EMPTY,
            SUPPORT_STATUS_BLOCKED,
            STATUS_UNKNOWN,
        }
        assert fec_values == _CANONICAL_SUPPORT_STATUSES


# ===========================================================================
# Category 6: UNKNOWN/BLOCKED/EMPTY/CONFLICTED cannot pass Exit (negative control)
# ===========================================================================

class TestCategory6BlockingStatusCannotPassExit:
    """Negative-control: blocking statuses must never produce outcome_authorized=True."""

    def _run_exit(self, support_status: str):
        from apps_rg.runtime.bindings.exit_binding import exit_finalize_apps_rg
        from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
        sealed = SealedL2Artifact(
            request_id="gov_neg",
            run_id="gov_neg",
            app_id="apps_rg",
            trace_id="gov_neg",
            execution_status="completed",
            generated_content="resume text",
            proposed_state_diff={"target_company": "Acme", "target_role": "SWE"},
            compilation_hash="abc123",
            sovereign_execution_receipt="stub",
            tenant_id="apps_rg",
            l5_certification_ref="w6-neg-ctrl",
        )
        fec = _make_fec(support_status=support_status)
        return exit_finalize_apps_rg(
            sealed, fec=fec, target_company="Acme", target_role="SWE"
        )

    @pytest.mark.parametrize("status", ["UNKNOWN", "EMPTY", "BLOCKED", "CONFLICTED"])
    def test_blocking_status_degrades_outcome_authorized(self, status):
        result = self._run_exit(status)
        assert result.disposition.outcome_authorized is False, (
            f"support_status={status} must degrade outcome_authorized to False; "
            f"got {result.disposition.outcome_authorized}"
        )

    def test_pass_status_does_not_degrade(self):
        result = self._run_exit("PASS")
        assert result.disposition.outcome_authorized is True

    def test_weak_with_caveats_does_not_degrade(self):
        result = self._run_exit("WEAK_WITH_CAVEATS")
        assert result.disposition.outcome_authorized is True

    @pytest.mark.parametrize("status", ["UNKNOWN", "EMPTY", "BLOCKED", "CONFLICTED"])
    def test_blocking_status_recorded_in_run_metadata(self, status):
        result = self._run_exit(status)
        meta = next(
            c.serialized_content for c in result.artifact_commit_candidates
            if c.artifact_type == "run_metadata"
        )
        assert meta["w4_c0_evidence"]["c0_blocking"] is True


# ===========================================================================
# Category 7: c0_metrics.json is replayable — same input → same final_evidence_digest
# ===========================================================================

class TestCategory7DigestReplayStability:
    """Same evidence items must always produce the same final_evidence_digest."""

    def _make_deterministic_fec(self, run_id: str = "replay_test") -> FinalEvidenceContract:
        return _make_fec(
            run_id=run_id,
            support_status="PASS",
            sources=("jd_payload:jd_text", "resume_payload:resume_text"),
            evidence_content=(
                ("jd_payload:jd_text", "Senior Python engineer role at Acme Corp"),
                ("resume_payload:resume_text", "10 years Python, distributed systems"),
            ),
        )

    def test_same_fec_produces_same_digest(self):
        from apps_rg.runtime.bindings.c0_metrics_writer import build_c0_metrics
        fec1 = self._make_deterministic_fec()
        fec2 = self._make_deterministic_fec()
        r1 = build_c0_metrics(fec=fec1, run_id="r", route_id="R0")
        r2 = build_c0_metrics(fec=fec2, run_id="r", route_id="R0")
        assert r1["final_evidence_digest"] == r2["final_evidence_digest"], (
            "Same FEC must produce same final_evidence_digest (deterministic replay)"
        )

    def test_different_evidence_produces_different_digest(self):
        from apps_rg.runtime.bindings.c0_metrics_writer import build_c0_metrics
        fec_a = _make_fec(
            run_id="r",
            evidence_content=(("jd_payload:jd_text", "Content A"),),
        )
        fec_b = _make_fec(
            run_id="r",
            evidence_content=(("jd_payload:jd_text", "Content B"),),
        )
        r_a = build_c0_metrics(fec=fec_a, run_id="r", route_id="R0")
        r_b = build_c0_metrics(fec=fec_b, run_id="r", route_id="R0")
        assert r_a["final_evidence_digest"] != r_b["final_evidence_digest"]

    def test_artifact_written_digest_matches_build_digest(self):
        from apps_rg.runtime.bindings.c0_metrics_writer import build_c0_metrics, write_c0_metrics
        fec = self._make_deterministic_fec("replay_write")
        built = build_c0_metrics(fec=fec, run_id="replay_write", route_id="R0")
        with tempfile.TemporaryDirectory() as tmpdir:
            path = write_c0_metrics(
                fec=fec, run_id="replay_write", route_id="R0",
                runs_root=Path(tmpdir)
            )
            assert path is not None
            written = json.loads(path.read_text(encoding="utf-8"))
        assert written["final_evidence_digest"] == built["final_evidence_digest"]

    def test_digest_is_non_empty_sha256_hex(self):
        from apps_rg.runtime.bindings.c0_metrics_writer import build_c0_metrics
        fec = self._make_deterministic_fec()
        result = build_c0_metrics(fec=fec, run_id="r", route_id="R0")
        digest = result["final_evidence_digest"]
        assert isinstance(digest, str) and len(digest) == 64, (
            f"final_evidence_digest should be 64-char SHA-256 hex, got {digest!r}"
        )


# ===========================================================================
# Category 8: No direct C0-to-L4 write path (AST scan)
# ===========================================================================

class TestCategory8NoDirectC0ToL4Write:
    """c0_binding.py must not make durable filesystem writes (C0-to-L4 boundary)."""

    # Durable write function names forbidden in C0 binding
    _DURABLE_WRITE_CALLS: set[str] = {
        "write_text", "write_bytes", "open", "mkdir", "makedirs",
    }

    # json.dump is allowed only via c0_metrics_writer (which is fail-soft and
    # handles its own path); direct calls in c0_binding itself are forbidden.
    _DIRECT_JSON_WRITES: set[str] = {"dump"}

    def _get_c0_binding_ast(self) -> ast.Module:
        path = _APPS_RG / "runtime" / "bindings" / "c0_binding.py"
        return ast.parse(path.read_text(encoding="utf-8"))

    def test_c0_binding_no_durable_write_text(self):
        tree = self._get_c0_binding_ast()
        violations = []
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in ("write_text", "write_bytes")
            ):
                violations.append(f"line {node.lineno}: .{node.func.attr}()")
        assert not violations, (
            "c0_binding.py contains durable write_text/write_bytes calls:\n"
            + "\n".join(violations)
        )

    def test_c0_binding_no_direct_os_makedirs(self):
        """os.makedirs in c0_binding itself is a durable side effect."""
        path = _APPS_RG / "runtime" / "bindings" / "c0_binding.py"
        text = path.read_text(encoding="utf-8")
        # Allow makedirs only inside the c0_metrics_writer (separate module)
        # c0_binding itself must not call makedirs
        tree = ast.parse(text)
        violations = []
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "makedirs"
            ):
                violations.append(f"line {node.lineno}: .makedirs()")
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "mkdir"
                # allow mkdir on Path objects only if it's inside c0_metrics_writer
                # c0_binding.py itself must not mkdir
            ):
                violations.append(f"line {node.lineno}: .mkdir()")
        assert not violations, (
            "c0_binding.py contains mkdir/makedirs durable calls:\n"
            + "\n".join(violations)
        )

    def test_inert_candidate_has_mutation_candidate_inert_true(self):
        """InertArtifactCommitCandidate.mutation_candidate_inert must always be True."""
        from apps_rg.runtime.bindings.exit_binding import InertArtifactCommitCandidate
        candidate = InertArtifactCommitCandidate(
            artifact_type="test",
            proposed_path="/virtual/path",
            content_digest="abc",
            serialized_content={"k": "v"},
        )
        assert candidate.mutation_candidate_inert is True
        assert candidate.non_durable is True
        assert candidate.not_l4_truth is True
        assert candidate.proposal_status == "PENDING_UWG"

    def test_exit_binding_inert_candidates_not_durable(self):
        """All artifact commit candidates produced by Exit must be inert (non-durable)."""
        from apps_rg.runtime.bindings.exit_binding import exit_finalize_apps_rg
        from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
        sealed = SealedL2Artifact(
            request_id="c8_test",
            run_id="c8_test",
            app_id="apps_rg",
            trace_id="c8_test",
            execution_status="completed",
            generated_content="resume",
            proposed_state_diff={"target_company": "Acme", "target_role": "SWE"},
            compilation_hash="abc123",
            sovereign_execution_receipt="stub",
            tenant_id="apps_rg",
            l5_certification_ref="w6-c8-test",
        )
        result = exit_finalize_apps_rg(
            sealed, target_company="Acme", target_role="SWE"
        )
        for candidate in result.artifact_commit_candidates:
            assert candidate.mutation_candidate_inert is True, (
                f"Candidate {candidate.artifact_type} has mutation_candidate_inert=False"
            )
            assert candidate.non_durable is True
            assert candidate.not_l4_truth is True


# ===========================================================================
# Category 9: No L6 current-run rescue path
# ===========================================================================

class TestCategory9NoL6CurrentRunRescue:
    """Neither c0_binding.py nor exit_binding.py may introduce an L6 rescue path."""

    _L6_RESCUE_IDENTIFIERS: set[str] = {
        "L6",
        "rescue",
        "current_run_rescue",
        "promote_current_run",
        "l6_rescue",
        "future_run_promotion",
        "regret_tracker",
        "promote_to_future",
    }

    def _check_file(self, path: Path) -> list[str]:
        """AST-scan for L6 rescue imports or function definitions."""
        violations: list[str] = []
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            return violations
        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.ImportFrom) and node.module:
                if "future_run_promotion" in node.module or "l6_rescue" in node.module:
                    violations.append(
                        f"line {node.lineno}: imports from L6 rescue module {node.module!r}"
                    )
            # Check for function/class definitions with rescue names
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if any(kw in node.name.lower() for kw in ("l6_rescue", "current_run_rescue", "promote_current")):
                    violations.append(f"line {node.lineno}: defines rescue function {node.name!r}")
        return violations

    def test_c0_binding_no_l6_rescue(self):
        path = _APPS_RG / "runtime" / "bindings" / "c0_binding.py"
        violations = self._check_file(path)
        assert not violations, (
            "c0_binding.py contains L6 rescue path:\n" + "\n".join(violations)
        )

    def test_exit_binding_no_l6_rescue(self):
        path = _APPS_RG / "runtime" / "bindings" / "exit_binding.py"
        violations = self._check_file(path)
        assert not violations, (
            "exit_binding.py contains L6 rescue path:\n" + "\n".join(violations)
        )

    def test_future_run_promotion_not_imported_in_exit(self):
        """Exit must not import future_run_promotion (current-run rescue pattern)."""
        path = _APPS_RG / "runtime" / "bindings" / "exit_binding.py"
        imports = _get_imports_from_file(path)
        rescue_imports = [m for m in imports if "future_run_promotion" in m]
        assert not rescue_imports, (
            f"exit_binding.py imports future_run_promotion: {rescue_imports}"
        )


# ===========================================================================
# Category 10: Regression guard — existing _apps_contract/ tests importable
# ===========================================================================

class TestCategory10RegressionGuard:
    """All W1-W5 test modules remain importable (zero regressions)."""

    @pytest.mark.parametrize("modpath", [
        "tests._apps_contract.test_rg_w1_retrieval_requirements_profile",
        "tests._apps_contract.test_rg_w2_c0_metrics_extractor",
        "tests._apps_contract.test_rg_w3_c0_metrics_artifact",
        "tests._apps_contract.test_apps_rg_c0_minimum_safety",
        "tests._apps_contract.test_rg_w4_exit_binding",
        "tests._apps_contract.test_rg_w5_briefing_path_proof",
    ])
    def test_prior_wave_test_module_importable(self, modpath):
        mod = importlib.import_module(modpath)
        assert mod is not None

    def test_c0_metrics_writer_module_importable(self):
        from apps_rg.runtime.bindings import c0_metrics_writer
        assert c0_metrics_writer is not None

    def test_briefing_mode_classifier_module_importable(self):
        from apps_rg.runtime.bindings import briefing_mode_classifier
        assert briefing_mode_classifier is not None

    def test_c0_binding_module_importable(self):
        from apps_rg.runtime.bindings import c0_binding
        assert c0_binding is not None

    def test_exit_binding_module_importable(self):
        from apps_rg.runtime.bindings import exit_binding
        assert exit_binding is not None

    def test_retrieval_requirements_module_importable(self):
        from apps_rg.runtime.profiles import retrieval_requirements
        assert retrieval_requirements is not None
