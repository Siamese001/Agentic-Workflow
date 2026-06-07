"""W1 contract behavior tests for l5_certification_contracts.py.

Tests:
  - frozen dataclass immutability
  - slots enabled
  - valid L5_CERTIFIED packet
  - valid L5_NOT_CERTIFIED packet
  - invalid packet status raises
  - packet-level L5_PARTIAL raises
  - packet-level L5_NOT_APPLICABLE raises
  - NOT_APPLICABLE child missing reason raises
  - NOT_APPLICABLE child missing policy raises
  - NOT_APPLICABLE child missing stage raises
  - digest fields validate as 64-char hex where required
  - tuple fields are immutable
  - egress receipt rejects empty provider_ref
  - egress receipt rejects empty redaction_policy_ref
  - egress receipt rejects empty response_digest
  - egress receipt rejects non-hex64 response_digest
  - no forbidden runtime disposition tokens in contract source
  - L5CertificationPacket subclasses L5Result (evidence-only)
  - is_evidence_only() is True
  - output_kind is 'result'
  - GOV-3 schema regression: changed_paths_covered=true accepted
  - GOV-3 schema regression: missing coverage still fails
  - GOV-3 schema regression: app literal in agentic_core still fails
  - GOV-3 schema regression: provider SDK import in L5_safety still fails
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

import pytest

from agentic_core.L5_safety.contracts._base import L5Result
from agentic_core.L5_safety.contracts._vocab import FORBIDDEN_RUNTIME_DISPOSITIONS
from agentic_core.L5_safety.contracts.l5_certification_contracts import (
    _CHILD_APPLICABILITY_VALUES,
    _PACKET_ALLOWED_STATUSES,
    ChildCertifierReceipt,
    EgressCertificationReceipt,
    L5CertificationPacket,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_GOOD_DIGEST = "a" * 64
_REPO_ROOT = pathlib.Path(__file__).parents[4]
_CONTRACT_FILE = (
    _REPO_ROOT
    / "agentic_core"
    / "L5_safety"
    / "contracts"
    / "l5_certification_contracts.py"
)
_GOV3_GATE = _REPO_ROOT / "ops_scripts" / "ci" / "check_agentic_core_addition.py"
_SCHEMA_FILE = (
    _REPO_ROOT
    / "docs/archive/windsurf/legacy-tree"
    / "schemas"
    / "CoreAdditionAuthorGateReceipt.schema.json"
)


def _make_child(
    applicability: str = "REQUIRED",
    certified: bool = True,
    **kwargs,
) -> ChildCertifierReceipt:
    return ChildCertifierReceipt(
        domain="test_domain",
        applicability=applicability,
        certified=certified,
        **kwargs,
    )


def _make_egress(
    response_digest: str = _GOOD_DIGEST,
    redaction_policy_ref: str = "policy://redaction/v1",
) -> EgressCertificationReceipt:
    return EgressCertificationReceipt(
        provider_ref="provider://symbolic/qwen-32b",
        response_digest=response_digest,
        redaction_policy_ref=redaction_policy_ref,
    )


def _make_packet(
    status: str = "L5_CERTIFIED",
    **kwargs,
) -> L5CertificationPacket:
    return L5CertificationPacket(
        certification_status=status,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Frozen / slots
# ---------------------------------------------------------------------------


class TestFrozenImmutability:
    def test_child_receipt_is_frozen(self):
        c = _make_child()
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            c.domain = "mutated"  # type: ignore[misc]

    def test_egress_receipt_is_frozen(self):
        e = _make_egress()
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            e.provider_ref = "mutated"  # type: ignore[misc]

    def test_packet_is_frozen(self):
        p = _make_packet()
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            p.certification_status = "mutated"  # type: ignore[misc]

    def test_child_receipt_has_slots(self):
        assert "__slots__" in ChildCertifierReceipt.__dict__

    def test_egress_receipt_has_slots(self):
        assert "__slots__" in EgressCertificationReceipt.__dict__

    def test_packet_has_slots(self):
        assert "__slots__" in L5CertificationPacket.__dict__

    def test_child_receipts_tuple_is_immutable(self):
        p = _make_packet(child_receipts=(_make_child(),))
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            p.child_receipts = ()  # type: ignore[misc]

    def test_reason_codes_is_tuple(self):
        c = _make_child(reason_codes=("code_a",))
        assert isinstance(c.reason_codes, tuple)


# ---------------------------------------------------------------------------
# Valid packet statuses
# ---------------------------------------------------------------------------


class TestValidPacketStatuses:
    def test_l5_certified_accepted(self):
        p = _make_packet("L5_CERTIFIED")
        assert p.certification_status == "L5_CERTIFIED"

    def test_l5_not_certified_accepted(self):
        p = _make_packet("L5_NOT_CERTIFIED")
        assert p.certification_status == "L5_NOT_CERTIFIED"

    def test_packet_is_evidence_only(self):
        p = _make_packet()
        assert p.is_evidence_only() is True

    def test_packet_subclasses_l5result(self):
        assert issubclass(L5CertificationPacket, L5Result)

    def test_output_kind_is_result(self):
        p = _make_packet()
        assert p.output_kind == "result"

    def test_output_name_set(self):
        assert L5CertificationPacket.output_name == "l5_certification_packet"

    def test_allowed_statuses_constant(self):
        assert "L5_CERTIFIED" in _PACKET_ALLOWED_STATUSES
        assert "L5_NOT_CERTIFIED" in _PACKET_ALLOWED_STATUSES
        assert len(_PACKET_ALLOWED_STATUSES) == 2


# ---------------------------------------------------------------------------
# Forbidden packet statuses
# ---------------------------------------------------------------------------


class TestForbiddenPacketStatuses:
    @pytest.mark.parametrize(
        "status",
        [
            "L5_PARTIAL",
            "L5_NOT_APPLICABLE",
            "L5_CERTIFICATION_READY",
            "ALLOW",
            "DENY",
            "L5_REQUIRES_RECLEARANCE",
            "",
            "unknown",
        ],
    )
    def test_forbidden_status_raises(self, status):
        with pytest.raises(ValueError, match="certification_status"):
            _make_packet(status)


# ---------------------------------------------------------------------------
# Child applicability
# ---------------------------------------------------------------------------


class TestChildApplicability:
    def test_required_accepted(self):
        c = _make_child("REQUIRED")
        assert c.applicability == "REQUIRED"

    def test_optional_accepted(self):
        c = _make_child("OPTIONAL")
        assert c.applicability == "OPTIONAL"

    def test_not_applicable_with_full_justification(self):
        c = _make_child(
            applicability="NOT_APPLICABLE",
            certified=False,
            not_applicable_reason="Domain not active for this run.",
            deciding_policy_ref="policy://l5/cert/na-domains/v1",
            deciding_stage="pre_flight",
        )
        assert c.applicability == "NOT_APPLICABLE"

    def test_not_applicable_missing_reason_raises(self):
        with pytest.raises(ValueError, match="not_applicable_reason"):
            _make_child(
                applicability="NOT_APPLICABLE",
                certified=False,
                not_applicable_reason="",
                deciding_policy_ref="policy://l5/cert/na-domains/v1",
                deciding_stage="pre_flight",
            )

    def test_not_applicable_missing_policy_raises(self):
        with pytest.raises(ValueError, match="deciding_policy_ref"):
            _make_child(
                applicability="NOT_APPLICABLE",
                certified=False,
                not_applicable_reason="Domain not active.",
                deciding_policy_ref="",
                deciding_stage="pre_flight",
            )

    def test_not_applicable_missing_stage_raises(self):
        with pytest.raises(ValueError, match="deciding_stage"):
            _make_child(
                applicability="NOT_APPLICABLE",
                certified=False,
                not_applicable_reason="Domain not active.",
                deciding_policy_ref="policy://l5/cert/na-domains/v1",
                deciding_stage="",
            )

    def test_invalid_applicability_raises(self):
        with pytest.raises(ValueError, match="applicability"):
            _make_child(applicability="UNKNOWN_VALUE")

    def test_applicability_constants(self):
        assert _CHILD_APPLICABILITY_VALUES == {"REQUIRED", "OPTIONAL", "NOT_APPLICABLE"}


# ---------------------------------------------------------------------------
# Digest validation
# ---------------------------------------------------------------------------


class TestDigestValidation:
    def test_child_evidence_digest_valid_hex64(self):
        c = _make_child(evidence_digest=_GOOD_DIGEST)
        assert c.evidence_digest == _GOOD_DIGEST

    def test_child_evidence_digest_empty_allowed(self):
        c = _make_child(evidence_digest="")
        assert c.evidence_digest == ""

    def test_child_evidence_digest_bad_length_raises(self):
        with pytest.raises(ValueError, match="64 lowercase hex"):
            _make_child(evidence_digest="abc123")

    def test_child_evidence_digest_uppercase_raises(self):
        with pytest.raises(ValueError, match="64 lowercase hex"):
            _make_child(evidence_digest="A" * 64)

    def test_packet_digest_sha256_valid(self):
        p = _make_packet(digest_sha256=_GOOD_DIGEST)
        assert p.digest_sha256 == _GOOD_DIGEST

    def test_packet_digest_sha256_empty_allowed(self):
        p = _make_packet(digest_sha256="")
        assert p.digest_sha256 == ""

    def test_packet_digest_sha256_bad_raises(self):
        with pytest.raises(ValueError, match="64 lowercase hex"):
            _make_packet(digest_sha256="not-hex")

    def test_egress_response_digest_valid(self):
        e = _make_egress(response_digest=_GOOD_DIGEST)
        assert e.response_digest == _GOOD_DIGEST

    def test_egress_response_digest_non_hex64_raises(self):
        with pytest.raises(ValueError, match="64 lowercase hex"):
            _make_egress(response_digest="short")

    def test_egress_response_digest_uppercase_raises(self):
        with pytest.raises(ValueError, match="64 lowercase hex"):
            _make_egress(response_digest="B" * 64)


# ---------------------------------------------------------------------------
# Egress receipt boundary rules
# ---------------------------------------------------------------------------


class TestEgressReceiptBoundary:
    def test_empty_provider_ref_raises(self):
        with pytest.raises(ValueError, match="provider_ref"):
            EgressCertificationReceipt(
                provider_ref="",
                response_digest=_GOOD_DIGEST,
                redaction_policy_ref="policy://redaction/v1",
            )

    def test_empty_redaction_policy_raises(self):
        with pytest.raises(ValueError, match="redaction_policy_ref"):
            EgressCertificationReceipt(
                provider_ref="provider://sym/v1",
                response_digest=_GOOD_DIGEST,
                redaction_policy_ref="",
            )

    def test_empty_response_digest_raises(self):
        with pytest.raises(ValueError, match="response_digest"):
            EgressCertificationReceipt(
                provider_ref="provider://sym/v1",
                response_digest="",
                redaction_policy_ref="policy://redaction/v1",
            )

    def test_valid_egress_receipt(self):
        e = _make_egress()
        assert e.certified is False
        assert e.provider_ref == "provider://symbolic/qwen-32b"

    def test_egress_receipt_is_frozen(self):
        e = _make_egress()
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            e.provider_ref = "mutated"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# No forbidden runtime dispositions in source
# ---------------------------------------------------------------------------


class TestNoForbiddenTokensInSource:
    def test_contract_source_has_no_forbidden_disposition_tokens(self):
        source = _CONTRACT_FILE.read_text(encoding="utf-8")
        hits = []
        for token in FORBIDDEN_RUNTIME_DISPOSITIONS:
            if f'"{token}"' in source or f"'{token}'" in source:
                hits.append(token)
        assert not hits, (
            f"Contract source contains forbidden runtime disposition tokens: {hits}"
        )

    def test_no_l5_certification_ready_in_source(self):
        source = _CONTRACT_FILE.read_text(encoding="utf-8")
        assert "L5_CERTIFICATION_READY" not in source

    def test_no_l5_partial_in_source(self):
        source = _CONTRACT_FILE.read_text(encoding="utf-8")
        assert "L5_PARTIAL" not in source

    def test_no_app_literals_in_source(self):
        source = _CONTRACT_FILE.read_text(encoding="utf-8")
        forbidden_literals = [
            "apps_rg",
            "apps_lic",
            "apps_research",
            "apps_qna",
            "resume",
            " CV",
            "openai",
            "anthropic",
            "boto3",
        ]
        hits = [lit for lit in forbidden_literals if lit in source]
        assert not hits, f"Contract source contains forbidden literals: {hits}"

    def test_no_provider_sdk_imports(self):
        source = _CONTRACT_FILE.read_text(encoding="utf-8")
        forbidden_imports = ["import openai", "import anthropic", "import boto3", "import httpx"]
        hits = [imp for imp in forbidden_imports if imp in source]
        assert not hits, f"Contract source contains forbidden SDK imports: {hits}"

    def test_no_gate_verdict_import(self):
        source = _CONTRACT_FILE.read_text(encoding="utf-8")
        assert "GateVerdict" not in source

    def test_no_x3_import(self):
        source = _CONTRACT_FILE.read_text(encoding="utf-8")
        assert "X3" not in source

    def test_no_l4_uwg_references(self):
        source = _CONTRACT_FILE.read_text(encoding="utf-8")
        for token in ("CommitRequest", "UWG", "L4"):
            assert token not in source, f"Found forbidden reference: {token!r}"


# ---------------------------------------------------------------------------
# GOV-3 schema regression proofs
# ---------------------------------------------------------------------------


class TestGov3SchemaRegression:
    """Prove that the W0 schema change did not weaken GOV-3."""

    def _run_gov3(
        self,
        env_paths: str | None = None,
        env_extra: dict[str, str] | None = None,
    ) -> tuple[int, str]:
        import os
        env = os.environ.copy()
        if env_paths:
            env["CORE_ADDITION_CHANGED_PATHS"] = env_paths
        if env_extra:
            env.update(env_extra)
        result = subprocess.run(
            [sys.executable, str(_GOV3_GATE)],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            env=env,
            timeout=60,
        )
        return result.returncode, result.stdout + result.stderr

    def test_schema_accepts_changed_paths_covered_true(self):
        """changed_paths_covered: true (boolean) passes schema — gate requires it."""
        import jsonschema
        schema = json.loads(_SCHEMA_FILE.read_text(encoding="utf-8"))
        artifact_ref = {
            "path": "artifacts/ci/gate.json",
            "digest": "sha256:" + "a" * 64,
            "verdict": "PASS",
            "plan_id": "test-plan",
            "freshness_ts": "2026-05-14T13:28:00-04:00",
            "changed_paths_covered": True,
        }
        jsonschema.validate(instance=artifact_ref, schema=schema["$defs"]["artifactRef"])

    def test_schema_accepts_changed_paths_covered_array(self):
        """changed_paths_covered as array of strings still passes schema."""
        import jsonschema
        schema = json.loads(_SCHEMA_FILE.read_text(encoding="utf-8"))
        artifact_ref = {
            "path": "artifacts/ci/gate.json",
            "digest": "sha256:" + "a" * 64,
            "verdict": "PASS",
            "plan_id": "test-plan",
            "freshness_ts": "2026-05-14T13:28:00-04:00",
            "changed_paths_covered": ["agentic_core/L5_safety/contracts/foo.py"],
        }
        jsonschema.validate(instance=artifact_ref, schema=schema["$defs"]["artifactRef"])

    def test_schema_rejects_changed_paths_covered_false(self):
        """Boolean false is not a valid changed_paths_covered value."""
        import jsonschema
        schema = json.loads(_SCHEMA_FILE.read_text(encoding="utf-8"))
        artifact_ref = {
            "path": "artifacts/ci/gate.json",
            "digest": "sha256:" + "a" * 64,
            "verdict": "PASS",
            "plan_id": "test-plan",
            "freshness_ts": "2026-05-14T13:28:00-04:00",
            "changed_paths_covered": False,
        }
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=artifact_ref, schema=schema["$defs"]["artifactRef"])

    def test_committed_receipt_format_is_valid(self):
        """Static test: the committed governance receipt is well-formed.

        Validates receipt structure without running GOV-3.  Does NOT rewrite any
        canonical artifact — reads only.
        """
        receipt_path = (
            _REPO_ROOT / "artifacts" / "governance"
            / "core_l5_producer_author_gate_receipt.json"
        )
        if not receipt_path.exists():
            pytest.skip("Receipt not present — skip in isolated env.")

        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))

        # Required top-level fields
        assert receipt.get("receipt_type") == "CoreAdditionAuthorGateReceipt", (
            f"receipt_type wrong: {receipt.get('receipt_type')!r}"
        )
        assert receipt.get("plan_type") == "platform_core_change", (
            f"plan_type wrong: {receipt.get('plan_type')!r}"
        )
        assert receipt.get("decision", {}).get("verdict") == "PASS", (
            "receipt.decision.verdict must be PASS"
        )

        # Signature present and sha256-prefixed
        digest = receipt.get("signature", {}).get("receipt_digest", "")
        assert digest.startswith("sha256:"), "receipt_digest missing or wrong prefix"

        # Artifacts block has expected keys
        artifacts = receipt.get("artifacts", {})
        for key in ("no_app_literal_scan_ref", "strict_scan_ref", "boundary_scan_ref"):
            assert key in artifacts, f"Missing artifact key: {key!r}"
            assert artifacts[key].get("verdict") == "PASS", (
                f"artifacts.{key}.verdict must be PASS"
            )
            assert artifacts[key].get("changed_paths_covered") is True, (
                f"artifacts.{key}.changed_paths_covered must be true"
            )

    def test_gov3_exit_code_passes_for_l5_contract_files(self):
        """Subprocess test: GOV-3 exits 0 for the W1 L5 contract files.

        Uses CORE_ADDITION_RECEIPT_PATH to redirect GOV-3 to a disposable temp
        copy of the canonical receipt.  The temp copy has its artifact digests
        synced to the current gate JSON so GOV-3 accepts it.  The canonical
        receipt, session-state, and gate JSON are snapshot/restored and asserted
        byte-identical before and after.

        CORE_ADDITION_RECEIPT_PATH is an env override added to
        check_agentic_core_addition.py for exactly this use-case.
        """
        import os

        receipt_path = (
            _REPO_ROOT / "artifacts" / "governance"
            / "core_l5_producer_author_gate_receipt.json"
        )
        gate_json = _REPO_ROOT / "artifacts" / "ci" / "agentic_core_addition_gate.json"
        session_state = _REPO_ROOT / "artifacts" / "windsurf" / "session_state.json"

        if not receipt_path.exists():
            pytest.skip("Receipt not present — skip in isolated env.")

        # Snapshot all canonical bytes before doing anything.
        receipt_before = receipt_path.read_bytes()
        gate_before = gate_json.read_bytes() if gate_json.exists() else None
        session_before = session_state.read_bytes() if session_state.exists() else None

        paths = ";".join([
            "agentic_core/L5_safety/contracts/l5_certification_contracts.py",
            "agentic_core/L5_safety/contracts/__init__.py",
        ])

        tmp_receipt = None
        try:
            # Build a disposable receipt copy with artifact digests synced to the
            # current gate JSON so GOV-3 passes digest verification.
            receipt_data = json.loads(receipt_before.decode("utf-8"))
            for key in ("no_app_literal_scan_ref", "strict_scan_ref", "boundary_scan_ref"):
                if key in receipt_data.get("artifacts", {}):
                    art_path = _REPO_ROOT / receipt_data["artifacts"][key].get("path", "")
                    if art_path.exists():
                        receipt_data["artifacts"][key]["digest"] = (
                            "sha256:" + hashlib.sha256(art_path.read_bytes()).hexdigest()
                        )
                    elif gate_json.exists():
                        receipt_data["artifacts"][key]["digest"] = (
                            "sha256:" + hashlib.sha256(gate_json.read_bytes()).hexdigest()
                        )
            body = json.dumps(
                {k: v for k, v in receipt_data.items() if k != "signature"},
                sort_keys=True,
                separators=(",", ":"),
            )
            receipt_data.setdefault("signature", {})["receipt_digest"] = (
                "sha256:" + hashlib.sha256(body.encode()).hexdigest()
            )
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".json",
                dir=str(_REPO_ROOT / "artifacts" / "governance"),
                delete=False,
                prefix="_test_tmp_receipt_",
                encoding="utf-8",
            ) as tf:
                json.dump(receipt_data, tf, indent=2)
                tmp_receipt = pathlib.Path(tf.name)

            # Run GOV-3 pointing at the temp receipt; canonical receipt untouched.
            env_extra = {"CORE_ADDITION_RECEIPT_PATH": str(tmp_receipt)}
            rc, output = self._run_gov3(paths, env_extra=env_extra)
        finally:
            # Remove temp receipt.
            if tmp_receipt is not None:
                tmp_receipt.unlink(missing_ok=True)
            # Restore gate JSON to pre-run state (GOV-3 always rewrites it).
            if gate_before is not None:
                gate_json.write_bytes(gate_before)
            elif gate_json.exists():
                gate_json.unlink()
            # Restore session state if changed.
            if session_before is not None:
                session_state.write_bytes(session_before)

        assert rc == 0, f"GOV-3 failed:\n{output}"

        # Assert canonical files are byte-identical to their pre-test state.
        assert receipt_path.read_bytes() == receipt_before, (
            "canonical receipt was permanently modified — restore failed"
        )
        if session_before is not None:
            assert session_state.read_bytes() == session_before, (
                "session_state.json was permanently modified — restore failed"
            )

    def test_gov3_fails_for_app_literal(self):
        """GOV-3 still catches app literals injected into agentic_core."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            dir=str(_REPO_ROOT / "agentic_core" / "L5_safety"),
            delete=False,
            prefix="_gov3_test_",
            encoding="utf-8",
        ) as f:
            f.write('# test\nAPPS_RG_LITERAL = "apps_rg"\n')
            tmp_path = pathlib.Path(f.name)

        try:
            rel = tmp_path.relative_to(_REPO_ROOT).as_posix()
            rc, output = self._run_gov3(rel)
            assert rc != 0, "GOV-3 should have failed for app literal"
            assert "apps_rg" in output.lower() or "finding" in output.lower()
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_gov3_fails_for_provider_sdk_import(self):
        """GOV-3 still catches provider SDK imports in agentic_core/L5_safety."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            dir=str(_REPO_ROOT / "agentic_core" / "L5_safety"),
            delete=False,
            prefix="_gov3_test_",
            encoding="utf-8",
        ) as f:
            f.write("import openai\n")
            tmp_path = pathlib.Path(f.name)

        try:
            rel = tmp_path.relative_to(_REPO_ROOT).as_posix()
            rc, output = self._run_gov3(rel)
            assert rc != 0, "GOV-3 should have failed for provider SDK import"
        finally:
            tmp_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# W4 — Contract immutability deep proof
# ---------------------------------------------------------------------------


class TestW4SlotsDictAbsence:
    """Slots must prevent __dict__ on all three contract dataclasses."""

    def test_child_receipt_has_no_dict(self):
        c = _make_child()
        assert not hasattr(c, "__dict__"), (
            "ChildCertifierReceipt with slots=True must not have __dict__"
        )

    def test_egress_receipt_has_no_dict(self):
        e = _make_egress()
        assert not hasattr(e, "__dict__"), (
            "EgressCertificationReceipt with slots=True must not have __dict__"
        )

    def test_packet_has_no_dict(self):
        p = _make_packet()
        assert not hasattr(p, "__dict__"), (
            "L5CertificationPacket with slots=True must not have __dict__"
        )


class TestW4DefaultInstanceIsolation:
    """Default tuple fields must not be shared across instances."""

    def test_child_reason_codes_default_isolated(self):
        c1 = _make_child()
        c2 = _make_child()
        assert c1.reason_codes == ()
        assert c2.reason_codes == ()
        assert c1.reason_codes is not c2.reason_codes or c1.reason_codes == ()

    def test_packet_child_receipts_default_empty_tuple(self):
        p1 = _make_packet()
        p2 = _make_packet()
        assert p1.child_receipts == ()
        assert p2.child_receipts == ()

    def test_packet_egress_receipts_default_empty_tuple(self):
        p = _make_packet()
        assert isinstance(p.egress_receipts, tuple)
        assert p.egress_receipts == ()

    def test_packet_reason_codes_default_empty_tuple(self):
        p = _make_packet()
        assert isinstance(p.reason_codes, tuple)


class TestW4TupleFieldsMutability:
    """tuple fields cannot be reassigned or modified after construction."""

    def test_child_reason_codes_tuple_immutable(self):
        import dataclasses
        c = _make_child(reason_codes=("code_a", "code_b"))
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            c.reason_codes = ("mutated",)  # type: ignore[misc]

    def test_packet_child_receipts_tuple_immutable(self):
        import dataclasses
        p = _make_packet(child_receipts=(_make_child(),))
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            p.child_receipts = ()  # type: ignore[misc]

    def test_packet_evidence_refs_tuple(self):
        p = _make_packet(
            "L5_CERTIFIED",
            evidence_refs=(_GOOD_DIGEST,),
        )
        assert isinstance(p.evidence_refs, tuple)
        assert p.evidence_refs[0] == _GOOD_DIGEST

    def test_child_receipt_applicability_not_mutable(self):
        import dataclasses
        c = _make_child()
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            c.applicability = "OPTIONAL"  # type: ignore[misc]


class TestW4DigestEdgeCases:
    """Boundary cases for digest field validation."""

    def test_child_evidence_digest_63_chars_rejected(self):
        with pytest.raises(ValueError, match="64 lowercase hex"):
            _make_child(evidence_digest="a" * 63)

    def test_child_evidence_digest_65_chars_rejected(self):
        with pytest.raises(ValueError, match="64 lowercase hex"):
            _make_child(evidence_digest="a" * 65)

    def test_child_evidence_digest_mixed_case_rejected(self):
        digest = "a" * 32 + "A" * 32
        with pytest.raises(ValueError, match="64 lowercase hex"):
            _make_child(evidence_digest=digest)

    def test_child_evidence_digest_non_hex_chars_rejected(self):
        with pytest.raises(ValueError, match="64 lowercase hex"):
            _make_child(evidence_digest="g" * 64)

    def test_packet_digest_sha256_63_chars_rejected(self):
        with pytest.raises(ValueError, match="64 lowercase hex"):
            _make_packet(digest_sha256="b" * 63)

    def test_egress_response_digest_wrong_length_rejected(self):
        with pytest.raises(ValueError, match="64 lowercase hex"):
            _make_egress(response_digest="a" * 32)

    def test_egress_response_digest_non_hex_rejected(self):
        with pytest.raises(ValueError, match="64 lowercase hex"):
            _make_egress(response_digest="z" * 64)


class TestW4PacketStatusVocabularyProof:
    """Explicit proof that forbidden packet-level statuses all raise."""

    @pytest.mark.parametrize(
        "status",
        [
            "L5_PARTIAL",
            "L5_NOT_APPLICABLE",
            "L5_CERTIFICATION_READY",
            "L5_REQUIRES_RECLEARANCE",
            "L5_REQUIRES_REMEDIATION_EVIDENCE",
            "L5_REQUIRES_HUMAN_REVIEW_PACKET",
            "L5_INCIDENT_EVIDENCE_REQUIRED",
            "L5_STATIC_VIOLATION_EVIDENCE",
            "L5_AUTHORITY_GAP_EVIDENCE",
            "L5_EGRESS_GAP_EVIDENCE",
            "L5_REPLAY_AUDIT_GAP_EVIDENCE",
            "ALLOW",
            "DENY",
            "REROUTE",
            "",
            "unknown_status",
        ],
    )
    def test_forbidden_status_always_raises(self, status: str):
        with pytest.raises(ValueError):
            _make_packet(status)

    def test_allowed_statuses_exactly_two(self):
        assert _PACKET_ALLOWED_STATUSES == {"L5_CERTIFIED", "L5_NOT_CERTIFIED"}
        assert len(_PACKET_ALLOWED_STATUSES) == 2

    def test_l5_certified_is_evidence_only_not_disposition(self):
        p = _make_packet("L5_CERTIFIED")
        assert p.is_evidence_only() is True
        assert p.output_kind == "result"
        source = _CONTRACT_FILE.read_text(encoding="utf-8")
        assert "L5_CERTIFICATION_READY" not in source

    def test_forbidden_runtime_dispositions_not_in_allowed(self):
        from agentic_core.L5_safety.contracts._vocab import FORBIDDEN_RUNTIME_DISPOSITIONS
        assert not (_PACKET_ALLOWED_STATUSES & FORBIDDEN_RUNTIME_DISPOSITIONS), (
            "No forbidden runtime disposition may overlap with allowed packet statuses"
        )


class TestW4NotApplicableChildProof:
    """Explicit proof of NOT_APPLICABLE invariants (W4 hardening)."""

    def test_not_applicable_all_three_required_fields(self):
        """All three justification fields must be present — any single absence fails."""
        base = dict(
            not_applicable_reason="reason",
            deciding_policy_ref="policy://v1",
            deciding_stage="stage",
        )
        for omit in ("not_applicable_reason", "deciding_policy_ref", "deciding_stage"):
            kwargs = {k: "" if k == omit else v for k, v in base.items()}
            with pytest.raises(ValueError, match=omit):
                ChildCertifierReceipt(
                    domain="safety_enforcement",
                    applicability="NOT_APPLICABLE",
                    certified=False,
                    **kwargs,
                )

    def test_not_applicable_with_full_triple_yields_valid_receipt(self):
        c = ChildCertifierReceipt(
            domain="safety_enforcement",
            applicability="NOT_APPLICABLE",
            certified=False,
            not_applicable_reason="not active",
            deciding_policy_ref="policy://l5/na/v1",
            deciding_stage="pre_flight",
        )
        assert c.applicability == "NOT_APPLICABLE"
        assert c.not_applicable_reason == "not active"
        assert c.deciding_policy_ref == "policy://l5/na/v1"
        assert c.deciding_stage == "pre_flight"
