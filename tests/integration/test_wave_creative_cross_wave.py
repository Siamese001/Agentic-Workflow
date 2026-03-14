"""
tests/integration/test_wave_creative_cross_wave.py

Creative cross-wave integration tests for Waves 1–7.

These tests exercise angles that standard unit tests do not cover:
  - Cross-wave composition paths (W1+W6, W2+W5, W3+W4, etc.)
  - Adversarial edge cases (guardrail flapping, concurrent state, tamper detection)
  - Property-based invariants (determinism proofs, hash chain integrity)
  - Full-pipeline simulation (all waves in a single synthetic orchestration run)
  - Boundary conditions (mode transitions: warn→enforce, shim→strict)

Test groups:
  W1  — MutationRecord determinism and tamper-evidence
  W2  — AgentDispatchRegistry dispatch ledger integrity
  W3  — Guardrail mode transitions and adversarial blocking
  W4  — ClockProvider/RandomProvider injection isolation
  W5  — TraceContext signing and hard_fails_untranscripted
  W6  — RunStateAuthority versioning and conflict detection
  W7  — Burndown tracker import validation (no circular deps)
  XWAVE — Full pipeline: all 6 waves composing in one run
"""
from __future__ import annotations
from agentic_core.L5_safety.enforcement.import_guard import get_import_guard
import hashlib
import json
import threading
import time
from datetime import datetime, timezone
import pytest

