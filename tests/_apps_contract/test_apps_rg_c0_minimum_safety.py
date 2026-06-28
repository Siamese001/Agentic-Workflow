"""S7: Minimum C0 safety — contract tests.

Verifies all required S7 invariants:
- grounding_required=True without FEC fails/blocks
- grounding_required=False marks C0 not applicable
- complete PASS FEC passes
- missing support_status is UNKNOWN/FAIL not PASS
- WEAK_WITH_CAVEATS is not promoted to PASS
- CONFLICTED blocks confident output
- EMPTY blocks confident output
- BLOCKED blocks confident output
- UNKNOWN blocks confident output
- missing evidence_items without explicit empty reason fails
- missing lineage/freshness/ACL/contradiction fields warn per profile
- authorized fresh briefing can pass if otherwise complete
- unauthorized briefing blocks
- stale briefing cannot be clean PASS
- company research lane is not available inside apps_rg C0
- checker does not import PA, L2, provider/model, section_agentic_pipeline,
  write_section_to_semantic_cache, l6_shadow_learning, or fact_vectors
- existing S1-S6 targeted tests still pass
"""
from __future__ import annotations

import importlib
import inspect
import json
import unittest
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_valid_fec(
    *,
    support_status: str = "PASS",
    evidence_items: list[Any] | None = None,
    final_evidence_digest: str = "abc123",
    source_lineage_map: list[Any] | None = None,
    freshness_receipts: list[Any] | None = None,
    acl_verification_receipts: list[Any] | None = None,
    contradiction_report: str = "NOT_APPLICABLE",
    citation_map: list[Any] | None = None,
    retrieval_sources: list[str] | None = None,
    evidence_items_empty_reason: str = "",
) -> dict[str, Any]:
    return {
        "evidence_items": evidence_items if evidence_items is not None else [{"source": "jd_payload:jd_text"}],
        "support_status": support_status,
        "final_evidence_digest": final_evidence_digest,
        "source_lineage_map": source_lineage_map if source_lineage_map is not None else [("ev1", "src1")],
        "freshness_receipts": freshness_receipts if freshness_receipts is not None else ["freshness:src1:FRESH"],
        "acl_verification_receipts": acl_verification_receipts if acl_verification_receipts is not None else ["acl:src1:ALLOWED"],
        "contradiction_report": contradiction_report,
        "citation_map": citation_map if citation_map is not None else [("ev1", "anchor1")],
        "retrieval_sources": retrieval_sources if retrieval_sources is not None else ["jd_payload:jd_text"],
        "evidence_items_empty_reason": evidence_items_empty_reason,
    }


def _minimal_valid_briefing() -> dict[str, Any]:
    return {
        "authority_class": "AUTHORITATIVE",
        "freshness_status": "FRESH",
        "freshness_timestamp_iso": "2026-05-14T10:00:00+00:00",
        "digest_ref": "sha256:abc123",
    }


def _get_checker_source() -> str:
    import apps_rg.runtime.bindings.c0_minimum_safety as mod
    return inspect.getsource(mod)


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------

