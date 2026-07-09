"""Build markdown report from SSOT dry-run JSON results + stderr log."""
import json
import logging
import re
from collections import defaultdict

from tqdm import tqdm

from agentic_core.L0_routing.config.path_constants import DOCS_REPORTS_DIR
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "_build_ssot_report", "uwg_governed_write")
_emit_writes_through("p1", "_build_ssot_report", "uwg_governed_write_2")
_emit_pulls_context("p1", "_build_ssot_report", "context_retrieval")
_emit_pulls_context("p1", "_build_ssot_report", "context_retrieval_2")
emit_determinism_digest("trace__build_ssot_report", "_build_ssot_report_dispatch")
emit_determinism_digest("trace__build_ssot_report", "_build_ssot_report_complete")
_emit_validated_by_safety_plane("p1", "_build_ssot_report", "safety_validation")
data = json.load(open("_ssot_results_v2.json", encoding="utf-8"))
logging.info("C3 write receipt: ops_scripts/root_scripts/_build_ssot_report.py write side effect recorded")
stderr = open("_ssot_stderr_v2.log", encoding="utf-8").read()
lines = []
W = lines.append
W("# SSOT Dry-Run Report: agentic_core/")
W("")
W("**Date**: 2026-02-11")
W("**Branch**: `agentic-core-v5.3`")
W("**Mode**: `--dry-run` (no file mutations)")
W("**Entrypoint**: `execute_ssot_entrypoint.py --legacy --dry-run`")
W("")
W("## Executive Summary")
W("")
agents_ok = data["agents_available"]
agents_fail = data["agents_failed_import"]
W(f"- **Agents importable**: {len(agents_ok)}/{len(agents_ok) + len(agents_fail)}")
W(
    f"- **Agents failed import**: {len(agents_fail)} (`{('`, `'.join(agents_fail) if agents_fail else 'none')}`)"
)
W(f"- **Territories scanned**: {len(data['territories_scanned'])}")
W(f"- **Layer violations (FCA)**: {len(data['layer_violations'])}")
W("")
W("## Agent Import Status")
W("")
W("| Agent | Status | Error |")
W("|---|---|---|")
for name, info in data["import_results"].items():
    status = info["status"]
    err = info.get("error", "—")[:120].replace("|", "\\|") if info.get("error") else "—"
    icon = "✅" if status == "OK" else "❌"
    W(f"| `{name}` | {icon} {status} | {err} |")
W("")
W("## Blocking Issues (Pre-existing)")
W("")
W("These pre-existing issues prevented full SSOT pipeline execution:")
W("")
sovereign_lock_count = stderr.count("CORE INTEGRITY COMPROMISED")
atomic_mixin_count = stderr.count("AtomicExecutionMixin")
struct_validator_count = stderr.count("StructuralValidatorAgent_types")
W(
    f"1. **SovereignLockError** ({sovereign_lock_count} occurrences) — Core integrity hash mismatch blocks LocationAgent, LocationValidatorAgent, SystemArchitectAgent, RootHygieneAgent. The sovereign core hash has drifted from the expected baseline."
)
W(
    f"2. **AtomicExecutionMixin NameError** ({atomic_mixin_count} occurrences) — HierarchyAgent fails to import because `AtomicExecutionMixin` is not defined. This blocks the standard `execute_ssot_entrypoint.py` from running at all (mandatory import)."
)
W(
    f"3. **StructuralValidatorAgent_types** ({struct_validator_count} occurrences) — ArchitectureGovernorAgent's guardian scan fails due to missing module `StructuralValidatorAgent_types`."
)
W("")
W("## Per-Territory Agent Results")
W("")
for territory in tqdm(data["territories_scanned"], desc="Processing", unit="item"):
    t_results = data["territory_results"].get(territory, {})
    W(f"### {territory}")
    W("")
    W("| Agent | Status | Result |")
    W("|---|---|---|")
    for agent_name, result in tqdm(t_results.items(), desc="Processing", unit="item"):
        if result.get("success"):
            r = result.get("result", {})
            if isinstance(r, dict):
                vf = r.get("violations_found", r.get("stats", {}).get("violations_found", "—"))
                vx = r.get("violations_fixed", "—")
                detail = f"violations_found={vf}, violations_fixed={vx}"
                ac = r.get("action_counters")
                if ac:
                    detail += (
                        f", renames={ac.get('renames', 0)}, territory_moves={ac.get('territory_moves', 0)}"
                    )
            else:
                detail = str(r)[:150]
            W(f"| `{agent_name}` | ✅ | {detail} |")
        else:
            err = result.get("error", "unknown")[:100].replace("|", "\\|")
            W(f"| `{agent_name}` | ❌ | {err} |")
    W("")
W("## FCA Proposed Renames (File Diffs)")
W("")
W(
    "These are all `[DETECT]` findings from FileClassificationAgent across all territories, showing proposed file renames:"
)
W("")
detect_lines = re.findall("\\[DETECT\\] (.+?) -> (.+?)$", stderr, re.MULTILINE)
rename_by_territory = defaultdict(list)
current_territory = None
for line in stderr.split("\n"):
    if "heal_repository(" in line and "FileClassificationAgent" in line:
        m = re.search("heal_repository\\((\\w+)\\)", line)
        if m:
            current_territory = m.group(1)
    if "[DETECT]" in line and current_territory:
        m = re.search("\\[DETECT\\] (.+?) \\((\\w+)\\) -> (.+)", line)
        if m:
            old_name, ftype, new_name = (m.group(1), m.group(2), m.group(3))
            rename_by_territory[current_territory].append((old_name, ftype, new_name))
