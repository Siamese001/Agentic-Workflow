# Resume Generation Engine v9.7 - P0 Enhancements

**Version:** 9.7.0-p0-enhancements  
**Date:** November 2025  
**Status:** Production-Ready with Critical Architectural Improvements

## 🎯 Executive Summary

Version 9.7 implements all **Priority 0 (P0) enhancements** identified in the architectural review, delivering critical upgrades that address fundamental gaps in the v9.6 codebase. These changes represent the minimum viable improvements required for a production-grade, enterprise-ready AI system.

### P0 Enhancements Delivered

| Priority | Enhancement | Impact | Effort | Status |
|----------|------------|--------|--------|--------|
| P0 | **SafetyGuardStack** | Very High | High | ✅ Complete |
| P0 | **Tree-of-Thoughts Strategist** | High | Medium | ✅ Complete |
| P0 | **LLM-Driven Prompt Engineer** | High | Low | ✅ Complete |
| P0 | **Local Self-Correction Loops** | High | Low | ✅ Complete |

---

## 🏗️ Architectural Changes

### 1. SafetyGuardStack (P0 Item #1)

**Problem Solved:** v9.6 mixed safety concerns (bias detection) into the QA validation stack, violating separation of concerns.

**Solution:**
- Created dedicated `SafetyGuardStack` with architectural separation
- **BiasDetectorAgent**: LLM-based bias detection (age, gender, cultural, accessibility, socioeconomic)
- **PIISanitizerAgent (Enhanced)**: More sophisticated PII detection and sanitization
- Safety checks run **before** QA validation in the graph flow
- Independent configuration flags: `agent_stacks.safety_stack_enabled`, `agent_stacks.pii_detection_enabled`

**Code References:**
- `core_v9_7.py`: Lines 440-510 (System prompts)
- `agent_swarm_v9_7.py`: Lines 30-125 (Agent implementations)
- Graph node: `run_safety_guard_stack`

**Configuration:**
```json
"agent_stacks": {
  "safety_stack_enabled": true,
  "bias_detection_threshold": 0.7,
  "pii_detection_enabled": true
}
```

---

### 2. Tree-of-Thoughts Strategist (P0 Item #2)

**Problem Solved:** v9.6's `ThemeClassifierAgent` was a single-path, low-intelligence agent. The workflow's entire "IQ" depended on this weak link.

**Solution:**
- **ToTStrategistAgent** replaces `ThemeClassifierAgent`
- Generates **N** distinct strategic approaches (branching factor: 3 default)
- Evaluates each strategy on 4 dimensions: relevance, credibility, differentiation, risk
- Selects optimal strategy via weighted scoring
- Uses Claude Sonnet 4 at temp=0.8 for creative strategy generation

**Code References:**
- `core_v9_7.py`: Lines 512-600 (ToT system prompt)
- `agent_swarm_v9_7.py`: Lines 130-190 (ToTStrategistAgent)
- Graph node: `run_tot_strategy`

**Configuration:**
```json
"agent_stacks": {
  "strategy_tot_enabled": true,
  "strategy_tot_branching_factor": 3,
  "strategy_tot_depth": 2
}
```

**State Schema Changes:**
```python
class MainGraphState(TypedDict):
    # ... existing fields ...
    strategy_thoughts: List[Dict[str, Any]]  # NEW: ToT candidates
    selected_strategy: Optional[Dict[str, Any]]  # NEW: Best strategy path
```

---

### 3. LLM-Driven Prompt Engineer (P0 Item #3)

**Problem Solved:** v9.6's `PromptStackAgent` was just a Python string formatter (score: 5/100). This was the cheapest, easiest upgrade for massive quality gains.

**Solution:**
- **DynamicPromptEngineerAgent** replaces `PromptStackAgent`
- LLM-crafted prompts using prompt engineering best practices:
  - Persona setting, task decomposition, constraint specification
  - Few-shot learning, output formatting, chain-of-thought reasoning
- Uses Claude Sonnet 4 at configurable temperature (default: 0.7)
- Outputs engineered prompt + estimated quality score

**Code References:**
- `core_v9_7.py`: Lines 602-680 (Prompt engineering system prompt)
- `agent_swarm_v9_7.py`: Lines 195-255 (DynamicPromptEngineerAgent)
- Graph node: `run_prompt_engineer`

**Configuration:**
```json
"agent_stacks": {
  "prompt_llm_driven": true,
  "prompt_temperature": 0.7
}
```

---

### 4. Local Self-Correction Loops (P0 Item #4)

**Problem Solved:** v9.6 routed all bullet critique failures to the main `replanner`, causing expensive, high-latency global replans for minor issues.

