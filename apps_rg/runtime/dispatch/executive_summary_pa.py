"""Executive summary: build PromptAssemblyInput from runtime payload + template YAML (W4).

Loads slot bodies from ``executive_summary.generate_scratch_v1.yaml`` and compiles via
``section_prompt_adapter``. C0 carries selected_fact_plan facts (proof). The
``c0_jd_requirements`` block carries JD_TEXT + BRIEFING + target framing for **targeting
only** (rank, order, vocabulary tilt among evidenced facts) - never as proof. Style should match the
canonical base résumé register (dense, concrete stack/governance nouns), without JD
keyword-stuffing.
"""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import yaml

from apps_rg.prompt_assembly.contracts import EvidenceSource, PromptAssemblyInput
from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt, compile_section_prompt
from apps_rg.runtime.dispatch.input_authority_prompt_block import augment_section_compiled_with_input_authority


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (
            parent
            / "apps_rg"
            / "prompt_assembly"
            / "templates"
            / "executive_summary.generate_scratch_v1.yaml"
        ).is_file():
            return parent
    raise FileNotFoundError(
        "Cannot resolve repo root from executive_summary_pa.py (template yaml not found in parents)"
    )


_REPO_ROOT = _repo_root()
_TEMPLATE_PATH = (
    _REPO_ROOT
    / "apps_rg"
    / "prompt_assembly"
    / "templates"
    / "executive_summary.generate_scratch_v1.yaml"
)

_EXEC_SUMMARY_OUTPUT_SCHEMA_JSON = json.dumps(
    {
        "type": "object",
        "required": [
            "resume_display_text",
            "claim_ledger",
            "jd_alignment",
            "gap_notes",
            "change_log",
            "self_check",
        ],
        "properties": {
            "resume_display_text": {
                "type": "string",
                "description": (
                    "Third-person polished executive summary: default 2–3 dense sentences for legacy runs; "
                    "SelectedRoleFactSet (SRFS) mode targets **4–5** period-delimited sentences with deterministic "
                    "95–160 word bounds (see SRFS appendix + X2 gates). "
                    "No inline citations or fact IDs; no selected_fact_plan echo"
                ),
            },
            "claim_ledger": {
                "type": "array",
                "description": (
                    "Each row must include non-empty claim_text (material claim supported by source_fact_ids) and "
                    "source_fact_ids copied exactly from ALLOWED_SOURCE_FACT_IDS. Rows with only source_fact_ids fail "
                    "gate x2_claim_ledger_claim_text_non_empty. Malformed or orphan IDs fail X2 and block X3."
                ),
                "items": {
                    "type": "object",
                    "required": ["claim_text", "source_fact_ids"],
                    "properties": {
                        "claim_text": {
                            "type": "string",
                            "minLength": 1,
                            "description": (
                                "Non-empty material claim text supported by this row's source_fact_ids; must align with "
                                "resume_display_text. Whitespace-only is invalid."
                            ),
                        },
                        "claim": {
                            "type": "string",
                            "description": (
                                "Optional legacy alias for claim_text; normalize to claim_text. JD, title, "
                                "company, and briefing are mandatory non-evidence inputs - never list them "
                                "in source_fact_ids or treat them as claim evidence."
                            ),
                        },
                        "source_fact_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "Each string must exactly match one entry from ALLOWED_SOURCE_FACT_IDS. "
                                "Example: bul_unify_003 is valid when listed; bul_unify_ 003 is never valid."
                            ),
                        },
                    },
                },
            },
            "jd_alignment": {"type": "object"},
            "gap_notes": {"type": "array"},
            "change_log": {"type": "array"},
            "self_check": {"type": "object"},
        },
    },
    sort_keys=True,
)


def load_executive_summary_template_slots() -> dict[str, str]:
    raw = yaml.safe_load(_TEMPLATE_PATH.read_text(encoding="utf-8"))
    bodies = raw.get("slot_bodies") or {}
    return {str(k): str(v) for k, v in bodies.items() if isinstance(v, str)}


def _ordered_allowed_source_fact_ids(
    runtime_payload: dict[str, Any], facts: list[dict[str, Any]]
) -> list[str]:
    raw = runtime_payload.get("allowed_fact_ids")
    if isinstance(raw, list) and raw:
        return [str(x) for x in raw]
    out: list[str] = []
    seen: set[str] = set()
    for fact in facts:
        fid = str(fact.get("fact_id") or "").strip()
        if fid and fid not in seen:
            seen.add(fid)
            out.append(fid)
    return out


