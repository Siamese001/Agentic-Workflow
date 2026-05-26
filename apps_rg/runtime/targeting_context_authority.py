"""Frozen material targeting authority — generation/judge parity SSOT (apps_rg)."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from typing import Any


class TargetingAuthorityError(RuntimeError):
    """Raised when downstream code reads raw CLI targeting instead of frozen bundle."""


@dataclass(frozen=True)
class MaterialTargetingBundle:
    authority_source_refs: dict[str, str]
    jd_text_frozen: str
    briefing_text_frozen: str
    target_title: str
    target_company: str
    bundle_digest: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> MaterialTargetingBundle:
        return cls(
            authority_source_refs=dict(raw.get("authority_source_refs") or {}),
            jd_text_frozen=str(raw.get("jd_text_frozen") or ""),
            briefing_text_frozen=str(raw.get("briefing_text_frozen") or ""),
            target_title=str(raw.get("target_title") or ""),
            target_company=str(raw.get("target_company") or ""),
            bundle_digest=str(raw.get("bundle_digest") or ""),
        )


@dataclass(frozen=True)
class GenerationMaterialContext:
    jd_text_material: str
    briefing_text_material: str
    generation_material_digest: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class JudgeMaterialContext:
    jd_text_material: str
    briefing_text_material: str
    judge_material_digest: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def sha256_hex64(body: str) -> str:
    return hashlib.sha256(str(body or "").encode("utf-8")).hexdigest()


def material_targeting_digest(jd_text: str, briefing_text: str) -> str:
    return sha256_hex64(f"{jd_text}\n---\n{briefing_text}")


_JD_FIELD_RE = re.compile(
    r"JD_TEXT \(targeting only[^:\n]+:\s*(.+?)(?=\nBRIEFING \(targeting only)",
    re.DOTALL,
)
_BRIEFING_FIELD_RE = re.compile(
    r"BRIEFING \(targeting only[^:\n]+:\s*(.+?)(?=\n(?:jd_alignment:|Use JD_TEXT|Use TARGET_|TARGET_TITLE|\[# APPS_RG))",
    re.DOTALL,
)


def _compiled_prompt_message_text(content: str) -> str:
    """Normalize compiled prompt JSON or plain text to searchable message body."""
    raw = str(content or "")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if isinstance(parsed, list):
        chunks: list[str] = []
        for msg in parsed:
            if isinstance(msg, dict) and msg.get("content") is not None:
                chunks.append(str(msg["content"]))
        if chunks:
            return "\n".join(chunks)
    if isinstance(parsed, dict) and parsed.get("content") is not None:
        return str(parsed["content"])
    return raw


def extract_material_targeting_from_compiled_prompt(content: str) -> tuple[str, str]:
    """Return (jd_text, briefing_text) embedded in provider-bound compiled prompt."""
    text = _compiled_prompt_message_text(content)
    from apps_rg.runtime.sections.executive_summary_targeting_cap import (
        extract_frozen_targeting_from_compiled_content,
    )

    jd, br = extract_frozen_targeting_from_compiled_content(text)
    if jd or br:
        return jd, br
    jd = ""
    br = ""
    m_jd = _JD_FIELD_RE.search(text)
    if m_jd:
        jd = m_jd.group(1).strip()
    m_br = _BRIEFING_FIELD_RE.search(text)
    if m_br:
        br = m_br.group(1).strip()
    return jd, br


def generation_material_context_from_bundle(bundle: MaterialTargetingBundle) -> GenerationMaterialContext:
    """SSOT for L2 vs X1D parity — same frozen bundle Qwen PA and judges must use."""
    jd = bundle.jd_text_frozen
    br = bundle.briefing_text_frozen
    return GenerationMaterialContext(
        jd_text_material=jd,
        briefing_text_material=br,
        generation_material_digest=material_targeting_digest(jd, br),
    )


def generation_material_context_from_compiled_prompt(content: str) -> GenerationMaterialContext:
    jd, br = extract_material_targeting_from_compiled_prompt(content)
    return GenerationMaterialContext(
        jd_text_material=jd,
        briefing_text_material=br,
        generation_material_digest=material_targeting_digest(jd, br),
    )


def judge_material_context_from_packet(packet: dict[str, Any]) -> JudgeMaterialContext:
    tc = packet.get("targeting_context") if isinstance(packet.get("targeting_context"), dict) else {}
    jd = str(tc.get("jd_text") or "")
    br = str(tc.get("briefing") or "")
    return JudgeMaterialContext(
        jd_text_material=jd,
        briefing_text_material=br,
        judge_material_digest=material_targeting_digest(jd, br),
    )


def graph_targeting_capsule_from_packet(packet: dict[str, Any]) -> dict[str, Any] | None:
    tc = packet.get("targeting_context") if isinstance(packet.get("targeting_context"), dict) else {}
    capsule = tc.get("graph_targeting_capsule")
    return dict(capsule) if isinstance(capsule, dict) else None


def build_targeting_binding_digest(
    *,
    target_title: str,
    target_company: str,
    jd_text: str,
    briefing_text: str,
    graph_targeting_capsule: dict[str, Any] | None = None,
) -> str:
    """Canonical generation/judge targeting binding (material + graph capsule + role anchors)."""
    from apps_rg.runtime.c0.exec_summary_graph_targeting_capsule import (
        canonical_graph_targeting_capsule_digest,
    )

    body = json.dumps(
        {
            "target_title": str(target_title or "").strip(),
            "target_company": str(target_company or "").strip(),
            "material_digest": material_targeting_digest(jd_text, briefing_text),
            "graph_targeting_capsule_digest": canonical_graph_targeting_capsule_digest(
                graph_targeting_capsule,
            ),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256_hex64(body)


def evaluate_targeting_parity(
    *,
    generation: GenerationMaterialContext,
    judge: JudgeMaterialContext,
    bundle: MaterialTargetingBundle | None = None,
    graph_targeting_capsule_generation: dict[str, Any] | None = None,
    graph_targeting_capsule_judge: dict[str, Any] | None = None,
) -> dict[str, Any]:
    material_match = generation.generation_material_digest == judge.judge_material_digest
    title = str(bundle.target_title if bundle else "")
    company = str(bundle.target_company if bundle else "")
    generation_targeting_digest = build_targeting_binding_digest(
        target_title=title,
        target_company=company,
        jd_text=generation.jd_text_material,
        briefing_text=generation.briefing_text_material,
        graph_targeting_capsule=graph_targeting_capsule_generation,
    )
    judge_targeting_digest = build_targeting_binding_digest(
        target_title=title,
        target_company=company,
        jd_text=judge.jd_text_material,
        briefing_text=judge.briefing_text_material,
        graph_targeting_capsule=graph_targeting_capsule_judge,
    )
    binding_match = generation_targeting_digest == judge_targeting_digest
    parity_match = material_match and binding_match
    bundle_matches_generation: bool | None = None
    if bundle is not None:
        bundle_matches_generation = (
            material_targeting_digest(bundle.jd_text_frozen, bundle.briefing_text_frozen)
            == generation.generation_material_digest
        )
        if bundle_matches_generation is False:
            parity_match = False
    return {
        "schema": "targeting_context_parity_v2",
        "targeting_bundle_digest": bundle.bundle_digest if bundle else None,
        "generation_material_digest": generation.generation_material_digest,
        "judge_material_digest": judge.judge_material_digest,
        "generation_targeting_digest": generation_targeting_digest,
        "judge_targeting_digest": judge_targeting_digest,
        "targeting_parity_status": "match" if parity_match else "mismatch",
        "targeting_binding_match": binding_match,
        "target_title": title,
        "target_company": company,
        "parity_match": parity_match,
        "bundle_matches_generation_material": bundle_matches_generation,
        "generation_jd_chars": len(generation.jd_text_material),
        "generation_briefing_chars": len(generation.briefing_text_material),
        "judge_jd_chars": len(judge.jd_text_material),
        "judge_briefing_chars": len(judge.briefing_text_material),
        "substantive_jd_fit_certification_allowed": parity_match,
    }


def merge_targeting_parity_into_usage_ledger(
    doc: dict[str, Any],
    parity_receipt: dict[str, Any],
) -> dict[str, Any]:
    """Merge parity truth into ledger; briefing_hash reflects L2 material digest only."""
    out = dict(doc)
    gen_d = str(parity_receipt.get("generation_material_digest") or "")
    judge_d = str(parity_receipt.get("judge_material_digest") or "")
    bundle_d = str(parity_receipt.get("targeting_bundle_digest") or "")
    match = parity_receipt.get("parity_match") is True
    out["targeting_context_parity"] = dict(parity_receipt)
    out["targeting_bundle_digest"] = bundle_d
    out["generation_material_digest"] = gen_d
    out["judge_material_digest"] = judge_d
    out["generation_targeting_digest"] = str(parity_receipt.get("generation_targeting_digest") or "")
    out["judge_targeting_digest"] = str(parity_receipt.get("judge_targeting_digest") or "")
    out["targeting_parity_status"] = str(parity_receipt.get("targeting_parity_status") or "")
    out["parity_match"] = match
    refs = dict(out.get("input_refs") or {})
    refs["targeting_bundle_digest"] = bundle_d
    refs["generation_material_digest"] = gen_d
    refs["judge_material_digest"] = judge_d
    refs["briefing_hash"] = gen_d
    refs["briefing_material_authority"] = "compiled_prompt_jd_requirements"
    refs["parity_match"] = match
    out["input_refs"] = refs
    riu = dict(out.get("required_input_usage") or {})
    br_row = dict(riu.get("briefing_research") or {})
    br_row["used"] = bool(gen_d) and int(parity_receipt.get("generation_briefing_chars") or 0) > 0
    br_row["material_delivered_to_l2"] = bool(gen_d)
    br_row["parity_match_generation_judge"] = match
    riu["briefing_research"] = br_row
    out["required_input_usage"] = riu
    return out


def require_material_targeting_bundle(runtime_payload: dict[str, Any]) -> MaterialTargetingBundle:
    raw = runtime_payload.get("material_targeting_bundle")
    if not isinstance(raw, dict) or not raw.get("bundle_digest"):
        raise TargetingAuthorityError(
            "material_targeting_bundle missing — downstream must not read args.briefing or args.jd_text"
        )
    return MaterialTargetingBundle.from_dict(raw)


def store_material_targeting_bundle(
    runtime_payload: dict[str, Any],
    bundle: MaterialTargetingBundle,
) -> None:
    runtime_payload["material_targeting_bundle"] = bundle.to_dict()
    runtime_payload["jd_text"] = bundle.jd_text_frozen
    runtime_payload["briefing"] = bundle.briefing_text_frozen
    runtime_payload["targeting_context_frozen"] = True


def frozen_jd_text(runtime_payload: dict[str, Any]) -> str:
    return require_material_targeting_bundle(runtime_payload).jd_text_frozen


def frozen_briefing_text(runtime_payload: dict[str, Any]) -> str:
    return require_material_targeting_bundle(runtime_payload).briefing_text_frozen


__all__ = [
    "GenerationMaterialContext",
    "JudgeMaterialContext",
    "MaterialTargetingBundle",
    "TargetingAuthorityError",
    "build_targeting_binding_digest",
    "evaluate_targeting_parity",
    "graph_targeting_capsule_from_packet",
    "generation_material_context_from_bundle",
    "extract_material_targeting_from_compiled_prompt",
    "frozen_briefing_text",
    "frozen_jd_text",
    "generation_material_context_from_compiled_prompt",
    "judge_material_context_from_packet",
    "material_targeting_digest",
    "require_material_targeting_bundle",
    "sha256_hex64",
    "store_material_targeting_bundle",
    "merge_targeting_parity_into_usage_ledger",
]
