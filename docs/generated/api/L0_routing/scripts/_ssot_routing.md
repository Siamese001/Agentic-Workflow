# API Documentation: _ssot_routing

**Target Audience**: developers, api_users

# _ssot_routing API Documentation

**File**: `_ssot_routing.py`
**Classes**: 1
**Functions**: 20

## Classes

- **SovereignDecisionEngine**

## Functions

- **compute_routing_decision** -> RoutingDecision
- **_get_safe_subprocess_run**
- **_decide** -> RoutingDecision
- **__init__**
- **_calculate_semantic_similarity** -> float
- **_get_bmg_cosine_similarity** -> object
- **_get_bmg_embedding_agent_keys** -> frozenset
- **_get_qwen_14b_routing_config** -> tuple
- **_get_qwen_vllm_arbiter**
- **_calculate_pattern_confidence** -> float
- **_compute_novelty_score** -> int
- **_route_decision** -> 'RoutingDecision'
- **_classify_violation_type** -> str
- **_check_healing_budget** -> tuple[bool, str]
- **calculate_healing_confidence** -> ConfidenceScore
- **should_proceed_with_healing** -> tuple[bool, str]
- **_hitl_gate** -> tuple[bool, str]
- **request_sovereignty_token** -> bool
- **release_sovereignty_token** -> None
- **_arbiter** -> dict


## Class: SovereignDecisionEngine

**Description**: 
    [HARDENED] Sovereign Decision Engine with strict token-based access control.
    Synthesizes patterns from FileClassificationAgent for cycle detection and resource protection.
    Unified flat class (formerly AutonomousDecisionEngine -> Enhanced -> Sovereign hierarchy).
    

### Methods

#### __init__
**Parameters**: self, enable_llm, state_mgr, enable_cda, execution_context, healing_memory_retriever, auto_approve

#### _calculate_semantic_similarity
**Parameters**: self, unknown, existing
**Returns**: float
**Description**: Calculate semantic similarity for unknown items against a candidate list.

        Uses BAAI/bge-m3 cosine similarity (GPU-accelerated on RTX 5090).
        Falls back to Jaccard word-overlap only on exception.
        

#### _get_bmg_cosine_similarity
**Returns**: object
**Description**: Lazy seam: load bmg_cosine_similarity from L2 healers without module-level import.

#### _get_bmg_embedding_agent_keys
**Returns**: frozenset
**Description**: Lazy seam: load BMG_EMBEDDING_AGENT_KEYS from L2 healing_tier_config.

#### _get_qwen_14b_routing_config
**Returns**: tuple
**Description**: Lazy seam: load Qwen 14B routing constants from L2 healing_tier_config.

#### _get_qwen_vllm_arbiter
**Description**: Lazy seam: return callable that invokes Qwen 14B via WSL vLLM subprocess.

#### _calculate_pattern_confidence
**Parameters**: self, violation_type
**Returns**: float
**Description**: Regex-based pattern matching for known violation types.

#### _compute_novelty_score
**Parameters**: self, failure_type, territory, confidence
**Returns**: int
**Description**: Compute the novelty score N (0-3) for RoutingInputs.

        Embeds the current failure signal text and compares against stored
        vectors to produce a true novelty score:
          N=0  max_similarity >= 0.85  (seen before)
          N=1  max_similarity >= 0.70  (similar)
          N=2  max_similarity >= 0.50  (somewhat novel)
          N=3  max_similarity <  0.50  (highly novel)

        Raises VectorSourceMismatchError if stored vectors and the current
        vector have incompatible dimensions.
        

#### _route_decision
**Parameters**: self, confidence, agent_name, territory, failure_type, retry_count, replay_mode, playbook_match, deterministic_coverage, provider_prohibited_gemini, provider_prohibited_qwen
**Returns**: 'RoutingDecision'
**Description**: Map healing context to a hardened SSOT RoutingDecision.

#### _classify_violation_type
**Parameters**: self, message
**Returns**: str
**Description**: Classify a violation message into a canonical violation type string.

#### _check_healing_budget
**Parameters**: self, agent_name, depth, max_depth
**Returns**: tuple[bool, str]
**Description**: Prevents infinite healing loops and budget exhaustion.

#### calculate_healing_confidence
**Parameters**: self, violations_count, violation_types, territory, historical_success_rate, agent_name
**Returns**: ConfidenceScore
**Description**: Calculates weighted confidence score.

        Uses GPU-accelerated BAAI/bge-m3 cosine similarity for pattern matching
        when agent_name is in BMG_EMBEDDING_AGENT_KEYS.
        

#### should_proceed_with_healing
**Parameters**: self, confidence, agent_name, territory, failure_type, retry_count, replay_mode, playbook_match, deterministic_coverage, provider_prohibited_gemini, provider_prohibited_qwen
**Returns**: tuple[bool, str]
**Description**: Determines if healing should proceed using the hardened SSOT routing algorithm.

#### _hitl_gate
**Parameters**: self, agent_name, confidence, tier
**Returns**: tuple[bool, str]
**Description**: 
        HITL terminal gate for medium/low confidence healing decisions.

        Prints a structured prompt showing the agent, confidence score, and
        reasoning, then reads Y/N/D from stdin. Non-interactive environments
        (no tty) default to DEFER (reject).

        Returns:
            (approved: bool, reason: str)
        

