# ruff: noqa: C401
"""One-shot analysis of heal_run_complete.json — high-signal gate summary."""

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
data = json.loads((ROOT / "logs/compliance_reports/heal_run_complete.json").read_text())
actions = data["healing_actions"]


# ─────────────────────────────────────────────────────────────────────────────
# Helper: parse a single fix_summary into (found, fixed) using priority order
# ─────────────────────────────────────────────────────────────────────────────
def parse_summary(s):
    """Return (found, fixed) from a fix_summary string. Prefer explicit 'N of M' forms."""
    if not s:
        return (0, 0)
    m = re.search(r"Healed (\d+) of (\d+)", s)
    if m:
        return (int(m.group(2)), int(m.group(1)))
    m = re.search(r"Cleaned (\d+) of (\d+)", s)
    if m:
        return (int(m.group(2)), int(m.group(1)))
    m = re.search(r"Fixed (\d+) of (\d+)", s)
    if m:
        return (int(m.group(2)), int(m.group(1)))
    # "Fixed 0 file classification violation(s)" — found=0, fixed=0
    m = re.search(r"Fixed (\d+) (?:file|architecture)", s)
    if m:
        return (0, int(m.group(1)))
    # generic "N violation(s)" with no fix claim — scanner-only entry
    m = re.search(r"(\d+) violation", s)
    if m:
        return (int(m.group(1)), 0)
    return (0, 0)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Per-agent totals (collapse territories)
# ─────────────────────────────────────────────────────────────────────────────
agent_found = defaultdict(int)
agent_fixed = defaultdict(int)
agent_skipped_viols = defaultdict(int)  # violations SKIPPED (no heal capability)

for a in actions:
    agent = a["agent"]
    s = a["fix_summary"] or ""
    found, fixed = parse_summary(s)
    agent_found[agent] += found
    agent_fixed[agent] += fixed
    if a["outcome"] == "SKIPPED":
        m = re.search(r"(\d+) violation", s)
        if m:
            agent_skipped_viols[agent] += int(m.group(1))

