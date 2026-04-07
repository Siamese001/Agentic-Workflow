#!/usr/bin/env python3
"""
Advanced token optimizer with dual-mode estimation.
Uses both exact OpenAI API counting and local fallback estimation.
Builds realistic message payloads for accurate token accounting.
"""

import json
import logging
import os
import sys
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

# ============================================================
# LOCAL TOKEN ESTIMATION (3.7 chars/token heuristic)
# ============================================================


def rough_token_estimate(text: str) -> int:
    """
    Local token estimator using ~3.7 chars/token heuristic.
    More accurate than /4, no external dependencies.
    """
    if not text:
        return 0
    return int(len(text) / 3.7)


# ============================================================
# PHASE PAYLOAD BUILDER (CRITICAL FIX)
# ============================================================


def build_phase_payload(phase: dict[str, Any]) -> list[dict[str, str]]:
    """
    Builds REALISTIC message payload instead of "xxxx" filler.
    """

    messages = []

    # System prompt (static)
    if "system" in phase:
        messages.append({"role": "system", "content": phase["system"]})

    # User content
    content_blocks = []

    for section in phase.get("sections", []):
        content = section.get("content", "")

        if section.get("type") == "code":
            content_blocks.append(f"```python\n{content}\n```")
        elif section.get("type") == "json":
            content_blocks.append(json.dumps(content))
        else:
            content_blocks.append(content)

    full_content = "\n\n".join(content_blocks)

    messages.append({"role": "user", "content": full_content})

    return messages


# ============================================================
# PHASE TOKEN ESTIMATION
# ============================================================


def estimate_phase_tokens(phase: dict[str, Any]) -> dict[str, Any]:
    """
    Returns token count using local estimation only.
    Simplified approach without OpenAI API dependency.
    """

    payload = build_phase_payload(phase)

    # Use local estimation for all content
    joined = "\n".join(m["content"] for m in payload)
    tokens = rough_token_estimate(joined)

    return {
        "id": phase.get("id"),
        "incremental_input_tokens": tokens,
        "estimation_method": "local_3.7_chars_per_token",
    }


# ============================================================
# PLAN RUNNER (FULL REPORT)
# ============================================================


