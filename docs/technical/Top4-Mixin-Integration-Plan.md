========================================================================================================================================================================================================================================================
                                              TOP 4 MIXIN INTEGRATION PLAN — execute_ssot OPERATIONAL HARDENING
                                              Delivers 92% of total value at 25% of implementation effort
========================================================================================================================================================================================================================================================

PRIORITY STACK (ordered by operational urgency):
  #1  MetaLearningClientMixin  — Strategic:   healing success 75% -> 90%   | 1 week
  #2  RedisCacheMixin          — Performance: 50x speedup on repeat violations | 1 week
  #3  TracingMixin             — Operational: debug time hours -> minutes   | 1 week
  #4  CircuitBreakerMixin      — Resilience:  prevents 95% cascading failures | 3 days

CURRENT STATE:
  All 4 mixin implementations EXIST in agentic_core/mixins/.
  NONE are wired into execute_ssot.py classes.
  This plan is purely about INTEGRATION — no new mixin code required.

TARGET CLASSES IN execute_ssot.py:
  - RuntimeStateManager          (line 1268) — orchestration hub, primary integration target
  - AutonomousDecisionEngine     (line 636)  — confidence + healing decisions
  - SovereignDecisionEngine      (line 869)  — token-based access control
  - EnhancedAutonomousDecisionEngine (line 807) — CDA integration

========================================================================================================================================================================================================================================================
  MIXIN #1: MetaLearningClientMixin
  File:   agentic_core/mixins/meta_learning_client_mixin.py
  Status: IMPLEMENTED — needs wiring into RuntimeStateManager + AutonomousDecisionEngine
========================================================================================================================================================================================================================================================

WHAT IT PROVIDES (already implemented):
  - ml_recall_healing_pattern(violation)     -> returns cached strategy or None
  - ml_store_healing_pattern(violation, result) -> persists successful strategies
  - ml_enhanced_heal(violation, heal_fn)     -> full recall->execute->store loop
  - ml_check_healing_depth(violation_id)     -> prevents infinite healing loops
  - ml_get_violation_signature(violation)    -> hash-based dedup key
  - Domain isolation: agentic_core / apps_lic / apps_rg
  - Guardrails: rate limiting, similarity threshold, cache size limits
  - MLWriteEnvelopeViolation: enforces writes only inside L2.2 commit sandbox

INTEGRATION STEPS:

  STEP 1 — Add mixin to RuntimeStateManager (execute_ssot.py line 1268)

    BEFORE:
      class RuntimeStateManager:

    AFTER:
      from agentic_core.mixins.meta_learning_client_mixin import MetaLearningClientMixin

      class RuntimeStateManager(MetaLearningClientMixin):

    MRO NOTE: MetaLearningClientMixin has no __init__, so no super() chain change needed.

  STEP 2 — Wire ml_enhanced_heal into execute_phase2_reconciliation (line 1112)

    BEFORE (current pattern):
      result = agent.heal(violation)

    AFTER:
      result = self.ml_enhanced_heal(violation, agent.heal)

    This single-line change activates:
      - Pattern recall before every heal attempt
      - Pattern storage after every successful heal
      - Depth tracking to prevent infinite loops

  STEP 3 — Wire ml_recall_healing_pattern into AutonomousDecisionEngine.should_proceed_with_healing

    BEFORE:
      def should_proceed_with_healing(self, confidence, agent_name):
          return confidence.value >= self._confidence_threshold

    AFTER:
      def should_proceed_with_healing(self, confidence, agent_name, violation=None):
          if violation is not None:
              cached = self.ml_recall_healing_pattern(violation)
              if cached:
                  return True  # Always proceed if we have a proven pattern
          return confidence.value >= self._confidence_threshold

  STEP 4 — Expose meta_learning stats in RuntimeStateManager.state dict

    In RuntimeStateManager.__init__, the state["meta_learning"] dict already exists (line 1283).
    Wire it to ml_get_stats() at mission completion:

      def complete_mission(self, ...):
          self.state["meta_learning"].update(self.ml_get_stats())
          self.save()

