# Figma Flowchart Instructions: Agentic Control Flow v2

**Date**: 2026-02-11
**Base**: "AGENTIC CONTROL FLOW: A++ Enforceable L2 Control Spec" (existing diagram)
**Scope**: Recreate base flowchart + add Control Plane, Classification Kernel, Agent Consolidation, LCD+ Skeleton, Blueprint Hardening, Phantom Baseline, Guardian Contract, and Dependency Governance features from last 5-6 development sessions.

---

## CANVAS SETUP

- **Frame**: 3200 × 2400 px (landscape), white background
- **Title**: `AGENTIC CONTROL FLOW v2: A++ Enforceable L2 Control Spec + Control Plane` — bold, 28pt, centered top
- **Grid**: 8-column soft grid, 16px gutters
- **Font**: Inter or DM Sans throughout
- **Corner radius**: 12px for all boxes/cards

---

## COLOR PALETTE (match original + new)

| Element | Fill | Border | Text |
|---------|------|--------|------|
| L0 — Core Logic & Routing | `#D4E8C2` (sage green) | `#8CB369` | `#1A3300` |
| L1 — Advanced Cognitive Engine | `#FFF3B0` (warm yellow) | `#E6C84D` | `#4A3800` |
| L2 — Symmetric Validator-Healer Pipe | `#FFF3B0` (warm yellow) | `#E6C84D` | `#4A3800` |
| L3 — Human Review Gate | `#FFD699` (amber/orange) | `#E6A030` | `#4A2800` |
| L4 — Knowledge System | `#B8D8F8` (light blue) | `#5A9BD5` | `#002B55` |
| L5 — Governance & Safety | `#F2B8C6` (pink/rose) | `#D35D7A` | `#4A0020` |
| L6 — Event & Anomaly Detection | `#C8A8E8` (lavender) | `#8B5DAA` | `#2A0050` |
| **NEW: Control Plane** | `#E8E0F0` (pale violet) | `#7B68AE` stroke 2px | `#2A0050` |
| **NEW: Classification Kernel** | `#F0E68C` (khaki gold) | `#BDB76B` dashed 2px | `#333300` |
| **NEW: Blueprint Enforcement** | `#FFE4E1` (misty rose) | `#CD5C5C` stroke 2px | `#8B0000` |
| **NEW: LCD+ Skeleton** | `#E0F0E0` (mint) | `#66BB6A` | `#1B5E20` |
| Flow arrows (main) | — | `#2C3E50` stroke 2px | — |
| Flow arrows (conditional) | — | `#E67E22` stroke 2px dashed | — |
| Flow arrows (telemetry) | — | `#C0392B` stroke 1.5px dotted | — |
| Flow arrows (advisory) | — | `#7F8C8D` stroke 1px dashed | — |

---

## LAYER-BY-LAYER CONSTRUCTION

### ═══════════════════════════════════════
### LAYER 0: CORE LOGIC & ROUTING (left-center)
### ═══════════════════════════════════════

**Position**: X=120, Y=520 — 360×320 px card
**Fill**: `#D4E8C2` with `#8CB369` border

**Title bar**: "L0: CORE LOGIC & ROUTING" — bold 14pt, dark green

**Inner box 1**: "CONTEXTUAL ROUTER & POLICY ENFORCER" — bold subtitle
- Bullet: "Policy Config Verification (Timestamp, Config Versions)"
- Bullet: "Typed Trace Parsing (Chat, SQL, Stream, Patch)"
- Bullet: "Strict Routing (Read-Only)"
- Bullet: "Healing, Human Escalation"

**Inner box 2** (NEW — mint accent `#E0F0E0`): "LCD+ CANONICAL SKELETON"
- Bullet: "6-folder standard: config/ types/ reasoning/ engines/ validators/ utils/"
- Bullet: "Nuance folders: tools/ scripts/ data/"
- Bullet: "Flat engines (no subfolders)"
- Bullet: "Dissolved: domain/, shared/, logic_nodes/, core/"

**Annotation**: Dashed gray line going down-left reading "— No direct writes from L0 →"

---

### ═══════════════════════════════════════
### LAYER 1: ADVANCED COGNITIVE ENGINE (top-right)
### ═══════════════════════════════════════

**Position**: X=1680, Y=60 — 520×260 px card
**Fill**: `#FFF3B0` with `#E6C84D` border

**Left sub-box**: "WORKING MEMORY (Internal State)"
- Bullet: "Schema"
- Bullet: "History"
- Bullet: "Rules"
- Bullet: "Deterministic Time"

