#!/usr/bin/env python3

def examine_domain_tokens_detailed():
    """Examine exact domain token occurrences that validation is flagging"""
    
    print("=== DETAILED DOMAIN TOKEN ANALYSIS ===")
    
    # Read the file as text
    with open('unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    domains = ['agentic_core', 'schemas', 'runtime', 'prompt_governance', 
              'config', 'data', 'observability', 'scripts', 'apps', 'tests']
    
    lines = content.split('\n')
    domain_token_details = {}
    
    for line_num, line in enumerate(lines, 1):
        for domain in domains:
            if domain in line:
                # Check if it's not a domain root declaration
                if not line.strip().startswith(f"{domain}:") and not line.strip().startswith(f"  {domain}:"):
                    if domain not in domain_token_details:
                        domain_token_details[domain] = []
                    domain_token_details[domain].append((line_num, line.strip()))
    
    for domain, occurrences in domain_token_details.items():
        if occurrences:
            print(f"\n{domain} ({len(occurrences)} occurrences):")
            for line_num, line in occurrences:
                print(f"  Line {line_num:4d}: {line}")
    
    # Analyze patterns
    print(f"\n=== PATTERN ANALYSIS ===")
    for domain, occurrences in domain_token_details.items():
        if occurrences:
            print(f"\n{domain} patterns:")
            prefixes = []
            suffixes = []
            standalone = []
            
            for line_num, line in occurrences:
                # Extract the key/filename from the line
                if ':' in line:
                    key_part = line.split(':')[0].strip()
                    
                    if key_part.startswith(f"{domain}_"):
                        prefixes.append(key_part)
                    elif key_part.endswith(f"_{domain}"):
                        suffixes.append(key_part)
                    elif domain in key_part and not key_part.startswith(domain) and not key_part.endswith(domain):
                        standalone.append(key_part)
            
            print(f"  Prefixes ({len(prefixes)}): {prefixes[:3]}{'...' if len(prefixes) > 3 else ''}")
            print(f"  Suffixes ({len(suffixes)}): {suffixes[:3]}{'...' if len(suffixes) > 3 else ''}")
            print(f"  Standalone ({len(standalone)}): {standalone[:3]}{'...' if len(standalone) > 3 else ''}")

if __name__ == '__main__':
    examine_domain_tokens_detailed()
