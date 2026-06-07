"""Bank-Grade Servicing AI Worker — Fee-Adjustment Review (case walkthrough UI).

A reference implementation of an agentic control plane. One LLM-backed worker
proposes; a deterministic control plane disposes; only the write gate can persist.

    The model proposes; the deterministic control plane disposes.
    The agent is the least-trusted component in the system.

Write law: L2 executes and seals (inert proposed_state_diff only). Exit emits one
X3. UWG validates and commits. L4 stores. HITL is an Exit disposition, not a model
action. UNKNOWN is never PASS.

Run:  streamlit run app.py
"""

from __future__ import annotations

import json
import pathlib
import sys

import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from src.runtime import (  # noqa: E402
    REVIEWER_DECISIONS,
    SCENARIOS,
    WriteGateError,
    commit_run,
    get_scenario,
    read_all,
    run_workflow,
)
from src.runtime.contracts import to_jsonable  # noqa: E402
from src.runtime.eval_suite import run_eval  # noqa: E402

THESIS = (
    "The model proposes; the deterministic control plane disposes. "
    "The agent is the least-trusted component in the system."
)
WRITE_LAW = (
    "L2 executes and seals. If a state change is possible, L2 emits only an inert "
    "proposed_state_diff. Exit decides whether that becomes a CommitRequest. UWG "
    "validates and commits. L4 stores."
)

_VERDICT_COLORS = {
    "PASS": "#1b7f4b", "STOP": "#b00020", "ESCALATE": "#b8730b",
    "ABSTAIN": "#1f5fb0", "REROUTE": "#6a1b9a", "UNKNOWN": "#b00020",
}

# Demo-oriented hero scenarios only. D/E injection cases live in the eval suite.
HERO = ["A", "B", "C"]

SCREENS = [
    "Overview",
    "Case & Evidence",
    "Live Worker Decision (L2)",
    "Exit Disposition (the gate)",
    "HITL Review",
    "Write Gate & Ledger",
    "Audit / Replay",
    "Eval Suite",
    "Architecture (v40)",
]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def badge(verdict: str) -> str:
    color = _VERDICT_COLORS.get(verdict, "#444")
    return (
        f"<span style='background:{color};color:#fff;padding:2px 10px;"
        f"border-radius:10px;font-size:0.80rem;font-weight:600'>{verdict}</span>"
    )


def get_trace():
    return run_workflow(
        st.session_state.scenario_id, st.session_state.get("reviewer_decision")
    )


# --------------------------------------------------------------------------- #
# Screens
# --------------------------------------------------------------------------- #
def screen_overview(trace) -> None:
    st.title("Bank-Grade Servicing AI Worker")
    st.subheader("Complaint-Sensitive Fee Adjustment Review")
    st.success(THESIS)
    st.markdown(
        "A reference implementation of an **agentic control plane** for bank "
        "servicing. A bounded LLM worker reviews a fee-adjustment request and "
        "**recommends**; a deterministic, auditable control plane **decides**; and "
        "only a validated write gate can change durable state."
    )
    st.info(
        "Reference implementation with synthetic data and a **local** model "
        "(Qwen2.5-32B via vLLM, on-prem). No real customer data, no external "
        "services, no system-of-record integration."
    )
    c1, c2, c3 = st.columns(3)
    c1.markdown("**The model**\n\nOne call, at L2. Proposes only. Least-trusted.")
    c2.markdown("**The gates**\n\nDeterministic. Derive the disposition from evidence, not the model's word.")
    c3.markdown("**The write**\n\nOne path (UWG). Refuses without an approved commit. Fail-closed.")
    st.markdown("---")
    st.markdown(
        "**Model risk management (SR 11-7) mapping** — the LLM is *a model* under "
        "MRM; the deterministic gates are the *controls* around it. The replayable "
        "trace is audit/dispute evidence. HITL is structural. UNKNOWN is never PASS."
    )
    st.caption("Use the sidebar to pick a scenario and walk the case end to end.")


