"""Test suite for Node Negotiation Protocol."""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from .node_negotiator import (
    NodeNegotiator,
    NegotiationMessage,
    NegotiationRound,
    NegotiationResult,
    NegotiationConfig,
    get_node_negotiator,
    request_upstream_change,
    send_clarification
)

from .subatomic_hop import (
    SubatomicHop,
    SubatomicHopConfig,
    HopState,
    MicroStage
)


class TestNodeNegotiator:
    """Test suite for NodeNegotiator class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = NegotiationConfig(
            max_rounds=2,
            max_message_length=500,
            response_timeout=5.0
        )
        self.negotiator = NodeNegotiator(self.config)
    
    def test_initialization(self):
        """Test NodeNegotiator initialization."""
        assert self.negotiator.config.max_rounds == 2
        assert len(self.negotiator.active_negotiations) == 0
        assert len(self.negotiator.message_handlers) == 3
        assert self.negotiator.stats["total_negotiations"] == 0
    
    @pytest.mark.asyncio
    async def test_send_feedback_success(self):
        """Test successful feedback sending."""
        config = SubatomicHopConfig(hop_id="sender")
        sender_hop = SubatomicHop(lambda x: x, config)
        
        result = await self.negotiator.send_feedback(
            from_hop=sender_hop,
            to_hop_id="receiver",
            message_type="CHANGE_REQUEST",
            payload="Please shorten output",
            priority=5
        )
        
        assert result is True
        assert len(self.negotiator.active_negotiations) == 1
        
        # Check negotiation round
        round_id = list(self.negotiator.active_negotiations.keys())[0]
        negotiation = self.negotiator.active_negotiations[round_id]
        
        assert len(negotiation.messages) == 1
        assert negotiation.messages[0].from_hop == "sender"
        assert negotiation.messages[0].to_hop == "receiver"
        assert negotiation.messages[0].message_type == "CHANGE_REQUEST"
    
    @pytest.mark.asyncio
    async def test_send_feedback_too_long(self):
        """Test feedback rejection for too long message."""
        config = SubatomicHopConfig(hop_id="sender")
        sender_hop = SubatomicHop(lambda x: x, config)
        
        long_payload = "x" * 1000  # Exceeds max length
        
        result = await self.negotiator.send_feedback(
            from_hop=sender_hop,
            to_hop_id="receiver",
            message_type="CHANGE_REQUEST",
            payload=long_payload
        )
        
        assert result is False
        assert len(self.negotiator.active_negotiations) == 0
    
    @pytest.mark.asyncio
    async def test_request_change_success(self):
        """Test successful change request."""
        config = SubatomicHopConfig(hop_id="downstream")
        downstream_hop = SubatomicHop(lambda x: x, config)
        
        result = await self.negotiator.request_change(
            downstream_hop=downstream_hop,
            upstream_hop_id="upstream",
            requested_change="Make output more concise",
            reason="Too verbose for downstream processing"
        )
        
        assert isinstance(result, NegotiationResult)
        assert result.rounds_completed >= 0
        assert self.negotiator.stats["total_negotiations"] == 1
    
    @pytest.mark.asyncio
    async def test_handle_clarification(self):
        """Test clarification message handling."""
        message = NegotiationMessage(
            from_hop="node1",
            to_hop="node2",
            message_type="CLARIFICATION_REQUEST",
            payload="What format should the output be?"
        )
        
        negotiation = NegotiationRound(
            round_id="test_round",
            participants=["node1", "node2"]
        )
        
        await self.negotiator._handle_clarification(message, negotiation)
        
        # Should have added response
        assert len(negotiation.messages) == 2
        assert negotiation.messages[1].message_type == "CLARIFICATION_RESPONSE"
    
    @pytest.mark.asyncio
    async def test_handle_change_request(self):
        """Test change request handling."""
        message = NegotiationMessage(
            from_hop="downstream",
            to_hop="upstream",
            message_type="CHANGE_REQUEST",
            payload="Please add more details"
        )
        
        negotiation = NegotiationRound(
            round_id="test_round",
            participants=["upstream", "downstream"]
        )
        
        # Mock active hop
        mock_hop = Mock()
        mock_hop.state = HopState.COMPLETED
        mock_hop.config.hop_id = "upstream"
        
        with patch.object(self.negotiator, '_get_active_hop', return_value=mock_hop):
            await self.negotiator._handle_change_request(message, negotiation)
        
        # Should have changed hop state
        assert mock_hop.state == HopState.NEGOTIATING
        assert mock_hop.current_stage == MicroStage.THINK
        assert "negotiation_request" in mock_hop.context
    
    def test_get_or_create_round(self):
        """Test round creation and retrieval."""
        # First call creates new round
        round_id1 = self.negotiator._get_or_create_round("node1", "node2")
        assert round_id1 in self.negotiator.active_negotiations
        
        # Second call returns same round
        round_id2 = self.negotiator._get_or_create_round("node1", "node2")
        assert round_id1 == round_id2
        
        # Different pair creates new round
        round_id3 = self.negotiator._get_or_create_round("node2", "node3")
        assert round_id3 != round_id1
    
    def test_check_resolution(self):
        """Test negotiation resolution checking."""
        negotiation = NegotiationRound(
            round_id="test",
            participants=["node1", "node2"]
        )
        
        # No messages - not resolved
        assert not self.negotiator._check_resolution(negotiation)
        
        # Negative response - not resolved
        negotiation.messages.append(
            NegotiationMessage(
                from_hop="node1",
                to_hop="node2",
                message_type="CHANGE_REQUEST",
                payload="Please fix this"
            )
        )
        assert not self.negotiator._check_resolution(negotiation)
        
        # Positive response - resolved
        negotiation.messages.append(
            NegotiationMessage(
                from_hop="node2",
                to_hop="node1",
                message_type="RESPONSE",
                payload="Fixed and updated"
            )
        )
        assert self.negotiator._check_resolution(negotiation)
    
    def test_negotiation_history(self):
        """Test negotiation history tracking."""
        # Add some completed negotiations
        for i in range(3):
            negotiation = NegotiationRound(
                round_id=f"round_{i}",
                participants=[f"node_{i}", f"node_{i+1}"],
                status="COMPLETED"
            )
            self.negotiator.negotiation_history.append(negotiation)
        
        history = self.negotiator.get_negotiation_history()
        assert len(history) == 3
        
        limited_history = self.negotiator.get_negotiation_history(limit=2)
        assert len(limited_history) == 2
        assert limited_history[0].round_id == "round_1"
    
    def test_statistics_tracking(self):
        """Test statistics tracking."""
        initial_stats = self.negotiator.get_stats()
        assert initial_stats["total_negotiations"] == 0
        assert initial_stats["successful_negotiations"] == 0


class TestSubatomicHopNegotiation:
    """Test suite for SubatomicHop negotiation capabilities."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = SubatomicHopConfig(hop_id="test_hop")
        self.hop = SubatomicHop(lambda x: x, self.config)
        self.hop.negotiation_enabled = True
    
    @pytest.mark.asyncio
    async def test_request_upstream_change(self):
        """Test requesting upstream change."""
        result = await self.hop.request_upstream_change(
            upstream_hop_id="upstream_node",
            change_request="Add more context",
            reason="Insufficient information"
        )
        
        assert isinstance(result, NegotiationResult)
        assert result.rounds_completed >= 0
    
    @pytest.mark.asyncio
    async def test_send_negotiation_message(self):
        """Test sending negotiation message."""
        result = await self.hop.send_negotiation_message(
            to_hop_id="target_node",
            message_type="CLARIFICATION_REQUEST",
            payload="What is the expected format?"
        )
        
        assert result is True
    
    def test_handle_negotiation_request(self):
        """Test handling negotiation request."""
        request = {
            "from_hop": "downstream_node",
            "request": "Please make output shorter"
        }
        
        self.hop.handle_negotiation_request(request)
        
        assert "negotiation_request" in self.hop.context
        assert self.hop.context["negotiation_request"] == request
        assert "negotiation_log" in self.hop.context
        assert len(self.hop.context["negotiation_log"]) == 1
    
    def test_negotiation_disabled(self):
        """Test behavior when negotiation is disabled."""
        self.hop.negotiation_enabled = False
        
        # Should raise error
        with pytest.raises(RuntimeError):
            asyncio.run(self.hop.request_upstream_change(
                "upstream",
                "change",
                "reason"
            ))
        
        # Should return False
        result = asyncio.run(self.hop.send_negotiation_message(
            "target",
            "TYPE",
            "payload"
        ))
        assert result is False


