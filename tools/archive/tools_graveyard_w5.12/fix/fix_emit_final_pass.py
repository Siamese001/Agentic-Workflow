"""Final-pass fix for all _emit_* NameErrors.

This script uses a compile-check approach: for every .py file under
agentic_core/, it tries to compile the file and catches NameError at
module level. If the missing name is one of our known emitters, it
adds the import.

Approach: Instead of parsing, we check if the file can be imported
without errors. But that's heavy. Instead, let's do a thorough text
scan that handles ALL import block patterns.
"""

import os
import re

ROOT = r"C:\Git\Agentic-Workflow"
LTC = "agentic_core.runtime.lifecycle_trace_contract"

# ALL known emitter functions from lifecycle_trace_contract
KNOWN_EMITTERS = {
    "_emit_reads_through",
    "_emit_writes_through",
    "_emit_links_incident_trace",
    "_emit_pulls_context",
    "_emit_validated_by_safety_plane",
    "_emit_execution_terminates_at_uwg",
    "_emit_invokes_eval",
    "_emit_proposal_commits_routing",
    "_emit_reads_environ",
    "_emit_reads_runtime_state",
    "_emit_captures_pattern",
    "_emit_records_learning_event",
    "_emit_writes_learning_snapshot",
    "_emit_feeds_meta_learning",
    "_emit_updates_routing_strategy",
    "_emit_improves_agent_policy",
    "_emit_stores_learning_state",
    "_emit_emits_metric_event",
    "_emit_records_incident_event",
    "_emit_captures_runtime_anomaly",
    "_emit_writes_observability_log",
    "_emit_updates_monitoring_state",
    "_emit_triggers_alert",
    "_emit_checks_agent_registry",
    "_emit_validates_agent_capability",
    "_emit_dispatches_execution_plan",
    "_emit_agent_executes_agent",
    "_emit_routes_to_agent",
    "_emit_verifies_policy",
    "_emit_observes_runtime_state",
    "_emit_verifies_boundary",
    "_emit_transcripts_response",
    "_emit_hard_fails_untranscripted",
    "_emit_gated_by_confidence",
}

fixed = 0

for base_dir in ["agentic_core", "tests", "system_learning"]:
    scan_dir = os.path.join(ROOT, base_dir)
    if not os.path.isdir(scan_dir):
        continue
    for dirpath, _, filenames in os.walk(scan_dir):
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fn)
            try:
                with open(fpath, encoding="utf-8") as f:
                    content = f.read()
            except (ValueError, TypeError, RuntimeError) as e:
                continue

            # Find ALL emitter calls in the file
            used_emitters = set()
            for emitter in KNOWN_EMITTERS:
                if emitter + "(" in content:
                    used_emitters.add(emitter)

            if not used_emitters:
                continue

            # Find ALL imported emitters (thorough scan through all import blocks)
            imported_emitters = set()
            lines = content.split("\n")
            in_import_block = False

            for line in lines:
                s = line.strip()
                if s.startswith("#"):
                    continue

                # Start of multi-line import
                if re.match(r"^from\s+\S+\s+import\s+\(", s):
                    in_import_block = True
                    # Check if any emitter is on this line
                    for e in KNOWN_EMITTERS:
                        if e in s:
                            imported_emitters.add(e)
                    continue

                if in_import_block:
                    if s == ")":
                        in_import_block = False
                        continue
                    for e in KNOWN_EMITTERS:
                        if e in s and not s.startswith("#"):
                            imported_emitters.add(e)
                    continue

                # Single-line import
                if re.match(r"^from\s+\S+\s+import\s+", s):
                    for e in KNOWN_EMITTERS:
                        if e in s:
                            imported_emitters.add(e)
                    continue

                # Function definition
                for e in KNOWN_EMITTERS:
                    if f"def {e}" in s:
                        imported_emitters.add(e)

            missing = used_emitters - imported_emitters
            if not missing:
                continue

            # Find the LAST lifecycle_trace_contract import block's closing ')'
            best_close = -1
            i = 0
            while i < len(lines):
                s = lines[i].strip()
                if LTC in lines[i] and "import" in lines[i] and "(" in lines[i]:
                    j = i + 1
                    while j < len(lines):
                        if lines[j].strip() == ")":
                            best_close = j
                            break
                        j += 1
                    i = j + 1 if j > i else i + 1
                else:
                    i += 1

            if best_close >= 0:
                # Insert missing imports before the closing ')'
                insert = [f"    {e},  # noqa: E402" for e in sorted(missing)]
                for k, il in enumerate(insert):
                    lines.insert(best_close + k, il)
            else:
                # No existing LTC import block — create one
                last_import = 0
                for i, line in enumerate(lines):
                    if line.startswith("from ") or line.startswith("import "):
                        last_import = i
                block = [f"from {LTC} import ("]
                for e in sorted(missing):
                    block.append(f"    {e},")
                block.append(")")
                for k, bl in enumerate(block):
                    lines.insert(last_import + 1 + k, bl)

            new_content = "\n".join(lines)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            fixed += 1
            rel = os.path.relpath(fpath, ROOT)
            if fixed <= 30:
                print(f"  Fixed: {rel} ({', '.join(sorted(missing))})")

if fixed > 30:
    print(f"  ... and {fixed - 30} more")
print(f"\nTotal: {fixed} files fixed")
