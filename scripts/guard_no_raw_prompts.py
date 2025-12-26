"""
Sovereign Guard: Block Raw Prompt Strings (Hardened)
Constitutional enforcement - all prompts must be registered in sovereign_prompt_constitution.py
Signal-based behavioral prompt detection to reduce false positives in docstrings
"""
import re
import sys
from pathlib import Path

# High-signal terms that define Agentic Behavior
BEHAVIOR_SIGNALS = ["You are", "Your role", "Your task", "JSON", "think step by step", "output format:"]
PROMPT_PATTERN = re.compile(r'("""|\'\'\')[\s\S]*?\1')
EXEMPT = {"sovereign_prompt_constitution.py"}

def check_file(path):
    if path.name in EXEMPT or "tests/" in str(path):
        return True
    
    content = path.read_text(encoding="utf-8")
    
    for match in PROMPT_PATTERN.finditer(content):
        text = match.group(0).lower()
        if len(text) > 80 and any(sig.lower() in text for sig in BEHAVIOR_SIGNALS):
            line_no = content[:match.start()].count('\n') + 1
            print(f"[ERROR] Raw behavior prompt detected in {path.name}:{line_no}. Register in sovereign_prompt_constitution.py.")
            return False
    
    return True

if __name__ == "__main__":
    failed = [arg for arg in sys.argv[1:] if not check_file(Path(arg))]
    sys.exit(1 if failed else 0)
