"""
Unit tests for L6 Observability Outcome Logger - deterministic outcome recording.
"""

import pytest

@pytest.mark.unit
class TestOutcomeLogger:
    """Test deterministic OutcomeLogger implementation."""

    def test_outcome_logger_initialization(self):
        """Test OutcomeLogger initializes correctly."""
        from agentic_core.L6_observation.outcome_logger import OutcomeLogger

        logger = OutcomeLogger()

        assert logger is not None
        assert hasattr(logger, "log_outcome")
        assert hasattr(logger, "get_outcomes")

    def test_log_outcome_records_event(self):
        """Test log_outcome records an event."""
        from agentic_core.L6_observation.outcome_logger import OutcomeLogger

        logger = OutcomeLogger()

        # Log a test outcome
        logger.log_outcome(
            event_type="test_event",
            outcome="success",
            metadata={"test": "value"},
        )

        # Retrieve outcomes
        outcomes = logger.get_outcomes()

        assert len(outcomes) == 1
        assert outcomes[0]["event_type"] == "test_event"
        assert outcomes[0]["outcome"] == "success"
        assert outcomes[0]["metadata"]["test"] == "value"

    def test_get_outcomes_returns_copy(self):
        """Test get_outcomes returns a copy, not reference."""
        from agentic_core.L6_observation.outcome_logger import OutcomeLogger

        logger = OutcomeLogger()

        logger.log_outcome("test", "success")

        outcomes1 = logger.get_outcomes()
        outcomes2 = logger.get_outcomes()

        # Should be equal but not the same object
        assert outcomes1 == outcomes2
        assert outcomes1 is not outcomes2

    def test_multiple_outcomes_ordered(self):
        """Test multiple outcomes are recorded in order."""
        from agentic_core.L6_observation.outcome_logger import OutcomeLogger

        logger = OutcomeLogger()

        # Log multiple outcomes
        logger.log_outcome("event1", "success")
        logger.log_outcome("event2", "failure")
        logger.log_outcome("event3", "success")

        outcomes = logger.get_outcomes()

        assert len(outcomes) == 3
        assert outcomes[0]["event_type"] == "event1"
        assert outcomes[1]["event_type"] == "event2"
        assert outcomes[2]["event_type"] == "event3"

    def test_clear_outcomes(self):
        """Test clearing outcomes."""
        from agentic_core.L6_observation.outcome_logger import OutcomeLogger

        logger = OutcomeLogger()

        logger.log_outcome("test", "success")
        assert len(logger.get_outcomes()) == 1

        # Clear if method exists
        if hasattr(logger, "clear_outcomes"):
            logger.clear_outcomes()
            assert len(logger.get_outcomes()) == 0
