#!/usr/bin/env python3
"""Validate RG_CAPABILITIES bucket structure"""

import sys
sys.path.append(r'C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\agentic_workflow\RG_capabilities')

from reconstructed_capabilities import RG_CAPABILITIES

expected_buckets = [
    'routing_rules', 'parameter_presets', 'quant_rules', 'bullet_engine',
    'rewrite_engine', 'skills_engine', 'section_rules', 'job_workflow_steps',
    'ats_rules', 'template_layouts', 'formatting_rules', 'seniority_rules',
    'tone_rules', 'constraints', 'validator_rules', 'mission_fields'
]

actual_buckets = list(RG_CAPABILITIES.keys())

print(f'Expected: {len(expected_buckets)} buckets')
print(f'Actual: {len(actual_buckets)} buckets')

extra = set(actual_buckets) - set(expected_buckets)
missing = set(expected_buckets) - set(actual_buckets)

if extra:
    print(f'Extra bucket(s): {extra}')
if missing:
    print(f'Missing bucket(s): {missing}')

print('\nFile counts per bucket:')
total_files = 0
for bucket, files in RG_CAPABILITIES.items():
    count = len(files)
    total_files += count
    print(f'  {bucket}: {count} files')

print(f'\nTotal files: {total_files}')

# Show sample files from each bucket
print('\nSample files per bucket:')
for bucket, files in RG_CAPABILITIES.items():
    if files:
        sample_file = list(files.keys())[0]
        print(f'  {bucket}: {sample_file.split("/")[-1]}')
