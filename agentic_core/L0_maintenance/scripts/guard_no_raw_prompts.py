"""
Sovereign Guard: Block Raw Prompt Strings (Final Sovereign Version)
Constitutional enforcement - all prompts must be registered in sovereign_prompt_constitution.py
Behavioral signal detection with prefix-tagged logs
"""
import re
import sys
import logging
from pathlib import Path

# Logger Setup
logger = logging.getLogger("sovereign.prompts")
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter("[PROMPTS] %(levelname)s %(asctime)s | %(message)s", "%H:%M:%S"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

BEHAVIOR_SIGNALS = ["You are", "Your role", "Your task", "JSON", "think step by step"]
PROMPT_PATTERN = re.compile(r'("""|\'\'\')[\s\S]*?\1')
EXEMPT = {"sovereign_prompt_constitution.py"}

def check_file(filepath):
    path = Path(filepath)
    if path.name in EXEMPT or "tests/" in str(path):
        logger.info(f"Skipping Exempt: {path.name}")
        return True
    
    logger.info(f"Auditing: {path.name}")
    content = path.read_text(encoding="utf-8")
    for match in PROMPT_PATTERN.finditer(content):
        text = match.group(0)
        if len(text) > 80 and any(sig.lower() in text.lower() for sig in BEHAVIOR_SIGNALS):
            line_no = content[:match.start()].count('\n') + 1
            logger.error(f"BLOCKED: Raw behavior prompt at {path.name}:{line_no}. Register in constitution.")
            return False
    return True

if __name__ == "__main__":
    if not all(check_file(arg) for arg in sys.argv[1:]):
        sys.exit(1)
