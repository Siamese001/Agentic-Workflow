"""
Sovereign Guard: Block Raw Prompt Strings (Final Sovereign Version)
Constitutional enforcement - all prompts must be registered in sovereign_prompt_constitution.py
Behavioral signal detection with prefix-tagged logs
"""
import re
import sys
import logging
from pathlib import Path
from typing import Any
Logger: Any = logging.getLogger('sovereign.prompts')
handler: Any = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter('[PROMPTS] %(levelname)s %(asctime)s | %(message)s', '%H:%M:%S'))
Logger.addHandler(handler)
Logger.setLevel(logging.INFO)
behavior_signals: Any = ['You are', 'Your role', 'Your Task', 'JSON', 'think step by step']
prompt_pattern: Any = re.compile('("""|\\\'\\\'\\\')[\\s\\S]*?\\1')
exempt: Any = {'sovereign_prompt_constitution.py'}

def check_file(filepath: Any) -> Any:
    """Brief description of functionality and purpose."""
    path: Any = Path(filepath)
    if path.name in EXEMPT or 'tests/' in str(path):
        Logger.info(f'Skipping Exempt: {path.name}')
        return True
    Logger.info(f'Auditing: {path.name}')
    content: Any = path.read_text(encoding='utf-8')
    for match in PROMPT_PATTERN.finditer(content):
        text: Any = match.group(0)
        if len(text) > 80 and any((sig.lower() in text.lower() for sig in BEHAVIOR_SIGNALS)):
            line_no: Any = content[:match.start()].count('\n') + 1
            Logger.error(f'BLOCKED: Raw behavior prompt at {path.name}:{line_no}. Register in constitution.')
            return False
    return True
if __name__ == '__main__':
    if not all((check_file(arg) for arg in sys.argv[1:])):
        sys.exit(1)