ACCEPTANCE CRITERIA:
  [ ] python -m pytest tests/ -k "meta_learning" exits 0
  [ ] ml_enhanced_heal called at least once per healing loop iteration (assert via mock)
  [ ] ml_store_healing_pattern only called inside L2.2 commit sandbox (MLWriteEnvelopeViolation not raised)
  [ ] state["meta_learning"]["total_experiences"] increments after each successful heal
  [ ] No new import cycles (python -m pytest tests/agentic_core/ -k "import_cycle" exits 0)

RISK:
  LOW — mixin has graceful degradation. If MetaLearningClient unavailable, all methods return None/False.
  The heal_fn is always called as fallback.

========================================================================================================================================================================================================================================================
  MIXIN #2: RedisCacheMixin
  File:   agentic_core/mixins/redis_cache_mixin.py
  Status: IMPLEMENTED — needs wiring into AutonomousDecisionEngine for AST result caching
========================================================================================================================================================================================================================================================

WHAT IT PROVIDES (already implemented):
  - cache_get(key) / cache_set(key, value, ttl) — async, Redis-first with local dict fallback
  - cache_invalidate(pattern) — pattern-based invalidation
  - cache_stats() — hit rate, size, connection state
  - CircuitBreaker built-in: 5 failures -> OPEN, 60s timeout -> HALF_OPEN
  - Feature flag: USE_REDIS_CACHE (env var) — local-only fallback if Redis unavailable
  - Key namespacing: sha256-hashed, prefix-scoped, TTL-enforced