**Right sub-box**: "THOUGHT GENERATION & COGNITIVE SAFETY"
- Bullet: "Episodic Memory"
- Bullet: "Trajectory Replay"
- Bullet: "Prompt Optimization"
- Bullet: "Token Management"

---

### ═══════════════════════════════════════
### LAYER 2: SYMMETRIC VALIDATOR-HEALER PIPE (far right)
### ═══════════════════════════════════════

**Position**: X=2300, Y=520 — 360×240 px card
**Fill**: `#FFF3B0` with `#E6C84D` border

**Title**: "L2: SYMMETRIC VALIDATOR-HEALER PIPE (HEALING & ROLLBACK)"
- Bullet: "Applies Approved Fix Only"
- Bullet: "Deterministic Order"
- Bullet: "Emits RESULT"

**NEW badge** (small rounded pill, `#E0F0E0`): "6 Canonical Executors"
- Sub-text (8pt): "InspectorExecutor · RGValidationExecutor · LICValidationExecutor"
- Sub-text (8pt): "ObservabilityProbeExecutor · RGStrategyExecutor · HOPPipelineExecutor"

**Output arrow** right: "Emit RESULT artifact" → exits frame

---

### ═══════════════════════════════════════
### LAYER 3: HUMAN REVIEW GATE (center-right)
### ═══════════════════════════════════════

**Position**: X=1680, Y=520 — 280×240 px card
**Fill**: `#FFD699` with `#E6A030` border

**Title**: "L3: HUMAN REVIEW GATE (APPROVAL QUEUE)"
- Bullet: "Approval Audit (RESULT)"
- Bullet: "Approved Decision (Remediation Pointer)"

**Incoming arrow from L5**: labeled "Escalate → HIL"
**AUTO-PASS label** (green pill badge above): "AUTO-PASS (No HIL, No Healing)" → arrow to L2

---

### ═══════════════════════════════════════
### LAYER 4: KNOWLEDGE SYSTEM (top-center)
### ═══════════════════════════════════════

**Position**: X=680, Y=40 — 560×200 px card
**Fill**: `#B8D8F8` with `#5A9BD5` border

**Left sub-box**: "SEMANTIC MEMORY (Knowledge Graph & Vector DB)"
- Bullet: "Ontology Management"
- Bullet: "Embedding Services"
- Bullet: "Fast Retrieval"

**Right sub-box**: "EPISODIC MEMORY"
- Bullet: "Experience Replay"
- Bullet: "Past Trajectories"
- Bullet: "Outcome Linking"

**Attached satellite** (left, smaller rounded rect `#B8D8F8`): "KNOWLEDGE GRAPH (Structured Memory)"
- Dashed gray arrow labeled "Advisory only (no control)"

**Arrow down**: Dashed blue labeled "Context retrieval request" → L0

---

### ═══════════════════════════════════════
### LAYER 5: GOVERNANCE & SAFETY (center)
### ═══════════════════════════════════════

**Position**: X=680, Y=420 — 480×360 px card
**Fill**: `#F2B8C6` with `#D35D7A` border

**Inner box 1** (top): "BUDGET GUARD (Token/Token Checks)"

**Inner box 2** (main): "GUARDIAN (VALIDATION GATE)"
- "Decision: ✅ Pass → RESULT"
- "❌ Escalate → HIL"
- "Enforces Hard Rules ≫ Only"
- "Safety Boundaries"
- "Budget Markers (fast goes)"

**NEW inner box 3** (bottom, `#FFE4E1` fill with `#CD5C5C` border): "AI-CHECKING-AI REMEDIATION"
- Bullet: "Deterministic Guardian Tests (no heuristic AI validation)"
- Bullet: "4 violations remediated: Autonomy, Canon Auditor, Architecture Governor, Phase5"
- Bullet: "32 test cases, 8 guardian tests"

**Arrows**:
- Right arrow → L3 "Escalate → HIL"
- Right arrow (bypassing L3) → L2 "AUTO-PASS"
- Down arrow → "Emit AGGREGATE artifact"

---

### ═══════════════════════════════════════
### LAYER 6: EVENT & ANOMALY DETECTION (far left)
### ═══════════════════════════════════════

**Position**: X=120, Y=200 — 360×280 px card
**Fill**: `#C8A8E8` with `#8B5DAA` border

**Title**: "L6: EVENT & ANOMALY DETECTION LAYER"
- Bullet: "Multi-modal Data Ingestion (Logs, Metrics)"
- Bullet: "Real-Time Stream Processing"
- Bullet: "Anomaly Detection (Signal Creetulational, ML)"
- Bullet: "Signal Correlation & Deduplication"

