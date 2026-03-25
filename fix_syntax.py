#!/usr/bin/env python3
"""Fix syntax error in sovereign_config.py"""

with open(r'C:\Git\Agentic-Workflow\agentic_core\config\core\sovereign_config.py') as f:
    lines = f.readlines()

# Fix lines 251-253
lines[250] = '            # TODO: Add proper input validation\n'
lines[251] = '            logger.warning(f"Config key {key} expected int, got {val}. Using default {default}.")\n'
lines[252] = '            return default\n'

with open(r'C:\Git\Agentic-Workflow\agentic_core\config\core\sovereign_config.py', 'w') as f:
    f.writelines(lines)

print('Fixed syntax error in sovereign_config.py')