def screen_case(trace) -> None:
    scn = get_scenario(trace.scenario_id)
    st.title("Case & Evidence")
    st.markdown(f"**{scn.title}** — {scn.one_liner}")
    st.markdown("**Customer message (DATA — never authority):**")
    st.info(scn.customer_message)

    st.subheader("C0 evidence custody")
    custody = trace.c0_custody_sequence
    st.caption("Deterministic custody sequence: " + " → ".join(f"`{p}`" for p in custody["pipeline"]))
    header = [
        "source_id", "acl_status", "freshness", "quality_state",
        "contradiction_status", "authority_level", "in_final_packet",
        "can_support_write", "exclusion_reason",
    ]
    rows = [
        {
            "source_id": c["source_id"], "acl_status": c["acl_status"],
            "freshness": c["freshness"], "quality_state": c["quality_state"],
            "contradiction_status": c["contradiction_status"],
            "authority_level": c["authority_level"],
            "in_final_packet": c["included_in_final_packet"],
            "can_support_write": c["can_support_write"],
            "exclusion_reason": c["exclusion_reason"] or "—",
        }
        for c in custody["candidates"]
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True, column_order=header)
    st.markdown(f"**Support classification:** `{custody['support_classification']}`")
    if custody["conflicted_sources"]:
        st.warning(f"Conflicted sources: {', '.join(custody['conflicted_sources'])}")

    st.subheader("Prompt / data boundary")
    pb = trace.prompt_boundary_check
    c1, c2 = st.columns(2)
    c1.markdown("**DATA (informs only)**\n\n" + "\n".join(f"- {x}" for x in pb["data"]))
    c2.markdown("**AUTHORITY (governs)**\n\n" + "\n".join(f"- {x}" for x in pb["authority"]))
    st.caption(pb["rule"])


def screen_worker(trace) -> None:
    st.title("Live Worker Decision (L2)")
    st.caption("The ONE model call in the system. It recommends; it cannot commit.")
    dec = trace.l2_agent_decision or {}
    prov = dec.get("provenance", {})

    c1, c2, c3 = st.columns(3)
    c1.metric("recommendation", dec.get("recommendation") or "UNKNOWN")
    c2.metric("source", prov.get("source", "—"))
    c3.metric("latency", f"{prov.get('latency_ms','—')} ms")
    usage = prov.get("usage") or {}
    st.caption(
        f"model `{prov.get('model','—')}` · prompt_tokens "
        f"{usage.get('prompt_tokens','—')} · completion_tokens "
        f"{usage.get('completion_tokens','—')} · prompt_hash `{prov.get('prompt_hash','—')}`"
    )
    st.markdown(f"**Worker rationale (model):** {dec.get('rationale','')}")

    st.subheader("Model vs. gate (the gate is authoritative)")
    mga = trace.model_gate_agreement or {}
    cols = st.columns(3)
    cols[0].markdown(f"**Model says**\n\n`{mga.get('model_bucket')}`")
    cols[1].markdown(f"**Gate requires**\n\n`{mga.get('gate_expectation')}`")
    agree = mga.get("agreement")
    cols[2].markdown(f"**Agreement**\n\n{'✅ aligned' if agree else '⚠️ overridden by gate'}")
    if not agree:
        st.warning(
            "Model and gate disagree (or the model is UNKNOWN). The deterministic "
            "gate decides regardless — a wrong or failed model never changes the outcome."
        )
    st.caption(mga.get("note", ""))
    with st.expander("Full model decision (recorded for replay)"):
        st.json(dec)


def screen_exit(trace) -> None:
    st.title("Exit Disposition (the deterministic gate)")
    st.caption("Exit computes ONE X3 from deterministic checks over the evidence — "
               "not from the model's word, not from a hardcoded branch.")
    all_x3 = [
        "X3A_DENY_REROUTE", "X3B_ESCALATE_HITL", "X3C_COMMIT_REQUEST_TO_UWG",
        "X3D_ALLOW_FINISH", "X3E_SAFE_ABSTAIN",
    ]
    emitted = {e["x3"] for e in trace.exit_disposition_history}
    st.markdown("\n".join(f"{'✅' if x in emitted else '▫️'} `{x}`" for x in all_x3))
    st.markdown("---")
    for e in trace.exit_disposition_history:
        st.markdown(
            f"#### [{e['evaluation']}] → `{e['x3']}` {badge(e['gate_verdict'])}",
            unsafe_allow_html=True,
        )
        st.caption(e["reason"])
        ec = e["exit_checks"]
        st.dataframe(
            [{"check": k, "value": v} for k, v in ec["checks"].items()],
            use_container_width=True, hide_index=True,
        )
        st.markdown("---")
    st.markdown(f"**Final disposition:** `{trace.final_exit}`")


