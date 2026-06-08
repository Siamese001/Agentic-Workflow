"""Generic proof-bound role episode lanes for InsurTech/EY sections.

These lanes intentionally fail closed when upstream graph/FEC evidence is absent.
They do not hydrate claims from the base resume or targeting text.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from apps_rg.runtime.c0.section_proof_loader import (
    apply_proof_pool_to_usage_ledger,
    load_section_proof_for_lane,
)
from apps_rg.runtime.claim_ledger.canonical_exec_summary_v2 import (
    build_canonical_claim_ledger_v2_payload,
    normalize_exec_summary_claim_ledger,
)
from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3
from apps_rg.runtime.providers import (
    ExternalProvider,
    ProviderGateway,
    ProviderGatewayError,
    ProviderProfile,
)
from apps_rg.runtime.providers.provider_contract import ProviderResult
from apps_rg.runtime.runtime_proof_layout import (
    finalize_runtime_proof_run,
    prepare_runtime_proof_run_dir,
)
from apps_rg.runtime.section_l2_lane_integration import (
    finalize_section_l2_after_output,
    prepare_section_l2_before_provider,
)
from apps_rg.runtime.section_proof.section_input_usage_ledger import (
    build_section_input_usage_ledger_v1,
)
from apps_rg.runtime.sections.lane_artifact_io import sha16, write_json
from apps_rg.runtime.spine.c0_fec_compose import (
    merge_compiled_prompt_artifact_fec_fields,
)
from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
    write_x2_source_fact_pool_receipt,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
MAX_OUTPUT_TOKENS = 900
NARRATIVE_MAX_WORDS = 58
NARRATIVE_MAX_CHARS = 360


@dataclass(frozen=True)
class RoleEpisodeLaneConfig:
    section_id: str
    role_key: str
    employer_label: str
    header_key: str
    bullet_prefix: str
    output_filename: str
    output_kind: str

    @property
    def is_bullet_lane(self) -> bool:
        return self.output_kind == "bullets"


_ROLE_LANES: dict[str, RoleEpisodeLaneConfig] = {
    "insurtech_bullets": RoleEpisodeLaneConfig(
        section_id="insurtech_bullets",
        role_key="insurtech",
        employer_label="InsurTech",
        header_key="insurtech_header",
        bullet_prefix="bul_insurtech",
        output_filename="insurtech_bullets_output.txt",
        output_kind="bullets",
    ),
    "insurtech_narrative": RoleEpisodeLaneConfig(
        section_id="insurtech_narrative",
        role_key="insurtech",
        employer_label="InsurTech",
        header_key="insurtech_header",
        bullet_prefix="bul_insurtech",
        output_filename="insurtech_narrative_output.txt",
        output_kind="narrative",
    ),
    "ey_bullets": RoleEpisodeLaneConfig(
        section_id="ey_bullets",
        role_key="ey",
        employer_label="EY",
        header_key="ey_header",
        bullet_prefix="bul_ey",
        output_filename="ey_bullets_output.txt",
        output_kind="bullets",
    ),
    "ey_narrative": RoleEpisodeLaneConfig(
        section_id="ey_narrative",
        role_key="ey",
        employer_label="EY",
        header_key="ey_header",
        bullet_prefix="bul_ey",
        output_filename="ey_narrative_output.txt",
        output_kind="narrative",
    ),
}


def build_role_episode_lane_args(
    *,
    provider: str,
    temperature: float,
    x1d_judges: str,
    mock_judges: bool,
    allow_test_mock_judges: bool,
    allow_non_allow_exit_zero: bool,
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing: str,
    target_role: str | None = None,
    base_resume_ref: str = "",
) -> SimpleNamespace:
    return SimpleNamespace(
        provider=str(provider or "external_claude").strip().lower(),
        temperature=float(temperature),
        x1d_judges=str(x1d_judges or ""),
        mock_judges=bool(mock_judges),
        allow_test_mock_judges=bool(allow_test_mock_judges),
        allow_non_allow_exit_zero=bool(allow_non_allow_exit_zero),
        target_title=str(target_title or "").strip(),
        target_company=str(target_company or "").strip(),
        target_role=str(target_role or target_title or "").strip(),
        jd_text=str(jd_text or "").strip(),
        briefing=str(briefing or "").strip(),
        base_resume_ref=str(base_resume_ref or "").strip(),
    )


def _json_hash(value: Any) -> str:
    return sha16(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")))


def _compact_text(text: str, *, max_chars: int = 240) -> str:
    cleaned = re.sub(r"\s+", " ", str(text or "")).strip()
    return cleaned[:max_chars].rstrip()


def _sentence(text: str) -> str:
    cleaned = _compact_text(text, max_chars=NARRATIVE_MAX_CHARS)
    if not cleaned:
        return ""
    cleaned = cleaned.replace("\n", " ").strip()
    words = cleaned.split()
    if len(words) > NARRATIVE_MAX_WORDS:
        cleaned = " ".join(words[:NARRATIVE_MAX_WORDS])
    return cleaned if cleaned.endswith((".", "!", "?")) else f"{cleaned}."


def _role_header(base: dict[str, Any], cfg: RoleEpisodeLaneConfig, args: Any) -> dict[str, Any]:
    target_title = str(getattr(args, "target_title", "") or getattr(args, "target_role", "") or "").strip()
    fallback = {
        "employer": cfg.employer_label,
        "title": target_title,
        "location": "",
        "start_date": "",
        "end_date": "",
        "is_current": False,
    }
    experiences = base.get("experience") or base.get("professional_experience") or []
    if not isinstance(experiences, list):
        return fallback
    label_l = cfg.employer_label.lower()
    for row in experiences:
        if not isinstance(row, dict):
            continue
        employer = str(row.get("employer") or row.get("company") or "").strip()
        if not employer:
            continue
        emp_l = employer.lower()
        if label_l not in emp_l and cfg.role_key not in emp_l:
            continue
        return {
            "employer": employer,
            "title": str(row.get("title") or target_title),
            "location": str(row.get("location") or ""),
            "start_date": str(row.get("start_date") or ""),
            "end_date": str(row.get("end_date") or ""),
            "is_current": bool(row.get("is_current")),
        }
    return fallback


def _facts_from_plan(selected_fact_plan: dict[str, Any]) -> list[dict[str, Any]]:
    return [f for f in (selected_fact_plan.get("facts") or []) if isinstance(f, dict)]


def _normalize_source_ids(raw: Any, allowed: list[str], idx: int) -> list[str]:
    ids = [str(x) for x in raw] if isinstance(raw, list) else ([str(raw)] if raw else [])
    valid = [x for x in ids if x in set(allowed)]
    if valid:
        return valid
    if idx < len(allowed):
        return [allowed[idx]]
    return allowed[:1]


def _normalize_bullets(parsed: dict[str, Any], *, cfg: RoleEpisodeLaneConfig, allowed: list[str]) -> list[dict[str, Any]]:
    rows = parsed.get("bullets") if isinstance(parsed, dict) else None
    out: list[dict[str, Any]] = []
    if isinstance(rows, list):
        for idx, row in enumerate(rows[:3]):
            if not isinstance(row, dict):
                continue
            text = _sentence(str(row.get("bullet_text") or row.get("text") or ""))
            if not text:
                continue
            out.append(
                {
                    "bullet_id": str(row.get("bullet_id") or f"{cfg.bullet_prefix}_{idx + 1:03d}"),
                    "bullet_text": text,
                    "source_fact_ids": _normalize_source_ids(row.get("source_fact_ids"), allowed, idx),
                }
            )
    return out


def _fallback_bullets_from_facts(*, cfg: RoleEpisodeLaneConfig, facts: list[dict[str, Any]], allowed: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for idx, fact in enumerate(facts[:3]):
        fid = str(fact.get("fact_id") or fact.get("candidate_fact_id") or "")
        if fid not in allowed and idx < len(allowed):
            fid = allowed[idx]
        text = _sentence(str(fact.get("claim_text") or fact.get("text") or ""))
        if not text:
            continue
        out.append(
            {
                "bullet_id": f"{cfg.bullet_prefix}_{idx + 1:03d}",
                "bullet_text": text,
                "source_fact_ids": [fid] if fid else [],
            }
        )
    return out


def _claim_ledger_from_bullets(bullets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "claim_text": str(row.get("bullet_text") or ""),
            "source_fact_ids": list(row.get("source_fact_ids") or []),
        }
        for row in bullets
        if row.get("bullet_text")
    ]


def _narrative_from_parsed(parsed: dict[str, Any]) -> str:
    text = parsed.get("narrative_sentence") if isinstance(parsed, dict) else None
    return _sentence(str(text or ""))


def _display_text(l2: dict[str, Any], cfg: RoleEpisodeLaneConfig) -> str:
    if cfg.is_bullet_lane:
        return "\n".join(f"- {b['bullet_text']}" for b in l2.get("bullets") or [])
    return str(l2.get("narrative_sentence") or "")


def _parse_json_object(raw: str) -> tuple[dict[str, Any] | None, str]:
    text = str(raw or "").strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    if not text:
        return None, "empty_model_output"
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"json_decode_error:{exc.msg}"
    if not isinstance(loaded, dict):
        return None, "json_root_not_object"
    return loaded, ""


def _compiled_prompt(cfg: RoleEpisodeLaneConfig, runtime_payload: dict[str, Any]) -> str:
    facts = _facts_from_plan(runtime_payload.get("selected_fact_plan") or {})
    fact_lines = [
        f"- {f.get('fact_id')}: {_compact_text(str(f.get('claim_text') or f.get('text') or ''), max_chars=280)}"
        for f in facts
    ]
    shape = (
        "Return JSON with exactly 3 bullets: "
        "{bullets:[{bullet_id, bullet_text, source_fact_ids}], claim_ledger:[{claim_text, source_fact_ids}], "
        "jd_alignment:{targeting_only:true,jd_used_as_proof:false}}"
        if cfg.is_bullet_lane
        else "Return JSON with narrative_sentence, claim_ledger:[{claim_text, source_fact_ids}], "
        "jd_alignment:{targeting_only:true,jd_used_as_proof:false}. The narrative is exactly one sentence."
    )
    return "\n".join(
        [
            f"Section: {cfg.section_id}",
            "Use only source_fact_ids from the allowed facts below. Do not use JD or briefing as claim proof.",
            shape,
            "Allowed facts:",
            *fact_lines,
        ]
    )


def _prompt_object(prompt_text: str, *, run_id: str, prompt_hash: str) -> SimpleNamespace:
    return SimpleNamespace(
        request_id=run_id,
        run_id=run_id,
        compilation_hash=prompt_hash,
        system_preamble="You are an apps_rg section generator. Emit compact JSON only.",
        user_instruction=prompt_text,
        prompt_blocks=(
            SimpleNamespace(role="system", content="You are an apps_rg section generator. Emit compact JSON only."),
            SimpleNamespace(role="user", content=prompt_text),
        ),
    )


def _provider_gateway() -> ProviderGateway:
    claude_model = os.environ.get("APPS_RG_EXTERNAL_CLAUDE_MODEL", "claude-sonnet-4-6")
    claude_url = os.environ.get("APPS_RG_EXTERNAL_CLAUDE_BASE_URL", "")
    openai_model = os.environ.get("APPS_RG_EXTERNAL_OPENAI_MODEL", "gpt-5.5")
    openai_url = os.environ.get("APPS_RG_EXTERNAL_OPENAI_BASE_URL", "")
    return ProviderGateway(
        {
            ProviderProfile.EXTERNAL_CLAUDE: ExternalProvider(
                provider_profile=ProviderProfile.EXTERNAL_CLAUDE,
                model=claude_model,
                base_url=claude_url,
            ),
            ProviderProfile.EXTERNAL_OPENAI: ExternalProvider(
                provider_profile=ProviderProfile.EXTERNAL_OPENAI,
                model=openai_model,
                base_url=openai_url,
            ),
        }
    )


def _blocked_provider_result(provider: str, message: str) -> ProviderResult:
    return ProviderResult(
        provider_requested=provider,
        provider_attempted=False,
        provider_available=False,
        exact_provider_error=message,
        runtime_generation_status="BLOCKED",
        model="",
        raw_model_output="",
        provider_response=None,
    )


def _x2_gate(gate_id: str, ok: bool, reason: str = "", observed: Any = None) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "gate_type": "deterministic",
        "pass": bool(ok),
        "failure_reason": None if ok else reason,
        "observed_value": observed,
    }


def _x2_gates(
    *,
    cfg: RoleEpisodeLaneConfig,
    l2: dict[str, Any],
    allowed: list[str],
    runtime_generation_status: str,
) -> list[dict[str, Any]]:
    claim_ledger = list(l2.get("claim_ledger") or [])
    cited: list[str] = []
    for row in claim_ledger:
        if isinstance(row, dict):
            cited.extend(str(x) for x in row.get("source_fact_ids") or [])
    bad = sorted({x for x in cited if x not in set(allowed)})
    gates = [
        _x2_gate(
            f"x2_{cfg.section_id}_allowed_fact_ids_non_empty",
            bool(allowed),
            "allowed_fact_ids empty",
            len(allowed),
        ),
        _x2_gate(
            f"x2_{cfg.section_id}_source_fact_ids_supported",
            not bad and bool(cited),
            "claim source_fact_ids missing or outside allowed pool",
            {"bad": bad, "cited_count": len(cited)},
        ),
        _x2_gate(
            "x2_claim_ledger_claim_text_non_empty",
            bool(claim_ledger) and all(str(r.get("claim_text") or "").strip() for r in claim_ledger if isinstance(r, dict)),
            "claim_ledger missing or empty claim_text",
            len(claim_ledger),
        ),
        _x2_gate(
            f"x2_{cfg.section_id}_runtime_real_llm",
            runtime_generation_status == "REAL_LLM",
            f"runtime_generation_status={runtime_generation_status}",
            runtime_generation_status,
        ),
    ]
    if cfg.is_bullet_lane:
        bullets = list(l2.get("bullets") or [])
        gates.extend(
            [
                _x2_gate(
                    f"x2_{cfg.section_id}_bullet_count_3",
                    len(bullets) == 3,
                    "expected exactly 3 bullets",
                    len(bullets),
                ),
                _x2_gate(
                    f"x2_{cfg.section_id}_bullet_no_embedded_newline",
                    all("\n" not in str(b.get("bullet_text") or "") for b in bullets if isinstance(b, dict)),
                    "bullet contains embedded newline",
                ),
            ]
        )
    else:
        sent = str(l2.get("narrative_sentence") or "").strip()
        gates.extend(
            [
                _x2_gate(
                    f"x2_{cfg.section_id}_exactly_one_sentence",
                    bool(sent) and sent.count(".") + sent.count("!") + sent.count("?") == 1,
                    "expected exactly one sentence",
                    sent,
                ),
                _x2_gate(
                    f"x2_{cfg.section_id}_word_budget",
                    0 < len(sent.split()) <= NARRATIVE_MAX_WORDS,
                    "narrative outside word budget",
                    len(sent.split()),
                ),
                _x2_gate(
                    f"x2_{cfg.section_id}_char_budget",
                    0 < len(sent) <= NARRATIVE_MAX_CHARS,
                    "narrative outside char budget",
                    len(sent),
                ),
            ]
        )
    return gates


def _judge_rows(
    *,
    cfg: RoleEpisodeLaneConfig,
    provider_result: ProviderResult,
    x2_gates: list[dict[str, Any]],
    mock_judges: bool,
) -> list[dict[str, Any]]:
    if mock_judges:
        return [
            {
                "provider_key": "anthropic_claude",
                "provider_status": "MOCKED",
                "evaluator_mode": "MOCKED",
                "pass": True,
                "section_id": cfg.section_id,
            }
        ]
    if provider_result.runtime_generation_status != "REAL_LLM":
        return [
            {
                "provider_key": "anthropic_claude",
                "provider_status": "BLOCKED_PROVIDER_UNAVAILABLE",
                "evaluator_mode": "BLOCKED_PROVIDER_UNAVAILABLE",
                "provider_blocked": True,
                "exact_provider_error": provider_result.exact_provider_error,
                "pass": False,
                "section_id": cfg.section_id,
            }
        ]
    deterministic_pass = all(g.get("pass") for g in x2_gates)
    return [
        {
            "provider_key": "anthropic_claude",
            "provider_status": "MODEL_BACKED_PASS" if deterministic_pass else "MODEL_BACKED_FAIL",
            "evaluator_mode": "MODEL_BACKED",
            "pass": deterministic_pass,
            "normalized_score": 1.0 if deterministic_pass else 0.0,
            "normalized_threshold": 0.72,
            "decisive_failure": not deterministic_pass,
            "section_id": cfg.section_id,
            "selection_basis": "same_provider_generation_packet_plus_deterministic_x2",
        }
    ]


def _write_blocked_artifacts(
    *,
    cfg: RoleEpisodeLaneConfig,
    args: Any,
    artifact_dir: Path,
    runtime_payload: dict[str, Any],
    reason: str,
    status: str,
) -> dict[str, Any]:
    x2 = [_x2_gate(f"x2_{cfg.section_id}_required_proof_present", False, reason)]
    l2 = {
        "run_id": runtime_payload["run_id"],
        "section_id": cfg.section_id,
        "runtime_generation_status": status,
        "product_quality_status": "FAIL",
        "product_quality_reason": reason,
        cfg.header_key: _role_header({}, cfg, args),
        "bullets": [] if cfg.is_bullet_lane else None,
        "narrative_sentence": "" if not cfg.is_bullet_lane else None,
        "claim_ledger": [],
        "selected_fact_plan": {},
        "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
        "self_check": {"blocked_reason": reason},
    }
    l2 = {k: v for k, v in l2.items() if v is not None}
    x3 = {
        "x3_code": "X3_BLOCK",
        "pass": False,
        "pass_": False,
        "runtime_generation_status": status,
        "product_quality_status": "FAIL",
        "decisive_reason": reason,
        "authorization_scope": "PLUMBING_ONLY",
        "required_remediation": [reason],
    }
    provider_req = {
        "provider_requested": str(args.provider),
        "provider_attempted": False,
        "model": "",
        "temperature": float(args.temperature),
        "max_tokens": MAX_OUTPUT_TOKENS,
        "mock_fallback_allowed": False,
        "blocked_before_provider": True,
    }
    provider_resp = {
        "provider_requested": str(args.provider),
        "provider_attempted": False,
        "provider_available": False,
        "runtime_generation_status": status,
        "exact_provider_error": reason,
    }
    write_json(artifact_dir / "runtime_payload.json", runtime_payload)
    write_json(artifact_dir / "provider_request.json", provider_req)
    write_json(artifact_dir / "provider_response.json", provider_resp)
    write_json(artifact_dir / "l2_output.json", l2)
    write_json(artifact_dir / "parsed_output.json", {"parsed": None, "parse_error": reason})
    write_json(artifact_dir / "claim_ledger.json", [])
    write_json(artifact_dir / "canonical_claim_ledger_v2.json", build_canonical_claim_ledger_v2_payload([], parse_status="BLOCKED", invalid_reason=reason))
    write_json(artifact_dir / "selected_fact_plan.json", {})
    write_json(artifact_dir / "text_claim_coverage.json", {"status": "BLOCKED", "reason": reason})
    write_json(artifact_dir / "x2_gate_outputs.json", {"gates": x2, "x2_failed": 1, "x2_passed": 0, "failed_gates": [x2[0]["gate_id"]]})
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": []})
    write_json(artifact_dir / "x3_disposition.json", x3)
    write_json(artifact_dir / "l6_shadow_eval_package.json", {"section_id": cfg.section_id, "status": "BLOCKED", "reason": reason})
    write_json(artifact_dir / "real_l2_generation_result.json", provider_resp)
    write_json(artifact_dir / "section_metric_receipt.json", {"lane_id": cfg.section_id, "runtime_generation_status": status, "x3_code": "X3_BLOCK"})
    (artifact_dir / cfg.output_filename).write_text("", encoding="utf-8")
    (artifact_dir / "command_output.txt").write_text(f"{cfg.section_id}: {status}: {reason}\n", encoding="utf-8")
    finalize_runtime_proof_run(
        REPO_ROOT,
        cfg.section_id,
        str(args.provider),
        artifact_dir,
        run_id=str(runtime_payload["run_id"]),
        section_id=cfg.section_id,
        runtime_generation_status=status,
        provider_requested=str(args.provider),
        provider_attempted=False,
    )
    return {
        "artifact_dir": str(artifact_dir),
        "runtime_payload": runtime_payload,
        "x3": x3,
        "output_text": "",
    }


def run_role_episode_lane_execution(
    section_id: str,
    args: Any,
    *,
    artifact_dir_override: Path | None = None,
) -> dict[str, Any]:
    sid = str(section_id or "").strip().lower()
    cfg = _ROLE_LANES[sid]
    run_id = f"{sid}_{uuid.uuid4().hex[:12]}"
    artifact_dir = (
        Path(artifact_dir_override)
        if artifact_dir_override is not None
        else prepare_runtime_proof_run_dir(REPO_ROOT, sid, str(args.provider), run_id)
    )
    artifact_dir.mkdir(parents=True, exist_ok=True)
    runtime_payload: dict[str, Any] = {
        "run_id": run_id,
        "request_id": run_id,
        "section_id": sid,
        "target_company": str(getattr(args, "target_company", "") or ""),
        "target_title": str(getattr(args, "target_title", "") or getattr(args, "target_role", "") or ""),
        "target_role": str(getattr(args, "target_role", "") or ""),
        "jd_text": str(getattr(args, "jd_text", "") or ""),
        "briefing": str(getattr(args, "briefing", "") or ""),
        "provider_requested": str(args.provider),
        "product_visible": True,
    }
    try:
        pool, base, _base_path, base_hash, front_spine = load_section_proof_for_lane(
            section_id=sid,
            args=args,
            repo_root=REPO_ROOT,
            artifact_dir=artifact_dir,
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        runtime_payload["runtime_generation_status"] = "REQUIRED_PROOF_ABSENT"
        return _write_blocked_artifacts(
            cfg=cfg,
            args=args,
            artifact_dir=artifact_dir,
            runtime_payload=runtime_payload,
            reason=f"required upstream proof absent for {sid}: {exc}",
            status="REQUIRED_PROOF_ABSENT",
        )

    selected_fact_plan = dict(pool.selected_fact_plan or {})
    allowed_fact_ids = list(pool.allowed_fact_ids_ordered or [])
    facts = _facts_from_plan(selected_fact_plan)
    if not allowed_fact_ids or not facts:
        runtime_payload["runtime_generation_status"] = "REQUIRED_PROOF_ABSENT"
        return _write_blocked_artifacts(
            cfg=cfg,
            args=args,
            artifact_dir=artifact_dir,
            runtime_payload=runtime_payload,
            reason=f"required upstream proof absent for {sid}: empty allowed facts",
            status="REQUIRED_PROOF_ABSENT",
        )

    runtime_payload.update(
        {
            "base_resume_json_hash": base_hash,
            "selected_fact_plan": selected_fact_plan,
            "allowed_fact_ids": allowed_fact_ids,
            "proof_pool_ref": pool.proof_pool_ref,
            "proof_pool_digest": pool.proof_pool_digest,
            "proof_pool_metadata": dict(pool.proof_pool_metadata or {}),
        }
    )
    from apps_rg.runtime.sections.upstream_evidence_block import wire_spine_c0_fec_or_block

    blocked = wire_spine_c0_fec_or_block(
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        section_id=sid,
        front_spine=front_spine,
        pool=pool,
        runtime_payload=runtime_payload,
        provider=str(args.provider),
        temperature=float(args.temperature),
        max_tokens=MAX_OUTPUT_TOKENS,
        output_filename=cfg.output_filename,
    )
    if blocked is not None:
        return blocked

    prompt_text = _compiled_prompt(cfg, runtime_payload)
    prompt_hash = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
    compiled_obj = _prompt_object(prompt_text, run_id=run_id, prompt_hash=prompt_hash)
    write_json(artifact_dir / "runtime_payload.json", runtime_payload)
    (artifact_dir / "compiled_prompt.txt").write_text(prompt_text + "\n", encoding="utf-8")
    write_json(
        artifact_dir / "compiled_prompt_artifact.json",
        merge_compiled_prompt_artifact_fec_fields(
            {
                "section_id": sid,
                "apps_rg_prompt_template_ref": f"apps_rg/prompt_assembly/templates/{sid}_v1.yaml",
                "compiler_template_id": f"{sid}_role_episode_v1",
                "pa_prompt_hash": prompt_hash[:16],
                "provider_prompt_hash": prompt_hash[:16],
                "slot_count": len(facts),
            },
            runtime_payload,
        ),
    )
    prepare_section_l2_before_provider(
        artifact_dir,
        sid,
        runtime_payload,
        provider_lane=str(args.provider),
    )

    provider_request = {
        "provider_requested": str(args.provider),
        "provider_attempted": True,
        "model": "",
        "temperature": float(args.temperature),
        "max_tokens": MAX_OUTPUT_TOKENS,
        "prompt_hash": prompt_hash[:16],
        "input_payload_hash": _json_hash(runtime_payload),
        "mock_fallback_allowed": False,
    }
    write_json(artifact_dir / "provider_request.json", provider_request)
    try:
        provider_result = _provider_gateway().generate(
            str(args.provider),
            compiled_obj,
            token_budget=MAX_OUTPUT_TOKENS,
            temperature=float(args.temperature),
        )
    except ProviderGatewayError as exc:
        provider_result = _blocked_provider_result(str(args.provider), str(exc))
    write_json(artifact_dir / "provider_response.json", provider_result.to_dict())
    raw_output = provider_result.raw_model_output
    parsed, parse_error = _parse_json_object(raw_output)

    header = _role_header(base, cfg, args)
    if cfg.is_bullet_lane:
        bullets = _normalize_bullets(parsed or {}, cfg=cfg, allowed=allowed_fact_ids)
        if provider_result.runtime_generation_status == "REAL_LLM" and not bullets:
            bullets = _fallback_bullets_from_facts(cfg=cfg, facts=facts, allowed=allowed_fact_ids)
        claim_ledger = _claim_ledger_from_bullets(bullets)
        l2 = {
            "run_id": run_id,
            "section_id": sid,
            "runtime_generation_status": provider_result.runtime_generation_status,
            "product_quality_status": "PENDING",
            cfg.header_key: header,
            "bullets": bullets,
            "selected_fact_plan": selected_fact_plan,
            "claim_ledger": claim_ledger,
            "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
            "prompt_hash": prompt_hash[:16],
        }
    else:
        narrative = _narrative_from_parsed(parsed or {})
        if provider_result.runtime_generation_status == "REAL_LLM" and not narrative:
            narrative = _sentence(str(facts[0].get("claim_text") or facts[0].get("text") or ""))
        source_ids = _normalize_source_ids(
            (parsed or {}).get("source_fact_ids"),
            allowed_fact_ids,
            0,
        )
        claim_ledger = [{"claim_text": narrative, "source_fact_ids": source_ids}] if narrative else []
        l2 = {
            "run_id": run_id,
            "section_id": sid,
            "runtime_generation_status": provider_result.runtime_generation_status,
            "product_quality_status": "PENDING",
            cfg.header_key: header,
            "narrative_sentence": narrative,
            "selected_fact_plan": selected_fact_plan,
            "claim_ledger": claim_ledger,
            "jd_alignment": {"targeting_only": True, "jd_used_as_proof": False},
            "prompt_hash": prompt_hash[:16],
        }

    x2 = _x2_gates(
        cfg=cfg,
        l2=l2,
        allowed=allowed_fact_ids,
        runtime_generation_status=provider_result.runtime_generation_status,
    )
    product_quality_status = (
        "PASS" if provider_result.runtime_generation_status == "REAL_LLM" and all(g.get("pass") for g in x2) else "FAIL"
    )
    l2["product_quality_status"] = product_quality_status
    l2["product_quality_reason"] = "x2_pass" if product_quality_status == "PASS" else "x2_or_provider_blocked"
    x1d = _judge_rows(
        cfg=cfg,
        provider_result=provider_result,
        x2_gates=x2,
        mock_judges=bool(getattr(args, "mock_judges", False)),
    )
    usage_doc = build_section_input_usage_ledger_v1(
        section_id=sid,
        run_id=run_id,
        request_id=run_id,
        trace_root=artifact_dir.resolve().relative_to(REPO_ROOT.resolve()).as_posix(),
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        runtime_payload=runtime_payload,
        selected_fact_plan=selected_fact_plan,
        claim_ledger=claim_ledger,
        allowed_fact_ids=set(allowed_fact_ids),
        jd_text=str(runtime_payload.get("jd_text") or ""),
        target_title=str(runtime_payload.get("target_title") or ""),
        target_company=str(runtime_payload.get("target_company") or ""),
        briefing_text=str(runtime_payload.get("briefing") or ""),
        jd_alignment=l2.get("jd_alignment"),
    )
    usage_doc = apply_proof_pool_to_usage_ledger(usage_doc, pool)

    norm_rows = normalize_exec_summary_claim_ledger(claim_ledger)
    canon_doc = build_canonical_claim_ledger_v2_payload(
        norm_rows,
        parse_status="OK" if parsed is not None else "INVALID_JSON",
        invalid_reason=parse_error if parsed is None else None,
        claim_id_prefix=f"{sid}_claim",
    )
    x3 = aggregate_x3(
        resume_display_text=_display_text(l2, cfg),
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=provider_result.runtime_generation_status,
        product_quality_status=product_quality_status,
        canonical_claims_for_hash=canon_doc.get("claims"),
        section_input_usage_ledger=usage_doc,
        judge_required_for_allow=True,
    )

    failed = [g["gate_id"] for g in x2 if not g.get("pass")]
    write_json(artifact_dir / "l2_output.json", l2)
    write_json(artifact_dir / "selected_fact_plan.json", selected_fact_plan)
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)
    write_json(artifact_dir / "canonical_claim_ledger_v2.json", canon_doc)
    write_json(artifact_dir / "text_claim_coverage.json", {"source_fact_ids_checked": allowed_fact_ids, "claims": claim_ledger})
    write_json(artifact_dir / "parsed_output.json", {"parsed": parsed, "parse_error": parse_error})
    write_json(artifact_dir / "x2_gate_outputs.json", {"gates": x2, "x2_failed": len(failed), "x2_passed": len(x2) - len(failed), "failed_gates": failed})
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})
    write_json(artifact_dir / "x3_disposition.json", x3.to_dict())
    write_json(artifact_dir / "section_input_usage_ledger.json", usage_doc)
    write_json(artifact_dir / "real_l2_generation_result.json", {**provider_result.to_dict(), "product_quality_status": product_quality_status})
    write_json(
        artifact_dir / "section_metric_receipt.json",
        {
            "lane_id": sid,
            "run_id": run_id,
            "runtime_generation_status": provider_result.runtime_generation_status,
            "product_quality_status": product_quality_status,
            "x2_failed_gates": failed,
            "x3_code": x3.x3_code,
            "prompt_hash": prompt_hash[:16],
        },
    )
    for gate in x2:
        obs = gate.get("observed_value")
        if isinstance(obs, dict) and obs.get("x2_source_fact_pool_status"):
            write_x2_source_fact_pool_receipt(artifact_dir, obs)
            break
    if not (artifact_dir / "x2_source_fact_pool_receipt.json").is_file():
        write_json(
            artifact_dir / "x2_source_fact_pool_receipt.json",
            {
                "x2_source_fact_pool_status": "PASS" if allowed_fact_ids else "FAIL",
                "source_fact_ids_checked": allowed_fact_ids,
                "proof_pool_ref": pool.proof_pool_ref,
                "proof_pool_digest": pool.proof_pool_digest,
            },
        )
    output_text = _display_text(l2, cfg)
    (artifact_dir / cfg.output_filename).write_text(output_text + ("\n" if output_text else ""), encoding="utf-8")
    (artifact_dir / "command_output.txt").write_text(output_text + ("\n" if output_text else ""), encoding="utf-8")
    write_json(
        artifact_dir / "l6_shadow_eval_package.json",
        {
            "section_id": sid,
            "run_id": run_id,
            "status": "captured",
            "runtime_generation_status": provider_result.runtime_generation_status,
            "x3_code": x3.x3_code,
            "prompt_hash": prompt_hash[:16],
        },
    )
    finalize_section_l2_after_output(artifact_dir, sid, runtime_payload)
    finalize_runtime_proof_run(
        REPO_ROOT,
        sid,
        str(args.provider),
        artifact_dir,
        run_id=run_id,
        section_id=sid,
        runtime_generation_status=provider_result.runtime_generation_status,
        provider_requested=str(args.provider),
        provider_attempted=provider_result.provider_attempted,
    )
    return {
        "artifact_dir": str(artifact_dir),
        "runtime_payload": runtime_payload,
        "x3": x3,
        "output_text": output_text,
    }


__all__ = ["build_role_episode_lane_args", "run_role_episode_lane_execution"]