class TestNegotiationIntegration:
    """Integration tests for negotiation system."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.negotiator = get_node_negotiator()
        
        # Create test hops
        self.upstream_config = SubatomicHopConfig(hop_id="upstream")
        self.downstream_config = SubatomicHopConfig(hop_id="downstream")
        
        def upstream_func(data):
            return {"summary": data.get("text", "")[:100]}  # Truncate
        
        def downstream_func(data):
            summary = data.get("summary", "")
            if len(summary) < 50:
                # Request more detail
                raise Exception("Need more detail")
            return {"processed": f"Processed: {summary}"}
        
        self.upstream_hop = SubatomicHop(upstream_func, self.upstream_config)
        self.downstream_hop = SubatomicHop(downstream_func, self.downstream_config)
        
        self.upstream_hop.negotiation_enabled = True
        self.downstream_hop.negotiation_enabled = True
    
    @pytest.mark.asyncio
    async def test_negotiation_flow(self):
        """Test complete negotiation flow."""
        # Downstream requests change
        result = await self.downstream_hop.request_upstream_change(
            upstream_hop_id="upstream",
            change_request="Provide full summary, not truncated",
            reason="Need complete information for processing"
        )
        
        assert isinstance(result, NegotiationResult)
        
        # Check negotiation was created
        assert len(self.negotiator.active_negotiations) > 0
    
    @pytest.mark.asyncio
    async def test_multiple_negotiation_rounds(self):
        """Test negotiation with multiple rounds."""
        # First request
        await self.downstream_hop.send_negotiation_message(
            to_hop_id="upstream",
            message_type="CHANGE_REQUEST",
            payload="Make output longer"
        )
        
        # Follow-up clarification
        await self.downstream_hop.send_negotiation_message(
            to_hop_id="upstream",
            message_type="CLARIFICATION_REQUEST",
            payload="What is the maximum length allowed?"
        )
        
        # Should have messages in negotiation
        assert len(self.negotiator.active_negotiations) == 1
        negotiation = list(self.negotiator.active_negotiations.values())[0]
        assert len(negotiation.messages) >= 2
    
    @pytest.mark.asyncio
    async def test_negotiation_timeout(self):
        """Test negotiation timeout handling."""
        config = NegotiationConfig(response_timeout=0.1)  # Very short timeout
        negotiator = NodeNegotiator(config)
        
        result = await negotiator.request_change(
            downstream_hop=self.downstream_hop,
            upstream_hop_id="upstream",
            requested_change="Test change",
            reason="Testing"
        )
        
        # Should timeout and not succeed
        assert not result.success
        assert result.resolution_type == "TIMEOUT"


class TestNegotiationScenarios:
    """Test realistic negotiation scenarios."""
    
    @pytest.mark.asyncio
    async def test_resume_length_negotiation(self):
        """Test negotiation over resume length."""
        # Create hops for resume generation and review
        def generate_resume(profile):
            return {
                "resume": f"Resume for {profile['name']}",
                "length": 100
            }
        
        def review_resume(resume_data):
            if resume_data["length"] < 200:
                # Request longer resume
                negotiator = get_node_negotiator()
                await negotiator.send_feedback(
                    from_hop=Mock(config=Mock(hop_id="reviewer")),
                    to_hop_id="generator",
                    message_type="CHANGE_REQUEST",
                    payload="Resume too short, need more details"
                )
            return {"approved": resume_data["length"] >= 200}
        
        generator_config = SubatomicHopConfig(hop_id="generator")
        generator = SubatomicHop(generate_resume, generator_config)
        generator.negotiation_enabled = True
        
        # Generate initial resume
        resume = generator.run(profile={"name": "John"})
        
        # Review requests change
        negotiator = get_node_negotiator()
        await negotiator.send_feedback(
            from_hop=Mock(config=Mock(hop_id="reviewer")),
            to_hop_id="generator",
            message_type="CHANGE_REQUEST",
            payload="Resume too short, need more details"
        )
        
        # Check negotiation was initiated
        assert len(negotiator.active_negotiations) == 1
    
    @pytest.mark.asyncio
    async def test_format_negotiation(self):
        """Test negotiation over output format."""
        def data_processor(data):
            return {"result": str(data)}
        
        def data_consumer(processed_data):
            result = processed_data.get("result", "")
            if not result.startswith("{"):
                # Request JSON format
                raise Exception("Need JSON format")
            return {"consumed": True}
        
        # Setup negotiation
        negotiator = get_node_negotiator()
        
        # Consumer requests format change
        await negotiator.send_feedback(
            from_hop=Mock(config=Mock(hop_id="consumer")),
            to_hop_id="processor",
            message_type="CHANGE_REQUEST",
            payload="Please output in JSON format"
        )
        
        # Verify message sent
        assert len(negotiator.active_negotiations) == 1
        negotiation = list(negotiator.active_negotiations.values())[0]
        assert "JSON format" in negotiation.messages[0].payload


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
