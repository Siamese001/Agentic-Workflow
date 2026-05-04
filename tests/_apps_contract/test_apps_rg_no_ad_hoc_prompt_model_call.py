"""Test: apps_rg has no ad-hoc prompt-provider calls.

Source scan: forbids model/provider calls with manually joined prompt
strings in the L2 step layer.  Direct SDK calls without
compiled_prompt_artifact are forbidden in steps.py.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_STEPS_PATH = Path(__file__).resolve().parent.parent.parent / "apps_rg" / "l2_recipe" / "steps.py"
_APPS_RG_ROOT = Path(__file__).resolve().parent.parent.parent / "apps_rg"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_steps_do_not_build_raw_prompts():
    content = _read(_STEPS_PATH)
    forbidden = [
        r"f\".*\{.*jd.*\}.*\{.*resume.*\}",
        r"prompt\s*=\s*f\"",
        r"prompt\s*=\s*\".*\+",
        r"\.format\(.*jd.*resume",
    ]
    for pattern in forbidden:
        matches = re.findall(pattern, content, re.IGNORECASE)
        assert not matches, f"Ad-hoc prompt construction found in steps.py: {pattern}"


def test_steps_require_pa_guard():
    content = _read(_STEPS_PATH)
    assert "_PAGuard.check" in content


def test_steps_reference_compiled_prompt_artifact():
    content = _read(_STEPS_PATH)
    assert "compiled_prompt_artifact" in content


def test_no_direct_anthropic_sdk_in_steps():
    content = _read(_STEPS_PATH)
    assert "anthropic.Anthropic" not in content
    assert "openai.OpenAI" not in content
    assert "import anthropic" not in content
    assert "import openai" not in content


def test_no_direct_provider_call_in_steps():
    content = _read(_STEPS_PATH)
    forbidden_patterns = [
        "client.messages.create",
        "client.chat.completions.create",
        "client.complete",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in content, f"Direct provider call found in steps.py: {pattern}"


def test_generate_step_class_has_requires_pa_true():
    content = _read(_STEPS_PATH)
    assert "REQUIRES_PA = True" in content
