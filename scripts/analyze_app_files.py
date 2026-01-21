#!/usr/bin/env python3
"""Analyze agentic_core for app-specific files that should be in apps_rg or apps_lic."""

from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
AGENTIC_CORE = ROOT / "agentic_core"

# Keywords for classification
RESUME_KEYWORDS = [
    "resume",
    "cv ",
    "ats",
    "job description",
    "bullet point",
    "work experience",
    "resume generator",
]
OUTREACH_KEYWORDS = [
    "outreach",
    "linkedin",
    "recipient",
    "campaign",
    "personalization",
    "sender",
    "inmail",
    "message generation",
]


def classify_file(filepath: Path) -> tuple:
    """Classify a file as resume-related, outreach-related, or generic."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace").lower()

        # Strong signals
        has_resume = any(kw in content for kw in RESUME_KEYWORDS)
        has_outreach = any(kw in content for kw in OUTREACH_KEYWORDS)

        # Check for explicit app references
        has_rg_ref = "apps_rg" in content or "resume_engine" in content
        has_lic_ref = "apps_lic" in content or "outreach_engine" in content

        # Score based on keyword frequency
        resume_score = sum(content.count(kw) for kw in RESUME_KEYWORDS)
        outreach_score = sum(content.count(kw) for kw in OUTREACH_KEYWORDS)

        if has_rg_ref:
            return "resume", resume_score, outreach_score
        elif has_lic_ref:
            return "outreach", resume_score, outreach_score
        elif has_resume and not has_outreach:
            return "resume", resume_score, outreach_score
        elif has_outreach and not has_resume:
            return "outreach", resume_score, outreach_score
        elif resume_score > outreach_score and resume_score > 5:
            return "resume", resume_score, outreach_score
        elif outreach_score > resume_score and outreach_score > 5:
            return "outreach", resume_score, outreach_score
        else:
            return "generic", resume_score, outreach_score
    except Exception:
        return "error", 0, 0


def main():
    app_files = {"resume": [], "outreach": [], "generic": [], "error": []}

    for f in sorted(AGENTIC_CORE.rglob("*.py")):
        if "__pycache__" in str(f) or f.name == "__init__.py":
            continue

        classification, rs, os = classify_file(f)
        rel_path = str(f.relative_to(ROOT))
        app_files[classification].append((rel_path, rs, os))

    print("=" * 70)
    print("APP-SPECIFIC FILES IN agentic_core")
    print("=" * 70)

    # Resume files
    print(f"\n## RESUME GENERATOR (apps_rg) - {len(app_files['resume'])} files")
    print("-" * 50)
    by_folder = defaultdict(list)
    for path, rs, os in app_files["resume"]:
        parts = path.replace("/", "\\").split("\\")
        if len(parts) > 2:
            folder = "/".join(parts[:3])
        else:
            folder = parts[0]
        by_folder[folder].append((path, rs, os))

    for folder, files in sorted(by_folder.items(), key=lambda x: -len(x[1])):
        print(f"\n  {folder}/ ({len(files)} files)")
        for path, rs, os in files[:8]:
            fname = path.split("\\")[-1]
            print(f"    {fname}")
        if len(files) > 8:
            print(f"    ... and {len(files) - 8} more")

    # Outreach files
    print(f"\n## LINKEDIN OUTREACH (apps_lic) - {len(app_files['outreach'])} files")
    print("-" * 50)
    by_folder = defaultdict(list)
    for path, rs, os in app_files["outreach"]:
        parts = path.replace("/", "\\").split("\\")
        if len(parts) > 2:
            folder = "/".join(parts[:3])
        else:
            folder = parts[0]
        by_folder[folder].append((path, rs, os))

    for folder, files in sorted(by_folder.items(), key=lambda x: -len(x[1])):
        print(f"\n  {folder}/ ({len(files)} files)")
        for path, rs, os in files[:8]:
            fname = path.split("\\")[-1]
            print(f"    {fname}")
        if len(files) > 8:
            print(f"    ... and {len(files) - 8} more")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Resume-related (-> apps_rg):    {len(app_files['resume'])} files")
    print(f"Outreach-related (-> apps_lic): {len(app_files['outreach'])} files")
    print(f"Generic (keep in agentic_core): {len(app_files['generic'])} files")

    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    # Find high-value moves
    l1_resume = [p for p, _, _ in app_files["resume"] if "L1_cognition" in p]
    l1_outreach = [p for p, _, _ in app_files["outreach"] if "L1_cognition" in p]

    print(
        f"\n1. L1_cognition/thought_engine has {len(l1_resume)} resume + {len(l1_outreach)} outreach files"
    )
    print("   -> Create apps_rg/engines/thought_engine/ and apps_lic/engines/thought_engine/")

    l5_resume = [p for p, _, _ in app_files["resume"] if "L5_safety" in p]
    l5_outreach = [p for p, _, _ in app_files["outreach"] if "L5_safety" in p]

    print(f"\n2. L5_safety has {len(l5_resume)} resume + {len(l5_outreach)} outreach files")
    print("   -> Move Dispatch*Agent files to respective app folders")


if __name__ == "__main__":
    main()
