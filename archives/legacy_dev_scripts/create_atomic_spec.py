#!/usr/bin/env python3
"""
Phase C - Convert RG_CAPABILITIES to ATOMIC_RG_SPEC
Direct one-to-one transformation with bucket remapping
"""

import sys
import json
from pathlib import Path

# Add path to import RG_CAPABILITIES
sys.path.append(r'C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\agentic_workflow\RG_capabilities')

from reconstructed_capabilities import RG_CAPABILITIES

def create_atomic_spec():
    """Transform RG_CAPABILITIES to ATOMIC_RG_SPEC with bucket mapping"""
    
    # Bucket mapping from legacy to atomic
    bucket_mapping = {
        "routing_rules": "routing",
        "parameter_presets": "parameters", 
        "quant_rules": "quant",
        "bullet_engine": "bullets",
        "rewrite_engine": "rewrite",
        "skills_engine": "skills",
        "section_rules": "sections",
        "job_workflow_steps": "job_workflow",
        "ats_rules": "ats",
        "template_layouts": "templates",
        "formatting_rules": "formatting",
        "seniority_rules": "seniority",
        "tone_rules": "tone",
        "constraints": "constraints",
        "validator_rules": "validators",
        "mission_fields": "mission"
    }
    
    # Create ATOMIC_RG_SPEC with direct mapping
    ATOMIC_RG_SPEC = {}
    
    for legacy_bucket, atomic_bucket in bucket_mapping.items():
        if legacy_bucket in RG_CAPABILITIES:
            ATOMIC_RG_SPEC[atomic_bucket] = RG_CAPABILITIES[legacy_bucket]
        else:
            ATOMIC_RG_SPEC[atomic_bucket] = {}
    
    return ATOMIC_RG_SPEC

def write_atomic_spec():
    """Write the atomic spec file"""
    
    # Create the atomic spec
    atomic_spec = create_atomic_spec()
    
    # Write to file
    output_path = Path(r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\agentic_workflow\RG_capabilities\rg_atomic_spec.py")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("#!/usr/bin/env python3\n")
        f.write('"""\n')
        f.write("ATOMIC_RG_SPEC - Normalized Resume Generator Specification\n")
        f.write("Direct transformation from RG_CAPABILITIES with zero loss\n")
        f.write('"""\n\n')
        
        f.write("ATOMIC_RG_SPEC = {\n")
        
        for bucket, content in atomic_spec.items():
            # Use json.dumps for proper serialization with unicode handling
            content_json = json.dumps(content, separators=(',', ':'), ensure_ascii=False)
            f.write(f'    "{bucket}": {content_json},\n')
        
        f.write("}\n")
    
    print(f"ATOMIC_RG_SPEC written to {output_path}")
    
    # Verify the transformation
    print("Transformation summary:")
    for bucket, content in atomic_spec.items():
        print(f"  {bucket}: {len(content)} files/capabilities")

if __name__ == "__main__":
    write_atomic_spec()
