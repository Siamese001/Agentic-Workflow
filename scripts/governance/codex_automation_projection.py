r"""Project repo-owned Codex automation contracts into Codex Desktop launchers.

The versioned source of truth stays under ``.codex/automations``. This helper
builds generated, digest-bound launcher mirrors under the Codex user profile so
the desktop UI can display and run approved schedules without becoming a second
policy registry. The launcher carries UI/execution fields copied from the repo
contract plus source metadata; validation rejects stale or hand-edited mirrors.
"""

from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path
from typing import Any

import verify_codex_enforcement_home as enforcement_home


def _toml_value(value: Any) -> str:
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    raise TypeError(f"Unsupported TOML value: {value!r}")


def _projection_toml(projection: dict[str, Any], existing: dict[str, Any] | None = None) -> str:
    now_ms = int(time.time() * 1000)
    created_at = existing.get("created_at") if isinstance(existing, dict) else None
    if not isinstance(created_at, int):
        created_at = now_ms
    lines = [
        "version = 1",
        f"schema = {_toml_value(projection['schema'])}",
        f"projection_kind = {_toml_value(projection['projection_kind'])}",
        f"automation_id = {_toml_value(projection['automation_id'])}",
        f"enabled = {_toml_value(projection['enabled'])}",
        f"repo_root = {_toml_value(projection['repo_root'])}",
        f"contract_path = {_toml_value(projection['contract_path'])}",
        f"contract_sha256 = {_toml_value(projection['contract_sha256'])}",
        f"id = {_toml_value(projection['id'])}",
        f"kind = {_toml_value(projection['kind'])}",
        f"name = {_toml_value(projection.get('name') or projection['id'])}",
        f"prompt = {_toml_value(projection['prompt'])}",
        f"status = {_toml_value(projection['status'])}",
        f"rrule = {_toml_value(projection['rrule'])}",
        f"model = {_toml_value(projection['model'])}",
        f"reasoning_effort = {_toml_value(projection['reasoning_effort'])}",
        f"execution_environment = {_toml_value(projection['execution_environment'])}",
        f"cwds = {_toml_value(projection['cwds'])}",
        f"created_at = {created_at}",
        f"updated_at = {now_ms}",
        "",
    ]
    return "\n".join(lines)


def _read_existing_toml(path: Path) -> dict[str, Any] | None:
    data, error = enforcement_home._load_toml(path)  # noqa: SLF001 - same governance package.
    if error is not None:
        return None
    return data


def write_user_profile_projections(*, root: Path, user_codex_home: Path) -> list[str]:
    written: list[str] = []
    for projection in enforcement_home.iter_user_profile_projections(root):
        automation_id = projection["id"]
        path = user_codex_home / "automations" / automation_id / "automation.toml"
        existing = _read_existing_toml(path)
        text = _projection_toml(projection, existing)
        if path.exists() and path.read_text(encoding="utf-8") == text:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        written.append(str(path))
    return written


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _unique_disabled_destination(disabled_root: Path, automation_dir: Path) -> Path:
    timestamp = time.strftime("%Y%m%d%H%M%S")
    base_name = f"{automation_dir.name}-{timestamp}"
    destination = disabled_root / base_name
    counter = 2
    while destination.exists():
        destination = disabled_root / f"{base_name}-{counter}"
        counter += 1
    return destination


def disable_stale_user_profile_launchers(*, root: Path, user_codex_home: Path) -> list[dict[str, str]]:
    """Move stale repo-specific profile launchers to a disabled holding directory."""
    root = root.resolve()
    user_codex_home = user_codex_home.resolve()
    automations_root = (user_codex_home / "automations").resolve()
    disabled_root = user_codex_home / "automations-disabled"
    moved: list[dict[str, str]] = []
    for artifact in enforcement_home._user_profile_automation_artifacts(user_codex_home, root):  # noqa: SLF001
        candidate = artifact.parent if artifact.name == "automation.toml" else artifact
        automation_dir = candidate.resolve()
        if automation_dir == automations_root or not _is_relative_to(automation_dir, automations_root):
            continue
        if not automation_dir.is_dir():
            continue
        destination = _unique_disabled_destination(disabled_root, automation_dir)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(automation_dir), str(destination))
        moved.append({"source": str(automation_dir), "destination": str(destination)})
    return moved


def build_report(
    *,
    root: Path,
    user_codex_home: Path,
    write_user_profile: bool,
    disable_stale_user_profile_launchers_before_write: bool = False,
    include_payloads: bool = False,
) -> dict[str, Any]:
    root = root.resolve()
    user_codex_home = user_codex_home.resolve()
    disabled: list[dict[str, str]] = []
    if disable_stale_user_profile_launchers_before_write:
        disabled = disable_stale_user_profile_launchers(root=root, user_codex_home=user_codex_home)
    written: list[str] = []
    if write_user_profile:
        written = write_user_profile_projections(root=root, user_codex_home=user_codex_home)

    projections = enforcement_home.iter_user_profile_projections(root)
    expected_ids = [projection["id"] for projection in projections]
    issues = enforcement_home.validate(root, user_codex_home)
    report: dict[str, Any] = {
        "schema_version": "codex-automation-ui-mirror-projection/v1",
        "status": "PASS" if not issues else "FAIL",
        "repo_root": str(root),
        "user_codex_home": str(user_codex_home),
        "expected_projection_ids": expected_ids,
        "projection_count": len(expected_ids),
        "disabled_stale_launchers": disabled,
        "written": written,
        "issues": [issue.__dict__ for issue in issues],
    }
    if include_payloads:
        report["launcher_ui_mirror_payloads"] = [
            {
                "mode": "ui_mirror",
                "schema": projection["schema"],
                "id": projection["id"],
                "automationId": projection["automation_id"],
                "kind": projection["kind"],
                "name": projection.get("name") or projection["id"],
                "prompt": projection["prompt"],
                "status": projection["status"],
                "rrule": projection["rrule"],
                "model": projection["model"],
                "reasoningEffort": projection["reasoning_effort"],
                "executionEnvironment": projection["execution_environment"],
                "cwds": projection["cwds"],
                "repoRoot": projection["repo_root"],
                "contractPath": projection["contract_path"],
                "contractSha256": projection["contract_sha256"],
            }
            for projection in projections
        ]
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=enforcement_home.REPO_ROOT, help="Repository root to read")
    parser.add_argument(
        "--user-codex-home",
        type=Path,
        default=enforcement_home.DEFAULT_USER_CODEX_HOME,
        help="Codex user profile home to check or write",
    )
    parser.add_argument(
        "--write-user-profile",
        action="store_true",
        help="Write generated launcher mirror TOMLs for active repo cron automations",
    )
    parser.add_argument(
        "--disable-stale-user-profile-launchers",
        action="store_true",
        help="Move stale full-copy user-profile launchers to automations-disabled before writing",
    )
    parser.add_argument(
        "--include-payloads",
        action="store_true",
        help="Include generated launcher mirror payloads in the report",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(
        root=args.root,
        user_codex_home=args.user_codex_home,
        write_user_profile=args.write_user_profile,
        disable_stale_user_profile_launchers_before_write=args.disable_stale_user_profile_launchers,
        include_payloads=args.include_payloads,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"{report['status']}: {report['projection_count']} expected Codex Desktop automation launcher mirrors")
        for automation_id in report["expected_projection_ids"]:
            print(f"- {automation_id}")
        for issue in report["issues"]:
            print(f"- {issue['code']}: {issue['detail']}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
