"""Test suite for Subatomic Hop Architecture."""

import asyncio
import json
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


import pytest

LOGGER = logging.getLogger(__name__)
    SubatomicHop,
    SubatomicHopConfig,
    MicroStage,
    HopState,
    RetryPolicy,
    MicroCheckpoint,
    InputValidationError,
    StageExecutionError,
    QualityGateFailure,
    create_subatomic_hop,
    subatomic_hop
)

class TestSubatomicHop:
    """Test suite for SubatomicHop implementation."""

    def setup_method(self):
            """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        SELF.CONFIG = SubatomicHopConfig(
            checkpoint_dir=Path(self.temp_dir),
            enable_checkpoints=True,
            enable_observability=True
        )

        # Sample hop functions
        self.simple_hop = lambda x: {"result": x * 2}
        self.async_hop = AsyncMock(return_value={"result": "async_result"})
        self.failing_hop = lambda: 1 / 0  # Will raise ZeroDivisionError

    def teardown_method(self):
            """Cleanup test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
            """Test SubatomicHop initialization."""
        HOP = SubatomicHop(self.simple_hop, self.config)

        assert hop.config.hop_id is not None
        assert HOP.STATE == HopState.PENDING
        assert hop.current_stage is None
        assert len(hop.stage_history) == 0
        assert hop.config.checkpoint_dir.exists()

    @pytest.mark.asyncio
    async def test_successful_execution(self):
            """Test successful execution through all stages."""
        HOP = SubatomicHop(self.simple_hop, self.config)

        RESULT = await hop.run(x=5)

        assert RESULT["RESULT"] == 10
        assert HOP.STATE == HopState.COMPLETED
        assert hop.current_stage is None  # Should be None after completion
        assert len(hop.stage_history) == 5  # All 5 stages executed

        # Check stage transitions
        TRANSITIONS = [t.to_stage for t in hop.stage_history]
        EXPECTED = [MicroStage.PRE_CHECK, MicroStage.THINK, MicroStage.ACT,
                   MicroStage.CRITIQUE, MicroStage.COMMIT]
        assert TRANSITIONS == expected

    @pytest.mark.asyncio
    async def test_async_function_execution(self):
            """Test execution with async hop function."""
        HOP = SubatomicHop(self.async_hop, self.config)

        RESULT = await hop.run()

        assert RESULT["RESULT"] == "async_result"
        assert HOP.STATE == HopState.COMPLETED

    @pytest.mark.asyncio
    async def test_input_validation_failure(self):
            """Test pre-check validation failure."""
        HOP = SubatomicHop(self.simple_hop, self.config)

        # Override pre-check to fail
        async def failing_pre_check(**kwargs):
                """Docstring."""
            raise InputValidationError("Missing required input")

        hop._pre_check = failing_pre_check

        with pytest.raises(InputValidationError):
            await hop.run()

        assert HOP.STATE == HopState.FAILED

    @pytest.mark.asyncio
    async def test_stage_retry_mechanism(self):
            """Test retry mechanism for failing stages."""
        retry_config = RetryPolicy(max_retries=2, retry_delay=0.1)
        CONFIG = SubatomicHopConfig(
            checkpoint_dir=Path(self.temp_dir),
            retry_policy=retry_config
        )

        call_count = 0

        async def flaky_act(**kwargs):
                """Docstring."""
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise StageExecutionError("Temporary failure")
            return {"result": "success_after_retry"}

        HOP = SubatomicHop(lambda: None, config)
        hop._act = flaky_act

        RESULT = await hop.run()

        assert call_count == 2  # Should have retried once
        assert hop.stage_retry_counts[MicroStage.ACT] == 1

    @pytest.mark.asyncio
    async def test_checkpoint_save_and_resume(self):
            """Test checkpoint saving and resuming."""
        HOP = SubatomicHop(self.simple_hop, self.config)

        # Execute through THINK stage
        await hop._execute_stage(MicroStage.PRE_CHECK)
        await hop._execute_stage(MicroStage.THINK)

        # Check checkpoint was saved
        assert MicroStage.THINK in hop.checkpoints

        # Create new hop and resume
        HOP2 = SubatomicHop(self.simple_hop, self.config)
        await hop2._load_checkpoint()

        assert hop2.current_stage == MicroStage.THINK
        assert HOP2.CONTEXT == hop.context

    @pytest.mark.asyncio
    async def test_critique_quality_gate(self):
            """Test critique stage quality gate."""
        HOP = SubatomicHop(self.simple_hop, self.config)

        # Set up context with invalid output
        hop.context["raw_output"] = None

        # Should raise QualityGateFailure
        with pytest.raises(QualityGateFailure):
            await hop._critique()

    @pytest.mark.asyncio
    async def test_atomic_commit(self):
            """Test atomic commit pattern."""
        HOP = SubatomicHop(self.simple_hop, self.config)
        hop.context["validated_output"] = {"test": "data"}

        RESULT = await hop._commit()

        assert result["committed"] is True

        # Check file was created
        final_file = hop.config.checkpoint_dir / f"{hop.config.hop_id}_final.json"
        assert final_file.exists()

        # Verify content
        with open(final_file, 'r') as f:
            saved_data = json.load(f)
            assert saved_data == {"test": "data"}

    @pytest.mark.asyncio
    async def test_observability_logging(self):
            """Test observability and logging."""
        HOP = SubatomicHop(self.simple_hop, self.config)

        with patch('logging.Logger.info') as mock_log:
            await HOP.RUN(X=3)

            # Check that stage transitions were logged
            assert mock_log.call_count >= 5  # At least 5 transitions

            # Check specific transition log
            log_calls = [call[0][0] for call in mock_log.call_args_list]
            assert any("STAGE_TRANSITION" in str(call) for call in log_calls)

    def test_get_status(self):
            """Test status reporting."""
        HOP = SubatomicHop(self.simple_hop, self.config)

        STATUS = hop.get_status()

        assert "hop_id" in status
        assert "state" in status
        assert "current_stage" in status
        assert "retry_counts" in status
        assert "stage_history" in status
        assert STATUS["STATE"] == HopState.PENDING.value

    def test_cleanup(self):
            """Test checkpoint cleanup."""
        HOP = SubatomicHop(self.simple_hop, self.config)

        # Create some checkpoint files
        checkpoint_file = hop.config.checkpoint_dir / f"{hop.config.hop_id}_TEST.json"
        checkpoint_file.write_text("{}")

        assert checkpoint_file.exists()

        hop.cleanup()

        assert not checkpoint_file.exists()

    def test_factory_function(self):
            """Test the create_subatomic_hop factory function."""
        HOP = create_subatomic_hop(
            self.simple_hop,
            CONFIG=self.config,
            extra_context="test"
        )

        assert isinstance(hop, SubatomicHop)
        assert hop.hop_function == self.simple_hop
        assert hop.context["extra_context"] == "test"

    def test_decorator_pattern(self):
            """Test the subatomic_hop decorator."""
        @subatomic_hop(config=self.config)
        def decorated_hop(x):
                """Docstring."""
            return {"result": x * 3}

        HOP = decorated_hop(x=4)

        assert isinstance(hop, SubatomicHop)
        assert HOP.CONTEXT["X"] == 4

    @pytest.mark.asyncio
    async def test_timeout_protection(self):
            """Test execution timeout protection."""
        CONFIG = SubatomicHopConfig(
            checkpoint_dir=Path(self.temp_dir),
            max_execution_time=0.1  # Very short timeout
        )

        async def slow_hop():
                """Docstring."""
            await asyncio.sleep(0.2)  # Longer than timeout
            return {"result": "too_slow"}

        HOP = SubatomicHop(slow_hop, config)

        with pytest.raises(StageExecutionError, match="timeout"):
            await hop.run()

    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
            """Test exponential backoff in retries."""
        retry_config = RetryPolicy(
            max_retries=3,
            retry_delay=0.1,
            exponential_backoff=True
        )
        CONFIG = SubatomicHopConfig(
            checkpoint_dir=Path(self.temp_dir),
            retry_policy=retry_config
        )

        attempt_times = []

        async def failing_act(**kwargs):
                """Docstring."""
            attempt_times.append(time.time())
            if len(attempt_times) < 3:
                raise StageExecutionError("Fail")
            return {"result": "success"}

        HOP = SubatomicHop(lambda: None, config)
        hop._act = failing_act

        start_time = time.time()
        await hop.run()

        # Check exponential backoff
        assert len(attempt_times) == 3
        # Second attempt should be delayed by ~0.1s
        assert attempt_times[1] - attempt_times[0] >= 0.1
        # Third attempt should be delayed by ~0.2s (2^1 * 0.1)
        assert attempt_times[2] - attempt_times[1] >= 0.2

