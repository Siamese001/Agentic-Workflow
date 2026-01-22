#!/usr/bin/env python3
"""
Scan for utilities/handlers incorrectly named with "Agent" suffix.

Identifies files where:
1. Filename ends with "Agent.py"
2. But the class inside doesn't match the filename or isn't a true agent
"""

import ast
from pathlib import Path
from typing import Dict, List, Tuple


def scan_file(file_path: Path) -> Tuple[str, List[str], bool]:
    """
    Scan a file to check if it's a misnamed agent.
    
    Returns:
        (filename, list_of_class_names, has_sovereign_base_inheritance)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        classes = []
        has_sovereign = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
                
                # Check if inherits from SovereignBaseAgent or layer bases
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        if base.id in ['SovereignBaseAgent', 'InfrastructureMixin', 
                                      'L3OrchestrationBaseAgent', 'L4StateBaseAgent',
                                      'L5SafetyBaseAgent', 'L6ObservabilityBaseAgent']:
                            has_sovereign = True
                    elif isinstance(base, ast.Attribute):
                        if base.attr in ['SovereignBaseAgent', 'InfrastructureMixin',
                                        'L3OrchestrationBaseAgent', 'L4StateBaseAgent',
                                        'L5SafetyBaseAgent', 'L6ObservabilityBaseAgent']:
                            has_sovereign = True
        
        return (file_path.stem, classes, has_sovereign)
        
    except Exception as e:
        return (file_path.stem, [], False)


def categorize_misnamed(file_path: Path, filename: str, classes: List[str], has_sovereign: bool) -> Dict:
    """Categorize the type of mismatch."""
    result = {
        'file': str(file_path),
        'filename': filename,
        'classes': classes,
        'has_sovereign': has_sovereign,
        'issue': None,
        'recommendation': None,
        'severity': None,
    }
    
    # Case 1: No classes found
    if not classes:
        result['issue'] = "File ends with 'Agent.py' but contains no classes"
        result['recommendation'] = f"Rename to {filename.replace('Agent', '')}.py or add proper Agent class"
        result['severity'] = 'HIGH'
        return result
    
    # Case 2: Class name doesn't match filename
    expected_class = filename
    if expected_class not in classes:
        # Check if it's a utility/handler class
        main_class = classes[0] if classes else None
        if main_class:
            if any(suffix in main_class for suffix in ['Handler', 'Manager', 'Helper', 'Util', 'Service']):
                result['issue'] = f"Utility class '{main_class}' incorrectly named with 'Agent' suffix in filename"
                result['recommendation'] = f"Rename file to {main_class}.py"
                result['severity'] = 'HIGH'
            elif not main_class.endswith('Agent'):
                result['issue'] = f"Class '{main_class}' doesn't end with 'Agent' but file does"
                result['recommendation'] = f"Either rename file to {main_class}.py or rename class to {expected_class}"
                result['severity'] = 'MEDIUM'
            else:
                result['issue'] = f"Class name '{main_class}' doesn't match filename '{filename}'"
                result['recommendation'] = f"Rename file to {main_class}.py or update class name"
                result['severity'] = 'LOW'
        return result
    
    # Case 3: Class name matches but no Sovereign inheritance
    if expected_class in classes and not has_sovereign:
        result['issue'] = f"Agent class '{expected_class}' doesn't inherit from SovereignBaseAgent"
        result['recommendation'] = f"Add SovereignBaseAgent inheritance to {expected_class}"
        result['severity'] = 'MEDIUM'
        return result
    
    # Case 4: All good
    result['issue'] = None
    result['recommendation'] = None
    result['severity'] = None
    return result


def main():
    print("\n" + "="*80)
    print("MISNAMED AGENT SCAN - Findings & Recommendations")
    print("="*80 + "\n")
    
    root_dir = Path("agentic_core")
    agent_files = list(root_dir.glob("**/*Agent.py"))
    
    print(f"Found {len(agent_files)} files ending with 'Agent.py'\n")
    
    findings = {
        'HIGH': [],
        'MEDIUM': [],
        'LOW': [],
        'CLEAN': [],
    }
    
    for file_path in sorted(agent_files):
        filename, classes, has_sovereign = scan_file(file_path)
        result = categorize_misnamed(file_path, filename, classes, has_sovereign)
        
        if result['severity']:
            findings[result['severity']].append(result)
        else:
            findings['CLEAN'].append(result)
    
    # Print findings by severity
    for severity in ['HIGH', 'MEDIUM', 'LOW']:
        if findings[severity]:
            print(f"\n{'='*80}")
            print(f"🚨 {severity} PRIORITY - {len(findings[severity])} issues")
            print(f"{'='*80}\n")
            
            for item in findings[severity]:
                print(f"📄 {item['file']}")
                print(f"   Issue: {item['issue']}")
                print(f"   Classes: {', '.join(item['classes']) if item['classes'] else 'None'}")
                print(f"   Has Sovereign DNA: {item['has_sovereign']}")
                print(f"   ✅ Recommendation: {item['recommendation']}")
                print()
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"  Total Agent files scanned: {len(agent_files)}")
    print(f"  HIGH priority issues: {len(findings['HIGH'])}")
    print(f"  MEDIUM priority issues: {len(findings['MEDIUM'])}")
    print(f"  LOW priority issues: {len(findings['LOW'])}")
    print(f"  Clean files: {len(findings['CLEAN'])}")
    print(f"  Total issues: {len(findings['HIGH']) + len(findings['MEDIUM']) + len(findings['LOW'])}")
    print("="*80 + "\n")
    
    # Generate rename script
    if findings['HIGH']:
        print("\n" + "="*80)
        print("SUGGESTED RENAME COMMANDS (HIGH PRIORITY)")
        print("="*80 + "\n")
        
        for item in findings['HIGH']:
            if 'Rename file to' in item['recommendation']:
                old_path = item['file']
                # Extract new filename from recommendation
                if item['classes']:
                    new_filename = item['classes'][0] + '.py'
                    new_path = old_path.replace(item['filename'] + '.py', new_filename)
                    print(f"git mv {old_path} {new_path}")
        
        print()


if __name__ == "__main__":
    main()
