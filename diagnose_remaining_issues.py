#!/usr/bin/env python3

import yaml

def diagnose_general_nodes():
    """Identify remaining general nodes"""
    print("=== DIAGNOSING REMAINING GENERAL NODES ===")
    
    with open('unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    general_nodes = []
    
    def traverse(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == 'general':
                    general_nodes.append(path)
                new_path = f"{path}/{key}" if path else key
                traverse(value, new_path)
    
    traverse(data)
    
    print(f"Found {len(general_nodes)} general nodes:")
    for i, path in enumerate(general_nodes, 1):
        print(f"  {i}. {path}")
    
    return general_nodes

def diagnose_domain_tokens():
    """Identify remaining domain token occurrences"""
    print("\n=== DIAGNOSING REMAINING DOMAIN TOKENS ===")
    
    with open('unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    domains = ['agentic_core', 'schemas', 'runtime', 'prompt_governance', 
              'config', 'data', 'observability', 'scripts', 'apps', 'tests']
    
    domain_token_details = {}
    
    lines = content.split('\n')
    for line_num, line in enumerate(lines, 1):
        for domain in domains:
            if domain in line and not line.strip().startswith(f"{domain}:"):
                # Check if it's not just the domain root
                if not line.strip().startswith(f"{domain}:") and not line.strip().startswith(f"  {domain}:"):
                    if domain not in domain_token_details:
                        domain_token_details[domain] = []
                    domain_token_details[domain].append((line_num, line.strip()))
    
    for domain, occurrences in domain_token_details.items():
        if occurrences:
            print(f"\n{domain} ({len(occurrences)} occurrences):")
            for line_num, line in occurrences[:5]:  # Show first 5
                print(f"  Line {line_num}: {line}")
            if len(occurrences) > 5:
                print(f"  ... and {len(occurrences) - 5} more")
    
    return domain_token_details

def diagnose_single_child_dirs():
    """Analyze single child directory structure"""
    print("\n=== DIAGNOSING SINGLE CHILD DIRECTORIES ===")
    
    with open('unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    single_child_count = 0
    single_child_examples = []
    
    def traverse(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict) and len(value) == 1:
                    single_child_count += 1
                    if len(single_child_examples) < 10:
                        child_key = list(value.keys())[0]
                        single_child_examples.append(f"{path}/{key} → {child_key}")
                
                new_path = f"{path}/{key}" if path else key
                traverse(value, new_path)
    
    traverse(data)
    
    print(f"Total single child directories: {single_child_count}")
    print("Examples:")
    for example in single_child_examples:
        print(f"  {example}")
    
    return single_child_count

if __name__ == '__main__':
    general_nodes = diagnose_general_nodes()
    domain_tokens = diagnose_domain_tokens()
    single_child_count = diagnose_single_child_dirs()
    
    print(f"\n=== SUMMARY ===")
    print(f"General nodes to fix: {len(general_nodes)}")
    print(f"Domain token occurrences to fix: {sum(len(occ) for occ in domain_tokens.values())}")
    print(f"Single child directories: {single_child_count}")