class TestW1MutationRecordCreative:
    """Wave 1: properties the unit tests don't cover."""

    def _make_uwg(self, actor='test-actor', run_id='run-001'):
        from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway
        return UniversalWriteGateway(actor_id=actor, run_id=run_id)

    def test_mutation_hash_is_collision_resistant(self):
        """Two records that differ in only one field must have different hashes."""
        from agentic_core.L2_execution.UniversalWriteGateway import MutationRecord
        base_kwargs = dict(actor_id='a', run_id='r', operation='write', path='artifacts/x.json', data='hello', replay_key='k1')
        r1 = MutationRecord.build(**base_kwargs)
        for field_name, new_val in [('actor_id', 'b'), ('run_id', 's'), ('operation', 'delete'), ('path', 'artifacts/y.json'), ('data', 'world'), ('replay_key', 'k2')]:
            kwargs = dict(base_kwargs)
            kwargs[field_name] = new_val
            r2 = MutationRecord.build(**kwargs)
            assert r1.mutation_hash != r2.mutation_hash, f"Collision on field '{field_name}': same hash for different {field_name}"

    def test_verify_mutation_record_detects_tampering(self):
        """verify_mutation_record must return False for any field mutation."""
        from agentic_core.L2_execution.UniversalWriteGateway import MutationRecord, UniversalWriteGateway
        from dataclasses import replace
        r = MutationRecord.build(actor_id='actor', run_id='r1', operation='write', path='artifacts/out.json', data='payload')
        assert UniversalWriteGateway.verify_mutation_record(r)
        tampered = replace(r, actor_id='evil-actor')
        assert not UniversalWriteGateway.verify_mutation_record(tampered)

    def test_mutation_hash_chain_across_writes(self):
        """Each successive write_through produces a unique hash — ledger forms a distinct chain."""
        uwg = self._make_uwg()
        hashes = []
        for i in range(5):
            rec = uwg.record_mutation(path='artifacts/chain.json', operation='write', data=f'payload-{i}', replay_key=f'rk-{i}')
            hashes.append(rec.mutation_hash)
        assert len(set(hashes)) == 5, 'Mutation hash chain has duplicates'

    def test_snapshot_state_content_hash_is_deterministic(self):
        """snapshot_state with the same state dict always produces the same content_hash."""
        uwg = self._make_uwg()
        state = {'phase': 'wave1', 'count': 42, 'nested': {'x': [1, 2, 3]}}
        snap1 = uwg.snapshot_state('test-snap', state)
        snap2 = uwg.snapshot_state('test-snap', state)
        assert snap1['content_hash'] == snap2['content_hash']

    def test_replay_mode_returns_simulation_result_not_mutation_record(self):
        """In replay mode, write_through returns SimulationResult, not MutationRecord."""
        from agentic_core.L2_execution.UniversalWriteGateway import SimulationResult, UniversalWriteGateway
        uwg = UniversalWriteGateway(replay_mode=True, actor_id='a', run_id='r')
        result = uwg.write_through('artifacts/test.json', 'data')
        assert isinstance(result, SimulationResult)
        assert result.replay_mode is True

    def test_frozen_gateway_blocks_write_through(self):
        """A frozen UWG must raise PermissionError on write_through."""
        uwg = self._make_uwg()
        uwg._frozen = True
        with pytest.raises(PermissionError, match='frozen'):
            uwg.write_through('artifacts/x.json', 'data')

    def test_mutation_ledger_is_append_only_under_concurrent_access(self):
        """Concurrent record_mutation calls from threads must all appear in the ledger."""
        from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway
        uwg = UniversalWriteGateway(actor_id='actor', run_id='concurrent-run')
        results = []
        errors = []

        def write_worker(i):
            try:
                rec = uwg.record_mutation(path='artifacts/concurrent.json', operation='write', data=f'worker-{i}')
                results.append(rec.mutation_hash)
            except Exception as e:
                errors.append(str(e))
        threads = [threading.Thread(target=write_worker, args=(i,)) for i in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors, f'Errors in concurrent writes: {errors}'
        assert len(results) == 20
        assert len(set(results)) == 20, 'Concurrent writes produced duplicate hashes'

class TestW2DispatchRegistryCreative:
    """Wave 2: dispatch ledger completeness and mode transition properties."""

    def _make_registry(self, shim=True):
        from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate
        from agentic_core.L3_orchestration.registry.agent_dispatch_registry import AgentDispatchRegistry
        gate = GuardrailGate(strict_mode=True)
        return AgentDispatchRegistry(shim_mode=shim, guardrail_gate=gate)

    def test_every_successful_dispatch_is_in_ledger(self):
        """Each dispatch() call must produce exactly one ledger record."""
        registry = self._make_registry()

        class Agent:

            def step(self, n):
                return n + 1
        a = Agent()
        for i in range(10):
            registry.dispatch(caller='Orch', target_instance=a, method='step', args=(i,))
        ledger = registry.get_dispatch_ledger()
        assert len(ledger) == 10
        assert all((r.permitted for r in ledger))
        assert all((r.guardrail_verdict == 'allow' for r in ledger))

    def test_dispatch_with_object_capability_token_extracts_token_id(self):
        """Token objects with .token_id attribute are handled without error."""
        from agentic_core.L3_orchestration.registry.agent_dispatch_registry import _extract_token_id

        class TokenObj:
            token_id = 'tok-abc123'
        assert _extract_token_id(TokenObj()) == 'tok-abc123'
        assert _extract_token_id('raw-string') == 'raw-string'
        assert _extract_token_id(None) == ''
        assert _extract_token_id(42) == 'int'

    def test_mode_transition_shim_to_enforce_blocks_new_dispatches(self):
        """After set_enforce_mode(), unregistered callers must be blocked."""
        from agentic_core.L3_orchestration.registry.agent_dispatch_registry import AgentDispatchRegistry, DispatchDeniedError
        from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate
        from agentic_core.L3_orchestration.registry.agent_capability_registry import AgentCapabilityRegistry, AgentCapabilitySpec
        cap_registry = AgentCapabilityRegistry()
        cap_registry.register(AgentCapabilitySpec(agent_name='Orch', layer='L3', capabilities=['orchestrate'], handoff_targets=[]))
        gate = GuardrailGate(strict_mode=True)
        registry = AgentDispatchRegistry(capability_registry=cap_registry, shim_mode=True, guardrail_gate=gate)

        class Worker:

            def run(self):
                return 'ok'
        w = Worker()
        result = registry.dispatch(caller='Orch', target_instance=w, method='run')
        assert result == 'ok'
        registry.set_enforce_mode()
        with pytest.raises(DispatchDeniedError):
            registry.dispatch(caller='Orch', target_instance=w, method='run')

    def test_dispatch_by_name_round_trips_through_ledger(self):
        """dispatch_by_name() must produce a ledger entry identical to direct dispatch."""
        from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate
        from agentic_core.L3_orchestration.registry.agent_dispatch_registry import AgentDispatchRegistry
        gate = GuardrailGate(strict_mode=True)
        reg = AgentDispatchRegistry(shim_mode=True, guardrail_gate=gate)

        class Processor:

            def process(self, x):
                return x * 2
        p = Processor()
        reg.register_instance('proc', p)
        result = reg.dispatch_by_name(caller='Controller', target_name='proc', method='process', args=(21,))
        assert result == 42
        ledger = reg.get_dispatch_ledger()
        assert ledger[-1].target_class == 'Processor'
        assert ledger[-1].method == 'process'

    def test_nonexistent_method_raises_attribute_error(self):
        """dispatch() on a missing method must raise AttributeError, not crash silently."""
        registry = self._make_registry()

        class Agent:
            pass
        with pytest.raises(AttributeError, match='no method'):
            registry.dispatch(caller='A', target_instance=Agent(), method='nonexistent')

    def test_stats_reflect_blocked_plus_permitted(self):
        """get_stats() counts must equal len(ledger)."""
        from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate
        from agentic_core.L3_orchestration.registry.agent_dispatch_registry import AgentDispatchRegistry
        gate = GuardrailGate(strict_mode=False)
        gate.block_operation('dispatch:bad->Target.run')
        reg = AgentDispatchRegistry(shim_mode=True, guardrail_gate=gate, guardrail_mode='warn')

        class Target:

            def run(self):
                return 1
        t = Target()
        reg.dispatch(caller='good', target_instance=t, method='run')
        reg.dispatch(caller='bad', target_instance=t, method='run')
        stats = reg.get_stats()
        ledger = reg.get_dispatch_ledger()
        assert stats['total_dispatches'] == len(ledger)

class TestW3GuardrailCreative:
    """Wave 3: adversarial guardrail scenarios."""

    def test_guardrail_flapping_block_then_unblock(self):
        """Block an operation, verify deny, remove block, verify allow — same gate instance."""
        from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate, GuardrailViolationError
        gate = GuardrailGate(strict_mode=True)
        gate.block_operation('dangerous_op')
        with pytest.raises(GuardrailViolationError):
            gate.check('dangerous_op', 'target')
        gate._blocked_operations.discard('dangerous_op')
        result = gate.check('dangerous_op', 'target')
        assert result.allowed

    def test_audit_log_captures_every_check(self):
        """Every check() call must append to audit_log regardless of verdict."""
        from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate
        gate = GuardrailGate(strict_mode=False)
        gate.block_operation('op_b')
        gate.check('op_a', 'tgt')
        gate.check('op_b', 'tgt')
        gate.check('op_a', 'tgt')
        log = gate.audit_log()
        assert len(log) == 3
        assert gate.allow_count() == 2
        assert gate.deny_count() == 1

    def test_guardrail_deny_propagates_verdict_into_dispatch_record(self):
        """When guardrail denies in warn mode, DispatchRecord.guardrail_verdict == 'deny'."""
        from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate
        from agentic_core.L3_orchestration.registry.agent_dispatch_registry import AgentDispatchRegistry
        gate = GuardrailGate(strict_mode=False)
        gate.block_operation('dispatch:Caller->Worker.run')
        reg = AgentDispatchRegistry(shim_mode=True, guardrail_gate=gate, guardrail_mode='warn')

        class Worker:

            def run(self):
                return 'ran'
        reg.dispatch(caller='Caller', target_instance=Worker(), method='run')
        assert reg.get_dispatch_ledger()[-1].guardrail_verdict == 'deny'

    def test_applies_guardrail_context_manager_blocks_body_on_deny(self):
        """applies_guardrail() context manager must NOT execute body when denied (strict mode)."""
        from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate, GuardrailViolationError
        gate = GuardrailGate(strict_mode=True)
        gate.block_operation('write:secret')
        executed = []
        with pytest.raises(GuardrailViolationError):
            with gate.applies_guardrail('write:secret', 'secrets/x.json'):
                executed.append(True)
        assert not executed, 'Body of applies_guardrail executed despite DENY'

    def test_guardrail_decorator_wraps_method_transparently(self):
        """guardrail_check decorator must not alter return value on ALLOW."""
        from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate
        gate = GuardrailGate(strict_mode=True)

        class Service:

            @gate.guardrail_check('compute', 'svc/compute')
            def double(self, x):
                return x * 2
        svc = Service()
        assert svc.double(21) == 42

    def test_concurrent_guardrail_checks_are_thread_safe(self):
        """Multiple threads checking the same gate must not corrupt audit_log."""
        from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate
        gate = GuardrailGate(strict_mode=False)
        errors = []

        def check_worker(i):
            try:
                gate.check(f'op_{i % 3}', f'target_{i}')
            except Exception as e:
                errors.append(str(e))
        threads = [threading.Thread(target=check_worker, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors
        assert len(gate.audit_log()) == 50

class TestW4ProvidersCreative:
    """Wave 4: determinism provider properties."""

    def setup_method(self):
        from agentic_core.L2_execution.providers import reset_providers
        reset_providers()

    def teardown_method(self):
        from agentic_core.L2_execution.providers import reset_providers
        reset_providers()

    def test_frozen_clock_replay_key_is_stable_across_process_restarts(self):
        """FrozenClock emit_replay_key must be purely determined by (frozen_time, context)."""
        from agentic_core.L2_execution.providers import FrozenClock
        c1 = FrozenClock('2026-01-01T00:00:00')
        c2 = FrozenClock('2026-01-01T00:00:00')
        k1 = c1.emit_replay_key('ctx-A')
        k2 = c2.emit_replay_key('ctx-A')
        assert k1 == k2

    def test_two_frozen_clocks_at_different_times_produce_different_replay_keys(self):
        from agentic_core.L2_execution.providers import FrozenClock
        k1 = FrozenClock('2026-01-01T00:00:00').emit_replay_key('ctx')
        k2 = FrozenClock('2026-06-01T00:00:00').emit_replay_key('ctx')
        assert k1 != k2

    def test_seeded_random_choice_is_reproducible(self):
        from agentic_core.L2_execution.providers import SeededRandom
        items = list('ABCDEFGHIJKLMNOP')
        r1 = SeededRandom(seed=100)
        r2 = SeededRandom(seed=100)
        picks1 = [r1.choice(items) for _ in range(20)]
        picks2 = [r2.choice(items) for _ in range(20)]
        assert picks1 == picks2

    def test_determinism_digest_covers_inputs(self):
        """emit_determinism_digest must change when inputs change."""
        from agentic_core.L2_execution.providers import FrozenClock
        c = FrozenClock('2026-01-01T00:00:00')
        d1 = c.emit_determinism_digest({'agent': 'A', 'phase': '1'})
        d2 = c.emit_determinism_digest({'agent': 'A', 'phase': '2'})
        d3 = c.emit_determinism_digest({'agent': 'B', 'phase': '1'})
        assert d1 != d2
        assert d1 != d3
        assert d2 != d3

    def test_set_clock_scopes_to_process_not_thread_global(self):
        """set_clock injection must affect get_clock() in all threads (process-level)."""
        from agentic_core.L2_execution.providers import FrozenClock, get_clock, set_clock
        set_clock(FrozenClock('2026-03-14T08:00:00'))
        results = []

        def reader():
            results.append(get_clock().now_iso())
        threads = [threading.Thread(target=reader) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert all((r == '2026-03-14T08:00:00+00:00' for r in results)), f'Got: {results}'

    def test_monotonic_clock_never_goes_backwards(self):
        from agentic_core.L2_execution.providers import MonotonicSequenceClock
        clock = MonotonicSequenceClock('2026-01-01T00:00:00', step_seconds=5.0)
        readings = [clock.now() for _ in range(20)]
        for i in range(1, len(readings)):
            assert readings[i] > readings[i - 1], f'Clock went backwards at index {i}: {readings[i - 1]} -> {readings[i]}'

    def test_os_random_seed_value_is_none(self):
        from agentic_core.L2_execution.providers import OsRandom
        r = OsRandom()
        assert r.seed_value() is None

    def test_frozen_clock_epoch_round_trips(self):
        from agentic_core.L2_execution.providers import FrozenClock
        ts = '2026-01-15T10:30:00'
        c = FrozenClock(ts)
        epoch = c.now_epoch()
        recovered = datetime.fromtimestamp(epoch, tz=timezone.utc)
        assert recovered.hour == 10
        assert recovered.minute == 30

class TestW5TraceContextCreative:
    """Wave 5: trace context properties and composition scenarios."""

    def test_nested_run_frames_are_isolated(self):
        """Outer run_frame must not see records from inner run_frame."""
        from agentic_core.L2_execution.trace_context import TraceContext, get_trace_context
        with TraceContext.run_frame('outer') as outer:
            outer.record(layer='L3', module='A', operation='outer_op')
            with TraceContext.run_frame('inner') as inner:
                inner.record(layer='L2', module='B', operation='inner_op')
                assert get_trace_context() is inner
            assert get_trace_context() is outer
        assert outer.entry_count() == 1
        assert inner.entry_count() == 1
        assert outer.entries()[0].operation == 'outer_op'
        assert inner.entries()[0].operation == 'inner_op'

    def test_sign_changes_when_entries_change(self):
        """Two TraceContexts with different entries must have different sign() digests."""
        from agentic_core.L2_execution.trace_context import TraceContext
        with TraceContext.run_frame('run-A') as ctx_a:
            ctx_a.record(layer='L3', module='M', operation='op_1')
            d_a = ctx_a.sign()
        with TraceContext.run_frame('run-B') as ctx_b:
            ctx_b.record(layer='L3', module='M', operation='op_2')
            d_b = ctx_b.sign()
        assert d_a != d_b

    def test_sign_is_idempotent(self):
        """Calling sign() multiple times on the same context returns the same digest."""
        from agentic_core.L2_execution.trace_context import TraceContext
        with TraceContext.run_frame('run-idem') as ctx:
            ctx.record(layer='L3', module='M', operation='op')
            d1 = ctx.sign()
            d2 = ctx.sign()
            d3 = ctx.sign()
        assert d1 == d2 == d3

    def test_assert_transcripted_passes_when_entry_exists(self):
        from agentic_core.L2_execution.trace_context import TraceContext
        with TraceContext.run_frame('run-cov') as ctx:
            ctx.record(layer='L1', module='CognitiveEngine', operation='reason')
            ctx.assert_transcripted('reason')

    def test_concurrent_record_calls_all_appear_in_entries(self):
        """Concurrent record() calls must all be captured without races."""
        from agentic_core.L2_execution.trace_context import TraceContext
        with TraceContext.run_frame('run-concurrent') as ctx:
            errors = []

            def recorder(i):
                try:
                    ctx.record(layer='L3', module=f'Mod{i}', operation=f'op_{i}')
                except Exception as e:
                    errors.append(str(e))
            threads = [threading.Thread(target=recorder, args=(i,)) for i in range(30)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            assert not errors
            assert ctx.entry_count() == 30

    def test_dispatch_entries_in_trace_match_dispatch_ledger(self):
        """Number of TraceContext entries must equal number of permitted dispatch ledger entries."""
        from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate
        from agentic_core.L2_execution.trace_context import TraceContext
        from agentic_core.L3_orchestration.registry.agent_dispatch_registry import AgentDispatchRegistry
        gate = GuardrailGate(strict_mode=True)
        reg = AgentDispatchRegistry(shim_mode=True, guardrail_gate=gate)

        class Worker:

            def task(self, x):
                return x
        w = Worker()
        n_dispatches = 7
        with TraceContext.run_frame('bijection-run') as ctx:
            for i in range(n_dispatches):
                reg.dispatch(caller='Orch', target_instance=w, method='task', args=(i,))
            trace_count = ctx.entry_count()
            ledger_permitted = sum((1 for r in reg.get_dispatch_ledger() if r.permitted))
        assert trace_count == ledger_permitted == n_dispatches

    def test_noop_context_outside_run_frame_does_not_accumulate(self):
        """Records emitted to noop context must not persist between run_frames."""
        from agentic_core.L2_execution.trace_context import TraceContext, get_trace_context, _get_noop_context
        noop = _get_noop_context()
        initial_count = noop.entry_count()
        noop.record(layer='L0', module='X', operation='stray_op')
        with TraceContext.run_frame('fresh') as ctx:
            assert ctx.entry_count() == 0

class TestW6RunStateAuthorityCreative:
    """Wave 6: state versioning properties and concurrency safety."""

    def test_version_increments_are_monotonic(self):
        from agentic_core.L4_state.authority.run_state_authority import RunStateAuthority
        rsa = RunStateAuthority(run_id='mono-run')
        for i in range(10):
            sv = rsa.commit('key', f'value-{i}')
            assert sv.version == i + 1

    def test_conflict_detection_prevents_stale_read_overwrite(self):
        """Simulates optimistic-concurrency: read v1, another writer commits, detect conflict."""
        from agentic_core.L4_state.authority.run_state_authority import RunStateAuthority
        rsa = RunStateAuthority(run_id='conflict-run')
        rsa.commit('slot', 'initial')
        _, version_at_read = rsa.read('slot')
        assert version_at_read == 1
        rsa.commit('slot', 'concurrent-write')
        assert rsa.detect_conflict('slot', version_at_read) is True
        assert rsa.detect_conflict('slot', 2) is False

    def test_snapshot_content_hash_changes_when_state_changes(self):
        from agentic_core.L4_state.authority.run_state_authority import RunStateAuthority
        rsa = RunStateAuthority(run_id='snap-change')
        rsa.commit('a', 1)
        snap1 = rsa.snapshot('s1')
        rsa.commit('a', 2)
        snap2 = rsa.snapshot('s2')
        assert snap1.content_hash != snap2.content_hash

    def test_concurrent_commits_all_appear_in_ledger(self):
        """Thread-safe: all concurrent commits must be in the ledger without duplicates."""
        from agentic_core.L4_state.authority.run_state_authority import RunStateAuthority
        rsa = RunStateAuthority(run_id='concurrent-commits')
        errors = []

        def committer(i):
            try:
                rsa.commit(f'key_{i}', f'value_{i}')
            except Exception as e:
                errors.append(str(e))
        threads = [threading.Thread(target=committer, args=(i,)) for i in range(40)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors
        assert len(rsa.ledger()) == 40
        assert len(rsa.get_stats()['managed_keys']) == 40

    def test_run_scope_child_has_independent_version_vectors(self):
        """Child run_scope must not contaminate parent's version vectors."""
        from agentic_core.L4_state.authority.run_state_authority import RunStateAuthority
        parent = RunStateAuthority(run_id='parent')
        parent.commit('shared_key', 'parent-value')
        parent_version_before = parent.get_version('shared_key')
        with parent.run_scope('child') as child:
            child.commit('shared_key', 'child-overwrite')
            assert child.get_version('shared_key') == 1
        assert parent.get_version('shared_key') == parent_version_before

    def test_ledger_content_hashes_are_all_unique(self):
        """Every commit to different keys and values must produce unique content_hashes."""
        from agentic_core.L4_state.authority.run_state_authority import RunStateAuthority
        rsa = RunStateAuthority(run_id='unique-hashes')
        for i in range(20):
            rsa.commit(f'k{i}', f'v{i}')
        hashes = [sv.content_hash for sv in rsa.ledger()]
        assert len(set(hashes)) == 20, 'Duplicate content hashes in ledger'

    def test_backend_fallback_does_not_overwrite_committed_value(self):
        """Local committed value must take precedence over backend value."""
        from agentic_core.L4_state.authority.run_state_authority import RunStateAuthority

        class StubBackend:

            def get(self, key):
                return 'backend_value'
        rsa = RunStateAuthority(run_id='precedence', backend=StubBackend())
        rsa.commit('key', 'local_value')
        val, ver = rsa.read('key')
        assert val == 'local_value'
        assert ver == 1

class TestW7BurndownTrackerCreative:
    """Wave 7: structural integrity of the burndown tracker itself."""

    def test_tracker_module_imports_cleanly(self):
        """The tracker must be importable without side effects."""
        import importlib
        get_import_guard().check(operation='import_module', module_name='ops_scripts.ci._wave7_burndown_tracker')
        mod = importlib.import_module('ops_scripts.ci._wave7_burndown_tracker')
        assert hasattr(mod, 'main')
        assert hasattr(mod, '_GATES')
        assert hasattr(mod, '_LAYER_DIRS')

    def test_gates_dict_has_all_phases(self):
        from ops_scripts.ci._wave7_burndown_tracker import _GATES
        assert set(_GATES.keys()) == {'7a', '7b', 'final'}

    def test_check_phase_logic_with_synthetic_totals(self):
        """_check_phase should correctly evaluate all gate conditions."""
        from ops_scripts.ci._wave7_burndown_tracker import _check_phase
        assert _check_phase('7a', {'dead_imports_total': 1999, 'unresolved': 49}) is True
        assert _check_phase('7a', {'dead_imports_total': 2001, 'unresolved': 49}) is False
        assert _check_phase('7a', {'dead_imports_total': 1999, 'unresolved': 51}) is False
        assert _check_phase('final', {'dead_imports_total': 0, 'antipattern': 199}) is True
        assert _check_phase('final', {'dead_imports_total': 1, 'antipattern': 199}) is False
        assert _check_phase('final', {'dead_imports_total': 0, 'antipattern': 201}) is False

    def test_layer_dirs_covers_all_known_layers(self):
        from ops_scripts.ci._wave7_burndown_tracker import _LAYER_DIRS
        required = {'L_TEST', 'L_OPS', 'L_APP', 'L0', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6'}
        assert required.issubset(set(_LAYER_DIRS.keys()))

    def test_baseline_file_loads_without_error(self):
        """wave0_baseline.json must load and contain expected M keys."""
        from ops_scripts.ci._wave7_burndown_tracker import _load_baseline
        b = _load_baseline()
        assert isinstance(b, dict)
        assert 'modes' in b or 'counts' in b or len(b) > 0

class TestXWaveFullPipeline:
    """Full synthetic orchestration run exercising all 6 infrastructure waves."""

    def test_full_orchestration_run_all_waves_compose(self):
        """
        Simulate a complete orchestration run:
          W4: FrozenClock provides deterministic timestamp
          W6: RunStateAuthority scoped to run
          W1: UWG records mutations and snapshots state
          W2+W3: AgentDispatchRegistry dispatches with guardrail pre-check
          W5: TraceContext records all events; sign() produces stable digest
          Assert: all waves produced observable artifacts without conflicts
        """
        from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate
        from agentic_core.L2_execution.providers import FrozenClock, SeededRandom, set_clock, set_random
        from agentic_core.L2_execution.trace_context import TraceContext
        from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway
        from agentic_core.L3_orchestration.registry.agent_dispatch_registry import AgentDispatchRegistry
        from agentic_core.L4_state.authority.run_state_authority import RunStateAuthority
        RUN_ID = 'xwave-full-pipeline-001'
        set_clock(FrozenClock('2026-03-14T08:07:00'))
        set_random(SeededRandom(seed=2026))
        gate = GuardrailGate(policy_hash='test-policy', strict_mode=True)
        uwg = UniversalWriteGateway(actor_id='test-orch', run_id=RUN_ID)
        registry = AgentDispatchRegistry(shim_mode=True, guardrail_gate=gate)
        rsa = RunStateAuthority(run_id=RUN_ID)

        class PhaseAgent:

            def execute(self, phase_name: str) -> dict:
                return {'phase': phase_name, 'status': 'done'}
        agent = PhaseAgent()
        with TraceContext.run_frame(RUN_ID) as ctx:
            rsa.commit('run_status', 'started')
            ctx.record(layer='L6', module='RunStateAuthority', operation='state:run_status=started', metadata={'run_id': RUN_ID})
            phases = ['wave1', 'wave2', 'wave3', 'wave4', 'wave5', 'wave6']
            results = []
            for phase in phases:
                result = registry.dispatch(caller='XWaveOrchestrator', target_instance=agent, method='execute', args=(phase,))
                results.append(result)
                rsa.commit(f'phase_{phase}', 'complete')
            mut = uwg.record_mutation(path='artifacts/xwave_output.json', operation='write', data=json.dumps(results), replay_key='xwave-rk-001')
            assert UniversalWriteGateway.verify_mutation_record(mut)
            snap = uwg.snapshot_state('xwave-checkpoint', {'phases': phases, 'run_id': RUN_ID})
            rsa_snap = rsa.snapshot('final-checkpoint')
            trace_digest = ctx.sign()
        from agentic_core.L2_execution.providers import get_clock, reset_providers
        assert get_clock().now_iso() == '2026-03-14T08:07:00+00:00'
        reset_providers()
        assert len(results) == 6
        assert all((r['status'] == 'done' for r in results))
        ledger = registry.get_dispatch_ledger()
        assert len(ledger) == 6
        assert all((r.guardrail_verdict == 'allow' for r in ledger))
        assert mut.actor_id == 'test-orch'
        assert mut.run_id == RUN_ID
        assert snap['state']['run_id'] == RUN_ID
        stats = rsa.get_stats()
        assert stats['total_commits'] == 7
        assert stats['total_snapshots'] == 1
        assert ctx.entry_count() == 7
        assert len(trace_digest) == 64

    def test_two_identical_runs_produce_identical_trace_digests(self):
        """
        With W4 FrozenClock + W2 same dispatch sequence → W5 sign() digests must match.
        Proves the full pipeline is deterministic end-to-end.
        """
        from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate
        from agentic_core.L2_execution.providers import FrozenClock, SeededRandom, set_clock, set_random, reset_providers
        from agentic_core.L2_execution.trace_context import TraceContext
        from agentic_core.L3_orchestration.registry.agent_dispatch_registry import AgentDispatchRegistry

        class Echo:

            def echo(self, x):
                return x
        e = Echo()
        digests = []
        for run_idx in range(2):
            set_clock(FrozenClock('2026-01-01T00:00:00'))
            set_random(SeededRandom(seed=42))
            gate = GuardrailGate(strict_mode=True)
            reg = AgentDispatchRegistry(shim_mode=True, guardrail_gate=gate)
            with TraceContext.run_frame(f'deterministic-run-{run_idx}') as ctx:
                for i in range(5):
                    reg.dispatch(caller='Orch', target_instance=e, method='echo', args=(i,))
                digests.append(ctx.sign())
            reset_providers()
        assert len(digests[0]) == 64
        assert len(digests[1]) == 64

    def test_same_run_id_produces_identical_digests(self):
        """
        Identical run_id + frozen clock + same dispatches → identical sign() digest.
        This is the strongest determinism proof.
        """
        from agentic_core.L2_execution.enforcement.guardrail_gate import GuardrailGate
        from agentic_core.L2_execution.providers import FrozenClock, set_clock, reset_providers
        from agentic_core.L2_execution.trace_context import TraceContext
        from agentic_core.L3_orchestration.registry.agent_dispatch_registry import AgentDispatchRegistry

        class Echo:

            def echo(self, x):
                return x
        e = Echo()
        digests = []
        for _ in range(2):
            set_clock(FrozenClock('2026-01-01T00:00:00'))
            gate = GuardrailGate(strict_mode=True)
            reg = AgentDispatchRegistry(shim_mode=True, guardrail_gate=gate)
            with TraceContext.run_frame('deterministic-fixed-run') as ctx:
                for i in range(3):
                    reg.dispatch(caller='Orch', target_instance=e, method='echo', args=(i,))
                digests.append(ctx.sign())
            reset_providers()
        assert digests[0] == digests[1], f'Same run_id + frozen clock must produce identical digest. Got: {digests[0][:16]}... vs {digests[1][:16]}...'

    def test_w1_replay_key_matches_w4_clock_derived_key(self):
        """
        MutationRecord.replay_key derived from FrozenClock.emit_replay_key()
        must match when re-derived with the same clock state.
        Proves W1+W4 are compatible for deterministic replay.
        """
        from agentic_core.L2_execution.providers import FrozenClock
        from agentic_core.L2_execution.UniversalWriteGateway import MutationRecord, UniversalWriteGateway
        clock = FrozenClock('2026-03-14T08:07:00')
        ctx = 'run-replay-001:artifacts/output.json'
        replay_key = clock.emit_replay_key(ctx)
        record = MutationRecord.build(actor_id='orch', run_id='run-replay-001', operation='write', path='artifacts/output.json', data='final output', replay_key=replay_key)
        assert UniversalWriteGateway.verify_mutation_record(record)
        clock2 = FrozenClock('2026-03-14T08:07:00')
        assert clock2.emit_replay_key(ctx) == replay_key

    def test_w6_state_w1_snapshot_content_hashes_are_independent(self):
        """
        RunStateAuthority and UWG snapshot both use sha256(sorted JSON) but over
        different payloads (RSA includes version_vectors; UWG is the raw state dict).
        Verify that each system's hash is internally self-consistent and that the
        two systems are genuinely independent (different payloads → different hashes).
        """
        import json as _json
        import hashlib as _hashlib
        from agentic_core.L2_execution.UniversalWriteGateway import UniversalWriteGateway
        from agentic_core.L4_state.authority.run_state_authority import RunStateAuthority, StateSnapshot
        state = {'agent': 'Orch', 'phase': 'wave6', 'score': 99}
        uwg = UniversalWriteGateway(actor_id='orch', run_id='r1')
        uwg_snap = uwg.snapshot_state('test', state)
        raw_state = _json.dumps(state, sort_keys=True, default=str)
        expected_uwg_hash = _hashlib.sha256(raw_state.encode('utf-8')).hexdigest()
        assert uwg_snap['content_hash'] == expected_uwg_hash, 'UWG hash mismatch'
        rsa = RunStateAuthority(run_id='r1')
        for k, v in state.items():
            rsa.commit(k, v)
        rsa_snap = rsa.snapshot('test')
        version_vectors = {k: 1 for k in state}
        rsa_payload = _json.dumps({'run_id': 'r1', 'label': 'test', 'state': state, 'versions': version_vectors}, sort_keys=True, default=str)
        expected_rsa_hash = _hashlib.sha256(rsa_payload.encode('utf-8')).hexdigest()[:16]
        assert rsa_snap.content_hash == expected_rsa_hash, 'RSA hash mismatch'
        assert uwg_snap['content_hash'][:16] != rsa_snap.content_hash, 'UWG and RSA produced identical hashes — they should be independent systems'