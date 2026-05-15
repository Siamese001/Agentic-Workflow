"""
RULES_INDEX Drift CI Gate

Detects drift between generated governance index and committed RULES_INDEX.md.
Uses generate_rules_index.py to produce fresh output and compares to committed version.

Usage:
    python ops_scripts/ci/check_rules_index_freshness.py [--advisory|--strict] [--artifact PATH]

Exit Codes:
    0: No drift detected (or --advisory mode with drift)
    1: Drift detected (strict mode only)
    2: Error during execution
"""

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


REPO_ROOT = Path(__file__).parent.parent.parent
GENERATOR_SCRIPT = REPO_ROOT / ".windsurf" / "scripts" / "generate_rules_index.py"
RULES_INDEX_PATH = REPO_ROOT / ".windsurf" / "RULES_INDEX.md"


def run_generator() -> Tuple[bool, str, str]:
    """
    Run generate_rules_index.py in dry-run mode and capture output.
    
    Returns:
        (success, generated_content, error_message)
    """
    if not GENERATOR_SCRIPT.exists():
        return False, "", f"Generator script not found: {GENERATOR_SCRIPT}"
    
    try:
        result = subprocess.run(
            [sys.executable, str(GENERATOR_SCRIPT), "--quiet"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO_ROOT),
        )
        
        if result.returncode != 0 and result.returncode != 1:
            # returncode 1 is expected from --check mode, not dry-run
            # but --quiet dry-run shouldn't return 1
            return False, "", f"Generator failed: {result.stderr}"
        
        return True, result.stdout, ""
    except subprocess.TimeoutExpired:
        return False, "", "Generator timed out after 60 seconds"
    except Exception as e:
        return False, "", f"Error running generator: {e}"


def read_committed_index() -> Tuple[bool, str, str]:
    """
    Read the committed RULES_INDEX.md file.
    
    Returns:
        (success, content, error_message)
    """
    if not RULES_INDEX_PATH.exists():
        return False, "", f"RULES_INDEX.md not found: {RULES_INDEX_PATH}"
    
    try:
        content = RULES_INDEX_PATH.read_text(encoding="utf-8")
        return True, content, ""
    except Exception as e:
        return False, "", f"Error reading RULES_INDEX.md: {e}"


def compute_diff(generated: str, committed: str) -> Dict:
    """
    Compute diff between generated and committed content.
    
    Returns dict with diff statistics and details.
    """
    gen_lines = generated.splitlines()
    commit_lines = committed.splitlines()
    
    # Simple line-by-line comparison
    added = []
    removed = []
    modified = []
    
    max_lines = max(len(gen_lines), len(commit_lines))
    
    for i in range(max_lines):
        gen_line = gen_lines[i] if i < len(gen_lines) else None
        commit_line = commit_lines[i] if i < len(commit_lines) else None
        
        if gen_line is None:
            removed.append((i + 1, commit_line))
        elif commit_line is None:
            added.append((i + 1, gen_line))
        elif gen_line != commit_line:
            modified.append((i + 1, commit_line, gen_line))
    
    return {
        "generated_lines": len(gen_lines),
        "committed_lines": len(commit_lines),
        "added_lines": len(added),
        "removed_lines": len(removed),
        "modified_lines": len(modified),
        "total_drift_lines": len(added) + len(removed) + len(modified),
        "has_drift": len(added) > 0 or len(removed) > 0 or len(modified) > 0,
    }


def extract_counts_from_content(content: str) -> Dict:
    """
    Extract governance counts from generated or committed content.
    
    Parses the summary table and metadata block to extract counts.
    """
    counts = {
        "rules": None,
        "skills": None,
        "workflows": None,
        "hook_entries": None,
        "hook_lifecycle_stages": None,
        "deprecated_skills": None,
        "redirects": None,
    }
    
    lines = content.splitlines()
    in_summary = False
    in_metadata = False
    
    for i, line in enumerate(lines):
        # Parse Summary table
        if "| Category |" in line and "Active" in line:
            in_summary = True
            continue
        
        if in_summary and line.startswith("|"):
            # Parse table row
            parts = [p.strip() for p in line.split("|")]
            parts = [p for p in parts if p]  # Remove empty
            
            if len(parts) >= 4:
                category = parts[0].lower()
                active = parts[1]
                deprecated = parts[2]
                total = parts[3]
                
                if "rules" in category:
                    counts["rules"] = int(total) if total.isdigit() else None
                elif "skills" in category and "hook" not in category:
                    counts["skills"] = int(total) if total.isdigit() else None
                    counts["deprecated_skills"] = int(deprecated) if deprecated.isdigit() else None
                elif "workflows" in category:
                    counts["workflows"] = int(total) if total.isdigit() else None
                elif "hooks" in category and "lifecycle" not in category and "stage" not in category:
                    counts["hook_entries"] = int(total) if total.isdigit() else None
                elif "hook lifecycle" in category or ("hooks" in category and "stage" in category):
                    counts["hook_lifecycle_stages"] = int(total) if total.isdigit() else None
        
        # Parse JSON metadata block
        if "```json" in line and "governance_metadata" in lines[min(i+1, len(lines)-1)]:
            in_metadata = True
            continue
        
        if in_metadata and line == "```":
            in_metadata = False
            continue
        
        if in_metadata:
            # Accumulate metadata lines
            pass
    
    # Try to extract from JSON metadata if present
    if "```json" in content:
        try:
            json_start = content.find("```json")
            json_end = content.find("```", json_start + 7)
            if json_end > json_start:
                json_block = content[json_start + 7:json_end].strip()
                metadata = json.loads(json_block)
                
                if "counts" in metadata:
                    c = metadata["counts"]
                    counts["rules"] = c.get("rules", counts["rules"])
                    counts["skills"] = c.get("skills", counts["skills"])
                    counts["workflows"] = c.get("workflows", counts["workflows"])
                    counts["hook_entries"] = c.get("hook_entries", counts["hook_entries"])
                    counts["hook_lifecycle_stages"] = c.get("hook_lifecycle_stages", counts["hook_lifecycle_stages"])
        except (json.JSONDecodeError, KeyError):
            pass
    
    return counts


