"""selectedAvatarGuard - enforce the active Codex avatar for this workspace."""

from __future__ import annotations

import os
import sys
import tomllib
from pathlib import Path

from lib.codex_hook_common import allow, block, read_payload, write_receipt

DEFAULT_AVATAR_ID = "patch-fox"
CONFIG_PATH = Path(
    os.environ.get("CODEX_CONFIG_TOML", str(Path.home() / ".codex" / "config.toml"))
)
REQUIRED_AVATAR_ID = os.environ.get("CODEX_REQUIRED_AVATAR_ID", DEFAULT_AVATAR_ID).strip() or DEFAULT_AVATAR_ID


def _read_selected_avatar_id() -> tuple[str, str]:
    if not CONFIG_PATH.is_file():
        return "", f"missing config file: {CONFIG_PATH}"
    try:
        with CONFIG_PATH.open("rb") as fh:
            data = tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return "", f"could not read {CONFIG_PATH}: {exc}"
    value = data.get("selected-avatar-id")
    if not isinstance(value, str) or not value.strip():
        return "", f"selected-avatar-id missing in {CONFIG_PATH}"
    return value.strip(), ""


def main() -> int:
    payload = read_payload()
    selected_avatar_id, error = _read_selected_avatar_id()
    if error:
        reason = f"Avatar enforcement failed: {error}; required avatar is '{REQUIRED_AVATAR_ID}'."
        write_receipt("selectedAvatarGuard", payload, "block", reason)
        sys.stderr.write(f"[HOOK] {reason}\n")
        raise SystemExit(block(reason))

    if selected_avatar_id != REQUIRED_AVATAR_ID:
        reason = (
            f"Codex avatar must be '{REQUIRED_AVATAR_ID}' for this workspace; "
            f"current selected-avatar-id is '{selected_avatar_id}' in {CONFIG_PATH}. "
            "Update Codex settings and restart."
        )
        write_receipt("selectedAvatarGuard", payload, "block", reason)
        sys.stderr.write(f"[HOOK] {reason}\n")
        raise SystemExit(block(reason))

    reason = f"selected-avatar-id is '{selected_avatar_id}'"
    write_receipt("selectedAvatarGuard", payload, "allow", reason)
    raise SystemExit(allow(reason))


if __name__ == "__main__":
    raise SystemExit(main())
