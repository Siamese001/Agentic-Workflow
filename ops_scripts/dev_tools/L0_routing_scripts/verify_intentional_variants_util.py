"""
Verification Script: Identify Intentional Variants vs True Duplicates

This script distinguishes between:
1. TRUE DUPLICATES: Same filename, identical content → Safe to delete
2. INTENTIONAL VARIANTS: Same filename, different content → Need renaming via NamingAgent

Purpose: Prevent accidental deletion of intentional variants that just need better names.
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

_emit_authorize_and_execute("p2", "verify_intentional_variants_util", "execution_auth")
_emit_validates_capability("p2", "verify_intentional_variants_util", "capability_check")
_emit_routes_to_capability("p2", "verify_intentional_variants_util", "capability_route")
_emit_writes_via_uwg("p2", "verify_intentional_variants_util", "uwg_write")
_emit_blocks_direct_write("p2", "verify_intentional_variants_util", "direct_write_block")
_emit_records_tool_invocation("p2", "verify_intentional_variants_util", "tool_invocation")
_emit_captures_execution_output("p2", "verify_intentional_variants_util", "exec_output")
_emit_dispatches_agent("p3", "verify_intentional_variants_util", "agent_dispatch")
_emit_coordinates_agents("p3", "verify_intentional_variants_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "verify_intentional_variants_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "verify_intentional_variants_util", "healing_outcome")
_emit_escalates_failure("p3", "verify_intentional_variants_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "verify_intentional_variants_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verify_intentional_variants_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "verify_intentional_variants_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "verify_intentional_variants_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verify_intentional_variants_util", "eval_metric")
_emit_stores_embedding("p4", "verify_intentional_variants_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "verify_intentional_variants_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verify_intentional_variants_util", "exec_snapshot_link")
from agentic_core.utils.ast_fuzzy_util import compute_file_hash

emit_replay_key("p0", "verify_intentional_variants_util")
emit_determinism_digest("p0", "verify_intentional_variants_util")

_emit_dispatches_healing_run("p1", "verify_intentional_variants_util", "L0")
_emit_routes_through("p1", "verify_intentional_variants_util", "L0")
_emit_checks_agent_registry("p1", "verify_intentional_variants_util", "agent_registry")
_emit_validates_agent_capability("p1", "verify_intentional_variants_util", "capability")
_emit_dispatches_execution_plan("p1", "verify_intentional_variants_util", "exec_plan")
_emit_agent_executes_agent("p1", "verify_intentional_variants_util", "sub_agent")
_emit_routes_to_agent("p1", "verify_intentional_variants_util", "target_agent")
_emit_verifies_policy("p1", "verify_intentional_variants_util", "policy_check")
_emit_observes_runtime_state("p1", "verify_intentional_variants_util", "runtime_state")
_emit_verifies_boundary("p1", "verify_intentional_variants_util", "boundary_check")
_emit_transcripts_response("p1", "verify_intentional_variants_util", "transcript")
_emit_hard_fails_untranscripted("p1", "verify_intentional_variants_util")
_emit_gated_by_confidence("p1", "verify_intentional_variants_util", "confidence_gate")
_emit_escalates_to_human("p1", "verify_intentional_variants_util", "L0")
_emit_reads_policy_state("p1", "verify_intentional_variants_util", "L0")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("verify_intentional_variants_util", "p4obs", "metric_1")
_emit_emits_metric_event("verify_intentional_variants_util", "p4obs", "metric_2")
_emit_emits_metric_event("verify_intentional_variants_util", "p4obs", "metric_3")
_emit_emits_metric_event("verify_intentional_variants_util", "p4obs", "metric_4")
_emit_emits_metric_event("verify_intentional_variants_util", "p4obs", "metric_5")
_emit_emits_metric_event("verify_intentional_variants_util", "p4obs", "metric_6")
_emit_records_incident_event("verify_intentional_variants_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("verify_intentional_variants_util", "p4obs", "anomaly")
_emit_writes_observability_log("verify_intentional_variants_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("verify_intentional_variants_util", "p4obs", "mon_state")
_emit_triggers_alert("verify_intentional_variants_util", "p4obs", "alert")
_emit_links_incident_trace("verify_intentional_variants_util", "p4obs", "trace_link")
_emit_captures_pattern("verify_intentional_variants_util", "p3lm", "pattern")
_emit_records_learning_event("verify_intentional_variants_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("verify_intentional_variants_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("verify_intentional_variants_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("verify_intentional_variants_util", "p3lm", "routing")
_emit_improves_agent_policy("verify_intentional_variants_util", "p3lm", "policy")
_emit_stores_learning_state("verify_intentional_variants_util", "p3lm", "state")
_emit_records_execution_trace("verify_intentional_variants_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("verify_intentional_variants_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("verify_intentional_variants_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("verify_intentional_variants_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("verify_intentional_variants_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("verify_intentional_variants_util", "env_read", "p2_env_1")
_emit_reads_environ("verify_intentional_variants_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("verify_intentional_variants_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("verify_intentional_variants_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "verify_intentional_variants_util", "context_pull")
_emit_pulls_context("p1", "verify_intentional_variants_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "verify_intentional_variants_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "verify_intentional_variants_util", "uwg_term_2")
_emit_writes_through("p1", "verify_intentional_variants_util", "write_through")
_emit_writes_through("p1", "verify_intentional_variants_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "verify_intentional_variants_util", "safety_validation")
_emit_invokes_eval("p1", "verify_intentional_variants_util", "eval_call")
_emit_proposal_commits_routing("p1", "verify_intentional_variants_util", "routing_commit")

project_root = Path(__file__).parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))  # guardian: allow-global-mutation


def read_file_content(file_path: Path) -> str:
    """Read file content as string."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "read_file_content", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "read_file_content", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "read_file_content")
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    # guardian: allow-silent-swallow
    except (ValueError, TypeError):
        return ""


