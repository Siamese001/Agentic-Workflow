"""Shared interactive-wizard helper for apps_* CLI entrypoints.

Extracted from apps_rg/__main__.py 2026-05-06 (W1 of plan
apps-rg-vllm-deferred-followup-f7d3a9). Apps that have mandatory target
inputs which would risk silent cross-target contamination if auto-filled
can use this helper to prompt the user.

**HARDENED 2026-05-06**: Wizard now ALWAYS fires when mandatory inputs are
missing — no TTY restriction. In non-TTY environments (IDE, CI), it uses
a file-based input mechanism: writes a template, user fills it, wizard
reads it back automatically.

Pattern (sibling rule: ``.windsurf/rules/apps-rg-interactive-discipline.md``):
  1. Parse argparse args
  2. If any required field missing → run_wizard() (ALWAYS, not just TTY)
  3. After wizard, run argparse error-checks anyway (for defense in depth)

Usage::

    from apps_shared.cli.interactive_wizard import WizardField, run_wizard

    fields = [
        WizardField("company", "Target company", kind="string"),
        WizardField("description", "Job description", kind="multiline_or_file"),
        WizardField(
            "briefing",
            "Briefing document",
            kind="multiline_or_file_or_auto",
            choices_help="'auto' delegates retrieval; '@path' loads file",
        ),
    ]
    values = run_wizard(fields, header="apps_rg interactive setup")
    # values["company"], values["description"], values["briefing"]
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

WizardKind = Literal[
    "string",
    "multiline_or_file",
    "multiline_or_file_or_auto",
]


@dataclass
class WizardField:
    """Specification for a single wizard prompt.

    Attributes
    ----------
    name : str
        Key under which the captured value is returned by ``run_wizard``.
    prompt : str
        Human-readable label shown to the user.
    kind : WizardKind
        Input shape — see module docstring for variants.
    choices_help : str | None
        Extra one-line help shown beneath the prompt for kinds that accept
        sentinel values like ``auto`` or ``@path``.
    required : bool
        When True (default), the wizard re-prompts on empty input. Set
        False to allow empty answers (rare for true mandatory inputs).
    """

    name: str
    prompt: str
    kind: WizardKind = "string"
    choices_help: str | None = None
    required: bool = True


def read_multiline_or_file(label: str) -> tuple[str, str | None]:
    """Read input that may be (a) multiline text terminated by ``END``, or
    (b) ``@path/to/file`` to load file contents.

    Returns ``(text, source_marker)``. ``source_marker`` is the file path
    when content was loaded from disk, else ``None``. Empty input returns
    ``("", None)``.
    """
    print(
        f"  Paste {label} (or '@path/to/file' to load, type 'END' on its own "
        "line to finish):"
    )
    first = input("  > ").strip()
    if not first:
        return "", None
    if first.startswith("@"):
        path = first[1:].strip()
        try:
            return Path(path).read_text(encoding="utf-8"), path
        except OSError as exc:
            print(f"    [warn] could not read {path}: {exc}")
            return "", None
    if first == "END":
        return "", None
    lines = [first]
    while True:
        try:
            line = input("  > ")
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines), None


def _prompt_string(field: WizardField, idx: str) -> str:
    while True:
        value = input(f"{idx} {field.prompt}: ").strip()
        if value or not field.required:
            return value
        print("    [warn] input required; please type a value")


def _prompt_multiline_or_file(field: WizardField, idx: str) -> dict[str, str | None]:
    print(f"{idx} {field.prompt}")
    if field.choices_help:
        print(f"      ({field.choices_help})")
    text, source = read_multiline_or_file(field.prompt.lower())
    return {"text": text, "source": source}


def _prompt_multiline_or_file_or_auto(
    field: WizardField, idx: str
) -> dict[str, str | None]:
    print(f"{idx} {field.prompt}")
    print("      Options:")
    print("        - 'auto'              → delegate retrieval to upstream service")
    print("        - '@path/to/file.json' → load existing file from disk")
    print("        - paste multiline text, terminate with 'END'")
    if field.choices_help:
        print(f"      Note: {field.choices_help}")
    choice = input("  > ").strip()

    if choice.lower() == "auto":
        return {"mode": "auto", "text": "", "source": None}
    if choice.startswith("@"):
        path = choice[1:].strip()
        if not Path(path).exists():
            print(f"      [warn] {path} not found; falling back to auto")
            return {"mode": "auto", "text": "", "source": None}
        return {"mode": "file", "text": "", "source": path}
    # Treat as start of multiline paste
    lines = [choice] if choice else []
    while True:
        try:
            line = input("  > ")
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    text = "\n".join(lines).strip()
    if not text:
        print("      [warn] empty input; falling back to auto")
        return {"mode": "auto", "text": "", "source": None}
    return {"mode": "paste", "text": text, "source": None}


_DEFAULT_WIZARD_INPUT_PATH = Path("apps_rg/scripts/_wizard_input.json")


def _load_wizard_input_from_file(input_path: Path) -> dict[str, Any] | None:
    """Load wizard inputs from the file-based fallback.

    Returns None if file doesn't exist or is invalid.
    """
    if not input_path.exists():
        return None
    try:
        import json
        data = json.loads(input_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, OSError):  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
        pass
    return None


def _write_wizard_template(fields: list[WizardField], header: str, input_path: Path) -> None:
    """Write a template JSON file for the user to fill in."""
    import json
    template: dict[str, Any] = {"_comment": header, "_instructions": "Fill in all fields, then save and re-run the command"}
    for field in fields:
        if field.kind == "string":
            template[field.name] = ""
        elif field.kind in ("multiline_or_file", "multiline_or_file_or_auto"):
            template[field.name] = {"text": "", "source": None, "mode": "paste"}
    input_path.parent.mkdir(parents=True, exist_ok=True)
    input_path.write_text(json.dumps(template, indent=2), encoding="utf-8")


def run_wizard(
    fields: list[WizardField],
    *,
    header: str = "",
    footer_hint: str = "",
    input_path: Path | str | None = None,
) -> dict[str, dict[str, str | None] | str]:
    """Run an interactive wizard for the given fields.

    Returns a dict keyed by ``field.name``. The value shape depends on the
    field's kind:
      - ``string`` → ``str`` (the typed value)
      - ``multiline_or_file`` → ``{"text": str, "source": str | None}``
      - ``multiline_or_file_or_auto`` → ``{"mode": "auto"|"file"|"paste",
        "text": str, "source": str | None}``

    **HARDENED**: Now works in both TTY and non-TTY environments:
      - TTY (terminal): Interactive prompts via input()
      - Non-TTY (IDE): Writes template file, waits for user to fill it,
        then reads it back automatically on next run.

    Caller is responsible for translating the returned dict into argparse
    namespace updates / file writes / etc.
    """
    # Resolve per-app input path (defaults to apps_rg legacy path for back-compat).
    _input_path = Path(input_path) if input_path else _DEFAULT_WIZARD_INPUT_PATH

    # Force file-based flow when env var is set (Cascade run panel etc. fake a TTY).
    import os as _os
    _force_file = _os.environ.get("WIZARD_FILE_MODE") == "1"

    # Interactive TTY path: always prompt directly when stdin is a real terminal.
    if sys.stdin.isatty() and not _force_file:
        try:
            if header:
                print("=" * 70)
                print(header)
                print("=" * 70)
                print()
            results: dict[str, dict[str, str | None] | str] = {}
            for idx, field in enumerate(fields, start=1):
                label = f"[{idx}/{len(fields)}]"
                if field.kind == "string":
                    results[field.name] = _prompt_string(field, label)
                elif field.kind == "multiline_or_file":
                    results[field.name] = _prompt_multiline_or_file(field, label)
                elif field.kind == "multiline_or_file_or_auto":
                    results[field.name] = _prompt_multiline_or_file_or_auto(field, label)
            if footer_hint:
                print(footer_hint)
            return results
        except EOFError:
            print("\n[wizard] stdin closed unexpectedly — falling back to file-based input flow")

    # Non-TTY fallback: file-based template workflow.
    # Check if the user already filled in the template from a previous run.
    file_input = _load_wizard_input_from_file(_input_path)
    if file_input is not None:
        # Validate that required fields are actually filled before accepting.
        # A stale/unfilled template (all required strings blank, all required
        # multiline blocks empty) must NOT be silently returned — that would
        # produce empty target_company / target_role and crash downstream.
        def _field_filled(field: WizardField, val: object) -> bool:
            if field.kind == "string":
                return isinstance(val, str) and val.strip() != ""
            if field.kind in ("multiline_or_file", "multiline_or_file_or_auto"):
                if not isinstance(val, dict):
                    return False
                if val.get("mode") == "auto":
                    return True
                if val.get("source"):
                    return True
                text = val.get("text")
                return isinstance(text, str) and text.strip() != ""
            return True

        all_required_filled = all(
            _field_filled(field, file_input.get(field.name))
            for field in fields
            if field.required
        )
        if all_required_filled:
            # Validate and convert file input to expected shapes
            file_results: dict[str, dict[str, str | None] | str] = {}
            for field in fields:
                val = file_input.get(field.name)
                if field.kind == "string":
                    file_results[field.name] = str(val) if val else ""
                elif field.kind in ("multiline_or_file", "multiline_or_file_or_auto"):
                    if isinstance(val, dict):
                        file_results[field.name] = val
                    else:
                        file_results[field.name] = {"text": str(val) if val else "", "source": None, "mode": "paste"}
            # Clear the file after reading to prevent stale reuse
            try:
                _input_path.unlink()
            except OSError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
                pass
            return file_results
        # Stale/unfilled template — discard and fall through to write+poll.
        try:
            _input_path.unlink()
        except OSError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
            pass
        print(f"[wizard] discarded stale/unfilled {_input_path} — re-templating")

    # No TTY and no pre-filled file — write template and poll for user input.
    _write_wizard_template(fields, header, _input_path)
    print("=" * 70)
    print(header)
    print("=" * 70)
    print()
    print("WIZARD INPUT REQUIRED")
    print()
    print(f"Template written to: {_input_path}")
    print()
    print("  1. Open that file in your editor")
    print("  2. Fill in ALL fields")
    print("  3. Save it")
    print()
    print("Waiting for you to fill the file... (Ctrl+C to abort)")

    import time
    while True:
        time.sleep(1)
        data = _load_wizard_input_from_file(_input_path)
        if data is None:
            continue
        # Check that at least one mandatory field is non-empty
        filled = any(
            (isinstance(v, str) and v.strip()) or
            (isinstance(v, dict) and (v.get("text") or v.get("source") or v.get("mode") not in (None, "paste")))
            for k, v in data.items()
            if not k.startswith("_")
        )
        if filled:
            print("  → inputs detected, continuing...")
            break

    # Now load and return the filled values.
    file_results: dict[str, dict[str, str | None] | str] = {}
    assert data is not None
    for field in fields:
        val = data.get(field.name)
        if field.kind == "string":
            file_results[field.name] = str(val) if val else ""
        elif field.kind in ("multiline_or_file", "multiline_or_file_or_auto"):
            if isinstance(val, dict):
                file_results[field.name] = val
            else:
                file_results[field.name] = {"text": str(val) if val else "", "source": None, "mode": "paste"}
    try:
        _input_path.unlink()
    except OSError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
        pass
    return file_results
