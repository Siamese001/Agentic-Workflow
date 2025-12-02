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
        """Convert hyphenated names to snake_case"""
        return name.replace('-', '_')
    
    def remove_domain_tokens(name, domain):
        """Remove domain tokens from names but preserve semantic meaning"""
        if not isinstance(name, str):
            return name
            
        normalized = name
        
        # Remove generic core tokens globally
        normalized = normalized.replace('_core_', '_')
        normalized = normalized.replace('core_', '')
        if normalized.startswith('core_'):
            normalized = normalized[5:]
        if normalized.endswith('_core'):
            normalized = normalized[:-5]
            
        # Remove domain-specific tokens
        if domain:
            normalized = normalized.replace(f'_{domain}_', '_')
            normalized = normalized.replace(f'{domain}_', '')
            normalized = normalized.replace(f'_{domain}', '')
            if normalized.startswith(f'{domain}_'):
                normalized = normalized[len(domain)+1:]
            if normalized.endswith(f'_{domain}'):
                normalized = normalized[:-len(domain)-1]
        
        return normalized
    
    def count_py_files(data):
        """Count .py files in YAML structure"""
        count = 0
        if isinstance(data, dict):
            for key, value in data.items():
                if key.endswith('.py'):
                    count += 1
                count += count_py_files(value)
        return count
    
    def transform_domain(domain_data, domain_name, is_subdomain=False):
        """Transform a single domain structure"""
        if not isinstance(domain_data, dict):
            return domain_data
        
        # Count files before transformation for debugging
        original_files = count_py_files(domain_data)
        print(f"  Processing {domain_name}: {original_files} files")
            
        result = {}
        
        # Check if this is a subdomain container (like apps with rg, lic, shared)
        has_subdomains = False
        subdomain_keys = ['rg', 'lic', 'shared']
        
        for key, content in domain_data.items():
            if key in subdomain_keys:
                has_subdomains = True
                break
        
        if has_subdomains and not is_subdomain:
            # This is a domain with subdomains - transform each subdomain
            print(f"    {domain_name} has subdomains")
            for subdomain_name, subdomain_data in domain_data.items():
                if subdomain_name in subdomain_keys:
                    print(f"    Transforming subdomain: {subdomain_name}")
                    result[subdomain_name] = transform_domain(subdomain_data, subdomain_name, is_subdomain=True)
                elif subdomain_name == '__init__.py':
                    result[subdomain_name] = subdomain_data
                else:
                    print(f"    Warning: Unexpected node '{subdomain_name}' in domain '{domain_name}'")
                    result[subdomain_name] = subdomain_data
        else:
            # Regular domain with layers
            for legacy_layer, layer_content in domain_data.items():
                if legacy_layer in layer_mapping:
                    canonical_layer = layer_mapping[legacy_layer]
                    print(f"    Mapping layer: {legacy_layer} -> {canonical_layer}")
                    result[canonical_layer] = transform_layer(layer_content, domain_name)
                elif legacy_layer == '__init__.py':
                    result[legacy_layer] = layer_content
                else:
                    print(f"    WARNING: Skipping unmapped layer '{legacy_layer}' in domain '{domain_name}'")
                    result[legacy_layer] = layer_content  # Keep it for now to preserve files
        
        # Count files after transformation
        transformed_files = count_py_files(result)
        print(f"    {domain_name} transformed: {original_files} -> {transformed_files} files")
        
        return result
    
    def transform_layer(layer_data, domain_name):
        """Transform layer structure"""
        if not isinstance(layer_data, dict):
            return layer_data
            
        result = {}
        
        # Process each legacy phase and merge when collisions occur
        for legacy_phase, phase_content in layer_data.items():
            if legacy_phase in phase_mapping:
                canonical_phase = phase_mapping[legacy_phase]
                print(f"      Mapping phase: {legacy_phase} -> {canonical_phase}")
                
                transformed_phase = transform_phase(phase_content, domain_name)
                
                if canonical_phase in result:
                    # Merge with existing phase content
                    print(f"        Merging {legacy_phase} into existing {canonical_phase}")
                    result[canonical_phase] = merge_phase_contents(result[canonical_phase], transformed_phase)
                else:
                    result[canonical_phase] = transformed_phase
            elif legacy_phase == '__init__.py':
                result[legacy_phase] = phase_content
            else:
                print(f"      WARNING: Skipping unmapped phase '{legacy_phase}' in domain '{domain_name}'")
                result[legacy_phase] = phase_content  # Keep it for now to preserve files
                
        return result
    
    def merge_phase_contents(existing_phase, new_phase):
        """Merge contents of two phases that map to the same canonical phase"""
        if not isinstance(existing_phase, dict) or not isinstance(new_phase, dict):
            return existing_phase
            
        merged = existing_phase.copy()
        
        for intent_name, intent_content in new_phase.items():
            if intent_name == '__init__.py':
                if '__init__.py' not in merged:
                    merged[intent_name] = intent_content
            elif intent_name in merged:
                # Merge intent contents if collision occurs
                merged[intent_name] = merge_intent_contents(merged[intent_name], intent_content)
            else:
                merged[intent_name] = intent_content
                
        return merged
    
    def merge_intent_contents(existing_intent, new_intent):
        """Merge contents of two intents that have the same name"""
        if not isinstance(existing_intent, dict) or not isinstance(new_intent, dict):
            return existing_intent
            
        merged = existing_intent.copy()
        
        for axis_name, axis_content in new_intent.items():
            if axis_name == '__init__.py':
                if '__init__.py' not in merged:
                    merged[axis_name] = axis_content
            elif axis_name in merged:
                # Merge axis contents if collision occurs
                merged[axis_name] = merge_axis_contents(merged[axis_name], axis_content)
            else:
                merged[axis_name] = axis_content
                
        return merged
    
    def merge_axis_contents(existing_axis, new_axis):
        """Merge contents of two axes that have the same name"""
        if not isinstance(existing_axis, dict) or not isinstance(new_axis, dict):
            return existing_axis
            
        merged = existing_axis.copy()
        
        for verb_name, verb_content in new_axis.items():
            if verb_name == '__init__.py':
                if '__init__.py' not in merged:
                    merged[verb_name] = verb_content
            elif verb_name in merged:
                # Merge verb contents if collision occurs
                merged[verb_name] = merge_verb_contents(merged[verb_name], verb_content)
            else:
                merged[verb_name] = verb_content
                
        return merged
    
    def merge_verb_contents(existing_verb, new_verb):
        """Merge contents of two verbs that have the same name"""
        if not isinstance(existing_verb, dict) or not isinstance(new_verb, dict):
            return existing_verb
            
        merged = existing_verb.copy()
        
        for filename, file_value in new_verb.items():
            if filename not in merged:
                merged[filename] = file_value
            # If file exists, keep the existing one (they should be the same)
                
        return merged
    
    def transform_phase(phase_data, domain_name):
        """Transform phase structure"""
        if not isinstance(phase_data, dict):
            return phase_data
        
        # Count files before transformation for debugging
        original_files = count_py_files(phase_data)
        print(f"        Transforming phase with {original_files} files")
            
        result = {}
        
        # Process each intent
        for intent_name, intent_content in phase_data.items():
            if intent_name == '__init__.py':
                result[intent_name] = intent_content
            else:
                # Normalize intent name
                normalized_intent = normalize_name(intent_name)
                normalized_intent = remove_domain_tokens(normalized_intent, domain_name)
                
                intent_files_before = count_py_files(intent_content)
                print(f"          Processing intent: {intent_name} -> {normalized_intent} ({intent_files_before} files)")
                
                transformed_intent = transform_intent(intent_content, domain_name)
                intent_files_after = count_py_files(transformed_intent)
                
                if intent_files_before != intent_files_after:
                    print(f"            WARNING: Intent lost {intent_files_before - intent_files_after} files")
                
                result[normalized_intent] = transformed_intent
        
        # Count files after transformation
        transformed_files = count_py_files(result)
        print(f"        Phase transformed: {original_files} -> {transformed_files} files")
                
        return result
    
    def transform_intent(intent_data, domain_name):
        """Transform intent structure and handle 'general' nodes"""
        if not isinstance(intent_data, dict):
            return intent_data
            
        result = {}
        general_children = {}
        
        # First, collect all children from 'general' nodes
        for axis_name, axis_content in intent_data.items():
            if axis_name == 'general':
                for child_name, child_content in axis_content.items():
                    if child_name == '__init__.py':
                        if '__init__.py' not in result:
                            result[child_name] = child_content
                    else:
                        normalized_child = normalize_name(child_name)
                        general_children[normalized_child] = child_content
        
        # Then process non-general nodes
        for axis_name, axis_content in intent_data.items():
            if axis_name == '__init__.py':
                if '__init__.py' not in result:
                    result[axis_name] = axis_content
            elif axis_name == 'general':
                # Skip - already processed above
                continue
            else:
                # Normalize axis name
                normalized_axis = normalize_name(axis_name)
                result[normalized_axis] = transform_axis(axis_content, domain_name)
        
        # Finally merge general children (they take precedence over duplicates)
        for child_name, child_content in general_children.items():
            if child_name == '__init__.py':
                result[child_name] = child_content
            else:
                result[child_name] = transform_axis(child_content, domain_name)
                
        return result
    
    def transform_axis(axis_data, domain_name):
        """Transform axis structure"""
        if not isinstance(axis_data, dict):
            return axis_data
            
        result = {}
        
        for verb_name, verb_content in axis_data.items():
            if verb_name == '__init__.py':
                result[verb_name] = verb_content
            else:
                # Normalize verb name
                normalized_verb = normalize_name(verb_name)
                result[normalized_verb] = transform_verb(verb_content, domain_name)
                
        return result
    
    def transform_verb(verb_data, domain_name):
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
                normalized_filename = remove_domain_tokens(normalized_filename, domain_name)
                result[normalized_filename] = file_value
                
        return result
    
    # Start transformation
    print("Starting YAML transformation...")
    
    # Handle agentic-directory wrapper
    if 'agentic-directory' in data:
        source_data = data['agentic-directory']
    else:
        source_data = data
    
    transformed_data = {}
    
    # Transform each domain
    for domain_name, domain_content in source_data.items():
        print(f"Transforming domain: {domain_name}")
        transformed_data[domain_name] = transform_domain(domain_content, domain_name)
    
    # Write the transformed YAML
    with open('unified_structure_subatomic_transformed.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(transformed_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Count files for verification
    original_count = count_py_files(source_data)
    transformed_count = count_py_files(transformed_data)
    
    print(f"\nTransformation completed!")
    print(f"Original file count: {original_count}")
    print(f"Transformed file count: {transformed_count}")
    
    if original_count == transformed_count:
        print("✅ Zero-loss verification PASSED")
        return True
    else:
        print(f"❌ Zero-loss verification FAILED - lost {original_count - transformed_count} files")
        return False

if __name__ == '__main__':
    success = transform_yaml_structure()
    if success:
        print("\n🎯 Transformation successful! Ready to replace original file.")
    else:
        print("\n⚠️  Transformation has issues - needs debugging.")
