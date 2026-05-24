"""Executive-summary X1D judge packet coherence + provider transport parity audits.

Catches the Brown & Brown class bug: X2 all PASS, Gemini/OpenAI PASS, Claude FAIL on the
same packet because GRAPH rubric soft-penalties conflict with deterministic_gate_summary and
provider adapters diverge (Anthropic missing shared score schema / JSON lock).
"""

from __future__ import annotations

import inspect
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.judges import executive_summary_judge_packet as judge_packet_mod
from apps_rg.runtime.judges.executive_summary_judge_packet import (
    GRAPH_ONLY_GRADE_ONLY_RUBRIC,
    build_executive_summary_judge_packet,
    judge_contract_hash,
    reconcile_grade_only_judge_result,
    reconcile_judge_result_against_deterministic_gate_closures,
    render_judge_prompt_from_packet,
)
from apps_rg.runtime.judges.executive_summary_x1d import (
    ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS,
    GOOGLE_AI_JUDGE_MAX_OUTPUT_TOKENS,
    _call_anthropic,
    _call_gemini,
    _call_openai,
    _make_model_backed_output,
)
from apps_rg.runtime.sections.section_x2_x1d_contract import X2X1dDriftViolation

# SRFS dim-8 authority text (active graph rubric must include equivalent).
X2_SUPREMACY_PHRASES: tuple[str, ...] = (
    "penalize gates that show",
    "deterministic_alignment",
    '"pass": false',
    "pass\": false",
)

# When these X2 gates are pass:true, active rubric must not instruct soft-fail on that axis.
GATE_PASSED_FORBIDDEN_RUBRIC_PHRASES: dict[str, tuple[str, ...]] = {
    "x2_exec_summary_no_credential_dump": (
        "credential inventory",
        "credential dump",
        "credential/certification inventory",
        "bare credential inventory",
    ),
    "x2_exec_summary_evidence_utilization": (
        "penalize under-use",
        "penalize under-use of allowed_fact_packet when unused_fact_ids",
    ),
    "x2_exec_summary_no_mechanism_inventory": (
        "mechanism inventory",
    ),
}

# Live Claude 001344 finding class — reconcile must address when all gates pass (W3 target).
CLAUDE_001344_SOFT_FAIL_FINDINGS: tuple[str, ...] = (
    "Sentences 2-5 read as a metric/credential stack rather than an integrated executive narrative",
    "No meaningful alignment with the JD's emphasis on enterprise architecture",
    "credential inventory despite passing the deterministic gate",
)

# Positive reconcile control: only findings that violate passed X2 gate closures.
CLAUDE_001344_GATE_CLOSURE_ONLY_FINDINGS: tuple[str, ...] = (
    "Sentences 2-5 read as a metric/credential stack rather than an integrated executive narrative",
    "credential inventory despite passing the deterministic gate",
)

CLAUDE_001344_RESIDUAL_QUALITY_FINDINGS: tuple[str, ...] = (
    "Executive positioning is unclear and narrative coherence is weak for an SVP reader.",
    "Poor commercial fit — the paragraph does not read as a cohesive executive story.",
)

CLAUDE_001344_JUDGE_RESULT: dict[str, Any] = {
    "score_scale": "0_to_5",
    "score": 2.8,
    "threshold": 4.0,
    "pass": False,
    "decisive_failure": False,
    "findings": list(CLAUDE_001344_SOFT_FAIL_FINDINGS),
    "cited_sentence_indexes": [2, 3, 4, 5],
    "remediation_suggestions": ["Weave JD emphasis", "Reduce metric stacking"],
}


@dataclass(frozen=True)
class JudgePacketCoherenceViolation:
    code: str
    detail: str
    path: str = ""


def _all_x2_gates_pass(deterministic_gate_summary: dict[str, Any]) -> bool:
    entries = [
        v
        for v in (deterministic_gate_summary or {}).values()
        if isinstance(v, dict) and "pass" in v
    ]
    return bool(entries) and all(bool(v.get("pass")) for v in entries)


def audit_active_graph_rubric_x2_supremacy() -> list[JudgePacketCoherenceViolation]:
    """Active GRAPH rubric must include SRFS-style X2 supremacy (dim 8)."""
    rubric = GRAPH_ONLY_GRADE_ONLY_RUBRIC.lower()
    if "penalize gates that show" in rubric and '"pass": false' in rubric:
        return []
    return [
        JudgePacketCoherenceViolation(
            code="graph_rubric_missing_x2_supremacy",
            detail=(
                "GRAPH_ONLY_GRADE_ONLY_RUBRIC lacks SRFS dim-8 clause "
                f"(expected one of {X2_SUPREMACY_PHRASES!r}); "
                "dim 6 still allows soft-fail on axes X2 may have passed."
            ),
            path=judge_packet_mod.__file__ or "",
        )
    ]


