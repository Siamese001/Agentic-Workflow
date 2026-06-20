---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-lic-signal-enhancements-p2p3-f4b8d1.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-lic-signal-enhancements-p2p3-f4b8d1.md'
source_sha256: 676ee67771d29edcce69883dcf82dea8fd9f8dc85338004d8567ec6d6f30475b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_lic Signal Enhancements — P2 and P3

**Plan slug:** `apps-lic-signal-enhancements-p2p3-f4b8d1`
**Parent plan:** `apps-lic-canonical-spine-wireup-e7c2a5`
**Status:** Not Started
**Domain:** `apps_lic` outreach signal elevation — P2 (high) + P3 (medium) priority enhancements
**Precondition:** Parent plan W7 + W8 (P0+P1 enhancements) MUST be complete before W3 and W4 here.

> **Use case context:** Outreach message targeting SVP Agentic Engineering positions. Signal = `P(reply | message)` for a senior engineering leader who has scanned 200+ messages. P0/P1 addressed the floor (anti-patterns removed, proof present). P2/P3 address the ceiling (narrative coherence, adaptive tone, situational intelligence, multi-channel strategy).

---

## SR_SUMMARY

This plan extends `apps_lic` with P2 (high-signal, medium-effort) and P3 (medium-signal, higher-effort) enhancements after P0/P1 foundation is proven. P2 focuses on message arc coherence, archetype-adaptive tone calibration, and competitive landscape narrative. P3 focuses on multi-touch follow-up sequencing, application-status-aware resurfacing, and mutual-intelligence-network mapping.

**Prerequisite:** `apps-lic-canonical-spine-wireup-e7c2a5` W7 + W8 DONE.

---

## Files In Scope

**New files (P2 — W1+W2):**
- `apps_lic/engines/narrative_arc_engine.py`
- `apps_lic/engines/archetype_tone_calibrator.py`
- `apps_lic/engines/competitive_landscape_engine.py`
- `apps_lic/config/archetype_tone_table.yaml`
- `tests/governance/test_apps_lic_signal_p2.py`

**New files (P3 — W3+W4):**
- `apps_lic/engines/multi_touch_sequence_planner.py`
- `apps_lic/engines/status_aware_resurfacer.py`
- `apps_lic/engines/mutual_network_mapper.py`
- `apps_lic/config/multi_touch_policy.yaml`
- `apps_lic/config/resurfacing_triggers.yaml`
- `tests/governance/test_apps_lic_signal_p3.py`

**Edit (P2):**
- `apps_lic/engines/HOP4DraftAgent.py` — integrate NarrativeArcEngine before draft assembly
- `apps_lic/engines/HOP3SenderGroundingAgent.py` — integrate ArchetypeToneCalibratorEngine
- `apps_lic/config/exit_rubric.yaml` — add `narrative_coherence` + `tone_register_fit` dims

**Edit (P3):**
- `apps_lic/integrations/governed_lic_run.py` — add optional `multi_touch_mode` flag
- `apps_lic/config/exit_rubric.yaml` — add `sequence_position_fit` dim

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W1** | P2a, P2b | P2 Message Arc + Archetype Tone Calibration | ~25k | P0/P1 in parent plan delivered; `SenderCredibilityCard` and `RecipientTriggerVector` available as context inputs | Not Started | `NarrativeArcEngine` produces opener→hook→proof→ask arc with explicit transitions; `ArchetypeToneCalibrator` selects correct register per archetype; 4 sentinel tests pass |
| **W2** | P2c, P2-tests | P2 Competitive Landscape Narrative + P2 test suite | ~20k | `apps_research` competitive briefing exposed via managed workflow; P2a+P2b complete | Not Started | `CompetitiveLandscapeEngine` produces 1-sentence differentiator per target company; no fabricated competitor facts; 3 sentinel tests pass |
| **W3** | P3a, P3b | P3 Multi-Touch Sequence Planner + Status-Aware Resurfacer | ~30k | Application status field in `PreloadedOutreachContextManifest` available; multi-touch policy externalized | Not Started | `MultiTouchSequencePlanner` produces 3-message sequence for cold-initial case; `StatusAwareResurfacer` generates correct message type for each application status transition; 5 sentinel tests pass |
| **W4** | P3c, P3-tests | P3 Mutual Network Mapper + P3 test suite | ~25k | `apps_research` can return mutual connection signals; `master_resume.json` career graph accessible | Not Started | `MutualNetworkMapper` surfaces ≥1 connection path per target company with evidence; 3 sentinel tests pass |
| **W5** | V1 | Final verification + Notion writeback | ~10k | Notion APIs reachable; parent plan still In Progress in Notion | Not Started | All 15 new tests pass; exit rubric extended to 17 dims; Notion registered |

