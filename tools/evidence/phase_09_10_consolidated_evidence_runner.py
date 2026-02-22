#!/usr/bin/env python3
"""
Phase 9-10 Consolidated Evidence Runner

Generates consolidated evidence for:
- Phase 9: Evidence Contract v2 Rollout (Runners)
- Phase 10: CI Evidence Contract Enforcement (Repo-Wide)

Uses Evidence Contract v2 helper for scope isolation and self-verification.
"""

import sys
from pathlib import Path

# Add the tools/evidence directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

from evidence_contract_v2 import EvidenceContractV2


def main():
    """Generate Phases 9-10 consolidated evidence using Contract v2."""
    args = EvidenceContractV2.parse_args("Generate Phases 9-10 consolidated evidence")
    
    code_commit = args.code_commit
    evidence_commit = args.evidence_commit
    
    repo_root = Path(__file__).parent.parent.parent
    evidence_file = repo_root / "docs" / "reports" / "plans" / "phase_09_10_consolidated.md"

    print(f"Generating Phases 9-10 consolidated evidence: {evidence_file}")
    print(f"CODE_COMMIT: {code_commit}")
    if evidence_commit:
        print(f"EVIDENCE_COMMIT: {evidence_commit}")
    
    # Initialize contract helper with allowed prefixes for phases 9-10
    allowed_prefixes = {
        "apps_shared/",
        "apps_lic/", 
        "apps_rg/",
        "agentic_core/",
        "ops_scripts/",
        "tools/evidence/",
        "tests/",
        "docs/reports/plans/",
        ".github/workflows/",
        "pytest.ini",
        "docs/rules/",
    }
    
    contract = EvidenceContractV2(repo_root, allowed_prefixes)
    
    # Validate evidence contract structure
    require_evidence_commit = evidence_commit is not None
    contract.validate_evidence_contract_structure(
        code_commit, evidence_commit, require_evidence_commit
    )
    
    # Start building evidence content
    evidence_lines = []
    evidence_lines.append("# Phases 9-10: Evidence Contract v2 Rollout + CI Enforcement (Consolidated)")
    evidence_lines.append("")
    evidence_lines.append("## Scope")
    evidence_lines.append("Phase 9: Evidence Contract v2 Rollout (Runners)")
    evidence_lines.append("Phase 10: CI Evidence Contract Enforcement (Repo-Wide)")
    evidence_lines.append("")
    
    # Build evidence sections using contract helper
    inspected = [
        "tools/evidence/evidence_contract_v2.py",
        "tools/evidence/phase02_consolidated_evidence_runner.py",
        "tools/evidence/phase03_04_consolidated_evidence_runner.py",
        "tools/evidence/phase05_06_consolidated_evidence_runner.py",
        "tools/evidence/phase07_08_consolidated_evidence_runner.py",
        "tools/evidence/phase_09_10_consolidated_evidence_runner.py",
        "ops_scripts/ci/check_evidence_contract_v2.py",
        ".github/workflows/spine-determinism-guard.yml",
    ]
    
    sections = contract.build_evidence_sections(
        code_commit, evidence_commit, inspected
    )
    
    # Add formatted sections
    evidence_lines.extend(contract.format_evidence_sections(sections))
    
    # Command outputs
    commands = [
        (
            [sys.executable, "-m", "pytest", "-q"],
            "Full Test Suite",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_evidence_contract_v2.py", "--paths", "docs/reports/plans"],
            "Evidence Contract v2 Checker (Repo-Wide)",
        ),
    ]
    
    for cmd, title in commands:
        evidence_lines.append(f"## {title}")
        evidence_lines.append("```")
        evidence_lines.append(f"$ {' '.join(cmd)}")
        
        rc, out, err = contract.run_cmd(cmd)
        evidence_lines.append(out)
        if err:
            evidence_lines.append(f"STDERR: {err}")
        if rc != 0:
            evidence_lines.append(f"EXIT CODE: {rc}")
        
        evidence_lines.append("```")
        evidence_lines.append("")
    
    # Embed full contents of inspected files
    evidence_lines.append("## INSPECTED_FILE_CONTENTS")
    evidence_lines.append("")
    
    for filepath in sections["INSPECTED_FILES"]:
        full_path = repo_root / filepath
        evidence_lines.append(f"### {filepath}")
        evidence_lines.append("```")
        content = EvidenceContractV2.read_file_content(full_path)
        evidence_lines.append(content)
        evidence_lines.append("```")
        evidence_lines.append("")
    
    # Write evidence file with LF line endings and no trailing whitespace
    evidence_content = "\n".join(line.rstrip() for line in evidence_lines)
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(evidence_content, encoding="utf-8", newline="\n")
    
    # Sanity check: evidence file should not start with Python code
    content_start = evidence_file.read_text(encoding="utf-8")[:200]
    if content_start.strip().startswith("#!/usr/bin/env python") or "def main()" in content_start[:200]:
        print("ERROR: Evidence file appears to contain Python code instead of markdown")
        print("This indicates the runner content was written to the evidence file.")
        sys.exit(1)

    print(f"Evidence generated successfully: {evidence_file}")
    print(f"CODE_COMMIT: {code_commit}")
    print(f"EVIDENCE_COMMIT: {sections['EVIDENCE_COMMIT']}")
    print(f"Current HEAD: {contract.get_current_head()}")
    
    if not evidence_commit:
        print("\nTo complete the evidence contract:")
        print("1. Commit this evidence file")
        print("2. Re-run with --evidence-commit <new_commit_hash>")
        print("3. The runner will update the sealed evidence file")


if __name__ == "__main__":
    main()