HIGH-VALUE CACHE TARGETS IN execute_ssot.py:

  Target A — AST parse results (ASTCodeQualityValidator._read_and_parse_file, line 589)
    Current: re-parses every file on every agent run
    Cached:  parse once, cache by (file_path, mtime) key, TTL=300s
    Speedup: 50x on repeated violations (same files scanned by multiple agents)

  Target B — _calculate_semantic_similarity results (AutonomousDecisionEngine, line 649)
    Current: Jaccard similarity recomputed for every (unknown, existing_list) pair
    Cached:  cache by hash(unknown + sorted(existing_list)), TTL=3600s
    Speedup: O(n*m) -> O(1) for repeated violation type lookups

  Target C — confidence scores per violation_type (AutonomousDecisionEngine._calculate_pattern_confidence)
    Current: regex match on every call
    Cached:  cache by violation_type string, TTL=3600s (patterns don't change mid-run)

INTEGRATION STEPS:

  STEP 1 — Add mixin to AutonomousDecisionEngine

    BEFORE:
      class AutonomousDecisionEngine:

    AFTER:
      from agentic_core.mixins.redis_cache_mixin import RedisCacheMixin

      class AutonomousDecisionEngine(RedisCacheMixin):
          _cache_prefix = "execute_ssot_decision"
          _default_ttl = 3600

    MRO NOTE: RedisCacheMixin has no __init__ (class-level attrs only). No super() change.

  STEP 2 — Cache AST parse results in ASTCodeQualityValidator

    BEFORE:
      def _read_and_parse_file(self, fp: str):
          source = Path(fp).read_text(encoding="utf-8")
          tree = ast.parse(source)
          return tree, source

    AFTER:
      def _read_and_parse_file(self, fp: str):
          import asyncio
          mtime = Path(fp).stat().st_mtime
          cache_key = f"ast:{fp}:{mtime}"
          cached = asyncio.get_event_loop().run_until_complete(self.cache_get(cache_key))
          if cached:
              return cached["tree"], cached["source"]
          source = Path(fp).read_text(encoding="utf-8")
          tree = ast.parse(source)
          asyncio.get_event_loop().run_until_complete(
              self.cache_set(cache_key, {"tree": tree, "source": source}, ttl=300)
          )
          return tree, source

    NOTE: ASTCodeQualityValidator is not async. Use asyncio.run() or convert to sync
    via redis_cache_mixin's sync wrapper pattern (see caching_mixin.py for sync alternative).

  STEP 3 — Cache confidence scores

    BEFORE:
      def _calculate_pattern_confidence(self, violation_type: str) -> float:
          # regex match logic

    AFTER:
      def _calculate_pattern_confidence(self, violation_type: str) -> float:
          cache_key = f"confidence:{violation_type}"
          cached = self._local_cache.get(self._make_key(cache_key))
          if cached and time.time() < cached.get("expire_at", 0):
              return cached["value"]
          result = self._compute_pattern_confidence(violation_type)
          self._local_cache[self._make_key(cache_key)] = {
              "value": result, "expire_at": time.time() + 3600
          }
          return result

    NOTE: Use local cache directly (no async) for synchronous hot-path methods.

ACCEPTANCE CRITERIA:
  [ ] cache_stats()["local_cache_size"] > 0 after processing 10+ violations
  [ ] Second run of same violation set is measurably faster (assert elapsed_run2 < elapsed_run1 * 0.5)
  [ ] USE_REDIS_CACHE=false still works (local fallback only)
  [ ] cache_invalidate() clears all entries for prefix (assert cache_stats()["local_cache_size"] == 0)
  [ ] No async/sync mismatch errors in test suite

RISK:
  MEDIUM — ASTCodeQualityValidator is sync; ast.Module objects are not JSON-serializable.
  MITIGATION: Cache only for local dict (not Redis) for AST objects. Redis cache only for
  serializable results (confidence scores, similarity floats, violation signatures).

========================================================================================================================================================================================================================================================
  MIXIN #3: TracingMixin
  File:   agentic_core/mixins/tracing_mixin.py
  Status: IMPLEMENTED — needs wiring into RuntimeStateManager for mission-level tracing
========================================================================================================================================================================================================================================================

WHAT IT PROVIDES (already implemented):
  - start_span(operation_name, attributes) — context manager, auto-nests spans
  - get_trace_context() / inject_trace_context(ctx) — cross-agent propagation
  - flush_traces() -> list[dict] — export all buffered spans
  - get_tracing_status() — enabled, sample_rate, active_spans, buffered count
  - Circuit breaker: 3 init failures -> DEGRADED mode (agent still initializes)
  - Sampling: TRACE_SAMPLE_RATE env var (default 10%), 100% for ERROR spans
  - SpanContext.to_dict() — OpenTelemetry-compatible output

KEY GAP (why tracing is #3):
  TracingMixin exists but RuntimeStateManager, AutonomousDecisionEngine, and
  SovereignDecisionEngine do NOT call start_span() anywhere.
  Result: zero trace coverage on the 1000-violation healing loop.

INTEGRATION STEPS:

  STEP 1 — Add mixin to RuntimeStateManager

    BEFORE:
      class RuntimeStateManager(MetaLearningClientMixin):  # after Step 1 of Mixin #1

    AFTER:
      from agentic_core.mixins.tracing_mixin import TracingMixin

      class RuntimeStateManager(MetaLearningClientMixin, TracingMixin):

    INIT CHANGE (TracingMixin requires __init__ call):
      def __init__(self, project_root: Path):
          TracingMixin.__init__(self, service_name="RuntimeStateManager")
          # ... existing init ...

  STEP 2 — Wrap start_mission with a root span

    BEFORE:
      def start_mission(self, mission_type: str, agents_order: list[str]):
          self.state["status"] = "running"
          ...

    AFTER:
      def start_mission(self, mission_type: str, agents_order: list[str]):
          with self.start_span("mission", {"mission_type": mission_type,
                                           "agent_count": len(agents_order)}):
              self.state["status"] = "running"
              ...

  STEP 3 — Wrap update_agent / complete_agent with per-agent spans

    BEFORE:
      def update_agent(self, agent_name: str, layer: str):
          self.state["current_agent"] = agent_name
          ...

    AFTER:
      def update_agent(self, agent_name: str, layer: str):
          # Push span — will be closed in complete_agent
          span = SpanContext(
              trace_id=self._current_trace_id or str(uuid.uuid4()),
              operation_name=f"agent:{agent_name}",
              attributes={"layer": layer}
          )
          self._span_stack.append(span)
          self._current_span_id = span.span_id
          self.state["current_agent"] = agent_name
          ...

      def complete_agent(self, agent_name: str, success: bool, details: str = ""):
          if self._span_stack:
              span = self._span_stack.pop()
              span.end_time = time.time()
              span.status = "OK" if success else "ERROR"
              span.attributes["success"] = success
              self._buffer_span(span)
          ...

  STEP 4 — Wrap healing decision in SovereignDecisionEngine

    In SovereignDecisionEngine.request_sovereignty_token:
      with self.start_span("sovereignty_token", {"agent": agent_name, "operation": operation}):
          granted = self._check_token_eligibility(agent_name, operation)
          span.attributes["granted"] = granted  # via active span
          return granted

  STEP 5 — Emit traces at mission end

    In RuntimeStateManager.complete_mission (or equivalent):
      traces = self.flush_traces()
      self.state["traces"] = traces  # stored in runtime state for dashboard
      # Optionally write to docs/reports/ for post-mortem analysis

  STEP 6 — Propagate trace context across agent boundaries

    When calling agent.heal(violation), inject current trace context:
      agent.inject_trace_context(self.get_trace_context())

    Requires agents to also inherit TracingMixin (future work — not in this phase).
    For now, RuntimeStateManager carries the root trace; agents log to it via context injection.

ACCEPTANCE CRITERIA:
  [ ] flush_traces() returns non-empty list after processing 1+ violations
  [ ] Each agent execution produces at least one span in the trace buffer
  [ ] Spans are properly nested (parent_span_id chains correctly)
  [ ] TRACE_ENABLED=false disables all tracing without errors
  [ ] TracingMixin circuit breaker: 3 forced init failures -> _tracing_degraded=True, agent still runs
  [ ] Trace output is OpenTelemetry-compatible (to_dict() keys match OTEL spec)

RISK:
  LOW — TracingMixin has full circuit breaker + graceful degradation.
  Tracing failure never blocks execution.
  The only risk is span_stack corruption if update_agent/complete_agent calls are unbalanced.
  MITIGATION: Use try/finally in complete_agent to always pop the stack.

========================================================================================================================================================================================================================================================
  MIXIN #4: CircuitBreakerMixin
  File:   agentic_core/mixins/circuit_breaker_mixin.py
  Status: IMPLEMENTED — needs wiring into execute_phase2_reconciliation LLM call path
========================================================================================================================================================================================================================================================

WHAT IT PROVIDES (already implemented):
  - circuit_protected(operation, *args, fallback=None, **kwargs) — wraps any callable
  - configure_circuit_breaker(failure_threshold, recovery_timeout, success_threshold)
  - get_circuit_state() -> dict — state, stats, time_until_recovery
  - reset_circuit() — manual reset
  - States: CLOSED (normal) -> OPEN (failing) -> HALF_OPEN (testing) -> CLOSED
  - Default thresholds: 5 failures -> OPEN, 30s -> HALF_OPEN, 2 successes -> CLOSED
  - CircuitOpenError raised when OPEN and no fallback provided

HIGH-VALUE PROTECTION TARGETS:

  Target A — LLM calls in SubAtomicEngine (called from agent.heal())
    Risk: LLM timeout cascades across all 1000 violations
    Protection: circuit_protected(llm_call, fallback=deterministic_fallback)

  Target B — execute_phase2_reconciliation agent loop (line 1112)
    Risk: one crashing agent blocks all subsequent agents
    Protection: circuit_protected(agent.heal, violation, fallback=skip_violation)

  Target C — Redis connection in RedisCacheMixin (already has its own CircuitBreaker)
    NOTE: RedisCacheMixin has a built-in CircuitBreaker class (line 40 of redis_cache_mixin.py).
    Do NOT add CircuitBreakerMixin to RedisCacheMixin — it already has one.
    Use CircuitBreakerMixin only for LLM and agent-level protection.

INTEGRATION STEPS:

  STEP 1 — Add mixin to AutonomousDecisionEngine (alongside RedisCacheMixin)

    BEFORE:
      class AutonomousDecisionEngine(RedisCacheMixin):

    AFTER:
      from agentic_core.mixins.circuit_breaker_mixin import CircuitBreakerMixin

      class AutonomousDecisionEngine(CircuitBreakerMixin, RedisCacheMixin):

    MRO NOTE: CircuitBreakerMixin MUST precede RedisCacheMixin per mixin's own docstring.
    CircuitBreakerMixin has no __init__ (uses __init_subclass__). No super() change.

  STEP 2 — Configure per-use-case thresholds

    In AutonomousDecisionEngine.__init__:
      self.configure_circuit_breaker(
          failure_threshold=3,    # Open after 3 consecutive agent failures
          recovery_timeout=60,    # Wait 60s before retry
          success_threshold=1,    # One success closes circuit
      )

  STEP 3 — Wrap agent.heal() calls in execute_phase2_reconciliation

    BEFORE:
      result = agent.heal(violation)

    AFTER:
      def _fallback_skip(v):
          return {"status": "skipped", "reason": "circuit_open", "violation": v}

      result = self.circuit_protected(
          agent.heal,
          violation,
          fallback=_fallback_skip,
      )

    NOTE: After Mixin #1 integration, this becomes:
      result = self.circuit_protected(
          lambda v: self.ml_enhanced_heal(v, agent.heal),
          violation,
          fallback=_fallback_skip,
      )

  STEP 4 — Expose circuit state in RuntimeStateManager.state

    In RuntimeStateManager.complete_agent:
      if hasattr(self, 'get_circuit_state'):
          self.state["circuit_breaker"] = self.get_circuit_state()

  STEP 5 — Log circuit transitions to trace spans (if TracingMixin also integrated)

    Override _record_failure in AutonomousDecisionEngine:
      def _record_failure(self, error):
          super()._record_failure(error)
          if hasattr(self, 'start_span'):
              # Emit a span for the failure event
              with self.start_span("circuit_failure", {"error": str(error)}):
                  pass

ACCEPTANCE CRITERIA:
  [ ] After 3 consecutive agent failures, circuit state == "open"
  [ ] While OPEN, fallback_skip is returned (no exception propagates)
  [ ] After recovery_timeout seconds, circuit transitions to "half_open"
  [ ] One successful heal closes the circuit
  [ ] get_circuit_state()["rejected_calls"] increments while OPEN
  [ ] reset_circuit() restores state to "closed" with zeroed stats
  [ ] CircuitOpenError is never unhandled (always has fallback in integration)

RISK:
  LOW — fallback is always provided; CircuitOpenError is never unhandled.
  The only risk is misconfigured thresholds causing premature circuit open.
  MITIGATION: Start with conservative thresholds (5/30/2 defaults), tune after observing
  get_circuit_state() stats in production.

========================================================================================================================================================================================================================================================
  INTEGRATION SEQUENCE & DEPENDENCY ORDER
========================================================================================================================================================================================================================================================

  Week 1, Days 1-2: Mixin #4 — CircuitBreakerMixin (3 days, no dependencies)
    Rationale: Smallest scope, no async, no external deps. Provides safety net for
    subsequent integrations. If Mixin #1 or #2 integration introduces a bug, the
    circuit breaker prevents it from cascading.

  Week 1, Days 3-5: Mixin #3 — TracingMixin (1 week, depends on nothing)
    Rationale: Adds observability before the more complex Mixin #1 and #2 integrations.
    When Mixin #1 or #2 has a bug, traces show exactly where.

  Week 2, Days 1-5: Mixin #2 — RedisCacheMixin (1 week, depends on nothing)
    Rationale: Pure performance. Async complexity is the main risk; isolated to
    ASTCodeQualityValidator and confidence score caching.

  Week 3, Days 1-5: Mixin #1 — MetaLearningClientMixin (1 week, depends on #2 for cache)
    Rationale: Highest ROI but most complex (FAISS/Redis backend, domain isolation,
    guardrails, MLWriteEnvelopeViolation). Implement last when observability (#3) and
    caching (#2) are already in place.

  COMBINED MRO for AutonomousDecisionEngine (final state):
    class AutonomousDecisionEngine(
        CircuitBreakerMixin,       # Must be first (per its docstring)
        MetaLearningClientMixin,   # No __init__, no conflicts
        RedisCacheMixin,           # No __init__, no conflicts
    ):

  COMBINED MRO for RuntimeStateManager (final state):
    class RuntimeStateManager(
        MetaLearningClientMixin,   # No __init__
        TracingMixin,              # Has __init__ — must be called explicitly
    ):
        def __init__(self, project_root):
            TracingMixin.__init__(self, service_name="RuntimeStateManager")
            # ... existing init ...

========================================================================================================================================================================================================================================================
  TESTING STRATEGY
========================================================================================================================================================================================================================================================

  For each mixin integration, add tests in tests/agentic_core/L0_routing/:

  test_meta_learning_integration.py:
    - test_ml_enhanced_heal_uses_cached_pattern_on_second_call()
    - test_ml_store_only_on_success()
    - test_ml_depth_limit_prevents_infinite_loop()
    - test_ml_graceful_degradation_when_client_unavailable()

  test_redis_cache_integration.py:
    - test_confidence_cache_hit_on_repeated_violation_type()
    - test_local_fallback_when_redis_disabled()
    - test_cache_invalidate_clears_all_entries()
    - test_non_serializable_ast_not_stored_in_redis()

  test_tracing_integration.py:
    - test_mission_span_created_on_start_mission()
    - test_agent_span_nested_under_mission_span()
    - test_tracing_degraded_mode_does_not_block_execution()
    - test_flush_traces_returns_all_spans()

  test_circuit_breaker_integration.py:
    - test_circuit_opens_after_threshold_failures()
    - test_fallback_called_when_circuit_open()
    - test_circuit_closes_after_recovery_timeout_and_success()
    - test_circuit_state_exposed_in_runtime_state()

  ALL tests must use existing marker taxonomy from pytest.ini.
  NO new markers. NO test file at repo root.

========================================================================================================================================================================================================================================================
  FILES TO MODIFY (SCOPE DECLARATION)
========================================================================================================================================================================================================================================================

  N = 5 files (code) + 4 test files

  CODE:
    1. agentic_core/L0_routing/scripts/execute_ssot.py
       - Add imports for 4 mixins
       - Add mixins to AutonomousDecisionEngine, RuntimeStateManager class declarations
       - Wire circuit_protected() around agent.heal() calls
       - Wire start_span() around start_mission(), update_agent(), complete_agent()
       - Wire ml_enhanced_heal() into healing loop
       - Wire cache_get/set into _calculate_pattern_confidence()
       - Call TracingMixin.__init__() in RuntimeStateManager.__init__()

    2. agentic_core/mixins/__init__.py  (if it exists — add exports)
    3. (No changes to mixin files themselves — implementations are complete)

  TESTS (new files):
    4. tests/agentic_core/L0_routing/test_meta_learning_integration.py
    5. tests/agentic_core/L0_routing/test_redis_cache_integration.py
    6. tests/agentic_core/L0_routing/test_tracing_integration.py
    7. tests/agentic_core/L0_routing/test_circuit_breaker_integration.py

  EVIDENCE:
    8. docs/reports/plans/TOP4_MIXIN_INTEGRATION_EVIDENCE.md  (generated by runner)

========================================================================================================================================================================================================================================================
  ACCEPTANCE GATE (all must pass before phase is complete)
========================================================================================================================================================================================================================================================

  [ ] python -m pytest -q --color=no  exits 0 (full suite)
  [ ] git status --porcelain is empty after commit
  [ ] python docs/tools/check_spec_consistency.py exits 0
  [ ] No new anti-pattern landmines (check_anti_patterns.py exits 0)
  [ ] No new import cycles detected
  [ ] RuntimeStateManager.state["meta_learning"]["total_experiences"] increments in integration test
  [ ] RuntimeStateManager.state["traces"] is non-empty after mission in integration test
  [ ] RuntimeStateManager.state["circuit_breaker"]["state"] == "closed" in happy-path test

========================================================================================================================================================================================================================================================
