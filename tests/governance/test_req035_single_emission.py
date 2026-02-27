"""REQ-035: determinism artifact emitted exactly once per wave."""

from __future__ import annotations

import pytest


@pytest.mark.governance
def test_single_emission_per_wave():
    from agentic_core.determinism.digest_authority import (
        DuplicateDigestViolation,
        digest_authority,
    )

    digest_authority.reset_for_testing()
    emissions = []

    digest_authority.emit_digest("abc123", wave_number=35)
    emissions.append("abc123")

    with pytest.raises(DuplicateDigestViolation):
        digest_authority.emit_digest("abc123", wave_number=35)

    assert len(emissions) == 1
    digest_authority.reset_for_testing()