total_renames = sum(len(v) for v in rename_by_territory.values())
W(f"**Total proposed renames**: {total_renames}")
W("")
for territory in tqdm(data["territories_scanned"], desc="Processing", unit="item"):
    renames = rename_by_territory.get(territory, [])
    if renames:
        W(f"### {territory} ({len(renames)} renames)")
        W("")
        W("| Current Name | FileType | Proposed Name |")
        W("|---|---|---|")
        for old, ftype, new in renames[:50]:
            W(f"| `{old}` | {ftype} | `{new}` |")
        if len(renames) > 50:
            W(f"| ... | ... | +{len(renames) - 50} more |")
        W("")
W("## FCA Other Findings (from stderr)")
W("")
other_tags = [
    "TERRITORY",
    "FOLDER_PURITY",
    "FOLDER_SUFFIX",
    "COMPOUND_SUFFIX",
    "FORBIDDEN",
    "PASSIVE_AGENT_NAMING",
    "DUAL-TAG",
    "CROSS_LAYER",
    "CROSS_DOMAIN",
    "EPHEMERAL",
    "FAKE_CONFIG",
    "MISPLACED-TEST",
]
for tag in tqdm(other_tags, desc="Processing", unit="item"):
    tag_lines = re.findall(f"\\[{re.escape(tag)}\\] (.+?)$", stderr, re.MULTILINE)
    if tag_lines:
        unique = sorted(set(tag_lines))
        W(f"### {tag} ({len(unique)} unique)")
        W("")
        for line in unique[:30]:
            W(f"- `{line[:150]}`")
        if len(unique) > 30:
            W(f"- ... +{len(unique) - 30} more")
        W("")
W("## Layer Alignment Violations (FCA validate_layer_alignment)")
W("")
W("| Violation Type | Count |")
W("|---|---|")
for vtype, count in sorted(data["layer_violation_counts"].items(), key=lambda x: -x[1]):
    W(f"| `{vtype}` | {count} |")
W("")
layer_by_type = defaultdict(list)
for v in data["layer_violations"]:
    layer_by_type[v["violation"]].append(v)
for vtype in tqdm(sorted(layer_by_type.keys()), desc="Processing", unit="item"):
    items = layer_by_type[vtype]
    W(f"### {vtype} ({len(items)})")
    W("")
    if vtype == "AGENT_LAYER_MISPLACEMENT":
        W("| File | Current | Suggested | Confidence | Evidence |")
        W("|---|---|---|---|---|")
        for v in items:
            ev = ", ".join(v.get("evidence", [])[:3])
            W(
                f"| `{v['file']}` | {v.get('current_layer', '')} | {v.get('suggested_layer', '')} | {v.get('confidence', '')} | {ev} |"
            )
    elif vtype == "NON_AGENT_IN_REASONING":
        W("| File | Message |")
        W("|---|---|")
        for v in items[:40]:
            msg = v.get("message", "")[:120].replace("|", "\\|")
            W(f"| `{v['file']}` | {msg} |")
        if len(items) > 40:
            W(f"| ... | +{len(items) - 40} more |")
    else:
        for v in items[:20]:
            msg = v.get("message", str(v))[:150].replace("|", "\\|")
            W(f"- `{v['file']}`: {msg}")
        if len(items) > 20:
            W(f"- ... +{len(items) - 20} more")
    W("")
W("## ArchitectureGovernorAgent Audit Results")
W("")
for territory in tqdm(data["territories_scanned"], desc="Processing", unit="item"):
    t_results = data["territory_results"].get(territory, {})
    gov = t_results.get("ArchitectureGovernorAgent", {})
    if gov.get("success"):
        r = gov["result"]
        if isinstance(r, dict) and "stats" in r:
            stats = r["stats"]
            W(f"### {territory}")
            W("")
            W(f"- violations_found: {stats.get('violations_found', 0)}")
            W(f"- drift_detected: {stats.get('drift_detected', 0)}")
            W(f"- files_scanned: {stats.get('files_scanned', '?')}")
            W("")
W("## Test Cases & Regression Guards")
W("")
W("Based on the findings above, these tests should be run or added:")
W("")
W("### Existing Guardian Tests")
W("")
W("```bash")
W("# Full folder purity hardening suite (includes reasoning/ purity ratchet)")
W("pytest tests/guardian/test_folder_purity_hardening.py -v")
W("")
W("# Architecture governance tests")
W("pytest tests/guardian/test_architecture_governance.py -v")
W("")
W("# MECE naming compliance")
W("pytest tests/guardian/test_mece_naming_compliance.py -v")
W("")
W("# Agent inventory contract (L4)")
W("pytest tests/agentic_core/L4_state/test_l4_state_agent_inventory_contract.py -v")
W("```")
W("")
W("### Recommended New Tests")
W("")
W(
    "1. **SovereignLock hash baseline update** — The sovereign core hash has drifted. Either update the expected hash or investigate what changed."
)
W(
    "2. **AtomicExecutionMixin resolution** — Fix the missing `AtomicExecutionMixin` in `HierarchyAgent.py` (blocks entire SSOT pipeline)."
)
W(
    "3. **StructuralValidatorAgent_types module** — Stale import reference in ArchitectureGovernorAgent's guardian scan."
)
W(
    "4. **FilesystemSSOTReconcilerAgent.heal_repository** — Missing `target_territory` parameter support (TypeError on invocation)."
)
W("")
report_path = f"{DOCS_REPORTS_DIR}/plans/ssot_dry_run_agentic_core.md"
with open(report_path, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines))
print(f"Report written to {report_path}")
print(f"  Total proposed renames: {total_renames}")
print(f"  Layer violations: {len(data['layer_violations'])}")
