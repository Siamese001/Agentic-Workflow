#!/usr/bin/env python3

import yaml

def analyze_domain_tokens():
    """Analyze which keys still contain domain tokens"""
    
    print("=== ANALYZING DOMAIN TOKENS IN DESCENDANTS ===")
    
    with open('unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    domains = ['agentic_core', 'schemas', 'runtime', 'prompt_governance', 
              'config', 'data', 'observability', 'scripts', 'apps', 'tests']
    
    domain_token_keys = defaultdict(list)
    
    def traverse(obj, path="", depth=0):
        if isinstance(obj, dict):
            for key, value in obj.items():
                full_path = f"{path}/{key}" if path else key
                
                # Check if key contains domain token (but not at root level)
                if depth > 0:  # Not at root level
                    for domain in domains:
                        if domain in key.lower() and not key.startswith(domain):
                            domain_token_keys[domain].append(full_path)
                
                new_path = f"{path}/{key}" if path else key
                traverse(value, new_path, depth + 1)
    
    traverse(data)
    
    print("Keys containing domain tokens:")
    for domain, keys in domain_token_keys.items():
        if keys:
            print(f"\n{domain} ({len(keys)} occurrences):")
            for key in keys[:10]:  # Show first 10
                print(f"  {key}")
            if len(keys) > 10:
                print(f"  ... and {len(keys) - 10} more")
    
    return domain_token_keys

if __name__ == '__main__':
    from collections import defaultdict
    analyze_domain_tokens()
