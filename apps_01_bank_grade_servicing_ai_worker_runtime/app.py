"""Private mechanics lab UI — Complaint-Sensitive Fee Adjustment Review.

This is NOT an interview demo. It is a fictional internal analyst-assist workbench
used to run ONE bank-grade AI worker workflow repeatedly so the mechanics can be
understood and explained from memory.

v40 write law:
    L2 executes and seals. If a state change is possible, L2 emits only an inert
    proposed_state_diff. Exit decides whether that becomes a CommitRequest. UWG
    validates and commits. L4 stores.

HITL is an Exit disposition, not a model action.
L6 learns only after the current run boundary.

Run:  streamlit run app.py
"""

from __future__ import annotations

import json
import pathlib
import sys

import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from src.runtime import REVIEWER_DECISIONS, SCENARIOS, get_scenario, run_workflow  # noqa: E402
from src.runtime.contracts import to_jsonable  # noqa: E402
from src.runtime.stages import STAGE_INFO, STAGE_ORDER  # noqa: E402

V40_WRITE_LAW = (
    "L2 executes and seals. If a state change is possible, L2 emits only an inert "
    "proposed_state_diff. Exit decides whether that becomes a CommitRequest. UWG "
    "validates and commits. L4 stores."
)
HITL_RULE = "HITL is an Exit disposition, not a model action."
L6_RULE = "L6 learns only after the current run boundary."

_VERDICT_COLORS = {
    "PASS": "#1b7f4b",
    "STOP": "#b00020",
    "ESCALATE": "#b8730b",
    "ABSTAIN": "#1f5fb0",
    "REROUTE": "#6a1b9a",
    "UNKNOWN": "#b00020",
}

SCREENS = [
    "Home / Lab Instructions",
    "Scenario Selector",
    "Step-Through Runtime",
    "Evidence Packet",
    "Prompt/Data Boundary",
    "L2 Execution",
    "Same-Authority Repair",
    "Exit Disposition",
    "HITL Review",
    "UWG Write Gate",
    "L4 Archive",
    "Audit / Replay",
    "L6 Post-Run Learning",
    "v40 Alignment",
    "Mechanics Self-Check",
]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def verdict_badge(verdict: str) -> str:
    color = _VERDICT_COLORS.get(verdict, "#444")
    return (
        f"<span style='background:{color};color:#fff;padding:2px 10px;"
        f"border-radius:10px;font-size:0.80rem;font-weight:600'>{verdict}</span>"
    )


def get_trace():
    return run_workflow(
        st.session_state.scenario_id, st.session_state.get("reviewer_decision")
    )


def receipts_by_stage(trace) -> dict:
    return {r.stage_id: r for r in trace.stage_receipts}


def stage_executed(trace, stage_id: str) -> bool:
    return stage_id in receipts_by_stage(trace)


def render_stage_card(stage_id: str, trace) -> None:
    info = STAGE_INFO[stage_id]
    receipts = receipts_by_stage(trace)
    receipt = receipts.get(stage_id)

    st.markdown(f"### {info.stage_name}")
    st.caption(f"v40 mapping — {info.v40_mapping}")
    if receipt:
        st.markdown(
            f"**Gate verdict:** {verdict_badge(receipt.gate_verdict)}",
            unsafe_allow_html=True,
        )
    else:
        st.info("This stage was NOT entered for the current scenario/run.")

    st.markdown(f"**Plain-English purpose** — {info.purpose}")
    st.markdown(f"**Authority owner** — `{info.authority_owner}`")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**This stage MAY:**")
        for item in info.may_do:
            st.markdown(f"- {item}")
    with c2:
        st.markdown("**This stage MUST NOT:**")
        for item in info.must_not_do:
            st.markdown(f"- {item}")

    if receipt:
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("**Input artifact(s)**")
            st.code("\n".join(receipt.inputs) or "—")
        with c4:
            st.markdown("**Output artifact / receipt**")
            st.code(receipt.output_artifact)
        st.markdown("**Trace update**")
        st.write(receipt.summary)
        with st.expander("Receipt detail (JSON)"):
            st.json(to_jsonable(receipt.detail))

    st.markdown("---")
    st.markdown(f"**Explain-back prompt** — *{info.explain_back_prompt}*")
    st.caption(
        "This lab asks you to explain the mechanics in your own words. "
        "It does not generate the answer for you."
    )


