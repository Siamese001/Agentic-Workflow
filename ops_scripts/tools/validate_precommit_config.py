#!/usr/bin/env python3
"""
Validate pre-commit configuration to prevent hook ordering issues.

Checks for:
- Hook ordering conflicts
- Missing auto-stage hook
- Known problematic hook combinations
"""

import yaml
import sys
from pathlib import Path


def check_auto_stage_hook_present(config):
    """Ensure auto-stage-hook-fixes is present and last in T0."""
    t0_hooks = []
    auto_stage_found = False
    auto_stage_position = -1
    
    for repo in config.get('repos', []):
        if 'https://github.com/pre-commit/pre-commit-hooks' in str(repo.get('rev', '')):
            for hook in repo.get('hooks', []):
                if hook.get('id') == 'auto-stage-hook-fixes':
                    auto_stage_found = True
                    auto_stage_position = len(t0_hooks)
                t0_hooks.append(hook['id'])
    
    if not auto_stage_found:
        print("❌ Missing auto-stage-hook-fixes hook")
        return False
    
    if auto_stage_position != len(t0_hooks) - 1:
        print(f"❌ auto-stage-hook-fixes is not last in T0 (position {auto_stage_position} of {len(t0_hooks)})")
        return False
    
    print("✅ auto-stage-hook-fixes is properly positioned")
    return True


def check_hook_ordering(config):
    """Check for known problematic hook ordering."""
    issues = []
    
    # T0 hooks should be in specific order
    t0_order = [
        'trailing-whitespace',
        'end-of-file-fixer', 
        'mixed-line-ending',
        'check-merge-conflict',
        'auto-stage-hook-fixes'
    ]
    
    for repo in config.get('repos', []):
        if 'https://github.com/pre-commit/pre-commit-hooks' in str(repo.get('rev', '')):
            hooks = [h['id'] for h in repo.get('hooks', [])]
            
            # Check if T0 hooks are in correct order
            t0_in_config = [h for h in hooks if h in t0_order]
            if t0_in_config != t0_order[:len(t0_in_config)]:
                issues.append("T0 hooks not in recommended order")
    
    if issues:
        for issue in issues:
            print(f"⚠️  {issue}")
        return False
    
    print("✅ Hook ordering looks good")
    return True


def check_exclude_patterns(config):
    """Check for exclude patterns that might cause issues."""
    global_exclude = config.get('exclude', '')
    
    # Should exclude .md files from formatting hooks
    if '.*\.md$' not in global_exclude:
        print("⚠️  Consider excluding .md files from formatting hooks")
    
    print("✅ Exclude patterns look reasonable")
    return True


def main():
    """Validate pre-commit configuration."""
    config_path = Path('.pre-commit-config.yaml')
    
    if not config_path.exists():
        print("❌ .pre-commit-config.yaml not found")
        return 1
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML: {e}")
        return 1
    
    print("Validating pre-commit configuration...")
    print()
    
    all_good = True
    all_good &= check_auto_stage_hook_present(config)
    all_good &= check_hook_ordering(config)
    all_good &= check_exclude_patterns(config)
    
    print()
    if all_good:
        print("✅ Pre-commit configuration is valid")
        return 0
    else:
        print("❌ Pre-commit configuration has issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
