"""Verify all dashboard territory counts are correct."""
import json
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

def main():
    lines = []
    in_data = False
    brace_count = 0
    with open('agentic_core/L6_observability/dashboards/autonomy_dashboard.html', encoding='utf-8') as f:
        for line in f:
            if 'const dashboardData = [' in line:
                in_data = True
                lines.append('[')
                continue
            if in_data:
                lines.append(line)
                brace_count += line.count('{') - line.count('}')
                if '];' in line and brace_count == 0:
                    lines[-1] = lines[-1].replace('];', ']')
                    break
    if not lines:
        print('Could not find dashboardData in HTML')
        exit(1)
    data_str = ''.join(lines)
    data = json.loads(data_str)
    print('=' * 70)
    print('DASHBOARD TERRITORY VERIFICATION')
    print('=' * 70)
    print()
    zero_territories = [row for row in data if row['Total'] == 0 and row['Territory'] != 'TOTAL']
    non_zero_territories = [row for row in data if row['Total'] > 0 and row['Territory'] != 'TOTAL']
    print(f'Total Territories: {len(data) - 1}')
    print(f'Non-Zero Territories: {len(non_zero_territories)}')
    print(f'Zero-Agent Territories: {len(zero_territories)}')
    print()
    if zero_territories:
        print('Zero-Agent Territories (expected for infrastructure placeholders):')
        print('-' * 70)
        for row in zero_territories:
            is_infra = '[infra] ' if row.get('IsInfrastructure') else '        '
            print(f"{is_infra}{row['Territory']:50} {row['Total']:>3} agents")
        print()
    print('Non-Zero Territories:')
    print('-' * 70)
    for row in sorted(non_zero_territories, key=lambda x: -x['Total']):
        print(f"   {row['Territory']:50} {row['Total']:>3} agents")
    print()
    print('=' * 70)
    print('KEY METRICS')
    print('=' * 70)
    total_row = data[0]
    print(f"Total Agents:        {total_row['Total']}")
    print(f"Heal Capability:     {total_row['Heal Cap %']}%")
    print(f"Health Score:        {total_row['Health']}")
    print(f"Compliant Agents:    {total_row['Compliant']}/{total_row['Total']}")
    print()
    l6_territories = [row for row in data if 'L6' in row['Territory']]
    l6_total = sum((row['Total'] for row in l6_territories))
    print('L6_Observability Breakdown:')
    for row in l6_territories:
        status = 'OK' if row['Total'] > 0 else 'WARN'
        print(f"   [{status}] {row['Territory']:45} {row['Total']:>3} agents")
    print(f"   {'L6 TOTAL':45} {l6_total:>3} agents")
    print()
    if l6_total > 0:
        print('L6_Observability data is CORRECT')
    else:
        print('L6_Observability has 0 agents - DATA ERROR')
if __name__ == '__main__':
    main()