def format_allowed_source_fact_ids_contract(allowed_ids: list[str]) -> str:
    """Pinned contract text: dynamic list + rules; spacing example matches orphan regressions."""
    lines = [
        "ALLOWED_SOURCE_FACT_IDS (authoritative list for every claim_ledger[].source_fact_ids entry):",
        "",
        "Rules:",
        "- Copy each ID character-for-character from the allowed lines below.",
        "- Do not invent, rewrite, normalize, split, merge, abbreviate, or approximate IDs.",
        "- Do not insert spaces or punctuation inside an ID (spacing drift fails coverage).",
        "- Every string in source_fact_ids MUST be exactly one of the allowed IDs below.",
        "- Tokens not in this list are orphan IDs: they fail deterministic gate x2_claim_ledger_orphan_zero and X3 stays BLOCK (not ALLOW).",
        "- Every claim_ledger row must include non-empty claim_text (material prose); rows with only source_fact_ids fail x2_claim_ledger_claim_text_non_empty.",
        "",
        "Spacing drift example (pattern only; your tokens are the allowed list):",
        '- INVALID: "bul_unify_ 003"  # space inside token',
        '- VALID when listed below: "bul_unify_003"  # exact copy from ALLOWED_SOURCE_FACT_IDS',
        "",
        "Allowed IDs:",
    ]
    for i in allowed_ids:
        lines.append(f"  - {i}")
    return "\n".join(lines)


def format_srfs_role_adaptive_appendix(srfs_integration: dict[str, Any]) -> str:
    """Prompt-only rules when a SelectedRoleFactSet artifact supplies the exec proof pool."""
    ids = srfs_integration.get("executive_summary_selected_fact_ids") or []
    n_blk = srfs_integration.get("blocked_facts_count")
    n_conf = srfs_integration.get("facts_requiring_human_confirmation_count")
    n_ujd = srfs_integration.get("unsupported_jd_needs_count")
    art = srfs_integration.get("artifact_path_resolved")
    sid = srfs_integration.get("selection_id")
    id_tail = ", ".join(str(x) for x in ids[:12])
    if len(ids) > 12:
        id_tail += ", …"
    return (
        "SELECTED_ROLE_FACT_SET_APPENDIX:\n"
        f"- Artifact: {art}\n"
        f"- selection_id: {sid}\n"
        f"- HIGH proof pool candidate_fact_ids (executive_summary slice only): [{id_tail}]\n"
        f"- Counts - blocked_facts: {n_blk}; facts_requiring_human_confirmation: {n_conf}; unsupported_jd_needs: {n_ujd}\n"
        "- These candidate_fact_ids are the ONLY allowable proof identifiers for substantive executive_summary claims; "
        "each claim_ledger row must cite concrete values from ALLOWED_SOURCE_FACT_IDS (verbatim).\n"
        "- JD_TEXT and BRIEFING_RESEARCH remain targeting/context inputs only - never citations, never proof substrates; "
        "jd_alignment jd_used_as_proof must remain false.\n"
        "- Unsupported JD themes listed in this artifact MUST be omitted from resume_display_text; do not fabricate JD-only needs.\n"
        "- MEDIUM, LOW, and NEEDS_VERIFICATION ledger rows excluded from ALLOWED_SOURCE_FACT_IDS MUST NOT appear in "
        "source_fact_ids unless the artifact was regenerated after explicit human confirmation and promotion.\n"
        "- Numeric evidence must still map to ledger metric-hash IDs when ALLOWED_SOURCE_FACT_IDS includes *_metric_* lines.\n"
    )


SRFS_STYLE_ONESHOT_MARKER = "SRFS_BASE_RESUME_STYLE_ONESHOT_V1"
# Legacy prompt contract marker (superseded in SRFS appendix by five-part architecture).
SRFS_THREE_SENTENCE_EXEC_ARCH_MARKER = "SRFS_THREE_SENTENCE_EXEC_ARCH_V1"
SRFS_FIVE_PART_EXEC_ARCH_MARKER = "SRFS_FIVE_PART_EXEC_ARCH_V1"
# Sentence responsibility separation - five-part SRFS arc (prompt contract marker).
SRFS_SENTENCE_RESP_SEP_MARKER = "SRFS_SENTENCE_RESP_SEP_V1"
SRFS_FORBIDDEN_PHRASE_CONTRACT_MARKER = "SRFS_FORBIDDEN_PHRASE_CONTRACT_V1"

# W4C: global resume_display_text bans (prompt contract; judge_safe may also strip at repair).
SRFS_FORBIDDEN_PHRASES_ALWAYS: tuple[str, ...] = (
    "applied depth",
    "documented credential training",
    "quantitative methods training",
    "distributed systems training",
    "fully autonomous production agents",
    "self-learning runtime",
    "autonomous AGI without oversight",
    "unsupervised production agents",
)


