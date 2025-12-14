"""Test suite for Subatomic Hop Architecture."""

import asyncio
import json
import logging
import tempfile
from pathlib import Path

import pytest

logger = logging.getLogger(__name__)
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
        self.config = SubatomicHopConfig(
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
        hop = SubatomicHop(self.simple_hop, self.config)

        assert hop.config.hop_id is not None
        assert hop.state == HopState.PENDING
        assert hop.current_stage is None
        assert len(hop.stage_history) == 0
        assert hop.config.checkpoint_dir.exists()

    @pytest.mark.asyncio
    async def test_successful_execution(self):
            """Test successful execution through all stages."""
        hop = SubatomicHop(self.simple_hop, self.config)

        result = await hop.run(x=5)

        assert result["result"] == 10
        assert hop.state == HopState.COMPLETED
        assert hop.current_stage is None  # Should be None after completion
        assert len(hop.stage_history) == 5  # All 5 stages executed

        # Check stage transitions
        transitions = [t.to_stage for t in hop.stage_history]
        expected = [MicroStage.PRE_CHECK, MicroStage.THINK, MicroStage.ACT,
                   MicroStage.CRITIQUE, MicroStage.COMMIT]
        assert transitions == expected

    @pytest.mark.asyncio
    async def test_async_function_execution(self):
            """Test execution with async hop function."""
        hop = SubatomicHop(self.async_hop, self.config)

        result = await hop.run()

        assert result["result"] == "async_result"
        assert hop.state == HopState.COMPLETED

    @pytest.mark.asyncio
    async def test_input_validation_failure(self):
            """Test pre-check validation failure."""
        hop = SubatomicHop(self.simple_hop, self.config)

        # Override pre-check to fail
        async def failing_pre_check(**kwargs):
                """Docstring."""
            raise InputValidationError("Missing required input")

        hop._pre_check = failing_pre_check

        with pytest.raises(InputValidationError):
            await hop.run()

        assert hop.state == HopState.FAILED

    @pytest.mark.asyncio
    async def test_stage_retry_mechanism(self):
            """Test retry mechanism for failing stages."""
        retry_config = RetryPolicy(max_retries=2, retry_delay=0.1)
        config = SubatomicHopConfig(
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

        hop = SubatomicHop(lambda: None, config)
        hop._act = flaky_act

        result = await hop.run()

        assert call_count == 2  # Should have retried once
        assert hop.stage_retry_counts[MicroStage.ACT] == 1

    @pytest.mark.asyncio
    async def test_checkpoint_save_and_resume(self):
            """Test checkpoint saving and resuming."""
        hop = SubatomicHop(self.simple_hop, self.config)

        # Execute through THINK stage
        await hop._execute_stage(MicroStage.PRE_CHECK)
        await hop._execute_stage(MicroStage.THINK)

        # Check checkpoint was saved
        assert MicroStage.THINK in hop.checkpoints

        # Create new hop and resume
        hop2 = SubatomicHop(self.simple_hop, self.config)
        await hop2._load_checkpoint()

        assert hop2.current_stage == MicroStage.THINK
        assert hop2.context == hop.context

    @pytest.mark.asyncio
    async def test_critique_quality_gate(self):
            """Test critique stage quality gate."""
        hop = SubatomicHop(self.simple_hop, self.config)

        # Set up context with invalid output
        hop.context["raw_output"] = None

        # Should raise QualityGateFailure
        with pytest.raises(QualityGateFailure):
            await hop._critique()

    @pytest.mark.asyncio
    async def test_atomic_commit(self):
            """Test atomic commit pattern."""
        hop = SubatomicHop(self.simple_hop, self.config)
        hop.context["validated_output"] = {"test": "data"}

        result = await hop._commit()

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
        hop = SubatomicHop(self.simple_hop, self.config)

        with patch('logging.Logger.info') as mock_log:
            await hop.run(x=3)

            # Check that stage transitions were logged
            assert mock_log.call_count >= 5  # At least 5 transitions

            # Check specific transition log
            log_calls = [call[0][0] for call in mock_log.call_args_list]
            assert any("STAGE_TRANSITION" in str(call) for call in log_calls)

    def test_get_status(self):
            """Test status reporting."""
        hop = SubatomicHop(self.simple_hop, self.config)

        status = hop.get_status()

        assert "hop_id" in status
        assert "state" in status
        assert "current_stage" in status
        assert "retry_counts" in status
        assert "stage_history" in status
        assert status["state"] == HopState.PENDING.value

    def test_cleanup(self):
            """Test checkpoint cleanup."""
        hop = SubatomicHop(self.simple_hop, self.config)

        # Create some checkpoint files
        checkpoint_file = hop.config.checkpoint_dir / f"{hop.config.hop_id}_TEST.json"
        checkpoint_file.write_text("{}")

        assert checkpoint_file.exists()

        hop.cleanup()

        assert not checkpoint_file.exists()

    def test_factory_function(self):
            """Test the create_subatomic_hop factory function."""
        hop = create_subatomic_hop(
            self.simple_hop,
            config=self.config,
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

        hop = decorated_hop(x=4)

        assert isinstance(hop, SubatomicHop)
        assert hop.context["x"] == 4

    @pytest.mark.asyncio
    async def test_timeout_protection(self):
            """Test execution timeout protection."""
        config = SubatomicHopConfig(
            checkpoint_dir=Path(self.temp_dir),
            max_execution_time=0.1  # Very short timeout
        )

        async def slow_hop():
                """Docstring."""
            await asyncio.sleep(0.2)  # Longer than timeout
            return {"result": "too_slow"}

        hop = SubatomicHop(slow_hop, config)

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
        config = SubatomicHopConfig(
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

        hop = SubatomicHop(lambda: None, config)
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
        self.config = SubatomicHopConfig(
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

            processed = []
            for record in data:
                processed.append({
                    "id": record["id"],
                    "value": record["value"] * 2,
                    "processed": True
                })

            return {"processed_count": len(processed), "data": processed}

        hop = SubatomicHop(process_data, self.config)

        test_data = [
            {"id": 1, "value": 10},
            {"id": 2, "value": 20}
        ]

        result = await hop.run(data=test_data)

        assert result["processed_count"] == 2
        assert len(result["data"]) == 2
        assert result["data"][0]["value"] == 20
        assert hop.state == HopState.COMPLETED

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
        hop1 = SubatomicHop(unreliable_hop, self.config)

        try:
            await hop1.run(x=10)
        except RuntimeError:
            pass  # Expected

        assert hop1.state == HopState.FAILED
        assert MicroStage.ACT in hop1.checkpoints

        # Second execution - should resume from checkpoint
        hop2 = SubatomicHop(unreliable_hop, self.config)

        result = await hop2.run(x=10)

        assert result["result"] == 50
        assert result["execution"] == 2
        assert hop2.state == HopState.COMPLETED

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
