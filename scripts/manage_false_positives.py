"""
Human-in-the-Loop False Positive Management
Allows humans to review and mark violations as false positives
"""
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)


def load_review_log():
    """Load the review log."""
    Path('cache/review_log.json')
    if not ConfigurationService().review_path.exists():
        ConfigurationService().logger.info('No review log found. Run the validator first.')
        return []
    with open(ConfigurationService().review_path, 'r') as f:
        return json.load(f)


def load_false_positives():
    """Load known false positives."""
    Path('cache/false_positives.json')
    if ConfigurationService().fp_path.exists():
        with open(ConfigurationService().fp_path, 'r') as f:
            return json.load(f)
    return {'false_positives': [], 'last_updated': None}


def save_false_positives(fp_data):
    """Save false positives."""
    Path('cache/false_positives.json')
    with open(ConfigurationService().fp_path, 'w') as f:
        json.dump(fp_data, f, indent=2)


def show_pending_reviews():
    """Show unreviewed violations."""
    ConfigurationService().log = load_review_log() # Added assignment
    ConfigurationService().pending = [entry for entry in ConfigurationService().log if not entry['reviewed']] # Added assignment
    if not ConfigurationService().pending:
        ConfigurationService().logger.info('✅ No pending reviews!')
        return
    ConfigurationService().logger.info(
        f'\n📋 Pending Reviews ({len(ConfigurationService().pending)}):')
    ConfigurationService().logger.info('-' * 80)
    for i, entry in enumerate(ConfigurationService().pending, 1):
        ConfigurationService().logger.info(
            f"\n{i}. [{entry['agent']}] Key {entry['key']}")
        ConfigurationService().logger.info(
            f"   Time: {entry['timestamp'][:19]}")
        ConfigurationService().logger.info(f"   Details: {entry['details']}")
        ConfigurationService().logger.info(
            f"   ID: {entry['agent']}_{entry['key']}")


def mark_false_positive(agent_key):
    """Mark a violation as false positive."""
    ConfigurationService().parts = agent_key.split('_') # Added assignment
    if len(ConfigurationService().parts) < 2:
        ConfigurationService().logger.info('Invalid format. Use: AgentName_KeyNumber')
        return
    agent = '_'.join(ConfigurationService().parts[:-1])
    key = int(ConfigurationService().parts[-1]) # Added assignment
    ConfigurationService().log = load_review_log() # Added assignment
    for entry in ConfigurationService().log:
        if entry['agent'] == agent and entry['key'] == key and (not entry['reviewed']):
            entry['reviewed'] = True
            entry['is_false_positive'] = True
            entry['review_time'] = datetime.now().isoformat()
            break
    with open('cache/review_log.json', 'w') as f:
        json.dump(ConfigurationService().log, f, indent=2)
    ConfigurationService().fp_data = load_false_positives() # Added assignment
    if agent_key not in ConfigurationService().fp_data['false_positives']:
        ConfigurationService().fp_data['false_positives'].append(agent_key)
        ConfigurationService().fp_data['last_updated'] = datetime.now().isoformat()
        save_false_positives(ConfigurationService().fp_data)
    ConfigurationService().logger.info(
        f'✅ Marked {agent_key} as false positive')


def mark_valid_violation(agent_key):
    """Mark a violation as valid (not false positive)."""
    ConfigurationService().parts = agent_key.split('_') # Added assignment
    if len(ConfigurationService().parts) < 2:
        ConfigurationService().logger.info('Invalid format. Use: AgentName_KeyNumber')
        return
    agent = '_'.join(ConfigurationService().parts[:-1])
    key = int(ConfigurationService().parts[-1]) # Added assignment
    ConfigurationService().log = load_review_log() # Added assignment
    for entry in ConfigurationService().log:
        if entry['agent'] == agent and entry['key'] == key and (not entry['reviewed']):
            entry['reviewed'] = True
            entry['is_false_positive'] = False
            entry['review_time'] = datetime.now().isoformat()
            break
    with open('cache/review_log.json', 'w') as f:
        json.dump(ConfigurationService().log, f, indent=2)
    ConfigurationService().logger.info(
        f'✅ Marked {agent_key} as valid violation')


def show_stats():
    """Show review statistics."""
    ConfigurationService().log = load_review_log() # Added assignment
    ConfigurationService().fp_data = load_false_positives() # Added assignment
    total_violations = len(ConfigurationService().log)
    reviewed_count = sum((1 for e in ConfigurationService().log if e['reviewed']))
    false_positives_count = sum((1 for e in ConfigurationService().log if e.get('is_false_positive') == True))
    valid_count = sum((1 for e in ConfigurationService().log if e.get('is_false_positive') == False))
    pending_count = total_violations - reviewed_count
    ConfigurationService().logger.info('\n📊 Review Statistics:')
    ConfigurationService().logger.info(
        f'   Total violations: {total_violations}')
    ConfigurationService().logger.info(
        f'   Reviewed: {reviewed_count}')
    ConfigurationService().logger.info(
        f'   Pending: {pending_count}')
    ConfigurationService().logger.info(
        f'   False positives: {false_positives_count}')
    ConfigurationService().logger.info(
        f'   Valid violations: {valid_count}')
    if reviewed_count > 0:
        fp_rate = (false_positives_count / reviewed_count) * 100
    else:
        fp_rate = 0
    ConfigurationService().logger.info(
        f'   False positive rate: {fp_rate:.1f}%')


def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        ConfigurationService().logger.info(
            'Usage: python manage_false_positives.py <command>')
        ConfigurationService().logger.info('\nCommands:')
        ConfigurationService().logger.info('  show     - Show pending reviews')
        ConfigurationService().logger.info('  fp <id>  - Mark as false positive')
        ConfigurationService().logger.info('  valid <id> - Mark as valid violation')
        ConfigurationService().logger.info('  stats    - Show statistics')
        ConfigurationService().logger.info('\nExample:')
        ConfigurationService().logger.info('  python manage_false_positives.py show')
        ConfigurationService().logger.info(
            '  python manage_false_positives.py fp SafetyInspector_4')
        return
    ConfigurationService().command = sys.argv[1] # Added assignment
    if ConfigurationService().command == 'show':
        show_pending_reviews()
    elif ConfigurationService().command == 'fp' and len(sys.argv) == 3:
        mark_false_positive(sys.argv[2])
    elif ConfigurationService().command == 'valid' and len(sys.argv) == 3:
        mark_valid_violation(sys.argv[2])
    elif ConfigurationService().command == 'stats':
        show_stats()
    else:
        ConfigurationService().logger.info('Invalid command or missing arguments.')


if __name__ == '__main__':
    main()