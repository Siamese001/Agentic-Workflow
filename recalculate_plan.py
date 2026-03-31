#!/usr/bin/env python3
"""
Recalibrated plan based on actual token usage.
"""

import pathlib
import tiktoken

def estimate_tokens(text: str) -> int:
    """Estimate tokens using GPT-4 tokenizer."""
    enc = tiktoken.encoding_for_model("gpt-4")
    return len(enc.encode(text))

def recalculate_plan():
    """Recalculate based on actual measurements."""

    # From calibration:
    avg_file_tokens = 12345
    template_tokens = 137
    context_limit = 128000

    # Reserve 30% for operations, instructions, and safety
    usable_context = context_limit * 0.7  # 89,600 tokens

    print(f"Context Limit: {context_limit:,} tokens")
    print(f"Usable Context (70%): {usable_context:,} tokens")
    print(f"Average file size: {avg_file_tokens:,} tokens")
    print(f"Template size: {template_tokens} tokens")
    print()

    # Calculate optimal batch size
    # Each file needs: original content + new template + overhead
    overhead_per_file = 100  # For instructions, etc.
    total_per_file = avg_file_tokens + template_tokens + overhead_per_file

    optimal_batch = int(usable_context / total_per_file)
    print(f"Tokens needed per file: {total_per_file:,}")
    print(f"Optimal batch size: {optimal_batch} files")
    print()

    # Calculate waves needed
    total_files = 1600
    files_per_wave = optimal_batch
    waves_needed = (total_files + files_per_wave - 1) // files_per_wave

    print(f"Total broken files: {total_files:,}")
    print(f"Files per wave: {files_per_wave}")
    print(f"Waves needed: {waves_needed}")
    print()

    # Wave breakdown
    print("REVISED WAVE PLAN:")
    print("=" * 50)

    wave = 1
    remaining = total_files

    # Directory breakdown
    dirs = [
        ("tests/adg/", 100),
        ("tests/unit/agentic_core/", 200),
        ("tests/unit/apps_lic/", 150),
        ("tests/unit/apps_rg/", 150),
        ("tests/unit/apps_shared/", 100),
        ("tests/unit/validators/", 100),
        ("tests/unit/utils/", 100),
        ("tests/unit_min_deps/", 400),
        ("tests/integration/", 100),
        ("tests/performance/", 100),
        ("Others", 100)
    ]

    for dir_name, count in dirs:
        if remaining <= 0:
            break

        # Split across multiple waves if needed
        while count > 0 and remaining > 0:
            wave_size = min(files_per_wave, count, remaining)
            print(f"Wave {wave:2d}: {dir_name:<25} - {wave_size:3d} files")
            count -= wave_size
            remaining -= wave_size
            wave += 1

    print()
    print("KEY INSIGHTS:")
    print("- Only 6-7 files per prompt (not 200!)")
    print("- ~230 waves needed (not 8)")
    print("- Each wave: ~85K tokens used")
    print("- More manageable but requires more iterations")

if __name__ == '__main__':
    recalculate_plan()
