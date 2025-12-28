"""
Sovereign Guard: Block Hardcoded Configuration Constants
Constitutional enforcement - all config must be centralized in sovereign_config.py
"""
import re
import sys
from pathlib import Path

# Patterns that indicate hardcoded configuration
HARDCODED_PATTERNS = [
    (r'PRIMARY_MODEL\s*=\s*["\']', "Model selection"),
    (r'REASONING_MODEL\s*=\s*["\']', "Model selection"),
    (r'MAX_RETRY_ATTEMPTS\s*=\s*\d+', "Retry configuration"),
    (r'CHECKPOINT_INTERVAL\s*=\s*\d+', "Checkpoint configuration"),
    (r'SEMANTIC_SIMILARITY_THRESHOLD\s*=\s*[\d.]+', "Threshold configuration"),
    (r'gpt-4o["\']', "Hardcoded model name"),
    (r'o1-preview["\']', "Hardcoded model name"),
]

EXEMPT = {"sovereign_config.py"}

def check_file(path):
    if path.name in EXEMPT:
        return True
    
    content = path.read_text(encoding="utf-8")
    lines = content.split("\n")
    
    violations = []
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("#"):
            continue
        
        for pattern, description in HARDCODED_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append((i, description, line.strip()[:60]))
                break
    
    if violations:
        print(f"[ERROR] Hardcoded config in {path.name}:")
        for line, desc, content in violations:
            print(f"  Line {line} ({desc}): {content}...")
        print("  → Centralize in: agentic_core/config/blueprint_sovereign/environments/sovereign_config.py")
        return False
    
    return True

if __name__ == "__main__":
    failed = [arg for arg in sys.argv[1:] if not check_file(Path(arg))]
    sys.exit(1 if failed else 0)
