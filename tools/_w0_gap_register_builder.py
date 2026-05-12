#!/usr/bin/env python3
"""
W0 Gap Register Builder
Builds the W0_REQ_MATRIX_GAP_REGISTER.md file with detailed inventory.
"""

import os
import re
from collections import defaultdict

def main():
    base_path = r'c:\Git\Agentic-Workflow-FRESH\docs\reference\contracts\step1'
    output_path = os.path.join(base_path, 'W0_REQ_MATRIX_GAP_REGISTER.md')

    # Get all REQ_MATRIX files
    req_matrix_files = [f for f in os.listdir(base_path) if f.endswith('_REQ_MATRIX.md')]
    req_matrix_files.sort()

    # Build gap data
    gap_data = []

    for filename in req_matrix_files:
        filepath = os.path.join(base_path, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')

        file_data = {
            'filename': filename,
            'filepath': filepath,
            'line_count': len(lines),
            'tbd_locations': [],
            'has_incoming_contracts': 'incoming_contracts' in content.lower() or 'incoming contract' in content.lower(),
            'has_outgoing_contracts': 'outgoing_contracts' in content.lower() or 'outgoing contract' in content.lower(),
            'has_l5': 'required_l5_refs' in content.lower() or 'l5' in content.lower(),
            'has_contract_gates': 'required_contract_gates' in content.lower() or 'contract_gate' in content.lower(),
            'has_receipts': 'receipt' in content.lower(),
            'has_otel': 'otel' in content.lower() or 'span' in content.lower(),
            'has_proof': 'proof' in content.lower(),
            'has_00c_refs': bool(re.search(r'00C|G0[1-9]|G1[0-9]|G2[0-9]', content)),
            'table_issues': []
        }

        # Find all TBD locations with context
        for i, line in enumerate(lines, 1):
            matches = re.findall(r'(TBD_\w+)', line)
            for match in matches:
                # Get surrounding context (2 lines before and after)
                start = max(0, i-3)
                end = min(len(lines), i+2)

                file_data['tbd_locations'].append({
                    'line': i,
                    'token': match,
                    'line_content': line.strip(),
                    'context_start': start,
                    'context_end': end
                })

        # Check for table issues
        for i, line in enumerate(lines, 1):
            if '|' in line and '---' in line:
                # Check for 5-column table dividers (should be 4)
                if re.search(r'\|---\+---\+---\+---\+---\|', line):
                    file_data['table_issues'].append({
                        'line': i,
                        'issue': '5-column table divider (should be 4 columns)',
                        'content': line.strip()
                    })

        gap_data.append(file_data)

    # Generate the gap register markdown
    output_lines = []
    output_lines.append('# W0 REQ_MATRIX Gap Register')
    output_lines.append('')
    output_lines.append('Generated: 2026-05-12')
    output_lines.append('Scope: Pre-hardening inventory of all REQ_MATRIX files under docs/reference/contracts/step1/')
    output_lines.append('')

    # Summary section
    output_lines.append('## Summary Counts by File')
    output_lines.append('')
    output_lines.append('| File | Lines | TBD Count | incoming | outgoing | L5 refs | contract gates | receipts | OTEL | proof | 00C refs | Table Issues |')
    output_lines.append('|------|-------|-----------|----------|----------|---------|----------------|----------|------|-------|----------|--------------|')

    for data in gap_data:
        filename_short = data['filename'][:30]
        output_lines.append(f"| {filename_short} | {data['line_count']} | {len(data['tbd_locations'])} | {'Y' if data['has_incoming_contracts'] else 'N'} | {'Y' if data['has_outgoing_contracts'] else 'N'} | {'Y' if data['has_l5'] else 'N'} | {'Y' if data['has_contract_gates'] else 'N'} | {'Y' if data['has_receipts'] else 'N'} | {'Y' if data['has_otel'] else 'N'} | {'Y' if data['has_proof'] else 'N'} | {'Y' if data['has_00c_refs'] else 'N'} | {len(data['table_issues'])} |")

    output_lines.append('')
    total_tbd = sum(len(d['tbd_locations']) for d in gap_data)
    files_with_00c = sum(1 for d in gap_data if d['has_00c_refs'])
    output_lines.append(f"**Total TBD placeholders: {total_tbd}**")
    output_lines.append(f"**Files with 00C/G01-G29 refs: {files_with_00c}**")
    output_lines.append('')

    # Gap details by file
    output_lines.append('---')
    output_lines.append('')
    output_lines.append('## Gap Details by File')
    output_lines.append('')

    for data in gap_data:
        output_lines.append(f"### {data['filename']}")
        output_lines.append('')

        # Missing coverage
        missing = []
        if not data['has_incoming_contracts']:
            missing.append('incoming_contracts')
        if not data['has_outgoing_contracts']:
            missing.append('outgoing_contracts')
        if not data['has_l5']:
            missing.append('required_l5_refs')
        if not data['has_contract_gates']:
            missing.append('required_contract_gates')
        if not data['has_receipts']:
            missing.append('receipts')
        if not data['has_otel']:
            missing.append('OTEL/spans')
        if not data['has_proof']:
            missing.append('proof')

        if missing:
            output_lines.append(f"**Missing coverage: {', '.join(missing)}**")
            output_lines.append('')

        if data['has_00c_refs']:
            output_lines.append('**⚠️ Contains 00C/G01-G29 references — must be migrated to contract gates**')
            output_lines.append('')

        # TBD locations
        if data['tbd_locations']:
            output_lines.append(f"**TBD Placeholders ({len(data['tbd_locations'])} total):**")
            output_lines.append('')

            # Group by token type
            tbd_by_token = defaultdict(list)
            for loc in data['tbd_locations']:
                tbd_by_token[loc['token']].append(loc)

            for token, locations in sorted(tbd_by_token.items()):
                output_lines.append(f"- **{token}** ({len(locations)} occurrences)")
                for loc in locations[:3]:  # Show first 3 of each type
                    content = loc['line_content'][:60]
                    output_lines.append(f"  - Line {loc['line']}: `{content}...`")
                if len(locations) > 3:
                    output_lines.append(f"  - ... and {len(locations) - 3} more")
            output_lines.append('')

        # Table issues
        if data['table_issues']:
            output_lines.append(f"**Table Issues ({len(data['table_issues'])}):**")
            for issue in data['table_issues']:
                output_lines.append(f"- Line {issue['line']}: {issue['issue']}")
                output_lines.append(f"  `{issue['content']}`")
            output_lines.append('')

        # Recommended wave assignment
        output_lines.append('**Recommended Wave Assignment:**')
        if missing:
            output_lines.append("- Contract handoff coverage: W1")
        if not data['has_l5']:
            output_lines.append("- L5 refs coverage: W1")
        if not data['has_contract_gates']:
            output_lines.append("- Contract gate coverage: W1")
        if data['tbd_locations']:
            output_lines.append("- TBD placeholder hardening: W2-W4 (by section)")
        if data['has_00c_refs']:
            output_lines.append("- 00C to contract gate migration: W3")
        if data['table_issues']:
            output_lines.append("- Table format fixes: W5")
        output_lines.append('')
        output_lines.append('---')
        output_lines.append('')

    # Verification commands section
    output_lines.append('## Verification Commands')
    output_lines.append('')
    output_lines.append('```bash')
    output_lines.append('# TBD placeholder count by file')
    output_lines.append('grep -R "TBD_" docs/reference/contracts/step1/ | wc -l')
    output_lines.append('')
    output_lines.append('# 00C/G01-G29 references check')
    output_lines.append("grep -r '00C\\|G01\\|G02\\|G03\\|G04\\|G05\\|G06\\|G07\\|G08\\|G09\\|G10\\|G11\\|G12\\|G13\\|G14\\|G15\\|G16\\|G17\\|G18\\|G19\\|G20\\|G21\\|G22\\|G23\\|G24\\|G25\\|G26\\|G27\\|G28\\|G29' docs/reference/contracts/step1/")
    output_lines.append('```')
    output_lines.append('')

    # Wave assignment summary
    output_lines.append('## Wave Assignment Summary')
    output_lines.append('')
    output_lines.append('| Gap Type | Wave | Files Affected |')
    output_lines.append('|----------|------|----------------|')

    missing_incoming = sum(1 for d in gap_data if not d['has_incoming_contracts'])
    missing_outgoing = sum(1 for d in gap_data if not d['has_outgoing_contracts'])
    missing_l5 = sum(1 for d in gap_data if not d['has_l5'])
    missing_gates = sum(1 for d in gap_data if not d['has_contract_gates'])
    has_tbd = sum(1 for d in gap_data if d['tbd_locations'])
    has_00c = sum(1 for d in gap_data if d['has_00c_refs'])
    has_table_issues = sum(1 for d in gap_data if d['table_issues'])

    output_lines.append(f"| Missing incoming contracts | W1 | {missing_incoming} |")
    output_lines.append(f"| Missing outgoing contracts | W1 | {missing_outgoing} |")
    output_lines.append(f"| Missing L5 refs | W1 | {missing_l5} |")
    output_lines.append(f"| Missing contract gates | W1 | {missing_gates} |")
    output_lines.append(f"| TBD placeholder hardening | W2-W4 | {has_tbd} |")
    output_lines.append(f"| 00C to contract gate migration | W3 | {has_00c} |")
    output_lines.append(f"| Table format issues | W5 | {has_table_issues} |")
    output_lines.append('')

    # Files with highest TBD count
    output_lines.append('## Files with Highest TBD Count')
    output_lines.append('')
    sorted_by_tbd = sorted(gap_data, key=lambda x: -len(x['tbd_locations']))
    for i, data in enumerate(sorted_by_tbd[:5], 1):
        output_lines.append(f"{i}. **{data['filename']}**: {len(data['tbd_locations'])} TBD placeholders")
    output_lines.append('')

    # 00C references detail
    if files_with_00c > 0:
        output_lines.append('## 00C/G01-G29 References Detail')
        output_lines.append('')
        output_lines.append('Files requiring migration to contract gate terminology:')
        output_lines.append('')
        for data in gap_data:
            if data['has_00c_refs']:
                output_lines.append(f"- **{data['filename']}**: Contains legacy 00C runtime gate references")
        output_lines.append('')

    # Write the file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f'W0 gap register created: {output_path}')
    print(f'Total bytes written: {os.path.getsize(output_path)}')

if __name__ == '__main__':
    main()
