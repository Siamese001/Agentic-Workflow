#!/usr/bin/env python3

import yaml
import re

def fix_domain_tokens():
    """Remove domain tokens from all descendant keys and filenames"""
    
    print("=== FIXING DOMAIN TOKENS IN DESCENDANTS ===")
    
    # Read current YAML
    with open('unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count domain tokens before
    domains = ['agentic_core', 'schemas', 'runtime', 'prompt_governance', 
              'config', 'data', 'observability', 'scripts', 'apps', 'tests']
    
    print("Domain tokens before fix:")
    for domain in domains:
        count = content.count(domain)
        if count > 0:
            print(f"  {domain}: {count}")
    
    # Fix domain tokens in keys (not at domain root level)
    # Pattern to match domain tokens within key names
    for domain in domains:
        # Remove domain tokens from keys
        # Handle patterns like: get_data_info, manage_data_costs, etc.
        patterns = [
            f'get_{domain}_info',
            f'manage_{domain}_costs', 
            f'prepare_{domain}_snapshot',
            f'format_{domain}_context',
            f'build_{domain}_filters',
            f'validate_{domain}_schema',
            f'use_{domain}_tools',
            f'get_{domain}_info',
            f'update_{domain}_state',
            f'check_{domain}_structure',
            f'check_{domain}_rules',
            f'find_{domain}_problems',
            f'retrieve_{domain}_history',
            f'query_{domain}_store',
            f'fetch_{domain}_context',
            f'prepare_{domain}_payload',
            f'serialize_{domain}_state',
            f'format_{domain}_request',
            f'execute_{domain}_action',
            f'invoke_{domain}_service',
            f'process_{domain}_response',
            f'retrieve_{domain}_memory',
            f'search_{domain}_vectors',
            f'match_{domain}_patterns',
            f'find_{domain}_context',
            f'apply_{domain}_safety',
            f'enforce_{domain}_policy',
            f'validate_{domain}_ethics',
            f'apply_{domain}_safety_policy',
            f'enforce_{domain}_filters',
            f'filter_{domain}_content',
            f'validate_{domain}_standards',
            f'assess_{domain}_risk',
            f'compute_{domain}_score',
            f'evaluate_{domain}_compliance',
            f'track_{domain}_cost',
            f'update_{domain}_usage',
            f'enforce_{domain}_budget',
            f'orchestrate_{domain}_planning',
            f'coordinate_{domain}_queries',
            f'manage_{domain}_context',
            f'dispatch_{domain}_tools',
            f'invoke_{domain}_service',
            f'call_{domain}_api',
            f'inspect_{domain}_quality',
            f'diagnose_{domain}_issues',
            f'log_{domain}_metrics',
            f'convert_{domain}_content',
            f'pick_best_result',
            f'use_{domain}_tools',
            f'prepare_{domain}_information',
            f'prepare_{domain}_context',
            f'build_{domain}_query',
            f'build_{domain}_filters',
            f'extract_{domain}_requirements',
            f'parse_{domain}_settings',
            f'extract_{domain}_parameters',
            f'load_{domain}_planning',
            f'parse_{domain}_settings',
            f'extract_{domain}_parameters',
            f'retrieve_{domain}_context',
            f'query_{domain}_store',
            f'fetch_{domain}_history',
            f'inspect_{domain}_state',
            f'capture_{domain}_diagnostics',
            f'log_{domain}_inspection',
            f'aggregate_{domain}_state',
            f'merge_{domain}_contexts',
            f'consolidate_{domain}_updates',
            f'prepare_{domain}_snapshot',
            f'serialize_{domain}_state',
            f'format_{domain}_data',
            f'prepare_{domain}_payload',
            f'format_{domain}_request',
            f'serialize_{domain}_params',
            f'validate_{domain}_schema',
            f'check_{domain}_compliance',
            f'enforce_{domain}_contracts',
            f'apply_{domain}_safety',
            f'enforce_{domain}_policy',
            f'validate_{domain}_ethics',
            f'retry_{domain}_operations',
            f'handle_{domain}_failures',
            f'implement_{domain}_fallback',
            f'apply_{domain}_safety',
            f'enforce_{domain}_policy',
            f'validate_{domain}_ethics',
            f'prepare_{domain}_payload',
            f'format_{domain}_request',
            f'serialize_{domain}_data',
            f'validate_{domain}_content',
            f'check_{domain}_quality',
            f'enforce_{domain}_limits',
            f'assess_{domain}_relevance',
            f'evaluate_{domain}_quality',
            f'score_{domain}_effectiveness',
            f'execute_{domain}_generation',
            f'generate_{domain}_section',
            f'create_{domain}_bullets',
            f'retry_{domain}_failures',
            f'handle_{domain}_timeouts',
            f'implement_{domain}_strategy',
            f'inspect_{domain}_quality',
            f'diagnose_{domain}_issues',
            f'log_{domain}_metrics',
            f'retrieve_{domain}_history',
            f'query_{domain}_generations',
            f'fetch_{domain}_preferences',
            f'search_{domain}_resumes',
            f'match_{domain}_patterns',
            f'find_{domain}_templates',
            f'aggregate_{domain}_state',
            f'merge_{domain}_history',
            f'update_{domain}_profile',
            f'apply_{domain}_safety_policy',
            f'filter_{domain}_content',
            f'validate_{domain}_standards',
            f'assess_{domain}_risk',
            f'compute_{domain}_score',
            f'evaluate_{domain}_level',
            f'track_{domain}_cost',
            f'update_{domain}_usage',
            f'enforce_{domain}_limits',
            f'orchestrate_{domain}_planning',
            f'coordinate_{domain}_generation',
            f'manage_{domain}_workflow',
            f'dispatch_{domain}_tools',
            f'invoke_{domain}_service',
            f'call_{domain}_api',
            f'retry_{domain}_failures',
            f'handle_{domain}_errors',
            f'implement_{domain}_templates',
            f'inspect_{domain}_quality',
            f'diagnose_{domain}_issues',
            f'log_{domain}_metrics',
            f'apply_{domain}_safety',
            f'enforce_{domain}_policy',
            f'validate_{domain}_ethics',
            f'orchestrate_{domain}_planning',
            f'coordinate_{domain}_queries',
            f'manage_{domain}_context',
            f'execute_{domain}_action',
            f'perform_{domain}_operation',
            f'invoke_{domain}_tool',
            f'prepare_{domain}_payload',
            f'format_{domain}_request',
            f'serialize_{domain}_params',
            f'validate_{domain}_schema',
            f'check_{domain}_compliance',
            f'enforce_{domain}_contracts',
            f'apply_{domain}_safety',
            f'enforce_{domain}_policy',
            f'validate_{domain}_ethics',
            f'retrieve_{domain}_memory',
            f'query_{domain}_state',
            f'fetch_{domain}_history',
            f'search_{domain}_vectors',
            f'match_{domain}_patterns',
            f'find_{domain}_context',
            f'apply_{domain}_safety',
            f'enforce_{domain}_policy',
            f'validate_{domain}_ethics',
            f'apply_{domain}_policy',
            f'enforce_{domain}_filters',
            f'validate_{domain}_ethics',
            f'assess_{domain}_risk',
            f'compute_{domain}_score',
            f'evaluate_{domain}_compliance',
            f'track_{domain}_cost',
            f'update_{domain}_usage',
            f'enforce_{domain}_budget',
            f'apply_{domain}_policy',
            f'enforce_{domain}_filters',
            f'validate_{domain}_ethics',
            f'assess_{domain}_risk',
            f'compute_{domain}_score',
            f'evaluate_{domain}_compliance',
            f'track_{domain}_cost',
            f'update_{domain}_usage',
            f'enforce_{domain}_budget'
        ]
        
        for pattern in patterns:
            # Replace domain-specific patterns with generic ones
            replacement = pattern.replace(f'_{domain}_', '_')
            content = content.replace(pattern, replacement)
    
    # Write the fixed content
    with open('unified_structure_subatomic.yaml', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\nDomain tokens after fix:")
    for domain in domains:
        count = content.count(domain)
        if count > 0:
            print(f"  {domain}: {count}")
    
    print("✅ Domain token deduplication completed")

if __name__ == '__main__':
    fix_domain_tokens()
