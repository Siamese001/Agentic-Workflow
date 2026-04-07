"""
analyze_agent_count_waterfall.py - Trace agent count changes through git history

Produces a detailed waterfall showing how agent count changed over time.
"""
import json
import subprocess
import sys
from collections import defaultdict


def get_agent_count_at_commit(commit_hash):
    """Get agent count from agent_discovery_full.json at a specific commit."""
    try:
        result = subprocess.run(['git', 'show', f'{commit_hash}:agent_discovery_full.json'], capture_output=True, text=True, cwd='C:/Git/Agentic-Workflow')
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return len(data) if isinstance(data, list) else len(data.get('agents', []))
    # guardian: allow-silent-swallow
    except:
        pass
    return None

def get_commit_history():
    """Get all commits that touched agent_discovery_full.json."""
    result = subprocess.run(['git', 'log', '--oneline', '--format=%h|%ad|%s', '--date=short', '--', 'agent_discovery_full.json'], capture_output=True, text=True, cwd='C:/Git/Agentic-Workflow')
    commits = []
    for line in result.stdout.strip().split('\n'):
        if '|' in line:
            parts = line.split('|', 2)
            if len(parts) == 3:
                commits.append({'hash': parts[0], 'date': parts[1], 'message': parts[2][:80]})
    return commits

def main():
    print('=' * 80)
    print('AGENT COUNT WATERFALL ANALYSIS')
    print('=' * 80)
    commits = get_commit_history()
    print(f'\nFound {len(commits)} commits touching agent_discovery_full.json\n')
    waterfall = []
    prev_count = None
    for i, commit in enumerate(reversed(commits)):
        count = get_agent_count_at_commit(commit['hash'])
        if count is not None:
            delta = 0 if prev_count is None else count - prev_count
            waterfall.append({**commit, 'count': count, 'delta': delta})
            prev_count = count
        if (i + 1) % 20 == 0:
            print(f'  Processed {i + 1}/{len(commits)} commits...')
    print('\n' + '=' * 80)
    print('SIGNIFICANT CHANGES (|delta| >= 10)')
    print('=' * 80)
    print(f"{'Date':<12} {'Count':>6} {'Delta':>7}  {'Commit':<10} Message")
    print('-' * 80)
    for entry in waterfall:
        if abs(entry['delta']) >= 10:
            delta_str = f"+{entry['delta']}" if entry['delta'] > 0 else str(entry['delta'])
            print(f"{entry['date']:<12} {entry['count']:>6} {delta_str:>7}  {entry['hash']:<10} {entry['message']}")
    print('\n' + '=' * 80)
    print('DAILY WATERFALL SUMMARY')
    print('=' * 80)
    daily = defaultdict(list)
    for entry in waterfall:
        daily[entry['date']].append(entry)
    print(f"{'Date':<12} {'Start':>6} {'End':>6} {'Net':>7}  Key Events")
    print('-' * 80)
    for date in sorted(daily.keys()):
        entries = daily[date]
        start_count = entries[0]['count'] - entries[0]['delta']
        end_count = entries[-1]['count']
        net = end_count - start_count
        net_str = f'+{net}' if net > 0 else str(net)
        max_delta_entry = max(entries, key=lambda x: abs(x['delta']))
        key_event = max_delta_entry['message'][:40] if abs(max_delta_entry['delta']) >= 5 else ''
        print(f'{date:<12} {start_count:>6} {end_count:>6} {net_str:>7}  {key_event}')
    print('\n' + '=' * 80)
    print('WATERFALL SUMMARY')
    print('=' * 80)
    if waterfall:
        first = waterfall[0]
        last = waterfall[-1]
        print(f"First recorded count: {first['count']} agents ({first['date']})")
        print(f"Current count:        {last['count']} agents ({last['date']})")
        print(f"Total change:         {last['count'] - first['count']} agents")
        peak = max(waterfall, key=lambda x: x['count'])
        print(f"\nPeak count:           {peak['count']} agents ({peak['date']})")
        print(f"  Commit: {peak['hash']} - {peak['message']}")
        print('\n' + '-' * 80)
        print('MAJOR REDUCTION EVENTS (delta <= -20)')
        print('-' * 80)
        for entry in waterfall:
            if entry['delta'] <= -20:
                print(f"  {entry['date']} | {entry['delta']:>4} | {entry['hash']} | {entry['message']}")
    return 0
if __name__ == '__main__':
    sys.exit(main())