# --------------------------------------------------------------------------- #
# Screens
# --------------------------------------------------------------------------- #
def screen_home(trace) -> None:
    st.title("Fee-Adjustment Mechanics Lab")
    st.markdown(
        "**This is a private mechanics lab, not an interview demo.** It exists so you "
        "can run ONE production-believable bank-grade AI worker workflow repeatedly, "
        "see exactly what each stage does, who holds authority, what is forbidden, and "
        "the receipt each stage emits — then replay and explain the run from memory."
    )
    st.info(
        "Fictional internal analyst-assist / case-review workbench for a regional bank. "
        "No real customer data. No external services. No production or institutional claims."
    )
    st.subheader("The one workflow")
    st.markdown(
        "**Complaint-Sensitive Fee Adjustment Review** — a servicing analyst reviews a "
        "customer fee-adjustment request (monthly maintenance, service, or card-related "
        "fee): assemble evidence, identify complaint sensitivity, generate a bounded "
        "recommendation, prepare an inert `proposed_state_diff` when eligible, escalate "
        "to human review when required, and route any eligible write through a durable "
        "write gate."
    )

    st.subheader("How to use this lab")
    for step in [
        "Run one scenario end to end.",
        "Pause at each stage.",
        "Identify who has authority.",
        "Identify what is forbidden.",
        "Inspect the emitted receipt.",
        "Replay the trace.",
        "Explain the run out loud in your own words.",
    ]:
        st.markdown(f"- {step}")

    st.subheader("Core v40 law")
    st.success(V40_WRITE_LAW)
    st.markdown(f"- **HITL rule** — {HITL_RULE}")
    st.markdown(f"- **Learning rule** — {L6_RULE}")
    st.caption("Note: this lab uses the exact wording above. It does NOT say 'L2 proposes.'")


def screen_scenario_selector(trace) -> None:
    st.title("Scenario Selector")
    st.caption("One workflow. Exactly three fee-adjustment scenarios. Nothing else.")
    for sid in ["A", "B", "C"]:
        scn = SCENARIOS[sid]
        selected = st.session_state.scenario_id == sid
        with st.container(border=True):
            st.markdown(f"### {scn.title}")
            st.write(scn.one_liner)
            st.caption(f"Evidence support status: **{scn.evidence_support_status}** · "
                       f"Complaint indicator: **{scn.complaint_indicator}**")
            if selected:
                st.success("Selected")
            else:
                if st.button(f"Select Scenario {sid}", key=f"sel_{sid}"):
                    st.session_state.scenario_id = sid
                    st.session_state.reviewer_decision = None
                    st.rerun()


def screen_step_through(trace) -> None:
    st.title("Step-Through Runtime")
    st.caption("Every screen is part of the same RunTrace. Step one stage at a time.")
    receipts = receipts_by_stage(trace)
    labels = []
    for sid in STAGE_ORDER:
        mark = "✓" if sid in receipts else "·"
        labels.append(f"{mark} {STAGE_INFO[sid].stage_name}")
    idx = st.radio(
        "Stage", options=list(range(len(STAGE_ORDER))),
        format_func=lambda i: labels[i], label_visibility="collapsed",
    )
    st.markdown("---")
    render_stage_card(STAGE_ORDER[idx], trace)