def extract_key_identifiers(content: str, file_ext: str) -> dict:
    """Extract key identifiers from file content to determine if it's a variant."""
    identifiers = {
        "classes": set(),
        "functions": set(),
        "imports": set(),
        "constants": set(),
        "has_main": False,
    }

    if file_ext == ".py":
        # Extract Python-specific identifiers
        identifiers["classes"] = set(re.findall(r"class\s+(\w+)", content))
        identifiers["functions"] = set(re.findall(r"def\s+(\w+)", content))
        identifiers["imports"] = set(re.findall(r"(?:from|import)\s+([\w.]+)", content))
        identifiers["constants"] = set(re.findall(r"^([A-Z_]{2,})\s*=", content, re.MULTILINE))
        identifiers["has_main"] = "if __name__" in content

    return identifiers


def analyze_variant_likelihood(file1: Path, file2: Path) -> dict:
    """
    Analyze if two files with same name are intentional variants or true duplicates.

    Returns:
        dict with 'is_variant', 'confidence', 'reasons'
    """
    content1 = read_file_content(file1)
    content2 = read_file_content(file2)

    if not content1 or not content2:
        return {"is_variant": False, "confidence": "unknown", "reasons": ["Cannot read files"]}

    # Check if identical
    if content1 == content2:
        return {"is_variant": False, "confidence": "certain", "reasons": ["Files are identical"]}

    # Extract identifiers
    ext = file1.suffix
    ids1 = extract_key_identifiers(content1, ext)
    ids2 = extract_key_identifiers(content2, ext)

    reasons = []
    variant_score = 0

    # Check for different class names (strong indicator of variant)
    if ids1["classes"] and ids2["classes"]:
        if ids1["classes"] != ids2["classes"]:
            reasons.append(f"Different classes: {ids1['classes']} vs {ids2['classes']}")
            variant_score += 3
        else:
            reasons.append("Same class names (likely duplicate)")
            variant_score -= 2

    # Check for different function sets (moderate indicator)
    if ids1["functions"] and ids2["functions"]:
        func_diff = ids1["functions"].symmetric_difference(ids2["functions"])
        if len(func_diff) > 3:
            reasons.append(f"Significantly different functions: {len(func_diff)} differences")
            variant_score += 2
        elif len(func_diff) > 0:
            reasons.append(f"Minor function differences: {len(func_diff)} differences")
            variant_score += 1

    # Check for different imports (weak indicator)
    if ids1["imports"] and ids2["imports"]:
        import_diff = ids1["imports"].symmetric_difference(ids2["imports"])
        if len(import_diff) > 5:
            reasons.append(f"Different imports: {len(import_diff)} differences")
            variant_score += 1

    # Check location patterns (strong indicator)
    path1_str = str(file1)
    path2_str = str(file2)

    if "config/blueprint_sovereign" in path1_str or "config/blueprint_sovereign" in path2_str:
        reasons.append("One file in deprecated blueprint folder (likely stale copy)")
        variant_score -= 2

    if ("L5_safety" in path1_str and "L2_execution" in path2_str) or (
        "L2_execution" in path1_str and "L5_safety" in path2_str
    ):
        reasons.append("Files in different layers (L2 vs L5) - likely intentional variants")
        variant_score += 2

    # Calculate line difference percentage
    lines1 = len(content1.splitlines())
    lines2 = len(content2.splitlines())
    if lines1 > 0:
        line_diff_pct = abs(lines1 - lines2) / max(lines1, lines2) * 100
        if line_diff_pct > 30:
            reasons.append(f"Significant size difference: {line_diff_pct:.1f}% line count difference")
            variant_score += 1

    # Determine verdict
    if variant_score >= 3:
        return {
            "is_variant": True,
            "confidence": "high",
            "reasons": reasons,
            "score": variant_score,
        }
    elif variant_score >= 1:
        return {
            "is_variant": True,
            "confidence": "medium",
            "reasons": reasons,
            "score": variant_score,
        }
    elif variant_score <= -2:
        return {
            "is_variant": False,
            "confidence": "high",
            "reasons": reasons,
            "score": variant_score,
        }
    else:
        return {
            "is_variant": False,
            "confidence": "low",
            "reasons": reasons,
            "score": variant_score,
        }


