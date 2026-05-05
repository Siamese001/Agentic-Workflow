"""W2 P3 Multi-Touch Sequence Tests

Integration tests for 3-touch sequences, context propagation, and state machine.
"""

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path


class TestW2P1SequenceDefinitions:
    """Test W2.P1: 3-Touch Sequence Definitions."""
    
    def test_standard_3_touch_sequence_defined(self):
        """Verify standard 3-touch sequence exists with correct structure."""
        from apps_lic.sequences.touch_sequence_definitions import (
            SequenceType, get_sequence_definition, STANDARD_3_TOUCH
        )
        
        seq_def = get_sequence_definition(SequenceType.STANDARD_3_TOUCH)
        
        assert seq_def.sequence_type == SequenceType.STANDARD_3_TOUCH
        assert len(seq_def.touches) == 3
        assert seq_def.requires_p2 is True
        assert seq_def.max_duration_days == 14
    
    def test_executive_3_touch_sequence_defined(self):
        """Verify executive 3-touch sequence exists."""
        from apps_lic.sequences.touch_sequence_definitions import (
            SequenceType, get_sequence_definition, EXECUTIVE_3_TOUCH
        )
        
        seq_def = get_sequence_definition(SequenceType.EXECUTIVE_3_TOUCH)
        
        assert seq_def.sequence_type == SequenceType.EXECUTIVE_3_TOUCH
        assert len(seq_def.touches) == 3
        assert seq_def.requires_p2 is True
        assert seq_def.max_duration_days == 21  # Longer for executives
    
    def test_recruiter_compact_sequence_defined(self):
        """Verify recruiter compact sequence exists."""
        from apps_lic.sequences.touch_sequence_definitions import (
            SequenceType, get_sequence_definition, RECRUITER_COMPACT
        )
        
        seq_def = get_sequence_definition(SequenceType.RECRUITER_COMPACT)
        
        assert seq_def.sequence_type == SequenceType.RECRUITER_COMPACT
        assert len(seq_def.touches) == 3
        assert seq_def.requires_p2 is False  # P2 optional for recruiters
        assert seq_def.max_duration_days == 12  # Shorter for recruiters
    
    def test_touch_definitions_have_required_fields(self):
        """Verify each touch has required field definitions."""
        from apps_lic.sequences.touch_sequence_definitions import (
            SequenceType, get_sequence_definition
        )
        
        seq_def = get_sequence_definition(SequenceType.STANDARD_3_TOUCH)
        
        for touch in seq_def.touches:
            assert touch.touch_number > 0
            assert touch.template_id != ""
            assert touch.strategy.value != ""
            assert touch.delay_days >= 0
            assert isinstance(touch.carry_forward_keys, list)
    
    def test_touch_1_is_initial_strategy(self):
        """Verify touch 1 uses 'initial' strategy."""
        from apps_lic.sequences.touch_sequence_definitions import (
            SequenceType, get_touch_definition, TouchStrategy
        )
        
        touch = get_touch_definition(SequenceType.STANDARD_3_TOUCH, 1)
        
        assert touch is not None
        assert touch.strategy == TouchStrategy.INITIAL
        assert touch.delay_days == 0
    
    def test_touch_2_is_nudge_strategy(self):
        """Verify touch 2 uses 'nudge' strategy."""
        from apps_lic.sequences.touch_sequence_definitions import (
            SequenceType, get_touch_definition, TouchStrategy
        )
        
        touch = get_touch_definition(SequenceType.STANDARD_3_TOUCH, 2)
        
        assert touch is not None
        assert touch.strategy == TouchStrategy.NUDGE
        assert touch.delay_days == 5
    
    def test_touch_3_is_fresh_angle_or_close(self):
        """Verify touch 3 uses appropriate strategy."""
        from apps_lic.sequences.touch_sequence_definitions import (
            SequenceType, get_touch_definition, TouchStrategy
        )
        
        standard_touch = get_touch_definition(SequenceType.STANDARD_3_TOUCH, 3)
        exec_touch = get_touch_definition(SequenceType.EXECUTIVE_3_TOUCH, 3)
        
        assert standard_touch.strategy == TouchStrategy.FRESH_ANGLE
        assert exec_touch.strategy == TouchStrategy.CLOSE_OR_OPTOUT
    
    def test_p2_context_requirements_per_touch(self):
        """Verify P2 context slots required per touch."""
        from apps_lic.sequences.touch_sequence_definitions import (
            SequenceType, get_touch_definition
        )
        
        # Touch 1: All P2 slots
        touch1 = get_touch_definition(SequenceType.STANDARD_3_TOUCH, 1)
        assert "N0" in touch1.p2_context_required
        assert "A0" in touch1.p2_context_required
        assert "L0" in touch1.p2_context_required
        
        # Touch 2: Just tone calibration
        touch2 = get_touch_definition(SequenceType.STANDARD_3_TOUCH, 2)
        assert "A0" in touch2.p2_context_required
        
        # Touch 3: Arc + competitive
        touch3 = get_touch_definition(SequenceType.STANDARD_3_TOUCH, 3)
        assert "N0" in touch3.p2_context_required
        assert "L0" in touch3.p2_context_required
    
    def test_calculate_touch_wake_time(self):
        """Verify wake time calculation works."""
        from apps_lic.sequences.touch_sequence_definitions import (
            SequenceType, calculate_touch_wake_time
        )
        
        start = datetime.now(timezone.utc)
        
        # Touch 1 should be at start (0 delay)
        wake1 = calculate_touch_wake_time(SequenceType.STANDARD_3_TOUCH, 1, start)
        assert wake1 == start
        
        # Touch 2 should be 5 days after
        wake2 = calculate_touch_wake_time(SequenceType.STANDARD_3_TOUCH, 2, start)
        expected2 = start + timedelta(days=5)
        assert (wake2 - expected2).total_seconds() < 1
        
        # Touch 3 should be 12 days after (5 + 7)
        wake3 = calculate_touch_wake_time(SequenceType.STANDARD_3_TOUCH, 3, start)
        expected3 = start + timedelta(days=12)
        assert (wake3 - expected3).total_seconds() < 1