**NEW sub-box** (`#E8E0F0`): "GUARDIAN-TO-L6 CONTRACT"
- Bullet: "GuardianResult schema (guardian_contract.py)"
- Bullet: "Correlation ID grouping for CI runs"
- Bullet: "Max 30s runtime, 512KB artifacts, depth=10"
- Bullet: "POSIX repo-relative paths only"

**Arrow down**: "Signal Correlation & Deduplication" → L0

---

## ═══════════════════════════════════════════════════
## NEW: CONTROL PLANE (BOTTOM FULL-WIDTH SECTION)
## ═══════════════════════════════════════════════════

**Position**: X=60, Y=1080 — 3080×800 px outer frame
**Fill**: `#E8E0F0` with `#7B68AE` 2px border, corner radius 16px
**Title bar**: "CONTROL PLANE — Structural Governance & Deterministic Enforcement" — bold 18pt, `#2A0050`
**Subtitle**: "All governance decisions trace to these SSOTs — no heuristic overrides"

This is a new full-width section below the main flow. It contains 5 inner cards arranged horizontally.

---

### Control Plane Card 1: CLASSIFICATION KERNEL SSOT
**Position**: leftmost in control plane, 540×340 px
**Fill**: `#F0E68C` with `#BDB76B` dashed 2px border

**Title**: "CLASSIFICATION KERNEL" — bold
**Subtitle**: `agentic_core/core/classification_kernel.py`

**Content**:
- "Zero-dependency (stdlib only)"
- "LRU-cached (maxsize=1024)"
- "`classify_file_standalone(path) → FileType` (20 types)"
- "`is_agent_file(path)` / `is_agent_or_orchestrator(path)`"
- "19-priority classification queue"
- "Error-hardened: SyntaxError / UnicodeDecodeError → IGNORE + log"

**Badge** (green pill): "0 shadow logic remaining"
**Badge** (blue pill): "68 contract tests"

**Arrows** (upward, gray advisory):
- → L0 "discovery_util.py delegates"
- → L5 "FileClassificationAgent imports kernel"
- → L5/enforcement "ssot_guardrail.py blocks shadow logic"

---

### Control Plane Card 2: BLUEPRINT ENFORCEMENT ENGINE
**Position**: second from left, 540×340 px
**Fill**: `#FFE4E1` with `#CD5C5C` 2px border

**Title**: "BLUEPRINT ENFORCEMENT" — bold
**Subtitle**: `structure_blueprint/enforcement/` (6 modules)

**Content table** (mini 2-col table):
| Module | Check |
|--------|-------|
| `territory_diff` | Undeclared/missing subfolders (ceiling=20) |
| `leaf_node` | No root .py in `allow_root_py=False` dirs |
| `volatile_rules` | No inbound imports to volatile territories |
| `mixin_ast` | Naming + flat + AST compliance (50 files) |
| `blueprint_hash` | SHA-256 lock over 20 blueprint .py files |
| `cross_layer` | Layer inversion detection (3356 edges, 14 cross-layer) |

**Stats row** (bottom): "2751 files parsed · 0 errors · 6/6 checks pass · debt headroom=1"

**Arrow** up to L5: "Enforcement SSOT wired via _verify.py §10"

---

### Control Plane Card 3: PHANTOM BASELINE SYSTEM
**Position**: center, 540×340 px
**Fill**: `#FFE4E1` with `#CD5C5C` border

**Title**: "PHANTOM BASELINE LOCK" — bold
**Subtitle**: `phantom_baseline.json` — non-growing debt contract

**Decision tree** (mini flowchart inside the card):
```
current phantoms == baseline → PASS (LOCKED)
current < baseline → PASS (improvement, not persisted unless --update flag)
current > baseline → HARD FAIL (no override exists)
baseline missing → FAIL (unless --init-phantom-baseline)
baseline corrupt → FAIL (unless --repair-phantom-baseline)
```

**Stats**: "29 phantom = 29 baseline · LOCKED"
**Prohibition badge** (red): "Maintenance flags FORBIDDEN in CI"

---

### Control Plane Card 4: AGENT CONSOLIDATION REGISTRY
**Position**: second from right, 540×340 px
**Fill**: `#E0F0E0` with `#66BB6A` border

**Title**: "AGENT CONSOLIDATION" — bold
**Subtitle**: "190 → 149 active agents (target ≤150)"

**Content**:
- "19 retirements (zero domain logic, boilerplate stubs)"
- "28 merge shims (import-alias, no ClassDef → invisible to discovery)"
- "6 canonical executors created:"