def format_srfs_forbidden_phrase_guardrails_block() -> str:
    """SRFS-only: explicit banned phrases + fact-supported exceptions for GraphRAG/partner engineering."""
    always = ", ".join(SRFS_FORBIDDEN_PHRASES_ALWAYS)
    return (
        f'<srfs_forbidden_phrase_contract marker="{SRFS_FORBIDDEN_PHRASE_CONTRACT_MARKER}">\n'
        "**Global forbidden phrases (never emit in resume_display_text):**\n"
        f"- {always}.\n"
        "- **Unsupported GraphRAG claims:** Do not introduce GraphRAG, graph-aware retrieval, or Graph-RAG "
        "vocabulary unless **verbatim** in a selected fact claim_text for an ALLOWED_SOURCE_FACT_ID. When the "
        "allowed claim_text includes GraphRAG or graph-aware retrieval, use **only** that fact-supported wording; "
        "do not extrapolate beyond the proved claim line.\n"
        "- **Unsupported partner engineering claims:** Do not introduce partner engineering, co-sell, ISV alliance, "
        "or partner GTM vocabulary unless a selected ALLOWED_SOURCE_FACT_ID claim_text **explicitly** supports "
        "partner / alliance / GTM substance. Do not infer partner engineering from JD_TEXT or BRIEFING alone.\n"
        "- **JD/briefing non-proof:** JD_TEXT and BRIEFING are targeting-only; they **cannot** authorize GraphRAG, "
        "partner engineering, autonomous runtime, or credential-training claims without matching proof IDs.\n"
        "- **Preserve allowed fact text:** When claim_text for an ALLOWED_SOURCE_FACT_ID includes GraphRAG or partner "
        "terms, you may reuse that exact vocabulary in prose tied to that fact_id; ban **unsupported extrapolation**, "
        "not verbatim allowed-fact wording.\n"
        "</srfs_forbidden_phrase_contract>\n\n"
    )


# Base-resume executive summary: style / density target only for SRFS appendix reinforcement (NOT runtime proof).
SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR = (
    "Engineering executive building production-grade AI platforms and the runtime architecture that makes autonomous "
    "systems usable in regulated enterprise environments. Designs and operates governed AI systems that combine "
    "deterministic routing, multi-agent orchestration, graph-aware retrieval, sandboxed execution, policy enforcement, "
    "replayable traces, evaluation discipline, and human escalation controls to improve reliability, auditability, and "
    "deployment speed. Leads the full platform lifecycle across architecture, operating model, engineering scale-out, "
    "and commercialization, converting bespoke delivery into reusable platform services adopted across enterprise "
    "programs. Generated $22M in productized AI revenue, expanded gross margins by 20%, reclaimed $14M in operating "
    "capacity, and reduced deployment cycles by turning complex AI capabilities into repeatable, production-ready "
    "infrastructure. Fellow of the Society of Actuaries with advanced training in causal inference, statistics, and "
    "distributed systems engineering."
)


