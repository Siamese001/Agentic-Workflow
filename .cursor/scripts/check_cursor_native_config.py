#!/usr/bin/env python3
from __future__ import annotations
import argparse, fnmatch, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
TEXT_EXTS = {'.md', '.mdc', '.txt', '.json', '.py', '.js', '.ps1', '.yaml', '.yml', '.toml', '.ini', '.sql', '.marker'}
DEFAULT_LEGACY_TOKENS = ['Cursor Agent', 'Cursor', 'Cursor', '.cursor', 'post_cursor_agent', 'pre_cursor_agent', 'mcp.json']
CURSOR_HOOK_EVENTS = {'beforeSubmitPrompt', 'beforeShellExecution', 'beforeMCPExecution', 'beforeReadFile', 'afterFileEdit', 'stop'}
LEGACY_HOOK_EVENTS = {'pre_read_code','pre_run_command','pre_write_code','post_write_code','post_run_command','post_cursor_agent_response','pre_user_prompt','pre_mcp_tool_use','post_mcp_tool_use'}


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT)).replace('\\','/')


def load_allowlist() -> dict:
    path = ROOT / 'migration_allowlist.json'
    if not path.exists():
        return {'allowed_legacy_paths': [], 'legacy_tokens': DEFAULT_LEGACY_TOKENS}
    return json.loads(path.read_text(encoding='utf-8'))


def is_allowed(path: Path, patterns: list[str]) -> bool:
    r = rel(path)
    return any(fnmatch.fnmatch(r, pat) for pat in patterns)


def read_text(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_EXTS:
        return None
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return None


def parse_frontmatter(text: str):
    if not text.startswith('---'):
        return None
    end = text.find('\n---', 3)
    if end == -1:
        return None
    return text[3:end].strip()


def check():
    allow = load_allowlist()
    allowed_paths = allow.get('allowed_legacy_paths', [])
    legacy_tokens = allow.get('legacy_tokens', DEFAULT_LEGACY_TOKENS)
    failures = []
    warnings = []

    # Active legacy token scan.
    for path in ROOT.rglob('*'):
        if not path.is_file() or is_allowed(path, allowed_paths):
            continue
        text = read_text(path)
        if text is None:
            continue
        hits = [tok for tok in legacy_tokens if tok in text]
        name_hits = [tok for tok in legacy_tokens if tok in path.name]
        if hits or name_hits:
            failures.append({'type': 'active_legacy_reference', 'path': rel(path), 'tokens': sorted(set(hits + name_hits))})

    # hooks.json.
    hooks_path = ROOT / 'hooks.json'
    if not hooks_path.exists():
        failures.append({'type': 'missing_hooks_json', 'path': rel(hooks_path)})
    else:
        try:
            hooks = json.loads(hooks_path.read_text(encoding='utf-8'))
            if hooks.get('version') != 1:
                failures.append({'type': 'hooks_version_not_1', 'path': rel(hooks_path), 'value': hooks.get('version')})
            events = set((hooks.get('hooks') or {}).keys())
            bad_events = sorted(events - CURSOR_HOOK_EVENTS)
            legacy_events = sorted(events & LEGACY_HOOK_EVENTS)
            missing = sorted(CURSOR_HOOK_EVENTS - events)
            if bad_events or legacy_events:
                failures.append({'type': 'non_cursor_hook_events', 'path': rel(hooks_path), 'bad_events': bad_events, 'legacy_events': legacy_events})
            if missing:
                warnings.append({'type': 'missing_recommended_cursor_hook_events', 'path': rel(hooks_path), 'missing': missing})
            for event, entries in (hooks.get('hooks') or {}).items():
                for idx, entry in enumerate(entries or []):
                    cmd = str(entry.get('command',''))
                    if '.windsurf' in cmd or 'post_cascade' in cmd or 'pre_cascade' in cmd:
                        failures.append({'type': 'legacy_hook_command', 'event': event, 'index': idx, 'command': cmd})
        except Exception as exc:
            failures.append({'type': 'invalid_hooks_json', 'path': rel(hooks_path), 'error': str(exc)})

    # mcp.json.
    mcp_path = ROOT / 'mcp.json'
    if not mcp_path.exists():
        failures.append({'type': 'missing_mcp_json', 'path': rel(mcp_path)})
    else:
        try:
            mcp = json.loads(mcp_path.read_text(encoding='utf-8'))
            if not isinstance(mcp.get('mcpServers'), dict):
                failures.append({'type': 'missing_mcpServers_root', 'path': rel(mcp_path)})
        except Exception as exc:
            failures.append({'type': 'invalid_mcp_json', 'path': rel(mcp_path), 'error': str(exc)})

    # MDC frontmatter and legacy globs.
    for path in (ROOT / 'rules').glob('*.mdc') if (ROOT / 'rules').exists() else []:
        text = path.read_text(encoding='utf-8')
        fm = parse_frontmatter(text)
        if fm is None:
            failures.append({'type': 'mdc_missing_frontmatter', 'path': rel(path)})
            continue
        if 'description:' not in fm:
            failures.append({'type': 'mdc_missing_description', 'path': rel(path)})
        if 'alwaysApply:' not in fm:
            failures.append({'type': 'mdc_missing_alwaysApply', 'path': rel(path)})
        if '.windsurf' in fm or 'mcp_config.json' in fm:
            failures.append({'type': 'mdc_legacy_frontmatter', 'path': rel(path)})

    # Skill frontmatter.
    for path in (ROOT / 'skills').glob('*/SKILL.md') if (ROOT / 'skills').exists() else []:
        text = path.read_text(encoding='utf-8')
        fm = parse_frontmatter(text)
        if fm is None:
            failures.append({'type': 'skill_missing_frontmatter', 'path': rel(path)})
            continue
        if 'description:' not in fm:
            failures.append({'type': 'skill_missing_description', 'path': rel(path)})

    # Agent presence.
    agents_dir = ROOT / 'agents'
    required_agents = {'boundary-auditor.md', 'hook-migration-auditor.md', 'mcp-governance-auditor.md', 'receipt-verifier.md'}
    present_agents = {p.name for p in agents_dir.glob('*.md')} if agents_dir.exists() else set()
    missing_agents = sorted(required_agents - present_agents)
    if missing_agents:
        failures.append({'type': 'missing_required_agents', 'missing': missing_agents})

    result = {
        'status': 'FAIL' if failures else 'PASS',
        'failures': failures,
        'warnings': warnings,
        'active_root': rel(ROOT),
    }
    print(json.dumps(result, indent=2))
    return 1 if failures else 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()
    raise SystemExit(check())
