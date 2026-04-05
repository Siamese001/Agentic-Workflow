"""Trace exactly what _inject_import does to bloat_analysis_util.py"""
import re
import sys

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("_trace_inject", "_trace_inject_digest")
record_execution_trace("_trace_inject", "_trace_inject_trace")

# guardian: allow-global-mutation
sys.path.insert(0, 'c:\\Git\\Agentic-Workflow')
_PC = 'agentic_core.L0_routing.config.path_constants'
head_content = '#!/usr/bin/env python3\n"""Bloat analysis script for approved folders."""\n\nimport ast\nfrom collections import defaultdict\nfrom datetime import datetime\nfrom pathlib import Path\n\nfrom agentic_core.L5_safety.config.structure_blueprint.ssot import (\n    GLOBAL_EXCLUDED_DIRS,\n    SOVEREIGN_EXCLUDED_FOLDERS,\n)\n\nROOT = Path(__file__).parent.parent\n'
lines = head_content.splitlines(keepends=True)

def find_last_import(lines):
    last = 0
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith('import ') or s.startswith('from '):
            last = i
            depth = lines[i].count('(') - lines[i].count(')')
            while depth > 0 and i + 1 < len(lines):
                i += 1
                depth += lines[i].count('(') - lines[i].count(')')
                last = i
        i += 1
    return last

def inject(lines, const, module):
    lines = list(lines)
    # guardian: allow-path-string
    from_multi = re.compile('^\\s*from\\s+' + re.escape(module) + '\\s+import\\s+\\(')
    # guardian: allow-path-string
    from_single = re.compile('^(\\s*from\\s+' + re.escape(module) + '\\s+import\\s+)(.+)$')
    for i, ln in enumerate(lines):
        if from_multi.match(ln):
            depth = 0
            j = i
            while j < len(lines):
                depth += lines[j].count('(') - lines[j].count(')')
                if depth <= 0:
                    break
                j += 1
            print(f'  [multi-match] module={module} at line {i}, closing ) at j={j}')
            lines.insert(j, f'    {const},\n')
            return lines
    for i, ln in enumerate(lines):
        m = from_single.match(ln)
        if m:
            names = [n.strip().rstrip(',') for n in m.group(2).split(',') if n.strip()]
            names.append(const)
            names.sort()
            indent = ' ' * (len(ln) - len(ln.lstrip()))
            new_lines = [indent + f'from {module} import (\n']
            for name in names:
                new_lines.append(indent + f'    {name},\n')
            new_lines.append(indent + ')\n')
            lines[i:i + 1] = new_lines
            print(f'  [single→multi] at line {i}, expanded to {len(new_lines)} elements')
            return lines
    last = find_last_import(lines)
    print(f'  [new import] after line {last}: {repr(lines[last].rstrip())}')
    lines.insert(last + 1, f'from {module} import {const}\n')
    return lines
print('=== Injecting AGENTIC_CORE_DIR ===')
lines = inject(lines, 'AGENTIC_CORE_DIR', _PC)
print(''.join(lines[:20]))
print('=== Injecting APPS_RG_DIR ===')
lines = inject(lines, 'APPS_RG_DIR', _PC)
print(''.join(lines[:20]))
print('=== Injecting APPS_LIC_DIR ===')
lines = inject(lines, 'APPS_LIC_DIR', _PC)
print(''.join(lines[:25]))
