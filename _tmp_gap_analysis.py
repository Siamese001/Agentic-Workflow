#!/usr/bin/env python3
"""Comprehensive bypass audit - find files that skip chokepoints."""
import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
print(f"DB: {db}\n")

NTEST = """
    AND source_file NOT LIKE '%test%'
    AND source_file NOT LIKE '%_tmp%'
    AND source_file NOT LIKE '%ops_scripts%'
"""

def files(rel, sym_like=""):
    extra = f"AND symbol LIKE '{sym_like}'" if sym_like else ""
    return set(r[0] for r in conn.execute(
        f"SELECT DISTINCT source_file FROM edges WHERE relation_type=? {extra} {NTEST}", (rel,)
    ).fetchall())

def sym_files(sym_like):
    return set(r[0] for r in conn.execute(
        f"SELECT DISTINCT source_file FROM edges WHERE symbol LIKE ? {NTEST}", (sym_like,)
    ).fetchall())

# --- Chokepoint callers ---
reason_callers   = sym_files("%reason_and_record%")
guardrail_callers = sym_files("%authorize_and_execute%")
agent_dispatch   = sym_files("%emit_agent_executes_agent%")
snap_callers     = sym_files("%snapshots_state%") | files("snapshots_state")
policy_callers   = sym_files("%enforce_policy_before_action%")

print(f"reason_and_record callers:         {len(reason_callers)}")
print(f"authorize_and_execute callers:     {len(guardrail_callers)}")
print(f"emit_agent_executes_agent callers: {len(agent_dispatch)}")
print(f"snapshots_state callers:           {len(snap_callers)}")
print(f"enforce_policy_before_action:      {len(policy_callers)}")

# --- LLM bypass candidates ---
# Guarded = has reason_and_record (preferred) OR at minimum _emit_records_execution_trace
trace_callers = files("records_execution_trace")
llm_callers = (sym_files("%AsyncOpenAI%") | sym_files("%AsyncAnthropic%")
               | sym_files("%genai%") | sym_files("%GeminiLLMClient%")
               | sym_files("%LLMClient%") | sym_files("%acompletion%")
               | sym_files("%chat.completions%"))
# Exclude known false-positive type-annotation files
llm_type_files = {f for f in llm_callers if '/types/' in f or '\\types\\' in f}
llm_real_callers = llm_callers - llm_type_files
llm_guarded = reason_callers | trace_callers
unguarded_llm = llm_real_callers - llm_guarded
print(f"\nLLM callers total:     {len(llm_real_callers)} (excl. {len(llm_type_files)} type-annotation files)")
print(f"  unguarded (no trace): {len(unguarded_llm)}")
for f in sorted(unguarded_llm)[:20]:
    print(f"    BYPASS-LLM: {f}")

# --- Tool execution bypass candidates ---
tool_callers = (sym_files("%tool_chain_executor%") | sym_files("%invoke_typed_tool%")
                | sym_files("%ToolChainExecutor%") | sym_files("%execute_command%"))
unguarded_tools = tool_callers - guardrail_callers
print(f"\nTool callers total:       {len(tool_callers)}")
print(f"  unguarded (no guardrail): {len(unguarded_tools)}")
for f in sorted(unguarded_tools)[:15]:
    print(f"    BYPASS-TOOL: {f}")

# --- L3 orchestration files not wiring agent dispatch ---
orch_files = set(r[0] for r in conn.execute(
    f"SELECT DISTINCT source_file FROM edges WHERE source_file LIKE '%L3_orchestration%' {NTEST}"
).fetchall())
unlinked_orch = orch_files - agent_dispatch
print(f"\nL3 orchestration files:      {len(orch_files)}")
print(f"  without agent dispatch:      {len(unlinked_orch)}")
for f in sorted(unlinked_orch)[:20]:
    print(f"    NO-DISPATCH: {f}")

# --- State authority bypass ---
state_writers = sym_files("%RunStateAuthority%") | sym_files("%run_state_authority%")
unsnapped = state_writers - snap_callers
print(f"\nRunStateAuthority users:    {len(state_writers)}")
print(f"  without snapshots_state:    {len(unsnapped)}")
for f in sorted(unsnapped)[:15]:
    print(f"    NO-SNAP: {f}")

# --- Current ADG coverage edge counts ---
print("\n=== Current coverage edge counts ===")
for rel in ["records_execution_trace", "applies_guardrail", "agent_executes_agent",
            "snapshots_state", "signs_execution_trace", "emits_replay_key",
            "emits_determinism_digest", "routes_path", "reads_policy_state",
            "issues_capability_token", "proposal_commits_routing"]:
    n = conn.execute(
        f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {NTEST}", (rel,)
    ).fetchone()[0]
    print(f"  {rel:<40} sources={n:4d}")

# --- Top high-traffic engine files for wiring priority ---
print("\n=== Top engine/enforcement files by edge count (wiring targets) ===")
rows = conn.execute(f"""
    SELECT source_file, COUNT(*) as cnt FROM edges
    WHERE (source_file LIKE '%engines%' OR source_file LIKE '%enforcement%'
           OR source_file LIKE '%orchestr%')
    {NTEST}
    GROUP BY source_file ORDER BY cnt DESC LIMIT 25
""").fetchall()
for f, cnt in rows:
    in_reason = "R" if f in reason_callers else " "
    in_guard  = "G" if f in guardrail_callers else " "
    in_agent  = "A" if f in agent_dispatch else " "
    print(f"  [{in_reason}{in_guard}{in_agent}] {cnt:5d}  {f}")
print("  R=has reason_and_record G=has authorize_and_execute A=has agent_dispatch")

conn.close()