**Mini executor table**:
| Executor | Replaces | Domain |
|----------|----------|--------|
| HOPPipelineExecutor | 9 HOP stage agents | apps_lic |
| RGValidationExecutor | 4 RG validators | apps_rg |
| LICValidationExecutor | 2 LIC validators | apps_lic |
| ObservabilityProbeExecutor | 6 obs agents | L6 |
| RGStrategyExecutor | 3 strategy agents | apps_rg |
| InspectorExecutor | 3 inspector agents | L5 |

**Stats row**: "-4339 LOC · -41 discovery nodes · 62/62 tests pass"

---

### Control Plane Card 5: DEPENDENCY GOVERNANCE
**Position**: rightmost, 540×340 px
**Fill**: `#B8D8F8` with `#5A9BD5` border

**Title**: "DEPENDENCY GOVERNANCE" — bold
**Subtitle**: "57 dist packages · 4 buckets"

**Bucket breakdown**:
- "**core** (19): pydantic, numpy, redis, networkx, libcst, chromadb..."
- "**dev** (1): pytest"
- "**infra** (34): openai, anthropic, fastapi, dash, boto3..."
- "**sdks** (3): provider-specific SDKs"
- "**phantom/stale** (17): internal refs to removed modules"

**Contract**: "Shipping contract excludes: tests/, ops_scripts/, data/, */scripts/, */dashboards/"

**Badge** (blue): "Import allowlist: 7 stdlib modules only in _constants.py"
**Badge** (gold): "Allowlist hash locked in SHA-256"

---

## CONNECTING THE CONTROL PLANE TO MAIN FLOW

Draw **upward arrows** from the Control Plane section to the main flow layers:

1. **Classification Kernel → L0** (green dashed): "Discovery delegation"
2. **Classification Kernel → L5** (green dashed): "FCA imports kernel"
3. **Blueprint Enforcement → L5** (red solid): "_verify.py §10 enforcement"
4. **Blueprint Enforcement → CI** (red dotted): connects to CI badge (see below)
5. **Phantom Baseline → L5** (red dashed): "Phantom debt tracking"
6. **Agent Consolidation → L2** (green solid): "Canonical executors power L2 pipe"
7. **Agent Consolidation → L6** (green solid): "ObservabilityProbeExecutor"
8. **Dependency Governance → L0** (blue dashed): "Import graph scan roots"

---

## BOTTOM STRIP: OBSERVABILITY & ARTIFACTS

**Position**: X=60, Y=1920 — 3080×200 px strip
**Fill**: `#F5F5F5` with `#CCCCCC` border

### Left section: Artifact Taxonomy Legend
Recreate existing legend with 4 artifact types:
- **RESULT** (result.json) — blue arrow icon: "Main Flow (result.json)"
- **AGGREGATE** (aggregate.json) — orange dashed icon: "Conditional Flow (aggregate.json)"
- **INCIDENT** (incident.json) — red dotted icon: "Incident Telemetry Emission (incident.json)"
- **HEALING_PLAN** (healing_plan.json) — green dotted icon: "HEALING_PLAN (healing_plan.json)"

### Center section: Routing connectors
- "L6: CORE LOGIC & ROUTING" box → "APPROVED REMEDIATION POINTER (Deterministic Trigger)"
- Connect to "METRICS DASHBOARD" and "AUDIT LOG" boxes

### Right section: NEW Enforcement Artifacts
- **enforcement_report.json** — "Machine-readable enforcement results"
- **blueprint_integrity.sha256** — "SHA-256 hash lock (20 files)"
- **guardian_{id}.json** — "Guardian result artifacts (L6 ingestible)"
- **phantom_baseline.json** — "Phantom debt register"
- **agent_discovery_full.json** — "Agent registry SSOT (149 agents)"

---

## CI/CD GOVERNANCE BADGE (top-right corner)

**Position**: X=2700, Y=20 — 440×180 px card
**Fill**: `#E8E0F0` with `#7B68AE` border

**Title**: "CI GOVERNANCE GATES"

**Gate list**:
- "✅ `ssot_verify.yml` — Blueprint enforcement + phantom baseline"
- "✅ `ssot-kernel-guardrail.yml` — Shadow logic block + 68 contract tests"
- "✅ `guardian-tests.yml` — Deterministic guardian tests"
- "✅ `agent-sprawl-check.yml` — Agent count ceiling"
- "🔒 Maintenance flags FORBIDDEN in CI (--update-phantom-baseline etc.)"

---

## FLOW ARROWS BETWEEN MAIN LAYERS (preserve from original)

