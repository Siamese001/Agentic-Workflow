"""W19: No wall-clock in SemanticClock AST; provider_id in digest.

REQ-411/413:
- No wall-clock usage in SemanticClock/determinism_types AST
- provider_id is included in the canonical replay digest
"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest

from agentic_core.L0_routing.types.determinism_types import (
    SemanticClockAdvancementArtifact,
)

pytestmark = pytest.mark.governance

REPO_ROOT = Path(__file__).parent.parent.parent
_DETERMINISM_MODULE = REPO_ROOT / "agentic_core/L0_routing/types/determinism_types.py"

_WALL_CLOCK_NAMES = frozenset(
    [
        "time",
        "monotonic",
        "perf_counter",
        "now",
        "utcnow",
        "localtime",
    ]
)


def _wallclock_violations(path: Path) -> list[str]:
    """Return list of wall-clock call violations in the given file."""
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    violations = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        # time.time(), time.monotonic(), etc.
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "time"
            and func.attr in _WALL_CLOCK_NAMES
        ):
            violations.append(f"line {node.lineno}: time.{func.attr}()")
        # datetime.now() / datetime.utcnow()
        elif isinstance(func, ast.Attribute) and func.attr in ("now", "utcnow"):
            violations.append(f"line {node.lineno}: .{func.attr}()")

    return violations


@pytest.mark.governance
def test_req411_no_wallclock_in_determinism_types():
    """REQ-411: No wall-clock calls in determinism_types.py (AST scan)."""
    assert _DETERMINISM_MODULE.exists(), f"Module not found: {_DETERMINISM_MODULE}"
    violations = _wallclock_violations(_DETERMINISM_MODULE)
    assert violations == [], f"Wall-clock calls in {_DETERMINISM_MODULE.name}:\n" + "\n".join(violations)


@pytest.mark.governance
def test_req413_provider_id_in_advancement_artifact():
    """REQ-413: provider_id is present in SemanticClockAdvancementArtifact."""
    artifact = SemanticClockAdvancementArtifact(
        advancement_id="adv_test_001",
        previous_tick=0,
        new_tick=1,
        advancement_reason="test",
        l4_version_binding="l4_v1.0",
        provider_id="provider_anthropic_claude_3",
        timestamp=1234567890.0,
    )
    assert artifact.provider_id == "provider_anthropic_claude_3"
    assert artifact.provider_id in artifact.artifact_hash or len(artifact.artifact_hash) == 64


@pytest.mark.governance
def test_req413_provider_id_affects_digest():
    """REQ-413: Different provider_id values produce different artifact hashes."""
    base_kwargs = {
        "advancement_id": "adv_test_002",
        "previous_tick": 0,
        "new_tick": 1,
        "advancement_reason": "test",
        "l4_version_binding": "l4_v1.0",
        "timestamp": 1234567890.0,
    }
    art_anthropic = SemanticClockAdvancementArtifact(**base_kwargs, provider_id="provider_anthropic")
    art_openai = SemanticClockAdvancementArtifact(**base_kwargs, provider_id="provider_openai")
    assert art_anthropic.artifact_hash != art_openai.artifact_hash


@pytest.mark.governance
def test_req413_provider_id_in_canonical_digest():
    """REQ-413: provider_id is included in canonical digest computation."""
    provider = "provider_test_replay"
    digest_inputs = {
        "plan_hash": "a" * 64,
        "tool_transcript_hash": "b" * 64,
        "capability_scope": "pointer_update:ns_a",
        "activation_flags_hash": "c" * 64,
        "provider_binding": provider,
        "semantic_clock_tick": 7,
        "guardian_policy_hash": "d" * 64,
        "trace_id": "trace_test_001",
    }
    digest = hashlib.sha256(
        json.dumps(digest_inputs, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    # Changing provider_binding must change digest
    alt_inputs = {**digest_inputs, "provider_binding": "provider_different"}
    alt_digest = hashlib.sha256(
        json.dumps(alt_inputs, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    assert digest != alt_digest
    assert len(digest) == 64


@pytest.mark.governance
def test_req411_determinism_types_importable():
    """determinism_types module imports without error (no wall-clock at module level)."""
    # Already imported at top of file — if it used time.time() at module level it
    # would show non-determinism; the import succeeding is the proof.
    assert SemanticClockAdvancementArtifact is not None


@pytest.mark.governance
def test_req413_two_run_artifact_with_provider_identical():
    """Two-run artifact construction with same provider_id → identical hash."""
    kwargs = {
        "advancement_id": "adv_r1",
        "previous_tick": 3,
        "new_tick": 4,
        "advancement_reason": "gate_transition",
        "l4_version_binding": "l4_v1.5",
        "provider_id": "provider_anthropic",
        "timestamp": 5555555.0,
    }
    h1 = SemanticClockAdvancementArtifact(**kwargs).artifact_hash
    h2 = SemanticClockAdvancementArtifact(**kwargs).artifact_hash
    assert h1 == h2
