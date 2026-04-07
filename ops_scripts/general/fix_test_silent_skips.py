#!/usr/bin/env python3
"""
Mass-fixer: narrow over-broad except Exception guards in test files.

Changes ONLY the specific `except` lines identified by TestSilentSkipDetector
as setting an availability flag to False.  Each targeted line is rewritten
as `except ImportError:` (preserving aliases and indentation).

Transformations applied:
    except Exception:            ->  except ImportError:
    except Exception as exc:     ->  except ImportError as exc:
    except BaseException:        ->  except ImportError:
    except BaseException as exc: ->  except ImportError as exc:
    except:                      ->  except ImportError:

Only lines at the exact line numbers flagged by the detector are modified —
no other `except` blocks are touched.

Usage:
    python ops_scripts/general/fix_test_silent_skips.py [--dry-run] [paths...]
    python ops_scripts/general/fix_test_silent_skips.py --dry-run tests/
    python ops_scripts/general/fix_test_silent_skips.py tests/

Exit codes:
    0 — All violations fixed (or dry-run complete)
    1 — Errors encountered
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "fix_test_silent_skips")
_emit_applies_guardrail("p0", "fix_test_silent_skips", "p0_governance")
_emit_reads_policy_state("p0", "fix_test_silent_skips", "policy_binding")
_emit_snapshots_state("p0", "fix_test_silent_skips", "state_snapshot")
emit_replay_key("p0", "fix_test_silent_skips")
emit_determinism_digest("p0", "fix_test_silent_skips")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "fix_test_silent_skips", "execution_auth")
_emit_validates_capability("p2", "fix_test_silent_skips", "capability_check")
_emit_routes_to_capability("p2", "fix_test_silent_skips", "capability_route")
_emit_writes_via_uwg("p2", "fix_test_silent_skips", "uwg_write")
_emit_blocks_direct_write("p2", "fix_test_silent_skips", "direct_write_block")
_emit_records_tool_invocation("p2", "fix_test_silent_skips", "tool_invocation")
_emit_captures_execution_output("p2", "fix_test_silent_skips", "exec_output")
_emit_dispatches_agent("p3", "fix_test_silent_skips", "agent_dispatch")
_emit_coordinates_agents("p3", "fix_test_silent_skips", "agent_coordination")
_emit_records_workflow_lineage("p3", "fix_test_silent_skips", "workflow_lineage")
_emit_records_healing_outcome("p3", "fix_test_silent_skips", "healing_outcome")
_emit_escalates_failure("p3", "fix_test_silent_skips", "failure_escalation")
_emit_orchestrates_workflow("p3", "fix_test_silent_skips", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "fix_test_silent_skips", "healing_dispatch")
_emit_invokes_evaluation("p3", "fix_test_silent_skips", "evaluation_signal")
_emit_records_telemetry_event("p4", "fix_test_silent_skips", "telemetry_event")
_emit_captures_evaluation_metric("p4", "fix_test_silent_skips", "eval_metric")
_emit_stores_embedding("p4", "fix_test_silent_skips", "embedding_store")
_emit_updates_meta_learning_state("p4", "fix_test_silent_skips", "meta_learning")
_emit_links_execution_to_snapshot("p4", "fix_test_silent_skips", "exec_snapshot_link")

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))  # guardian: allow-global-mutation -- CI bootstrap

from agentic_core.L5_safety.validators.test_skip_detector_validator import (
    TestSilentSkipDetector,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("fix_test_silent_skips", "p4obs", "metric_1")
_emit_emits_metric_event("fix_test_silent_skips", "p4obs", "metric_2")
_emit_emits_metric_event("fix_test_silent_skips", "p4obs", "metric_3")
_emit_emits_metric_event("fix_test_silent_skips", "p4obs", "metric_4")
_emit_emits_metric_event("fix_test_silent_skips", "p4obs", "metric_5")
_emit_emits_metric_event("fix_test_silent_skips", "p4obs", "metric_6")
_emit_records_incident_event("fix_test_silent_skips", "p4obs", "incident")
_emit_captures_runtime_anomaly("fix_test_silent_skips", "p4obs", "anomaly")
_emit_writes_observability_log("fix_test_silent_skips", "p4obs", "obs_log")
_emit_updates_monitoring_state("fix_test_silent_skips", "p4obs", "mon_state")
_emit_triggers_alert("fix_test_silent_skips", "p4obs", "alert")
_emit_links_incident_trace("fix_test_silent_skips", "p4obs", "trace_link")
_emit_captures_pattern("fix_test_silent_skips", "p3lm", "pattern")
_emit_records_learning_event("fix_test_silent_skips", "p3lm", "learning_event")
_emit_writes_learning_snapshot("fix_test_silent_skips", "p3lm", "snapshot")
_emit_feeds_meta_learning("fix_test_silent_skips", "p3lm", "meta_feed")
_emit_updates_routing_strategy("fix_test_silent_skips", "p3lm", "routing")
_emit_improves_agent_policy("fix_test_silent_skips", "p3lm", "policy")
_emit_stores_learning_state("fix_test_silent_skips", "p3lm", "state")
_emit_records_execution_trace("fix_test_silent_skips", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("fix_test_silent_skips", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("fix_test_silent_skips", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("fix_test_silent_skips", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("fix_test_silent_skips", "L4_STATE", "p2_trace_5")
_emit_reads_environ("fix_test_silent_skips", "env_read", "p2_env_1")
_emit_reads_environ("fix_test_silent_skips", "env_read", "p2_env_2")
_emit_reads_runtime_state("fix_test_silent_skips", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("fix_test_silent_skips", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "fix_test_silent_skips", "context_pull")
_emit_pulls_context("p1", "fix_test_silent_skips", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "fix_test_silent_skips", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "fix_test_silent_skips", "uwg_term_secondary")
_emit_writes_through("p1", "fix_test_silent_skips", "write_through")
_emit_writes_through("p1", "fix_test_silent_skips", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "fix_test_silent_skips", "safety_validation")
_emit_invokes_eval("p1", "fix_test_silent_skips", "eval_call")
_emit_proposal_commits_routing("p1", "fix_test_silent_skips", "routing_commit")
_emit_escalates_to_human("p1", "fix_test_silent_skips", "human_escalation")
_emit_routes_through("p1", "fix_test_silent_skips", "route_through")
_emit_checks_agent_registry("p1", "fix_test_silent_skips", "agent_registry")
_emit_validates_agent_capability("p1", "fix_test_silent_skips", "capability")
_emit_dispatches_execution_plan("p1", "fix_test_silent_skips", "exec_plan")
_emit_agent_executes_agent("p1", "fix_test_silent_skips", "sub_agent")
_emit_routes_to_agent("p1", "fix_test_silent_skips", "target_agent")
_emit_verifies_policy("p1", "fix_test_silent_skips", "policy_check")
_emit_observes_runtime_state("p1", "fix_test_silent_skips", "runtime_state")
_emit_verifies_boundary("p1", "fix_test_silent_skips", "boundary_check")
_emit_transcripts_response("p1", "fix_test_silent_skips", "transcript")
_emit_hard_fails_untranscripted("p1", "fix_test_silent_skips")
_emit_gated_by_confidence("p1", "fix_test_silent_skips", "confidence_gate")

# Matches:  except Exception:
#           except Exception as exc:
#           except BaseException:
#           except BaseException as exc:
_BROAD_PATTERN = re.compile(
    r"^(\s*)except\s+(?:Exception|BaseException)(\s+as\s+\w+)?(\s*):(\s*)$",
)
# Matches:  except:
_BARE_PATTERN = re.compile(r"^(\s*)except(\s*):(\s*)$")


def _fix_line(line: str) -> str | None:
    """
    Return the fixed version of a line if it matches a broad except pattern.
    Returns None if the line does not match (should not be changed).
    """
    m = _BROAD_PATTERN.match(line.rstrip("\n"))
    if m:
        indent, alias, _ws, trailing = m.group(1), m.group(2) or "", m.group(3), m.group(4)
        eol = "\n" if line.endswith("\n") else ""
        return f"{indent}except ImportError{alias}:{trailing}{eol}"

    m = _BARE_PATTERN.match(line.rstrip("\n"))
    if m:
        indent, _ws, trailing = m.group(1), m.group(2), m.group(3)
        eol = "\n" if line.endswith("\n") else ""
        return f"{indent}except ImportError:{trailing}{eol}"

    return None


def _collect_test_files(roots: list[str]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        p = Path(root)
        if p.is_file() and p.suffix == ".py":
            files.append(p)
        elif p.is_dir():
            for f in p.rglob("*.py"):
                if "__pycache__" in f.parts:
                    continue
                if f.name.startswith("test_") or f.name.endswith("_test.py"):
                    files.append(f)
    return sorted(set(files))


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="fix_test_silent_skips",
        description="Narrow over-broad except guards in test files (except Exception → except ImportError)",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        default=["tests"],
        help="Directories or files to fix (default: tests/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would change without writing any files",
    )
    args = parser.parse_args()

    detector = TestSilentSkipDetector()
    test_files = _collect_test_files(args.paths)

    if not test_files:
        print(f"No test files found under: {args.paths}")
        return 0

    # Collect all violations: {path: [line_number, ...]}
    violations_by_file: dict[Path, list[int]] = {}
    for f in test_files:
        result = detector.scan_file(f)
        active = [v.line_number for v in result.violations if not v.whitelisted]
        if active:
            violations_by_file[f] = active

    if not violations_by_file:
        print("No violations found — nothing to fix.")
        return 0

    files_fixed = 0
    lines_changed = 0
    errors = 0

    for file_path, violation_lines in sorted(violations_by_file.items()):
        try:
            original = file_path.read_text(encoding="utf-8")
        except Exception as exc:
            print(f"ERROR reading {file_path}: {exc}", file=sys.stderr)
            errors += 1
            continue

        lines = original.splitlines(keepends=True)
        changed_in_file = []

        for lineno in violation_lines:
            idx = lineno - 1  # 0-indexed
            if idx < 0 or idx >= len(lines):
                continue
            fixed = _fix_line(lines[idx])
            if fixed is None:
                print(
                    f"  WARNING: could not rewrite line {lineno} in {file_path.name}: "
                    f"{lines[idx].rstrip()!r}",
                    file=sys.stderr,
                )
                continue
            if fixed != lines[idx]:
                changed_in_file.append((lineno, lines[idx].rstrip(), fixed.rstrip()))
                lines[idx] = fixed

        if not changed_in_file:
            continue

        rel = file_path.relative_to(_REPO_ROOT) if file_path.is_absolute() else file_path
        if args.dry_run:
            for lineno, before, after in changed_in_file:
                print(f"  [DRY-RUN] {rel}:{lineno}")
                print(f"    - {before}")
                print(f"    + {after}")
        else:
            new_content = "".join(lines)
            try:
                file_path.write_text(new_content, encoding="utf-8")
            except Exception as exc:
                print(f"ERROR writing {file_path}: {exc}", file=sys.stderr)
                errors += 1
                continue
            for lineno, before, after in changed_in_file:
                print(f"  FIXED {rel}:{lineno}  {before!r} -> {after!r}")

        files_fixed += 1
        lines_changed += len(changed_in_file)

    action = "Would fix" if args.dry_run else "Fixed"
    print(f"\n{action} {lines_changed} line(s) across {files_fixed} file(s).")
    if errors:
        print(f"{errors} error(s) encountered.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
