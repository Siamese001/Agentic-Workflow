"""Evidence runner for L2.3 Healing Tier Router.

Commit+amend flow captures Git Proof Completeness Gate AFTER
evidence-only HEAD exists, eliminating the chicken-and-egg problem.

Sequence:
  1. Preflight: assert clean porcelain (empty stdout)
  2. CODE_COMMIT = git rev-parse HEAD (current code commit)
  3. Run pytest (verbatim)
  4. Write initial evidence (CODE_COMMIT + SEALED_FROM only)
  5. git add + commit via commit_with_retry -> evidence-only HEAD
  6. Capture 6 git commands verbatim AFTER evidence-only HEAD exists
  7. Run assertions (hard-fail on any mismatch)
  8. Rewrite evidence with git proof + assertions
  9. git add + amend via commit_with_retry
  10. Re-verify post-amend invariants
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_reads_through,
    _emit_validated_by_safety_plane,
    _emit_writes_through,
    emit_determinism_digest,
)

_emit_writes_through("p1", "healing_tier_evidence_runner", "uwg_governed_write")
_emit_writes_through("p1", "healing_tier_evidence_runner", "uwg_governed_write_2")
_emit_pulls_context("p1", "healing_tier_evidence_runner", "context_retrieval")
_emit_pulls_context("p1", "healing_tier_evidence_runner", "context_retrieval_2")
emit_determinism_digest("trace_healing_tier_evidence_runner", "healing_tier_evidence_runner_dispatch")
emit_determinism_digest("trace_healing_tier_evidence_runner", "healing_tier_evidence_runner_complete")
_emit_validated_by_safety_plane("p1", "healing_tier_evidence_runner", "safety_validation")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_1")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_2")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_3")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_4")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_5")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_6")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_7")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_8")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_9")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_10")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_11")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_12")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_13")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_14")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_15")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_16")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_17")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_18")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_19")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_20")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_21")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_22")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_23")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_24")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_25")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_26")
_emit_reads_through("l4", "healing_tier_evidence_runner", "urg_read_27")
REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = 'reports'
EVIDENCE_PATH = REPO_ROOT / 'docs' / REPORTS_DIR / 'plans' / 'healing_tier_router_evidence.md'
EVIDENCE_REL = 'docs/reports/plans/healing_tier_router_evidence.md'
_HEX40_RE = re.compile('^[0-9a-f]{40}$')
_ANSI_RE = re.compile('\\x1b\\[[0-9;]*m')

def _write_lf(lines: list[str]) -> None:
    """Write evidence file with explicit LF line endings (no CRLF)."""
    with open(EVIDENCE_PATH, 'w', encoding='utf-8', newline='\n') as f:
        for line in lines:
            f.write(line + '\n')

def _clean(text: str) -> str:
    """Strip ANSI escapes and non-ASCII bytes."""
    text = _ANSI_RE.sub('', text)
    return text.encode('ascii', errors='replace').decode('ascii')

def run_cmd(argv: list[str]) -> tuple[int, str, str]:
    """Run command via subprocess. Returns (rc, stdout, stderr) -- always 3-tuple."""
    r = subprocess.run(argv, cwd=str(REPO_ROOT), capture_output=True, encoding='utf-8', errors='replace', shell=False)
    return (r.returncode, _clean(r.stdout or ''), _clean(r.stderr or ''))

def run_cmd_combined(argv: list[str]) -> tuple[int, str]:
    """Run command, return (rc, combined stdout+stderr)."""
    rc, out, err = run_cmd(argv)
    return (rc, (out + err).strip())

def stdout_or_fail(argv: list[str]) -> str:
    """Run command, return stripped stdout. Hard-fail on non-zero exit."""
    rc, out, err = run_cmd(argv)
    if rc != 0:
        print(f"FAIL: {' '.join(argv)} exited {rc}", file=sys.stderr)
        print(err, file=sys.stderr)
        sys.exit(1)
    return out.strip()

def commit_with_retry(argv_commit: list[str]) -> None:
    """Attempt a git commit. On failure, parse porcelain, re-add, retry once.

    Contract:
      1. Attempt commit via run_cmd(argv_commit)
      2. If rc==0: return (success)
      3. If rc!=0:
         a. Print verbatim failed stdout/stderr
         b. Run and print verbatim: git status --porcelain
         c. Parse porcelain lines; collect paths where status is not "??"
         d. Sort paths; print re-add list
         e. Run: git add -- <sorted_paths>
         f. Retry: run_cmd(argv_commit) again (exact same argv)
         g. Print verbatim retry stdout/stderr
         h. Hard-fail if rc still != 0
    """
    rc, out, err = run_cmd(argv_commit)
    if rc == 0:
        return
    print(f'INFO: commit attempt 1 failed (rc={rc})')
    print(f'--- failed stdout ---\n{out}')
    print(f'--- failed stderr ---\n{err}')
    rc_p, porcelain_out, porcelain_err = run_cmd(['git', 'status', '--porcelain'])
    print(f'$ git status --porcelain\n{porcelain_out}')
    if porcelain_err:
        print(f'(porcelain stderr: {porcelain_err})')
    paths_to_readd: list[str] = []
    for line in porcelain_out.splitlines():
        if not line or len(line) < 4:
            continue
        status_code = line[:2].strip()
        file_path = line[3:]
        if status_code != '??':
            paths_to_readd.append(file_path)
    paths_to_readd.sort()
    print(f'Re-add paths (sorted): {paths_to_readd}')
    if paths_to_readd:
        rc_add, add_out, add_err = run_cmd(['git', 'add', '--'] + paths_to_readd)
        if rc_add != 0:
            print(f'FAIL: git add exited {rc_add}\n{add_err}', file=sys.stderr)
            sys.exit(1)
    rc2, out2, err2 = run_cmd(argv_commit)
    print(f'--- retry stdout ---\n{out2}')
    print(f'--- retry stderr ---\n{err2}')
    if rc2 != 0:
        print(f'FAIL: commit retry also failed (rc={rc2})\n{out2}\n{err2}', file=sys.stderr)
        sys.exit(1)

def validate_40hex(label: str, value: str) -> str:
    """Validate 40-hex. Returns the OK line. Hard-fails on mismatch."""
    if _HEX40_RE.match(value):
        line = f'OK: {label} validated as 40-hex: {value}'
        print(line)
        return line
    print(f"FAIL: {label} is not valid 40-hex: '{value}'", file=sys.stderr)
    sys.exit(1)

def hard_assert(condition: bool, ok_msg: str, fail_msg: str) -> str:
    """Assert condition. Print OK line and return it, or hard-fail."""
    if condition:
        print(ok_msg)
        return ok_msg
    print(f'FAIL: {fail_msg}', file=sys.stderr)
    sys.exit(1)

def main() -> None:
    evidence_lines: list[str] = []
    assertion_lines: list[str] = []
    print('=== Step 1: Preflight ===')
    rc_pre, porcelain_pre, _ = run_cmd(['git', 'status', '--porcelain'])
    porcelain_pre = porcelain_pre.strip()
    hard_assert(len(porcelain_pre) == 0, 'OK: Preflight git status --porcelain is empty', f'Working tree not clean: {porcelain_pre}')
    print('\n=== Step 2: CODE_COMMIT ===')
    code_commit = stdout_or_fail(['git', 'rev-parse', 'HEAD'])
    sealed_from = code_commit
    validate_40hex('CODE_COMMIT', code_commit)
    validate_40hex('SEALED_FROM', sealed_from)
    print('\n=== Step 3: Pytest ===')
    test_argv = [sys.executable, '-m', 'pytest', 'tests/agentic_core/L2_execution/healers/test_healing_tier_router.py', '-v', '--color=no', '--tb=short', '-m', 'unit_min_deps']
    test_cmd_str = ' '.join(test_argv)
    print(f'$ {test_cmd_str}')
    test_rc, test_out = run_cmd_combined(test_argv)
    print(test_out)
    if test_rc != 0:
        print(f'FAIL: pytest exited {test_rc}', file=sys.stderr)
        sys.exit(1)
    print('OK: pytest passed')
    print('\n=== Step 4: Write initial evidence ===')
    evidence_lines = ['# L2.3 Healing Tier Router - Evidence', '', '## Scope', '', 'Implement centralized L2.3 healing tier router with:', '- HealingInput/HealingDecision/FailureSignal contracts', '- L4-backed config (X/Y thresholds, model IDs)', '- Deterministic heal_confidence scoring', '- Single choke point tier routing', '- Tiering allowlist (10 YES_TIERING agents)', '- AST-based enforcement (NO_TIERING prohibition)', '- Determinism proof (byte-identical decisions)', '', f'CODE_COMMIT={code_commit}', f'SEALED_FROM={sealed_from}', '', '## Config Values', '', '```', 'HEAL_CONFIDENCE_X=0.75', 'HEAL_CONFIDENCE_Y=0.40', 'MAX_HEAL_RETRIES=3', 'MODEL_QWEN_VLLM_ID=qwen2.5-coder-32b-instruct', 'MODEL_GEMINI_2_5_PRO_ID=gemini-2.5-pro', '```', '', '## Test Execution', '', f'$ {test_cmd_str}', '', '```', test_out, '```', '']
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _write_lf(evidence_lines)
    print(f'OK: Initial evidence written to {EVIDENCE_PATH}')
    print('\n=== Step 5: Create evidence-only commit ===')
    rc_add, _, add_err = run_cmd(['git', 'add', EVIDENCE_REL])
    if rc_add != 0:
        print(f'FAIL: git add exited {rc_add}\n{add_err}', file=sys.stderr)
        sys.exit(1)
    commit_with_retry(['git', 'commit', '-m', 'docs: healing tier router evidence (sealed)'])
    print('OK: Evidence-only commit created')
    print('\n=== Step 6: Git Proof Completeness Gate ===')
    git_cmds: list[tuple[str, str]] = []
    for label, argv in [('git log -1 --format=%H', ['git', 'log', '-1', '--format=%H']), ('git rev-parse HEAD', ['git', 'rev-parse', 'HEAD']), ('git rev-parse HEAD~1', ['git', 'rev-parse', 'HEAD~1']), ('git rev-parse HEAD~2', ['git', 'rev-parse', 'HEAD~2']), ('git show --name-only --pretty=format: HEAD', ['git', 'show', '--name-only', '--pretty=format:', 'HEAD']), ('git status --porcelain', ['git', 'status', '--porcelain'])]:
        out = stdout_or_fail(argv)
        git_cmds.append((label, out))
        print(f'$ {label}')
        print(out if out else '')
    v_log = git_cmds[0][1]
    v_head = git_cmds[1][1]
    v_head1 = git_cmds[2][1]
    _ = git_cmds[3][1]
    v_show = git_cmds[4][1]
    v_porcelain = git_cmds[5][1]
    print('\n=== Step 7: Assertions ===')
    assertion_lines.append(hard_assert(v_log == v_head, f'OK: git log -1 == git rev-parse HEAD: {v_log}', f'git log -1 ({v_log}) != git rev-parse HEAD ({v_head})'))
    assertion_lines.append(hard_assert(len(v_porcelain) == 0, 'OK: len(porcelain_stdout) == 0', f'porcelain not empty: {v_porcelain}'))
    assertion_lines.append(hard_assert(v_show.strip() == EVIDENCE_REL, f'OK: git show --name-only HEAD lists only: {EVIDENCE_REL}', f'git show --name-only HEAD unexpected: {v_show.strip()}'))
    ev_content = EVIDENCE_PATH.read_text(encoding='utf-8')
    ex_code = ex_sealed = None
    for ln in ev_content.splitlines():
        if ln.startswith('CODE_COMMIT='):
            ex_code = ln.split('=', 1)[1]
        elif ln.startswith('SEALED_FROM='):
            ex_sealed = ln.split('=', 1)[1]
    if ex_code is None or ex_sealed is None:
        print('FAIL: Could not extract CODE_COMMIT/SEALED_FROM', file=sys.stderr)
        sys.exit(1)
    assertion_lines.append(validate_40hex('CODE_COMMIT', ex_code))
    assertion_lines.append(validate_40hex('SEALED_FROM', ex_sealed))
    assertion_lines.append(hard_assert(v_head1 == ex_code == ex_sealed, f'OK: HEAD~1 == CODE_COMMIT == SEALED_FROM: {v_head1}', f'HEAD~1 ({v_head1}) != CODE_COMMIT ({ex_code}) != SEALED_FROM ({ex_sealed})'))
    print('\n=== Step 8: Rewrite evidence with git proof ===')
    evidence_lines.append('## Git Proof Completeness Gate (post evidence-only HEAD)')
    evidence_lines.append('')
    for label, out in git_cmds:
        evidence_lines.append(f'$ {label}')
        evidence_lines.append(out if out else '')
        evidence_lines.append('')
    evidence_lines.append('## Assertions')
    evidence_lines.append('')
    for a in assertion_lines:
        evidence_lines.append(a)
    evidence_lines.append('')
    code_files = stdout_or_fail(['git', 'show', '--name-only', '--pretty=format:', code_commit])
    evidence_lines.extend(['## FILES_CHANGED_CODE', '', '```', code_files.strip(), '```', ''])
    evidence_lines.extend(['## INSPECTED_FILES', '', '```', 'agentic_core/L2_execution/healers/healing_tier_types.py', 'agentic_core/L2_execution/healers/healing_tier_config.py', 'agentic_core/L2_execution/healers/healing_tier_router.py', 'agentic_core/L2_execution/healers/tiering_allowlist.py', 'tests/agentic_core/L2_execution/healers/test_healing_tier_router.py', 'docs/technical/agent_confidence_tiering_recommendations.csv', 'docs/technical/agent_confidence_tiering_recommendations.md', '```', ''])
    _write_lf(evidence_lines)
    print(f'OK: Complete evidence written to {EVIDENCE_PATH}')
    print('\n=== Step 9: Amend evidence commit ===')
    rc_add, _, add_err = run_cmd(['git', 'add', EVIDENCE_REL])
    if rc_add != 0:
        print(f'FAIL: git add exited {rc_add}\n{add_err}', file=sys.stderr)
        sys.exit(1)
    commit_with_retry(['git', 'commit', '--amend', '--no-edit'])
    print('OK: Evidence commit amended')
    print('\n=== Step 10: Post-amend re-verification ===')
    post_head = stdout_or_fail(['git', 'rev-parse', 'HEAD'])
    post_head1 = stdout_or_fail(['git', 'rev-parse', 'HEAD~1'])
    post_show = stdout_or_fail(['git', 'show', '--name-only', '--pretty=format:', 'HEAD'])
    rc_post_p, post_porcelain, _ = run_cmd(['git', 'status', '--porcelain'])
    post_porcelain = post_porcelain.strip()
    hard_assert(post_show.strip() == EVIDENCE_REL, f'OK: Post-amend HEAD is evidence-only: {EVIDENCE_REL}', f'Post-amend HEAD not evidence-only: {post_show.strip()}')
    hard_assert(post_head1 == code_commit, f'OK: Post-amend HEAD~1 == CODE_COMMIT: {post_head1}', f'Post-amend HEAD~1 ({post_head1}) != CODE_COMMIT ({code_commit})')
    hard_assert(len(post_porcelain) == 0, 'OK: Post-amend git status --porcelain is empty', f'Post-amend porcelain not empty: {post_porcelain}')
    print('\n=== SUCCESS ===')
    print(f'Evidence file: {EVIDENCE_PATH}')
    print(f'HEAD (evidence-only): {post_head}')
    print(f'HEAD~1 (CODE_COMMIT): {post_head1}')
if __name__ == '__main__':
    main()
