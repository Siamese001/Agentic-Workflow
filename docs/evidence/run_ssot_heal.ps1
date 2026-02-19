$env:AGENTIC_ALLOW_MUTATION_FOR_TESTS = "1"
$env:AGENTIC_BYPASS_LONGPATHS_CHECK = "1"

$logPath = "docs/evidence/ssot_heal_run_output.txt"

$pyScript = @"
import os, sys, json, traceback

sys.path.insert(0, '.')
os.environ['AGENTIC_ALLOW_MUTATION_FOR_TESTS'] = '1'
os.environ['AGENTIC_BYPASS_LONGPATHS_CHECK'] = '1'

from agentic_core.L0_routing.scripts.execute_ssot import _legacy_main

log_path = 'docs/evidence/ssot_heal_run_output.txt'

with open(log_path, 'w', encoding='utf-8') as log:
    log.write('=== SSOT HEAL MODE RUN ===\n')
    log.write('AGENTIC_ALLOW_MUTATION_FOR_TESTS=1\n')
    log.write('AGENTIC_BYPASS_LONGPATHS_CHECK=1\n')
    log.write('---------------------------\n')

    import logging
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s %(message)s',
                        handlers=[logging.StreamHandler(open(log_path, 'a', encoding='utf-8'))])

    exit_code = 0
    try:
        _legacy_main(['--domains'])
    except SystemExit as e:
        exit_code = e.code or 0
    except Exception:
        exit_code = -1
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write('UNHANDLED EXCEPTION:\n')
            f.write(traceback.format_exc())

    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f'\nEXIT_CODE={exit_code}\n')
        if os.path.exists('runtime_state.json'):
            try:
                data = json.load(open('runtime_state.json', encoding='utf-8'))
                f.write('runtime_state.json: PARSE_OK\n')
                f.write(f'Top-level keys: {list(data.keys())}\n')
            except Exception as e:
                f.write('runtime_state.json: PARSE_FAIL\n')
                f.write(str(e) + '\n')
        else:
            f.write('runtime_state.json: NOT_FOUND\n')

print('DONE')
"@

python -c $pyScript 2>&1 | Tee-Object -FilePath $logPath -Append

Write-Host "--- Tail of $logPath ---"
Get-Content $logPath | Select-Object -Last 20
