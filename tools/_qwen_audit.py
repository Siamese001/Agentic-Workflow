"""Audit Qwen/healing routing wiring - find all usages of key symbols."""
import os
from pathlib import Path

search_terms = ['QwenInvokerAdapter', 'GeminiInvokerAdapter', 'LocalAgentAdapter', 'healing_provider_adapters', 'validate_qwen_startup_state', 'qwen_vllm_inference', 'QWEN_VLLM_ENABLED', 'invoke_qwen_vllm', 'DefaultHealingProviderInvoker', 'dispatch_healing']
SKIP_DIRS = {'__pycache__', '.git', 'archives', '.backup', '.healing_backups'}
root = 'c:/Git/Agentic-Workflow'
found = {}
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fname in filenames:
        if not fname.endswith('.py'):
            continue
        fpath = Path(dirpath) / fname
        try:
            content = open(fpath, encoding='utf-8', errors='ignore').read()
            for term in search_terms:
                if term in content:
                    rel = fpath.replace(root + os.sep, '').replace('\\', '/')
                    found.setdefault(term, []).append(rel)
        # guardian: allow-silent-swallow
        except Exception:
            pass
for term, files in sorted(found.items()):
    print(f'TERM: {term}')
    for f in sorted(files):
        print(f'  {f}')
    print()