print("=== PER-AGENT VIOLATION COUNTS ===")
print(f"  {'Agent':<38} {'found':>6}  {'fixed':>6}  {'skipped_viols':>13}")
print(f"  {'-' * 38} {'-' * 6}  {'-' * 6}  {'-' * 13}")
for agent in sorted(set(list(agent_found) + list(agent_fixed))):
    f = agent_found[agent]
    x = agent_fixed[agent]
    sk = agent_skipped_viols[agent]
    print(f"  {agent:<38} {f:>6}  {x:>6}  {sk:>13}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Territory-level open violations (per-agent, so no double-count)
# ─────────────────────────────────────────────────────────────────────────────
# Key insight: each (agent, territory) pair is one row. We want:
#   territory_total_found  = max across agents that *scanned* for violations
#                            (scanner agents say "N violations found")
#   territory_total_fixed  = sum of fixes across agents in that territory
# We separate "scan" agents from "fix" agents by outcome.

SCANNER_AGENTS = {
    "FilesystemSSOTHealerAgent",
    "GravityValidatorAgent",
    "LocationHealerAgent",
    "RootHygieneAgent",
}

territory_scan_found = defaultdict(int)  # violations detected by scanners
territory_fixed = defaultdict(int)  # violations healed by any agent
territory_skipped = defaultdict(int)  # explicitly unresolvable

for a in actions:
    t = a["territory"]
    s = a["fix_summary"] or ""
    found, fixed = parse_summary(s)
    if a["agent"] in SCANNER_AGENTS:
        territory_scan_found[t] += found
    territory_fixed[t] += fixed
    if a["outcome"] == "SKIPPED":
        m = re.search(r"(\d+) violation", s)
        if m:
            territory_skipped[t] += int(m.group(1))

print()
print("=== TERRITORY VIOLATION SUMMARY ===")
print(f"  {'Territory':<22} {'found':>6}  {'fixed':>6}  {'skipped':>7}  {'remaining':>9}  status")
print(f"  {'-' * 22} {'-' * 6}  {'-' * 6}  {'-' * 7}  {'-' * 9}  ------")

open_territories = 0
all_territories = sorted(set(list(territory_scan_found) + list(territory_fixed)))
for t in all_territories:
    found = territory_scan_found.get(t, 0)
    fixed = territory_fixed.get(t, 0)
    skip = territory_skipped.get(t, 0)
    # remaining = found that were neither fixed nor structurally blocked
    actionable_remaining = max(0, found - fixed - skip)
    status = "✓ CLEAN" if actionable_remaining == 0 else "⚠ OPEN"
    if actionable_remaining > 0:
        open_territories += 1
    print(f"  {t:<22} {found:>6}  {fixed:>6}  {skip:>7}  {actionable_remaining:>9}  {status}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. SKIPPED outcomes — structural violations no agent can auto-fix
# ─────────────────────────────────────────────────────────────────────────────
print()
print("=== STRUCTURAL (MANUAL-ONLY) VIOLATIONS ===")
for a in actions:
    if a["outcome"] == "SKIPPED":
        print(f"  [{a['agent']}][{a['territory']}] {a['fix_summary']}")

# ─────────────────────────────────────────────────────────────────────────────
# 4. PARTIAL outcomes — distinguish genuine vs vacuous
# ─────────────────────────────────────────────────────────────────────────────
genuine_partials = []
for a in actions:
    if a["outcome"] == "PARTIAL":
        found, fixed = parse_summary(a["fix_summary"] or "")
        if found > 0 and fixed < found:
            genuine_partials.append((a, found, fixed))

print()
print(f"=== GENUINE PARTIAL outcomes (found>0, fixed<found): {len(genuine_partials)} ===")
for a, found, fixed in genuine_partials:
    print(f"  [{a['agent']}][{a['territory']}] found={found} fixed={fixed}  '{a['fix_summary']}'")

vacuous_partial_count = sum(1 for a in actions if a["outcome"] == "PARTIAL") - len(genuine_partials)
print(f"  (vacuous PARTIALs where found=0: {vacuous_partial_count})")

# ─────────────────────────────────────────────────────────────────────────────
# 5. Outcome breakdown
# ─────────────────────────────────────────────────────────────────────────────
outcome_counts = defaultdict(int)
for a in actions:
    outcome_counts[a["outcome"]] += 1
print()
print("=== OUTCOME BREAKDOWN ===")
for k, v in sorted(outcome_counts.items()):
    print(f"  {k}: {v}")

# ─────────────────────────────────────────────────────────────────────────────
# 6. HIGH-SIGNAL GATE EVALUATION
# ─────────────────────────────────────────────────────────────────────────────
coverage = data["coverage"]["coverage_ratio"]
success_rate_raw = data["learning"]["run_comparison"]["current_success_rate_raw"]
ml_ran = data["learning"]["meta_learning_pipeline"]["pipeline_ran"]
ml_exp = data["learning"]["meta_learning_pipeline"]["total_experiences"]
prior_run = data["learning"]["run_comparison"].get("previous_run_id") or ""

total_found_all = sum(agent_found.values())
total_fixed_all = sum(agent_fixed.values())
total_skipped_v = sum(agent_skipped_viols.values())
actionable_found = total_found_all - total_skipped_v
fix_rate = total_fixed_all / actionable_found if actionable_found > 0 else None

error_actions = [a for a in actions if a["outcome"] == "ERROR"]
territories_seen = set(a["territory"] for a in actions)

print()
print("=" * 72)
print("  HIGH-SIGNAL EFFECTIVENESS GATE SUMMARY")
print("=" * 72)
print()
print(f"  {'Gate':<5} {'Criterion':<38} {'Target':<12} {'Actual':<16} Result")
print(f"  {'-' * 5} {'-' * 38} {'-' * 12} {'-' * 16} ------")


def row(num, criterion, target, actual_str, result, note=""):
    tag = "✓ PASS" if result is True else "✗ FAIL" if result is False else "~ N/A"
    print(f"  G{num:<4} {criterion:<38} {target:<12} {actual_str:<16} {tag}  {note}")


# G1: Agent Coverage — did every expected agent run?
g1 = coverage >= 1.0
row(1, "Agent Coverage", "100%", f"{coverage:.0%}", g1)

# G2: Territory Coverage — all territories scanned
expected_t = {
    "L0_routing",
    "L2_execution",
    "L3_orchestration",
    "L5_safety",
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_rfp",
    "apps_rg",
    "apps_shared",
    "ops_scripts",
    "tests",
    "__global__",
    ".git",
    ".vscode",
}
missing_t = expected_t - territories_seen
g2 = len(missing_t) == 0
row(
    2,
    "Territory Coverage",
    "0 missing",
    f"{len(missing_t)} missing",
    g2,
    f"missing: {missing_t}" if missing_t else "",
)

# G3: Zero crash outcomes
g3 = len(error_actions) == 0
row(3, "Zero Crash Outcomes", "0 errors", f"{len(error_actions)} errors", g3)

# G4: Fix rate on actionable violations
if fix_rate is None:
    row(4, "Actionable Fix Rate", ">=50%", "no violations", None, "no actionable violations found")
else:
    g4 = fix_rate >= 0.50
    row(
        4,
        "Actionable Fix Rate",
        ">=50%",
        f"{total_fixed_all}/{actionable_found} ({fix_rate:.0%})",
        g4,
        f"skipped_structural={total_skipped_v}",
    )

# G5: No genuine partial fixes
g5 = len(genuine_partials) == 0
row(5, "No Genuine Partial Fixes", "0", str(len(genuine_partials)), g5)

# G6: Open territory count — territories with unfixed actionable violations
g6 = open_territories == 0
row(6, "All Territories Clean", "0 open", f"{open_territories} open", g6, "(manual-only violations excluded)")

# G7: Raw run success rate
g7 = success_rate_raw >= 0.70
row(7, "Run Success Rate", ">=0.70", f"{success_rate_raw:.4f}", g7)

# G8: Meta-learning pipeline active
g8 = ml_ran and ml_exp >= 1
row(8, "Meta-Learning Active", "ran + exp>=1", f"ran={ml_ran} exp={ml_exp}", g8)

# G9: Territory regression (N/A on first run)
if not prior_run:
    row(9, "Territory Regression", "0 regressions", "N/A", None, "first run — baseline set")
else:
    row(9, "Territory Regression", "0 regressions", "TBD", None, "requires delta calc")

gates_bool = [g1, g2, g3, g4 if fix_rate is not None else True, g5, g7, g8]
passed = sum(1 for g in gates_bool if g is True)
failed = sum(1 for g in gates_bool if g is False)
na = 1 if not prior_run else 0  # G9

print()
print("=" * 72)
total_evaluated = len(gates_bool)
print(
    f"  VERDICT: {passed}/{total_evaluated} evaluated gates passed  |  {failed} FAIL  |  G6={'OPEN: ' + str(open_territories) + ' territories' if open_territories else 'CLEAN'}  |  G9=N/A (first run)"
)
print()
print("  STRUCTURAL BACKLOG (manual-only, cannot auto-fix):")
for a in actions:
    if a["outcome"] == "SKIPPED":
        m = re.search(r"(\d+) violation", a["fix_summary"] or "")
        n = int(m.group(1)) if m else 0
        if n > 0:
            print(f"    • [{a['territory']}] {a['fix_summary']}")
print()
print("  WHAT CHANGED THIS RUN:")
for agent in sorted(agent_fixed):
    fx = agent_fixed[agent]
    if fx > 0:
        print(f"    • {agent} fixed {fx} violation(s)")
print("=" * 72)