**Solution:**
- **BulletCritiqueAgent**: Evaluates bullets on 6 dimensions (relevance, impact, specificity, credibility, length, grammar)
- **Acceptance threshold**: 7.0/10 average score
- **Local retry loop**: Up to 2 retries (configurable) before proceeding
- Adds `check_bullet_critique` conditional edge to graph
- Uses Gemini 2.0 Flash at temp=0.2 for consistent evaluation

**Code References:**
- `core_v9_7.py`: Lines 682-740 (Bullet critique system prompt)
- `agent_swarm_v9_7.py`: Lines 260-315 (BulletCritiqueAgent)
- Graph nodes: `run_bullet_critique`, `check_bullet_critique`, `increment_local_retry`

**Configuration:**
```json
"agent_stacks": {
  "enable_local_retries": true,
  "max_local_retries": 2
}
```

**State Schema Changes:**
```python
class MainGraphState(TypedDict):
    # ... existing fields ...
    local_retry_count: int  # NEW: Track local retries
    bullet_critique_history: List[Dict[str, Any]]  # NEW: Critique history
```

---

## 📊 Updated Graph Flow

```
Entry → parse_jd → tot_strategy → prompt_engineer → rag_search 
  → bullet_generation → bullet_critique
      ↓ (if fails & retries < max)
  increment_local_retry → (loop back to bullet_generation)
      ↓ (if passes or max retries)
  compile_draft → safety_guard_stack → qa_validation → END
```

**Key Changes:**
1. `tot_strategy` replaces old `theme_classifier`
2. `prompt_engineer` replaces old `prompt_stack`
3. `bullet_critique` + conditional loop added
4. `safety_guard_stack` inserted before QA

---

## 📁 File Structure

```
v9.7/
├── core_v9_7.py                 # Core framework (791 lines)
│   ├── Enhanced config system with AgentStackConfig
│   ├── P0 system prompts (5 new prompts)
│   ├── Updated MainGraphState schema
│   └── Model client factory
│
├── agent_swarm_v9_7.py          # Agent implementations (760 lines)
│   ├── BiasDetectorAgent
│   ├── PIISanitizerAgent (enhanced)
│   ├── ToTStrategistAgent
│   ├── DynamicPromptEngineerAgent
│   ├── BulletCritiqueAgent
│   ├── Existing agents (updated)
│   └── Graph construction with P0 enhancements
│
├── main_v9_7.py                 # Entry point (378 lines)
│   ├── Updated imports
│   ├── Enhanced summary output with P0 stats
│   └── Version tracking (9.7.0-p0-enhancements)
│
├── run_batch_v9_7.py            # Batch processing (207 lines)
│   └── Updated for v9.7 imports and state schema
│
├── run_learning_v9_7.py         # Meta-learning (287 lines)
│   └── Updated for v9.7 imports (no functional changes)
│
├── master_config_v9_7.json      # Configuration (159 lines)
│   ├── agent_stacks section (P0 configs)
│   ├── model_config section (per-agent model assignments)
│   └── p0_enhancements_summary section (documentation)
│
└── README_v9_7.md               # This file
```

**Total Lines of Code:** ~2,582 lines (production-grade, zero mock data)

---

## 🚀 Usage

### Single Job Execution

```bash
# Basic usage
python main_v9_7.py -j job_input.json -m master_resume.json

# With debug logging
python main_v9_7.py -j job_input.json --debug

# Custom output directory
python main_v9_7.py -j job_input.json -o /path/to/output
```

### Batch Processing

```bash
# Place job JSONs in batch_queue/
python run_batch_v9_7.py
```

### Configuration

Edit `master_config_v9_7.json` to toggle P0 enhancements:

```json
"agent_stacks": {
  "safety_stack_enabled": true,      // Toggle SafetyGuardStack
  "strategy_tot_enabled": true,      // Toggle Tree-of-Thoughts
  "prompt_llm_driven": true,         // Toggle LLM-driven prompting
  "enable_local_retries": true       // Toggle local self-correction
}
```

---

## 🔬 Testing Recommendations

### Unit Tests
```python
# Test BiasDetectorAgent
from agent_swarm_v9_7 import BiasDetectorAgent
agent = BiasDetectorAgent({})
result = agent.run("Test content with potential age bias: seasoned professional")
assert result["bias_detected"] == True

# Test ToTStrategistAgent
from agent_swarm_v9_7 import ToTStrategistAgent
agent = ToTStrategistAgent({})
result = agent.run(master_resume, job_input)
assert len(result["strategy_thoughts"]) == 3  # Branching factor
assert "selected_strategy" in result
```