1. **L4 → L1**: Blue solid arrow labeled "Context retrieval request"
2. **L0 → L5**: Solid arrow, "Route to governance check"
3. **L5 → L3**: Orange arrow, "❌ Escalate → HIL"
4. **L5 → L2**: Green arrow (bypass L3), "✅ AUTO-PASS (No HIL, No Healing)"
5. **L3 → L2**: Orange arrow, "Approved Decision (Remediation Pointer)"
6. **L2 → output**: "Emit RESULT artifact"
7. **L6 → L0**: Purple arrow, "Signal Correlation & Deduplication"
8. **L0 ← L4**: Dashed gray, "Advisory only (no control)"
9. **L5 → bottom**: "Emit AGGREGATE artifact"
10. **L6 bottom**: "Emit telemetry (telemetry.event)" connections to METRICS DASHBOARD and AUDIT LOG

### NEW flow arrows:
11. **Control Plane → L5**: Red upward arrow, "Structural enforcement feeds L5 governance"
12. **Control Plane → L0**: Green upward arrow, "Classification kernel powers routing/discovery"
13. **Control Plane → L2**: Green upward arrow, "Canonical executors drive healing pipe"
14. **Classification Kernel → all layers**: Faint dashed gold lines, "Zero-dep SSOT importable from any layer"

---

## FIGMA COMPONENT / AUTO-LAYOUT TIPS

1. **Use Auto Layout** on each layer card — vertical, 12px gap, 16px padding
2. **Create components** for:
   - `LayerCard` (title bar + content area + optional badge strip)
   - `ArrowLabel` (line + text label)
   - `ArtifactLegendItem` (icon + label + description)
   - `StatsBadge` (rounded pill with count text)
   - `ControlPlaneCard` (same as LayerCard but with dashed border variant)
3. **Use Figma Sections** to group:
   - "Main Flow Layers" (L0-L6)
   - "Control Plane"
   - "Observability Strip"
   - "CI Governance"
4. **Arrow plugin**: Use "Autoflow" or "FigJam Connector" for clean arrow routing
5. **Responsive**: Set frame constraints so horizontal resize keeps cards proportional

---

## FIGMA LAYER NAMING CONVENTION

```
📁 Frame: "Agentic Control Flow v2"
  📁 Section: "Title"
  📁 Section: "Main Flow"
    📁 L0-CoreLogicRouting
    📁 L1-CognitiveEngine
    📁 L2-ValidatorHealerPipe
    📁 L3-HumanReviewGate
    📁 L4-KnowledgeSystem
    📁 L5-GovernanceSafety
    📁 L6-EventAnomalyDetection
  📁 Section: "Flow Arrows"
    📁 MainFlow-Arrows
    📁 Conditional-Arrows
    📁 Telemetry-Arrows
    📁 ControlPlane-Arrows
  📁 Section: "Control Plane"
    📁 CP1-ClassificationKernel
    📁 CP2-BlueprintEnforcement
    📁 CP3-PhantomBaseline
    📁 CP4-AgentConsolidation
    📁 CP5-DependencyGovernance
  📁 Section: "Observability Strip"
    📁 ArtifactTaxonomy
    📁 RoutingConnectors
    📁 EnforcementArtifacts
  📁 Section: "CI Governance Badge"
```

---

## SUMMARY OF NEW ELEMENTS vs. ORIGINAL DIAGRAM

| New Element | What it represents | Where on canvas |
|-------------|-------------------|-----------------|
| Control Plane (full section) | Structural governance layer | Bottom half, full-width |
| Classification Kernel card | Zero-dep SSOT for file classification | Control Plane, left |
| Blueprint Enforcement card | 6-module enforcement engine | Control Plane, center-left |
| Phantom Baseline card | Non-growing debt contract | Control Plane, center |
| Agent Consolidation card | 190→149 reduction, 6 executors | Control Plane, center-right |
| Dependency Governance card | 57 packages in 4 buckets | Control Plane, right |
| LCD+ Skeleton sub-box | 6-folder canonical structure | Inside L0 card |
| AI-Checking-AI sub-box | Deterministic guardian tests | Inside L5 card |
| Guardian-to-L6 Contract sub-box | Structured ingestion schema | Inside L6 card |
| Canonical Executors badge | 6 executors powering L2 | Inside L2 card |
| CI Governance badge | 4 CI gates + forbidden flags | Top-right corner |
| Enforcement Artifacts | 5 new artifact types | Observability strip, right |
| Control Plane → layers arrows | Governance connections upward | Between sections |

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