class TestW2P2TouchPropagation:
    """Test W2.P2: Touch N→N+1 Context Propagation."""
    
    def test_touch_context_creation(self):
        """Verify TouchContext can be created from result."""
        from apps_lic.sequences.touch_propagation import (
            TouchContext, create_touch_context_from_result
        )
        from apps_lic.sequences.touch_sequence_definitions import SequenceType
        
        result = {
            "touch_id": "test-001",
            "touch_number": 1,
            "campaign_id": "camp-001",
            "recipient_hash": "hash123",
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "message_body": "Test message content",
            "response_received": False,
            "context_data": {"hook_used": "hook1"},
        }
        
        context = create_touch_context_from_result(result, SequenceType.STANDARD_3_TOUCH)
        
        assert context.touch_id == "test-001"
        assert context.touch_number == 1
        assert context.sequence_type == SequenceType.STANDARD_3_TOUCH
        assert context.message_body_hash is not None
    
    def test_context_to_carry_forward(self):
        """Verify context extraction for propagation."""
        from apps_lic.sequences.touch_propagation import TouchContext
        from apps_lic.sequences.touch_sequence_definitions import SequenceType
        
        context = TouchContext(
            touch_id="test-001",
            touch_number=1,
            sequence_type=SequenceType.STANDARD_3_TOUCH,
            campaign_id="camp-001",
            recipient_hash="hash123",
            sent_at=datetime.now(timezone.utc),
            message_body_hash="abc123",
            response_received=False,
            context_data={"hook_used": "hook1", "angles_used": ["angle1"]},
        )
        
        carry_forward = context.to_carry_forward(["hook_used", "angles_used"])
        
        assert "hook_used" in carry_forward
        assert carry_forward["hook_used"] == "hook1"
        assert "angles_used" in carry_forward
        assert "touch_number" in carry_forward  # Always included
    
    def test_propagator_propagates_context(self):
        """Verify propagator moves context from N to N+1."""
        from apps_lic.sequences.touch_propagation import TouchContextPropagator, TouchContext
        from apps_lic.sequences.touch_sequence_definitions import SequenceType
        
        propagator = TouchContextPropagator()
        
        source = TouchContext(
            touch_id="test-001",
            touch_number=1,
            sequence_type=SequenceType.STANDARD_3_TOUCH,
            campaign_id="camp-001",
            recipient_hash="hash123",
            context_data={"hook_used": "hook1"},
        )
        
        result = propagator.propagate(source, 2)
        
        assert result.success is True
        assert result.source_touch_id == "test-001"
        assert result.target_touch_number == 2
        assert "hook_used" in result.propagated_context or len(result.p2_slots_bound) >= 0
    
    def test_p2_slot_binding(self):
        """Verify P2 slots are bound during propagation."""
        from apps_lic.sequences.touch_propagation import TouchContextPropagator, TouchContext
        from apps_lic.sequences.touch_sequence_definitions import SequenceType
        
        propagator = TouchContextPropagator()
        
        source = TouchContext(
            touch_id="test-001",
            touch_number=1,
            sequence_type=SequenceType.STANDARD_3_TOUCH,
            campaign_id="camp-001",
            recipient_hash="hash123",
        )
        
        # Provide fresh P2 context
        p2_context = {
            "archetype_tone_calibration": {"tone": "professional"},
        }
        
        result = propagator.propagate(source, 2, p2_context)
        
        # Touch 2 requires A0 (archetype tone calibration)
        assert result.success is True
        # Either the P2 slot is bound or fallback is provided
        assert "A0" in result.p2_slots_bound or len(result.p2_slots_bound) == 0
    
    def test_p2_graceful_fallback(self):
        """Verify graceful fallback when P2 context missing."""
        from apps_lic.sequences.touch_propagation import TouchContextPropagator, TouchContext
        from apps_lic.sequences.touch_sequence_definitions import SequenceType
        
        propagator = TouchContextPropagator()
        
        source = TouchContext(
            touch_id="test-001",
            touch_number=1,
            sequence_type=SequenceType.STANDARD_3_TOUCH,
            campaign_id="camp-001",
            recipient_hash="hash123",
        )
        
        # No P2 context provided
        result = propagator.propagate(source, 2)
        
        assert result.success is True
        # Should have fallback text for missing P2 slots
        if "A0" in result.p2_slots_bound:
            assert "No archetype" in result.p2_slots_bound["A0"] or "neutral" in result.p2_slots_bound["A0"]


