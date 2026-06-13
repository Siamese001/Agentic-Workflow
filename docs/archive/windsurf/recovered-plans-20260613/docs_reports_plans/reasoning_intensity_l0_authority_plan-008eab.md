# L0 Authority-Based Reasoning Intensity Calibration Plan (Hardened)

This plan establishes L0 as the authoritative policy engine for deterministic reasoning intensity calibration with versioned profiles, pure-function complexity scoring, and fail-closed enforcement across the architectural stack.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Architecture Analysis Summary

**Current State:** Static configuration in apps_lic/rg with environment-based presets, no runtime adaptation, and inconsistent reasoning intensity across applications.

**Key Insight:** L0 routing already contains the authority patterns (arbitration, policy enforcement, signed artifacts) needed for deterministic reasoning intensity governance.

## Proposed Architecture

### A) L0: ReasoningPolicyEngine (Authoritative)
**Location:** `agentic_core/L0_routing/engines/reasoning_policy_engine.py`

**Inputs (deterministic & capturable):**
- Request structure features (size, tool count, risk tier)
- L4 active config/budgets (token caps, rate limits)
- Aggregated L6/L4 outcome metrics (windowed, versioned)

**Output (sealed + versioned):**
- `ReasoningIntensityProfile` with cryptographic binding
- Required fields: `reasoning_profile_version`, `reasoning_policy_hash`, `profile_hash`
- `profile_hash = SHA256(deterministic_serialization(profile))`
- Parameters: max branches/depth, reflection enable/disable, token budgets per stage, allowed reasoning modes
- Coarse-grained tiers: LOW/MEDIUM/HIGH/CRITICAL (no micro-adjustments)

### B) L3: ReasoningIntensityEnforcer (Operational)
**Location:** `agentic_core/L3_orchestration/engines/reasoning_intensity_enforcer.py`

**Responsibilities:**
- Enforce branch/depth ceilings with **fail-closed** behavior (HARD STOP on violation)
- **No upward mutation**: cannot increase branches/depth, enable reflection, or switch modes
- May only reduce execution if budget constrained
- Emit **non-authoritative telemetry** (cannot influence current run, only future L0 calibrations)
- Record enforcement compliance with profile_hash in execution trace

### C) apps_lic/apps_rg: Consume-Only
**Changes:**
- Replace `get_toggles()` from env with profile injection from governed payload
- HOPPipelineExecutor accepts read-only `ReasoningIntensityProfile`
- Static config becomes defaults-only; runtime values from stamped profile

## Implementation Scope

### Phase 1: Contract Definition
1. **Define `ReasoningIntensityProfile`** in shared contracts module
   - Required fields: `reasoning_profile_version`, `reasoning_policy_hash`, `profile_hash`
   - Parameters: max_branches, max_depth, enable_reflection, token_budget_per_stage, allowed_modes
   - Immutable dataclass with deterministic serialization
   - Coarse-grained tiers: LOW/MEDIUM/HIGH/CRITICAL

2. **Create `SignedExecutionEnvelope`** (first-class sealed contract)
   ```
   SignedExecutionEnvelope:
       route_decision: RouteDecisionArtifact
       reasoning_profile: ReasoningIntensityProfile
       enforcement_constraints: dict
       policy_hash: str
       signature: str
   ```

3. **Extend existing L0 routing contracts** with profile hash binding
   - Include profile_hash in execution trace and replay key
   - Integration with existing policy hash and signature mechanisms

### Phase 2: L0 Policy Engine
1. **Create ReasoningPolicyEngine** in L0 routing
   - **Pure-function complexity scoring**: `complexity_score = f(request_structure, risk_tier, tool_count, input_length, l4_budget_state)`
   - No runtime heuristics, time-based signals, adaptive decay, or stochastic weighting
   - Deterministic calibration using L4 budget state + versioned aggregated metrics
   - Profile computation with cryptographic signing

2. **Integrate with existing L0 arbitration**
   - Leverage `arbitration_contract.py` patterns for multi-advisor input
   - Use existing policy enforcement and signing infrastructure

### Phase 3: L3 Enforcement
1. **Create ReasoningIntensityEnforcer** in L3 orchestration
   - Profile validation and **fail-closed constraint enforcement**
   - HARD STOP on branch/depth/token budget violations (no silent truncation or fallback)
   - Integration with existing `NervousSystemAgent` orchestration
   - Telemetry emission using existing `TelemetryEmitter` patterns (non-authoritative)

2. **Update orchestration flow**
   - Profile extraction from `SignedExecutionEnvelope`
   - Constraint enforcement during HOP stage execution with deterministic failure states
   - Compliance recording with profile_hash in execution trace and replay key

### Phase 4: Apps Integration
1. **Refactor apps_lic reasoning toggles**
   - Make `reasoning_toggles_config.py` defaults-only
   - Update `HOPPipelineExecutor` to accept injected profile
   - Remove environment-based factory patterns

2. **Refactor apps_rg reasoning toggles**
   - Similar consume-only pattern
   - Update `ResumeOrchestratorEngine` to use profile constraints
   - Preserve existing validation logic

## Determinism & Auditability

**Deterministic Calibration:**
- Pure-function complexity scoring: same inputs = same profile
- No C0 embedding dependencies or runtime memory
- All calibration inputs captured in execution snapshot
- Profile hash included in replay key for byte-for-byte reproducibility

**Audit Trail:**
- `SignedExecutionEnvelope` with cryptographic binding
- Profile signed with L0 policy hash (existing mechanisms)
- L3 enforcement actions with profile_hash in execution trace
- apps_* consumption logged as read-only operations

**Fail-Closed Enforcement:**
- HARD STOP on any constraint violation
- No silent truncation, reflection fallback, or mode downgrade
- Deterministic failure states preserved in audit trail

## Governance Compliance

**L0 Authority:** Pure-function policy computation with cryptographic signing
**L3 Operational:** Fail-closed enforcement with non-authoritative telemetry
**Apps Separation:** Read-only consumption, no authority or mutation capability
**C0 Boundary:** Explicit prohibition of embedding-driven policy decisions
**Policy Sovereignty:** No upward mutation across layers, L3 may only reduce execution

## Determinism Validation Test

**Required Test:**
1. Run identical request twice with same L4 state
2. Capture and compare byte-for-byte:
   - `reasoning_profile_hash`
   - `route_hash`
   - `enforcement_trace_hash`
3. All hashes must match exactly or calibration logic is leaking non-determinism

## Success Criteria

1. **Deterministic:** Identical inputs produce identical reasoning profiles (byte-for-byte)
2. **Auditable:** Full reasoning intensity decision trail with cryptographic binding
3. **Compliant:** L0 decides, L3 enforces fail-closed, apps_* consume-only
4. **Adaptive:** Runtime calibration from pure-function complexity + L4 state
5. **Backwards Compatible:** Existing static configs become fallback defaults
6. **Fail-Closed:** HARD STOP on violations with deterministic failure states
7. **Sovereign:** No upward policy mutation across layers

This hardened architecture eliminates environment toggle drift, centralizes reasoning intensity under sovereign L0 control, and provides production-grade determinism with full auditability.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