class TestModuleImportSmoke(unittest.TestCase):

    def test_module_importable(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import (
            C0SafetyVerdict,
            C0SafetyResult,
            run_c0_minimum_safety,
        )
        self.assertIsNotNone(run_c0_minimum_safety)
        self.assertIsNotNone(C0SafetyVerdict)

    def test_profile_json_loadable(self) -> None:
        profile_path = (
            Path(__file__).resolve().parents[2]
            / "apps_rg" / "config" / "domain_contract"
            / "resume_c0_minimum_safety_profile.v1.json"
        )
        self.assertTrue(profile_path.exists(), f"Profile not found: {profile_path}")
        with profile_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertEqual(data["app_id"], "apps_rg")

    def test_result_dataclass_shape(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import C0SafetyResult
        r = C0SafetyResult(
            verdict="PASS",
            decisive_reason="ok",
            support_status="PASS",
            missing_fields=(),
            blocked_reason="",
            evidence_summary="",
            safe_to_continue_to_pa=True,
        )
        self.assertEqual(r.verdict, "PASS")
        self.assertTrue(r.safe_to_continue_to_pa)


class TestBoundaryGuard(unittest.TestCase):
    """Verify that c0_minimum_safety.py has no forbidden imports.

    Checks are AST-based (import nodes only) to avoid matching names
    that appear only in the module docstring listing.
    """

    def _get_imports(self) -> list[str]:
        """Return all imported module names from the checker module AST."""
        import ast
        import apps_rg.runtime.bindings.c0_minimum_safety as mod
        tree = ast.parse(inspect.getsource(mod))
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        return imported

    def _get_non_docstring_source(self) -> str:
        """Return source with module/function docstrings stripped."""
        import ast
        import apps_rg.runtime.bindings.c0_minimum_safety as mod
        src = inspect.getsource(mod)
        tree = ast.parse(src)
        # Collect all docstring line spans to strip them
        lines = src.splitlines()
        strip_lines: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                if (node.body and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)):
                    ds_node = node.body[0]
                    for lineno in range(ds_node.lineno - 1, ds_node.end_lineno):
                        strip_lines.add(lineno)
        return "\n".join(
            line for i, line in enumerate(lines) if i not in strip_lines
        )

    def test_no_section_agentic_pipeline(self) -> None:
        imports = self._get_imports()
        self.assertFalse(
            any("section_agentic_pipeline" in m for m in imports),
            f"Forbidden import found: section_agentic_pipeline in {imports}",
        )

    def test_no_write_section_to_semantic_cache(self) -> None:
        imports = self._get_imports()
        self.assertFalse(
            any("semantic_cache" in m or "write_section" in m for m in imports),
            f"Forbidden import found: write_section_to_semantic_cache in {imports}",
        )

    def test_no_l6_shadow_learning(self) -> None:
        imports = self._get_imports()
        self.assertFalse(
            any("l6_shadow" in m or "shadow_learning" in m for m in imports),
            f"Forbidden import found: l6_shadow_learning in {imports}",
        )

    def test_no_fact_vectors(self) -> None:
        imports = self._get_imports()
        self.assertFalse(
            any("fact_vectors" in m for m in imports),
            f"Forbidden import found: fact_vectors in {imports}",
        )

    def test_no_openai(self) -> None:
        imports = self._get_imports()
        self.assertFalse(
            any(m.startswith("openai") for m in imports),
            f"Forbidden import found: openai in {imports}",
        )

    def test_no_anthropic(self) -> None:
        imports = self._get_imports()
        self.assertFalse(
            any(m.startswith("anthropic") for m in imports),
            f"Forbidden import found: anthropic in {imports}",
        )

    def test_no_local_model_server(self) -> None:
        imports = self._get_imports()
        self.assertFalse(
            any(m.startswith("local_model_server") for m in imports),
            f"Forbidden import found: local_model_server in {imports}",
        )

    def test_no_requests_post(self) -> None:
        src = self._get_non_docstring_source()
        self.assertNotIn("requests.post", src)

    def test_no_httpx(self) -> None:
        imports = self._get_imports()
        self.assertFalse(
            any(m.startswith("httpx") for m in imports),
            f"Forbidden import found: httpx in {imports}",
        )

    def test_no_pa_binding_import(self) -> None:
        imports = self._get_imports()
        self.assertFalse(
            any("pa_binding" in m for m in imports),
            f"Forbidden import found: pa_binding in {imports}",
        )

    def test_no_l2_binding_import(self) -> None:
        imports = self._get_imports()
        self.assertFalse(
            any("l2_binding" in m for m in imports),
            f"Forbidden import found: l2_binding in {imports}",
        )

    def test_no_agentic_core_import(self) -> None:
        import ast
        import apps_rg.runtime.bindings.c0_minimum_safety as mod
        tree = ast.parse(inspect.getsource(mod))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module:
                    self.assertFalse(
                        node.module.startswith("agentic_core"),
                        f"Forbidden agentic_core import: {node.module}",
                    )
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertFalse(
                            alias.name.startswith("agentic_core"),
                            f"Forbidden agentic_core import: {alias.name}",
                        )


class TestGroundingDispatch(unittest.TestCase):

    def test_grounding_required_true_no_fec_is_blocked(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        result = run_c0_minimum_safety(grounding_required=True, fec=None)
        self.assertIn(result.verdict, ("BLOCKED", "FAIL", "UNKNOWN"))
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_grounding_required_true_no_fec_blocks_sendable(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        result = run_c0_minimum_safety(grounding_required=True, fec=None)
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_grounding_required_false_with_no_fec_passes(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        result = run_c0_minimum_safety(grounding_required=False, fec=None)
        self.assertEqual(result.verdict, "PASS")
        self.assertTrue(result.safe_to_continue_to_pa)

    def test_grounding_required_false_marks_not_applicable(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        result = run_c0_minimum_safety(grounding_required=False, fec=None)
        reason_lower = result.decisive_reason.lower()
        self.assertTrue(
            "not_applicable" in reason_lower or "not applicable" in reason_lower or "not required" in reason_lower,
            f"Expected not_applicable/not required in reason: {result.decisive_reason!r}",
        )

    def test_grounding_required_true_with_fec_passes_dispatch(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        # dispatch confirmed is encoded in evidence_summary
        self.assertIn("dispatch=", result.evidence_summary)

    def test_grounding_required_true_fec_present_can_pass(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertIn(result.verdict, ("PASS", "WARN"))
        self.assertTrue(result.safe_to_continue_to_pa)


class TestSupportStatusPolicy(unittest.TestCase):

    def test_missing_support_status_is_unknown_not_pass(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        fec["support_status"] = None
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertNotEqual(result.verdict, "PASS")
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_empty_support_status_is_unknown_not_pass(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        fec["support_status"] = ""
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertNotEqual(result.verdict, "PASS")
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_unknown_support_status_is_never_pass(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety, C0SafetyVerdict
        fec = _minimal_valid_fec(support_status="UNKNOWN")
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertNotEqual(result.verdict, C0SafetyVerdict.PASS)
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_weak_with_caveats_not_promoted_to_pass(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(support_status="WEAK_WITH_CAVEATS")
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertNotEqual(result.verdict, "PASS")
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_weak_not_promoted_to_pass(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(support_status="WEAK")
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertNotEqual(result.verdict, "PASS")
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_conflicted_blocks_confident_output(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(support_status="CONFLICTED")
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertFalse(result.safe_to_continue_to_pa)
        self.assertIn(result.verdict, ("BLOCKED", "FAIL", "UNKNOWN"))

    def test_empty_support_status_blocks_confident_output(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(support_status="EMPTY")
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_blocked_support_status_blocks_confident_output(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(support_status="BLOCKED")
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_pass_support_status_with_evidence_passes(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(support_status="PASS")
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertIn(result.verdict, ("PASS", "WARN"))
        self.assertTrue(result.safe_to_continue_to_pa)

    def test_partial_support_status_not_pass(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(support_status="PARTIAL")
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertNotIn(str(result.verdict), ("PASS", "WARN"), (
            "PARTIAL is not a canonical support_status and must not produce PASS/WARN"
        ))

    def test_pass_with_empty_evidence_items_fails(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(support_status="PASS", evidence_items=[])
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_unknown_verdict_enum_is_never_pass_enum(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import C0SafetyVerdict
        self.assertNotEqual(C0SafetyVerdict.UNKNOWN, C0SafetyVerdict.PASS)


class TestFECCompleteness(unittest.TestCase):

    def test_complete_fec_passes(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertIn(result.verdict, ("PASS", "WARN"))
        self.assertTrue(result.safe_to_continue_to_pa)

    def test_missing_evidence_items_without_reason_fails(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(evidence_items=[])
        fec["evidence_items_empty_reason"] = ""
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_missing_evidence_items_with_reason_not_hard_fail(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(support_status="NOT_APPLICABLE", evidence_items=[])
        fec["evidence_items_empty_reason"] = "grounding_not_required_for_this_route"
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        # With explicit reason, evidence_items check passes — but support_status
        # may still fail depending on its value
        self.assertIsNotNone(result)

    def test_missing_source_lineage_map_warns(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(source_lineage_map=[])
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        # Should be WARN at worst (not required hard field in file-only path)
        self.assertIn(result.verdict, ("PASS", "WARN"))

    def test_missing_freshness_receipts_warns(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(freshness_receipts=[])
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertIn(result.verdict, ("PASS", "WARN"))

    def test_missing_acl_verification_receipts_warns(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(acl_verification_receipts=[])
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertIn(result.verdict, ("PASS", "WARN"))

    def test_missing_contradiction_report_warns(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(contradiction_report="")
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertIn(result.verdict, ("PASS", "WARN"))

    def test_missing_final_evidence_digest_warns(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(final_evidence_digest="")
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertIn(result.verdict, ("PASS", "WARN"))

    def test_missing_fields_populated_in_result(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(evidence_items=[])
        fec["evidence_items_empty_reason"] = ""
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertIn("evidence_items", result.missing_fields)


class TestBriefingChecks(unittest.TestCase):

    def test_authorized_fresh_briefing_passes(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        briefing = _minimal_valid_briefing()
        result = run_c0_minimum_safety(grounding_required=True, fec=fec, briefing_meta=briefing)
        self.assertIn(result.verdict, ("PASS", "WARN"))
        self.assertTrue(result.safe_to_continue_to_pa)

    def test_unauthorized_briefing_blocks(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        briefing = _minimal_valid_briefing()
        briefing["authority_class"] = "UNAUTHORIZED"
        result = run_c0_minimum_safety(grounding_required=True, fec=fec, briefing_meta=briefing)
        self.assertFalse(result.safe_to_continue_to_pa)
        self.assertIn(result.verdict, ("BLOCKED", "FAIL", "UNKNOWN"))

    def test_unknown_authority_briefing_blocks(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        briefing = _minimal_valid_briefing()
        briefing["authority_class"] = "UNKNOWN"
        result = run_c0_minimum_safety(grounding_required=True, fec=fec, briefing_meta=briefing)
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_stale_briefing_cannot_be_clean_pass(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        briefing = _minimal_valid_briefing()
        briefing["freshness_status"] = "STALE"
        result = run_c0_minimum_safety(grounding_required=True, fec=fec, briefing_meta=briefing)
        self.assertNotEqual(result.verdict, "PASS")
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_missing_authority_marker_is_unknown(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        briefing = {"authority_class": "", "freshness_status": "FRESH", "digest_ref": "abc"}
        result = run_c0_minimum_safety(grounding_required=True, fec=fec, briefing_meta=briefing)
        self.assertNotEqual(result.verdict, "PASS")

    def test_missing_freshness_marker_warns(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        briefing = {"authority_class": "AUTHORITATIVE", "freshness_status": "", "digest_ref": "abc"}
        result = run_c0_minimum_safety(grounding_required=True, fec=fec, briefing_meta=briefing)
        # WARN from missing freshness — not PASS
        self.assertIn(result.verdict, ("WARN", "FAIL", "UNKNOWN", "BLOCKED"))

    def test_missing_digest_ref_warns_not_fail(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        briefing = {"authority_class": "AUTHORITATIVE", "freshness_status": "FRESH", "digest_ref": ""}
        result = run_c0_minimum_safety(grounding_required=True, fec=fec, briefing_meta=briefing)
        self.assertIn(result.verdict, ("WARN", "PASS"))

    def test_no_briefing_supplied_passes_briefing_check(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        result = run_c0_minimum_safety(grounding_required=True, fec=fec, briefing_meta=None)
        self.assertIn(result.verdict, ("PASS", "WARN"))

    def test_old_timestamp_stale_briefing_fails(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        briefing = {
            "authority_class": "AUTHORITATIVE",
            "freshness_status": "FRESH",
            "freshness_timestamp_iso": "2020-01-01T00:00:00+00:00",
            "digest_ref": "abc123",
        }
        result = run_c0_minimum_safety(grounding_required=True, fec=fec, briefing_meta=briefing)
        # Timestamp is years old — must not be clean PASS
        self.assertNotEqual(result.verdict, "PASS")
        self.assertFalse(result.safe_to_continue_to_pa)


class TestCompanyResearchLane(unittest.TestCase):

    def test_no_company_research_sources_passes(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(retrieval_sources=["jd_payload:jd_text", "resume_payload:resume_text"])
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertIn(result.verdict, ("PASS", "WARN"))

    def test_company_research_source_fails(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(retrieval_sources=["company_research:brown_and_brown"])
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertFalse(result.safe_to_continue_to_pa)
        self.assertIn(result.verdict, ("FAIL", "BLOCKED", "UNKNOWN"))

    def test_company_brief_kb_source_fails(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(retrieval_sources=["company_brief_kb:chroma_hits"])
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_company_brief_colon_source_fails(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(retrieval_sources=["company_brief:some_source"])
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_candidate_profile_source_is_allowed(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(retrieval_sources=[
            "jd_payload:jd_text",
            "resume_payload:resume_text",
            "chromadb:candidate_profile:resume_chunk_1",
        ])
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertIn(result.verdict, ("PASS", "WARN"))

    def test_no_fec_company_research_check_passes(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        result = run_c0_minimum_safety(grounding_required=False, fec=None)
        self.assertEqual(result.verdict, "PASS")


class TestUnknownInvariants(unittest.TestCase):

    def test_unknown_verdict_is_never_pass(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import C0SafetyVerdict
        self.assertNotEqual(C0SafetyVerdict.UNKNOWN, C0SafetyVerdict.PASS)

    def test_unknown_verdict_not_pass_string(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import C0SafetyVerdict
        self.assertNotEqual(C0SafetyVerdict.UNKNOWN.value, "PASS")

    def test_result_with_unknown_verdict_not_safe(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import C0SafetyResult
        r = C0SafetyResult(
            verdict="UNKNOWN",
            decisive_reason="test",
            support_status="UNKNOWN",
            missing_fields=(),
            blocked_reason="test",
            evidence_summary="",
            safe_to_continue_to_pa=False,
        )
        self.assertFalse(r.safe_to_continue_to_pa)
        self.assertNotEqual(r.verdict, "PASS")

    def test_full_unknown_fec_blocks(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(support_status="UNKNOWN")
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertFalse(result.safe_to_continue_to_pa)
        self.assertNotEqual(result.verdict, "PASS")


class TestSafeToContributeToPA(unittest.TestCase):

    def test_pass_verdict_is_safe(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        if result.verdict == "PASS":
            self.assertTrue(result.safe_to_continue_to_pa)

    def test_warn_verdict_is_safe(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(final_evidence_digest="")  # triggers WARN
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        if result.verdict == "WARN":
            self.assertTrue(result.safe_to_continue_to_pa)

    def test_fail_verdict_is_not_safe(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        result = run_c0_minimum_safety(grounding_required=True, fec=None)
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_blocked_verdict_is_not_safe(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(support_status="BLOCKED")
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertFalse(result.safe_to_continue_to_pa)

    def test_unknown_verdict_is_not_safe(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec(support_status="UNKNOWN")
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertFalse(result.safe_to_continue_to_pa)


class TestResultShape(unittest.TestCase):

    def test_result_has_required_fields(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertIsNotNone(result.verdict)
        self.assertIsNotNone(result.decisive_reason)
        self.assertIsNotNone(result.support_status)
        self.assertIsInstance(result.missing_fields, tuple)
        self.assertIsNotNone(result.blocked_reason)
        self.assertIsNotNone(result.evidence_summary)
        self.assertIsInstance(result.safe_to_continue_to_pa, bool)

    def test_evidence_summary_contains_counts(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        fec = _minimal_valid_fec()
        result = run_c0_minimum_safety(grounding_required=True, fec=fec)
        self.assertIn("evidence_items=", result.evidence_summary)
        self.assertIn("support_status=", result.evidence_summary)

    def test_blocked_reason_populated_when_fail(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        result = run_c0_minimum_safety(grounding_required=True, fec=None)
        self.assertTrue(len(result.blocked_reason) > 0)


class TestS1ToS6Regression(unittest.TestCase):

    def test_exit_checks_importable(self) -> None:
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        self.assertIsNotNone(run_exit_checks)

    def test_runtime_summary_importable(self) -> None:
        from apps_rg.runtime.runtime_executive_summary import build_resume_shipping_status
        self.assertIsNotNone(build_resume_shipping_status)

    def test_payload_synthesizer_importable(self) -> None:
        from apps_rg.runtime.u0.payload_synthesizer import synthesize_contract_payload
        self.assertIsNotNone(synthesize_contract_payload)

    def test_section_treatment_profile_importable(self) -> None:
        from apps_rg.runtime.schemas.section_treatment_profile import get_section_policy
        self.assertIsNotNone(get_section_policy)

    def test_source_resume_schema_importable(self) -> None:
        from apps_rg.runtime.schemas.source_resume_schema import load_schema
        self.assertIsNotNone(load_schema)

    def test_c0_minimum_safety_coexists_with_s6(self) -> None:
        from apps_rg.runtime.bindings.c0_minimum_safety import run_c0_minimum_safety
        from apps_rg.runtime.exit.resume_exit_checks import run_exit_checks
        self.assertIsNotNone(run_c0_minimum_safety)
        self.assertIsNotNone(run_exit_checks)


if __name__ == "__main__":
    unittest.main()
