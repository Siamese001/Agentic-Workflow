#!/usr/bin/env python3
"""
Phase 2.2: Rename duplicate agents with Rg/Lic prefixes.
Performs file renames, class name updates, and import statement fixes.
"""
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Define rename mappings: (old_path, new_path, old_class, new_class)
RENAME_MAP = [
    # apps_rg agents
    ("apps_rg/engines/resume_engine/ResumeOrchestratorAgent.py", 
     "apps_rg/engines/resume_engine/RgResumeOrchestratorAgent.py",
     "ResumeOrchestratorAgent", "RgResumeOrchestratorAgent"),
    
    ("apps_rg/engines/resume_engine/HealingOrchestratorAgent.py",
     "apps_rg/engines/resume_engine/RgHealingOrchestratorAgent.py",
     "HealingOrchestratorAgent", "RgHealingOrchestratorAgent"),
    
    ("apps_rg/engines/resume_engine/ReflectionAgent.py",
     "apps_rg/engines/resume_engine/RgReflectionAgent.py",
     "ReflectionAgent", "RgReflectionAgent"),
    
    ("apps_rg/engines/resume_engine/StrategicPlannerAgent.py",
     "apps_rg/engines/resume_engine/RgStrategicPlannerAgent.py",
     "StrategicPlannerAgent", "RgStrategicPlannerAgent"),
    
    ("apps_rg/engines/resume_engine/TemplateOptimizerAgent.py",
     "apps_rg/engines/resume_engine/RgTemplateOptimizerAgent.py",
     "TemplateOptimizerAgent", "RgTemplateOptimizerAgent"),
    
    # apps_lic agents
    ("apps_lic/engines/outreach_engine/InternalAgent.py",
     "apps_lic/engines/outreach_engine/LicInternalAgent.py",
     "InternalAgent", "LicInternalAgent"),
    
    ("apps_lic/engines/outreach_engine/OrganizationAgent.py",
     "apps_lic/engines/outreach_engine/LicOrganizationAgent.py",
     "OrganizationAgent", "LicOrganizationAgent"),
    
    ("apps_lic/engines/outreach_engine/RecipientAgent.py",
     "apps_lic/engines/outreach_engine/LicRecipientAgent.py",
     "RecipientAgent", "LicRecipientAgent"),
    
    ("apps_lic/engines/outreach_engine/OutreachReflectionAgent.py",
     "apps_lic/engines/outreach_engine/LicReflectionAgent.py",
     "OutreachReflectionAgent", "LicReflectionAgent"),
    
    ("apps_lic/engines/outreach_engine/S2_SupervisorAgent.py",
     "apps_lic/engines/outreach_engine/LicS2SupervisorAgent.py",
     "S2_SupervisorAgent", "LicS2SupervisorAgent"),
    
    ("apps_lic/engines/outreach_engine/TemplateOptimizerAgent.py",
     "apps_lic/engines/outreach_engine/LicTemplateOptimizerAgent.py",
     "TemplateOptimizerAgent", "LicTemplateOptimizerAgent"),
    
    ("apps_lic/engines/outreach_engine/WorkflowOrchestratorAgent.py",
     "apps_lic/engines/outreach_engine/LicWorkflowOrchestratorAgent.py",
     "WorkflowOrchestratorAgent", "LicWorkflowOrchestratorAgent"),
    
    ("apps_lic/engines/outreach_engine/OutreachHealingOrchestratorAgent.py",
     "apps_lic/engines/outreach_engine/LicHealingOrchestratorAgent.py",
     "OutreachHealingOrchestratorAgent", "LicHealingOrchestratorAgent"),
]

