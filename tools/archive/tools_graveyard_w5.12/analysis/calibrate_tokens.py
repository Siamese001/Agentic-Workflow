#!/usr/bin/env python3
"""
Calibrate token usage for SWE 1.5 128K context window.
"""

import pathlib

import tiktoken


def estimate_tokens(text: str) -> int:
    """Estimate tokens using GPT-4 tokenizer."""
    enc = tiktoken.encoding_for_model("gpt-4")
    return len(enc.encode(text))


def calibrate_file_sizes():
    """Calculate actual token requirements."""
    # Standard template
    template = '''import pytest

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes

@pytest.mark.unit
class TestClassName:
    """Test class placeholder."""

    def test_placeholder_1(self):
        """Placeholder test 1."""
        assert True

    def test_placeholder_2(self):
        """Placeholder test 2."""
        assert True

    def test_placeholder_3(self):
        """Placeholder test 3."""
        assert True
'''

    template_tokens = estimate_tokens(template)
    print(f"Template tokens: {template_tokens}")

    # Sample actual broken files
    tests_dir = pathlib.Path("tests")
    sample_sizes = []

    count = 0
    for f in sorted(tests_dir.rglob("test_*.py")):
        if count >= 20:  # Sample 20 files
            break
        if "archive" in str(f).lower():
            continue

        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            import ast

            ast.parse(content)
            continue
        except SyntaxError:
            # This is a broken file
            tokens = estimate_tokens(content)
            sample_sizes.append(tokens)
            count += 1
        except Exception:
            continue

    if sample_sizes:
        avg_file_tokens = sum(sample_sizes) / len(sample_sizes)
        max_file_tokens = max(sample_sizes)
        min_file_tokens = min(sample_sizes)

        print(f"\nSample broken files ({len(sample_sizes)}):")
        print(f"  Average tokens per file: {avg_file_tokens:.0f}")
        print(f"  Max tokens per file: {max_file_tokens:.0f}")
        print(f"  Min tokens per file: {min_file_tokens:.0f}")

        # Calculate requirements for different batch sizes
        print("\nToken requirements (including template):")
        for batch_size in [10, 20, 30, 40, 50, 75, 100]:
            # We need original content + template + overhead for operations
            total_tokens = (
                (avg_file_tokens * batch_size) + (template_tokens * batch_size) + 5000
            )  # 5K overhead
            print(
                f"  {batch_size:3d} files: ~{total_tokens:7.0f} tokens ({total_tokens / 128000:.1%} of context)"
            )

        # Find optimal batch size
        print("\nOptimal batch sizes for 128K context:")
        # Reserve 20% for safety and operations
        usable_context = 128000 * 0.8
        for batch_size in [10, 20, 30, 40, 50, 75, 100]:
            total_tokens = (avg_file_tokens * batch_size) + (template_tokens * batch_size) + 5000
            if total_tokens <= usable_context:
                print(f"  ✓ {batch_size} files: {total_tokens:.0f} tokens")
            else:
                print(f"  ✗ {batch_size} files: {total_tokens:.0f} tokens (exceeds limit)")


if __name__ == "__main__":
    calibrate_file_sizes()