**Total est tokens:** ~110k.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| **P2a** | Narrative Arc Engine | `apps_lic/engines/narrative_arc_engine.py` (NEW); integrate into `HOP4DraftAgent.py` | Message sections exist but have no arc binding — opener may contradict proof, ask may not follow from hook; structural arc enforcer needed | 12k | Not Started |
| **P2b** | Archetype Tone Calibrator | `apps_lic/engines/archetype_tone_calibrator.py` (NEW); `apps_lic/config/archetype_tone_table.yaml` (NEW); integrate into `HOP3SenderGroundingAgent.py` | Current tone guidance is fixed per channel; must vary by recipient archetype (technical builder, business executive, research-academic, recruiter) | 13k | Not Started |
| **P2c** | Competitive Landscape Narrative | `apps_lic/engines/competitive_landscape_engine.py` (NEW) | Requires managed workflow (`apps_research` briefing) for company data; must produce exactly 1 differentiator sentence; cannot fabricate | 10k | Not Started |
| **P2-tests** | P2 test suite (7 tests) | `tests/governance/test_apps_lic_signal_p2.py` | Test fixtures for NarrativeArc, ArchetypeTone, CompetitiveLandscape; verifies Exit V6 dim binding | 10k | Not Started |
| **P3a** | Multi-Touch Sequence Planner | `apps_lic/engines/multi_touch_sequence_planner.py` (NEW); `apps_lic/config/multi_touch_policy.yaml` (NEW) | Only first message in scope of parent plan; follow-up 2 and 3 require stateful sequencing; each touch must have different hook, different ask, declining ask scope | 15k | Not Started |
| **P3b** | Status-Aware Resurfacer | `apps_lic/engines/status_aware_resurfacer.py` (NEW); `apps_lic/config/resurfacing_triggers.yaml` (NEW) | Application status changes (applied→screened, screened→rejected, rejected→new-req-opened) require entirely different message type; cannot reuse first-contact draft | 15k | Not Started |
| **P3c** | Mutual Network Mapper | `apps_lic/engines/mutual_network_mapper.py` (NEW) | Career graph inference from public signals (shared employer history, conference co-speakers, open-source co-contributors); no LinkedIn API assumed; signal must be from `apps_research` briefing | 12k | Not Started |
| **P3-tests** | P3 test suite (8 tests) | `tests/governance/test_apps_lic_signal_p3.py` | Test fixtures for MultiTouch, StatusAware, MutualNetwork; verifies policy YAML binding + Exit dim | 13k | Not Started |
| **V1** | Final verification | exit rubric YAML + Notion | 17-dim rubric, 15 new tests, no regressions in parent plan test suite | 10k | Not Started |

---

## P2 Signal Enhancements — Specification

### P2a: Narrative Arc Engine

**File:** `apps_lic/engines/narrative_arc_engine.py` (NEW)
**Integration:** `apps_lic/engines/HOP4DraftAgent.py` — pre-assembly context

**Signal problem:** Even with correct content, a message with misaligned arc is deleted in 15 seconds. The four arc failures at SVP level: (1) opener repeats resume intro rather than leading with recipient context, (2) proof section disconnected from hook topic, (3) ask scope doesn't follow from value proposition, (4) closing dilutes the ask.

**NarrativeArc contract:**
```python
@dataclass(frozen=True)
class MessageSection:
    section_id: str          # opener | hook | proof | ask | close
    required_input: str      # what this section must reference (e.g., "trigger_id", "claim_id")
    forbidden_inputs: List[str]  # what breaks the arc (e.g., opener cannot reference "resume")
    transition_marker: str   # explicit hand-off phrase connecting to next section

@dataclass(frozen=True)
class NarrativeArc:
    sections: List[MessageSection]  # ordered; length = 4 (no close) or 5
    arc_coherence_score: float       # 0.0-1.0; bound-fail < 0.6
    arc_breaks: List[str]            # human-readable break descriptions
    recommended_order: List[str]     # section IDs in optimal order
```

