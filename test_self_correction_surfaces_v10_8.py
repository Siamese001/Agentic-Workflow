import pytest

from self_correction_surfaces import SelfCorrectionSurface, should_retry


def test_should_retry_qa_pending():
    state = {}
    last_result = {
        "qa_report": {
            "findings": [
                {"status": "pending", "detail": "needs review"},
                {"status": "pass", "detail": "ok"},
            ]
        }
    }

    assert should_retry(SelfCorrectionSurface.QA_RECHECK, state, last_result) is True


def test_should_retry_qa_no_pending():
    state = {}
    last_result = {
        "qa_report": {
            "findings": [
                {"status": "pass", "detail": "good"},
                {"status": "pass", "detail": "ok"},
            ]
        }
    }

    assert should_retry(SelfCorrectionSurface.QA_RECHECK, state, last_result) is False


def test_should_retry_other_surfaces_false():
    state = {}
    last_result = {}
    for surface in (
        SelfCorrectionSurface.RAG_RETRY,
        SelfCorrectionSurface.DRAFT_RETRY,
        SelfCorrectionSurface.STRATEGY_REPLAN,
    ):
        assert should_retry(surface, state, last_result) is False
