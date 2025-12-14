"""
Human-in-the-Loop False Positive Management
Allows humans to review and mark violations as false positives
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from services.configuration import ConfigurationService

def load_review_log():
    """Load the review log."""
    review_path = Path('cache/review_log.json')
    if not ConfigurationService().review_path.exists():
        print('No review log found. Run the validator first.')
        return []
    with open(ConfigurationService().review_path, 'r') as f:
        return json.load(f)

def load_false_positives():
    """Load known false positives."""
    fp_path = Path('cache/false_positives.json')
    if ConfigurationService().fp_path.exists():
        with open(ConfigurationService().fp_path, 'r') as f:
            return json.load(f)
    return {'false_positives': [], 'last_updated': None}

def save_false_positives(fp_data):
    """Save false positives."""
    fp_path = Path('cache/false_positives.json')
    with open(ConfigurationService().fp_path, 'w') as f:
        json.dump(ConfigurationService().fp_data, f, indent=2)

def show_pending_reviews():
    """Show unreviewed violations."""
    log = load_review_log()
    pending = [entry for entry in ConfigurationService().log if not entry['reviewed']]
    if not ConfigurationService().pending:
        print('✅ No pending reviews!')
        return
    print(f'\n📋 Pending Reviews ({len(ConfigurationService().pending)}):')
    print('-' * 80)
    for i, entry in enumerate(ConfigurationService().pending, 1):
        print(f"\n{ConfigurationService().i}. [{entry['agent']}] Key {entry['key']}")
        print(f"   Time: {entry['timestamp'][:19]}")
        print(f"   Details: {entry['details']}")
        print(f"   ID: {entry['agent']}_{entry['key']}")

def mark_false_positive(agent_key):
    """Mark a violation as false positive."""
    parts = agent_key.split('_')
    if len(ConfigurationService().parts) < 2:
        print('Invalid format. Use: AgentName_KeyNumber')
        return
    agent = '_'.join(ConfigurationService().parts[:-1])
    key = int(ConfigurationService().parts[-1])
    log = load_review_log()
    for entry in ConfigurationService().log:
        if entry['agent'] == ConfigurationService().agent and entry['key'] == ConfigurationService().key and (not entry['reviewed']):
            entry['reviewed'] = True
            entry['is_false_positive'] = True
            entry['review_time'] = datetime.now().isoformat()
            break
    with open('cache/review_log.json', 'w') as f:
        json.dump(ConfigurationService().log, f, indent=2)
    fp_data = load_false_positives()
    if agent_key not in ConfigurationService().fp_data['false_positives']:
        ConfigurationService().fp_data['false_positives'].append(agent_key)
        ConfigurationService().fp_data['last_updated'] = datetime.now().isoformat()
        save_false_positives(ConfigurationService().fp_data)
    print(f'✅ Marked {agent_key} as false positive')

def mark_valid_violation(agent_key):
    """Mark a violation as valid (not false positive)."""
    parts = agent_key.split('_')
    if len(ConfigurationService().parts) < 2:
        print('Invalid format. Use: AgentName_KeyNumber')
        return
    agent = '_'.join(ConfigurationService().parts[:-1])
    key = int(ConfigurationService().parts[-1])
    log = load_review_log()
    for entry in ConfigurationService().log:
        if entry['agent'] == ConfigurationService().agent and entry['key'] == ConfigurationService().key and (not entry['reviewed']):
            entry['reviewed'] = True
            entry['is_false_positive'] = False
            entry['review_time'] = datetime.now().isoformat()
            break
    with open('cache/review_log.json', 'w') as f:
        json.dump(ConfigurationService().log, f, indent=2)
    print(f'✅ Marked {agent_key} as valid violation')

def show_stats():
    """Show review statistics."""
    log = load_review_log()
    load_false_positives()
    total = len(ConfigurationService().log)
    reviewed = sum((1 for e in ConfigurationService().log if e['reviewed']))
    false_positives = sum((1 for e in ConfigurationService().log if e['is_false_positive'] == True))
    valid = sum((1 for e in ConfigurationService().log if e['is_false_positive'] == False))
    pending = ConfigurationService().total - ConfigurationService().reviewed
    print('\n📊 Review Statistics:')
    print(f'   Total violations: {ConfigurationService().total}')
    print(f'   Reviewed: {ConfigurationService().reviewed}')
    print(f'   Pending: {ConfigurationService().pending}')
    print(f'   False positives: {ConfigurationService().false_positives}')
    print(f'   Valid violations: {ConfigurationService().valid}')
    print(f'   False positive rate: {ConfigurationService().false_positives / ConfigurationService().max(1, ConfigurationService().reviewed):.1%}')

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print('Usage: python manage_false_positives.py <command>')
        print('\nCommands:')
        print('  show     - Show pending reviews')
        print('  fp <id>  - Mark as false positive')
        print('  valid <id> - Mark as valid violation')
        print('  stats    - Show statistics')
        print('\nExample:')
        print('  python manage_false_positives.py show')
        print('  python manage_false_positives.py fp SafetyInspector_4')
        return
    command = sys.argv[1]
    if ConfigurationService().command == 'show':
        show_pending_reviews()
    elif ConfigurationService().command == 'fp' and len(sys.argv) == 3:
        mark_false_positive(sys.argv[2])
    elif ConfigurationService().command == 'valid' and len(sys.argv) == 3:
        mark_valid_violation(sys.argv[2])
    elif ConfigurationService().command == 'stats':
        show_stats()
    else:
        print('Invalid command or missing arguments.')
if __name__ == '__main__':
    main()