def count_redirects_in_content(content: str) -> int:
    """
    Count deprecated/redirect entries in the content.
    
    Looks for deprecated skills section and redirect/stub markers.
    """
    count = 0
    lines = content.splitlines()
    in_deprecated = False
    
    for line in lines:
        # Check for deprecated section headers
        if "## Deprecated Skills" in line or "### Deprecated Skills" in line:
            in_deprecated = True
            continue
        
        if in_deprecated and line.startswith("## ") and "Skills" not in line:
            in_deprecated = False
            continue
        
        if in_deprecated and line.startswith("|") and "`" in line:
            # Count rows in deprecated skills table
            parts = line.split("|")
            if len(parts) >= 2 and "filename" not in line.lower():
                count += 1
        
        # Also check for redirect markers in skills section
        if "redirect" in line.lower() or "deprecated" in line.lower():
            if line.strip().startswith("|") and "filename" not in line.lower():
                # Count redirect entries
                pass
    
    # Alternative: count by looking for redirect marker text
    if "Redirects/Stubs Summary" in content:
        # Count deprecated skills from the Deprecated Skills section
        deprecated_section = content.find("## Deprecated Skills")
        if deprecated_section > 0:
            next_section = content.find("\n## ", deprecated_section + 20)
            if next_section < 0:
                next_section = len(content)
            section_content = content[deprecated_section:next_section]
            # Count table rows (excluding header and separator)
            table_rows = [l for l in section_content.splitlines() if l.startswith("|") and "filename" not in l.lower() and "---" not in l]
            count = max(0, len(table_rows) - 1)  # Exclude header
    
    return count