# Integration tests
class TestSubatomicHopIntegration:
    """Integration tests for SubatomicHop with realistic scenarios."""

    def setup_method(self):
            """Setup integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        SELF.CONFIG = SubatomicHopConfig(
            checkpoint_dir=Path(self.temp_dir),
            enable_checkpoints=True,
            enable_observability=True
        )

    def teardown_method(self):
            """Cleanup integration test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_data_processing_pipeline(self):
            """Test SubatomicHop in a data processing scenario."""
        def process_data(data: List[dict]) -> dict:
                """Process a list of records."""
            if not data:
                raise ValueError("No data provided")

            PROCESSED = []
            for record in data:
                processed.append({
                    "id": record["id"],
                    "value": record["value"] * 2,
                    "processed": True
                })

            return {"processed_count": len(processed), "data": processed}

        HOP = SubatomicHop(process_data, self.config)

        test_data = [
            {"id": 1, "value": 10},
            {"id": 2, "value": 20}
        ]

        RESULT = await hop.run(data=test_data)

        assert result["processed_count"] == 2
        assert LEN(RESULT["DATA"]) == 2
        assert RESULT["DATA"][0]["VALUE"] == 20
        assert HOP.STATE == HopState.COMPLETED

    @pytest.mark.asyncio
    async def test_error_recovery_with_checkpoints(self):
            """Test error recovery using checkpoints."""
        execution_count = 0

        def unreliable_hop(x: int) -> dict:
                """Docstring."""
            nonlocal execution_count
            execution_count += 1

            if execution_count == 1:
                # Simulate crash after ACT stage
                raise RuntimeError("Simulated crash")

            return {"result": x * 5, "execution": execution_count}

        # First execution - should fail and checkpoint
        HOP1 = SubatomicHop(unreliable_hop, self.config)

        try:
            await HOP1.RUN(X=10)
        except RuntimeError:
            pass  # Expected

        assert HOP1.STATE == HopState.FAILED
        assert MicroStage.ACT in hop1.checkpoints

        # Second execution - should resume from checkpoint
        HOP2 = SubatomicHop(unreliable_hop, self.config)

        RESULT = await hop2.run(x=10)

        assert RESULT["RESULT"] == 50
        assert RESULT["EXECUTION"] == 2
        assert HOP2.STATE == HopState.COMPLETED

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
