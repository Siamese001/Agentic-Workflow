"""Test enforcement for .windsurfrules budget and evidence gate invariants."""


def test_windsurfrules_contains_execution_evidence_gate():
    """Ensure .windsurfrules contains execution evidence gate rule."""
    with open(".windsurfrules", encoding="utf-8") as f:
        content = f.read()

    # Check for evidence gate rule
    assert "## -2. Execution Evidence Gate (ANTI-SPIN LOCK)" in content
    assert "Tee-Object -FilePath $E -Append" in content
    assert "2>&1" in content
    assert "pytest commands MUST show tests EXECUTED" in content
    assert "no tests ran" in content
    assert "AUTOMATIC FAIL" in content


def test_windsurfrules_contains_wave_phase_budget():
    """Ensure .windsurfrules contains wave/phase budget rule."""
    with open(".windsurfrules", encoding="utf-8") as f:
        content = f.read()

    # Check for budget rule
    assert "## -3. Wave/Phase Budget Lock (ANTI-INFINITE LOOP)" in content
    assert "Each wave MUST have evidence capture" in content
    assert "Phase MUST complete with proper evidence documentation" in content
    assert "IMMEDIATE FAIL" in content


def test_windsurfrules_contains_stop_discipline():
    """Ensure .windsurfrules contains STOP discipline requirement."""
    with open(".windsurfrules", encoding="utf-8") as f:
        content = f.read()

    # Check for STOP discipline
    assert "evidence file path + commit hash + STOP" in content
    assert "Chat output MUST be limited to" in content
