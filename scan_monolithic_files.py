#!/usr/bin/env python3
"""
Scan repository for monolithic non-agentic files that should be modularized.
"""
import os
import re
from pathlib import Path

# Skip directories
SKIP_DIRS = {'.git', '__pycache__', 'node_modules', 'venv', '.venv', 'vendor', '.sovereign_healing_backup'}

def is_agentic(content):
    """Check if file contains agent behavior"""
    markers = ['BaseAgent', 'CanonBaseAgent', '@tool', 'def execute(', 'def run(', 'def step(']
    return any(marker in content for marker in markers)

def count_structures(content):
    """Count class definitions and dataclasses"""
    classes = len(re.findall(r'^class \w+', content, re.MULTILINE))
    dataclasses = len(re.findall(r'@dataclass', content))
    basemodels = len(re.findall(r'\(BaseModel\)', content))
    enums = len(re.findall(r'\(Enum\)', content))
    return classes, dataclasses, basemodels, enums

def scan_repo():
    results = {
        'python_monolithic': [],
        'json_large': [],
        'yaml_large': [],
        'md_large': [],
    }
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        
        for f in files:
            path = Path(root) / f
            rel_path = str(path).replace('\\', '/')
            
            if 'archive' in rel_path.lower():
                continue
                
            try:
                size = path.stat().st_size
                
                if f.endswith('.py'):
                    content = path.read_text(encoding='utf-8', errors='ignore')
                    lines = len(content.split('\n'))
                    
                    if lines > 500:
                        classes, dc, bm, enums = count_structures(content)
                        agentic = is_agentic(content)
                        
                        if not agentic and (dc > 5 or bm > 5 or enums > 5 or classes > 15):
                            results['python_monolithic'].append({
                                'path': rel_path,
                                'lines': lines,
                                'classes': classes,
                                'dataclasses': dc,
                                'basemodels': bm,
                                'enums': enums
                            })
                
                elif f.endswith('.json') and size > 10000:
                    lines = len(path.read_text(encoding='utf-8', errors='ignore').split('\n'))
                    results['json_large'].append({'path': rel_path, 'lines': lines, 'size_kb': size // 1024})
                
                elif f.endswith(('.yaml', '.yml')) and size > 5000:
                    lines = len(path.read_text(encoding='utf-8', errors='ignore').split('\n'))
                    results['yaml_large'].append({'path': rel_path, 'lines': lines, 'size_kb': size // 1024})
                
                elif f.endswith('.md') and size > 20000:
                    lines = len(path.read_text(encoding='utf-8', errors='ignore').split('\n'))
                    results['md_large'].append({'path': rel_path, 'lines': lines, 'size_kb': size // 1024})
                    
            except Exception:
                pass
    
    for key in results:
        results[key].sort(key=lambda x: -x['lines'])
    
    return results

def print_results(results):
    print('=' * 100)
    print('MONOLITHIC NON-AGENTIC FILES TO MODULARIZE FOR SUBATOMIC ARCHITECTURE')
    print('=' * 100)
    print()
    
    print('## PYTHON FILES (>500 lines, >5 dataclasses/BaseModels/Enums OR >15 classes)')
    print('-' * 100)
    if results['python_monolithic']:
        for item in results['python_monolithic']:
            print(f"{item['lines']:5d} lines | {item['classes']:3d} cls | {item['dataclasses']:2d} dc | {item['basemodels']:2d} bm | {item['enums']:2d} enum | {item['path']}")
    else:
        print('None found')
    print()
    
    print('## JSON FILES (>10KB)')
    print('-' * 100)
    if results['json_large']:
        for item in results['json_large'][:30]:
            print(f"{item['lines']:5d} lines | {item['size_kb']:4d} KB | {item['path']}")
    else:
        print('None found')
    print()
    
    print('## YAML FILES (>5KB)')
    print('-' * 100)
    if results['yaml_large']:
        for item in results['yaml_large'][:30]:
            print(f"{item['lines']:5d} lines | {item['size_kb']:4d} KB | {item['path']}")
    else:
        print('None found')
    print()
    
    print('## MARKDOWN FILES (>20KB)')
    print('-' * 100)
    if results['md_large']:
        for item in results['md_large'][:30]:
            print(f"{item['lines']:5d} lines | {item['size_kb']:4d} KB | {item['path']}")
    else:
        print('None found')
    print()
    
    print('=' * 100)
    total = len(results['python_monolithic']) + len(results['json_large']) + len(results['yaml_large']) + len(results['md_large'])
    print(f'TOTAL FILES TO MODULARIZE: {total}')
    print(f'  Python: {len(results["python_monolithic"])} | JSON: {len(results["json_large"])} | YAML: {len(results["yaml_large"])} | Markdown: {len(results["md_large"])}')
    print('=' * 100)

if __name__ == '__main__':
    results = scan_repo()
    print_results(results)