def audit_rubric_soft_penalties_when_gates_pass(
    packet: dict[str, Any],
) -> list[JudgePacketCoherenceViolation]:
    """When gate pass:true, active rubric must not instruct penalizing that axis."""
    summary = packet.get("deterministic_gate_summary") or {}
    if not _all_x2_gates_pass(summary):
        return []
    rubric_lower = str(packet.get("rubric") or "").lower()
    out: list[JudgePacketCoherenceViolation] = []
    for gate_id, required_fragments in GATE_PASSED_FORBIDDEN_RUBRIC_PHRASES.items():
        entry = summary.get(gate_id)
        if not isinstance(entry, dict) or not entry.get("pass"):
            continue
        hits: list[str] = []
        for frag in required_fragments:
            idx = rubric_lower.find(frag.lower())
            if idx < 0:
                continue
            window_before = rubric_lower[max(0, idx - 24) : idx]
            window_after = rubric_lower[idx : idx + 80]
            if "do not" in window_before or "must not" in window_before:
                continue
            if "only when" in window_after and '"pass": false' in window_after:
                continue
            hits.append(frag)
        if not hits:
            continue
        out.append(
            JudgePacketCoherenceViolation(
                code="rubric_soft_penalty_conflicts_with_passed_x2_gate",
                detail=(
                    f"{gate_id} pass:true but rubric still mentions penalizing: {hits!r}"
                ),
                path=judge_packet_mod.__file__ or "",
            )
        )
    return out


def audit_evidence_utilization_prompt_coherence(
    packet: dict[str, Any],
) -> list[JudgePacketCoherenceViolation]:
    """When util gate passes but unused_fact_ids non-empty, prompt must not imply defect."""
    summary = packet.get("deterministic_gate_summary") or {}
    util = summary.get("x2_exec_summary_evidence_utilization")
    if not isinstance(util, dict) or not util.get("pass"):
        return []
    eu = packet.get("evidence_utilization") or {}
    unused = eu.get("unused_fact_ids") or []
    if not unused:
        return []
    rubric_lower = str(packet.get("rubric") or "").lower()
    util_penalty_unconditional = "penalize under-use" in rubric_lower and (
        "only when" not in rubric_lower or '"pass": false' not in rubric_lower
    )
    weave_optional = "optional weave" in rubric_lower or "not proof gaps" in rubric_lower
    if util_penalty_unconditional or (
        not weave_optional
        and "unused_fact_ids" in rubric_lower
        and "penalize under-use" in rubric_lower
    ):
        return [
            JudgePacketCoherenceViolation(
                code="evidence_util_rubric_penalizes_unused_when_x2_util_pass",
                detail=(
                    f"x2_exec_summary_evidence_utilization pass:true but unused_fact_ids={unused!r} "
                    "and rubric still penalizes under-use (X2 structural util does not require citing all facts)."
                ),
                path=judge_packet_mod.__file__ or "",
            )
        ]
    prompt = render_judge_prompt_from_packet(packet)
    if "EVIDENCE_UTILIZATION" not in prompt:
        return []
    start = prompt.index("EVIDENCE_UTILIZATION")
    end = prompt.index("CANDIDATE_OUTPUT:", start) if "CANDIDATE_OUTPUT:" in prompt[start:] else len(prompt)
    section = prompt[start:end].lower()
    optional_markers = ("optional", "not a defect", "not proof gaps", "weave target")
    if not any(m in section for m in optional_markers):
        return [
            JudgePacketCoherenceViolation(
                code="evidence_util_section_missing_optional_weave_semantics",
                detail=(
                    "Rendered EVIDENCE_UTILIZATION block lacks optional-weave semantics "
                    f"while util gate passed and unused_fact_ids={unused!r}."
                ),
                path=judge_packet_mod.__file__ or "",
            )
        ]
    return []


def audit_judge_packet_coherence(packet: dict[str, Any]) -> list[JudgePacketCoherenceViolation]:
    """Full packet coherence audit (rubric + rendered prompt)."""
    violations: list[JudgePacketCoherenceViolation] = []
    violations.extend(audit_active_graph_rubric_x2_supremacy())
    violations.extend(audit_rubric_soft_penalties_when_gates_pass(packet))
    violations.extend(audit_evidence_utilization_prompt_coherence(packet))
    return violations


