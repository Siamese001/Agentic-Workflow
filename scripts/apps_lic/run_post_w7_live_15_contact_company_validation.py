"""Secondary live company-soak validation for apps_lic.

This runner uses public LinkedIn-indexed/current web search pulls collected on
2026-06-08: 5 contacts each for AIG, Citi, and Neo4j. It does not scrape behind
login, send messages, or call LinkedIn APIs. When ANTHROPIC_API_KEY is loaded
from .env, required X1D judges run through live Claude.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from apps_lic.engines.governed_opportunity_ingestion import (  # noqa: E402
    NAMESPACE_COMPANY,
    NAMESPACE_COMPANY_TRIGGER,
    NAMESPACE_CONTACT,
    NAMESPACE_JD,
    NAMESPACE_ROLE_OWNERSHIP,
)
from apps_lic.engines.message_type_requirement_gate import (  # noqa: E402
    MESSAGE_GENERAL_INTRO,
    MESSAGE_ROLE_SPECIFIC,
    MESSAGE_TRIGGER_BASED_INSIGHT,
)
from apps_lic.runtime.dispatch import stage_receipts as sr  # noqa: E402
from apps_lic.runtime.dispatch.canonical_dispatch import (  # noqa: E402
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)


RUN_ID = "post_w7_live_15_contact_aig_citi_neo4j_20260608"
FIXED_FRESHNESS_DATE = "2026-06-08T00:00:00+00:00"
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT / "artifacts" / "apps_lic" / "post_w7_live_15_contact_company_validation"
)
SECONDARY_E2E_GATE_ROLE = "secondary_live_company_soak"
SECONDARY_E2E_GATE_SHAPE = "5_per_company_15_company_validation"
DEFAULT_ENV_FILE_CANDIDATES = (
    REPO_ROOT / ".env",
    REPO_ROOT.parent / "Agentic-Workflow-FRESH" / ".env",
)
LIVE_PROVIDER_ENV_KEYS = (
    "APPS_LIC_TEST_PROVIDER_STUB",
    "APPS_LIC_REQUIRE_QWEN_VLLM",
    "APPS_LIC_RUN_LIVE_CLAUDE_X1D",
)


@dataclass(frozen=True)
class CompanyConfig:
    key: str
    name: str
    jd_path: Path
    briefing_path: Path
    jd_title: str
    requisition_number: str
    company_context: str
    trigger_text: str


@dataclass(frozen=True)
class LiveContact:
    company_key: str
    profile_id: str
    name: str
    title: str
    expected_class: str
    message_type_hint: str
    role_ownership_text: str
    source_url: str
    source_label: str
    source_evidence: str


COMPANIES: dict[str, CompanyConfig] = {
    "aig": CompanyConfig(
        key="aig",
        name="AIG",
        jd_path=REPO_ROOT
        / "apps_rg"
        / "config"
        / "targeting"
        / "aig_vp_global_head_agentic_ai_jd.txt",
        briefing_path=REPO_ROOT
        / "apps_rg"
        / "config"
        / "targeting"
        / "aig_vp_global_head_agentic_ai_briefing.md",
        jd_title="VP, Global Head of Agentic AI Solutions",
        requisition_number="JR2601998",
        company_context=(
            "AIG enterprise AI operating context for regulated insurance, "
            "claims, underwriting, governance, and GenAI standards."
        ),
        trigger_text=(
            "AIG's VP Global Head of Agentic AI Solutions role reports into the "
            "Global Chief Data Officer and spans agentic AI operating-model work."
        ),
    ),
    "citi": CompanyConfig(
        key="citi",
        name="Citi",
        jd_path=REPO_ROOT
        / "apps_rg"
        / "config"
        / "targeting"
        / "citi_head_of_ai_strategy_jd.txt",
        briefing_path=REPO_ROOT
        / "apps_rg"
        / "config"
        / "targeting"
        / "citi_head_of_ai_strategy_briefing.md",
        jd_title="Head of AI Strategy - Firmwide AI",
        requisition_number="CITI-AI-STRATEGY-2026",
        company_context=(
            "Citi firmwide AI strategy context across regulated finance, risk "
            "controls, responsible AI, data governance, and platform execution."
        ),
        trigger_text=(
            "Citi is expanding firmwide AI strategy under senior AI leadership, "
            "with responsible AI, Citi Sky, and global AI adoption signals."
        ),
    ),
    "neo4j": CompanyConfig(
        key="neo4j",
        name="Neo4j",
        jd_path=REPO_ROOT
        / "apps_rg"
        / "config"
        / "targeting"
        / "neo4j_vp_product_management_agentic_ai_jd.txt",
        briefing_path=REPO_ROOT
        / "apps_rg"
        / "config"
        / "targeting"
        / "neo4j_vp_product_management_agentic_ai_briefing.md",
        jd_title="VP of Product Management, Agentic AI",
        requisition_number="NEO4J-AI-PM-2026",
        company_context=(
            "Neo4j graph intelligence, product strategy, knowledge graph, RAG, "
            "and agentic AI platform context."
        ),
        trigger_text=(
            "Neo4j is hiring for Agentic AI product leadership and positioning "
            "graph intelligence as context infrastructure for enterprise agents."
        ),
    ),
}


LIVE_CONTACTS: tuple[LiveContact, ...] = (
    LiveContact(
        company_key="aig",
        profile_id="aig_nina_k",
        name="Nina K.",
        title="Strategic Technical Recruiter and Sourcer",
        expected_class="RECRUITER",
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        role_ownership_text="Technical recruiter and sourcer specializing in AI and emerging technology searches at AIG.",
        source_url="https://www.linkedin.com/in/nkshatri",
        source_label="LinkedIn public profile result",
        source_evidence="Profile result says Nina K. is at AIG and specializes in hiring AI researchers and machine roles.",
    ),
    LiveContact(
        company_key="aig",
        profile_id="aig_regina_gilligan",
        name="Regina Gilligan",
        title="Talent Acquisition Manager",
        expected_class="SENIOR_TA",
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        role_ownership_text="Talent Acquisition Manager at AIG with active AIG hiring activity.",
        source_url="https://www.linkedin.com/in/regina-gilligan-8644639",
        source_label="LinkedIn public profile result",
        source_evidence="Profile result says Regina Gilligan is an experienced Talent Acquisition Manager at AIG.",
    ),
    LiveContact(
        company_key="aig",
        profile_id="aig_kristie_cooper",
        name="Kristie Cooper",
        title="Talent Acquisition Manager",
        expected_class="SENIOR_TA",
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        role_ownership_text="Talent Acquisition Manager at AIG responsible for shaping future talent pipelines.",
        source_url="https://uk.linkedin.com/in/kristiesmith86",
        source_label="LinkedIn public profile result",
        source_evidence="Profile result says Kristie Cooper is a Talent Acquisition Manager at AIG.",
    ),
    LiveContact(
        company_key="aig",
        profile_id="aig_tamara_thaxton",
        name="Tamara Thaxton",
        title="Talent Acquisition Leader",
        expected_class="SENIOR_TA",
        message_type_hint=MESSAGE_GENERAL_INTRO,
        role_ownership_text="Talent Acquisition Leader at AIG with AIG early-career and hiring activity.",
        source_url="https://www.linkedin.com/in/tamara-thaxton",
        source_label="LinkedIn public profile result",
        source_evidence="Profile result says Tamara Thaxton is a collaborative Talent Acquisition Leader at AIG.",
    ),
    LiveContact(
        company_key="aig",
        profile_id="aig_jim_young",
        name="Jim Young",
        title="Global Chief Data Officer",
        expected_class="C_LEVEL",
        message_type_hint=MESSAGE_TRIGGER_BASED_INSIGHT,
        role_ownership_text="Global Chief Data Officer tied to AIG agentic AI strategy and platform context.",
        source_url="https://www.linkedin.com/posts/cdo-magazine_jim-young-aig-global-chief-data-officer-activity-7097271787876450304-3St1",
        source_label="LinkedIn public post result",
        source_evidence="LinkedIn-indexed CDO Magazine post identifies Jim Young as AIG Global Chief Data Officer.",
    ),
    LiveContact(
        company_key="citi",
        profile_id="citi_dee_morgan",
        name="Dee Morgan",
        title="Talent Acquisition Strategist",
        expected_class="RECRUITER",
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        role_ownership_text="Talent Acquisition Strategist at Citi sharing AI audit and AI governance hiring activity.",
        source_url="https://www.linkedin.com/in/deemorgan-talentacquisition",
        source_label="LinkedIn public profile result",
        source_evidence="Profile result says Dee Morgan is a Citi Talent Acquisition Strategist posting AI audit hiring.",
    ),
    LiveContact(
        company_key="citi",
        profile_id="citi_shobhit_varshney",
        name="Shobhit Varshney",
        title="Head of AI",
        expected_class="EXECUTIVE",
        message_type_hint=MESSAGE_TRIGGER_BASED_INSIGHT,
        role_ownership_text="Citi Head of AI discussing responsible and effective frontier AI integration.",
        source_url="https://www.linkedin.com/in/shobhitvarshney",
        source_label="LinkedIn public profile result",
        source_evidence="Profile and Citi post results identify Shobhit Varshney as Citi's Head of AI.",
    ),
    LiveContact(
        company_key="citi",
        profile_id="citi_ravi_sunkara",
        name="Ravi Sunkara",
        title="Senior Principal Product Manager, AI Cloud and Data Platforms",
        expected_class="HIRING_MANAGER",
        message_type_hint=MESSAGE_GENERAL_INTRO,
        role_ownership_text="Senior Principal Product Manager building AI, cloud, and data platform products at Citi.",
        source_url="https://www.linkedin.com/in/ravi-sunkara-frm-pmp-caie-3a15a68",
        source_label="LinkedIn public profile result",
        source_evidence="Profile result says Ravi Sunkara is a Senior Principal Product Manager building AI, cloud, and data platform products at Citi.",
    ),
    LiveContact(
        company_key="citi",
        profile_id="citi_pratik_waghmare",
        name="Pratik Waghmare",
        title="AI Systems Builder",
        expected_class="HIRING_MANAGER",
        message_type_hint=MESSAGE_GENERAL_INTRO,
        role_ownership_text="Citi AI practitioner building AI systems that work in production-like settings.",
        source_url="https://www.linkedin.com/in/pratik-waghmare",
        source_label="LinkedIn public profile result",
        source_evidence="Profile result says Pratik Waghmare builds AI systems that work in the real world and has Citi experience.",
    ),
    LiveContact(
        company_key="citi",
        profile_id="citi_tim_ryan",
        name="Tim Ryan",
        title="Head of Technology and Business Enablement",
        expected_class="EXECUTIVE",
        message_type_hint=MESSAGE_TRIGGER_BASED_INSIGHT,
        role_ownership_text="Citi executive sponsor for AI approach and technology/business enablement.",
        source_url="https://www.linkedin.com/posts/citi_citiaisummit-ai-activity-7451016191470456832-W_0w",
        source_label="LinkedIn public company post result",
        source_evidence="Citi post says Tim Ryan, Head of Technology & Business Enablement, spoke about Citi's AI approach.",
    ),
    LiveContact(
        company_key="neo4j",
        profile_id="neo4j_clint_obrien",
        name="Clint O'Brien",
        title="Senior Recruiter",
        expected_class="RECRUITER",
        message_type_hint=MESSAGE_GENERAL_INTRO,
        role_ownership_text="Senior Recruiter at Neo4j working on go-to-market, GNA, global SDR, and internship recruiting.",
        source_url="https://www.linkedin.com/posts/clint-o-brien-089133149_recruiting-neo4jcareers-recruiterbranding-activity-7290007549263687680-tGet",
        source_label="LinkedIn public post result",
        source_evidence="Post transcript says Clint O'Brien is a Senior Recruiter at Neo4j in the United States.",
    ),
    LiveContact(
        company_key="neo4j",
        profile_id="neo4j_firat_tekiner",
        name="Firat Tekiner",
        title="Director of Product Management",
        expected_class="HIRING_MANAGER",
        message_type_hint=MESSAGE_TRIGGER_BASED_INSIGHT,
        role_ownership_text="Director of Product Management at Neo4j building at the intersection of AI and knowledge-driven systems.",
        source_url="https://www.linkedin.com/posts/firattekiner_newrole-productmanagement-neo4j-activity-7391439577435127808-wL3Y",
        source_label="LinkedIn public post result",
        source_evidence="Post says Firat Tekiner joined Neo4j as Director of Product Management focused on AI and knowledge-driven systems.",
    ),
    LiveContact(
        company_key="neo4j",
        profile_id="neo4j_sudhir_hasbe",
        name="Sudhir Hasbe",
        title="President and Chief Product Officer",
        expected_class="C_LEVEL",
        message_type_hint=MESSAGE_TRIGGER_BASED_INSIGHT,
        role_ownership_text="President and Chief Product Officer at Neo4j tied to product strategy and AI-native graph expansion.",
        source_url="https://www.linkedin.com/posts/shasbe_a-warm-welcome-to-sudhir-hasbe-neo4js-chief-activity-7049019857933107200-zJ5V",
        source_label="LinkedIn public post result",
        source_evidence="Post result says Sudhir Hasbe joined Neo4j as Chief Product Officer; other result identifies him as President & Chief Product Officer.",
    ),
    LiveContact(
        company_key="neo4j",
        profile_id="neo4j_dan_mcgrath",
        name="Dan McGrath",
        title="Neo4j Product / Hiring Amplifier",
        expected_class="HIRING_MANAGER",
        message_type_hint=MESSAGE_TRIGGER_BASED_INSIGHT,
        role_ownership_text="Neo4j product/hiring signal amplifying the VP Product Management, Agentic AI role.",
        source_url="https://www.linkedin.com/in/dmcgra",
        source_label="LinkedIn public profile result",
        source_evidence="Profile result says Dan McGrath reposted Neo4j's VP Product Management, Agentic AI hiring post.",
    ),
    LiveContact(
        company_key="neo4j",
        profile_id="neo4j_pramod_b",
        name="Pramod B.",
        title="AI and Data Platform Product/Architecture Leader",
        expected_class="HIRING_MANAGER",
        message_type_hint=MESSAGE_GENERAL_INTRO,
        role_ownership_text="Neo4j product and technical leader around cloud, AI, data analytics, and graph platforms.",
        source_url="https://www.linkedin.com/in/pramodborkar",
        source_label="LinkedIn public profile result",
        source_evidence="Profile result says Pramod B. is at Neo4j and architects/positions data platforms across cloud, AI, and data analytics.",
    ),
)


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _load_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def _strip_env_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _load_env_file(env_file: Path | None) -> Path | None:
    candidates = (env_file,) if env_file else DEFAULT_ENV_FILE_CANDIDATES
    for candidate in candidates:
        if candidate is None:
            continue
        path = candidate.resolve()
        if not path.is_file():
            continue
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export ") :].strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if key and key not in os.environ:
                os.environ[key] = _strip_env_quotes(value)
        return path
    return None


def _brief_excerpt(path: Path, *, max_chars: int = 850) -> str:
    return _clean(_load_text(path))[:max_chars]


def _fact_packet(
    *,
    namespace: str,
    document_id: str,
    fact_text: str,
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "document_id": document_id,
        "namespace": namespace,
        "fact_family": namespace,
        "fact_text": fact_text,
        "source_id": f"live_pull:{document_id}",
        "source_type": "public_linkedin_indexed_web_result",
        "source_lineage": [f"live_pull:{document_id}"],
        "freshness_date": FIXED_FRESHNESS_DATE,
        "confidence": 0.90,
        "metadata": dict(metadata or {}),
    }


def _governed_facts(company: CompanyConfig, contact: LiveContact) -> list[dict[str, Any]]:
    canonical_contact = f"{contact.name}|{contact.title}|{company.name}"
    return [
        _fact_packet(
            namespace=NAMESPACE_CONTACT,
            document_id=f"{contact.profile_id}-contact",
            fact_text=f"{contact.name} | {contact.title} | {company.name}. {contact.source_evidence}",
            metadata={
                "name": contact.name,
                "title": contact.title,
                "company": company.name,
                "source_url": contact.source_url,
                "source_label": contact.source_label,
                "conflict_key": "contact_identity",
                "canonical_value": canonical_contact,
            },
        ),
        _fact_packet(
            namespace=NAMESPACE_COMPANY,
            document_id=f"{company.key}-company",
            fact_text=company.company_context,
            metadata={"company": company.name, "briefing_path": str(company.briefing_path)},
        ),
        _fact_packet(
            namespace=NAMESPACE_JD,
            document_id=f"{company.key}-jd",
            fact_text=f"{company.jd_title} role, {company.requisition_number}.",
            metadata={
                "position_name": company.jd_title,
                "requisition_number": company.requisition_number,
                "company": company.name,
                "jd_path": str(company.jd_path),
            },
        ),
        _fact_packet(
            namespace=NAMESPACE_ROLE_OWNERSHIP,
            document_id=f"{contact.profile_id}-role-owner",
            fact_text=contact.role_ownership_text,
            metadata={
                "ownership_signal": contact.role_ownership_text,
                "conflict_key": "role_ownership",
                "canonical_value": contact.role_ownership_text,
            },
        ),
        _fact_packet(
            namespace=NAMESPACE_COMPANY_TRIGGER,
            document_id=f"{company.key}-trigger",
            fact_text=company.trigger_text,
            metadata={"trigger_text": company.trigger_text, "company": company.name},
        ),
    ]


def _message_modifiers(message_type: str) -> dict[str, bool]:
    return {
        "uses_jd": message_type == MESSAGE_ROLE_SPECIFIC,
        "uses_company_trigger": message_type == MESSAGE_TRIGGER_BASED_INSIGHT,
        "uses_referral_context": False,
        "uses_prior_thread": False,
        "uses_sensitive_constraints": False,
    }


def _manual_brief(company: CompanyConfig, contact: LiveContact) -> str:
    return (
        f"Live public web pull for {company.name}: {contact.name}, {contact.title}. "
        f"Evidence: {contact.source_evidence}. "
        f"JD: {company.jd_title} ({company.requisition_number}). "
        f"Briefing excerpt: {_brief_excerpt(company.briefing_path)}"
    )


def _artifact_json(run_dir: Path, name: str) -> dict[str, Any]:
    path = run_dir / name
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _draft_text(run_dir: Path) -> str:
    w4 = _artifact_json(run_dir, sr.FILENAME_W4_CANDIDATE_BATCH)
    selected = ((w4.get("payload") or {}).get("selected_candidate") or {})
    return str(selected.get("draft_text") or "")


def _generated_content_payload(run_dir: Path) -> dict[str, Any]:
    l2 = _artifact_json(run_dir, sr.FILENAME_L2_EXECUTION)
    raw = str((l2.get("payload") or {}).get("generated_content") or "")
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _row_from_run(company: CompanyConfig, contact: LiveContact, run_dir: Path) -> dict[str, Any]:
    manifest = _artifact_json(run_dir, sr.FILENAME_SPINE_MANIFEST)
    proof = _artifact_json(run_dir, "runtime_proof_bundle.json")
    w4 = _artifact_json(run_dir, sr.FILENAME_W4_CANDIDATE_BATCH)
    w5 = _artifact_json(run_dir, sr.FILENAME_W5_VALIDATION_EXIT)
    generated = _generated_content_payload(run_dir)
    w5_payload = w5.get("payload") or {}
    exit_bundle = w5_payload.get("exit_proof_bundle") or {}
    x1d = exit_bundle.get("x1d") or {}
    x2 = exit_bundle.get("x2") or {}
    selected = ((w4.get("payload") or {}).get("selected_candidate") or {})
    app_disposition = (
        str(w5_payload.get("disposition") or "")
        or str(manifest.get("w5_validation_exit_disposition") or "")
        or str(manifest.get("exit_disposition") or "")
        or str(manifest.get("exit_status") or "")
    )
    return {
        "company": company.name,
        "company_key": company.key,
        "profile_id": contact.profile_id,
        "contact_name": contact.name,
        "contact_title": contact.title,
        "source": contact.source_url,
        "source_label": contact.source_label,
        "source_evidence": contact.source_evidence,
        "source_mode": "live_public_web_pull",
        "jd_path": str(company.jd_path),
        "briefing_path": str(company.briefing_path),
        "expected_recipient_class": contact.expected_class,
        "derived_recipient_class": str(manifest.get("derived_recipient_class") or ""),
        "recipient_class_confidence": manifest.get("recipient_class_confidence"),
        "c0_readiness_status": str(manifest.get("c0_readiness_status") or ""),
        "c0_recipient_class_status": str(manifest.get("c0_recipient_class_status") or ""),
        "source_snapshot_ids": list(
            manifest.get("source_snapshot_ids")
            or manifest.get("c03_source_snapshot_ids")
            or []
        ),
        "message_type": str(manifest.get("c03_message_type") or contact.message_type_hint),
        "proof_packet_id": str(manifest.get("c03_proof_packet_id") or ""),
        "candidate_batch_id": str((w4.get("payload") or {}).get("l2_generated_content_digest") or ""),
        "generation_generator": str(generated.get("generator") or ""),
        "generation_provider_profile": str(generated.get("provider_profile") or ""),
        "generation_target_provider": str(generated.get("target_provider") or ""),
        "generation_model": str(generated.get("model") or selected.get("model_id") or ""),
        "generation_qa_notes": list(generated.get("qa_notes") or []),
        "generation_candidate_selection_strategy": str(
            generated.get("candidate_selection_strategy") or ""
        ),
        "provider_receipts": list((w4.get("payload") or {}).get("provider_receipts") or []),
        "model_call_refs": list((w4.get("payload") or {}).get("model_call_refs") or []),
        "selected_candidate_id": str(
            manifest.get("c03_postgen_selected_candidate_id")
            or (w4.get("payload") or {}).get("selected_candidate_id")
            or selected.get("candidate_id")
            or ""
        ),
        "x2_result": str(manifest.get("w5_x2_status") or x2.get("status") or ""),
        "x1d_result": str(manifest.get("w5_x1d_status") or x1d.get("status") or ""),
        "x1d_required_judges": list(
            manifest.get("w5_x1d_required_judge_ids")
            or x1d.get("required_judge_ids")
            or []
        ),
        "x1d_missing_judge_ids": list(
            manifest.get("w5_x1d_missing_judge_ids")
            or x1d.get("missing_judge_ids")
            or []
        ),
        "shared_x3_disposition": str(manifest.get("x3_disposition") or ""),
        "apps_lic_disposition": app_disposition,
        "exit_status": str(manifest.get("exit_status") or ""),
        "draft_visibility_decision": (
            "draft_visible" if manifest.get("outcome_authorized") is True else "not_visible"
        ),
        "outcome_authorized": bool(manifest.get("outcome_authorized") is True),
        "proof_bundle_status": str(proof.get("status") or ""),
        "proof_mode": str(proof.get("proof_mode") or ""),
        "runtime_artifact_dir": str(run_dir),
        "canonical_producer": str(manifest.get("producer_component") or ""),
        "no_send_assertion": bool(manifest.get("no_send_assertion") is True),
        "no_l4_write_assertion": bool(manifest.get("no_l4_write_assertion") is True),
        "no_connector_post_assertion": bool(manifest.get("no_connector_post_assertion") is True),
        "draft_text": _draft_text(run_dir),
    }


def _counter_dict(values: Iterable[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _nested_counter(rows: Iterable[Mapping[str, Any]], field: str) -> dict[str, dict[str, int]]:
    counters: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        counters[str(row["company"])][str(row.get(field) or "")] += 1
    return {
        company: dict(sorted(counter.items()))
        for company, counter in sorted(counters.items())
    }


def _quality_violations(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for row in rows:
        draft = str(row.get("draft_text") or "").lower()
        if str(row["company"]) != "AIG":
            for forbidden in ("aig assist", "underwriting", "claims", "insurance"):
                if forbidden in draft:
                    violations.append(
                        {
                            "profile_id": row["profile_id"],
                            "company": row["company"],
                            "reason": f"non_aig_aig_texture:{forbidden}",
                        }
                    )
        if row.get("proof_bundle_status") != "PASS":
            violations.append({"profile_id": row["profile_id"], "reason": "proof_bundle_not_pass"})
        if not str(row.get("canonical_producer") or "").endswith("canonical_dispatch"):
            violations.append({"profile_id": row["profile_id"], "reason": "not_canonical_dispatch"})
        for field in ("no_send_assertion", "no_l4_write_assertion", "no_connector_post_assertion"):
            if row.get(field) is not True:
                violations.append({"profile_id": row["profile_id"], "reason": f"{field}_false"})
        if (
            row.get("c0_recipient_class_status") == "RECIPIENT_CLASS_DERIVED"
            and row.get("generation_generator") != "qwen_vllm"
        ):
            violations.append(
                {
                    "profile_id": row["profile_id"],
                    "reason": f"live_qwen_candidate_missing:{row.get('proof_mode')}",
                }
            )
        if row.get("draft_text"):
            if row.get("generation_generator") != "qwen_vllm":
                violations.append(
                    {
                        "profile_id": row["profile_id"],
                        "reason": f"draft_not_live_qwen:{row.get('generation_generator')}",
                    }
                )
            if "deterministic_test_provider_stub" in row.get("generation_qa_notes", []):
                violations.append(
                    {"profile_id": row["profile_id"], "reason": "draft_used_test_provider_stub"}
                )
        if row.get("outcome_authorized") is True:
            if not row.get("proof_packet_id"):
                violations.append({"profile_id": row["profile_id"], "reason": "clear_missing_proof_packet_id"})
            if not row.get("selected_candidate_id"):
                violations.append({"profile_id": row["profile_id"], "reason": "clear_missing_selected_candidate_id"})
            if row.get("x2_result") != "X2_VALIDATION_PASS":
                violations.append({"profile_id": row["profile_id"], "reason": "clear_without_x2_pass"})
            if row.get("x1d_result") not in {"X1D_NOT_REQUIRED", "X1D_VALIDATION_PASS"}:
                violations.append({"profile_id": row["profile_id"], "reason": "clear_without_x1d_clearance"})
    return violations


def _build_summary(rows: tuple[dict[str, Any], ...], *, generated_at: str) -> dict[str, Any]:
    company_counts = _counter_dict(str(row["company"]) for row in rows)
    violations = _quality_violations(rows)
    return {
        "schema_version": "apps_lic.post_w7_live_15_contact_company_validation.v1",
        "run_id": RUN_ID,
        "gate_role": SECONDARY_E2E_GATE_ROLE,
        "gate_shape": SECONDARY_E2E_GATE_SHAPE,
        "acceptance_contract": "company_soak_allows_review_required_when_quality_violations_are_zero",
        "generated_at_utc": generated_at,
        "profile_count": len(rows),
        "company_counts": company_counts,
        "source_mode": "live_public_web_pull",
        "canonical_runtime_rows": sum(
            1
            for row in rows
            if str(row.get("canonical_producer") or "").endswith("canonical_dispatch")
        ),
        "parseable_proof_bundle_count": sum(
            1 for row in rows if row.get("proof_bundle_status") == "PASS"
        ),
        "outcome_counts_by_company": _nested_counter(rows, "apps_lic_disposition"),
        "x3_counts_by_company": _nested_counter(rows, "shared_x3_disposition"),
        "recipient_class_counts_by_company": _nested_counter(rows, "derived_recipient_class"),
        "message_type_counts_by_company": _nested_counter(rows, "message_type"),
        "gate_family_counts_by_company": _nested_counter(rows, "proof_mode"),
        "draft_visible_count": sum(1 for row in rows if row.get("outcome_authorized") is True),
        "review_or_block_count": sum(1 for row in rows if row.get("outcome_authorized") is not True),
        "quality_violation_count": len(violations),
        "quality_violations": violations,
        "acceptance_passed": (
            len(rows) == 15
            and company_counts == {"AIG": 5, "Citi": 5, "Neo4j": 5}
            and not violations
        ),
        "live_contact_pull": True,
        "live_contact_pull_note": (
            "Contacts were pulled from public LinkedIn-indexed/current web search "
            "results during the 2026-06-08 Codex run. No LinkedIn login, API, or "
            "behind-auth scraping was used."
        ),
    }


def _write_report(output_dir: Path, summary: Mapping[str, Any], rows: tuple[dict[str, Any], ...]) -> None:
    lines = [
        "# apps_lic Secondary Live Company Soak",
        "",
        f"Run ID: `{summary['run_id']}`",
        f"Gate role: `{summary['gate_role']}`",
        f"Gate shape: `{summary['gate_shape']}`",
        f"Acceptance passed: `{summary['acceptance_passed']}`",
        f"Rows: `{summary['profile_count']}`",
        f"Parseable proof bundles: `{summary['parseable_proof_bundle_count']}`",
        f"Quality violations: `{summary['quality_violation_count']}`",
        "",
        "## Contacts",
        "",
    ]
    for row in rows:
        lines.append(
            "- {company}: {name} ({title}) -> {x3}/{app} proof={proof} source={source}".format(
                company=row["company"],
                name=row["contact_name"],
                title=row["contact_title"],
                x3=row["shared_x3_disposition"],
                app=row["apps_lic_disposition"],
                proof=row["proof_mode"],
                source=row["source"],
            )
        )
    (output_dir / "aggregate_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_post_w7_live_15_contact_company_validation(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    clean_output: bool = False,
    env_file: Path | None = None,
) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    if clean_output and output_dir.exists():
        if REPO_ROOT not in output_dir.parents and output_dir != REPO_ROOT:
            raise ValueError(f"refusing to clean output outside repo: {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    runs_dir = output_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    for company in COMPANIES.values():
        _load_text(company.jd_path)
        _load_text(company.briefing_path)

    loaded_env_file = _load_env_file(env_file)
    old_provider_env = {key: os.environ.get(key) for key in LIVE_PROVIDER_ENV_KEYS}
    os.environ.pop("APPS_LIC_TEST_PROVIDER_STUB", None)
    os.environ["APPS_LIC_REQUIRE_QWEN_VLLM"] = "1"
    os.environ["APPS_LIC_RUN_LIVE_CLAUDE_X1D"] = (
        "1" if str(os.environ.get("ANTHROPIC_API_KEY") or "").strip() else "0"
    )
    live_claude_x1d_enabled = os.environ["APPS_LIC_RUN_LIVE_CLAUDE_X1D"] == "1"
    rows: list[dict[str, Any]] = []
    try:
        for index, contact in enumerate(LIVE_CONTACTS, start=1):
            company = COMPANIES[contact.company_key]
            run_root = runs_dir / company.key / f"{index:02d}_{contact.profile_id}"
            raw = build_cli_ingress_raw(
                run_id=f"{RUN_ID}_{company.key}_{index:02d}",
                request_id=f"req_{RUN_ID}_{company.key}_{index:02d}",
                trace_id=f"trace_{RUN_ID}_{company.key}_{index:02d}",
                recipient_class="",
                manual_brief=_manual_brief(company, contact),
                campaign_objective=(
                    f"Draft a concise LinkedIn outreach note for {company.name} "
                    f"using the live-sourced contact and {company.jd_title} context."
                ),
                lead_profile={
                    "verified_name": contact.name,
                    "title": contact.title,
                    "seniority_class": "",
                    "company_name": company.name,
                    "industry": "AI",
                    "consent_attested": True,
                },
                governed_opportunity_facts=_governed_facts(company, contact),
                message_type_hint=contact.message_type_hint,
                message_modifiers=_message_modifiers(contact.message_type_hint),
                desired_next_step="a concise screen or follow-up conversation",
            )
            result = run_canonical_apps_lic_spine(raw, artifact_root=run_root)
            rows.append(_row_from_run(company, contact, result.artifact_dir))
    finally:
        for key, value in old_provider_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    row_tuple = tuple(rows)
    summary = _build_summary(row_tuple, generated_at=datetime.now(timezone.utc).isoformat())
    summary["provider_mode"] = "live_qwen_vllm_required"
    summary["x1d_provider_mode"] = (
        "live_claude_required_when_x1d_required"
        if live_claude_x1d_enabled
        else "live_claude_unavailable_fail_closed"
    )
    summary["env_file_loaded"] = str(loaded_env_file) if loaded_env_file else ""
    summary["stub_forbidden"] = True
    summary["live_claude_x1d_enabled"] = live_claude_x1d_enabled
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "rows.json").write_text(
        json.dumps({"schema_version": "apps_lic.post_w7_live_15_rows.v1", "rows": row_tuple}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "live_contact_pull.json").write_text(
        json.dumps(
            {
                "schema_version": "apps_lic.post_w7_live_contact_pull.v1",
                "pulled_at_utc": datetime.now(timezone.utc).isoformat(),
                "source_mode": "public_linkedin_indexed_web_search",
                "contacts": [contact.__dict__ for contact in LIVE_CONTACTS],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    _write_report(output_dir, summary, row_tuple)
    return {
        "output_dir": str(output_dir),
        "summary": summary,
        "artifact_files": [
            "summary.json",
            "rows.json",
            "live_contact_pull.json",
            "aggregate_report.md",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--env-file", type=Path, default=None)
    args = parser.parse_args()
    result = run_post_w7_live_15_contact_company_validation(
        output_dir=args.output_dir,
        clean_output=args.clean,
        env_file=args.env_file,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["summary"]["acceptance_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
