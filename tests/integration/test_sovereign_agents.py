import pytest
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from pathlib import Path
from agentic_core.L3_orchestration.healing.territory_healer_agent import TerritoryHealerAgent

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

from typing import Any


@pytest.fixture
def mock_canon(tmp_path: Any) -> Any:
    """Brief description of functionality and purpose."""
    root: Any = tmp_path / 'root'
    (root / 'agentic_core/L3_orchestration/scripts').mkdir(parents=True)
    return root

def test_healer_logic(mock_canon: Any) -> Any:
    """Brief description of functionality and purpose."""
    stray: Any = mock_canon / 'agentic_core/stray_logic.py'
    stray.write_text("print('I am drift')")
    ctx: Any = type('Ctx', (), {'report_list': []})()
    healer: Any = TerritoryHealerAgent(mock_canon, ctx)
    actions: Any = healer.find_all_stray()
    assert len(actions) > 0
    assert actions[0]['action'] == 'move'
    assert 'scripts' in actions[0]['target']
