"""Hard invariant tests — the things intake MUST NEVER do.

Spec sections:
- THE FRONT DESK / SECURITY CHECK invariants (lines 75-94)
- HARD NO blocks in every E-stage (E1 200-205, E2 255-259, E3 310-314,
  E4 367-371, E5 433-437, E6 490-496)
- INGRESS OUTPUT CONTRACT MUST NOT INCLUDE (lines 535-551)
- OBSERVABILITY HARD NO (lines 660-664)
- SECURITY / AUTHORITY BOUNDARIES (lines 668-702)
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from agentic_core.L0_routing.intake import pipeline as pipeline_mod
from agentic_core.L0_routing.intake import stages as stages_mod
from agentic_core.L0_routing.intake.envelope import RawIngressEnvelope
from agentic_core.L0_routing.intake.events import (
    FORBIDDEN_EVENT_FIELDS,
    INGRESS_METRIC_NAMES,
    IngressEvent,
    IngressEventRecord,
)
from agentic_core.L0_routing.intake.pipeline import IntakePipeline, IntakePolicy
from agentic_core.L0_routing.intake.validated_request import (
    FORBIDDEN_VALIDATED_REQUEST_KEYS,
    ValidatedRequest,
)


# ----------------------------------------------------------------------
# HARD NO: intake never imports L1+, retrievers, models, tools.
# ----------------------------------------------------------------------


_INTAKE_DIR = Path(stages_mod.__file__).parent

# Forbidden import-tokens — fragments that, if present in any intake source
# file, indicate a constitutional violation.
_FORBIDDEN_IMPORT_TOKENS = (
    "from agentic_core.L1_cognition",
    "from agentic_core.L2_execution",
    "from agentic_core.L3_orchestration",
    "from agentic_core.L4_state",
    "from agentic_core.L5_safety",
    "from agentic_core.L6_observability",
    "import agentic_core.L1",
    "import agentic_core.L2",
    "import agentic_core.L3",
    "import agentic_core.L4",
    "import agentic_core.L5",
    "import agentic_core.L6",
    "from openai",
    "import openai",
    "from anthropic",
    "import anthropic",
    "from chromadb",
    "import chromadb",
    "import requests",  # no HTTP from intake
    "import httpx",
    "import urllib.request",
)


@pytest.mark.parametrize(
    "py_file",
    sorted(_INTAKE_DIR.glob("*.py")),
    ids=lambda p: p.name,
)
def test_intake_module_does_not_import_higher_layers(py_file: Path) -> None:
    src = py_file.read_text(encoding="utf-8")
    for token in _FORBIDDEN_IMPORT_TOKENS:
        assert token not in src, (
            f"{py_file.name} contains forbidden import token {token!r}; "
            f"intake must not import models, retrievers, tool runners, or higher layers"
        )


# ----------------------------------------------------------------------
# HARD NO: validated_request carries no route/answer/tool/capability fields
# ----------------------------------------------------------------------


def test_validated_request_has_no_forbidden_fields() -> None:
    """Spec lines 535-551 — MUST NOT INCLUDE."""
    actual = set(ValidatedRequest.__dataclass_fields__.keys())
    leak = actual & FORBIDDEN_VALIDATED_REQUEST_KEYS
    assert not leak, f"Forbidden fields present on ValidatedRequest: {leak}"


def test_downstream_authority_is_pinned_to_none() -> None:
    """Spec line 481: downstream_authority = none."""
    out = IntakePipeline(IntakePolicy()).run(
        RawIngressEnvelope(transport="chat", body_text="hi")
    )
    vr = out.validated
    assert vr is not None
    assert vr.downstream_authority == "none"


def test_permitted_next_layer_is_pinned_to_l1() -> None:
    """Spec line 482: permitted_next_layer = L1 only if pass."""
    out = IntakePipeline(IntakePolicy()).run(
        RawIngressEnvelope(transport="chat", body_text="hi")
    )
    vr = out.validated
    assert vr is not None
    assert vr.permitted_next_layer == "L1"


def test_validated_request_rejects_authority_tampering() -> None:
    """Constructor refuses any non-'none' / non-'L1' value."""
    out = IntakePipeline(IntakePolicy()).run(
        RawIngressEnvelope(transport="chat", body_text="hi")
    )
    base = out.validated
    assert base is not None
    with pytest.raises(ValueError):
        ValidatedRequest(**{**_dataclass_kwargs(base), "downstream_authority": "L2"})
    with pytest.raises(ValueError):
        ValidatedRequest(**{**_dataclass_kwargs(base), "permitted_next_layer": "L2"})


def _dataclass_kwargs(obj) -> dict:
    """Extract constructor kwargs from a frozen dataclass."""
    return {k: getattr(obj, k) for k in obj.__dataclass_fields__.keys()}


# ----------------------------------------------------------------------
# HARD NO: events never carry secrets / credentials / raw payload
# ----------------------------------------------------------------------


def test_event_record_rejects_forbidden_fields() -> None:
    for forbidden in FORBIDDEN_EVENT_FIELDS:
        with pytest.raises(ValueError):
            IngressEventRecord(
                event=IngressEvent.INGRESS_RECEIVED,
                request_id="r",
                trace_root="t",
                fields={forbidden: "leaked"},
            )


def test_pipeline_events_do_not_leak_credentials() -> None:
    env = RawIngressEnvelope(
        transport="api",
        body_text="hello",
        auth_credential={"kind": "api_key", "token": "SUPER_SECRET", "principal_kind": "service"},
        claimed_service_id="svc-1",
    )
    out = IntakePipeline(IntakePolicy()).run(env)
    assert out.accepted
    for evt in out.events:
        flat = repr(evt.fields)
        assert "SUPER_SECRET" not in flat, f"Credential leaked into event {evt.event}"
        assert "api_key" not in flat or "kind" in flat  # may carry kind label, never raw value


# ----------------------------------------------------------------------
# E1 hard-no: no semantic interpretation, no fetch, no model call
# ----------------------------------------------------------------------


def test_e1_does_not_fetch_attachments() -> None:
    """Spec lines 200-204 — no retrieval of referenced URLs/files."""
    src = (Path(stages_mod.__file__)).read_text(encoding="utf-8")
    # No HTTP libraries in stages.py
    forbidden_calls = ["requests.get", "httpx.get", "urlopen", "fetch_url"]
    for call in forbidden_calls:
        assert call not in src, f"E1 must not perform fetch ({call} found)"


# ----------------------------------------------------------------------
# E5 hard-no: no answer drafting, no semantic cleanup, no prompt assembly
# ----------------------------------------------------------------------


def test_e5_does_not_summarize_or_rewrite() -> None:
    """Spec lines 405-414, 433-437."""
    src = (Path(stages_mod.__file__)).read_text(encoding="utf-8")
    # No model calls
    assert "openai" not in src.lower()
    assert "anthropic" not in src.lower()
    # No "summarize" function or call in stages
    assert "def summarize" not in src
    assert ".summarize(" not in src


# ----------------------------------------------------------------------
# Pipeline state isolation
# ----------------------------------------------------------------------


def test_pipeline_returns_validated_xor_rejected() -> None:
    """A pass produces validated_request, a fail produces rejected_request_notice — never both."""
    out = IntakePipeline(IntakePolicy()).run(
        RawIngressEnvelope(transport="chat", body_text="hi")
    )
    assert (out.validated is None) != (out.rejected is None)


def test_pipeline_does_not_run_downstream_stages_on_e1_failure() -> None:
    """When E1 fails, E2..E6 fields are not stamped."""
    out = IntakePipeline(IntakePolicy()).run(
        RawIngressEnvelope(transport="smtp", body_text="x")
    )
    assert out.rejected is not None
    assert out.rejected.rejection_stage == "E1"
    # No auth/quota/schema/normalization verdicts on E1-rejection audit
    assert out.audit.auth_verdict is None
    assert out.audit.quota_verdict is None


def test_pipeline_only_emits_intake_events() -> None:
    """No non-intake event types emitted (e.g., RouteSelected, ToolInvoked)."""
    out = IntakePipeline(IntakePolicy()).run(
        RawIngressEnvelope(transport="chat", body_text="hi")
    )
    for evt in out.events:
        assert isinstance(evt.event, IngressEvent)


# ----------------------------------------------------------------------
# Metric name stability
# ----------------------------------------------------------------------


def test_all_11_metric_names_present() -> None:
    """Spec lines 634-645."""
    expected = {
        "ingress_count",
        "ingress_reject_rate",
        "auth_reject_rate",
        "quota_throttle_rate",
        "duplicate_rate",
        "malformed_schema_rate",
        "unsupported_modality_rate",
        "average_payload_size",
        "attachment_count_distribution",
        "ingress_latency_ms",
        "normalization_failure_rate",
    }
    assert set(INGRESS_METRIC_NAMES) == expected


def test_all_11_event_types_present() -> None:
    """Spec lines 622-632."""
    expected = {
        "IngressReceived",
        "RequestIdAssigned",
        "TraceRootBound",
        "SourceClassified",
        "AuthBaselineEvaluated",
        "QuotaEvaluated",
        "SchemaEvaluated",
        "PayloadNormalized",
        "AttachmentManifestCaptured",
        "IngressAccepted",
        "IngressRejected",
    }
    actual = {e.value for e in IngressEvent}
    assert actual == expected


# ----------------------------------------------------------------------
# Pipeline class shape
# ----------------------------------------------------------------------


def test_pipeline_run_signature() -> None:
    sig = inspect.signature(IntakePipeline.run)
    # (self, env) -> IntakeOutcome
    assert list(sig.parameters.keys()) == ["self", "env"]


def test_pipeline_module_does_not_call_l1_or_l2() -> None:
    """Defense-in-depth: pipeline.py source has no L1/L2 imports."""
    src = Path(pipeline_mod.__file__).read_text(encoding="utf-8")
    assert "L1_cognition" not in src
    assert "L2_execution" not in src
    assert "L3_orchestration" not in src
