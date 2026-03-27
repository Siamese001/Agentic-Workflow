#!/usr/bin/env python3
"""
Run token optimizer on the repo hygiene plan phases.
Uses ContextWindowEstimator from agentic_core.planning.token_estimator
to produce actual token estimates per phase.

No code changes — read-only analysis.
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

try:
    from agentic_core.planning.token_estimator import ContextWindowEstimator
    est = ContextWindowEstimator()
except ImportError as e:
    logging.error(f"Failed to import ContextWindowEstimator: {e}. Ensure agentic_core is available.")
    sys.exit(1)

# --- Agentic Context Assumptions ---
# Establish baseline overhead for the L1/C0 worktable assembly
ASSUMED_SYSTEM_PROMPT_TOKENS = 2500  # Core laws, persona definitions, strict rules
ASSUMED_HISTORY_TOKENS = 1500        # Recent conversation turns/context


def chars(path):
    """Safely reads characters from a file path."""
    fp = os.path.join(ROOT, path)
    if os.path.isfile(fp):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            logging.warning(f"Failed to read {fp}: {e}")
            return ""
    return ""


def tok(text, ctype="text"):
    """Estimates tokens, guarding against empty inputs."""
    if not text:
        return 0
    return est._estimate_tokens(text, ctype)


def main():
    # --- Phase 0: Token Optimization & Pre-Commit Cleanup ---
    plan_content = chars(
        "docs/reports/plans/repo-hygiene-precommit-optimization-e0f719.md"
    )
    precommit_content = chars(".pre-commit-config.yaml")
    p0_plan = tok(plan_content, "text")
    p0_pc = tok(precommit_content, "text")
    p0 = p0_plan + p0_pc
    print(f"Phase 0 — Token Optimization & Pre-Commit Cleanup")
    print(f"  plan file:     {p0_plan:>8,} tokens  ({len(plan_content):,} chars)")
    print(f"  precommit cfg: {p0_pc:>8,} tokens  ({len(precommit_content):,} chars)")
    print(f"  TOTAL P0:      {p0:>8,} tokens")
    print(f"  Assumption: read plan + pre-commit config, apply compression")
    print()

# --- Phase 1: Inventory & HITL Classification ---
    # 644 files × ~200 chars per manifest entry (path + classification + reason)
    manifest_chars = 644 * 200
    p1 = tok("x" * manifest_chars, "json")
    print(f"Phase 1 — Inventory & HITL Classification")
    print(f"  manifest out:  {p1:>8,} tokens  ({manifest_chars:,} chars)")
    print(f"  TOTAL P1:      {p1:>8,} tokens")
    print(f"  Assumption: 644 files × 200 chars/entry JSON manifest")
    print()

    # --- Phase 2: Archive with HITL Confirmation ---
    # ~90 git mv commands × ~80 chars each + HITL prompts (~500 chars × 5 batches)
    mv_chars = 90 * 80
    hitl_chars = 5 * 500
    p2_mv = tok("x" * mv_chars, "text")
    p2_hitl = tok("x" * hitl_chars, "text")
    p2 = p2_mv + p2_hitl
    print(f"Phase 2 — Archive with HITL Confirmation")
    print(f"  git mv cmds:   {p2_mv:>8,} tokens  ({mv_chars:,} chars, 90 files)")
    print(f"  HITL prompts:  {p2_hitl:>8,} tokens  ({hitl_chars:,} chars, 5 batches)")
    print(f"  TOTAL P2:      {p2:>8,} tokens")
    print(f"  Assumption: 90 archive moves + 5 HITL batch prompts")
    print()

    # --- Phase 3: Extract Reusable Capabilities ---
    # ~20 source files × avg 300 lines × 40 chars/line
    extract_chars = 20 * 300 * 40
    p3 = tok("x" * extract_chars, "code")
    print(f"Phase 3 — Extract Reusable Capabilities")
    print(f"  source files:  {p3:>8,} tokens  ({extract_chars:,} chars, 20 files)")
    print(f"  TOTAL P3:      {p3:>8,} tokens")
    print(f"  Assumption: 20 files × 300 lines × 40 chars/line")
    print()

    # --- Phase 4: Pre-Commit Tiering & CI Integration ---
    # Read all 31 workflow files + pre-commit config
    wf_dir = os.path.join(ROOT, ".github", "workflows")
    wf_chars = 0
    wf_count = 0
    if os.path.isdir(wf_dir):
        try:
            for f in os.listdir(wf_dir):
                if f.endswith((".yml", ".yaml")):
                    wf_count += 1
                    wf_chars += len(chars(os.path.join(".github", "workflows", f)))
        except OSError as e:
            logging.error(f"Error accessing workflows directory: {e}")
    p4_wf = tok("x" * wf_chars, "text")
    p4 = p4_wf + p0_pc
    print(f"Phase 4 — Pre-Commit Tiering & CI Integration")
    print(f"  {wf_count} workflows:  {p4_wf:>8,} tokens  ({wf_chars:,} chars)")
    print(f"  precommit cfg: {p0_pc:>8,} tokens  (reused from P0)")
    print(f"  TOTAL P4:      {p4:>8,} tokens")
    print(f"  Assumption: read all {wf_count} workflow files + pre-commit config")
    print()

    # --- Phase 5: Territory Boundary Enforcement ---
    # Script sprawl guard updates + root hygiene rules (~5KB)
    p5_chars = 5000
    p5 = tok("x" * p5_chars, "code")
    print(f"Phase 5 — Territory Boundary Enforcement")
    print(f"  script updates:{p5:>8,} tokens  ({p5_chars:,} chars)")
    print(f"  TOTAL P5:      {p5:>8,} tokens")
    print(f"  Assumption: ~5KB of script sprawl guard updates")
    print()

    # --- Grand Total ---
    total_input = p0 + p1 + p2 + p3 + p4 + p5
    reserved_output = est.budget.DEFAULT_RESERVED_OUTPUT
    safety_buffer = est.budget.DEFAULT_SAFETY_BUFFER
    
    # The true context window includes the system prompt, history, files, and output buffers
    baseline_overhead = ASSUMED_SYSTEM_PROMPT_TOKENS + ASSUMED_HISTORY_TOKENS
    grand_total = baseline_overhead + total_input + reserved_output + safety_buffer

    print("=" * 60)
    print(f"ANALYSIS: FULL PLAN (UNPACKED)")
    print(f"  File payload tokens:  {total_input:>8,}")
    print(f"  Agent overhead:       {baseline_overhead:>8,} (System + History)")
    print(f"  Grand total:          {grand_total:>8,}")
    print(f"  Status:               {est._determine_status_action(grand_total)[0].upper()}")
    print("=" * 60)

    # High-Density Packing Analysis
    # Wave 1: P0 (Cleanup) + P1 (Inventory) + P2 (Archive) + P4 (CI/Precommit) + P5 (Enforcement)
    w1_input = p0 + p1 + p2 + p4 + p5
    w1_total = baseline_overhead + w1_input + reserved_output + safety_buffer
    w1_status, _ = est._determine_status_action(w1_total)

    # Wave 2: P3 (Extract)
    w2_input = p3
    w2_total = baseline_overhead + w2_input + reserved_output + safety_buffer
    w2_status, _ = est._determine_status_action(w2_total)

    print("\n=== HIGH-DENSITY WAVE PACKING (Target 150-160K) ===")
    print(f"Wave 1 (P0+P1+P2+P4+P5):")
    print(f"  Input tokens:  {w1_input:>8,}")
    print(f"  Total context: {w1_total:>8,}")
    print(f"  Status:        {w1_status.upper()}")

    print(f"\nWave 2 (P3):")
    print(f"  Input tokens:  {w2_input:>8,}")
    print(f"  Total context: {w2_total:>8,}")
    print(f"  Status:        {w2_status.upper()}")
    print("=" * 60)

    # Per-phase summary table for plan
    print()
    print("| Phase | Tokens | Chars | Assumption |")
    print("|---|---|---|---|")
    print(f"| P0 Token Optimization | {p0:,} | {len(plan_content) + len(precommit_content):,} | Plan file + pre-commit config |")
    print(f"| P1 Inventory | {p1:,} | {manifest_chars:,} | 644 files × 200 chars/entry |")
    print(f"| P2 Archive | {p2:,} | {mv_chars + hitl_chars:,} | 90 moves + 5 HITL batches |")
    print(f"| P3 Extract | {p3:,} | {extract_chars:,} | 20 files × 300 lines × 40 chars |")
    print(f"| P4 CI Integration | {p4:,} | {wf_chars + len(precommit_content):,} | {wf_count} workflows + pre-commit |")
    print(f"| P5 Enforcement | {p5:,} | {p5_chars:,} | ~5KB script updates |")
    print(f"| **Total** | **{grand_total:,}** | — | incl. {baseline_overhead:,} overhead + {reserved_output:,} output + {safety_buffer:,} buffer |")

if __name__ == "__main__":
    main()
