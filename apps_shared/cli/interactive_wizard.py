"""Shared interactive-wizard helper for apps_* CLI entrypoints.

Extracted from apps_rg/__main__.py 2026-05-06 (W1 of plan
apps-rg-vllm-deferred-followup-f7d3a9). Apps that have mandatory target
inputs which would risk silent cross-target contamination if auto-filled
can use this helper to prompt the user when stdin is a TTY.

When stdin is NOT a TTY (CI, pipe, automation), callers should retain
their hard-fail path — this helper does NOT replace argparse validation,
it supplements it for interactive sessions.

Pattern (sibling rule: ``.windsurf/rules/apps-rg-interactive-discipline.md``):
  1. Parse argparse args
  2. If sys.stdin.isatty() AND any required field missing → run_wizard()
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
from typing import Literal

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


def run_wizard(
    fields: list[WizardField],
    *,
    header: str = "",
    footer_hint: str = "",
) -> dict[str, dict[str, str | None] | str]:
    """Run an interactive wizard for the given fields.

    Returns a dict keyed by ``field.name``. The value shape depends on the
    field's kind:
      - ``string`` → ``str`` (the typed value)
      - ``multiline_or_file`` → ``{"text": str, "source": str | None}``
      - ``multiline_or_file_or_auto`` → ``{"mode": "auto"|"file"|"paste",
        "text": str, "source": str | None}``

    Caller is responsible for translating the returned dict into argparse
    namespace updates / file writes / etc. This helper does NOT touch
    sys.argv or write any files — it only collects user input.

    Raises
    ------
    RuntimeError
        If invoked when ``sys.stdin.isatty()`` is False. Callers must
        gate the invocation themselves; this error is a defense-in-depth
        guard.
    """
    if not sys.stdin.isatty():
        raise RuntimeError(
            "run_wizard requires a TTY; caller must gate on sys.stdin.isatty()"
        )

    print()
    print("=" * 70)
    if header:
        print(header)
        print("=" * 70)

    results: dict[str, dict[str, str | None] | str] = {}
    total = len(fields)
    for i, field in enumerate(fields, start=1):
        idx = f"[{i}/{total}]"
        if field.kind == "string":
            results[field.name] = _prompt_string(field, idx)
        elif field.kind == "multiline_or_file":
            results[field.name] = _prompt_multiline_or_file(field, idx)
        elif field.kind == "multiline_or_file_or_auto":
            results[field.name] = _prompt_multiline_or_file_or_auto(field, idx)
        else:  # pragma: no cover — kind is Literal; mypy/runtime guard
            raise ValueError(f"unknown WizardField kind: {field.kind!r}")
        print()

    print("=" * 70)
    if footer_hint:
        print(footer_hint)
        print("=" * 70)
    print()
    return results
