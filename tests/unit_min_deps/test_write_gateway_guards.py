"""Unit tests for write gateway guards (RCA Phase 5).

Tests write amplification detector, size cap, and mutation entropy cap.
"""

import tempfile
from pathlib import Path

import pytest

from agentic_core.L2_execution.tools.write_gateway import (
    MAX_GROWTH_RATIO,
    MAX_WRITE_BYTES,
    MutationEntropyError,
    WriteAmplificationError,
    WriteSizeCapError,
    get_prohibition_hit_count,
    record_prohibition_hit,
    write_text,
)


@pytest.mark.unit_min_deps
def test_write_size_cap_exceeded():
    """Test that writes exceeding MAX_WRITE_BYTES raise WriteSizeCapError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "large.txt"
        # Attempt to write 11 MB (exceeds 10 MB cap)
        large_content = "x" * (MAX_WRITE_BYTES + 1024)

        with pytest.raises(WriteSizeCapError) as exc_info:
            write_text(target, large_content)

        assert exc_info.value.proposed_bytes == len(large_content.encode("utf-8"))
        assert exc_info.value.max_bytes == MAX_WRITE_BYTES
        assert "WRITE_SIZE_CAP_EXCEEDED" in str(exc_info.value)


@pytest.mark.unit_min_deps
def test_write_amplification_detected():
    """Test that writes exceeding MAX_GROWTH_RATIO raise WriteAmplificationError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "grow.txt"
        # Create a small file
        original_content = "small"
        write_text(target, original_content)

        # Attempt to write 3x larger content (exceeds 2.0x growth ratio)
        amplified_content = "x" * (len(original_content) * 3)

        with pytest.raises(WriteAmplificationError) as exc_info:
            write_text(target, amplified_content)

        assert exc_info.value.original_bytes == len(original_content.encode("utf-8"))
        assert exc_info.value.proposed_bytes == len(amplified_content.encode("utf-8"))
        assert exc_info.value.growth_ratio > MAX_GROWTH_RATIO
        assert "WRITE_AMPLIFICATION_DETECTED" in str(exc_info.value)


@pytest.mark.unit_min_deps
def test_write_amplification_boundary_cases():
    """Test write amplification boundary cases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Case 1: Missing file (original_bytes=0) still enforces size cap
        target = Path(tmpdir) / "new.txt"
        large_content = "x" * (MAX_WRITE_BYTES + 1024)

        with pytest.raises(WriteSizeCapError):
            write_text(target, large_content)

        # Case 2: Growth ratio exactly at threshold should pass
        target2 = Path(tmpdir) / "boundary.txt"
        original = "x" * 1000
        write_text(target2, original)

        # 2.0x growth should pass (boundary)
        grown = "x" * 2000
        write_text(target2, grown)  # Should not raise

        # Case 3: Growth ratio over threshold should fail (relative to current file)
        # Current file is 2000 bytes, so 4200 bytes = 2.1x growth
        grown_over = "x" * 4200
        with pytest.raises(WriteAmplificationError):
            write_text(target2, grown_over)


@pytest.mark.unit_min_deps
def test_mutation_entropy_cap():
    """Test that substitution_count > expected_max raises MutationEntropyError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "entropy.txt"

        # Attempt to write with substitution_count=5, expected_max=1
        with pytest.raises(MutationEntropyError) as exc_info:
            write_text(
                target,
                "content",
                substitution_count=5,
                expected_max_substitutions=1,
            )

        assert exc_info.value.substitution_count == 5
        assert exc_info.value.expected_max == 1
        assert "MUTATION_ENTROPY_EXCEEDED" in str(exc_info.value)


@pytest.mark.unit_min_deps
def test_mutation_entropy_default_expected_max():
    """Test that expected_max defaults to 1 when not provided."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "entropy_default.txt"

        # substitution_count=2 with no expected_max should default to expected_max=1
        with pytest.raises(MutationEntropyError) as exc_info:
            write_text(target, "content", substitution_count=2)

        assert exc_info.value.expected_max == 1


@pytest.mark.unit_min_deps
def test_mutation_entropy_pass():
    """Test that substitution_count <= expected_max passes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "entropy_pass.txt"

        # substitution_count=1, expected_max=1 should pass
        write_text(
            target,
            "content",
            substitution_count=1,
            expected_max_substitutions=1,
        )

        assert target.read_text() == "content"


@pytest.mark.unit_min_deps
def test_prohibition_loop_signal():
    """Test prohibition-loop signal aggregator."""
    # First hit: no warning
    record_prohibition_hit("L0", "json.dump", "/path/to/file.json")
    assert get_prohibition_hit_count("L0", "json.dump", "/path/to/file.json") == 1

    # Second hit: warning emitted (check via count, not log capture)
    record_prohibition_hit("L0", "json.dump", "/path/to/file.json")
    assert get_prohibition_hit_count("L0", "json.dump", "/path/to/file.json") == 2

    # Third hit: count increments but no additional warning
    record_prohibition_hit("L0", "json.dump", "/path/to/file.json")
    assert get_prohibition_hit_count("L0", "json.dump", "/path/to/file.json") == 3

    # Different key: independent counter
    record_prohibition_hit("L0", "write_text", "/other/path.txt")
    assert get_prohibition_hit_count("L0", "write_text", "/other/path.txt") == 1
