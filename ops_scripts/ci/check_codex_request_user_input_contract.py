#!/usr/bin/env python3
"""Verify the Codex request_user_input decision UI contract.

This is intentionally scoped to the active request-decision surface. Historical
archives, provider model IDs, and unrelated hook runtimes are not part of this
guard.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[2]

CONTRACT_FILES = (
    ".codex/skills/ask-user-question-recommendation/SKILL.md",
    ".codex/hooks.json",
    ".codex/hooks/before_ask_user_question.py",
    ".codex/hooks/after_ask_user_question.py",
    ".codex/hooks/pre_write_north_star_gate.py",
    ".codex/governance/scripts/pre_ask_user_question_recommendation_gate.py",
    ".codex/governance/scripts/post_ask_user_question_capture.py",
    ".codex/governance/scripts/post_agent_recommendation_gate_audit.py",
    "tools/decisions/enriched_choice_builder.py",
    "ops_scripts/ci/check_ask_user_question_loop_wired.py",
)

REQUIRED_SUBSTRINGS = {
    ".codex/skills/ask-user-question-recommendation/SKILL.md": (
        "call `request_user_input` only when Codex exposes it in the",
        "ask one plain-text clarifying question",
        "Do not claim the UI rendered unless the tool call actually succeeds.",
    ),
    ".codex/rules/constitutional.md": (
        "If the tool is unavailable in the current mode",
        "do not claim the UI rendered",
    ),
}


class Finding(NamedTuple):
    path: str
    line: int
    code: str
    detail: str


_FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("legacy_product_token", re.compile("c" + "laude", re.IGNORECASE)),
    ("legacy_question_tool", re.compile("Ask" + "User" + "Question")),
    ("raw_question_helper_call", re.compile(r"\bask_user_question\s*\(")),
    ("retired_packet_marker", re.compile("AUTHOR" + "_GATE" + "_PACKET")),
    ("retired_decision_marker", re.compile("DECISION" + "_CAPTURED")),
    ("retired_ui_renderer_skill", re.compile("author-gate-ui-" + "renderer", re.IGNORECASE)),
    ("retired_packet_builder_skill", re.compile("author-gate-packet-" + "builder", re.IGNORECASE)),
)


def _scan_contract_files(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for rel_path in CONTRACT_FILES:
        path = root / rel_path
        if not path.is_file():
            findings.append(Finding(rel_path, 0, "missing_contract_file", "file is required"))
            continue
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            for code, pattern in _FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(rel_path, line_no, code, line.strip()))
    return findings


def _required_text_findings(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for rel_path, snippets in REQUIRED_SUBSTRINGS.items():
        path = root / rel_path
        if not path.is_file():
            findings.append(Finding(rel_path, 0, "missing_required_text_file", "file is required"))
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet not in text:
                findings.append(Finding(rel_path, 0, "missing_required_fallback_text", snippet))
    return findings


def _builder_schema_findings(root: Path) -> list[Finding]:
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from tools.decisions.enriched_choice_builder import build_enriched_choice_question

    payload = build_enriched_choice_question(
        question="Which implementation path should Codex use?",
        options=[
            {
                "id": "A",
                "label": "Direct fix",
                "description": "Patch the active decision UI path",
                "pros": "Smallest code change",
                "cons": "Leaves less room for broader cleanup",
                "tradeoff": "Smallest change but narrower cleanup",
                "confidence": 0.81,
            },
            {
                "id": "B",
                "label": "Broad cleanup",
                "description": "Patch every historical governance reference",
                "pros": "Removes more old wording",
                "cons": "High churn and unrelated risk",
                "tradeoff": "More complete wording cleanup but much higher churn",
                "confidence": 0.62,
            },
        ],
        recommended_id="A",
        telemetry_context="codex-request-ui-contract",
    )

    findings: list[Finding] = []
    if payload.get("tool_name") != "functions.request_user_input":
        findings.append(Finding("tools/decisions/enriched_choice_builder.py", 0, "wrong_tool_name", str(payload.get("tool_name"))))

    tool_input = payload.get("tool_input")
    questions = tool_input.get("questions") if isinstance(tool_input, dict) else None
    if not isinstance(questions, list) or len(questions) != 1:
        findings.append(Finding("tools/decisions/enriched_choice_builder.py", 0, "missing_questions_array", repr(tool_input)))
        return findings

    question = questions[0]
    if not isinstance(question, dict):
        findings.append(Finding("tools/decisions/enriched_choice_builder.py", 0, "invalid_question_shape", repr(question)))
        return findings

    for field in ("id", "header", "question"):
        if not isinstance(question.get(field), str) or not question[field].strip():
            findings.append(Finding("tools/decisions/enriched_choice_builder.py", 0, f"missing_question_{field}", repr(question)))

    if "multiSelect" in question:
        findings.append(Finding("tools/decisions/enriched_choice_builder.py", 0, "legacy_multiselect_field", repr(question)))

    options = question.get("options")
    if not isinstance(options, list) or not 2 <= len(options) <= 3:
        findings.append(Finding("tools/decisions/enriched_choice_builder.py", 0, "invalid_option_count", repr(options)))
        return findings

    first = options[0]
    if not isinstance(first, dict) or not str(first.get("label", "")).endswith("(Recommended)"):
        findings.append(Finding("tools/decisions/enriched_choice_builder.py", 0, "recommended_not_first", repr(first)))
    if "[RECOMMENDED" not in str(first.get("description", "")):
        findings.append(Finding("tools/decisions/enriched_choice_builder.py", 0, "missing_recommendation_detail", repr(first)))

    return findings


def check_contract(root: Path = ROOT) -> list[Finding]:
    findings = _scan_contract_files(root)
    findings.extend(_required_text_findings(root))
    findings.extend(_builder_schema_findings(root))
    return findings


def main() -> int:
    findings = check_contract(ROOT)
    if findings:
        print("[check_codex_request_user_input_contract] FAIL")
        for finding in findings:
            location = f"{finding.path}:{finding.line}" if finding.line else finding.path
            print(f"- {location}: {finding.code}: {finding.detail}")
        return 1

    print("[check_codex_request_user_input_contract] PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