#### request_sovereignty_token
**Parameters**: self, agent_name, operation
**Returns**: bool
**Description**: 
        Request permission to perform a state-mutating operation.
        Enforces atomic locking and stack depth limits.
        

#### release_sovereignty_token
**Parameters**: self, agent_name, success
**Returns**: None
**Description**: Release the lock after operation completion.



## Function: compute_routing_decision

**Parameters**: inputs
**Returns**: RoutingDecision
**Description**: Pure SSOT routing function — strict gate order, no side effects.



## Function: _get_safe_subprocess_run



## Function: _decide

**Parameters**: tier, gate, score
**Returns**: RoutingDecision


## Function: __init__

**Parameters**: self, enable_llm, state_mgr, enable_cda, execution_context, healing_memory_retriever, auto_approve


## Function: _calculate_semantic_similarity

**Parameters**: self, unknown, existing
**Returns**: float
**Description**: Calculate semantic similarity for unknown items against a candidate list.

        Uses BAAI/bge-m3 cosine similarity (GPU-accelerated on RTX 5090).
        Falls back to Jaccard word-overlap only on exception.
        



## Function: _get_bmg_cosine_similarity

**Returns**: object
**Description**: Lazy seam: load bmg_cosine_similarity from L2 healers without module-level import.



## Function: _get_bmg_embedding_agent_keys

**Returns**: frozenset
**Description**: Lazy seam: load BMG_EMBEDDING_AGENT_KEYS from L2 healing_tier_config.



## Function: _get_qwen_14b_routing_config

**Returns**: tuple
**Description**: Lazy seam: load Qwen 14B routing constants from L2 healing_tier_config.



## Function: _get_qwen_vllm_arbiter

**Description**: Lazy seam: return callable that invokes Qwen 14B via WSL vLLM subprocess.



## Function: _calculate_pattern_confidence

**Parameters**: self, violation_type
**Returns**: float
**Description**: Regex-based pattern matching for known violation types.



## Function: _compute_novelty_score

**Parameters**: self, failure_type, territory, confidence
**Returns**: int
**Description**: Compute the novelty score N (0-3) for RoutingInputs.

        Embeds the current failure signal text and compares against stored
        vectors to produce a true novelty score:
          N=0  max_similarity >= 0.85  (seen before)
          N=1  max_similarity >= 0.70  (similar)
          N=2  max_similarity >= 0.50  (somewhat novel)
          N=3  max_similarity <  0.50  (highly novel)

        Raises VectorSourceMismatchError if stored vectors and the current
        vector have incompatible dimensions.
        



## Function: _route_decision

**Parameters**: self, confidence, agent_name, territory, failure_type, retry_count, replay_mode, playbook_match, deterministic_coverage, provider_prohibited_gemini, provider_prohibited_qwen
**Returns**: 'RoutingDecision'
**Description**: Map healing context to a hardened SSOT RoutingDecision.



## Function: _classify_violation_type

**Parameters**: self, message
**Returns**: str
**Description**: Classify a violation message into a canonical violation type string.



## Function: _check_healing_budget

**Parameters**: self, agent_name, depth, max_depth
**Returns**: tuple[bool, str]
**Description**: Prevents infinite healing loops and budget exhaustion.



## Function: calculate_healing_confidence

**Parameters**: self, violations_count, violation_types, territory, historical_success_rate, agent_name
**Returns**: ConfidenceScore
**Description**: Calculates weighted confidence score.

        Uses GPU-accelerated BAAI/bge-m3 cosine similarity for pattern matching
        when agent_name is in BMG_EMBEDDING_AGENT_KEYS.
        



## Function: should_proceed_with_healing

**Parameters**: self, confidence, agent_name, territory, failure_type, retry_count, replay_mode, playbook_match, deterministic_coverage, provider_prohibited_gemini, provider_prohibited_qwen
**Returns**: tuple[bool, str]
**Description**: Determines if healing should proceed using the hardened SSOT routing algorithm.



## Function: _hitl_gate

**Parameters**: self, agent_name, confidence, tier
**Returns**: tuple[bool, str]
**Description**: 
        HITL terminal gate for medium/low confidence healing decisions.

        Prints a structured prompt showing the agent, confidence score, and
        reasoning, then reads Y/N/D from stdin. Non-interactive environments
        (no tty) default to DEFER (reject).

        Returns:
            (approved: bool, reason: str)
        



## Function: request_sovereignty_token

**Parameters**: self, agent_name, operation
**Returns**: bool
**Description**: 
        Request permission to perform a state-mutating operation.
        Enforces atomic locking and stack depth limits.
        



## Function: release_sovereignty_token

**Parameters**: self, agent_name, success
**Returns**: None
**Description**: Release the lock after operation completion.



## Function: _arbiter

**Parameters**: agent_name, violation_types, territory, score, gate
**Returns**: dict


## Usage Examples

### Class Usage

```python
# Using SovereignDecisionEngine
sovereigndecisionengine = SovereignDecisionEngine()
sovereigndecisionengine.calculate_healing_confidence()
sovereigndecisionengine.should_proceed_with_healing()
```

### Function Usage

```python
# Using compute_routing_decision
result = compute_routing_decision(inputs)
```

```python
# Using _get_safe_subprocess_run
result = _get_safe_subprocess_run()
```

```python
# Using _decide
result = _decide(tier, gate)
```



---
**Generated**: 2026-03-26T09:39:03.375579
**Type**: api_reference
**Quality**: comprehensive
