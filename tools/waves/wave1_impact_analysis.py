#!/usr/bin/env python3
"""Wave 1 Impact Analysis - Path normalization bug blast radius"""

import json


def analyze_impact():
    # Load audit results
    with open("artifacts/path_replace_audit.json", "r") as f:
        audit = json.load(f)

    suspicious = audit.get("suspicious", [])

    # Categorize by file
    by_file = {}
    for item in suspicious:
        file = item["file"]
        if file not in by_file:
            by_file[file] = []
        by_file[file].append(item)

    # Analyze impact
    impact_analysis = {
        "total_suspicious_patterns": len(suspicious),
        "affected_files": list(by_file.keys()),
        "file_count": len(by_file),
        "critical_files": [],
        "high_risk_files": [],
        "medium_risk_files": [],
        "findings": [],
    }

    # Risk categorization
    for file, items in by_file.items():
        count = len(items)
        if count >= 5:
            impact_analysis["critical_files"].append(file)
            risk = "CRITICAL"
        elif count >= 3:
            impact_analysis["high_risk_files"].append(file)
            risk = "HIGH"
        else:
            impact_analysis["medium_risk_files"].append(file)
            risk = "MEDIUM"

        impact_analysis["findings"].append(
            {
                "file": file,
                "pattern_count": count,
                "risk": risk,
                "lines": [i["line"] for i in items],
            },
        )

    # Check for the specific bug pattern
    bug_pattern_found = False
    bug_location = None

    for item in suspicious:
        content = item.get("content", "")
        # Check for backslash-to-dot replacement
        if "chr(92)" in content and "'.'" in content:
            bug_pattern_found = True
            bug_location = f"{item['file']}:{item['line']}"
            break
        if "'\\\\'" in content and "'.'" in content:
            bug_pattern_found = True
            bug_location = f"{item['file']}:{item['line']}"
            break

    impact_analysis["bug_pattern_found"] = bug_pattern_found
    impact_analysis["bug_location"] = bug_location

    # Blast radius
    impact_analysis["blast_radius"] = {
        "direct_files": len(by_file),
        "total_patterns": len(suspicious),
        "critical": len(impact_analysis["critical_files"]),
        "high_risk": len(impact_analysis["high_risk_files"]),
        "medium_risk": len(impact_analysis["medium_risk_files"]),
    }

    # Save impact analysis
    with open("artifacts/wave1_impact_analysis.json", "w") as f:
        json.dump(impact_analysis, f, indent=2)

    # Print summary
    print("Wave 1 Impact Analysis Complete")
    print("=" * 50)
    print(f"Total suspicious patterns: {impact_analysis['total_suspicious_patterns']}")
    print(f"Affected files: {impact_analysis['file_count']}")
    print(f"Critical files: {impact_analysis['blast_radius']['critical']}")
    print(f"High risk files: {impact_analysis['blast_radius']['high_risk']}")
    print(f"Medium risk files: {impact_analysis['blast_radius']['medium_risk']}")
    print()

    if bug_location:
        print(f"BUG LOCATION: {bug_location}")

    print("\nTop 5 Most Affected Files:")
    sorted_findings = sorted(impact_analysis["findings"], key=lambda x: x["pattern_count"], reverse=True)
    for finding in sorted_findings[:5]:
        print(f"  {finding['file']}: {finding['pattern_count']} patterns ({finding['risk']})")


if __name__ == "__main__":
    analyze_impact()