def format_srfs_style_only_quality_oneshot_block() -> str:
    """SRFS-only: style + density/structure exemplar; never proof. Facts from ALLOWED_SOURCE_FACT_IDS only."""
    ex = SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR
    return (
        f'<srfs_style_only_oneshot marker="{SRFS_STYLE_ONESHOT_MARKER}">\n'
        "STYLE_ONLY_NOT_PROOF - SelectedRoleFactSet reinforcement block.\n"
        "- The boxed **exemplar_paragraph** teaches **density, structure, synthesis quality, executive voice**, and "
        "**five-part causal narrative** - it is a **density/structure target**, not a proof substrate.\n"
        "- **It is not a proof source.** Do not copy facts, metrics, credentials, tools, platforms, or claims from it "
        "unless the **same substance** is present in ALLOWED_SOURCE_FACT_IDS for **this** run "
        "(e.g. do not emit **$14M operating capacity**, sandboxed execution, or other exemplar-only lines unless those "
        "exact claims are proved by this run's IDs).\n"
        "- In SRFS mode do **not** use the canonical base-resume top-N fact plan as proof; "
        "**selected_facts_by_section[\"executive_summary\"]** HIGH facts carried in C0 / ALLOWED_SOURCE_FACT_IDS "
        "(plus allowed *_metric_* hash lines) are the **sole** substantive proof pool.\n"
        "- JD_TEXT and BRIEFING remain **targeting-only** (emphasis, order, vocabulary tilt); they never prove capability "
        "and must never appear as claim evidence.\n\n"
        "<srfs_allowed_fact_aware_density STYLE_ONLY_NOT_PROOF>\n"
        "**Allowed-fact-aware density (SRFS):**\n"
        "- Use **all high-value selected facts** that sharpen executive signal (governance, platform lifecycle, "
        "commercialization, credentials) when IDs are present and relevant.\n"
        "- **Do not omit** a selected governance, platform lifecycle, commercialization, or credential fact when it would "
        "materially strengthen truthfulness - if you skip one for tension with other facts, record it in **gap_notes** "
        "or **`self_check.sentence_roles_omitted_with_reason`**.\n"
        "- If the exemplar mentions a claim **not** in ALLOWED_SOURCE_FACT_IDS, treat it as **forbidden to copy**.\n"
        "- If the selected pool cannot honestly support **95+ words** without padding or invention, keep the paragraph "
        "truthful and set **`self_check.selected_fact_pool_too_small=true`** with a non-empty "
        "**`self_check.selected_fact_pool_too_small_reason`** (Deterministic gate **`x2_exec_summary_srfs_density_word_count`** "
        "excuses sub-95 only when both fields are set).\n"
        "</srfs_allowed_fact_aware_density>\n\n"
        "<srfs_anti_thinness STYLE_ONLY_NOT_PROOF>\n"
        "**Anti-thinness (SRFS) - forbidden patterns:**\n"
        "- Thin **50–70 word** abstracts or **compressed three-sentence** résumé summaries.\n"
        "- Stripping mechanisms or governance depth **only** to stay syntactically safe.\n"
        "- **Isolated credential tails** (a sentence that is only a credential list) or **metric-only proof chains** that "
        "drop platform context.\n"
        "- **Over-compression** of platform, governance, commercialization, and leadership arcs into **one** sentence.\n"
        "</srfs_anti_thinness>\n\n"
        + format_srfs_forbidden_phrase_guardrails_block()
        + f'<srfs_five_part_exec_architecture marker="{SRFS_FIVE_PART_EXEC_ARCH_MARKER}">\n'
        f'<srfs_sentence_responsibility_separation marker="{SRFS_SENTENCE_RESP_SEP_MARKER}">\n'
        "**SRFS five-part executive arc (exactly **four or five** period-delimited sentences; prefer **five**):**\n\n"
        "**Density contract (SRFS):** target **105–145 words** in `resume_display_text`; **hard minimum 95**, "
        "**hard maximum 160**. Aim for **comparable depth** to the **exemplar_paragraph** - not a short abstract. "
        "Deterministic gates: **`x2_exec_summary_srfs_sentence_count_4_5`**, **`x2_exec_summary_srfs_density_word_count`**, "
        "**`x2_exec_summary_srfs_sentence_responsibility_shape`**.\n\n"
        "**Sentence 1 - executive thesis (production-grade / governed AI platform; regulated enterprise when supported):**\n"
        "- Thesis + positioning **only**; **no metrics** (no digits, **$**, **%**).\n"
        "- Same structural bans as before: no mechanism/outcome bridges in S1 (`integrating`, `combining`, `using`, "
        "`through`, `while`, `by`, `to improve`, `to reduce`, `to streamline`, or stack nouns `microservices` / `HPC` / "
        "`vector services` / `routing` / `orchestration` / `retrieval` / `pipelines`).\n\n"
        "**Sentence 2 - platform / architecture mechanics (ALLOWED_SOURCE_FACT_IDS vocabulary only):**\n"
        "- Use **only** mechanism language present in selected facts (e.g. cloud-native microservices, AWS, "
        "Databricks, data pipelines, vector services, API gateways, identity controls, containerized microservices, "
        "HPC workflows, automated validation frameworks, Basel III / CCAR lineage).\n"
        "- **Forbidden unless verbatim in a selected fact claim_text:** deterministic routing, multi-agent "
        "orchestration, graph-aware retrieval, GraphRAG, sandboxed execution, replayable traces (see "
        f"``{SRFS_FORBIDDEN_PHRASE_CONTRACT_MARKER}`` for unsupported GraphRAG extrapolation).\n"
        "- **Must not include:** revenue, margin, dollars, org-scale spans, or credential nouns in this lane.\n\n"
        "**Sentence 3 - platform lifecycle / operating model / commercialization bridge:**\n"
        "- Connect architecture to **reusable services**, adoption, enterprise programs, or operating model **without** "
        "dropping commercial **metrics** here (keep **$ / revenue / margin / headcount spans** for Sentence 4).\n"
        "- **No** credential inventory in Sentence 3.\n\n"
        "**Sentence 4 - measurable outcomes:**\n"
        "- Commercial, margin, team-scale, latency, deployment-cycle, or capacity metrics **when supported**; group "
        "related metrics instead of dumping every number into one chain.\n"
        "- **Metric wording must match the fact lines:** use the same revenue or capacity phrasing as `metric_raw` / "
        "claim_text (e.g. **IP-led revenue**). Do **not** substitute exemplar-only labels such as **`productized AI "
        "revenue`** when that contiguous phrase is absent from the selected fact blob "
        "(gate **`x2_north_star_style_echo_unsupported_zero`**).\n"
        "- **Must not begin** with `Fellow of`, `Holds`, `Certified`, or `Credentials`.\n\n"
        "**Sentence 5 - integrated credibility clause (omit sentence 5 only when merging into Sentence 4 with honest "
        "4-sentence justification in self_check):**\n"
        "- **Write an integrated credibility clause**, not a bare cert list: **bring** AWS / Databricks / FSA (or other "
        "proved tokens) into governed AI platform leadership, balancing engineering execution, governance, and "
        "commercialization when those themes appear in ALLOWED_SOURCE_FACT_IDS - **do not** invent training domains.\n"
        "- **Forbidden phrases:** applied depth, documented credential training, quantitative methods training, "
        "distributed systems training, credentialed foundation strength, platform record above, record above "
        f"(full list in ``{SRFS_FORBIDDEN_PHRASE_CONTRACT_MARKER}``).\n"
        "- **Preferred shape (when fact_certs_001 is in the pool):** weave AWS / Databricks / FSA (and FSA "
        "actuarial rigor when the cert fact mentions Fellow of the Society of Actuaries) into governance and "
        "commercialization balance; **do not** name causal inference, statistics, quantitative methods training, "
        "or distributed systems training unless those tokens appear verbatim in fact_certs_001 claim_text.\n"
        "- **Must not start** with **`Holds`**, **`Holds certifications`**, or a **bare credential inventory** "
        "(comma-separated cert labels only).\n"
        "- `Fellow of ...` may appear **inside** Sentence 5 when proved, but avoid leading with a thin **Holds ...** opener.\n\n"
        "<srfs_suggested_target_shape STYLE_ONLY_NOT_PROOF>\n"
        "Illustrative **five-sentence** density layout (**not proof**; emit only clauses supported by "
        "ALLOWED_SOURCE_FACT_IDS):\n"
        "- S1: Engineering executive building governed agentic AI platforms for regulated enterprise environments "
        "(emit **agentic** only when ALLOWED_SOURCE_FACT_IDS include agentic AI substance).\n"
        "- S2: Designs cloud-native microservices across AWS and Databricks with data pipelines, vector services, API "
        "gateways, and automated validation frameworks that strengthen reliability and auditability (mechanism IDs only).\n"
        "- S3: Leads the full platform lifecycle across architecture, operating model, engineering scale-out, and "
        "commercialization, turning bespoke delivery into reusable platform services adopted across enterprise programs.\n"
        "- S4: Groups proof-backed revenue, margin, org-scale, and cycle-time outcomes consistent with metric facts in the "
        "allowed pool (do not invent $14M capacity unless proved).\n"
        "- S5 (integrated credibility): **Combines** proved AWS / Databricks / FSA credentials with platform/governance "
        "depth (causal inference, statistics, distributed systems when cert facts support); never meta **above** "
        "references, never a **Holds ...** inventory lead, never invented training domains.\n"
        "</srfs_suggested_target_shape>\n"
        f"</srfs_sentence_responsibility_separation>\n"
        "</srfs_five_part_exec_architecture>\n\n"
        f"<!-- Legacy marker retained for tooling continuity: {SRFS_THREE_SENTENCE_EXEC_ARCH_MARKER} (retired for SRFS). -->\n\n"
        + (
            "<srfs_hard_anti_chain STYLE_ONLY_NOT_PROOF>\n"
            "**Hard anti-chain (SRFS) - violation if any of these appear in ``resume_display_text``:**\n"
            "- ``while scaling`` / ``while generating`` / ``while expanding`` **gluing** architecture text to org or "
            "commercial outcomes.\n"
            "- **Sentence 2 or 3** naming **architecture / governance mechanics** together with **revenue, margin, "
            "team scale, $, or credentials** (move commercial metrics to Sentence 4; credentials to Sentence 5).\n"
            "- **Sentence 4** that **begins** with ``Fellow of``, ``Holds``, ``Certified``, or ``Credentials``.\n\n"
            "**Metric family cap (per sentence):** at most **two** of these **families** unless you state a **direct** "
            "causal link in-prose (same clause):\n"
            "1. **Technical performance** (latency, cycle time, deployment-cycle).\n"
            "2. **Commercial** (revenue, margin, operating capacity).\n"
            "3. **Organization** (team size / scale-out).\n"
            "4. **Credentials** (FSA, AWS, Databricks, education / training labels).\n"
            "Default: Sentences 2–3 stay in **technical + lifecycle** lanes; Sentence 4 uses **(1–3)**; Sentence 5 carries "
            "**(4)** without duplicating a metric dump.\n"
            "</srfs_hard_anti_chain>\n\n"
            "<srfs_style_contrast_chain_vs_split STYLE_ONLY_NOT_PROOF>\n"
            "**Compact style contrast (NOT PROOF; do not copy facts unless ALLOWED_SOURCE_FACT_IDS contains the same "
            "substance):**\n\n"
            "**Bad (overloaded chain - DO NOT EMIT):**\n"
            "Designed and operationalized architectures combining deterministic routing, multi-agent orchestration, and "
            "graph-aware retrieval to reduce deployment cycles and improve reliability, while scaling the ML engineering "
            "organization from 8 to 28 specialists and generating $22M in IP-led revenue, expanding gross margins by 20%.\n\n"
            "**Good structure (split responsibility - map fragments across S2-S5):**\n"
            "Designed governed runtime architectures that combine deterministic routing, multi-agent orchestration, "
            "graph-aware retrieval, validation controls, and traceability to improve reliability and shorten the path from AI "
            "capability to production use. Leads lifecycle commercialization, converting primitives into reusable services "
            "adopted across enterprise programs. Pairs engineering scale-out with proof-backed revenue and margin outcomes in "
            "a dedicated outcomes sentence. Closes with subordinated credibility clauses only when IDs support them.\n"
            "- **SelectedRoleFactSet** remains the **sole** proof pool; JD/briefing stay **targeting-only**.\n"
            "</srfs_style_contrast_chain_vs_split>\n\n"
            "<srfs_anti_metric_chain>\n"
            "**Anti metric-chain (SRFS):** one sentence must not concatenate unrelated outcomes without a causal bridge "
            "**or** mix forbidden families per ``srfs_hard_anti_chain``.\n"
            "**Forbidden shapes (illustrative):**\n"
            "- ``Led X that reduced A, enabled B, and generated C, expanding D.``\n"
            "- ``Architected X, reducing Y, while leading Z, generating A, and expanding B.``\n"
            "</srfs_anti_metric_chain>\n\n"
            "<srfs_credential_integration>\n"
            "If **fact_certs_001** (or equivalent creds fact) appears in ALLOWED_SOURCE_FACT_IDS and you use it:\n"
            "- Do **not** emit a **standalone credential inventory** sentence; integrate into **Sentence 5** (or merged "
            "Sentence 4) with delivery context.\n"
            "- Prefer an **integrated** credibility clause (pair creds with proved depth) over **Holds ...** / cert-label "
            "stacking.\n"
            "- **Forbidden openers** on **Sentence 4** include ``Fellow of``, ``Holds``, ``Certified``, ``Credentials``, "
            "and **`Holds certifications`**.\n"
            "- **Sentence 5** must not begin with **`Holds`** or **`Holds certifications`** or lead with a bare cert list.\n"
            "- If credentials do not improve the SVP narrative, **omit** them from ``resume_display_text`` and explain "
            "briefly in ``self_check.sentence_roles_omitted_with_reason`` (no JD/briefing as proof).\n"
            "</srfs_credential_integration>\n\n"
            "<srfs_governance_required_or_explain>\n"
            "**Governance: cite or document omission (SRFS):**\n"
            "- **Governance-class fact** means a selected HIGH executive_summary row whose ``fact_id`` or ``claim_text`` "
            "signals **governance, risk, regulated, auditability, compliance, lineage, validation, CCAR, Basel, reporting "
            "integrity**, or similar (e.g. ``fact_governance_003`` when it appears in ALLOWED_SOURCE_FACT_IDS).\n"
            "- **Targeting trigger:** JD_TEXT and/or BRIEFING (targeting only, not proof) mention **governance, regulated, "
            "audit, compliance, reliability, lineage, validation**, or **AI governance** for enterprise delivery.\n"
            "- When **both** a governance-class fact is in ALLOWED_SOURCE_FACT_IDS **and** the targeting trigger applies: "
            "**you must cite at least one such governance-class fact_id in ``claim_ledger``** and materialize it in "
            "``resume_display_text`` with correct IDs.\n"
            "- **If you intentionally omit** it (rare; only when it would contradict selected facts or break truth): add "
            "a compact **gap_notes** entry (e.g. ``srfs_governance_fact_unused: <fact_id> reason: <one line>``) **and** set "
            "``self_check.srfs_governance_omission_explained`` to **true** with ``self_check.srfs_governance_omission_reason`` "
            "as a short token string. Do **not** cite JD/briefing text as proof for the omission.\n"
            "- If **no** governance-class ID exists in ALLOWED_SOURCE_FACT_IDS, do **not** invent governance; this rule does "
            "not apply.\n"
            "- Do **not** use MEDIUM / LOW / NEEDS_VERIFICATION facts; only IDs listed under ALLOWED_SOURCE_FACT_IDS.\n"
            "</srfs_governance_required_or_explain>\n\n"
            "<exemplar_paragraph>\n"
            f"{ex}\n"
            "</exemplar_paragraph>\n\n"
            "<svp_quality_bar>\n"
            "- Match this exemplar's **quality bar plus executive density**, not its exact facts.\n"
            "- Do **not** open with generic phrasing like ``Engineering executive with expertise in...``; start with a "
            "differentiated thesis supported by selected facts.\n"
            "- Weave platform architecture, governance/reliability, lifecycle bridge, measurable outcomes, and credibility "
            "across the **4–5 sentence** SRFS arc.\n"
            "- Do **not** stack metrics as a proof list; do **not** use proof-list prose.\n"
            "- Do **not** use ``while`` or comma chains to glue unrelated facts (e.g. ``Architected X, reducing Y, while "
            "leading Z, generating A, and expanding B``).\n"
            "- **Four or five** dense sentences with **strict separation** per ``srfs_sentence_responsibility_separation``; "
            "external-facing resume voice: concise, human, credible, executive.\n"
            "- Forbidden generic recruiter phrases include **expertise in** (as thin opener framing), **proven track "
            "record**, **results-driven**, **seasoned leader** (plus I0 FORBIDDEN_OPENERS).\n"
            "</svp_quality_bar>\n"
            "</srfs_style_only_oneshot>\n"
        )
    )