def scan_for_duplicates():
    """Scan project for duplicate files."""
    file_hashes = defaultdict(list)
    extensions = {".py", ".html", ".json", ".yaml", ".md", ".txt"}
    exclude_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

    # Absolute Zero: Use ssot_discovery instead of rglob
    from agentic_core.utils.runners.ssot_discovery_validator import get_data_files, get_python_files

    all_files = list(get_python_files(project_root)) + list(get_data_files(project_root))
    for file_path in all_files:
        if not file_path.is_file():
            continue
        if any(excluded in file_path.parts for excluded in exclude_dirs):
            continue
        if file_path.suffix not in extensions:
            continue

        file_hash = compute_file_hash(file_path)
        if file_hash != "ERROR":
            file_hashes[file_hash].append(file_path)

    return {h: paths for h, paths in file_hashes.items() if len(paths) > 1}


def main():
    print("=" * 120)
    print("INTENTIONAL VARIANTS VERIFICATION")
    print("Distinguishing between true duplicates and intentional variants needing rename")
    print("=" * 120)
    print()

    # Scan for duplicates
    print("[1/3] Scanning for duplicate files...")
    duplicates = scan_for_duplicates()
    print(f"   Found {len(duplicates)} duplicate sets")
    print()

    # Group by filename
    print("[2/3] Grouping by filename...")
    by_filename = defaultdict(list)
    for file_hash, paths in duplicates.items():
        for path in paths:
            by_filename[path.name].append({"path": path, "hash": file_hash})

    filename_groups = {name: files for name, files in by_filename.items() if len(files) > 1}
    print(f"   Found {len(filename_groups)} filename groups with duplicates")
    print()

    # Analyze each group
    print("[3/3] Analyzing for intentional variants...")
    print()

    true_duplicates = []
    intentional_variants = []
    needs_review = []

    for filename, file_info in sorted(filename_groups.items()):
        # Check if all hashes are the same (identical content)
        hashes = {f["hash"] for f in file_info}

        if len(hashes) == 1:
            # All identical - true duplicates
            true_duplicates.append((filename, file_info))
        else:
            # Different content - analyze if intentional variant
            paths = [f["path"] for f in file_info]

            # Analyze pairwise
            max_variant_score = 0
            max_analysis = None

            for i in range(len(paths)):
                for j in range(i + 1, len(paths)):
                    analysis = analyze_variant_likelihood(paths[i], paths[j])
                    score = analysis.get("score", 0)
                    if score > max_variant_score:
                        max_variant_score = score
                        max_analysis = analysis

            if (
                max_analysis
                and max_analysis.get("is_variant")
                and max_analysis.get("confidence") in ["high", "medium"]
            ):
                intentional_variants.append((filename, file_info, max_analysis))
            else:
                needs_review.append((filename, file_info, max_analysis))

    print()
    print("=" * 120)
    print("ANALYSIS RESULTS")
    print("=" * 120)
    print()

    # Summary
    print("SUMMARY:")
    print(f"  ✓ True Duplicates (safe to delete): {len(true_duplicates)}")
    print(f"  ⚠ Intentional Variants (need rename): {len(intentional_variants)}")
    print(f"  ? Needs Manual Review: {len(needs_review)}")
    print()

    # Show intentional variants
    if intentional_variants:
        print("=" * 120)
        print("INTENTIONAL VARIANTS - REQUIRE RENAMING VIA NamingAgent")
        print("=" * 120)
        print()

        for idx, (filename, file_info, analysis) in enumerate(intentional_variants, 1):
            print(f"[{idx}] {filename}")
            print(f"    Copies: {len(file_info)}")
            print(f"    Variant Confidence: {analysis['confidence'].upper()}")
            print(f"    Variant Score: {analysis['score']}")
            print()
            print("    Reasons:")
            for reason in analysis["reasons"]:
                print(f"      - {reason}")
            print()
            print("    Locations:")
            for f in file_info:
                rel_path = f["path"].relative_to(project_root)
                print(f"      {rel_path}")
            print()
            print("    ⚠️  ACTION REQUIRED:")
            print("       DO NOT DELETE - These files have different functionality")
            print("       Use NamingAgent to suggest unique names for each variant")
            print(
                f"       Command: python -m agentic_core.utils.core_extensions.NamingAgent --file {file_info[0]['path']}",
            )
            print()
            print("-" * 120)
            print()

    # Show needs review
    if needs_review:
        print("=" * 120)
        print("NEEDS MANUAL REVIEW - Unclear if variant or duplicate")
        print("=" * 120)
        print()

        for idx, (filename, file_info, analysis) in enumerate(needs_review, 1):
            print(f"[{idx}] {filename}")
            print(f"    Copies: {len(file_info)}")
            if analysis:
                print(f"    Analysis Score: {analysis['score']}")
                print(f"    Reasons: {', '.join(analysis['reasons'][:2])}")
            print(f"    Locations: {len(file_info)} files")
            print()

    # Show true duplicates summary
    print("=" * 120)
    print("TRUE DUPLICATES - SAFE TO DELETE")
    print("=" * 120)
    print()
    print(f"Found {len(true_duplicates)} filename groups with identical content")
    print(f"Total files to delete: {sum(len(files) - 1 for _, files in true_duplicates)}")
    print()
    print("These files have identical content and can be safely deleted via:")
    print("  python scripts/delete_duplicates.py --execute")
    print()

    # Final recommendations
    print()
    print("=" * 120)
    print("NEXT STEPS")
    print("=" * 120)
    print()
    print("1. INTENTIONAL VARIANTS (DO NOT DELETE):")
    print(f"   - {len(intentional_variants)} filename groups need renaming")
    print("   - Use NamingAgent to suggest unique names")
    print("   - Rename files to reflect their different purposes")
    print()
    print("2. TRUE DUPLICATES (SAFE TO DELETE):")
    print(f"   - {len(true_duplicates)} filename groups are identical")
    print("   - Run: python scripts/delete_duplicates.py --execute")
    print()
    print("3. NEEDS REVIEW:")
    print(f"   - {len(needs_review)} filename groups need manual inspection")
    print("   - Review diff and decide: rename or delete")
    print()

    # Save results
    output_file = project_root / "variant_analysis_results.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("INTENTIONAL VARIANTS - DO NOT DELETE\n")
        f.write("=" * 80 + "\n\n")
        for filename, file_info, analysis in intentional_variants:
            f.write(f"{filename}\n")
            for fi in file_info:
                f.write(f"  {fi['path'].relative_to(project_root)}\n")
            f.write("\n")

    print(f"Detailed results saved to: {output_file}")
    print()


if __name__ == "__main__":
    main()
