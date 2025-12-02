#!/usr/bin/env python3

import yaml
import re

def normalize_key_name(key, current_domain):
    """Remove domain tokens from a key name"""
    if not isinstance(key, str):
        return key
    
    # Don't modify domain root keys
    if key in ['agentic_core', 'schemas', 'runtime', 'prompt_governance', 
              'config', 'data', 'observability', 'scripts', 'apps', 'tests']:
        return key
    
    # Remove domain tokens from key names
    domains = ['agentic_core', 'schemas', 'runtime', 'prompt_governance', 
              'config', 'data', 'observability', 'scripts', 'apps', 'tests']
    
    normalized = key
    for domain in domains:
        # Remove domain tokens from anywhere in the key
        normalized = normalized.replace(f'_{domain}_', '_')
        normalized = normalized.replace(f'{domain}_', '')
        normalized = normalized.replace(f'_{domain}', '')
        
        # Handle specific patterns
        if normalized.startswith(f'{domain}_'):
            normalized = normalized[len(domain)+1:]
        if normalized.endswith(f'_{domain}'):
            normalized = normalized[:-len(domain)-1]
    
    return normalized

def fix_domain_tokens_recursive(obj, current_domain="", path=""):
    """Recursively fix domain tokens in YAML structure"""
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            # Determine current domain from path
            if key in ['agentic_core', 'schemas', 'runtime', 'prompt_governance', 
                      'config', 'data', 'observability', 'scripts', 'apps', 'tests']:
                current_domain = key
                new_path = key
            else:
                # Normalize the key
                normalized_key = normalize_key_name(key, current_domain)
                new_path = f"{path}/{normalized_key}" if path else normalized_key
                result[normalized_key] = fix_domain_tokens_recursive(value, current_domain, new_path)
        
        return result
    elif isinstance(obj, list):
        return [fix_domain_tokens_recursive(item, current_domain, path) for item in obj]
    else:
        return obj

def fix_domain_tokens():
    """Fix domain tokens throughout the YAML structure"""
    
    print("=== SYSTEMATIC DOMAIN TOKEN FIX ===")
    
    # Load YAML
    with open('unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    print("Loaded YAML structure")
    
    # Apply recursive fix
    fixed_data = fix_domain_tokens_recursive(data)
    
    print("Applied domain token fixes")
    
    # Write back
    with open('unified_structure_subatomic.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(fixed_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("✅ Domain token deduplication completed")
    
    # Verify the fix
    with open('unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    domains = ['agentic_core', 'schemas', 'runtime', 'prompt_governance', 
              'config', 'data', 'observability', 'scripts', 'apps', 'tests']
    
    print("\nDomain tokens after fix:")
    total_remaining = 0
    for domain in domains:
        # Count occurrences not at domain root level
        lines = content.split('\n')
        count = 0
        for line in lines:
            if domain in line and not line.strip().startswith(f"{domain}:"):
                count += 1
        if count > 0:
            print(f"  {domain}: {count}")
            total_remaining += count
    
    if total_remaining == 0:
        print("✅ All domain tokens removed from descendants!")
    else:
        print(f"⚠️  {total_remaining} domain tokens still remain")

if __name__ == '__main__':
    fix_domain_tokens()
