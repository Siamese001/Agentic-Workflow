from src.lic_agentic.agents.k3_message_architect import score_quality


def test_reflexion_improves_score():
    base = score_quality("draft without reflexion", reflexion=False)
    with_reflexion = score_quality("draft with reflexion insights", reflexion=True)
    assert with_reflexion >= base + 1
