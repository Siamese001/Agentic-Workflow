"""Generate detailed snake_case audit report."""
import re
from pathlib import Path
from collections import defaultdict

pattern_def = re.compile(r'^\s*class\s+([a-z_][a-z0-9_]*)\s*[\(:]', re.MULTILINE)
pattern_alias = re.compile(r'^\s*([A-Z][A-Za-z0-9_]*)\s*=\s*([a-z_][a-z0-9_]*)\s*$', re.MULTILINE)

scopes = ['agentic_core', 'apps_rg', 'apps_lic', 'apps_shared']

# Detailed breakdown
by_layer = defaultdict(lambda: {'files': 0, 'defs': 0, 'aliases': 0, 'examples': []})

for scope in scopes:
    for path in Path('.').rglob('*.py'):
        if scope in str(path):
            try:
                content = path.read_text(encoding='utf-8')
                defs = pattern_def.findall(content)
                aliases = pattern_alias.findall(content)
                if defs or aliases:
                    parts = str(path).replace('\\', '/').split('/')
                    if 'agentic_core' in str(path):
                        layer = parts[1] if len(parts) > 1 else 'root'
                    else:
                        layer = parts[0]
                    
                    by_layer[layer]['files'] += 1
                    by_layer[layer]['defs'] += len(defs)
                    by_layer[layer]['aliases'] += len(aliases)
                    if len(by_layer[layer]['examples']) < 3:
                        by_layer[layer]['examples'].extend(defs[:2])
            except:
                pass

print('=== SNAKE_CASE BREAKDOWN BY LAYER ===')
print()
header = f"{'Layer':<30} {'Files':>8} {'Classes':>10} {'Aliases':>10}"
print(header)
print('-' * 62)

total_files = 0
total_defs = 0
total_aliases = 0
for layer, data in sorted(by_layer.items(), key=lambda x: -x[1]['defs']):
    row = f"{layer:<30} {data['files']:>8} {data['defs']:>10} {data['aliases']:>10}"
    print(row)
    if data['examples']:
        examples = ', '.join(data['examples'][:3])
        print(f"   Examples: {examples}")
    total_files += data['files']
    total_defs += data['defs']
    total_aliases += data['aliases']

print('-' * 62)
total_row = f"{'TOTAL':<30} {total_files:>8} {total_defs:>10} {total_aliases:>10}"
print(total_row)