def run_plan(phases: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Produces structured token report aligned with OpenAI request model.
    """

    phase_results = []
    total_incremental = 0

    for phase in phases:
        result = estimate_phase_tokens(phase)
        phase_results.append(result)
        total_incremental += result["incremental_input_tokens"]

    return {"phases": phase_results, "total_incremental_tokens": total_incremental, "num_phases": len(phases)}


# ============================================================
# LEGACY COMPATIBILITY & FILE READING
# ============================================================


def chars(path):
    """Safely reads characters from a file path."""
    fp = os.path.join(ROOT, path)
    if os.path.isfile(fp):
        try:
            with open(fp, encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            logging.warning(f"Failed to read {fp}: {e}")
            return ""
    return ""


def build_legacy_phase(id: str, name: str, content: str, content_type: str = "text") -> dict[str, Any]:
    """Builds phase dict in new format from legacy content."""
    return {"id": id, "name": name, "sections": [{"type": content_type, "content": content}]}


def main():
    print("=== Advanced Token Optimizer (Local Estimation Only) ===")
    print("Using 3.7 chars/token heuristic - no external dependencies")
    print()

    # Build phases using new realistic payload approach
    phases = []

    # --- Phase 0: Token Optimization & Pre-Commit Cleanup ---
    plan_content = chars("docs/reports/plans/repo-hygiene-precommit-optimization-e0f719.md")
    precommit_content = chars(".pre-commit-config.yaml")

    p0_phase = build_legacy_phase(
        "P0",
        "Token Optimization & Pre-Commit Cleanup",
        f"Plan Content:\n{plan_content}\n\nPre-commit Config:\n{precommit_content}",
        "text",
    )
    phases.append(p0_phase)

    # --- Phase 1: Inventory & HITL Classification ---
    # Simulate manifest content
    manifest_entries = [
        {"path": f"file_{i}.py", "classification": "keep", "reason": "core logic"} for i in range(644)
    ]
    manifest_json = json.dumps(manifest_entries, indent=2)

    p1_phase = build_legacy_phase("P1", "Inventory & HITL Classification", manifest_json, "json")
    phases.append(p1_phase)

    # --- Phase 2: Archive with HITL Confirmation ---
    # Simulate git mv commands and HITL prompts
    mv_commands = "\n".join([f"git mv old_path_{i}.py archive/" for i in range(90)])
    hitl_prompts = "\n\n".join(
        [f"Batch {i + 1}: Please confirm these archive operations..." for i in range(5)],
    )

    p2_phase = build_legacy_phase(
        "P2",
        "Archive with HITL Confirmation",
        f"Git MV Commands:\n{mv_commands}\n\nHITL Prompts:\n{hitl_prompts}",
        "text",
    )
    phases.append(p2_phase)

    # --- Phase 3: Extract Reusable Capabilities ---
    # Simulate source file content
    source_files = []
    for i in range(20):
        source_content = "\n".join([f"def function_{j}():\n    pass" for j in range(300)])
        source_files.append(f"File {i}:\n```python\n{source_content}\n```")

    p3_phase = build_legacy_phase("P3", "Extract Reusable Capabilities", "\n\n".join(source_files), "code")
    phases.append(p3_phase)

    # --- Phase 4: Pre-Commit Tiering & CI Integration ---
    # Read actual workflow files
    wf_dir = os.path.join(ROOT, ".github", "workflows")
    workflow_contents = []

    if os.path.isdir(wf_dir):
        try:
            for f in sorted(os.listdir(wf_dir)):
                if f.endswith((".yml", ".yaml")):
                    content = chars(os.path.join(".github", "workflows", f))
                    workflow_contents.append(f"{f}:\n```yaml\n{content}\n```")
        except OSError as e:
            logging.error(f"Error accessing workflows directory: {e}")

    all_workflows = "\n\n".join(workflow_contents)
    p4_phase = build_legacy_phase(
        "P4",
        "Pre-Commit Tiering & CI Integration",
        f"Workflows:\n{all_workflows}\n\nPre-commit Config:\n{precommit_content}",
        "text",
    )
    phases.append(p4_phase)

    # --- Phase 5: Territory Boundary Enforcement ---
    # Simulate script updates
    script_updates = "# Script sprawl guard updates\n" + "\n".join([f"update_{i}()" for i in range(100)])

    p5_phase = build_legacy_phase("P5", "Territory Boundary Enforcement", script_updates, "code")
    phases.append(p5_phase)

    # Run the advanced token estimation
    results = run_plan(phases)

    # Display results
    print("Token Estimation Results:")
    print("=" * 80)
    for phase_result in results["phases"]:
        print(f"Phase {phase_result['id']}:")
        print(f"  Incremental Input Tokens: {phase_result['incremental_input_tokens']:>8,}")
        print(f"  Estimation Method: {phase_result['estimation_method']}")
        print()

    # Calculate total context with overhead
    DEFAULT_SHARED_PREFIX_TOKENS = 4000
    DEFAULT_HISTORY_TOKENS = 2000
    GENERATION_RESERVE_TOKENS = 25000
    SAFETY_BUFFER_TOKENS = 5000

    total_context = (
        DEFAULT_SHARED_PREFIX_TOKENS
        + DEFAULT_HISTORY_TOKENS
        + results["total_incremental_tokens"]
        + GENERATION_RESERVE_TOKENS
        + SAFETY_BUFFER_TOKENS
    )

    print("=" * 80)
    print("SUMMARY:")
    print(f"  Total Incremental Input: {results['total_incremental_tokens']:>8,}")
    print(f"  Shared Prefix (System+Tools): {DEFAULT_SHARED_PREFIX_TOKENS:>8,}")
    print(f"  History Tokens: {DEFAULT_HISTORY_TOKENS:>8,}")
    print(f"  Generation Reserve: {GENERATION_RESERVE_TOKENS:>8,}")
    print(f"  Safety Buffer: {SAFETY_BUFFER_TOKENS:>8,}")
    print(f"  TOTAL CONTEXT: {total_context:>8,}")

    status = "GREEN" if total_context <= 180000 else "YELLOW" if total_context <= 200000 else "RED"
    print(f"  Status: {status}")
    print("=" * 80)

    # Wave packing analysis using new packer
    from tools.adg.wave_packer import pack_waves, summarize_wave

    waves = pack_waves(results["phases"])

    print("\nWAVE PACKING ANALYSIS:")
    print("=" * 80)
    for i, wave in enumerate(waves):
        summary = summarize_wave(wave)
        print(f"Wave {i + 1}:")
        print(f"  Phases: {', '.join(summary['phase_ids'])}")
        print(f"  Incremental Tokens: {summary['incremental_tokens']:>8,}")
        print(f"  Total Context: {summary['total_context_tokens']:>8,}")
        print(f"  Break Reason: {wave['break_reason']}")
        print()


if __name__ == "__main__":
    main()