**Arc template for SVP agentic engineering (cold):**
1. **Opener** — leads with a specific observation about *them* (`RecipientTrigger.value`); NEVER opens with "I" or sender name
2. **Hook** — one sentence connecting their trigger to a shared technical problem; introduces sender expertise obliquely
3. **Proof** — one `RepoClaim` or one `Credibility` metric that is precisely relevant to the hook topic; no others
4. **Ask** — scope-calibrated ask from `ScopeCalculatedAskEngine`; must logically follow from proof value

**Exit V6:** New `narrative_coherence` dim (weight 1.5). Bound-fail if `arc_coherence_score < 0.6` or any `arc_breaks` present.

**Sentinel tests:**
- `test_narrative_arc_opener_leads_with_recipient_not_sender`
- `test_narrative_arc_fails_if_proof_disconnected_from_hook`
- `test_narrative_arc_ask_logically_follows_proof`

**Signal mechanism:** Coherent arc is a signaling property — only prepared, thoughtful senders write them. An incoherent arc exposes that the message is template-generated. A coherent arc implies the sender researched them specifically.

---

### P2b: Archetype-Adaptive Tone Calibrator

**File:** `apps_lic/engines/archetype_tone_calibrator.py` (NEW)
**Config:** `apps_lic/config/archetype_tone_table.yaml` (NEW)
**Integration:** `apps_lic/engines/HOP3SenderGroundingAgent.py`

**Signal problem:** A tone that converts for a technical IC-level agentic engineer fails with a business-focused SVP. The same core content at wrong register reads as either too casual (builder) or too formal (research-academic). Archetype detection enables single-message tone surgery.

**Archetype taxonomy (from `RecipientTriggerVector` + `company_brief`):**

| Archetype ID | Detection Signals | Tone Register | Vocabulary | Avoid |
|---|---|---|---|---|
| `TECHNICAL_BUILDER` | Wrote/contributes OSS; conf talks on infra/systems; tweets code | Peer-to-peer; specific, precise; low jargon but high detail | "implementation", "tradeoffs", "latency budget", "failure mode" | Business-speak; outcomes only; no metrics without mechanism |
| `BUSINESS_EXECUTIVE` | P&L ownership; board-facing; revenue-first POV; hiring senior roles with business titles | Outcome-first; ROI-visible; precision without implementation detail | "$Xm", "time-to-production", "headcount leverage", "competitive moat" | Architecture diagrams; low-level implementation detail |
| `RESEARCH_ACADEMIC` | Published papers; lab affiliation or research-adjacent; peer review discourse | Evidence-first; citation-heavy; conceptual rigor before application | "empirical", "evaluation methodology", "benchmark", "generalization" | Pure business framing; no conceptual depth |
| `TALENT_SCOUT` | TA or recruiter title; hiring volume; network-dense | Efficiency-first; fit-signal; no fluff | "skills match", "team shape", "timeline", "compensation range known" | Long content; architecture detail; skip to fit signals |

**ArchetypeToneCalibration contract:**
```python
@dataclass(frozen=True)
class ArchetypeToneCalibration:
    archetype_id: str
    confidence: float
    detection_signals: List[str]        # which RecipientTrigger / brief fields fired
    vocabulary_boosted: List[str]       # words to prefer
    vocabulary_suppressed: List[str]    # words to replace
    sentence_structure_hint: str        # "short-and-specific" | "mechanism-then-outcome" | "evidence-then-claim"
    register: str                       # "peer" | "executive-brief" | "academic" | "recruiter-pitch"
```

**Exit V6:** New `tone_register_fit` dim (weight 1.0, soft). Bound-fail if `archetype_id` is `TECHNICAL_BUILDER` and message contains ≥3 `vocabulary_suppressed` words.

**Sentinel tests:**
- `test_archetype_calibrator_technical_builder_suppresses_business_jargon`
- `test_archetype_calibrator_business_executive_drops_implementation_detail`

**Signal mechanism:** Tone-register mismatch is the #2 reason high-content messages fail. A TECHNICAL_BUILDER receiving a pitch full of "ROI" and "competitive moat" routes it to "not a peer." A BUSINESS_EXECUTIVE receiving architecture diagrams routes it to "too junior."

