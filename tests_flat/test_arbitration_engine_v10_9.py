from core_v10_7.models import QAOutputModel
from core_v10_7.services import ArbitrationEngine


def test_arbitration_engine_records_decisions():
    engine = ArbitrationEngine()
    options = {
        "opt1": QAOutputModel(answer="a1"),
        "opt2": QAOutputModel(answer="a2"),
    }
    choice = engine.decide("strategy_post_plan", options)
    assert choice in options
    assert engine.history[0]["stage"] == "strategy_post_plan"
    assert set(engine.history[0]["options"]) == set(options.keys())
