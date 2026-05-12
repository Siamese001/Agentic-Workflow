"""
Hook Consolidation / Growth CI Gate

Detects hook proliferation and validates hook metadata integrity.
Parses .windsurf/hooks.json to report statistics and detect growth risks.

Usage:
    python ops_scripts/ci/check_hook_consolidation.py [--advisory|--strict] [options]

Exit Codes:
    0: No issues detected (or --advisory mode with issues)
    1: Issues detected (--strict mode only)
    2: Error during execution
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


REPO_ROOT = Path(__file__).parent.parent.parent
HOOKS_JSON_PATH = REPO_ROOT / ".windsurf" / "hooks.json"

# Default thresholds
DEFAULT_MAX_HOOKS = 70  # Allow some growth from current 59
DEFAULT_MAX_LIFECYCLE_STAGES = 12  # Current: 10
DEFAULT_MAX_POST_CASCADE = 35  # Current: 27


def parse_hooks_json() -> Tuple[bool, Optional[Dict], str]:
    """
    Parse hooks.json and return structured data.
    
    Returns:
        (success, hooks_data, error_message)
    """
    if not HOOKS_JSON_PATH.exists():
        return False, None, f"hooks.json not found: {HOOKS_JSON_PATH}"
    
    try:
        content = HOOKS_JSON_PATH.read_text(encoding="utf-8")
        data = json.loads(content)
        
        hooks_by_stage = data.get("hooks", {})
        if not isinstance(hooks_by_stage, dict):
            return False, None, "hooks.json 'hooks' field is not a dict"
        
        # Parse all hooks
        all_hooks = []
        hooks_by_stage_parsed = {}
        
        for stage_name, hook_list in hooks_by_stage.items():
            if not isinstance(hook_list, list):
                continue
            
            parsed_hooks = []
            for hook in hook_list:
                if not isinstance(hook, dict):
                    continue
                
                parsed_hook = {
                    "stage": stage_name,
                    "hook_id": hook.get("hook_id"),
                    "script_path": hook.get("script_path"),
                    "survivor": hook.get("survivor", False),
                    "replacement_for": hook.get("replacement_for", []),
                    "metadata": hook.get("metadata", {}),
                    "raw": hook,
                }
                parsed_hooks.append(parsed_hook)
                all_hooks.append(parsed_hook)
            
            hooks_by_stage_parsed[stage_name] = parsed_hooks
        
        result = {
            "lifecycle_stage_count": len(hooks_by_stage_parsed),
            "hook_entry_count": len(all_hooks),
            "hooks_by_stage": hooks_by_stage_parsed,
            "all_hooks": all_hooks,
        }
        
        return True, result, ""
    
    except json.JSONDecodeError as e:
        return False, None, f"Invalid JSON in hooks.json: {e}"
    except Exception as e:
        return False, None, f"Error reading hooks.json: {e}"


def analyze_hooks(hooks_data: Dict) -> Dict:
    """
    Analyze hooks for various metrics and risks.
    
    Returns dict with:
    - counts: various statistics
    - duplicates: duplicate hook_id detection
    - missing_v2_metadata: hooks without v2 metadata
    - replacement_classification: classified replacement_for references
    - growth_indicators: metrics for growth monitoring
    """
    all_hooks = hooks_data["all_hooks"]
    hooks_by_stage = hooks_data["hooks_by_stage"]
    
    # Build set of all hook IDs for reference checking
    all_hook_ids = set(h["hook_id"] for h in all_hooks if h["hook_id"])
    
    # Basic counts
    # "Semantic survivors" = hooks with replacement_for (they consolidated other hooks)
    survivor_hooks = [h for h in all_hooks if h["replacement_for"]]
    survivor_count = len(survivor_hooks)
    replacement_count = sum(len(h["replacement_for"]) for h in survivor_hooks)
    
    # Per-stage counts
    stage_counts = {stage: len(hooks) for stage, hooks in hooks_by_stage.items()}
    
    # Check for duplicate hook_ids
    hook_ids = [h["hook_id"] for h in all_hooks if h["hook_id"]]
    seen_ids = set()
    duplicate_ids = []
    for hook_id in hook_ids:
        if hook_id in seen_ids:
            duplicate_ids.append(hook_id)
        seen_ids.add(hook_id)
    
    # Check for v2 metadata baseline
    # Current baseline: NO hooks have v2 metadata (this is expected/historical)
    # v2 metadata includes: priority, lifecycle_stage, run_mode, show_output
    hooks_with_v2 = []
    hooks_without_v2 = []
    for hook in all_hooks:
        metadata = hook["metadata"]
        # Check for essential v2 fields
        has_priority = "priority" in metadata
        has_run_mode = "run_mode" in metadata
        has_show_output = "show_output" in metadata
        has_lifecycle_stage = "lifecycle_stage" in metadata
        
        if has_priority and has_run_mode and has_show_output and has_lifecycle_stage:
            hooks_with_v2.append(hook["hook_id"])
        else:
            hooks_without_v2.append({
                "hook_id": hook["hook_id"],
                "stage": hook["stage"],
                "has": {
                    "priority": has_priority,
                    "run_mode": has_run_mode,
                    "show_output": has_show_output,
                    "lifecycle_stage": has_lifecycle_stage,
                }
            })
    
    # Classify replacement_for references
    # Build set of "deprecated" hooks (those being replaced)
    replaced_hooks = set()
    for hook in all_hooks:
        for ref in hook["replacement_for"]:
            replaced_hooks.add(ref)
    
    replacement_classification = {
        "active_ref": 0,
        "deprecated_original_ref": 0,
        "invalid_ref": 0,
        "details": [],
    }
    
    for hook in all_hooks:
        for ref in hook["replacement_for"]:
            if ref in all_hook_ids:
                # Reference points to a hook that still exists
                status = "active_ref"
            elif ref in replaced_hooks:
                # Reference points to a hook that was replaced (chain replacement)
                status = "deprecated_original_ref"
            else:
                # Reference points to a non-existent hook
                status = "invalid_ref"
            
            replacement_classification[status] += 1
            replacement_classification["details"].append({
                "survivor_hook": hook["hook_id"],
                "replaced_ref": ref,
                "classification": status,
            })
    
    # Check for deprecated/shim hooks
    deprecated_count = 0
    shim_count = 0
    for hook in all_hooks:
        metadata = hook["metadata"]
        if metadata.get("deprecated"):
            deprecated_count += 1
        if metadata.get("shim"):
            shim_count += 1
    
    # Detect growth risks
    post_cascade_count = stage_counts.get("post_cascade_response", 0)
    
    return {
        "counts": {
            "hook_entry_count": len(all_hooks),
            "lifecycle_stage_count": len(hooks_by_stage),
            "survivor_count": survivor_count,
            "replacement_mapping_count": replacement_count,
            "deprecated_count": deprecated_count,
            "shim_count": shim_count,
            "stage_counts": stage_counts,
            "post_cascade_count": post_cascade_count,
            "v2_metadata_implemented": len(hooks_with_v2),  # 0 = baseline not yet migrated
        },
        "duplicates": {
            "found": len(duplicate_ids) > 0,
            "count": len(duplicate_ids),
            "ids": duplicate_ids,
        },
        "v2_metadata_status": {
            "implemented_count": len(hooks_with_v2),
            "pending_count": len(hooks_without_v2),
            "baseline_status": "not_yet_migrated" if len(hooks_with_v2) == 0 else "partial" if len(hooks_with_v2) < len(all_hooks) else "complete",
            "note": "v2 metadata migration not yet applied to this baseline (expected for historical hooks)",
        },
        "replacement_classification": replacement_classification,
        "growth_indicators": {
            "total_hooks": len(all_hooks),
            "post_cascade_hooks": post_cascade_count,
            "stage_count": len(hooks_by_stage),
        },
    }


def check_thresholds(analysis: Dict, args) -> List[Dict]:
    """
    Check if current metrics exceed configured thresholds.
    
    Returns list of threshold violations.
    """
    violations = []
    counts = analysis["counts"]
    
    # Check max hooks
    if counts["hook_entry_count"] > args.max_hooks:
        violations.append({
            "type": "max_hooks_exceeded",
            "threshold": args.max_hooks,
            "actual": counts["hook_entry_count"],
            "severity": "warning" if counts["hook_entry_count"] <= args.max_hooks + 10 else "error",
        })
    
    # Check max lifecycle stages
    if counts["lifecycle_stage_count"] > args.max_lifecycle_stages:
        violations.append({
            "type": "max_stages_exceeded",
            "threshold": args.max_lifecycle_stages,
            "actual": counts["lifecycle_stage_count"],
            "severity": "error",
        })
    
    # Check max post_cascade_response hooks
    if counts["post_cascade_count"] > args.max_post_cascade:
        violations.append({
            "type": "max_post_cascade_exceeded",
            "threshold": args.max_post_cascade,
            "actual": counts["post_cascade_count"],
            "severity": "warning",
        })
    
    # Check data quality issues
    if analysis["duplicates"]["found"]:
        violations.append({
            "type": "duplicate_hook_ids",
            "count": analysis["duplicates"]["count"],
            "severity": "error",
        })
    
    # Check for invalid replacement references
    invalid_refs = analysis["replacement_classification"]["invalid_ref"]
    if invalid_refs > 0:
        violations.append({
            "type": "invalid_replacement_refs",
            "count": invalid_refs,
            "severity": "warning",
        })
    
    return violations


def generate_receipt(
    status: str,
    hooks_data: Dict,
    analysis: Dict,
    violations: List[Dict],
    args,
    exit_code: int,
) -> Dict:
    """Generate structured receipt for this gate run."""
    return {
        "receipt_version": "W5P3R-1.0",
        "gate_name": "check_hook_consolidation",
        "phase": "W5.P3-R",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verdict": status,
        "exit_code": exit_code,
        "mode": {
            "advisory": args.advisory,
            "strict": args.strict,
            "configured": "strict" if args.strict else "advisory",
        },
        "thresholds": {
            "max_hooks": args.max_hooks,
            "max_lifecycle_stages": args.max_lifecycle_stages,
            "max_post_cascade": args.max_post_cascade,
        },
        "hooks_summary": {
            "hook_entry_count": hooks_data["hook_entry_count"],
            "lifecycle_stage_count": hooks_data["lifecycle_stage_count"],
            "survivor_count": analysis["counts"]["survivor_count"],
            "replacement_mapping_count": analysis["counts"]["replacement_mapping_count"],
            "deprecated_count": analysis["counts"]["deprecated_count"],
            "shim_count": analysis["counts"]["shim_count"],
        },
        "hooks_by_stage": analysis["counts"]["stage_counts"],
        "v2_metadata_status": analysis["v2_metadata_status"],
        "replacement_classification": {
            "active_ref": analysis["replacement_classification"]["active_ref"],
            "deprecated_original_ref": analysis["replacement_classification"]["deprecated_original_ref"],
            "invalid_ref": analysis["replacement_classification"]["invalid_ref"],
            "total": analysis["replacement_classification"]["active_ref"] + 
                     analysis["replacement_classification"]["deprecated_original_ref"] + 
                     analysis["replacement_classification"]["invalid_ref"],
        },
        "issues": {
            "duplicates": analysis["duplicates"],
        },
        "violations": violations,
        "violation_count": len(violations),
        "has_errors": any(v.get("severity") == "error" for v in violations),
        "has_warnings": any(v.get("severity") == "warning" for v in violations),
        "paths": {
            "hooks_json": str(HOOKS_JSON_PATH.relative_to(REPO_ROOT)),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Check hook consolidation and detect growth risks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s --advisory                    # Report issues but exit 0
    %(prog)s --strict                      # Exit nonzero on issues
    %(prog)s --max-hooks 65                # Custom hook threshold
    %(prog)s --max-post-cascade 30         # Custom post-cascade threshold
    %(prog)s --artifact result.json        # Write JSON receipt
        """,
    )
    
    parser.add_argument(
        "--advisory",
        action="store_true",
        help="Report issues but exit with code 0 (default)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if issues detected",
    )
    parser.add_argument(
        "--max-hooks",
        type=int,
        default=DEFAULT_MAX_HOOKS,
        help=f"Maximum allowed hook entries (default: {DEFAULT_MAX_HOOKS})",
    )
    parser.add_argument(
        "--max-lifecycle-stages",
        type=int,
        default=DEFAULT_MAX_LIFECYCLE_STAGES,
        help=f"Maximum allowed lifecycle stages (default: {DEFAULT_MAX_LIFECYCLE_STAGES})",
    )
    parser.add_argument(
        "--max-post-cascade",
        type=int,
        default=DEFAULT_MAX_POST_CASCADE,
        help=f"Maximum allowed post_cascade_response hooks (default: {DEFAULT_MAX_POST_CASCADE})",
    )
    parser.add_argument(
        "--artifact",
        metavar="PATH",
        type=str,
        help="Write JSON receipt to specified path",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress console output",
    )
    
    args = parser.parse_args()
    
    # Determine mode
    advisory = args.advisory or (not args.advisory and not args.strict)
    strict = args.strict
    
    # Parse hooks.json
    parse_success, hooks_data, parse_error = parse_hooks_json()
    
    if not parse_success:
        error_receipt = {
            "receipt_version": "W5P3-1.0",
            "gate_name": "check_hook_consolidation",
            "phase": "W5.P3",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verdict": "ERROR",
            "exit_code": 2,
            "error": parse_error,
        }
        
        if args.artifact:
            artifact_path = Path(args.artifact)
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(json.dumps(error_receipt, indent=2), encoding="utf-8")
        
        if not args.quiet:
            print(f"[ERROR] {parse_error}", file=sys.stderr)
        
        sys.exit(2)
    
    # Analyze hooks
    analysis = analyze_hooks(hooks_data)
    
    # Check thresholds
    violations = check_thresholds(analysis, args)
    
    # Determine status
    has_errors = any(v.get("severity") == "error" for v in violations)
    has_warnings = any(v.get("severity") == "warning" for v in violations)
    has_issues = has_errors or has_warnings
    
    if has_issues:
        if has_errors and strict:
            status = "FAIL"
            exit_code = 1
        else:
            status = "ADVISORY_FAIL" if has_errors else "WARN"
            exit_code = 0
    else:
        status = "PASS"
        exit_code = 0
    
    # Generate receipt
    receipt = generate_receipt(
        status=status,
        hooks_data=hooks_data,
        analysis=analysis,
        violations=violations,
        args=args,
        exit_code=exit_code,
    )
    
    # Write artifact if requested
    if args.artifact:
        artifact_path = Path(args.artifact)
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    
    # Console output
    if not args.quiet:
        # Status line
        if status == "PASS":
            print(f"[PASS] Hook consolidation check passed")
        elif status == "WARN":
            print(f"[WARN] Hook consolidation warnings detected")
        elif status == "ADVISORY_FAIL":
            print(f"[ADVISORY_FAIL] Hook consolidation errors detected")
        else:
            print(f"[FAIL] Hook consolidation errors detected")
        
        print(f"")
        print(f"Hook Statistics:")
        print(f"  Total hook entries:          {hooks_data['hook_entry_count']}")
        print(f"  Lifecycle stages:            {hooks_data['lifecycle_stage_count']}")
        print(f"  Survivor hooks (consolidated): {analysis['counts']['survivor_count']}")
        print(f"  Replacement mappings:        {analysis['counts']['replacement_mapping_count']}")
        print(f"  Deprecated hooks:            {analysis['counts']['deprecated_count']}")
        print(f"  Shim hooks:                  {analysis['counts']['shim_count']}")
        print(f"")
        
        print(f"Hooks by Lifecycle Stage:")
        for stage, count in sorted(analysis["counts"]["stage_counts"].items()):
            print(f"  {stage}: {count}")
        print(f"")
        
        # Show threshold status
        print(f"Threshold Status:")
        print(f"  Max hooks:          {hooks_data['hook_entry_count']}/{args.max_hooks} {'✓' if hooks_data['hook_entry_count'] <= args.max_hooks else '✗'}")
        print(f"  Max stages:         {hooks_data['lifecycle_stage_count']}/{args.max_lifecycle_stages} {'✓' if hooks_data['lifecycle_stage_count'] <= args.max_lifecycle_stages else '✗'}")
        print(f"  Max post-cascade:   {analysis['counts']['post_cascade_count']}/{args.max_post_cascade} {'✓' if analysis['counts']['post_cascade_count'] <= args.max_post_cascade else '✗'}")
        print(f"")
        
        # Show v2 metadata status
        v2_status = analysis["v2_metadata_status"]
        print(f"v2 Metadata Status: {v2_status['baseline_status']}")
        print(f"  Implemented: {v2_status['implemented_count']}")
        print(f"  Pending:     {v2_status['pending_count']}")
        print(f"  Note: {v2_status['note']}")
        print(f"")
        
        # Show replacement reference classification
        rc = analysis["replacement_classification"]
        print(f"Replacement Reference Classification:")
        print(f"  Active references:      {rc['active_ref']} (point to existing hooks)")
        print(f"  Deprecated originals: {rc['deprecated_original_ref']} (replaced and removed)")
        print(f"  Invalid references:     {rc['invalid_ref']} (point to non-existent hooks)")
        print(f"")
        
        # Show issues
        if analysis["duplicates"]["found"]:
            print(f"[ERROR] Duplicate hook_ids found: {analysis['duplicates']['count']}")
            for dup_id in analysis["duplicates"]["ids"][:5]:
                print(f"        - {dup_id}")
        
        if rc["invalid_ref"] > 0:
            print(f"[WARN] Invalid replacement references: {rc['invalid_ref']}")
        
        if violations:
            print(f"")
            print(f"Threshold Violations ({len(violations)}):")
            for v in violations:
                severity_emoji = "❌" if v.get("severity") == "error" else "⚠️"
                print(f"  {severity_emoji} {v['type']}: {v.get('actual', 'N/A')} > {v.get('threshold', 'N/A')}")
        
        if status != "PASS":
            print(f"")
            if not strict and not advisory:
                print(f"[NOTE] Running in advisory mode by default.")
                print(f"       Use --strict to enforce thresholds in CI.")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
