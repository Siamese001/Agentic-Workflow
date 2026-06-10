"""Main full live E2E gate for apps_lic.

Runs one recruiter, one senior TA, one C-level, and one executive-archetype
contact for each of AIG, Citi, and Neo4j. Sources are public LinkedIn-indexed
web results; this script does not log in, scrape behind auth, send messages, or
call LinkedIn APIs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from collections import Counter, defaultdict
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
    MESSAGE_ROLE_SPECIFIC,
    MESSAGE_TRIGGER_BASED_INSIGHT,
)
from apps_lic.runtime.dispatch import stage_receipts as sr  # noqa: E402
from apps_lic.runtime.dispatch.canonical_dispatch import (  # noqa: E402
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from apps_lic.engines.validation_exit import x1d_judge_profile_policy  # noqa: E402
from apps_lic.types.recipient_archetype_mapping import (  # noqa: E402
    ARCHETYPE_C_LEVEL,
    ARCHETYPE_EXECUTIVE,
    ARCHETYPE_RECRUITER,
    ARCHETYPE_SENIOR_TA,
    map_lic_recipient_class_to_archetype,
)
from apps_lic.types.recipient_policy_profile import (  # noqa: E402
    build_recipient_policy_profile,
)
from scripts.apps_lic.run_post_w7_live_15_contact_company_validation import (  # noqa: E402
    COMPANIES,
    DEFAULT_ENV_FILE_CANDIDATES,
    LIVE_PROVIDER_ENV_KEYS,
    CompanyConfig,
    LiveContact,
    _load_env_file,
    _load_text,
    _message_modifiers,
    _quality_violations,
    _row_from_run,
)


RUN_ID = "post_w7_live_12_archetype_matrix_20260609"
FRESHNESS_DATE = "2026-06-09T00:00:00+00:00"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "artifacts" / "apps_lic" / "post_w7_live_12_archetype_matrix"
FULL_E2E_GATE_ROLE = "main_full_e2e_gate"
FULL_E2E_GATE_SHAPE = "4_per_company_12_archetype_matrix"
THRESHOLD_PROFILE_ID = "atp::apps_lic::outreach_message::v1"
SCORE_TYPE_LIVE_X1D_MIN = "Live X1D min score"
SCORE_TYPE_X2_PASS_RATIO = "X2 pass ratio"

REQUESTED_SLOT_BY_PROFILE: dict[str, str] = {
    "aig_nina_k": "Recruiter",
    "aig_regina_gilligan": "Senior TA",
    "aig_jim_young": "C-Level",
    "aig_charlie_fry": "Executive",
    "citi_dee_morgan": "Recruiter",
    "citi_juan_manuel_cerda": "Senior TA",
    "citi_brian_saluzzo": "C-Level",
    "citi_shobhit_varshney": "Executive",
    "neo4j_clint_obrien": "Recruiter",
    "neo4j_penny_stevenson": "Senior TA",
    "neo4j_sudhir_hasbe": "C-Level",
    "neo4j_firat_tekiner": "Executive",
}

REQUESTED_ARCHETYPE_BY_PROFILE: dict[str, str] = {
    "aig_nina_k": ARCHETYPE_RECRUITER,
    "aig_regina_gilligan": ARCHETYPE_SENIOR_TA,
    "aig_jim_young": ARCHETYPE_C_LEVEL,
    "aig_charlie_fry": ARCHETYPE_EXECUTIVE,
    "citi_dee_morgan": ARCHETYPE_RECRUITER,
    "citi_juan_manuel_cerda": ARCHETYPE_SENIOR_TA,
    "citi_brian_saluzzo": ARCHETYPE_C_LEVEL,
    "citi_shobhit_varshney": ARCHETYPE_EXECUTIVE,
    "neo4j_clint_obrien": ARCHETYPE_RECRUITER,
    "neo4j_penny_stevenson": ARCHETYPE_SENIOR_TA,
    "neo4j_sudhir_hasbe": ARCHETYPE_C_LEVEL,
    "neo4j_firat_tekiner": ARCHETYPE_EXECUTIVE,
}

LIVE_ARCHETYPE_CONTACTS: tuple[LiveContact, ...] = (
    LiveContact(
        company_key="aig",
        profile_id="aig_nina_k",
        name="Nina K.",
        title="Strategic Technical Recruiter and Sourcer",
        expected_class="RECRUITER",
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        role_ownership_text="Strategic technical recruiter and sourcer specializing in AI and emerging technology searches at AIG.",
        source_url="https://www.linkedin.com/in/nkshatri",
        source_label="LinkedIn public profile result",
        source_evidence="Profile result identifies Nina K. at AIG as a strategic technical recruiter and sourcer specializing in AI researchers and machine roles.",
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
        source_evidence="Profile result identifies Regina Gilligan as an experienced Talent Acquisition Manager at AIG.",
    ),
    LiveContact(
        company_key="aig",
        profile_id="aig_jim_young",
        name="Jim Young",
        title="Global Chief Data Officer",
        expected_class="C_LEVEL",
        message_type_hint=MESSAGE_TRIGGER_BASED_INSIGHT,
        role_ownership_text="Global Chief Data Officer tied to AIG data, AI, and agentic AI platform context.",
        source_url="https://www.linkedin.com/posts/cdo-magazine_jim-young-aig-global-chief-data-officer-activity-7097271787876450304-3St1",
        source_label="LinkedIn public post result",
        source_evidence="LinkedIn-indexed CDO Magazine post identifies Jim Young as AIG Global Chief Data Officer.",
    ),
    LiveContact(
        company_key="aig",
        profile_id="aig_charlie_fry",
        name="Charlie Fry",
        title="Executive Vice President, Reinsurance Purchasing and Risk Capital Optimization",
        expected_class="EXECUTIVE",
        message_type_hint=MESSAGE_TRIGGER_BASED_INSIGHT,
        role_ownership_text="Executive Vice President at AIG responsible for reinsurance purchasing and capital allocation optimization.",
        source_url="https://www.linkedin.com/posts/aig_aig-names-charlie-fry-executive-vice-president-activity-6957335677134888960-mKrg",
        source_label="LinkedIn public company post result",
        source_evidence="AIG's LinkedIn post says Charlie Fry rejoined as EVP, Reinsurance Purchasing and Risk Capital Optimization, reporting to the company's top executive.",
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
        source_evidence="Profile result identifies Dee Morgan as a Citi Talent Acquisition Strategist posting AI audit and AI governance roles.",
    ),
    LiveContact(
        company_key="citi",
        profile_id="citi_juan_manuel_cerda",
        name="Juan Manuel Cerda",
        title="Head of Talent Acquisition and People Insights",
        expected_class="SENIOR_TA",
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        role_ownership_text="Head of Talent Acquisition and People Insights at Citi discussing recruiting and retention.",
        source_url="https://www.linkedin.com/posts/citi_how-are-we-attracting-and-retaining-talent-activity-6932013561556742144-mOY2",
        source_label="LinkedIn public company post result",
        source_evidence="Citi's LinkedIn post identifies Juan Manuel Cerda as Head of Talent Acquisition and People Insights.",
    ),
    LiveContact(
        company_key="citi",
        profile_id="citi_brian_saluzzo",
        name="Brian Saluzzo",
        title="Chief Information Officer",
        expected_class="C_LEVEL",
        message_type_hint=MESSAGE_TRIGGER_BASED_INSIGHT,
        role_ownership_text="Chief Information Officer at Citi shaping global technology services and AI-enabled firmwide technology work.",
        source_url="https://www.linkedin.com/posts/bsaluzzo_excited-to-share-that-i-have-joined-citi-activity-7454569884090417152-B5Fa",
        source_label="LinkedIn public post result",
        source_evidence="LinkedIn post says Brian Saluzzo joined Citi as Chief Information Officer.",
    ),
    LiveContact(
        company_key="citi",
        profile_id="citi_shobhit_varshney",
        name="Shobhit Varshney",
        title="Head of AI",
        expected_class="HIRING_MANAGER",
        message_type_hint=MESSAGE_TRIGGER_BASED_INSIGHT,
        role_ownership_text="Head of AI at Citi leading responsible scaling of AI capabilities across the company.",
        source_url="https://www.linkedin.com/posts/citi_shobhit-varshney-citis-head-of-ai-talks-activity-7439389670972682240-stKp",
        source_label="LinkedIn public company post result",
        source_evidence="Citi's LinkedIn post identifies Shobhit Varshney as Head of AI discussing responsible and effective AI.",
    ),
    LiveContact(
        company_key="neo4j",
        profile_id="neo4j_clint_obrien",
        name="Clint O'Brien",
        title="Senior Recruiter",
        expected_class="RECRUITER",
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        role_ownership_text="Senior Recruiter at Neo4j working on go-to-market, GNA, global SDR, and internship recruiting.",
        source_url="https://www.linkedin.com/posts/clint-o-brien-089133149_recruiting-neo4jcareers-recruiterbranding-activity-7290007549263687680-tGet",
        source_label="LinkedIn public post result",
        source_evidence="Post transcript says Clint O'Brien is a Senior Recruiter at Neo4j based in the United States.",
    ),
    LiveContact(
        company_key="neo4j",
        profile_id="neo4j_penny_stevenson",
        name="Penny Stevenson",
        title="Talent Acquisition Manager",
        expected_class="SENIOR_TA",
        message_type_hint=MESSAGE_ROLE_SPECIFIC,
        role_ownership_text="Talent Acquisition Manager at Neo4j leading recruitment strategy for EMEA.",
        source_url="https://uk.linkedin.com/in/penny-stevenson-81260435",
        source_label="LinkedIn public profile result",
        source_evidence="Profile result identifies Penny Stevenson as a Talent Acquisition Manager at Neo4j leading recruitment strategy for EMEA.",
    ),
    LiveContact(
        company_key="neo4j",
        profile_id="neo4j_sudhir_hasbe",
        name="Sudhir Hasbe",
        title="President and Chief Product Officer",
        expected_class="C_LEVEL",
        message_type_hint=MESSAGE_TRIGGER_BASED_INSIGHT,
        role_ownership_text="President and Chief Product Officer at Neo4j tied to graph intelligence and AI product strategy.",
        source_url="https://www.linkedin.com/posts/shasbe_a-warm-welcome-to-sudhir-hasbe-neo4js-chief-activity-7049019857933107200-zJ5V",
        source_label="LinkedIn public post result",
        source_evidence="LinkedIn post identifies Sudhir Hasbe as Neo4j's Chief Product Officer; current result also identifies him as President and Chief Product Officer.",
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
)


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


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
        "freshness_date": FRESHNESS_DATE,
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


def _brief_excerpt(path: Path, *, max_chars: int = 850) -> str:
    return _clean(_load_text(path))[:max_chars]


def _manual_brief(company: CompanyConfig, contact: LiveContact) -> str:
    return (
        f"Live public LinkedIn-indexed web pull for {company.name}: "
        f"{contact.name}, {contact.title}. Evidence: {contact.source_evidence}. "
        f"JD: {company.jd_title} ({company.requisition_number}). "
        f"Briefing excerpt: {_brief_excerpt(company.briefing_path)}"
    )


def _artifact_json(run_dir: Path, name: str) -> dict[str, Any]:
    path = run_dir / name
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _x2_score_10(x2: Mapping[str, Any]) -> float:
    gates = [
        gate
        for gate in x2.get("gate_results", [])
        if isinstance(gate, Mapping) and gate.get("status") != "not_applicable"
    ]
    if not gates:
        return 0.0
    passed = sum(1 for gate in gates if gate.get("status") == "pass")
    return round((passed / len(gates)) * 10.0, 2)


def _gate_metrics(run_dir: Path) -> dict[str, Any]:
    w5 = _artifact_json(run_dir, sr.FILENAME_W5_VALIDATION_EXIT)
    exit_bundle = ((w5.get("payload") or {}).get("exit_proof_bundle") or {})
    x2 = exit_bundle.get("x2") or {}
    x1d = exit_bundle.get("x1d") or {}
    judge_results = [
        dict(item)
        for item in x1d.get("judge_results", [])
        if isinstance(item, Mapping)
    ]
    scores = [
        float(item["score"])
        for item in judge_results
        if isinstance(item.get("score"), (int, float))
    ]
    thresholds = [
        float(item["threshold"])
        for item in judge_results
        if isinstance(item.get("threshold"), (int, float))
    ]
    if scores:
        score_10 = round(min(scores) * 10.0, 2)
        basis = "min_required_live_x1d_judge"
        score_type = SCORE_TYPE_LIVE_X1D_MIN
    else:
        score_10 = _x2_score_10(x2)
        basis = "x2_applicable_gate_pass_ratio"
        score_type = SCORE_TYPE_X2_PASS_RATIO
    return {
        "gate_score_10": score_10,
        "gate_score_basis": basis,
        "score_type": score_type,
        "x2_applicable_score_10": _x2_score_10(x2),
        "x2_failed_gate_ids": list(x2.get("failed_gate_ids") or []),
        "x1d_judge_scores_10": [
            {
                "judge_id": str(item.get("judge_id") or ""),
                "score_10": round(float(item.get("score") or 0.0) * 10.0, 2),
                "threshold_10": round(float(item.get("threshold") or 0.0) * 10.0, 2),
                "passed": bool(item.get("passed") is True),
                "issues": list(item.get("issues") or []),
                "required_repairs": list(item.get("required_repairs") or []),
            }
            for item in judge_results
        ],
        "gate_threshold_10": round(min(thresholds) * 10.0, 2) if thresholds else None,
    }


def _x1d_not_required_acceptable_by_policy(row: Mapping[str, Any]) -> bool:
    if row.get("x1d_result") != "X1D_NOT_REQUIRED":
        return False
    reasons = set(str(item) for item in row.get("recipient_policy_reason_codes") or [])
    if "x1d_explicitly_waived_by_policy" in reasons:
        return True
    return (
        row.get("minimum_score_profile_id") == "apps_lic.score_profile.x2_only.v1"
        and row.get("mapped_recipient_archetype") not in {ARCHETYPE_EXECUTIVE, ARCHETYPE_C_LEVEL}
    )


def _x1d_policy_clearance(row: Mapping[str, Any]) -> str:
    if row.get("outcome_authorized") is not True:
        return "not_clear_draft"
    if row.get("x1d_result") == "X1D_VALIDATION_PASS":
        return "required_live_x1d_judge_evidence_present"
    if _x1d_not_required_acceptable_by_policy(row):
        return "x1d_not_required_acceptable_by_policy"
    if row.get("x1d_result") == "X1D_NOT_REQUIRED":
        return "x1d_not_required_not_acceptable_by_policy"
    return "x1d_not_clear"


def _selected_message_details(run_dir: Path) -> dict[str, Any]:
    w5 = _artifact_json(run_dir, sr.FILENAME_W5_VALIDATION_EXIT)
    selected = ((w5.get("payload") or {}).get("final_selected_candidate") or {})
    w4 = _artifact_json(run_dir, sr.FILENAME_W4_CANDIDATE_BATCH)
    if not selected:
        selected = ((w4.get("payload") or {}).get("selected_candidate") or {})
    subject = _clean(selected.get("subject_line") or selected.get("subject"))
    body = str(selected.get("draft_text") or "")
    return {
        "subject_line": subject,
        "subject_chars": len(subject),
        "body_chars": len(body),
        "draft_text": body,
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


def _matrix_violations(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    violations = list(_quality_violations(rows))
    for row in rows:
        if row.get("expected_mapped_archetype") != row.get("mapped_recipient_archetype"):
            violations.append(
                {
                    "profile_id": row["profile_id"],
                    "company": row["company"],
                    "reason": "requested_archetype_not_matched",
                }
            )
        if row.get("derived_recipient_class") != row.get("expected_recipient_class"):
            violations.append(
                {
                    "profile_id": row["profile_id"],
                    "company": row["company"],
                    "reason": "expected_lic_class_not_matched",
                }
            )
        if row.get("outcome_authorized") is not True:
            violations.append(
                {
                    "profile_id": row["profile_id"],
                    "company": row["company"],
                    "reason": "draft_not_cleared_by_exit_gate",
                }
            )
        if row.get("message_route") != "INMAIL":
            violations.append(
                {
                    "profile_id": row["profile_id"],
                    "company": row["company"],
                    "reason": "message_route_not_inmail",
                }
            )
        if row.get("message_channel") != "linkedin_inmail":
            violations.append(
                {
                    "profile_id": row["profile_id"],
                    "company": row["company"],
                    "reason": "message_channel_not_linkedin_inmail",
                }
            )
        if not _clean(row.get("subject_line")):
            violations.append(
                {
                    "profile_id": row["profile_id"],
                    "company": row["company"],
                    "reason": "inmail_subject_missing",
                }
            )
        if int(row.get("body_chars") or 0) > 1900:
            violations.append(
                {
                    "profile_id": row["profile_id"],
                    "company": row["company"],
                    "reason": "inmail_body_over_1900_chars",
                }
            )
        if (
            row.get("outcome_authorized") is True
            and row.get("x1d_result") == "X1D_NOT_REQUIRED"
            and row.get("mapped_recipient_archetype") in {ARCHETYPE_EXECUTIVE, ARCHETYPE_C_LEVEL}
            and not _x1d_not_required_acceptable_by_policy(row)
        ):
            violations.append(
                {
                    "profile_id": row["profile_id"],
                    "company": row["company"],
                    "reason": "executive_archetype_x1d_not_required",
                }
            )
    return violations


def _build_summary(rows: tuple[dict[str, Any], ...], *, generated_at: str) -> dict[str, Any]:
    company_counts = _counter_dict(str(row["company"]) for row in rows)
    slot_counts = _nested_counter(rows, "requested_slot")
    violations = _matrix_violations(rows)
    return {
        "schema_version": "apps_lic.post_w7_live_12_archetype_matrix.v1",
        "run_id": RUN_ID,
        "gate_role": FULL_E2E_GATE_ROLE,
        "gate_shape": FULL_E2E_GATE_SHAPE,
        "acceptance_contract": "all_12_company_archetype_rows_clear_with_zero_quality_violations",
        "generated_at_utc": generated_at,
        "profile_count": len(rows),
        "company_counts": company_counts,
        "requested_slot_counts_by_company": slot_counts,
        "source_mode": "live_public_linkedin_indexed_web_pull",
        "canonical_runtime_rows": sum(
            1
            for row in rows
            if str(row.get("canonical_producer") or "").endswith("canonical_dispatch")
        ),
        "parseable_proof_bundle_count": sum(
            1 for row in rows if row.get("proof_bundle_status") == "PASS"
        ),
        "outcome_counts_by_company": _nested_counter(rows, "apps_lic_disposition"),
        "recipient_class_counts_by_company": _nested_counter(rows, "derived_recipient_class"),
        "mapped_archetype_counts_by_company": _nested_counter(rows, "mapped_recipient_archetype"),
        "message_type_counts_by_company": _nested_counter(rows, "message_type"),
        "route_counts_by_company": _nested_counter(rows, "message_route"),
        "channel_counts_by_company": _nested_counter(rows, "message_channel"),
        "draft_visible_count": sum(1 for row in rows if row.get("outcome_authorized") is True),
        "review_or_block_count": sum(1 for row in rows if row.get("outcome_authorized") is not True),
        "quality_violation_count": len(violations),
        "quality_violations": violations,
        "acceptance_passed": (
            len(rows) == 12
            and company_counts == {"AIG": 4, "Citi": 4, "Neo4j": 4}
            and all(
                set(company_slots) == {"Recruiter", "Senior TA", "C-Level", "Executive"}
                for company_slots in (
                    set(row["requested_slot"] for row in rows if row["company"] == company)
                    for company in ("AIG", "Citi", "Neo4j")
                )
            )
            and not violations
        ),
        "live_contact_pull": True,
        "live_contact_pull_note": (
            "Contacts were pulled from public LinkedIn-indexed/current web results "
            "during the 2026-06-09 Codex run. No LinkedIn login, API, or behind-auth "
            "scraping was used."
        ),
    }


def _escape_table(value: Any) -> str:
    text = str(value or "")
    text = text.replace("\n", "<br>")
    return text.replace("|", "\\|")


def _write_report(output_dir: Path, summary: Mapping[str, Any], rows: tuple[dict[str, Any], ...]) -> None:
    lines = [
        "# apps_lic Main Full Live E2E Gate",
        "",
        f"Run ID: `{summary['run_id']}`",
        f"Gate role: `{summary.get('gate_role', FULL_E2E_GATE_ROLE)}`",
        f"Gate shape: `{summary.get('gate_shape', FULL_E2E_GATE_SHAPE)}`",
        f"Acceptance passed: `{summary['acceptance_passed']}`",
        f"Rows: `{summary['profile_count']}`",
        f"Quality violations: `{summary['quality_violation_count']}`",
        "",
        "## Summary",
        "",
        "| # | Company | Requested Slot | Contact | LinkedIn Title | LIC Class | Prompt Archetype | Policy Profile | Threshold Profile | Message Type | Route | Score Type | Gate Score/10 | Threshold/10 | X1D Policy | Exit | Source |",
        "|---:|---|---|---|---|---|---|---|---|---|---|---|---:|---:|---|---|---|",
    ]
    for index, row in enumerate(rows, start=1):
        lines.append(
            "| {index} | {company} | {slot} | {name} | {title} | {lic} | {arch} | {policy} | {threshold_profile} | {message_type} | {route} | {score_type} | {score} | {threshold} | {x1d_policy} | {exit_status} | {source} |".format(
                index=index,
                company=_escape_table(row["company"]),
                slot=_escape_table(row["requested_slot"]),
                name=_escape_table(row["contact_name"]),
                title=_escape_table(row["contact_title"]),
                lic=_escape_table(row["derived_recipient_class"]),
                arch=_escape_table(row["mapped_recipient_archetype"]),
                policy=_escape_table(row.get("policy_profile_id") or row.get("recipient_policy_profile_id")),
                threshold_profile=_escape_table(row.get("threshold_profile_id")),
                message_type=_escape_table(row["message_type"]),
                route=_escape_table(row["message_route"]),
                score_type=_escape_table(row.get("score_type")),
                score=_escape_table(row["gate_score_10"]),
                threshold=_escape_table(row.get("gate_threshold_10")),
                x1d_policy=_escape_table(row.get("x1d_policy_clearance")),
                exit_status=_escape_table(row["apps_lic_disposition"]),
                source=_escape_table(row["source"]),
            )
        )
    lines.extend(["", "## Full Messages", ""])
    for index, row in enumerate(rows, start=1):
        lines.append(
            "### {index}. {company} - {slot} - {name}".format(
                index=index,
                company=row["company"],
                slot=row["requested_slot"],
                name=row["contact_name"],
            )
        )
        lines.append("")
        lines.append(f"- LinkedIn title: `{row['contact_title']}`")
        lines.append(f"- Route/channel: `{row['message_route']}` / `{row['message_channel']}`")
        lines.append(
            f"- LIC class -> archetype: `{row['derived_recipient_class']}` -> `{row['mapped_recipient_archetype']}`"
        )
        lines.append(f"- Policy profile: `{row.get('policy_profile_id') or row['recipient_policy_profile_id']}`")
        lines.append(f"- Threshold profile: `{row['threshold_profile_id']}`")
        lines.append(
            f"- Policy reasons: `{json.dumps(row['recipient_policy_reason_codes'], sort_keys=True)}`"
        )
        lines.append(f"- Message type: `{row['message_type']}`")
        lines.append(f"- Score type: `{row['score_type']}`")
        lines.append(f"- X1D policy clearance: `{row['x1d_policy_clearance']}`")
        lines.append(f"- Subject ({row['subject_chars']} chars): {row['subject_line']}")
        lines.append(f"- Body chars: `{row['body_chars']}`")
        lines.append(f"- Gate score: `{row['gate_score_10']}/10`")
        lines.append(f"- Exit: `{row['apps_lic_disposition']}`")
        lines.append(f"- Source: {row['source']}")
        lines.append("")
        lines.append("**Message**")
        lines.append("")
        for message_line in str(row["draft_text"]).strip().splitlines():
            lines.append(message_line)
        lines.append("")
    lines.extend(
        [
            "",
            "## Judge Details",
            "",
        ]
    )
    for row in rows:
        lines.append(
            "### {company} - {slot} - {name}".format(
                company=row["company"],
                slot=row["requested_slot"],
                name=row["contact_name"],
            )
        )
        lines.append("")
        lines.append(f"- Gate score basis: `{row['gate_score_basis']}`")
        lines.append(f"- X2 failed gates: `{row['x2_failed_gate_ids']}`")
        lines.append(f"- Score type: `{row['score_type']}`")
        lines.append(f"- X1D policy clearance: `{row['x1d_policy_clearance']}`")
        judges = list(row.get("x1d_judge_scores_10") or [])
        if judges:
            lines.extend(
                [
                    "",
                    "| Judge | Score/10 | Threshold/10 | Passed |",
                    "|---|---:|---:|---|",
                ]
            )
            for judge in judges:
                lines.append(
                    "| {judge_id} | {score} | {threshold} | {passed} |".format(
                        judge_id=_escape_table(judge.get("judge_id")),
                        score=_escape_table(judge.get("score_10")),
                        threshold=_escape_table(judge.get("threshold_10")),
                        passed=_escape_table(judge.get("passed")),
                    )
                )
        else:
            lines.append("- X1D judges: `none_required_by_policy`")
        lines.append("")
    (output_dir / "full_messages.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_post_w7_live_12_archetype_matrix(
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
    judge_thresholds = {
        judge_id: profile.threshold
        for judge_id, profile in x1d_judge_profile_policy().items()
    }
    rows: list[dict[str, Any]] = []
    try:
        for index, contact in enumerate(LIVE_ARCHETYPE_CONTACTS, start=1):
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
                desired_next_step="a concise screen, fit review, redirect, or follow-up conversation",
                connection_status="NOT_CONNECTED",
                premium_available=True,
                route_override="INMAIL",
            )
            route_packet = (
                ((raw.get("personalization") or {}).get("inputs") or {}).get(
                    "linkedin_route_envelope"
                )
                or {}
            )
            result = run_canonical_apps_lic_spine(raw, artifact_root=run_root)
            row = _row_from_run(company, contact, result.artifact_dir)
            derived_class = str(row.get("derived_recipient_class") or "")
            mapped_archetype = map_lic_recipient_class_to_archetype(derived_class)
            row.update(
                {
                    "requested_slot": REQUESTED_SLOT_BY_PROFILE[contact.profile_id],
                    "expected_mapped_archetype": REQUESTED_ARCHETYPE_BY_PROFILE[contact.profile_id],
                    "mapped_recipient_archetype": mapped_archetype,
                    "archetype_match": mapped_archetype
                    == REQUESTED_ARCHETYPE_BY_PROFILE[contact.profile_id],
                    "message_route": str(route_packet.get("route") or ""),
                    "message_channel": str(route_packet.get("channel") or ""),
                    "route_decision_reason": str(route_packet.get("decision_reason") or ""),
                    "route_hard_cap_chars": int(route_packet.get("hard_cap_chars") or 0),
                }
            )
            policy_profile = build_recipient_policy_profile(
                requested_slot=REQUESTED_SLOT_BY_PROFILE[contact.profile_id],
                actual_linkedin_title=contact.title,
                derived_recipient_class=derived_class,
                expected_prompt_archetype=REQUESTED_ARCHETYPE_BY_PROFILE[contact.profile_id],
                message_type=str(row.get("message_type") or contact.message_type_hint),
                required_route_family=str(route_packet.get("route") or ""),
                required_x1d_judge_profile_ids=list(row.get("x1d_required_judges") or []),
                x1d_thresholds_by_judge_id=judge_thresholds,
            )
            row.update(policy_profile.to_row_fields())
            row.update(_selected_message_details(result.artifact_dir))
            row.update(_gate_metrics(result.artifact_dir))
            row["policy_profile_id"] = policy_profile.policy_profile_id
            row["threshold_profile_id"] = THRESHOLD_PROFILE_ID
            row["x1d_not_required_policy_acceptable"] = _x1d_not_required_acceptable_by_policy(row)
            row["x1d_policy_clearance"] = _x1d_policy_clearance(row)
            rows.append(row)
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
        json.dumps(
            {"schema_version": "apps_lic.post_w7_live_12_archetype_rows.v1", "rows": row_tuple},
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    (output_dir / "live_contact_pull.json").write_text(
        json.dumps(
            {
                "schema_version": "apps_lic.post_w7_live_12_archetype_contact_pull.v1",
                "pulled_at_utc": datetime.now(timezone.utc).isoformat(),
                "source_mode": "public_linkedin_indexed_web_search",
                "contacts": [contact.__dict__ for contact in LIVE_ARCHETYPE_CONTACTS],
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
            "full_messages.md",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--env-file", type=Path, default=None)
    args = parser.parse_args()
    result = run_post_w7_live_12_archetype_matrix(
        output_dir=args.output_dir,
        clean_output=args.clean,
        env_file=args.env_file,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["summary"]["acceptance_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
