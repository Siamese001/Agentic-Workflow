#!/usr/bin/env python3
"""Generate wave plan for placeholder test conversions."""

import json
from pathlib import Path

# Load remaining placeholders
with open('remaining_placeholders.json') as f:
    all_files = json.load(f)

# Organize into waves of 38 files each
WAVE_SIZE = 38
waves = {}
wave_num = 13  # Starting from Wave 13

for i in range(0, len(all_files), WAVE_SIZE):
    wave_files = all_files[i:i+WAVE_SIZE]
    waves[wave_num] = {
        'files': wave_files,
        'count': len(wave_files),
    }
    wave_num += 1

# Create wave plan document
plan_content = f"""# Wave 13-30: Placeholder Test Conversion Plan
## Generated: {Path.cwd()}

## Summary
- **Total Remaining Placeholder Files:** {len(all_files)}
- **Waves Required:** {len(waves)}
- **Files Per Wave:** {WAVE_SIZE}

## Wave Assignments

"""

for wave_num, wave_data in waves.items():
    plan_content += f"### Wave {wave_num} ({wave_data['count']} files)\n"
    for f in wave_data['files']:
        plan_content += f"- [ ] `{f}`\n"
    plan_content += "\n"

# Save plan to proper SSOT location
plan_path = Path('docs/reports/plans/wave_13_30_placeholder_conversion_plan.md')
plan_path.parent.mkdir(parents=True, exist_ok=True)
with open(plan_path, 'w') as f:
    f.write(plan_content)

# Save waves as JSON for execution
with open('wave_assignments.json', 'w') as f:
    json.dump(waves, f, indent=2)

print(f'Plan saved to: {plan_path}')
print(f'Total waves: {len(waves)}')

# Print wave summary
for wave_num, wave_data in waves.items():
    print(f"Wave {wave_num}: {wave_data['count']} files")
