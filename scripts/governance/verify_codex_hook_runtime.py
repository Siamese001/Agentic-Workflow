"""Verify Codex hook configuration and optional local-runtime registration.

The repository check validates the documented Codex hook schema. A local runtime
check additionally proves that the user profile has hooks enabled and has a saved
trust-state entry for every currently registered repository command. Registration
does not prove that every specialized tool path will dispatch a hook.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS_RELATIVE = Path(".codex/hooks.json")
CONFIG_RELATIVE = Path(".codex/config.toml")
SUPPORTED_EVENTS = frozenset(
    {
        "PreToolUse",
        "PermissionRequest",
        "PostToolUse",
        "PreCompact",
        "PostCompact",
        "UserPromptSubmit",
        "SubagentStop",
        "Stop",
        "SessionStart",
        "SubagentStart",
        "SessionEnd",
    }
)
REQUIRED_AVATAR_ID = "patch-fox"


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        value = tomllib.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected TOML object: {path}")
    return value


def _event_state_name(event: str) -> str:
    return re.sub(r"(?<!^)([A-Z])", r"_\1", event).lower()


def _valid_matcher(value: object) -> bool:
    if not isinstance(value, str):
        return False
    if value in {"", "*"}:
        return True
    try:
        re.compile(value)
    except re.error:
        return False
    return True


def validate_contract(root: Path = REPO_ROOT) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    try:
        config = _read_toml(root / CONFIG_RELATIVE)
        hooks_document = _read_json(root / HOOKS_RELATIVE)
    except (OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
        return {"status": "FAIL", "errors": [str(exc)], "registered_commands": []}

    features = config.get("features")
    if not isinstance(features, Mapping) or features.get("hooks") is not True:
        errors.append(".codex/config.toml must set [features].hooks = true")
    if isinstance(features, Mapping) and "codex_hooks" in features:
        errors.append(".codex/config.toml uses deprecated [features].codex_hooks; use hooks")

    hooks = hooks_document.get("hooks")
    if not isinstance(hooks, Mapping):
        return {"status": "FAIL", "errors": [*errors, "hooks.json hooks must be an object"], "registered_commands": []}

    registered_commands: list[dict[str, Any]] = []
    for event, groups in hooks.items():
        if event not in SUPPORTED_EVENTS:
            errors.append(f"unsupported hook event: {event}")
        if not isinstance(groups, list):
            errors.append(f"{event} groups must be an array")
            continue
        for group_index, group in enumerate(groups):
            if not isinstance(group, Mapping):
                errors.append(f"{event}[{group_index}] must be an object")
                continue
            matcher = group.get("matcher", "")
            if not _valid_matcher(matcher):
                errors.append(f"{event}[{group_index}] has invalid matcher: {matcher!r}")
            handlers = group.get("hooks")
            if not isinstance(handlers, list) or not handlers:
                errors.append(f"{event}[{group_index}] needs at least one command hook")
                continue
            for handler_index, handler in enumerate(handlers):
                if not isinstance(handler, Mapping):
                    errors.append(f"{event}[{group_index}].hooks[{handler_index}] must be an object")
                    continue
                if handler.get("type") != "command":
                    errors.append(f"{event}[{group_index}].hooks[{handler_index}] must use type=command")
                command = handler.get("command")
                if not isinstance(command, str) or not command.strip():
                    errors.append(f"{event}[{group_index}].hooks[{handler_index}] needs a command")
                    continue
                registered_commands.append(
                    {
                        "event": event,
                        "event_state": _event_state_name(event),
                        "group_index": group_index,
                        "handler_index": handler_index,
                        "matcher": matcher,
                        "command": command,
                    }
                )

    return {
        "status": "FAIL" if errors else "PASS",
        "errors": errors,
        "registered_commands": registered_commands,
    }


def validate_runtime_registration(root: Path, runtime_config: Path) -> dict[str, Any]:
    contract = validate_contract(root)
    errors = list(contract["errors"])
    warnings: list[str] = []
    try:
        runtime = _read_toml(runtime_config)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        return {**contract, "status": "FAIL", "errors": [*errors, str(exc)], "warnings": warnings}

    features = runtime.get("features")
    if not isinstance(features, Mapping):
        errors.append(f"{runtime_config}: missing [features] table")
    elif features.get("hooks") is not True:
        if features.get("codex_hooks") is True:
            warnings.append(f"{runtime_config}: deprecated codex_hooks alias is active; migrate to hooks")
        else:
            errors.append(f"{runtime_config}: [features].hooks is not enabled")

    selected_avatar = runtime.get("selected-avatar-id")
    if selected_avatar != REQUIRED_AVATAR_ID:
        errors.append(
            f"{runtime_config}: selected-avatar-id must be {REQUIRED_AVATAR_ID!r} "
            "for the registered selected_avatar_guard"
        )

    state = runtime.get("hooks", {})
    state = state.get("state", {}) if isinstance(state, Mapping) else {}
    if not isinstance(state, Mapping):
        errors.append(f"{runtime_config}: [hooks.state] must be a table")
    else:
        state_keys = {str(key).replace("\\", "/") for key in state}
        for command in contract["registered_commands"]:
            suffix = (
                f"{HOOKS_RELATIVE.as_posix()}:{command['event_state']}:"
                f"{command['group_index']}:{command['handler_index']}"
            )
            if not any(key.endswith(suffix) for key in state_keys):
                errors.append(f"runtime trust state missing: {suffix}")

    return {
        **contract,
        "status": "FAIL" if errors else "PASS",
        "errors": errors,
        "warnings": warnings,
        "runtime_config": str(runtime_config),
        "selected_avatar_id": selected_avatar,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root to validate")
    parser.add_argument("--runtime-config", type=Path, help="User Codex config.toml for local registration proof")
    parser.add_argument("--json", action="store_true", help="Emit the complete validation report as JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = (
        validate_runtime_registration(args.root, args.runtime_config)
        if args.runtime_config
        else validate_contract(args.root)
    )
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"codex-hook-runtime: {result['status']}")
        print(f"- registered command hooks: {len(result['registered_commands'])}")
        for warning in result.get("warnings", []):
            print(f"- WARN: {warning}")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