---

### P2c: Competitive Landscape Narrative Engine

**File:** `apps_lic/engines/competitive_landscape_engine.py` (NEW)
**Precondition:** Managed workflow (`R3R4`) — requires `apps_research` briefing with company section
**Integration:** `HOP5GenerationAgent.py` — optional context field; skipped on R4 (preloaded only) path if no company section

**Signal problem:** 90% of outreach is company-agnostic. Inserting one sentence that proves the sender knows what makes this company's engineering challenge unique — and why their profile maps directly — is a top-3 reply driver.

**CompetitiveLandscape contract:**
```python
@dataclass(frozen=True)
class CompetitiveLandscapeNarrative:
    company_id: str
    differentiator_claim: str    # exactly 1 sentence; sourced from briefing
    source_refs: List[str]       # briefing citation IDs
    relevance_bridge: str        # why sender's profile is uniquely fit for THIS differentiation
    confidence: float
    fallback_mode: bool          # True = generic company context; no fabrication allowed
```

**Constraints:**
- Maximum 1 sentence in final draft — this is a single presupposition, not an analysis
- MUST be sourced from `apps_research` company briefing; `factual_support` rejects fabrication
- If managed workflow not available: skip entirely (no fallback fabrication)
- `confidence < 0.5` → skip; no partial-confidence company analysis allowed

**Exit V6:** `factual_support` dim extended: company-specific claims MUST have `CompetitiveLandscapeNarrative.source_refs` entries.

**Sentinel test:** `test_competitive_landscape_skipped_on_r4_without_briefing`

**Signal mechanism:** "I know your company rebuilds Kubernetes operators because your last two platform hires wrote K8s tooling, and that's exactly where my ADG-driven migration tooling removes the worst-case unknown-unknowns" → 1 sentence that proves research. Generates genuine surprise and curiosity.

---

## P3 Signal Enhancements — Specification

### P3a: Multi-Touch Sequence Planner

**File:** `apps_lic/engines/multi_touch_sequence_planner.py` (NEW)
**Config:** `apps_lic/config/multi_touch_policy.yaml` (NEW)
**Integration:** Extend `governed_lic_run.py` with optional `multi_touch_mode: bool` flag

**Signal problem:** Single-touch outreach has 1-4% reply rate at SVP level for cold contact. Three-touch sequence (each with different hook and progressively lower ask scope) recovers 3-5x of that. But follow-up 2 that repeats or escalates from follow-up 1 permanently damages the relationship. Sequence must be planned as a unit.

**MultiTouchSequence contract:**
```python
@dataclass(frozen=True)
class TouchSpec:
    touch_number: int           # 1, 2, or 3
    delay_days: int             # days after previous touch
    hook: str                   # must differ from all previous hooks
    ask: str                    # must have lower or equal friction to previous
    escalation_allowed: bool    # False for touch 2 if touch 1 not replied to
    max_words: int              # strictly decreasing: T1≤120, T2≤80, T3≤60

@dataclass(frozen=True)
class MultiTouchSequence:
    sequence_id: str
    touches: List[TouchSpec]
    total_hooks_distinct: bool   # validation: all 3 hooks reference different triggers
    ask_scope_monotone: bool     # validation: ask friction ≤ previous
    reply_convergence_ask: str   # T3 always ends with "close the loop" ask
```

**Policy YAML (multi_touch_policy.yaml):**
```yaml
max_touches: 3
minimum_gap_days: 7
maximum_gap_days: 14
touch_3_required_close: true
escalation_on_no_reply: forbidden
word_ceiling_by_touch:
  1: 120
  2: 80
  3: 60
ask_friction_ceiling_by_touch:
  1: 0.5
  2: 0.4
  3: 0.2   # T3 must be close-the-loop, almost zero friction
```

**New R5 reason:** `MULTI_TOUCH_SEQUENCE_INVALID` — if any `total_hooks_distinct: false` or `ask_scope_monotone: false`.

**Sentinel tests:**
- `test_multi_touch_sequence_asks_are_monotone_decreasing`
- `test_multi_touch_sequence_hooks_are_distinct`
- `test_multi_touch_touch_3_is_close_the_loop`