def audit_provider_transport_parity() -> list[JudgePacketCoherenceViolation]:
    """Provider _call_* wiring must share score-schema system anchors (transport-only deltas OK)."""
    out: list[JudgePacketCoherenceViolation] = []
    anthropic_src = inspect.getsource(_call_anthropic)
    openai_src = inspect.getsource(_call_openai)
    gemini_src = inspect.getsource(_call_gemini)

    if "build_x1d_judge_system_prompt" not in anthropic_src and "JUDGE_SCORE_SCHEMA" not in anthropic_src:
        out.append(
            JudgePacketCoherenceViolation(
                code="anthropic_missing_judge_score_schema",
                detail=(
                    "_call_anthropic does not use build_x1d_judge_system_prompt or JUDGE_SCORE_SCHEMA; "
                    "OpenAI does — judges receive asymmetric instruction anchors."
                ),
                path="apps_rg/runtime/judges/executive_summary_x1d.py",
            )
        )
    if "json_object" not in openai_src and "response_format" not in openai_src:
        out.append(
            JudgePacketCoherenceViolation(
                code="openai_missing_json_mode",
                detail="_call_openai missing response_format json_object",
                path="apps_rg/runtime/judges/executive_summary_x1d.py",
            )
        )
    if "responseSchema" not in gemini_src and "_gemini_generation_config" not in gemini_src:
        out.append(
            JudgePacketCoherenceViolation(
                code="gemini_missing_response_schema",
                detail="_call_gemini missing structured JSON schema enforcement",
                path="apps_rg/runtime/judges/executive_summary_x1d.py",
            )
        )
    if ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS < min(2048, GOOGLE_AI_JUDGE_MAX_OUTPUT_TOKENS // 2):
        out.append(
            JudgePacketCoherenceViolation(
                code="anthropic_token_budget_asymmetric",
                detail=(
                    f"ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS={ANTHROPIC_JUDGE_MAX_OUTPUT_TOKENS} "
                    f"vs GOOGLE_AI_JUDGE_MAX_OUTPUT_TOKENS={GOOGLE_AI_JUDGE_MAX_OUTPUT_TOKENS}"
                ),
                path="apps_rg/runtime/judges/executive_summary_x1d.py",
            )
        )
    if "stop_reason" not in anthropic_src and "max_tokens" in anthropic_src:
        out.append(
            JudgePacketCoherenceViolation(
                code="anthropic_missing_stop_reason_truncation_check",
                detail="_call_anthropic does not check stop_reason for max_tokens truncation",
                path="apps_rg/runtime/judges/executive_summary_x1d.py",
            )
        )
    return out


def audit_reconcile_claude_class_soft_fail() -> list[JudgePacketCoherenceViolation]:
    """reconcile_grade_only_judge_result must not leave Claude-class soft fails when all X2 pass."""
    gate_summary = {
        gid: {"pass": True, "detail": "ok"}
        for gid in (
            "x2_exec_summary_sentence_count_6",
            "x2_exec_summary_evidence_utilization",
            "x2_exec_summary_no_credential_dump",
            "x2_exec_summary_no_mechanism_inventory",
            "x2_exec_summary_paragraph_max_words",
            "x2_exec_summary_meta_filler_zero",
        )
    }
    positive_body = dict(CLAUDE_001344_JUDGE_RESULT)
    positive_body["findings"] = list(CLAUDE_001344_GATE_CLOSURE_ONLY_FINDINGS)
    reconciled = reconcile_judge_result_against_deterministic_gate_closures(
        positive_body,
        gate_summary,
    )
    score = float(reconciled.get("score", 0.0))
    threshold = float(reconciled.get("threshold", 4.0))
    if score >= threshold and not reconciled.get("decisive_failure"):
        return []
    return [
        JudgePacketCoherenceViolation(
            code="reconcile_leaves_claude_class_soft_fail",
            detail=(
                f"All gates pass + Claude 001344-class findings; after reconcile "
                f"score={score} threshold={threshold} decisive_failure={reconciled.get('decisive_failure')!r}"
            ),
            path=judge_packet_mod.__file__ or "",
        )
    ]


def audit_identical_judge_json_same_pass_all_providers() -> list[JudgePacketCoherenceViolation]:
    """Same parsed judge JSON must yield same MODEL_BACKED pass/fail for every provider key."""
    result = {
        "score_scale": "0_to_5",
        "score": 4.2,
        "threshold": 4.0,
        "pass": True,
        "decisive_failure": False,
        "findings": ["ok"],
        "cited_sentence_indexes": [1],
        "remediation_suggestions": [],
    }
    gate_summary = {"x2_exec_summary_sentence_count_6": {"pass": True, "detail": "ok"}}
    statuses: dict[str, str] = {}
    for key in ("gemini_pro", "openai_chatgpt", "anthropic_claude"):
        out = _make_model_backed_output(
            key,
            "hash-parity",
            "test-model",
            dict(result),
            deterministic_gate_summary=gate_summary,
        )
        statuses[key] = out.provider_status
    unique = set(statuses.values())
    if len(unique) == 1:
        return []
    return [
        JudgePacketCoherenceViolation(
            code="provider_pass_math_divergence",
            detail=f"identical judge JSON produced provider_status map: {statuses!r}",
            path="apps_rg/runtime/judges/executive_summary_x1d.py",
        )
    ]


def load_frozen_post_x2_packet(repo_root: Path) -> dict[str, Any] | None:
    """Load Brown & Brown 001344 post-X2 packet when present (optional live fixture)."""
    path = (
        repo_root
        / "artifacts"
        / "apps_rg"
        / "runtime_proofs"
        / "executive_summary"
        / "real"
        / "exec_summary_20260524_001344"
        / "executive_summary_judge_packet_post_x2.json"
    )
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_brown_brown_six_sentence_packet() -> dict[str, Any]:
    """Synthetic packet mirroring 001344: all X2 pass, unused cert fact (fact_certs_001 class)."""
    resume = (
        "Technology strategy executive who operationalizes governed agentic AI platforms for regulated "
        "enterprise workflows with traceable execution and enterprise scale. "
        "Platform commercialization generated $22M in IP-led revenue and expanded gross margins by 20%, "
        "while scaling the ML engineering organization from 8 to 28 specialists. "
        "Implemented Basel III and CCAR data lineage, cataloging, and automated reconciliation across "
        "risk and finance stakeholders. "
        "Re-architected risk analytics with containerized microservices for faster calculations and "
        "real-time stress testing for senior leadership. "
        "Quantitative actuarial depth informs governance and delivery trade-offs across complex programs. "
        "Governed runtime delivery stays audit-ready without weakening commercial velocity."
    )
    allowed = {
        "fact_platform_001",
        "fact_revenue_001",
        "fact_basel_001",
        "fact_risk_001",
        "fact_actuarial_001",
        "fact_governance_001",
        "fact_certs_001",
    }
    ledger = [
        {
            "claim_text": f"claim {i}",
            "source_fact_ids": [f"fact_{name}"],
        }
        for i, name in enumerate(
            ["platform_001", "revenue_001", "basel_001", "risk_001", "actuarial_001", "governance_001"]
        )
    ]
    return build_executive_summary_judge_packet(
        resume_display_text=resume,
        claim_ledger=ledger,
        allowed_fact_packet=[{"fact_id": fid, "claim_text": fid} for fid in sorted(allowed)],
        allowed_fact_ids=allowed,
        target_title="SVP IT Strategy & Innovation",
        target_company="Brown & Brown",
        jd_text="Enterprise architecture, innovation, IT roadmap.",
        briefing_text="Targeting context only.",
        parsed_output={"resume_display_text": resume},
    )


def audit_executive_summary_x1d_judge_coherence(
    packet: dict[str, Any] | None = None,
) -> list[X2X1dDriftViolation]:
    """Convert coherence violations to X2X1dDriftViolation for CI drift gate."""
    from apps_rg.runtime.judges.executive_summary_judge_packet import render_judge_prompt_from_packet
    from apps_rg.runtime.judges.x1d_judge_transport_contract import audit_x1d_judge_transport_parity

    pkt = packet or build_brown_brown_six_sentence_packet()
    rendered = render_judge_prompt_from_packet(pkt)
    raw: list[JudgePacketCoherenceViolation] = []
    raw.extend(audit_judge_packet_coherence(pkt))
    raw.extend(audit_provider_transport_parity())
    raw.extend(audit_reconcile_claude_class_soft_fail())
    raw.extend(audit_identical_judge_json_same_pass_all_providers())
    transport_violations = audit_x1d_judge_transport_parity(pkt, prompt=rendered)
    merged = list(raw) + [
        JudgePacketCoherenceViolation(v.code, v.detail, v.path) for v in transport_violations
    ]
    return [
        X2X1dDriftViolation(
            "executive_summary",
            v.code,
            v.detail,
            v.path or judge_packet_mod.__file__ or "",
        )
        for v in merged
    ]


def assert_executive_summary_x1d_judge_coherence(packet: dict[str, Any] | None = None) -> None:
    violations = audit_executive_summary_x1d_judge_coherence(packet)
    if violations:
        lines = "\n".join(f"  [{v.kind}] {v.detail}" for v in violations)
        raise AssertionError(f"executive_summary X1D judge coherence violations:\n{lines}")


__all__ = [
    "CLAUDE_001344_JUDGE_RESULT",
    "CLAUDE_001344_SOFT_FAIL_FINDINGS",
    "JudgePacketCoherenceViolation",
    "audit_active_graph_rubric_x2_supremacy",
    "audit_evidence_utilization_prompt_coherence",
    "audit_executive_summary_x1d_judge_coherence",
    "audit_identical_judge_json_same_pass_all_providers",
    "audit_judge_packet_coherence",
    "audit_provider_transport_parity",
    "audit_reconcile_claude_class_soft_fail",
    "audit_rubric_soft_penalties_when_gates_pass",
    "assert_executive_summary_x1d_judge_coherence",
    "build_brown_brown_six_sentence_packet",
    "load_frozen_post_x2_packet",
]
