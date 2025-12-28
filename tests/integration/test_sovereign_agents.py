import pytest
from pathlib import Path
from agentic_core.L3_orchestration.healing.territory_healer_agent import TerritoryHealerAgent

@pytest.fixture
def mock_canon(tmp_path):
    # Setup a mini-canon structure
    root = tmp_path / "root"
    (root / "agentic_core/L3_orchestration/scripts").mkdir(parents=True)
    return root

def test_healer_logic(mock_canon):
    # Place a 'stray' file in the wrong place
    stray = mock_canon / "agentic_core/stray_logic.py"
    stray.write_text("print('I am drift')")
    
    # Run the healer
    ctx = type('Ctx', (), {"report_list": []})()
    healer = TerritoryHealerAgent(mock_canon, ctx)
    actions = healer.find_all_stray()
    
    # VERDICT: It must detect the stray and suggest a move to 'scripts'
    assert len(actions) > 0
    assert actions[0]['action'] == 'move'
    assert 'scripts' in actions[0]['target']