**Signal mechanism:** T2 with SAME hook as T1 = "they copy-pasted, not a real interest". T3 "close the loop" ask ("Closing this out — let me know if timing is off, happy to reconnect in 6 months") converts 40% of the non-replies because it removes fear of being pestered.

---

### P3b: Application-Status-Aware Resurfacer

**File:** `apps_lic/engines/status_aware_resurfacer.py` (NEW)
**Config:** `apps_lic/config/resurfacing_triggers.yaml` (NEW)
**Integration:** Feeds a new `resurfacing_mode` flag into `PreloadedOutreachContextManifest`; `MessagePlanner` selects a different section strategy per mode

**Signal problem:** 70% of applications receive no reply. Standard behavior: candidate waits and sends a "follow up" message that is structurally identical to the original. No new information → no new response. Application-status-aware resurfacing introduces *new evidence* based on what changed since first contact.

**StatusTransition taxonomy and message type:**

| From Status | To Status / Trigger | Resurfacing Message Type | New Evidence Required |
|---|---|---|---|
| `applied` | No reply after 14 days | "New development" touch | New role announcement / company news that wasn't in T1 |
| `applied` | ATS ghost (no ATS status change) | "Proof" touch | New technical artifact — ADR, PR, plan written since T1 |
| `screened` | Rejected after phone screen | "Address the gap" message | Explicit hypothesis about rejection gap + evidence addressing it |
| `rejected_app` | Same company opens new similar req | "New match" resurface | New req title + specific skill overlap not in T1 |
| `rejected_app` | Referral arrives post-rejection | "Referral-assisted" message | Mutual contact intro framing replaces direct ask |
| `interviewing` | Extended silence between rounds | "Progress" check | Restate value prop + specific question about what the round is testing |

**ResurfacingSpec contract:**
```python
@dataclass(frozen=True)
class ResurfacingSpec:
    application_status: str     # current canonical status
    trigger_type: str           # what changed
    message_type: str           # which of the above types
    required_new_evidence: str  # what MUST be new vs T1
    forbidden_repetition: List[str]  # specific phrases from T1 that must not appear
    ask_type: str               # dictated by message_type
```

**Manifest extension:** `PreloadedOutreachContextManifest` gains `resurfacing_spec_ref: Optional[str]` field.

**Sentinel tests:**
- `test_resurfacer_proof_touch_requires_new_artifact_not_in_t1`
- `test_resurfacer_address_gap_requires_rejection_hypothesis`

**Signal mechanism:** "As I mentioned in my last email…" → triaged as persistent/tone-deaf. "Since my last note, I published this ADR on governed agentic routing that addresses exactly the deployment risk you raised in the phone screen" → new evidence that changes the information state. Uncommon behavior = high signal.

---

### P3c: Mutual-Intelligence Network Mapper

**File:** `apps_lic/engines/mutual_network_mapper.py` (NEW)
**Precondition:** `apps_research` briefing includes at least one connection field; OR `master_resume.json` shared-employer history present
**Integration:** Optional enrichment in `HOP1ProfileAnalysisAgent.py` output

**Signal problem:** Warm introductions convert at 5-10x cold. But 80% of candidates who have a mutual connection never surface it because the mapping is manual. The mapper infers connection paths from public signals.

**ConnectionPath taxonomy:**
```python
class ConnectionType(str, Enum):
    SHARED_EMPLOYER        = "shared_employer"        # overlapping tenure at same company
    CONFERENCE_CO_SPEAKER  = "conference_co_speaker"  # both spoke at same event
    OPEN_SOURCE_CO_CONTRIB = "open_source_co_contrib" # same OSS repo/org
    ACADEMIC_OVERLAP       = "academic_overlap"       # same institution/lab
    PUBLICATION_CO_AUTHOR  = "publication_co_author"  # shared paper/report
    COMMUNITY_OVERLAP      = "community_overlap"      # same Slack/Discord/community listed

@dataclass(frozen=True)
class ConnectionPath:
    path_id: str
    connection_type: ConnectionType
    strength: str           # "direct" | "1-hop" | "2-hop"
    evidence: str           # the verifiable signal (e.g., "Both at Yelp 2018-2020")
    source_ref: str         # briefing or master_resume hash
    intro_ask_appropriate: bool  # True only for "direct" strength
    intro_ask_template: str      # pre-written intro ask for the mutual (if applicable)
```

