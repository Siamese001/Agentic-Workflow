import re

with open('agentic_core/adg/extraction/static_scanner.py', 'r') as f:
    content = f.read()

# Count lines before
lines_before = len(content.split('\n'))

# Remove large empty blocks (45+ lines of just whitespace/comments)
lines = content.split('\n')
new_lines = []
empty_streak = 0

for line in lines:
    stripped = line.strip()
    if stripped == '' or stripped.startswith('#') or stripped.startswith('---'):
        empty_streak += 1
        # Keep at most 2 consecutive empty/comment lines
        if empty_streak <= 2:
            new_lines.append(line)
    else:
        empty_streak = 0
        new_lines.append(line)

content = '\n'.join(new_lines)

lines_after = len(content.split('\n'))
print(f'Lines removed: {lines_before - lines_after}')

with open('agentic_core/adg/extraction/static_scanner.py', 'w', newline='') as f:
    f.write(content)