def screen_evidence(trace) -> None:
    st.title("Evidence Packet")
    scn = get_scenario(trace.scenario_id)
    st.caption(f"{scn.title} · custody-controlled C0 evidence packet")

    custody = trace.c0_custody_sequence
    st.subheader("C0 retrieval / evidence custody")
    st.markdown(
        "Deterministic mock retrieval custody sequence (no external retrieval): "
        + " → ".join(f"`{p}`" for p in custody["pipeline"])
    )
    header = [
        "source_id", "retrieved", "acl_status", "freshness", "quality_state",
        "contradiction_status", "authority_level", "in_final_packet",
        "can_support_write", "exclusion_reason",
    ]
    rows = []
    for c in custody["candidates"]:
        rows.append(
            {
                "source_id": c["source_id"],
                "retrieved": c["retrieved"],
                "acl_status": c["acl_status"],
                "freshness": c["freshness"],
                "quality_state": c["quality_state"],
                "contradiction_status": c["contradiction_status"],
                "authority_level": c["authority_level"],
                "in_final_packet": c["included_in_final_packet"],
                "can_support_write": c["can_support_write"],
                "exclusion_reason": c["exclusion_reason"] or "—",
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True, column_order=header)
    st.markdown(f"**Support classification:** `{custody['support_classification']}`")
    if custody["conflicted_sources"]:
        st.warning(f"Conflicted sources: {', '.join(custody['conflicted_sources'])}")

    st.subheader("FinalEvidenceContract (output of C0, consumed by PA)")
    st.json(trace.final_evidence_contract)

    st.markdown("---")
    st.subheader("Evidence items")
    for ev in trace.evidence_packet:
        with st.expander(f"{ev.id} — {ev.label}", expanded=False):
            st.write(ev.value)
            cols = st.columns(2)
            fields = [
                ("source_type", ev.source_type),
                ("acl_status", ev.acl_status),
                ("freshness", ev.freshness),
                ("quality_state", ev.quality_state),
                ("contradiction_status", ev.contradiction_status),
                ("citation_anchor", ev.citation_anchor),
                ("used_for", ev.used_for),
                ("authority_level", ev.authority_level),
                ("can_support_write", str(ev.can_support_write)),
            ]
            for i, (k, v) in enumerate(fields):
                cols[i % 2].markdown(f"**{k}:** `{v}`")


def screen_boundary(trace) -> None:
    st.title("Prompt / Data Boundary")
    pb = trace.prompt_boundary_check
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("DATA (informs only)")
        for item in pb["data"]:
            st.markdown(f"- {item}")
    with c2:
        st.subheader("AUTHORITY (governs)")
        for item in pb["authority"]:
            st.markdown(f"- {item}")
    st.markdown("---")
    st.warning(pb["rule"])
    st.markdown(f"Boundary gate verdict: {verdict_badge(pb['verdict'])}", unsafe_allow_html=True)
    if pb.get("carries_conflict_status"):
        st.info("This boundary check passes but carries conflict status (Scenario C).")


def screen_l2(trace) -> None:
    st.title("L2 Execution")
    art = trace.l2_execution_artifact
    st.success(V40_WRITE_LAW)
    st.markdown("**Frozen execution context**")
    st.json(art["frozen_execution_context"])
    st.markdown(f"**Selected route** — `{art['selected_route']}`")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Allowed L2 actions**")
        for a in art["allowed_actions"]:
            st.markdown(f"- {a}")
    with c2:
        st.markdown("**Forbidden L2 actions**")
        for a in art["forbidden_actions"]:
            st.markdown(f"- {a}")

    st.markdown(f"**Worker summary** — {art['worker_summary']}")
    st.markdown(f"**Rule comparison** — {art['rule_comparison']}")
    st.markdown(f"**Recommendation** — `{art['recommendation']}`")
    st.markdown(f"**Blocked action** — {art['blocked_action']}")

    if art["proposed_state_diff"]:
        st.markdown("**Inert proposed_state_diff** (NOT a commit)")
        st.json(art["proposed_state_diff"])
    else:
        st.caption("No proposed_state_diff prepared for this scenario.")

    if art["human_review_packet"]:
        st.markdown("**human_review_packet** (prepared for Exit to escalate)")
        st.json(art["human_review_packet"])

    st.markdown("**Seal receipt**")
    st.json(art["seal_receipt"])


def screen_repair(trace) -> None:
    st.title("Same-Authority Repair (L2.E4)")
    if not trace.heal_receipt:
        st.info(
            "No same-authority repair occurred for this scenario. The deterministic "
            "schema repair is modeled only in Scenario C (initial L2 output omits a "
            "required `contradiction_status` field)."
        )
        return
    st.caption("Schema-only repair. E4 is not an agent.")
    st.markdown("**Repair event log**")
    for line in trace.heal_receipt["event_log"]:
        st.markdown(f"- {line}")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Changed (schema only)**")
        st.json(trace.heal_receipt["changed"])
    with c2:
        st.markdown("**Unchanged (no authority expansion)**")
        st.json(trace.heal_receipt["unchanged"])


def screen_exit(trace) -> None:
    st.title("Exit Disposition")
    st.caption("Exit emits exactly ONE X3 per evaluation.")
    all_x3 = [
        "X3A_DENY_REROUTE",
        "X3B_ESCALATE_HITL",
        "X3C_COMMIT_REQUEST_TO_UWG",
        "X3D_ALLOW_FINISH",
        "X3E_SAFE_ABSTAIN",
    ]
    emitted = {e["x3"] for e in trace.exit_disposition_history}
    st.markdown("**Possible dispositions** (emitted ones highlighted):")
    for x in all_x3:
        flag = "✅" if x in emitted else "▫️"
        st.markdown(f"{flag} `{x}`")
    st.markdown("---")
    st.caption(
        "Exit evaluator runs deterministic checks before emitting an X3 — no LLM, "
        "no write, exactly one X3 per evaluation."
    )
    for e in trace.exit_disposition_history:
        st.markdown(
            f"#### [{e['evaluation']}] → `{e['x3']}` "
            f"{verdict_badge(e['gate_verdict'])}",
            unsafe_allow_html=True,
        )
        st.caption(e["reason"])
        ec = e["exit_checks"]
        st.markdown("**Exit evaluation checks (deterministic)**")
        rows = [{"check": k, "value": v} for k, v in ec["checks"].items()]
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.markdown("---")
    st.markdown(f"**Final disposition:** `{trace.final_exit}`")


def screen_hitl(trace) -> None:
    st.title("HITL Review")
    st.warning(HITL_RULE)
    if trace.final_exit != "X3B_ESCALATE_HITL" and not trace.reviewer_decision:
        # Only Scenario B (escalated) enters HITL.
        if trace.scenario_id != "B":
            st.info(
                "This screen is only entered when Exit emits X3B_ESCALATE_HITL "
                "(Scenario B). The current run did not escalate to HITL."
            )
            return

    if not trace.hitl_review_packet:
        st.info("No human_review_packet was prepared for this run.")
        return

    st.subheader("Reviewer packet")
    st.json(trace.hitl_review_packet)

    st.subheader("Reviewer decision")
    if trace.reviewer_decision:
        st.success(
            f"Decision recorded: **{trace.reviewer_decision.decision}** "
            f"(reason `{trace.reviewer_decision.reason_code}`)"
        )
        st.json(to_jsonable(trace.reviewer_decision))
        if st.button("Clear reviewer decision (re-open HITL)"):
            st.session_state.reviewer_decision = None
            st.rerun()
        st.markdown("---")
        st.markdown(
            "After the reviewer acts, **re-clearance** re-runs Exit deterministically. "
            "See the *Exit Disposition* and *UWG Write Gate* screens for the outcome."
        )
    else:
        st.caption("Choose a reviewer action. Re-clearance (Exit re-evaluation) follows.")
        cols = st.columns(2)
        for i, (key, label) in enumerate(REVIEWER_DECISIONS.items()):
            if cols[i % 2].button(label, key=f"rvw_{key}"):
                st.session_state.reviewer_decision = key
                st.rerun()


def screen_uwg(trace) -> None:
    st.title("UWG Write Gate")
    st.caption("UWG is the only path to a durable write.")
    if not trace.uwg_validation_result:
        st.info(
            "UWG is only entered when Exit (or re-clearance) emits "
            "X3C_COMMIT_REQUEST_TO_UWG. The current run produced no CommitRequest."
        )
        return
    st.markdown("**CommitRequest**")
    st.json(trace.commit_request)
    st.markdown("**Write-gate validation checks (deterministic)**")
    st.caption(
        "Deterministic write-gate validation — not a judge. UWG is the only "
        "component that can create an L4ArchiveRecord."
    )
    res = trace.uwg_validation_result
    rows = [{"check": k, "value": v} for k, v in res.checks.items()]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    if res.approved:
        st.success(f"Approved simulated commit — {res.reason}")
    else:
        st.error(f"Blocked commit — {res.reason}")


def screen_l4(trace) -> None:
    st.title("L4 Archive")
    st.caption("Only a UWG-approved commit can create an L4ArchiveRecord.")
    st.markdown(
        "- L2 cannot write L4\n- UI cannot bypass UWG\n- L6 cannot write L4\n"
        "- only UWG-approved commit can create L4ArchiveRecord"
    )
    if not trace.l4_archive_record:
        st.info("No durable write occurred. L4 received nothing for this run.")
        return
    rec = trace.l4_archive_record
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Before (mock state)**")
        st.json({"fee_status": rec.prior_fee_status, "adjustment_status": "none"})
    with c2:
        st.markdown("**After (mock state)**")
        st.json({"fee_status": "adjusted", "adjustment_status": rec.adjustment_status})
    st.markdown("**Archive record**")
    st.json(to_jsonable(rec))


def screen_audit(trace) -> None:
    st.title("Audit / Replay")
    st.caption("Full deterministic RunTrace. Replay reproduces the exact same trace.")
    c1, c2, c3 = st.columns(3)
    c1.metric("policy_hash", trace.policy_hash)
    c2.metric("prompt_hash", trace.prompt_hash)
    c3.metric("replay_key", trace.replay_key)

    if st.button("Replay this run"):
        replay = run_workflow(trace.scenario_id, st.session_state.get("reviewer_decision"))
        same = to_jsonable(replay) == to_jsonable(trace)
        st.session_state["_replay_same"] = same
    if "_replay_same" in st.session_state:
        if st.session_state["_replay_same"]:
            st.success(
                "Deterministic replay receipt: replay reproduced the EXACT same trace "
                "(no values recomputed)."
            )
        else:
            st.error("Replay diverged — this would violate determinism.")

    trace_json = json.dumps(to_jsonable(trace), indent=2)
    st.download_button(
        "Download RunTrace JSON",
        data=trace_json,
        file_name=f"runtrace_{trace.run_id}.json",
        mime="application/json",
    )
    with st.expander("Full RunTrace JSON", expanded=False):
        st.json(to_jsonable(trace))


def screen_l6(trace) -> None:
    st.title("L6 Post-Run Learning")
    st.warning(L6_RULE)
    if not trace.l6_post_run_evaluation:
        st.info(
            "L6 has not run. The current run boundary has not been reached "
            "(e.g. Scenario B is still awaiting a reviewer decision)."
        )
        return
    l6 = trace.l6_post_run_evaluation
    st.markdown("**Inert post-run artifacts** (proposals only):")
    st.markdown("**Completed eval record**")
    st.json(l6["completed_eval_record"])
    st.markdown("**RCA packet**")
    st.json(l6["rca_packet"])
    st.markdown(f"**Future-run proposal** — {l6['future_run_proposal']}")
    st.markdown(f"**Suggested eval case** — `{l6['suggested_eval_case']}`")
    st.markdown(f"**Proposed policy/prompt/rubric update** — {l6['proposed_policy_prompt_rubric_update']}")
    st.markdown("**L6 must not:**")
    for c in l6["constraints"]:
        st.markdown(f"- {c}")


def screen_v40(trace) -> None:
    st.title("v40 Alignment")
    st.success(V40_WRITE_LAW)
    mapping = [
        ("U0", "validate fee-adjustment case"),
        ("L1", "frame ambiguity"),
        ("L0", "deterministic fee_adjustment route"),
        ("C0", "evidence custody"),
        ("PA", "prompt/data boundary"),
        ("L2", "bounded execution"),
        ("L2.E4", "same-authority schema repair only"),
        ("Exit", "one X3 disposition"),
        ("HITL", "Exit escalation path"),
        ("UWG", "write validation"),
        ("L4", "archive after UWG only"),
        ("L6", "post-run learning after boundary only"),
        ("L5", "cross-cutting certification"),
        ("00C", "runtime gates"),
    ]
    for layer, desc in mapping:
        st.markdown(f"- **{layer}** = {desc}")
    st.markdown("---")
    st.subheader("Runtime gates")
    st.markdown(
        "GateVerdict values: `PASS` · `STOP` · `ESCALATE` · `ABSTAIN` · `REROUTE` · `UNKNOWN`"
    )
    st.error("Hard rule: UNKNOWN is never PASS.")
    unknown = trace.runtime_exhaust_bundle.get("unknown_present")
    st.markdown(
        f"This run's gate verdicts contain UNKNOWN: **{unknown}** "
        f"(must always be False for a PASS path)."
    )
    st.json(trace.gate_verdicts)


def screen_self_check(trace) -> None:
    st.title("Mechanics Self-Check")
    st.caption(
        "This is NOT interview coaching. It is a personal-understanding checklist. "
        "Tick an item only once you can explain it without notes."
    )
    items = [
        "I can explain why U0 validates before reasoning.",
        "I can explain why L1 has route hints but no route authority.",
        "I can explain why L0 route is deterministic.",
        "I can explain why evidence has quality states.",
        "I can explain why customer narrative is data, not authority.",
        "I can explain what L2 executes and seals.",
        "I can explain why E4 Heal is not an agent.",
        "I can explain why Exit emits exactly one X3.",
        "I can explain why HITL is an Exit disposition.",
        "I can explain why UWG is the only write path.",
        "I can explain why L4 only stores after UWG.",
        "I can explain why L6 cannot affect the active run.",
    ]
    done = 0
    for i, item in enumerate(items):
        if st.checkbox(item, key=f"sc_{i}"):
            done += 1
    st.progress(done / len(items))
    st.caption(f"{done} / {len(items)} mechanics you can explain from memory.")


_RENDERERS = {
    "Home / Lab Instructions": screen_home,
    "Scenario Selector": screen_scenario_selector,
    "Step-Through Runtime": screen_step_through,
    "Evidence Packet": screen_evidence,
    "Prompt/Data Boundary": screen_boundary,
    "L2 Execution": screen_l2,
    "Same-Authority Repair": screen_repair,
    "Exit Disposition": screen_exit,
    "HITL Review": screen_hitl,
    "UWG Write Gate": screen_uwg,
    "L4 Archive": screen_l4,
    "Audit / Replay": screen_audit,
    "L6 Post-Run Learning": screen_l6,
    "v40 Alignment": screen_v40,
    "Mechanics Self-Check": screen_self_check,
}


def main() -> None:
    st.set_page_config(page_title="Fee-Adjustment Mechanics Lab", layout="wide")
    if "scenario_id" not in st.session_state:
        st.session_state.scenario_id = "A"
    if "reviewer_decision" not in st.session_state:
        st.session_state.reviewer_decision = None

    trace = get_trace()
    scn = get_scenario(trace.scenario_id)

    with st.sidebar:
        st.markdown("### Mechanics Lab")
        st.caption("Private. Not an interview demo.")
        st.markdown("**Scenario**")
        choice = st.radio(
            "scenario",
            options=["A", "B", "C"],
            format_func=lambda s: f"{s} — {SCENARIOS[s].title.split('—')[1].strip()}",
            index=["A", "B", "C"].index(st.session_state.scenario_id),
            label_visibility="collapsed",
        )
        if choice != st.session_state.scenario_id:
            st.session_state.scenario_id = choice
            st.session_state.reviewer_decision = None
            st.rerun()

        st.markdown("---")
        st.markdown(f"**Run:** `{trace.run_id}`")
        st.markdown(f"**Final X3:** `{trace.final_exit}`")
        wrote = trace.l4_archive_record is not None
        st.markdown(f"**Durable write:** {'yes' if wrote else 'no'}")
        if trace.runtime_exhaust_bundle.get("awaiting_reviewer"):
            st.warning("Awaiting reviewer (HITL).")
        st.markdown("---")
        screen = st.radio("Screen", options=SCREENS, label_visibility="collapsed")

    st.caption(
        f"Workflow: Complaint-Sensitive Fee Adjustment Review · {scn.title} · "
        f"runtime {trace.runtime_version}"
    )
    _RENDERERS[screen](trace)


if __name__ == "__main__":
    main()