**Manifest extension:** `PreloadedOutreachContextManifest` gains `connection_paths_ref: Optional[str]` field.

**Exit V6:** If `connection_paths_ref` is set AND `strength == "direct"` AND `intro_ask_appropriate == True`, Exit V6 flags message as `WARM_PATH_AVAILABLE` — HITL prompt to confirm mutual contact is appropriate for intro request.

**Sentinel tests:**
- `test_mutual_mapper_shared_employer_path_detection`
- `test_mutual_mapper_no_fabrication_without_source`
- `test_mutual_mapper_warm_path_flags_hitl_for_direct_intro`

**Signal mechanism:** "I saw we both worked at Yelp in 2019 — I know the infra team was dealing with exactly this scaling problem then" converts because it's verifiable, specific, and proves overlapping professional context. No intro needed — the shared history is the warm signal.

---

## Extended Exit V6 Rubric (17 dims after P2+P3)

Adds 3 new dims to the 14 from parent plan (10 base + 4 from P0+P1):

| Dim ID | Name | Weight | Fail-Closed | P2/P3 Origin |
|--------|------|--------|-------------|--------------|
| `narrative_coherence` | Message Arc Coherence | 1.5 | Yes (<0.6) | P2a |
| `tone_register_fit` | Archetype Tone Fit | 1.0 | Soft | P2b |
| `sequence_position_fit` | Multi-Touch Position Fit | 1.0 | Soft (fail-closed in P3a) | P3a |

---

## New P2+P3 Sentinel Tests (15 total across W1–W4)

```python
# W1 — P2a/P2b
def test_narrative_arc_opener_leads_with_recipient_not_sender(): ...
def test_narrative_arc_fails_if_proof_disconnected_from_hook(): ...
def test_narrative_arc_ask_logically_follows_proof(): ...
def test_archetype_calibrator_technical_builder_suppresses_business_jargon(): ...
def test_archetype_calibrator_business_executive_drops_implementation_detail(): ...

# W2 — P2c
def test_competitive_landscape_skipped_on_r4_without_briefing(): ...
def test_competitive_landscape_no_fabrication_below_confidence_threshold(): ...

# W3 — P3a/P3b
def test_multi_touch_sequence_asks_are_monotone_decreasing(): ...
def test_multi_touch_sequence_hooks_are_distinct(): ...
def test_multi_touch_touch_3_is_close_the_loop(): ...
def test_resurfacer_proof_touch_requires_new_artifact_not_in_t1(): ...
def test_resurfacer_address_gap_requires_rejection_hypothesis(): ...

# W4 — P3c
def test_mutual_mapper_shared_employer_path_detection(): ...
def test_mutual_mapper_no_fabrication_without_source(): ...
def test_mutual_mapper_warm_path_flags_hitl_for_direct_intro(): ...
```

---

## ADG Hotspot Report

| Node | Layer | Fan-in | Archetype | P2/P3 blast radius |
|------|-------|--------|-----------|-------------------|
| `HOP4DraftAgent.py` | L2 | High (5 callers) | ORCHESTRATOR | SE-P2a NarrativeArcEngine injects into pre-assembly context |
| `HOP3SenderGroundingAgent.py` | L2 | High (7 callers) | CENTRAL_DEPENDENCY | SE-P2b ArchetypeToneCalibrator integrates as context provider |
| `HOP5GenerationAgent.py` | L2 | Medium (4 callers) | ORCHESTRATOR | SE-P2c CompetitiveLandscape injects optional field |
| `governed_lic_run.py` | L3 | High (orchestrator) | ORCHESTRATOR | SE-P3a multi_touch_mode flag threads through governed run |
| `message_planner.py` | L1 | High (9 callers) | CENTRAL_DEPENDENCY | SE-P3b ResurfacingSpec changes section strategy selection |

---

## ADG Graph Layer Evidence

**P-view coverage:**
- `v_p1_*` — `message_planner.py` and `HOP3SenderGroundingAgent.py` are both P1 (zero-caller risk after P2b refactor adds a new caller path — monitor)
- `v_p0_*` — check `governed_lic_run.py` for any layer-break violations after multi_touch_mode flag addition