def screen_hitl(trace) -> None:
    st.title("HITL Review")
    st.warning("HITL is an Exit disposition, not a model action.")
    if trace.scenario_id != "B":
        st.info("Only the complaint-sensitive case (B) escalates to a human reviewer.")
        return
    if not trace.hitl_review_packet:
        st.info("No human_review_packet prepared for this run.")
        return
    st.subheader("Reviewer packet")
    st.json(trace.hitl_review_packet)
    st.subheader("Reviewer decision")
    if trace.reviewer_decision:
        st.success(
            f"Decision: **{trace.reviewer_decision.decision}** "
            f"(reason `{trace.reviewer_decision.reason_code}`)"
        )
        if st.button("Clear decision (re-open HITL)"):
            st.session_state.reviewer_decision = None
            st.rerun()
        st.caption("After the reviewer acts, Exit re-runs (re-clearance) deterministically.")
    else:
        cols = st.columns(2)
        for i, (key, label) in enumerate(REVIEWER_DECISIONS.items()):
            if cols[i % 2].button(label, key=f"rvw_{key}"):
                st.session_state.reviewer_decision = key
                st.rerun()


def screen_uwg(trace) -> None:
    st.title("Write Gate & Durable Ledger")
    st.caption("UWG is the only path to a durable write. The write is physically gated.")
    if not trace.uwg_validation_result:
        st.info(
            "No CommitRequest — UWG was not entered. A durable write here is "
            "**refused** (fail-closed)."
        )
    else:
        st.markdown("**CommitRequest**")
        st.json(trace.commit_request)
        res = trace.uwg_validation_result
        st.dataframe(
            [{"check": k, "value": v} for k, v in res.checks.items()],
            use_container_width=True, hide_index=True,
        )
        if res.approved:
            st.success(f"UWG approved — {res.reason}")
        else:
            st.error(f"UWG blocked — {res.reason}")

    st.markdown("---")
    st.subheader("Durable write (real SQLite ledger)")
    if st.button("Attempt durable commit via UWG"):
        try:
            result = commit_run(trace)
            if result["inserted"]:
                st.success(f"Committed L4 record `{result['archive_id']}` to the ledger.")
            else:
                st.info(f"Already committed (idempotent): `{result['archive_id']}`.")
        except WriteGateError as exc:
            st.error(f"Write refused by the gate: {exc}")

    rows = read_all()
    st.markdown(f"**L4 archive ledger ({len(rows)} row(s)):**")
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.caption("Ledger is empty.")


def screen_audit(trace) -> None:
    st.title("Audit / Replay")
    st.caption("The full RunTrace. Replay reproduces the exact same trace.")
    c1, c2, c3 = st.columns(3)
    c1.metric("policy_hash", trace.policy_hash)
    c2.metric("prompt_hash", trace.prompt_hash)
    c3.metric("replay_key", trace.replay_key)
    if st.button("Replay this run"):
        replay = run_workflow(trace.scenario_id, st.session_state.get("reviewer_decision"))
        st.session_state["_replay_same"] = to_jsonable(replay) == to_jsonable(trace)
    if "_replay_same" in st.session_state:
        if st.session_state["_replay_same"]:
            st.success("Deterministic replay: reproduced the EXACT same trace.")
        else:
            st.error("Replay diverged — would violate determinism.")
    st.download_button(
        "Download RunTrace JSON",
        data=json.dumps(to_jsonable(trace), indent=2),
        file_name=f"runtrace_{trace.run_id}.json",
        mime="application/json",
    )
    with st.expander("Full RunTrace JSON"):
        st.json(to_jsonable(trace))