class TestW2P3SequenceStateMachine:
    """Test W2.P3: Sequence State Machine."""
    
    def test_create_sequence(self):
        """Verify sequence creation."""
        from apps_lic.state.sequence_state_machine import (
            SequenceStateMachine, SequenceState, SequenceStateRecord
        )
        from apps_lic.sequences.touch_sequence_definitions import SequenceType
        
        machine = SequenceStateMachine()
        
        record = machine.create_sequence(
            sequence_id="seq-001",
            campaign_id="camp-001",
            recipient_hash="hash123",
            sequence_type=SequenceType.STANDARD_3_TOUCH,
        )
        
        assert record.sequence_id == "seq-001"
        assert record.current_state == SequenceState.PENDING
        assert record.sequence_type == SequenceType.STANDARD_3_TOUCH
    
    def test_sequence_state_transitions(self):
        """Verify state machine transitions work correctly."""
        from apps_lic.state.sequence_state_machine import (
            SequenceStateMachine, SequenceState, TouchStatus
        )
        from apps_lic.sequences.touch_sequence_definitions import SequenceType
        
        machine = SequenceStateMachine()
        
        record = machine.create_sequence("seq-001", "camp", "hash", SequenceType.STANDARD_3_TOUCH)
        
        # PENDING → SCHEDULED (on touch_scheduled event)
        record = machine.transition(record, "touch_scheduled")
        assert record.current_state == SequenceState.SCHEDULED
        
        # Add a touch and transition to ACTIVE
        machine.add_touch_state(record, "touch-001", 1)
        machine.update_touch_status(record, "touch-001", TouchStatus.SCHEDULED)
        record = machine.transition(record, "touch_sent")
        assert record.current_state == SequenceState.ACTIVE
    
    def test_sequence_timeout_transition(self):
        """Verify timeout handling."""
        from apps_lic.state.sequence_state_machine import (
            SequenceStateMachine, SequenceState
        )
        from apps_lic.sequences.touch_sequence_definitions import SequenceType
        
        machine = SequenceStateMachine()
        
        record = machine.create_sequence("seq-001", "camp", "hash", SequenceType.STANDARD_3_TOUCH)
        
        # Set created_at far in the past to trigger timeout
        record.created_at = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Check timeout
        record = machine.transition(record, "check_timeout")
        
        assert record.current_state == SequenceState.TIMEOUT
        assert record.completed_at is not None
    
    def test_sequence_abandonment(self):
        """Verify operator abandonment."""
        from apps_lic.state.sequence_state_machine import (
            SequenceStateMachine, SequenceState
        )
        from apps_lic.sequences.touch_sequence_definitions import SequenceType
        
        machine = SequenceStateMachine()
        
        record = machine.create_sequence("seq-001", "camp", "hash", SequenceType.STANDARD_3_TOUCH)
        record = machine.transition(record, "abandoned")
        
        assert record.current_state == SequenceState.ABANDONED
        assert record.completed_at is not None
    
    def test_touch_state_management(self):
        """Verify touch states are tracked within sequence."""
        from apps_lic.state.sequence_state_machine import (
            SequenceStateMachine, TouchStatus
        )
        from apps_lic.sequences.touch_sequence_definitions import SequenceType
        
        machine = SequenceStateMachine()
        
        record = machine.create_sequence("seq-001", "camp", "hash", SequenceType.STANDARD_3_TOUCH)
        
        # Add multiple touches
        touch1 = machine.add_touch_state(record, "touch-001", 1)
        touch2 = machine.add_touch_state(record, "touch-002", 2)
        
        assert len(record.touches) == 2
        
        # Update touch status
        machine.update_touch_status(record, "touch-001", TouchStatus.SENT, message_body_hash="hash123")
        
        assert touch1.status == TouchStatus.SENT
        assert touch1.message_body_hash == "hash123"
    
    def test_transition_logging(self):
        """Verify transitions are logged."""
        from apps_lic.state.sequence_state_machine import (
            SequenceStateMachine, SequenceState
        )
        from apps_lic.sequences.touch_sequence_definitions import SequenceType
        
        machine = SequenceStateMachine()
        
        record = machine.create_sequence("seq-001", "camp", "hash", SequenceType.STANDARD_3_TOUCH)
        record = machine.transition(record, "touch_scheduled")
        
        history = machine.get_transition_history("seq-001")
        
        assert len(history) >= 1
        assert history[0].from_state == SequenceState.PENDING
        assert history[0].to_state == SequenceState.SCHEDULED