def format_selected_facts_for_c0(facts: list[dict[str, Any]], allowed_source_fact_ids: list[str]) -> str:
    header = format_allowed_source_fact_ids_contract(allowed_source_fact_ids)
    lines: list[str] = []
    for fact in facts:
        fid = fact.get("fact_id", "")
        ct = str(fact.get("claim_text") or "").strip()
        extra = ""
        if fact.get("metric_raw"):
            extra = f" metric_raw={fact.get('metric_raw')!r}"
        lines.append(f"- {fid}: {ct}{extra}")
    body = "SELECTED_FACT_PLAN (proof-only; do not invent beyond these lines):\n" + "\n".join(lines)
    return f"{header}\n\n{body}"


def build_executive_summary_assembly_input(
    runtime_payload: dict[str, Any],
    *,
    request_id: str,
    run_id: str,
    trace_root: str,
) -> PromptAssemblyInput:
    slots = load_executive_summary_template_slots()
    plan = runtime_payload.get("selected_fact_plan") or {}
    facts = list(plan.get("facts") or [])
    if not facts:
        raise ValueError("selected_fact_plan.facts is required for executive_summary PA input")

    t_title = str(runtime_payload.get("target_title") or "")
    t_company = str(runtime_payload.get("target_company") or "")
    jd = str(runtime_payload.get("jd_text") or "")
    briefing = str(runtime_payload.get("briefing") or "")

    jd_block = (
        f"TARGET_TITLE (positioning only  -  NOT PROOF): {t_title}\n"
        f"TARGET_COMPANY (positioning only  -  NOT PROOF): {t_company}\n"
        f"JD_TEXT (targeting only  -  rank/order/frame facts; NOT PROOF): {jd}\n"
        f"BRIEFING (targeting only  -  rank/order/frame facts; NOT PROOF): {briefing}\n"
        "Use TARGET_TITLE and TARGET_COMPANY for positioning toward the reader. "
        "Use JD_TEXT and BRIEFING only to rank, order, and frame selected facts in resume_display_text: "
        "which themes lead, how vocabulary tilts toward the target, and what stays implicit. "
        "Never treat JD_TEXT, BRIEFING, titles, or company as proof of capability.\n"
        "Do not mirror JD phrasing, paste JD lists, or keyword-stuff. Paraphrase sparingly into the dense, "
        "concrete register of the canonical base résumé (stack and governance nouns from selected facts).\n"
        "Every substantive claim must trace to C0 selected facts; jd_alignment must state jd_used_as_proof=false."
    )
    srfs = runtime_payload.get("srfs_integration")
    if isinstance(srfs, dict) and srfs:
        jd_block += (
            "\nSelectedRoleFactSet mode: substantive claims cite ONLY ALLOWED_SOURCE_FACT_IDS from the HIGH "
            "executive_summary slice embedded in SELECTED_ROLE_FACT_SET_APPENDIX plus this block; "
            "JD/briefing are never proof; unsupported JD necessities from the artifact are omitted from prose."
        )

    allowed_ids = _ordered_allowed_source_fact_ids(runtime_payload, facts)
    if not allowed_ids:
        raise ValueError("allowed_fact_ids or non-empty fact_id on each selected fact is required for executive_summary PA")

    u0 = (
        f"Generate executive summary for target title: {t_title!r}. "
        f"Target company (positioning only, never as employer proof): {t_company!r}.\n"
        "Use ONLY facts listed under <selected_facts> in C0 (proof substrate: SELECTED_FACT_PLAN lines + "
        "ALLOWED_SOURCE_FACT_IDS). "
        "Use JD_TEXT + BRIEFING in the jd_requirements block for **targeting context** only: prioritization, ordering, "
        "and vocabulary tilt among those facts - never to add employers, metrics, or uncited claims.\n"
        "Return RAW JSON only (object). First character `{`; last character `}` on the top-level object.\n"
        "begin with { and end with } (bare JSON only, no markdown fences).\n"
        "No ```json or ``` markdown fences around the object.\n"
        "resume_display_text: default **2 or 3** dense executive sentences (period-delimited). "
        "Synthesize across **sentence role goals**: "
        "(1) executive identity and operating domain; "
        "(2) governed runtime / platform / autonomous systems capability; "
        "(3) platform lifecycle, operating model, engineering scale-out, or commercialization; "
        "(4) quantified business, reliability, capacity, margin, revenue, adoption, or deployment impact; "
        "(5) credential or analytic depth only when directly supported by selected facts. "
        "Combine roles when facts are thin; split when a sentence becomes a comma-heavy capability list; "
        "**never** one sentence per source fact; **never** paste internal labels with colon+space; "
        "prefer polished executive narrative over bullet-by-bullet translation.\n"
        "**Do not** emit `selected_fact_plan` in JSON - runtime materializes selected_fact_plan.json.\n"
        "Internally compare supported narrative orderings; do not output chain-of-thought.\n"
        "resume_display_text: NO [source:…], NO raw fact_id tokens, NO bracket citations.\n"
        "claim_ledger: each row MUST have non-empty claim_text and source_fact_ids copied exactly from "
        "ALLOWED_SOURCE_FACT_IDS (candidate_fact_id strings plus any *_metric_* hash lines emitted there). "
        "Do not fabricate claim_text from JD, target title, target company, or briefing.\n"
        "Match canonical base-résumé register: third person, engineering executive density.\n"
        "jd_alignment must state jd_used_as_proof=false.\n"
        "Emit compact JSON: finish the object with a valid closing `}`; keep self_check to the required boolean/token "
        "fields from I0 only (no long prose, no repeated claim paragraphs).\n"
    )
    srfs_patch = ""
    if isinstance(srfs, dict) and srfs:
        srfs_patch = (
            "\nROLE-ADAPTIVE SRFS HARD RULES: JD_TEXT/BRIEFING are targeting-only framing; NEVER list them "
            "(or surrogate targeting tokens such as standalone JD_/BRIEFING_ placeholders) "
            "inside claim_ledger source_fact_ids. Every ID must exactly match ALLOWED_SOURCE_FACT_IDS from SelectedRoleFactSet.\n"
        )
    return PromptAssemblyInput(
        template_id="strategic_tailor_v1",
        request_id=request_id,
        run_id=run_id,
        trace_root=trace_root,
        s0_system_preamble=slots.get("S0", ""),
        d0_fences=slots.get("D0"),
        i0_instructions=slots.get("I0", ""),
        e0_examples=slots.get("E0"),
        y0_style_preferences=slots.get("Y0"),
        c0_candidate_facts=EvidenceSource(
            source_type="selected_facts",
            content=format_selected_facts_for_c0(facts, allowed_ids),
            confidence=1.0,
            source_tag="selected_facts",
        ),
        c0_jd_requirements=EvidenceSource(
            source_type="jd_requirements",
            content=jd_block,
            confidence=0.0,
            source_tag="jd_requirements",
        ),
        u0_user_task=u0 + srfs_patch,
        r0_response_schema=_EXEC_SUMMARY_OUTPUT_SCHEMA_JSON,
        render_context={
            "target_title": t_title,
            "target_company": t_company,
            "section_id": "executive_summary",
        },
    )


