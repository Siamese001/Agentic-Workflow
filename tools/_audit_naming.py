"""
Audit naming convention compliance for all agents/scripts active in execute_ssot.
Framework: docs/technical/File Naming - Script vs. Agent.md

Rules:
  Agent file  : snake_case name ending in _agent.py  (e.g. root_hygiene_healer_agent.py)
                OR PascalCase ending in Agent.py      (e.g. LocationHealerAgent.py)
  Class name  : PascalCase ending in Agent            (e.g. RootHygieneAgent → FAIL, needs 'Agent' suffix)
  Validator   : <domain>_validator.py / <Domain>ValidatorAgent
  Healer      : <domain>_healer_agent.py / <Domain>HealerAgent
  Script      : no '_agent' suffix, no Agent class wrapper
"""

from pathlib import Path

REPO = Path(__file__).parent.parent

# All files directly imported/used in execute_ssot active pipeline
ACTIVE_FILES = [
    # Validators (scan only)
    (
        "agentic_core/L5_safety/reasoning/filesystem_ssot_validator.py",
        "FilesystemSSOTValidatorAgent",
        "validator",
    ),
    ("agentic_core/L5_safety/reasoning/gravity_validator.py", "GravityValidatorAgent", "validator"),
    ("agentic_core/L5_safety/reasoning/hierarchy_validator.py", "HierarchyValidatorAgent", "validator"),
    ("agentic_core/L5_safety/reasoning/location_validator.py", "LocationValidatorAgent", "validator"),
    (
        "agentic_core/L5_safety/reasoning/file_classification_validator.py",
        "FileClassificationValidatorAgent",
        "validator",
    ),
    ("agentic_core/L5_safety/reasoning/root_hygiene_validator.py", "RootHygieneValidatorAgent", "validator"),
    # Healers (fix)
    (
        "agentic_core/L5_safety/reasoning/filesystem_ssot_reconciler.py",
        "FilesystemSSOTReconcilerAgent",
        "healer",
    ),
    ("agentic_core/L5_safety/reasoning/GravityLeakHealerAgent.py", "GravityLeakHealerAgent", "healer"),
    ("agentic_core/L5_safety/reasoning/hierarchy_healer.py", "HierarchyAgent", "healer"),
    ("agentic_core/L5_safety/reasoning/LocationHealerAgent.py", "LocationHealerAgent", "healer"),
    ("agentic_core/L5_safety/reasoning/FileClassificationAgent.py", "FileClassificationAgent", "healer"),
    ("agentic_core/L5_safety/reasoning/root_hygiene_healer.py", "RootHygieneAgent", "healer"),
    # Orchestrator/governor
    (
        "agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py",
        "ArchitectureGovernorAgent",
        "governor",
    ),
    (
        "agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py",
        "CognitiveDispositionAgent",
        "governor",
    ),
    (
        "agentic_core/L6_observability/reasoning/observability_probe_executor.py",
        "ObservabilityProbeExecutorAgent",
        "executor",
    ),
]

print("=" * 90)
print("NAMING CONVENTION AUDIT — execute_ssot active pipeline")
print("=" * 90)
print(f"{'File (actual)':<52} {'Class (actual)':<36} {'Role':<10} {'Issues'}")
print("-" * 120)

issues_found = []

for rel_path, expected_class, role in ACTIVE_FILES:
    fpath = REPO / rel_path
    fname = fpath.name
    stem = fpath.stem

    file_issues = []

    # --- FILE NAME RULES ---
    # PascalCase files: must end with 'Agent'
    if fname[0].isupper():
        if not stem.endswith("Agent"):
            file_issues.append(f"FILE: PascalCase file '{fname}' should end with 'Agent'")
    else:
        # snake_case files: active-pipeline healer/validator should end with _agent or _validator
        if role == "healer" and not (stem.endswith("_agent") or stem.endswith("_healer_agent")):
            file_issues.append(f"FILE: healer file '{fname}' should be snake_case ending '_healer_agent.py'")
        if role == "validator" and not stem.endswith("_validator"):
            file_issues.append(f"FILE: validator file '{fname}' missing '_validator' suffix")

    # --- CLASS NAME RULES ---
    if not expected_class.endswith("Agent"):
        file_issues.append(f"CLASS: '{expected_class}' should end with 'Agent'")

    # Healer class naming: should end with 'HealerAgent'
    if role == "healer" and not (
        expected_class.endswith("HealerAgent")
        or expected_class.endswith("ReconcilerAgent")
        or expected_class.endswith("ExecutorAgent")
    ):
        file_issues.append(f"CLASS: healer class '{expected_class}' should end with 'HealerAgent'")

    # Validator class naming: should end with 'ValidatorAgent'
    if role == "validator" and not expected_class.endswith("ValidatorAgent"):
        file_issues.append(f"CLASS: validator class '{expected_class}' should end with 'ValidatorAgent'")

    status = "✓ OK" if not file_issues else "✗ VIOLATION"
    issue_str = " | ".join(file_issues) if file_issues else ""
    print(f"{fname:<52} {expected_class:<36} {role:<10} {status}  {issue_str}")
    if file_issues:
        issues_found.extend([(fname, expected_class, role, i) for i in file_issues])

print()
print("=" * 90)
print(f"SUMMARY: {len(issues_found)} naming violations found across {len(ACTIVE_FILES)} active files")
print("=" * 90)

FILE_VIOLATIONS = {}
for fname, cls, role, issue in issues_found:
    FILE_VIOLATIONS.setdefault(fname, []).append((cls, role, issue))

if FILE_VIOLATIONS:
    print("\nREQUIRED CHANGES:")
    for fname, items in FILE_VIOLATIONS.items():
        cls, role, _ = items[0]
        file_issues = [i for _, _, i in items]
        print(f"\n  {fname}  [{role}]")
        for i in file_issues:
            print(f"    → {i}")
        # Suggest canonical name
        stem = Path(fname).stem
        # Derive canonical names
        if role == "healer":
            domain = stem.replace("_healer", "").replace("_agent", "").replace("Agent", "")
            domain_snake = "".join(["_" + c.lower() if c.isupper() else c for c in domain]).lstrip("_")
            print(f"    → Canonical file: {domain_snake}_healer_agent.py")
            # Class: keep or rename
            domain_pascal = "".join(w.capitalize() for w in domain_snake.split("_"))
            print(f"    → Canonical class: {domain_pascal}HealerAgent")