def generate_receipt(
    status: str,
    mode: str,
    drift_info: Dict,
    gen_counts: Dict,
    commit_counts: Dict,
    exit_code: int,
    advisory: bool,
    strict: bool,
) -> Dict:
    """
    Generate the JSON receipt for this gate run.
    """
    return {
        "receipt_version": "W5P2-1.0",
        "gate_name": "check_rules_index_freshness",
        "phase": "W5.P2",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verdict": status,
        "exit_code": exit_code,
        "mode": {
            "advisory": advisory,
            "strict": strict,
            "configured": "strict" if strict else "advisory" if advisory else "default",
        },
        "drift": {
            "detected": drift_info["has_drift"],
            "generated_lines": drift_info["generated_lines"],
            "committed_lines": drift_info["committed_lines"],
            "added_lines": drift_info["added_lines"],
            "removed_lines": drift_info["removed_lines"],
            "modified_lines": drift_info["modified_lines"],
            "total_drift_lines": drift_info["total_drift_lines"],
        },
        "counts": {
            "generated": gen_counts,
            "committed": commit_counts,
        },
        "paths": {
            "generator_script": str(GENERATOR_SCRIPT.relative_to(REPO_ROOT)),
            "rules_index": str(RULES_INDEX_PATH.relative_to(REPO_ROOT)),
        },
        "action_required": "regenerate" if drift_info["has_drift"] else None,
        "regenerate_command": "python .cursor/scripts/generate_rules_index.py --write" if drift_info["has_drift"] else None,
        "advisory_note": "Drift detected but exiting 0 due to --advisory mode" if (drift_info["has_drift"] and advisory) else None,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Check RULES_INDEX.md freshness against generator output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s --advisory                    # Report drift but exit 0
    %(prog)s --strict                      # Exit nonzero on drift
    %(prog)s --artifact drift.json         # Write receipt to file
    %(prog)s --strict --artifact result.json # Full strict mode with artifact
        """,
    )
    
    parser.add_argument(
        "--advisory",
        action="store_true",
        help="Report drift but exit with code 0 (default if neither --advisory nor --strict)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if drift detected",
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
        help="Suppress console output (receipt still written if --artifact specified)",
    )
    
    args = parser.parse_args()
    
    # Determine mode
    advisory = args.advisory or (not args.advisory and not args.strict)
    strict = args.strict
    
    # Run generator to get fresh output
    gen_success, generated_content, gen_error = run_generator()
    
    if not gen_success:
        error_receipt = {
            "receipt_version": "W5P2-1.0",
            "gate_name": "check_rules_index_freshness",
            "phase": "W5.P2",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verdict": "ERROR",
            "exit_code": 2,
            "error": gen_error,
        }
        
        if args.artifact:
            artifact_path = Path(args.artifact)
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(json.dumps(error_receipt, indent=2), encoding="utf-8")
        
        if not args.quiet:
            print(f"[ERROR] {gen_error}", file=sys.stderr)
        
        sys.exit(2)
    
    # Read committed RULES_INDEX.md
    commit_success, committed_content, commit_error = read_committed_index()
    
    if not commit_success:
        # No committed index exists - this is a special case
        drift_info = {
            "generated_lines": len(generated_content.splitlines()),
            "committed_lines": 0,
            "added_lines": len(generated_content.splitlines()),
            "removed_lines": 0,
            "modified_lines": 0,
            "total_drift_lines": len(generated_content.splitlines()),
            "has_drift": True,
        }
        
        gen_counts = extract_counts_from_content(generated_content)
        gen_counts["redirects"] = count_redirects_in_content(generated_content)
        
        receipt = generate_receipt(
            status="NO_COMMITTED_INDEX",
            mode="strict" if strict else "advisory",
            drift_info=drift_info,
            gen_counts=gen_counts,
            commit_counts={},
            exit_code=1 if strict else 0,
            advisory=advisory,
            strict=strict,
        )
        
        if args.artifact:
            artifact_path = Path(args.artifact)
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        
        if not args.quiet:
            print("[WARN] No committed RULES_INDEX.md found")
            print(f"[INFO] Generated content: {drift_info['generated_lines']} lines")
            print("[ACTION] Run: python .cursor/scripts/generate_rules_index.py --write")
        
        sys.exit(1 if strict else 0)
    
    # Compute diff
    drift_info = compute_diff(generated_content, committed_content)
    
    # Extract counts from both
    gen_counts = extract_counts_from_content(generated_content)
    commit_counts = extract_counts_from_content(committed_content)
    gen_counts["redirects"] = count_redirects_in_content(generated_content)
    commit_counts["redirects"] = count_redirects_in_content(committed_content)
    
    # Determine status
    if drift_info["has_drift"]:
        if strict:
            status = "FAIL"
            exit_code = 1
        else:
            status = "ADVISORY_FAIL"
            exit_code = 0
    else:
        status = "PASS"
        exit_code = 0
    
    # Generate receipt
    receipt = generate_receipt(
        status=status,
        mode="strict" if strict else "advisory",
        drift_info=drift_info,
        gen_counts=gen_counts,
        commit_counts=commit_counts,
        exit_code=exit_code,
        advisory=advisory,
        strict=strict,
    )
    
    # Write artifact if requested
    if args.artifact:
        artifact_path = Path(args.artifact)
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    
    # Console output
    if not args.quiet:
        # Status line with color codes
        if status == "PASS":
            print(f"[PASS] RULES_INDEX.md is up to date")
        elif status == "ADVISORY_FAIL":
            print(f"[ADVISORY_FAIL] Drift detected between generated and committed RULES_INDEX.md")
        else:
            print(f"[FAIL] Drift detected between generated and committed RULES_INDEX.md")
        
        print(f"")
        print(f"Drift Statistics:")
        print(f"  Generated lines:   {drift_info['generated_lines']}")
        print(f"  Committed lines:   {drift_info['committed_lines']}")
        print(f"  Added:             {drift_info['added_lines']}")
        print(f"  Removed:           {drift_info['removed_lines']}")
        print(f"  Modified:          {drift_info['modified_lines']}")
        print(f"  Total drift lines: {drift_info['total_drift_lines']}")
        print(f"")
        
        print(f"Governance Counts (Generated vs Committed):")
        for key in ["rules", "skills", "workflows", "hook_entries", "hook_lifecycle_stages"]:
            gen_val = gen_counts.get(key, "N/A")
            commit_val = commit_counts.get(key, "N/A")
            marker = "✓" if gen_val == commit_val and gen_val is not None else "✗" if gen_val != commit_val else "?"
            print(f"  {marker} {key}: {gen_val} vs {commit_val}")
        
        print(f"")
        
        if drift_info["has_drift"]:
            print(f"[ACTION] To refresh RULES_INDEX.md, run:")
            print(f"         python .cursor/scripts/generate_rules_index.py --write")
            
            if not strict and not advisory:
                print(f"")
                print(f"[NOTE] This gate runs in advisory mode by default.")
                print(f"       Use --strict to enforce freshness in CI.")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
