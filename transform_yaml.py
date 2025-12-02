#!/usr/bin/env python3

import yaml
import re
from pathlib import Path

def transform_yaml_structure():
    """Transform legacy YAML structure to canonical L1-L5/P1-P4 format"""
    
    # Read the original YAML
    with open('unified_structure_subatomic.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Legacy to canonical mappings
    layer_mapping = {
        'plan-layer': 'L1_cognition',
        'exec-layer': 'L2_execution', 
        'orc-layer': 'L3_orchestration',
        'mem-layer': 'L4_memory',
        'safe-layer': 'L5_safety'
    }
    
    phase_mapping = {
        'plan-phase': 'P1_retrieve',
        'retrieve-phase': 'P1_retrieve',
        'inspect-phase': 'P2_inspect',
        'expand-phase': 'P2_inspect',
        'refine-phase': 'P3_aggregate',
        'act-phase': 'P3_aggregate',
        'agg-phase': 'P3_aggregate',
        'validate-phase': 'P2_inspect',
        'safety-phase': 'P4_safety'
    }
    
    def normalize_name(name):
        """Convert hyphenated names to snake_case and remove domain tokens"""
        # Convert hyphens to underscores
        normalized = name.replace('-', '_')
        
        # Remove domain tokens from deeper nodes
        domains = ['agentic_core', 'apps', 'config', 'data', 'observability', 
                  'prompt_governance', 'runtime', 'schemas', 'scripts', 'tests',
                  'resume', 'lic', 'shared', 'rg', 'config', 'data', 'runtime',
                  'observability', 'prompt', 'schema', 'script', 'test']
        
        for domain in domains:
            # Remove domain prefix if present
            if normalized.startswith(f'{domain}_'):
                normalized = normalized[len(domain)+1:]
            # Remove domain suffix if present  
            if normalized.endswith(f'_{domain}'):
                normalized = normalized[:-len(domain)-1]
        
        return normalized
    
    def transform_node(node, domain_name, path=[]):
        """Recursively transform a node"""
        if isinstance(node, dict):
            result = {}
            
            # Handle special case for apps domain structure
            if domain_name == 'apps' and path == []:
                # apps has subdomains: rg, lic, shared
                for subdomain, subdomain_data in node.items():
                    if subdomain in ['rg', 'lic', 'shared']:
                        result[subdomain] = transform_domain_structure(subdomain_data, subdomain)
                    else:
                        result[subdomain] = transform_node(subdomain_data, domain_name, [subdomain])
                return result
            else:
                # Regular domain structure
                return transform_domain_structure(node, domain_name)
        
        return node
    
    def transform_domain_structure(domain_data, domain_name):
        """Transform a domain's layer/phase structure"""
        if not isinstance(domain_data, dict):
            return domain_data
            
        result = {}
        
        # Process legacy layers
        for legacy_layer, layer_data in domain_data.items():
            if legacy_layer in layer_mapping:
                canonical_layer = layer_mapping[legacy_layer]
                result[canonical_layer] = transform_layer_structure(layer_data, domain_name)
            elif legacy_layer == '__init__.py':
                result[legacy_layer] = layer_data
            # Skip any other non-layer nodes
        
        return result
    
    def transform_layer_structure(layer_data, domain_name):
        """Transform a layer's phase structure"""
        if not isinstance(layer_data, dict):
            return layer_data
            
        result = {}
        
        # Process legacy phases
        for legacy_phase, phase_data in layer_data.items():
            if legacy_phase in phase_mapping:
                canonical_phase = phase_mapping[legacy_phase]
                result[canonical_phase] = transform_phase_structure(phase_data, domain_name)
            elif legacy_phase == '__init__.py':
                result[legacy_phase] = phase_data
        
        return result
    
    def transform_phase_structure(phase_data, domain_name):
        """Transform a phase's intent/axis/verb_group structure"""
        if not isinstance(phase_data, dict):
            return phase_data
            
        result = {}
        
        for intent_name, intent_data in phase_data.items():
            if intent_name == '__init__.py':
                result[intent_name] = intent_data
            else:
                # Normalize intent name and transform children
                normalized_intent = normalize_name(intent_name)
                
                # Remove domain-specific prefixes
                if normalized_intent.startswith(f'get_{domain_name}_'):
                    normalized_intent = f'get_info{normalized_intent[len(f"get_{domain_name}"):]}' if normalized_intent[len(f'get_{domain_name}'):] else 'get_info'
                elif normalized_intent.startswith(f'check_{domain_name}_'):
                    normalized_intent = f'check_rules{normalized_intent[len(f"check_{domain_name}"):]}' if normalized_intent[len(f'check_{domain_name}'):] else 'check_rules'
                elif normalized_intent.startswith(f'find_{domain_name}_'):
                    normalized_intent = f'find_problems{normalized_intent[len(f"find_{domain_name}"):]}' if normalized_intent[len(f'find_{domain_name}'):] else 'find_problems'
                elif normalized_intent.startswith(f'update_{domain_name}_'):
                    normalized_intent = f'update_state{normalized_intent[len(f"update_{domain_name}"):]}' if normalized_intent[len(f'update_{domain_name}'):] else 'update_state'
                elif normalized_intent.startswith(f'use_{domain_name}_'):
                    normalized_intent = f'use_tools{normalized_intent[len(f"use_{domain_name}"):]}' if normalized_intent[len(f'use_{domain_name}'):] else 'use_tools'
                elif normalized_intent.startswith(f'manage_{domain_name}_'):
                    normalized_intent = f'manage_costs{normalized_intent[len(f"manage_{domain_name}"):]}' if normalized_intent[len(f'manage_{domain_name}'):] else 'manage_costs'
                
                result[normalized_intent] = transform_intent_structure(intent_data, domain_name)
        
        return result
    
    def transform_intent_structure(intent_data, domain_name):
        """Transform intent's axis/verb_group structure and remove 'general' nodes"""
        if not isinstance(intent_data, dict):
            return intent_data
            
        result = {}
        
        for axis_name, axis_data in intent_data.items():
            if axis_name == '__init__.py':
                result[axis_name] = axis_data
            elif axis_name == 'general':
                # Remove 'general' node and promote its children
                for verb_name, verb_data in axis_data.items():
                    if verb_name == '__init__.py':
                        result[verb_name] = verb_data
                    else:
                        normalized_verb = normalize_name(verb_name)
                        result[normalized_verb] = transform_verb_structure(verb_data, domain_name)
            else:
                # Normalize axis name and transform children
                normalized_axis = normalize_name(axis_name)
                result[normalized_axis] = transform_axis_structure(axis_data, domain_name)
        
        return result
    
    def transform_axis_structure(axis_data, domain_name):
        """Transform axis's verb_group structure"""
        if not isinstance(axis_data, dict):
            return axis_data
            
        result = {}
        
        for verb_name, verb_data in axis_data.items():
            if verb_name == '__init__.py':
                result[verb_name] = verb_data
            else:
                normalized_verb = normalize_name(verb_name)
                result[normalized_verb] = transform_verb_structure(verb_data, domain_name)
        
        return result
    
    def transform_verb_structure(verb_data, domain_name):
        """Transform verb structure and normalize filenames"""
        if not isinstance(verb_data, dict):
            return verb_data
            
        result = {}
        
        for filename, file_value in verb_data.items():
            if filename == '__init__.py':
                result[filename] = file_value
            else:
                # Normalize filename by removing domain tokens
                normalized_filename = normalize_name(filename)
                result[normalized_filename] = file_value
        
        return result
    
    # Transform the entire structure
    transformed_data = {}
    
    # Handle the agentic-directory wrapper
    if 'agentic-directory' in data:
        for domain_name, domain_data in data['agentic-directory'].items():
            transformed_data[domain_name] = transform_node(domain_data, domain_name)
    else:
        # Direct domain structure
        for domain_name, domain_data in data.items():
            transformed_data[domain_name] = transform_node(domain_data, domain_name)
    
    # Write the transformed YAML
    with open('unified_structure_subatomic_transformed.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(transformed_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("Transformation completed!")
    print(f"Original file: unified_structure_subatomic.yaml")
    print(f"Transformed file: unified_structure_subatomic_transformed.yaml")
    
    # Count files for verification
    def count_files(data):
        count = 0
        if isinstance(data, dict):
            for value in data.values():
                count += count_files(value)
        elif isinstance(data, str) and data.endswith('.py'):
            count += 1
        return count
    
    original_count = count_files(data)
    transformed_count = count_files(transformed_data)
    
    print(f"Original file count: {original_count}")
    print(f"Transformed file count: {transformed_count}")
    
    if original_count == transformed_count:
        print("✅ Zero-loss verification PASSED")
    else:
        print("❌ Zero-loss verification FAILED")
    
    return transformed_data

if __name__ == '__main__':
    transform_yaml_structure()
