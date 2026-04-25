#!/usr/bin/env python3
"""Standalone Anthropic API key sanity check.

Answers the question "does my ANTHROPIC_API_KEY actually work?" without
depending on the (currently import-broken) HardenedAnthropicExecutor.

Usage:
    python tools/diag/verify_anthropic_key.py
    python tools/diag/verify_anthropic_key.py --model claude-haiku-4-5
    python tools/diag/verify_anthropic_key.py --no-network  # env-only check

Exit codes:
    0 - key present and API call succeeded
    1 - key present but API call failed (see stderr for reason)
    2 - key missing from environment AND .env

This script is deliberately self-contained: no imports from agentic_core or
apps_rg so it runs even when those subsystems are broken.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import WINDSURF_PLANS_DIR


def _load_dotenv_if_available() -> None:
    """Import python-dotenv and load .env. Silent if dotenv is not installed."""
    try:
        from dotenv import load_dotenv  # noqa: PLC0415
    except ImportError:
        print("[warn] python-dotenv not installed; .env will not be read", file=sys.stderr)
        return
    repo_root = Path(__file__).resolve().parents[2]
    dotenv_path = repo_root / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path)


def _check_key_present() -> tuple[bool, str]:
    """Return (found, description)."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return False, "ANTHROPIC_API_KEY is not set in the environment"
    if not key.startswith("sk-ant-"):
        return True, f"set (len={len(key)}) but does NOT start with 'sk-ant-' - looks malformed"
    return True, f"set (len={len(key)}, prefix={key[:12]}...)"


def _live_ping(model: str) -> tuple[bool, str]:
    """Make the smallest possible Anthropic API call to verify the key works."""
    try:
        import anthropic  # noqa: PLC0415
    except ImportError:
        return False, "anthropic SDK is not installed (pip install anthropic)"

    try:
        client = anthropic.Anthropic()
    except (anthropic.APIError, ValueError) as exc:
        return False, f"client construction failed: {exc!r}"

    try:
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Reply with exactly: OK"}],
        )
    except anthropic.AuthenticationError as exc:
        return False, f"authentication failed (key rejected by API): {exc}"
    except anthropic.NotFoundError as exc:
        return False, f"model not found - try --model claude-haiku-4-5 or claude-sonnet-4-5: {exc}"
    except anthropic.APIError as exc:
        return False, f"API error: {exc!r}"

    text = ""
    if response.content:
        first = response.content[0]
        text = getattr(first, "text", str(first))

    usage = getattr(response, "usage", None)
    usage_str = ""
    if usage is not None:
        usage_str = f" (input={usage.input_tokens}, output={usage.output_tokens})"

    return True, f"live call succeeded{usage_str}; response: {text!r}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--model",
        default="claude-haiku-4-5",
        help="Anthropic model to ping (default: claude-haiku-4-5, cheapest)",
    )
    parser.add_argument(
        "--no-network",
        action="store_true",
        help="Skip the live API call; only check that the key is present",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Anthropic API key sanity check")
    print("=" * 60)

    _load_dotenv_if_available()

    found, description = _check_key_present()
    print(f"[env]  ANTHROPIC_API_KEY: {description}")
    if not found:
        repo_root = Path(__file__).resolve().parents[2]
        dotenv = repo_root / ".env"
        if dotenv.exists():
            has_key_in_file = any(
                line.strip().startswith("ANTHROPIC_API_KEY=")
                for line in dotenv.read_text(encoding="utf-8").splitlines()
                if not line.strip().startswith("#")
            )
            if has_key_in_file:
                print(
                    f"[hint] Key IS in {dotenv} but python-dotenv did not load it. "
                    "Ensure python-dotenv is installed: pip install python-dotenv",
                    file=sys.stderr,
                )
        return 2

    if args.no_network:
        print("[skip] --no-network flag set; skipping live API call")
        return 0

    print(f"[ping] calling {args.model} with a 10-token test prompt...")
    ok, description = _live_ping(args.model)
    print(f"[ping] result: {description}")

    if ok:
        print()
        print("SUCCESS: your Anthropic API key works.")
        print()
        print("If HardenedAnthropicExecutor still fails at runtime, the issue")
        print("is NOT your key. See the cascade-import RCA tracked in")
        print(f"{WINDSURF_PLANS_DIR}/anthropic-rag-gaps-7f3c2a.md W2 P2.1.followup.")
        return 0

    print()
    print("FAILURE: the key is set but the API call did not succeed.", file=sys.stderr)
    print("See error above for the specific cause.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