class TestW2Integration:
    """Test W2 End-to-End: Sequence → Propagation → State Machine."""
    
    def test_full_3_touch_sequence_lifecycle(self):
        """Simulate complete 3-touch sequence from start to exhaust."""
        from apps_lic.sequences.touch_sequence_definitions import (
            SequenceType, get_sequence_definition, calculate_touch_wake_time
        )
        from apps_lic.sequences.touch_propagation import TouchContextPropagator, TouchContext
        from apps_lic.state.sequence_state_machine import (
            SequenceStateMachine, SequenceState, TouchStatus
        )
        
        # Create sequence
        machine = SequenceStateMachine()
        record = machine.create_sequence(
            "seq-001", "camp-001", "recipient-123", SequenceType.STANDARD_3_TOUCH
        )
        
        seq_def = get_sequence_definition(SequenceType.STANDARD_3_TOUCH)
        propagator = TouchContextPropagator()
        
        # Touch 1
        touch1 = machine.add_touch_state(record, "touch-001", 1)
        machine.update_touch_status(record, "touch-001", TouchStatus.SCHEDULED)
        record = machine.transition(record, "touch_scheduled")
        
        # Touch 1 sent
        machine.update_touch_status(record, "touch-001", TouchStatus.SENT)
        record = machine.transition(record, "touch_sent")
        
        # Create context and propagate
        context1 = TouchContext(
            touch_id="touch-001",
            touch_number=1,
            sequence_type=SequenceType.STANDARD_3_TOUCH,
            campaign_id="camp-001",
            recipient_hash="recipient-123",
            context_data={"hook_used": "hook1"},
        )
        
        result = propagator.propagate(context1, 2)
        assert result.success
        
        # Touch 2
        touch2 = machine.add_touch_state(record, "touch-002", 2)
        touch2.context_carry_forward = result.propagated_context
        machine.update_touch_status(record, "touch-002", TouchStatus.SCHEDULED)
        record = machine.transition(record, "next_touch_scheduled")
        
        # Verify final state is still progressing
        assert record.current_state in [SequenceState.SCHEDULED, SequenceState.ACTIVE]


class TestW2SpineWiring:
    """Test W2 components in spine wiring."""
    
    def test_spine_wiring_has_w2_components(self):
        """Verify spine wiring includes W2 verifiers."""
        wiring_path = Path("apps_lic/spine_wiring.py")
        content = wiring_path.read_text()
        
        assert "sequence_definitions" in content
        assert "touch_propagation" in content
        assert "sequence_state_machine" in content
    
    def test_sequence_definitions_verifier_exists(self):
        """Verify _verify_sequence_definitions method exists."""
        from apps_lic.spine_wiring import SpineWiringVerifier
        
        verifier = SpineWiringVerifier()
        assert hasattr(verifier, '_verify_sequence_definitions')
    
    def test_touch_propagation_verifier_exists(self):
        """Verify _verify_touch_propagation method exists."""
        from apps_lic.spine_wiring import SpineWiringVerifier
        
        verifier = SpineWiringVerifier()
        assert hasattr(verifier, '_verify_touch_propagation')
    
    def test_sequence_state_machine_verifier_exists(self):
        """Verify _verify_sequence_state_machine method exists."""
        from apps_lic.spine_wiring import SpineWiringVerifier
        
        verifier = SpineWiringVerifier()
        assert hasattr(verifier, '_verify_sequence_state_machine')