### Integration Tests
```bash
# Test full workflow with P0 enhancements enabled
python main_v9_7.py -j test_job.json -m test_resume.json --debug

# Verify local retry loop triggered
grep "Local retry triggered" logs/workflow_v9_7.log
```

### Performance Tests
```bash
# Benchmark with vs. without P0 enhancements
# Disable all P0 features in config, measure time/cost
# Re-enable features one-by-one, measure impact
```

---

## 📈 Expected Improvements

| Metric | v9.6 Baseline | v9.7 Target | Measurement |
|--------|---------------|-------------|-------------|
| Strategy Quality Score | 11/100 | 85+/100 | Human evaluation of positioning |
| Prompt Quality Score | 5/100 | 75+/100 | LLM-as-judge evaluation |
| Local Error Recovery | 0% | 60%+ | % of critiques resolved locally |
| Safety Coverage | Partial | 95%+ | % of bias/PII issues flagged |
| Overall Draft Quality | Baseline | +30-50% | Composite score (relevance, impact, credibility) |

---

## 🛣️ Roadmap: P1 & P2 Enhancements

### Priority 1 (Next)
- **Upgrade Conductors to ReAct Agents**: Make DraftingConductor and QAConductor true step-by-step reasoning agents
- **DynamicToolingStack**: Tool selection, execution, and generation (vs. hard-coded tools)
- **HIL_InteractionStack**: Proactive ambiguity detection and collaborative feedback routing

### Priority 2 (Future)
- **Evolve RAGStack**: Add HyDE query enrichment and cross-encoder re-ranker
- **Dynamic Agent Selection**: Read `feedback_log.jsonl` for reliability-based agent routing
- **In-flight Cost Tracking**: Per-agent cost monitoring and circuit breakers

---

## 🐛 Known Limitations

1. **No HIL in v9.7**: Human-in-the-loop removed to focus on batch automation. Will be reintroduced in P1 with enhanced interaction stack.

2. **Conductors Still Plan Executors**: DraftingConductor and QAConductor execute static plans vs. dynamic reasoning (P1 upgrade).

3. **RAG Still Basic**: Keyword matching vs. embeddings + re-ranking (P2 upgrade).

4. **No In-Flight Cost Tracking**: Only pre-flight cost ceiling checks (P1 upgrade).

5. **Meta-Loop Not Closed**: Dynamic agent selection based on feedback not yet implemented (P2 upgrade).

---

## 🔒 Safety & Compliance

### PII Handling
- All PII detection/sanitization happens **before** external LLM API calls
- PII mapping stored in blackboard for potential restoration (user-approved)
- SSN, DOB, government IDs **always** redacted

### Bias Detection
- 5 categories: age, gender, cultural, accessibility, socioeconomic
- Threshold: 0.7 (configurable)
- Actionable recommendations for remediation

### Provenance Tracking
- All agent actions logged to `provenance_ledger`
- Full audit trail for regulatory compliance

---

## 📝 Migration from v9.6

1. **Update imports:**
   ```python
   # Old
   from core_v9_6 import CONFIG
   from agent_swarm_v9_6 import get_graph_app
   
   # New
   from core_v9_7 import CONFIG
   from agent_swarm_v9_7 import get_graph_app
   ```

2. **Update state initialization:**
   ```python
   inputs = {
       # ... existing fields ...
       # Add P0 fields:
       "strategy_thoughts": [],
       "selected_strategy": None,
       "local_retry_count": 0,
       "bullet_critique_history": []
   }
   ```

3. **Update config file:**
   - Rename `master_config_v9_6.json` → `master_config_v9_7.json`
   - Add `agent_stacks` section (see template in config file)

4. **Test thoroughly:**
   - Run single job with debug logging
   - Verify P0 enhancements active in summary output
   - Check logs for new agent activity

---

## 🤝 Contributing

This is production code with zero tolerance for:
- Mock/placeholder data
- Architectural shortcuts
- Silent failures
- Cost/time tradeoffs at expense of quality

All changes must:
1. Include complete, untruncated implementations
2. Update all version numbers (9.6 → 9.7)
3. Add comprehensive logging
4. Update this README with new features

---

## 📄 License

Proprietary - Unify Consulting  
Chief AI Officer: Amit Ayer

---

## 📞 Support

For questions or issues:
- Review logs: `./logs/workflow_v9_7.log`
- Check config: `master_config_v9_7.json`
- Debug mode: `python main_v9_7.py --debug`

---

**Version 9.7.0-p0-enhancements** | Built with rigorous standards. Zero compromises.
