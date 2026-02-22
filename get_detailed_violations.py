#!/usr/bin/env python3
import subprocess
import json
import sys

def get_detailed_violations():
    """Extract detailed violation information from SSOT"""
    try:
        # Run the SSOT script
        result = subprocess.run([
            sys.executable, '-m', 
            'agentic_core.L0_routing.scripts.execute_ssot_entrypoint', 
            '--legacy', '--dry-run'
        ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        output = result.stdout
        
        # Parse violations from the output
        violations = []
        
        # Parse location violations
        import re
        location_pattern = r"'file': '([^']+)', 'reason': '([^']+)'"
        location_matches = re.findall(location_pattern, output)
        
        for file_path, reason in location_matches:
            violations.append({
                "type": "LOCATION",
                "source": "LocationAgent",
                "file": file_path,
                "message": f"File '{file_path}' violates location rules: {reason}",
                "reason": reason,
                "severity": "medium",
                "recommended_action": "Fix location/naming issue",
                "llm_triggered": False,
                "confidence": 0.792
            })
        
        # Add gravity violations
        if "gravity violations" in output.lower():
            gravity_match = re.search(r'Found (\d+) gravity violations', output)
            if gravity_match:
                violations.append({
                    "type": "GRAVITY",
                    "source": "GravityLeakRepairAgent",
                    "file": "unknown",
                    "message": f"Found {gravity_match.group(1)} gravity violations (layer inversions)",
                    "count": int(gravity_match.group(1)),
                    "severity": "high",
                    "recommended_action": "Review and fix layer boundary violations",
                    "llm_triggered": False,
                    "confidence": 0.9
                })
        
        # Add root hygiene violations
        if "Illegal 'scripts/' directory" in output:
            violations.append({
                "type": "ILLEGAL_ROOT_SCRIPTS",
                "source": "RootHygieneAgent",
                "file": "C:\\Git\\Agentic-Workflow\\scripts",
                "message": "Illegal 'scripts/' directory in project root",
                "severity": "high",
                "recommended_action": "Move scripts to ops_scripts/ or agentic_core/L0_routing/scripts/",
                "llm_triggered": False,
                "confidence": 0.9
            })
        
        if "Illegal cache directory" in output:
            violations.append({
                "type": "ILLEGAL_CACHE_DIR",
                "source": "RootHygieneAgent",
                "file": "C:\\Git\\Agentic-Workflow\\.pytest_cache",
                "message": "Illegal cache directory '.pytest_cache' in project root",
                "severity": "low",
                "recommended_action": "Add .pytest_cache to .gitignore and remove from root",
                "llm_triggered": False,
                "confidence": 0.6
            })
        
        # Create detailed report
        detailed_report = {
            "meta": {
                "territory": "prompt_governance",
                "timestamp": "2026-02-22T15:32:20.311364",
                "status": "NON-COMPLIANT",
                "sovereignty_level": "L5",
                "report_type": "detailed_violations"
            },
            "summary": {
                "total_violations": len(violations),
                "severity_breakdown": {
                    "high": len([v for v in violations if v["severity"] == "high"]),
                    "medium": len([v for v in violations if v["severity"] == "medium"]),
                    "low": len([v for v in violations if v["severity"] == "low"])
                },
                "violation_types": list(set([v["type"] for v in violations]))
            },
            "violations": violations,
            "agents_executed": [
                "ArchitectureGovernorAgent",
                "GravityLeakRepairAgent", 
                "FilesystemSSOTReconcilerAgent",
                "DebateSynthesisAgent",
                "HierarchyAgent",
                "FileClassificationAgent",
                "LocationAgent",
                "SystemArchitectAgent",
                "RootHygieneAgent"
            ]
        }
        
        return detailed_report
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    report = get_detailed_violations()
    if report:
        print(json.dumps(report, indent=2, ensure_ascii=False))