def rename_files_and_update_classes(root: Path, dry_run: bool = True) -> Dict:
    """Rename files and update class definitions."""
    results = {"renamed": [], "failed": [], "updated_classes": []}
    
    for old_rel, new_rel, old_class, new_class in RENAME_MAP:
        old_path = root / old_rel
        new_path = root / new_rel
        
        if not old_path.exists():
            results["failed"].append(f"Source not found: {old_path}")
            continue
        
        if new_path.exists():
            results["failed"].append(f"Destination exists: {new_path}")
            continue
        
        # Read file content
        try:
            content = old_path.read_text(encoding='utf-8')
        except Exception as e:
            results["failed"].append(f"Read error {old_path}: {e}")
            continue
        
        # Update class name
        class_pattern = rf'\bclass\s+{re.escape(old_class)}\b'
        updated_content = re.sub(class_pattern, f'class {new_class}', content)
        
        if content != updated_content:
            results["updated_classes"].append(f"{old_class} → {new_class}")
        
        if not dry_run:
            # Write to new file
            new_path.parent.mkdir(parents=True, exist_ok=True)
            new_path.write_text(updated_content, encoding='utf-8')
            # Delete old file
            old_path.unlink()
        
        results["renamed"].append(f"{old_rel} → {new_rel}")
    
    return results

def update_imports_globally(root: Path, dry_run: bool = True) -> Dict:
    """Update all import statements across the codebase."""
    results = {"files_scanned": 0, "files_updated": 0, "replacements": []}
    
    # Build import replacement patterns
    import_replacements = []
    for _, _, old_class, new_class in RENAME_MAP:
        # Pattern 1: from ... import OldClass
        import_replacements.append((
            rf'\bfrom\s+([^\s]+)\s+import\s+([^,\n]*\b){re.escape(old_class)}\b',
            lambda m: f'from {m.group(1)} import {m.group(2)}{new_class}'
        ))
        # Pattern 2: OldClass in code (instantiation, type hints, etc.)
        # Only replace if followed by ( or : or whitespace (not part of another word)
        import_replacements.append((
            rf'\b{re.escape(old_class)}\b(?=[\s\(\:\[])',
            new_class
        ))
    
    # Scan Python files
    for py_file in root.rglob("*.py"):
        if any(skip in py_file.parts for skip in ["__pycache__", ".git", "archives", "venv"]):
            continue
        
        results["files_scanned"] += 1
        
        try:
            content = py_file.read_text(encoding='utf-8')
            updated_content = content
            
            # Apply replacements
            for pattern, replacement in import_replacements:
                updated_content = re.sub(pattern, replacement, updated_content)
            
            if content != updated_content:
                results["files_updated"] += 1
                results["replacements"].append(str(py_file.relative_to(root)))
                
                if not dry_run:
                    py_file.write_text(updated_content, encoding='utf-8')
        
        except Exception as e:
            print(f"Warning: Failed to process {py_file}: {e}")
    
    return results

def main():
    root = Path(__file__).parent
    
    print("=" * 70)
    print("PHASE 2.2: DUPLICATE AGENT RESOLUTION")
    print("=" * 70)
    print()
    
    # Step 1: Rename files and update class names
    print("Step 1: Renaming files and updating class names...")
    print("-" * 70)
    rename_results = rename_files_and_update_classes(root, dry_run=False)
    
    print(f"✅ Renamed: {len(rename_results['renamed'])} files")
    for item in rename_results['renamed']:
        print(f"   {item}")
    
    if rename_results['failed']:
        print(f"\n⚠️  Failed: {len(rename_results['failed'])} operations")
        for item in rename_results['failed']:
            print(f"   {item}")
    
    print(f"\n✅ Updated classes: {len(rename_results['updated_classes'])}")
    for item in rename_results['updated_classes']:
        print(f"   {item}")
    
    # Step 2: Update imports globally
    print("\n" + "=" * 70)
    print("Step 2: Updating import statements across codebase...")
    print("-" * 70)
    import_results = update_imports_globally(root, dry_run=False)
    
    print(f"✅ Scanned: {import_results['files_scanned']} Python files")
    print(f"✅ Updated: {import_results['files_updated']} files with import changes")
    
    if import_results['replacements']:
        print(f"\nFiles with updated imports (showing first 20):")
        for item in import_results['replacements'][:20]:
            print(f"   {item}")
        if len(import_results['replacements']) > 20:
            print(f"   ... and {len(import_results['replacements']) - 20} more")
    
    print("\n" + "=" * 70)
    print("✅ PHASE 2.2 COMPLETE")
    print("=" * 70)
    print("\nNext: Run discovery validation to verify duplicates resolved")

if __name__ == "__main__":
    main()
