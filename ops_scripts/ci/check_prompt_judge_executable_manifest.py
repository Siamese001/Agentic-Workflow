#!/usr/bin/env python3
"""Advisory CI: W4 executable prompt manifest covers all GENERATED_LANES."""

from __future__ import annotations

import sys


def main() -> int:
    from apps_rg.runtime.sections.section_prompt_authority_ssot import (
        assert_all_generated_lanes_executable_corpus_non_empty,
    )

    try:
        assert_all_generated_lanes_executable_corpus_non_empty()
    except AssertionError as exc:
        print(f"prompt_judge_executable_manifest: FAIL — {exc}", file=sys.stderr)
        return 1
    print("prompt_judge_executable_manifest: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
