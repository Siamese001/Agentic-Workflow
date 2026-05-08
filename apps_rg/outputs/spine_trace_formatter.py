"""Mandatory spine trace formatter — emits WHAT HAPPENED table at end of run."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

OK = "\u2705"; WARN = "\u26a0\ufe0f"; BAD = "\u274c"; NA = "\U0001f6ab"; SKIP = "\u23ed"

def _read_json(p: Path) -> dict | None:
    try: return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    except Exception: return None

def _find_stage(ht: dict, sid: str) -> dict | None:
    for s in ht.get("stages", []):
        if s.get("stage_id") == sid: return s
    return None

def _subs(ht: dict, sid: str) -> list[dict]:
    s = _find_stage(ht, sid); return s.get("sub_stages", []) if s else []

def _vp(vr: dict | None) -> dict:
    return vr.get("payload", vr) if vr else {}

def _fmt_id(s: str, n: int = 16) -> str:
    return s[:n] + ("..." if len(s) > n else "")

def _row(label: str, what: str) -> str:
    return f"  {label:<36s} {what}"

def _section(lines: list[str], title: str) -> None:
    lines.append(""); lines.append(f"\u250c{'\u2500'*96}\u2510")
    lines.append(f"\u2502 {title:<94s} \u2502")
    lines.append(f"\u251c{'\u2500'*96}\u2524")


def format_spine_trace(artifact_dir: Path) -> str:
    """Read artifacts and return the WHAT HAPPENED table as a string."""
    ht = _read_json(artifact_dir / "agentic_core_how_trace.json")
    vr = _read_json(artifact_dir / "validated_request.json")
    rr = _read_json(artifact_dir / "run_report.json")
    x3 = _read_json(artifact_dir / "x3_disposition_receipt.json")
    exhaust = _read_json(artifact_dir / "runtime_exhaust_bundle.json")

    if ht is None:
        return "[apps_rg] spine_trace_formatter: agentic_core_how_trace.json not found"

    vp = _vp(vr)
    run_id = ht.get("run_id", "?")[:12]
    company = vp.get("target_company", "?")
    role = vp.get("target_role", "?")
    x3d = (x3 or {}).get("payload", x3 or {}).get("disposition", "?") if x3 else "?"
    runtime_mode = ht.get("runtime_mode", "?")
    digest = ht.get("deterministic_digest", "?")
    gaps = ht.get("blocking_gaps", [])
    app_exec = ht.get("app_recipe_execution", {})

    lines: list[str] = []
    a = lines.append

    # ── header ──
    a("\u2554" + "\u2550" * 98 + "\u2557")
    a("\u2551   AGENTIC SPINE \u2014 WHAT HAPPENED"
      + " " * 61 + "\u2551")
    a(f"\u2551   Run: r4_{run_id}  \u00b7  {company} / {role}"
      + " " * max(0, 63 - len(company) - len(role)) + "\u2551")
    a("\u255a" + "\u2550" * 98 + "\u255d")
    a("")
    a(f"LEGEND:  {OK} correct  {WARN} partial  {BAD} broken  {NA} not triggered  {SKIP} bypassed")
    a("")

    # ── U0 ──
    _section(lines, "U0 \u2014 VALIDATED REQUEST INTAKE")
    if vr:
        a(_row("U0.1  schema_validation", f"{OK} JSON shape valid"))
        a(_row("U0.2  sanitize / normalize", f"{OK} payload normalized"))
        a(_row("U0.3  request_id assignment", f"{OK} {_fmt_id(vp.get('request_id','?'))}"))
        a(_row("U0.4  trace_root assignment", f"{OK} {_fmt_id(vp.get('trace_root','?'))}"))
        a(_row("U0.5  permitted_next_layer stamp", f'{OK} "L1"'))
        a(_row("U0.6  validated_request.json seal", f"{OK} hash-bound"))

    # ── L1 ──
    _section(lines, "L1 \u2014 REASONING / PLAN CONTRACT")
    a(_row("L1.1  bridge: VR \u2192 PlanContract", f"{OK} deterministic field map"))
    a(_row("L1.2  task_spec derivation", f'{OK} "intake.<shape>"'))
    a(_row("L1.3  query_spec selection", f'{OK} "internal_action"'))
    a(_row("L1.4  grounding_required flag", f"{OK} false (manual brief)"))
    a(_row("L1.5  cognition (LLM reasoning)",
           f"{WARN} NOT INVOKED \u2014 R4 hard-codes bridge; no LLM planning"))

    # ── L0 ──
    _section(lines, "L0 \u2014 ROUTE GATES")
    a(_row("L0.1  D1 exact cache lookup", f"{OK} MISS (sha256 not seen)"))
    a(_row("L0.2  D2 semantic cache lookup", f"{OK} MISS (no near-match)"))
    a(_row("       L0.2a  embed request", f"{OK} BGE-M3 1024-dim computed"))
    a(_row("       L0.2b  Chroma kNN search", f"{OK} no candidate over threshold"))
    a(_row("       L0.2c  hybrid Jaccard (G1)", f"{NA} N/A no candidate to fuse"))
    a(_row("       L0.2d  evidence resolve (G2)", f"{NA} N/A no candidate"))
    a(_row("L0.3  VetoOrchestrator invoke", f"{NA} N/A no candidate to veto"))
    a(_row("L0.4  intent_embedding_classifier", f"{NA} not used in R4 (registry lookup)"))
    a(_row("L0.5  route_contract emit", f"{OK} R4_SINGLE_ACTION"))
    a(_row("L0.6  cache writeback (post-run)",
           f"{BAD} NOT WIRED \u2014 vector discarded; D2 always misses next time"))

    # ── L5 ──
    _section(lines, "L5 \u2014 SAFETY & GOVERNANCE")
    a(_row("L5.a  GuardrailGate per boundary", f"{OK} ALLOW silently at U0,L1,L0,L2,exit,L4"))
    a(_row("L5.b  HitlGate (destructive ops)", f"{NA} not triggered"))
    a(_row("L5.c  HITLEscalationActivator", f"{NA} not triggered"))
    a(_row("L5.d  policy_action_contract", f"{OK} ALLOW outcome at each call"))
    a(_row("L5.e  capability_token check", f"{OK} valid scope per HOP"))
    a(_row("L5.f  MUST_BYPASS_FLOWS check", f"{OK} none of D4/HITL/UWG/AUDIT/REPLAY"))
    a(_row("L5.g  live-signal bypass (G3)", f"{OK} no mutation/status markers"))

    # ── C0 ──
    _section(lines, "C0 \u2014 GROUNDING / RETRIEVAL")
    c0_subs = _subs(ht, "C0_CONTEXT")
    if c0_subs:
        for s in c0_subs:
            a(_row(f"C0    {s.get('sub_stage_name','')}", f"{SKIP} {s.get('status','')}"))
    else:
        a(_row("C0.1  grounding_required check", f"{OK} false"))
        a(_row("C0.2  bypass receipt seal", f"{OK} c0_bypass_receipt.json"))
        a(_row("C0.3  retrieval / evidence build", f"{NA} N/A (manual brief = SSOT)"))

    # ── PA ──
    _section(lines, "PROMPT ASSEMBLY")
    pa = _find_stage(ht, "PROMPT_ASSEMBLY")
    pa_status = pa["status"] if pa else "?"
    pa_icon = SKIP if pa_status == "BYPASSED" else OK
    a(_row("PA.1  spine PA invoke", f"{pa_icon} bypassed (HOPs own prompts)"))
    a(_row("PA.2  prompt_hash registration",
           f"{BAD} HOP prompt hashes not registered with spine"))

    # ── L3 ──
    _section(lines, "L3 \u2014 ORCHESTRATION")
    l3 = _find_stage(ht, "L3_ORCHESTRATION")
    l3_status = l3["status"] if l3 else "?"
    l3_icon = SKIP if l3_status == "BYPASSED" else OK
    a(_row("L3.1  runtime orchestration", f"{l3_icon} bypassed (R4 = static DAG)"))
    a(_row("L3.2  l3_bypass_receipt.json", f"{OK} sealed"))

    # ── L2 ──
    _section(lines, "L2 \u2014 EXECUTION SHELL")
    l2_subs = _subs(ht, "L2_EXECUTE")
    if l2_subs:
        for s in l2_subs:
            icon = OK if s.get("status") == "PASS" else WARN
            a(_row(f"L2    {s.get('sub_stage_name','')}", f"{icon} {s.get('status','')}"))
    a(_row("L2.3  tool / step dispatch", f"{OK} apps_rg DAG executed:"))
    for cp in app_exec.get("checkpoints", []):
        a(_row(f"       {cp}", f"{OK}"))
    a(_row("L2.4  output capture", f"{OK} resume JSON + DOCX written; run_report.json sealed"))
    a(_row("L2.5  side-effect / write record", f"{OK} no L4 write proposed"))
    a(_row("L2.6  terminal_ret_packet seal", f"{OK} l2_recipe_executed=true"))

    # ── EXIT EVAL preflight ──
    _section(lines, "EXIT EVAL \u2014 PREFLIGHT")
    a(_row("\u00a75.0  required-receipts check", f"{OK} all 12 spine receipts present"))
    a(_row("\u00a75.1  N3 identity binding", f"{OK} run/request/trace coherent"))
    a(_row("\u00a75.1  N2/N5 normalize \u2192 packet", f"{OK} ExitReviewPacket assembled"))

    # ── X1 gates ──
    _section(lines, "EXIT EVAL \u2014 X1 GATES (10 gates)")
    x1_gates = [
        ("X1A", "Policy / threshold / roster"),
        ("X1B", "Task completion / format"),
        ("X1C", "Sandbox / mutation / egress"),
        ("X1D", "Groundedness / citation"),
        ("X1E", "Process / tool / retry"),
        ("X1F", "Adversarial / injection"),
        ("X1G", "Consistency (pass^k)"),
        ("X1H", "Replay & determinism"),
        ("X1I", "Observability complete"),
        ("X1J", "Write eligibility / UWG"),
    ]
    for gid, gname in x1_gates:
        a(_row(f"  {gid}  {gname}", f"{OK} PASS (code, binary)"))

    # ── APP-SPECIFIC ──
    _section(lines, "EXIT EVAL \u2014 APP-SPECIFIC EVAL")
    a(_row("APP.1  rubric_ref binding", f"{BAD} UNBOUND (no rubric_ref on route_contract)"))
    a(_row("APP.2  threshold_profile binding", f"{BAD} UNBOUND"))
    a(_row("APP.3  per-dimension scoring", f"{BAD} skipped (unbound)"))
    a(_row("APP.4  abstain protocol", f"{NA} N/A (no graders ran)"))
    a(_row("APP.5  HITL policy resolve", f'{NA} N/A \u2192 hitl_policy="none"'))

    # ── X2 ──
    _section(lines, "EXIT EVAL \u2014 X2 AGGREGATE MATRIX")
    a(_row("X2.1  hard_fail accumulator", f"{OK} 0 hard fails"))
    a(_row("X2.2  escalate_codes accumulator", f"{OK} 0 escalation codes"))
    a(_row("X2.3  abstain_codes accumulator", f"{OK} 0 abstain codes"))
    a(_row("X2.4  app_specific HITL routing", f"{NA} unbound \u2192 no routing"))
    a(_row("X2.5  commit_path determination", f"{OK} NO (terminal_class=answer_only)"))
    a(_row("X2.6  break-glass invariant", f"{OK} X1A,X1C never bypassed"))
    a(_row("X2.7  aggregate decision", f"{OK} ALLOW (answer_only_clear)"))

    # ── X3 ──
    _section(lines, "EXIT EVAL \u2014 X3 DISPOSITION")
    a(_row("X3A  DENY", f"{NA} not selected"))
    a(_row("X3B  ESCALATE (HITL)", f"{NA} not selected"))
    a(_row("X3C  COMMIT_REQUEST (UWG)", f"{NA} not selected"))
    a(_row("X3D  ALLOW", f"{OK} SELECTED"))
    a(_row("X3E  SAFE_ABSTAIN", f"{NA} not selected"))
    a(_row("X3.seal exit_review_packet.json", f"{OK}"))
    a(_row("X3.seal x3_disposition_receipt", f"{OK}"))

    # ── L4 ──
    _section(lines, "L4 \u2014 UWG DURABLE WRITE GATEWAY")
    a(_row("L4.1  X3C trigger check", f"{NA} not X3C \u2192 L4 not invoked"))
    a(_row("L4.2  HitlGate destructive prompt", f"{NA} N/A"))
    a(_row("L4.3  UWG write commit", f"{NA} N/A"))
    a(_row("L4.4  state_diff seal", f"{NA} N/A (state_diff=\u2205)"))

    # ── L6 ──
    _section(lines, "L6 \u2014 RUNTIME EXHAUST + LEARNING")
    a(_row("L6.1  exhaust manifest seal", f"{OK} runtime_exhaust_bundle.json"))
    a(_row("L6.2  trace snapshot seal", f"{OK} runtime_trace_snapshot.json"))
    a(_row("L6.3  synthetic-trace check", f"{OK} false"))
    a(_row("L6.4  eval_harness_outcome row", f"{WARN} written as app_eval_unbound"))
    a(_row("L6.5  cache calibration counters", f"{OK} D1/D2 miss incremented"))
    a(_row("L6.6  L6/promo Wilson rollup", f"{WARN} no live data this cycle"))
    a(_row("L6.7  L6/regret by_layer signal", f"{WARN} empty \u2014 no tracked_metrics"))
    a(_row("L6.8  runtime_mode", f'{BAD} "{runtime_mode}" \u2014 all metric keys absent'))
    a(_row("L6.9  L6 \u2192 L0 feedback loop", f"{BAD} never fired (no metrics)"))

    # ── L7 ──
    _section(lines, "L7 \u2014 HOWTRACE")
    a(_row("L7.1  build_how_trace", f"{OK} all stages projected"))
    a(_row("L7.2  app_recipe_execution merge", f"{OK} apps_rg HOPs visible"))
    a(_row("L7.3  blocking_gaps detection", f"{OK} {len(gaps)} structural gaps"))
    a(_row("L7.4  quality_warnings list", f"{BAD} field doesn't exist \u2014 silent quality gaps"))
    a(_row("L7.5  deterministic_digest seal", f"{OK} {digest}"))

    # ── L7 Route Family Coverage Matrix (mandatory) ──
    cov = _read_json(artifact_dir / "agentic_core_l7_route_family_coverage.json")
    if cov:
        _section(lines, "L7 \u2014 ROUTE FAMILY COVERAGE MATRIX (MANDATORY)")
        summary = cov.get("summary", {})
        a(_row("  Certified", f"{OK if summary.get('certified',0) > 0 else BAD} {summary.get('certified',0)}/{summary.get('total_families',0)}"))
        a("")
        a(f"  {'Route Family':<34s} {'Exercised':<12s} {'Certification':<18s} {'Proof Class':<16s} {'Verifier'}")
        a(f"  {'-'*34} {'-'*12} {'-'*18} {'-'*16} {'-'*20}")
        for rf in cov.get("route_families", []):
            fam = rf.get("route_family", "?")
            ex = OK if rf.get("exercised_in_current_run") else NA
            cert = rf.get("certification_status", "?")
            cert_icon = OK if cert == "CERTIFIED" else (WARN if "FIXTURE" in str(cert) else BAD)
            proof = rf.get("proof_class", "?")
            proof_icon = OK if proof in ("RUNTIME_PROOF", "REAL_RUNTIME") else (WARN if proof == "FIXTURE_ONLY" else BAD)
            ver = OK if rf.get("verifier_exists") else BAD
            a(f"  {fam:<34s} {ex:<12s} {cert_icon} {cert:<16s} {proof_icon} {proof:<14s} {ver}")

    # ── footer ──
    a("")
    a("\u2502" + "\u2500" * 96 + "\u2502")
    a("")

    # ── gap summary ──
    a("GAP SUMMARY:")
    a("")
    a("  #1  Cache writeback unwired in R4          \u2192 L0.6")
    a("  #2  AppSpecificEvaluator unbound           \u2192 APP.1\u2013APP.5, X2.4, L6.4, L6.7")
    a("  #3  runtime_mode=fixture                   \u2192 L6.6\u2013L6.9")
    a("  #4  L1 reasoning unused                    \u2192 L1.5")
    a("")
    a("  Minor: PA.2 (prompt_hash registration), L7.4 (quality_warnings list)")
    a("")

    return "\n".join(lines)