**Semantic edges of concern:**
- `HOP4DraftAgent.py` → `flows_to` → `HOP5GenerationAgent.py` — NarrativeArc must not break this flow
- `governed_lic_run.py` → `controls_flow` → all 9 HOP stages — multi_touch_mode must not fork the flow graph
- `message_planner.py` → `reads_from` → `PreloadedOutreachContextManifest` — ResurfacingSpec adds a new reads_from edge

**Materialized views:**
- `mv_hotspot_centrality` — rank HOP4, HOP3, HOP5, governed_lic_run before W1 to confirm blast radius still bounded
- `mv_graph_critical_path_blast_radius` — P2a NarrativeArc injects into critical path; verify no new P0 violations
- `mv_dependency_cone_risk` — P3b ResurfacingSpec changes message_planner section strategy; verify cone risk bounded

---

## Gap Register

| Gap | Severity | Mitigation |
|-----|----------|------------|
| `apps_research` company briefing may not expose competitive signals | HIGH | P2c `fallback_mode = True` skips fabrication entirely; sentinel verifies skip |
| Multi-touch sequencing requires durable state between runs | HIGH | P3a sequence is planned in a single run; delivery scheduling is out of scope |
| Mutual network mapper depends on `apps_research` briefing quality | MEDIUM | Fallback: `master_resume.json` shared-employer history only; mapper skips if no evidence |
| `HOP4DraftAgent` integration complexity unknown | MEDIUM | Pre-W1 discovery phase reads HOP4 before committing NarrativeArc integration pattern |
| ResurfacingSpec changes MessagePlanner section strategy — may break existing tests | LOW | Pre-W3 regression pass on parent plan test suite required |

---

## Deferred Scope

```
DEFERRED_SCOPE: Delivery scheduling for multi-touch sequences — apps_lic drafts only; scheduling is a CRM concern
DEFERRED_SCOPE: Real-time LinkedIn API integration for mutual network mapping — briefing-only inference in scope
DEFERRED_SCOPE: A/B test framework for narrative arc variants — planned under L6 shadow eval; not in this plan
DEFERRED_SCOPE: Personalization quality scoring feedback loop from actual reply rates — production-log mining deferred
DEFERRED_SCOPE: Campaign-level competitive landscape batch analysis — single-recipient only in this plan
```

---

## Author-Gate Queue Seed

```
AG_QUEUE_SEED: plan=apps-lic-signal-enhancements-p2p3-f4b8d1 id=ag-p2p3-arc-vs-standalone title="NarrativeArc as mandatory vs optional dim"
AG_QUEUE_SEED: plan=apps-lic-signal-enhancements-p2p3-f4b8d1 id=ag-p2p3-multitouch-state title="Multi-touch state: in-memory vs durable store"
```

---

## Verification Plan

1. Pre-W1: `adg_health` green; parent plan `apps-lic-canonical-spine-wireup-e7c2a5` W7+W8 DONE
2. Pre-W1: `adg_mv_hotspot_centrality` — verify HOP3/HOP4/HOP5/governed_lic_run fan-in bounded
3. Post-W1: 5 P2a+P2b tests pass; existing 10 P0+P1 sentinel tests still green
4. Post-W2: 7 total P2 tests pass; `narrative_coherence` + `tone_register_fit` dims present in exit rubric YAML
5. Post-W3: 12 total P2+P3a+P3b tests pass; multi_touch_policy.yaml validates
6. Post-W4: All 15 tests pass; 17-dim rubric complete; `mutual_mapper` sentinel passes
7. V1: Notion Plans row registered; parent plan Notion row updated with P2/P3 followup link

---

## Acceptance Criteria Summary

- 15 new sentinel tests pass across W1–W4 without regressions in parent plan suite
- Exit V6 rubric reaches 17 dims (base 10 + 4 P0/P1 + 3 P2/P3)
- `NarrativeArcEngine`, `ArchetypeToneCalibratorEngine`, `CompetitiveLandscapeEngine`, `MultiTouchSequencePlanner`, `StatusAwareResurfacer`, `MutualNetworkMapper` all present as typed dataclass contracts
- Zero fabrication paths — all competitive/mutual claims require `source_ref` with confidence ≥ 0.5
- Managed workflow dependency (`P2c`, `P3c`) fails-closed with `fallback_mode = True` when `apps_research` briefing not present
- Notion Plans row registered; parent plan Notion row updated

---

## PLAN_CREATED: apps-lic-signal-enhancements-p2p3-f4b8d1