def compile_executive_summary_prompt(runtime_payload: dict[str, Any], *, run_id: str) -> SectionCompiledPrompt:
    assembly = build_executive_summary_assembly_input(
        runtime_payload,
        request_id=run_id,
        run_id=run_id,
        trace_root=f"exec_summary:{run_id}",
    )
    compiled = compile_section_prompt(assembly, section_id="executive_summary")
    ids = list(runtime_payload.get("allowed_fact_ids") or [])
    pp = runtime_payload.get("proof_pool_metadata") or {}
    pool_type = str(pp.get("proof_pool_type") or "")
    srfs = runtime_payload.get("srfs_integration")
    if pool_type == "selected_role_fact_set":
        proof_pool_mode = "srfs"
        srfs_mode = True
    elif pool_type == "broad_skills_ledger":
        proof_pool_mode = "broad_skills_ledger"
        srfs_mode = False
    else:
        proof_pool_mode = "base_resume_fallback"
        srfs_mode = isinstance(srfs, dict) and bool(srfs.get("artifact_path_resolved"))
    compiled = augment_section_compiled_with_input_authority(
        compiled,
        allowed_source_fact_ids=ids,
        selected_role_fact_set_mode=srfs_mode,
        proof_pool_mode=proof_pool_mode,
        skills_authority_metadata=pp if isinstance(pp, dict) else None,
    )
    if srfs_mode:
        appendix = format_srfs_role_adaptive_appendix(srfs)
        style_oneshot = format_srfs_style_only_quality_oneshot_block()
        art = compiled.artifact
        msgs = [dict(m) for m in art.messages]
        if msgs:
            last = msgs[-1]
            content = str(last.get("content") or "").rstrip()
            last["content"] = f"{content}\n\n{appendix}\n\n{style_oneshot}".rstrip() + "\n"
            msgs[-1] = last
        compiled = SectionCompiledPrompt(
            section_id=compiled.section_id,
            apps_rg_prompt_template_ref=compiled.apps_rg_prompt_template_ref,
            artifact=replace(art, messages=msgs),
        )
    return compiled


__all__ = [
    "SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR",
    "SRFS_FORBIDDEN_PHRASE_CONTRACT_MARKER",
    "SRFS_FORBIDDEN_PHRASES_ALWAYS",
    "SRFS_STYLE_ONESHOT_MARKER",
    "SRFS_THREE_SENTENCE_EXEC_ARCH_MARKER",
    "SRFS_SENTENCE_RESP_SEP_MARKER",
    "build_executive_summary_assembly_input",
    "compile_executive_summary_prompt",
    "format_srfs_forbidden_phrase_guardrails_block",
    "format_srfs_role_adaptive_appendix",
    "format_srfs_style_only_quality_oneshot_block",
    "load_executive_summary_template_slots",
]
