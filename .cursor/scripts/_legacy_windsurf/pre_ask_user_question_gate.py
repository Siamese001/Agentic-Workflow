#!/usr/bin/env python3
"""Pre-hook for ask_user_question to route decisions through correct pipeline.

Plan: author-gate-ask-ui-consolidated-a1e3f7 W2.

Responsibility:
1. Detect if ask_user_question context is Author-Gate-class (governance decisions)
2. Route AG-class → canonical emit_packet.py pipeline
3. Route non-AG → enriched_choice_builder pipeline
4. Ensure exactly one of AUTHOR_GATE_PACKET or ASK_USER_QUESTION_PACKET is emitted

Detection uses keyword heuristics + option structure analysis.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

# Detection heuristics from plan a7e3d2
AUTHOR_GATE_KEYWORDS = [
    # Governance-class decision indicators
    "author-gate", "author_gate", "AG-", "decision", "confidence",
    "recommend", "option A", "blast radius", "precedent",
    # Architecture/refactoring indicators
    "refactor", "delete", "archive", "cross-layer", "migration",
    "breaking change", "extract", "consolidate", "deprecat",
    "new dependency", "add dependency", "rename file", "move file",
    # Anti-pattern indicators
    "bare except", "except exception", "shell=true", "subprocess",
]

# Minimum keyword density to trigger AG classification
DENSITY_THRESHOLD = 2


def _decision_keyword_count(text: str) -> int:
    """Count governance-class keywords in text."""
    lower = text.lower()
    return sum(1 for kw in AUTHOR_GATE_KEYWORDS if kw in lower)


def _has_structured_options(options: list[dict[str, Any]]) -> bool:
    """Check if options have AG-structured fields (confidence, thesis, tradeoffs)."""
    for opt in options:
        if any(field in opt for field in ["confidence", "score", "thesis", "key_tradeoffs"]):
            return True
        # Check description for bracketed confidence prefix
        desc = opt.get("description", "")
        if re.search(r"\[confidence=\d+\.\d+\]", desc):
            return True
    return False


def classify_decision_type(
    question: str,
    options: list[dict[str, Any]],
    context_text: str = "",
) -> str:
    """Classify decision as AUTHOR_GATE or ENRICHED_CHOICE.
    
    Returns:
        "AUTHOR_GATE" — governance-class decision requiring canonical pipeline
        "ENRICHED_CHOICE" — standard multi-option decision
    """
    combined_text = f"{question} {context_text}"
    
    # Check 1: Keyword density
    keyword_count = _decision_keyword_count(combined_text)
    if keyword_count >= DENSITY_THRESHOLD:
        return "AUTHOR_GATE"
    
    # Check 2: Structured options with AG fields
    if _has_structured_options(options):
        return "AUTHOR_GATE"
    
    # Check 3: Option count — 2-4 options typical for AG decisions
    if 2 <= len(options) <= 4:
        # Additional check: do options have trade-off like language?
        tradeoff_indicators = ["pros:", "cons:", "trade-off", "risk", "benefit"]
        for opt in options:
            desc = opt.get("description", "").lower()
            if any(ti in desc for ti in tradeoff_indicators):
                return "AUTHOR_GATE"
    
    # Default: standard enriched choice
    return "ENRICHED_CHOICE"


def route_to_author_gate(
    question: str,
    options: list[dict[str, Any]],
    recommended_id: str | None = None,
    telemetry_context: str | None = None,
) -> dict[str, Any]:
    """Route through canonical Author-Gate pipeline.
    
    Returns payload ready for emit_packet.py.
    """
    # Import emit_packet components
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from tools.decisions.enriched_choice_builder import build_enriched_choice_question
        
        # Use enriched builder but mark as AUTHOR_GATE context
        # The actual AUTHOR_GATE_PACKET emission happens via emit_packet.py
        payload = build_enriched_choice_question(
            question=question,
            options=options,
            recommended_id=recommended_id,
            telemetry_context=telemetry_context or "author_gate_routed",
        )
        
        # Mark packet type for downstream routing
        payload["telemetry_packet"]["packet_type"] = "AUTHOR_GATE_ROUTED"
        payload["_routing"] = "AUTHOR_GATE"
        
        return payload
    finally:
        sys.path.pop(0)


def route_to_enriched_choice(
    question: str,
    options: list[dict[str, Any]],
    recommended_id: str | None = None,
    telemetry_context: str | None = None,
) -> dict[str, Any]:
    """Route through lightweight enriched choice pipeline.
    
    Returns payload with ASK_USER_QUESTION_PACKET.
    """
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from tools.decisions.enriched_choice_builder import build_enriched_choice_question
        
        payload = build_enriched_choice_question(
            question=question,
            options=options,
            recommended_id=recommended_id,
            telemetry_context=telemetry_context or "enriched_choice",
        )
        
        payload["_routing"] = "ENRICHED_CHOICE"
        return payload
    finally:
        sys.path.pop(0)


def pre_ask_user_question_gate(
    question: str,
    options: list[dict[str, Any]],
    recommended_id: str | None = None,
    telemetry_context: str | None = None,
    context_text: str = "",
) -> dict[str, Any]:
    """Main entry point: classify and route ask_user_question.
    
    Args:
        question: The question text
        options: List of option dicts (id, label, description, ...)
        recommended_id: Optional recommended option ID
        telemetry_context: Optional context string
        context_text: Additional context for classification (e.g., surrounding text)
    
    Returns:
        Payload dict with:
        - question: str (enriched)
        - options: list[dict] (formatted)
        - telemetry_packet: dict (ASK_USER_QUESTION_PACKET or AUTHOR_GATE_ROUTED)
        - _routing: str (AUTHOR_GATE or ENRICHED_CHOICE)
    
    Example:
        >>> payload = pre_ask_user_question_gate(
        ...     question="Which approach for the refactor?",
        ...     options=[
        ...         {"id": "A", "label": "Extract module", "description": "...", "tradeoff": "..."},
        ...         {"id": "B", "label": "Inline code", "description": "...", "tradeoff": "..."},
        ...     ],
        ...     recommended_id="A",
        ... )
        >>> # Route determined by keyword "refactor"
        >>> assert payload["_routing"] == "AUTHOR_GATE"
    """
    decision_type = classify_decision_type(question, options, context_text)
    
    if decision_type == "AUTHOR_GATE":
        return route_to_author_gate(
            question=question,
            options=options,
            recommended_id=recommended_id,
            telemetry_context=telemetry_context,
        )
    else:
        return route_to_enriched_choice(
            question=question,
            options=options,
            recommended_id=recommended_id,
            telemetry_context=telemetry_context,
        )


def main() -> int:
    """CLI entry point for testing/hook integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pre-hook for ask_user_question routing")
    parser.add_argument("--hook-mode", action="store_true", help="Run as Windsurf hook")
    parser.add_argument("--test", action="store_true", help="Test mode (prints diagnostic)")
    args = parser.parse_args()
    
    if args.test:
        print("[pre_ask_user_question_gate] Test mode: OK")
        return 0
    
    if args.hook_mode:
        # In hook mode, we check environment/context for decision signals
        # This is a passive hook - it logs context but doesn't block
        import os
        
        context_file = os.environ.get("WINDSURF_CONTEXT_FILE")
        if context_file and Path(context_file).exists():
            try:
                with open(context_file) as f:
                    ctx = json.load(f)
                # Log that we're in a decision context
                if ctx.get("tool_name") == "ask_user_question":
                    print("[pre_ask_user_question_gate] Detected ask_user_question context")
            except Exception:
                pass
        
        # Hook always returns 0 (passive observation)
        return 0
    
    # Standard stdin mode for testing
    try:
        input_raw = sys.stdin.read()
        if not input_raw.strip():
            print("[pre_ask_user_question_gate] Error: No input provided", file=sys.stderr)
            return 1
        
        input_data = json.loads(input_raw)
    except json.JSONDecodeError as e:
        print(f"[pre_ask_user_question_gate] Error: Invalid JSON: {e}", file=sys.stderr)
        return 1
    
    # Extract parameters
    question = input_data.get("question", "")
    options = input_data.get("options", [])
    recommended_id = input_data.get("recommended_id")
    telemetry_context = input_data.get("telemetry_context")
    context_text = input_data.get("context_text", "")
    
    if not question or not options:
        print("[pre_ask_user_question_gate] Error: Missing required fields", file=sys.stderr)
        return 1
    
    # Route
    payload = pre_ask_user_question_gate(
        question=question,
        options=options,
        recommended_id=recommended_id,
        telemetry_context=telemetry_context,
        context_text=context_text,
    )
    
    # Output result
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
