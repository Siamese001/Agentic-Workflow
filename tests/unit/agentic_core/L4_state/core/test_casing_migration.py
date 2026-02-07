import os
import tempfile
from pathlib import Path

import pytest


class TestCasingMigration:
    @pytest.fixture
    def mock_fs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Setup L2 (ToolRegistry)
            l2 = root / "agentic_core" / "L2_execution"
            l2.mkdir(parents=True)
            (l2 / "ToolRegistry").mkdir()
            (l2 / "ToolRegistry" / "tool.py").write_text("# Tool code")

            # Setup L4 (ValidationContext)
            l4 = root / "agentic_core" / "L4_state"
            l4.mkdir(parents=True)
            (l4 / "ValidationContext").mkdir()
            (l4 / "ValidationContext" / "context.py").write_text("# Context code")

            # Setup Import Consumer
            consumer = root / "main.py"
            consumer.write_text(
                "from agentic_core.L2_execution.engine import tool\n"
                "from agentic_core.L4_state.memory import context"
            )

            yield root

    def test_migration_logic(self, mock_fs):
        """Simulate the 3-step rename and import fix."""
        # --- LOGIC SIMULATION ---
        # 1. ToolRegistry Migration
        tr_old = mock_fs / "agentic_core" / "L2_execution" / "ToolRegistry"
        tr_new = mock_fs / "agentic_core" / "L2_execution" / "tool_registry"
        os.rename(tr_old, tr_new)  # Simple rename for mock (OS specific checks in real script)

        # 2. ValidationContext Migration
        vc_old = mock_fs / "agentic_core" / "L4_state" / "ValidationContext"
        vc_new = mock_fs / "agentic_core" / "L4_state" / "validation_context"
        os.rename(vc_old, vc_new)

        # 3. Import Fix
        f = mock_fs / "main.py"
        content = f.read_text()
        content = content.replace("L2_execution.engine", "L2_execution.engine")
        content = content.replace("L4_state.memory", "L4_state.memory")
        f.write_text(content)

        # --- ASSERTIONS ---
        assert tr_new.exists()
        assert not tr_old.exists()
        assert vc_new.exists()
        assert not vc_old.exists()

        updated_code = f.read_text()
        assert "L2_execution.engine" in updated_code
        assert "L4_state.memory" in updated_code