def screen_eval(trace) -> None:
    st.title("Eval Suite")
    st.caption("Golden set incl. prompt-injection. Defense-in-depth: model resists AND gate catches.")
    report = run_eval()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("passed", f"{report['passed']}/{report['total']}")
    c2.metric("durable writes", report["durable_writes"])
    c3.metric("injection caught (gate)", f"{report['injection_gate_caught']}/{report['injection_cases']}")
    c4.metric("injection resisted (model)", f"{report['injection_model_resisted']}/{report['injection_cases']}")
    rows = [
        {
            "case": r.case.case_id,
            "category": r.case.category,
            "final_exit": r.final_exit,
            "model": r.model_recommendation,
            "wrote": "yes" if r.wrote else "no",
            "pass": "PASS" if r.passed else "FAIL",
        }
        for r in report["results"]
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.markdown(
        f"Dispositions — commit `{report['auto_or_approved_commits']}` · "
        f"escalate `{report['escalations']}` · abstain `{report['abstains']}` · "
        f"deny `{report['denials']}`."
    )


def screen_arch(trace) -> None:
    st.title("Architecture (v40 spine)")
    st.success(WRITE_LAW)
    mapping = [
        ("U0", "validate fee-adjustment case"),
        ("L1", "frame ambiguity (hints, no route authority)"),
        ("L0", "deterministic fee_adjustment route"),
        ("C0", "evidence custody"),
        ("PA", "prompt/data boundary"),
        ("L2", "bounded MODEL worker — proposes only"),
        ("L2.E4", "same-authority schema repair only"),
        ("Exit", "one X3 disposition (deterministic)"),
        ("HITL", "Exit escalation path (human authority)"),
        ("UWG", "write validation — the only write path"),
        ("L4", "archive after UWG only"),
        ("L6", "post-run learning after boundary only"),
    ]
    for layer, desc in mapping:
        st.markdown(f"- **{layer}** — {desc}")
    st.markdown("---")
    st.error("Hard rule: UNKNOWN is never PASS.")
    st.markdown(
        "GateVerdicts: `PASS` · `STOP` · `ESCALATE` · `ABSTAIN` · `REROUTE` · `UNKNOWN`"
    )
    st.json(trace.gate_verdicts)


_RENDERERS = {
    "Overview": screen_overview,
    "Case & Evidence": screen_case,
    "Live Worker Decision (L2)": screen_worker,
    "Exit Disposition (the gate)": screen_exit,
    "HITL Review": screen_hitl,
    "Write Gate & Ledger": screen_uwg,
    "Audit / Replay": screen_audit,
    "Eval Suite": screen_eval,
    "Architecture (v40)": screen_arch,
}


def main() -> None:
    st.set_page_config(page_title="Bank-Grade Servicing AI Worker", layout="wide")
    if "scenario_id" not in st.session_state:
        st.session_state.scenario_id = "B"  # hero scenario
    if "reviewer_decision" not in st.session_state:
        st.session_state.reviewer_decision = None

    trace = get_trace()
    scn = get_scenario(trace.scenario_id)

    with st.sidebar:
        st.markdown("### Servicing AI Worker")
        st.caption("Reference implementation · synthetic data · local model")
        choice = st.radio(
            "Scenario",
            options=HERO,
            format_func=lambda s: f"{s} — {SCENARIOS[s].title.split('—')[1].strip()}",
            index=HERO.index(st.session_state.scenario_id),
        )
        if choice != st.session_state.scenario_id:
            st.session_state.scenario_id = choice
            st.session_state.reviewer_decision = None
            st.rerun()
        st.markdown("---")
        st.markdown(f"**Run:** `{trace.run_id}`")
        st.markdown(f"**Final X3:** `{trace.final_exit}`")
        st.markdown(f"**Durable write:** {'yes' if trace.l4_archive_record else 'no'}")
        mga = trace.model_gate_agreement or {}
        st.markdown(f"**Model vs gate:** {'aligned' if mga.get('agreement') else 'gate override'}")
        if trace.runtime_exhaust_bundle.get("awaiting_reviewer"):
            st.warning("Awaiting reviewer (HITL).")
        st.markdown("---")
        screen = st.radio("Screen", options=SCREENS, label_visibility="collapsed")

    st.caption(
        f"Complaint-Sensitive Fee Adjustment Review · {scn.title} · "
        f"runtime {trace.runtime_version}"
    )
    _RENDERERS[screen](trace)


if __name__ == "__main__":
    main()
