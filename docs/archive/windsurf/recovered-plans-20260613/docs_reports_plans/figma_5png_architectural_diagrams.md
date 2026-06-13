# Figma Instructions — Five Architectural Clarity PNGs

**Series Title**: A+++ Grade Agentic Architecture Training Set
**Style Reference**: "AGENTIC CONTROL FLOW: A++ Enforceable L2 Control Spec" (existing PNG)
**Export**: PNG @ 2x, 1920×1080 base (3840×2160 export)
**Date**: 2026-02-11

---

## Global Style System (Apply to ALL Five PNGs)

### Canvas & Background

| Property          | Value                                      |
|-------------------|--------------------------------------------|
| Background        | `#F5F0E1` (warm parchment/cream)           |
| Noise overlay     | 3% grain texture at 8% opacity (optional)  |
| Canvas padding    | 60px all sides                             |
| Grid              | 8px base grid, 24px layout grid            |

### Typography

| Element              | Font              | Size   | Weight   | Color     |
|----------------------|-------------------|--------|----------|-----------|
| Page title           | Inter / Helvetica | 28px   | 800      | `#1A1A1A` |
| Section header       | Inter / Helvetica | 18px   | 700      | `#1A1A1A` |
| Box title (inside)   | Inter / Helvetica | 15px   | 700      | `#1A1A1A` |
| Body / bullet text   | Inter / Helvetica | 12px   | 500      | `#2D2D2D` |
| Label on arrows      | Inter / Helvetica | 10px   | 600 Ital | `#555555` |
| Legend text           | Inter / Helvetica | 11px   | 500      | `#333333` |

### Box Style

| Property          | Value                                                   |
|-------------------|---------------------------------------------------------|
| Corner radius     | 8px (outer boxes), 4px (inner sub-boxes)                |
| Border            | 2px solid, color-matched to fill (30% darker)           |
| Shadow            | `0 2px 6px rgba(0,0,0,0.12)`                            |
| Padding           | 16px internal                                           |
| Min width         | 200px per box                                           |

### Color Palette (Semantic)

| Semantic Role        | Fill        | Border      | Header BG   | Usage                        |
|----------------------|-------------|-------------|-------------|------------------------------|
| **Core / Routing**   | `#FFF3C4`  | `#D4A017`   | `#F0D060`   | L0, core logic, router       |
| **Knowledge / State**| `#D4EDFC`  | `#4A90C4`   | `#8BBEE8`   | L4, memory, knowledge        |
| **Cognition**        | `#C8E6C9`  | `#388E3C`   | `#66BB6A`   | L1, reasoning, thought       |
| **Execution**        | `#B2EBF2`  | `#00838F`   | `#4DD0E1`   | L2, healer pipe, mutation    |
| **Orchestration**    | `#E1BEE7`  | `#7B1FA2`   | `#CE93D8`   | L3, orchestration            |
| **Governance/Safety**| `#FFCDD2`  | `#C62828`   | `#EF9A9A`   | L5, guardian, policy         |
| **Observability**    | `#FFE0B2`  | `#E65100`   | `#FFB74D`   | L6, telemetry, audit         |
| **Certification**    | `#C8E6C9`  | `#2E7D32`   | `#81C784`   | Green = certified / approved |
| **Neutral / Shared** | `#ECEFF1`  | `#607D8B`   | `#B0BEC5`   | Shared contracts, legends    |

### Arrow Styles

| Type                  | Stroke  | Width | Dash       | Head       | Usage                    |
|-----------------------|---------|-------|------------|------------|--------------------------|
| Primary flow          | `#333`  | 2px   | Solid      | Filled tri | Main data/control flow   |
| Conditional flow      | `#E65100`| 2px  | `8,4` dash | Open tri   | Conditional / gated      |
| Telemetry emission    | `#C62828`| 1.5px| `4,4` dash | Diamond    | Observability signals    |
| Advisory (read-only)  | `#4A90C4`| 1.5px| `6,3` dash | Open tri   | Read-only / advisory     |
| Forbidden             | `#C62828`| 2px  | Solid      | X-head     | Prohibited path          |

### Legend Box

- Position: Bottom-left or bottom-center
- Fill: `#ECEFF1`, Border: `#607D8B` 1.5px
- Title: **"Legend"** bold 13px
- Show arrow types + color meaning + artifact types
- Always include the **Enforceable Artifact Taxonomy** where relevant:
  - `RESULT (result.json)` — blue solid arrow
  - `AGGREGATE (agg.json)` — orange dashed arrow
  - `INCIDENT (incident.json)` — red dashed arrow
  - `HEALING_PLAN (healing_plan.json)` — green dotted arrow

---

---

## PNG 1 — The Authority Stack (L0–L6 with Functional Roles)

### Page Title

```
THE AUTHORITY STACK: L0–L6 Layer Responsibility & Execution Authority
```

### Canvas Size

1920×1200 (portrait-leaning, tall stack)

### Layout

**Primary structure**: 7 horizontal bands stacked vertically (top = L6, bottom = L0).
Each band is a full-width rounded rectangle, ~140px tall, with 12px vertical gap between bands.

```
┌──────────────────────────────────────────────────────────────────────┐
│  L6 – OBSERVABILITY                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────────────┐│
│  │ Detect   │ │ Authorize│ │ Mutate   │ │ Certify                  ││
│  │   ✔      │ │   ✖      │ │   ✖      │ │   ✖                     ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────────────┘│
├──────────────────────────────────────────────────────────────────────┤
│  L5 – GOVERNANCE & SAFETY                                            │
│  ...                                                                 │
├──────────────────────────────────────────────────────────────────────┤
│  L4 – STATE & KNOWLEDGE                                              │
│  ...                                                                 │
├──────────────────────────────────────────────────────────────────────┤
│  L3 – ORCHESTRATION                                                  │
│  ...                                                                 │
├──────────────────────────────────────────────────────────────────────┤
│  L2 – EXECUTION                                                      │
│  ...                                                                 │
├──────────────────────────────────────────────────────────────────────┤
│  L1 – COGNITION                                                      │
│  ...                                                                 │
├──────────────────────────────────────────────────────────────────────┤
│  L0 – MAINTENANCE                                                    │
│  ...                                                                 │
└──────────────────────────────────────────────────────────────────────┘
```

### Each Layer Band Contains

**Left zone (30% width)**: Layer identity box
- Layer number + name in header bar (use layer-specific Header BG color)
- Core responsibility (2–3 bullet points, 12px body text)

**Center zone (40% width)**: Four authority columns as sub-boxes
- **Detect** | **Authorize** | **Mutate** | **Certify**
- Each sub-box: 100×60px, shows ✔ / ✖ / ⚠ in 24px bold center-aligned
- Color the sub-box green for ✔, red for ✖, yellow for ⚠

**Right zone (30% width)**: Constraints box
- "Can call subprocess?" — Yes/No
- "Authorizes healing?" — Yes/No
- "Certifies compliance?" — Yes/No
- "May write to filesystem?" — Yes/No
- Use checkmark/cross icons, 11px text

### Layer-Specific Content

| Layer | Header Color | Core Responsibility | Detect | Authorize | Mutate | Certify | Subprocess | Heal Auth | FS Write |
|-------|-------------|---------------------|--------|-----------|--------|---------|------------|-----------|----------|
| **L6** | `#FFB74D` (orange) | Telemetry ingestion, anomaly detection, metrics dashboards, audit log | ✔ | ✖ | ✖ | ✖ | No | No | Log-only |
| **L5** | `#EF9A9A` (red) | Policy enforcement, guardian gates, budget guard, safety boundaries | ✔ | ✔ | ✖ | ✔ | No | Yes (gate) | No |
| **L4** | `#8BBEE8` (blue) | Knowledge graph, semantic memory, episodic memory, embedding services | ✔ | ✖ | ⚠ (own state) | ✖ | No | No | Own DB |
| **L3** | `#CE93D8` (purple) | Phase orchestration, human review queue, pipeline coordination | ✔ | ⚠ (escalation) | ✖ | ✖ | Yes | Delegates | No |
| **L2** | `#4DD0E1` (teal) | Approved fix execution, deterministic order, healing & rollback | ✔ | ✖ | ✔ | ✖ | Yes | Receives | Yes |
| **L1** | `#66BB6A` (green) | Working memory, schema/rules, trajectory replay, prompt optimization | ✔ | ✖ | ✖ | ✖ | No | No | No |
| **L0** | `#F0D060` (yellow) | Contextual routing, policy config verification, typed trace parsing | ✔ | ✖ | ✖ | ✖ | No | No | No |

### Vertical Arrows (Left Margin)

- Downward solid arrow labeled **"Authority flows DOWN"** (L5 → L3 → L2)
- Upward dashed arrow labeled **"Telemetry flows UP"** (L2 → L6)
- X-cross arrow from L6 to L2 labeled **"No direct writes from L6"**

### Bottom Callout Box

**"KEY INVARIANT"** — Red-bordered box, cream fill:
> "Detection is universal. Authorization lives in L5. Mutation lives in L2. Certification lives in L5. No layer may both authorize AND mutate."

### Legend (Bottom-Left)

- ✔ Green = Allowed
- ✖ Red = Forbidden
- ⚠ Yellow = Conditional / Bounded
- Arrow types as defined in global style

---

---

## PNG 2 — Validation vs Healing vs Certification Flow

### Page Title

```
VALIDATION → HEALING → CERTIFICATION: The Enforceable Pipeline
```

### Canvas Size

1920×1080 (landscape, wide pipeline)

### Layout

**Primary structure**: Left-to-right horizontal pipeline with 6 stages.
Each stage is a rounded box (~220×280px) connected by styled arrows.

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐
│  SCAN   │───▶│ DETECT  │───▶│  GATE   │───▶│  HEAL   │───▶│RE-VALIDATE│───▶│ CERTIFY  │
│ (Blue)  │    │ (Blue)  │    │(Yellow) │    │ (Red)   │    │  (Blue)   │    │ (Green)  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └──────────┘    └──────────┘
```

### Stage Details

#### Stage 1: SCAN (Blue fill `#D4EDFC`)
- **Header**: "1. SCAN" in blue header bar `#8BBEE8`
- **Agents**: FCA, LocationAgent, RootHygiene
- **Action**: Enumerate all files, classify types, check locations
- **Output**: `scan_result.json`
- **Icon**: Magnifying glass

#### Stage 2: DETECT (Blue fill `#D4EDFC`)
- **Header**: "2. DETECT" in blue header bar `#8BBEE8`
- **Agents**: HierarchyAgent, ArchitectureGovernor
- **Action**: Compare scan results against structural blueprint
- **Output**: `violation_report.json`
- **Artifact count badge**: Show "N violations" in red pill badge
- **Icon**: Warning triangle

#### Stage 3: GATE (Yellow fill `#FFF3C4`)
- **Header**: "3. GATE" in yellow header bar `#F0D060`
- **Agents**: Guardian, SystemArchitect, BudgetGuard
- **Action**: Evaluate violations, authorize or reject healing
- **Decision tree** (small diagram inside box):
  - Pass ✔ → Continue
  - Escalate → HIL (Human-in-Loop)
  - Reject ✖ → Hard stop
- **Output**: `authorization_token`
- **Icon**: Shield

#### Stage 4: HEAL (Red fill `#FFCDD2`)
- **Header**: "4. HEAL" in red header bar `#EF9A9A`
- **Agents**: L2 Symmetric Validator-Healer Pipe
- **Action**: Execute approved fixes ONLY, deterministic order
- **Constraints** (inside box):
  - Max actions per wave
  - Rollback on failure
  - No unauthorized mutation
- **Output**: `healing_result.json`
- **Icon**: Wrench

#### Stage 5: RE-VALIDATE (Blue fill `#D4EDFC`)
- **Header**: "5. RE-VALIDATE" in blue header bar `#8BBEE8`
- **Agents**: Same validators as Stage 1+2
- **Action**: Re-scan to confirm healing resolved violations
- **Decision** (inside box):
  - All clear → Continue
  - Regressions → ABORT + rollback
- **Output**: `revalidation_report.json`
- **Icon**: Checkmark with magnifying glass

#### Stage 6: CERTIFY (Green fill `#C8E6C9`)
- **Header**: "6. CERTIFY" in green header bar `#81C784`
- **Agents**: L5 certification authority
- **Action**: Stamp compliance, emit telemetry, update baseline
- **Output**: `certification.json`
- **Emits**: Telemetry event to L6
- **Icon**: Green seal / ribbon

### Arrows Between Stages

- Stages 1→2→3: Blue solid arrows (validation phase)
- Stage 3→4: Yellow-to-red gradient arrow labeled **"Authorization Required"**
- Stage 4→5: Red solid arrow
- Stage 5→6: Blue-to-green gradient arrow labeled **"All Clear"**

### Feedback Loops (Dashed Arrows)

- Stage 5 → Stage 4: Red dashed arrow labeled **"Regressions → Rollback"**
- Stage 3 → ABORT box (below pipeline): Red dashed arrow labeled **"Reject → Hard Stop"**
- Stage 3 → HIL box (above pipeline): Yellow dashed arrow labeled **"Escalate → Human Review"**

### Bottom Legend

Four-section color legend:
- **Blue** = Validation only (read-only, no mutation)
- **Yellow** = Authorization (gate decision, no mutation)
- **Red** = Mutation (bounded, approved-only)
- **Green** = Certification (compliance stamp, baseline update)

### Agent Role Annotations

Below the pipeline, a thin horizontal bar mapping agents to stages:
```
FCA ──────────── Scan + Detect
Guardian ─────── Gate
SystemArchitect ─ Gate
L2 Healer ────── Heal
execute_ssot ─── Orchestrates entire pipeline
L5 Certifier ─── Certify
```

---

---

## PNG 3 — execute_ssot vs Guardian Scripts

### Page Title

```
RUNTIME vs CI: execute_ssot vs Guardian Scripts
```

### Canvas Size

1920×1080 (landscape, split canvas)

### Layout

**Split canvas vertically** into two equal halves with a divider line.

```
┌──────────────────────────┐ ║ ┌──────────────────────────┐
│                          │ ║ │                          │
│   GUARDIAN SCRIPTS (CI)  │ ║ │   execute_ssot (RUNTIME) │
│                          │ ║ │                          │
│                          │ ║ │                          │
│                          │ ║ │                          │
└──────────────────────────┘ ║ └──────────────────────────┘
                             ║
       ┌─────────────────────╨─────────────────────┐
       │        SHARED CONTRACTS (BOTTOM)           │
       └───────────────────────────────────────────┘
```

### Left Side: Guardian Scripts (CI)

**Background tint**: Very light red `#FFF5F5`
**Header bar**: Full-width, red `#EF9A9A`, text: **"GUARDIAN SCRIPTS (CI ENFORCEMENT)"**

**Four stacked content boxes** (each ~180px tall):

**Box 1 — "DETERMINISTIC"** (Red-bordered)
- Fixed rules, no learning, no adaptation
- Same input → same output, always
- Icon: Lock

**Box 2 — "NON-MUTATING"** (Red-bordered)
- Read-only filesystem access
- NEVER modifies source files
- NEVER writes healing plans
- Icon: Eye (read-only)

**Box 3 — "HARD INVARIANT ENFORCEMENT"** (Red-bordered)
- Layer boundary violations → FAIL
- Import cycles → FAIL
- Phantom drift → FAIL
- Shim structural violations → FAIL
- Non-canonical paths → FAIL
- Icon: Gavel

**Box 4 — "FAIL BUILD"** (Red-bordered, bold)
- Exit code != 0 → PR blocked
- No partial pass
- No auto-fix in CI
- `pytest -xvv` strict mode
- Icon: Red octagon (stop sign)

**Left margin vertical text**: "PREVENTION" (rotated 90° CCW, red, 24px bold)

### Right Side: execute_ssot (Runtime)

**Background tint**: Very light teal `#F0FFFE`
**Header bar**: Full-width, teal `#4DD0E1`, text: **"execute_ssot (RUNTIME ORCHESTRATOR)"**

**Four stacked content boxes** (each ~180px tall):

**Box 1 — "PHASE ENGINE"** (Teal-bordered)
- Runs phases 0→N sequentially
- Each phase: scan → detect → gate → heal → validate
- Phase fails → STOP (no skip)
- Icon: Gear sequence

**Box 2 — "MAY HEAL (BOUNDED)"** (Teal-bordered)
- Delegates to L2 Healer Pipe
- Bounded by wave model (see PNG 4)
- Max actions per wave enforced
- Rollback on any failure
- Icon: Wrench with guardrails

**Box 3 — "CONFIDENCE GATED"** (Teal-bordered)
- Each action has confidence score
- Below threshold → escalate to HIL
- Above threshold → auto-execute
- Budget guard enforced per phase
- Icon: Gauge / meter

**Box 4 — "CERTIFIES"** (Green-bordered, not teal)
- Emits certification artifact on success
- Updates baseline JSON
- Emits telemetry to L6
- Produces audit trail
- Icon: Green seal

**Right margin vertical text**: "REPAIR" (rotated 90° CW, teal, 24px bold)

### Center Divider

- Vertical double-line (`║`) in `#607D8B`, 3px wide
- Label at top center: **"BOUNDARY"** in 14px bold
- Red X-cross icon at center of divider with label: **"No CI script may call execute_ssot"**
- Another X-cross below: **"No runtime healer may bypass Guardian invariants"**

### Bottom: Shared Contracts

**Full-width box** spanning both halves:
- Fill: `#ECEFF1` (neutral gray)
- Header: **"SHARED CONTRACTS"**
- Content in 3 columns:

| Column 1: Schemas | Column 2: Artifact Types | Column 3: Invariant Definitions |
|---|---|---|
| `structure_blueprint.py` | `result.json` | Layer boundary rules |
| `structure_blueprint_config.py` | `violation_report.json` | Import cycle definitions |
| `agent_discovery_full.json` | `healing_plan.json` | Phantom baseline sets |
| `classification_kernel.py` | `certification.json` | Canonical path normalization |

### Arrows

- From Left (Guardian) down to Shared Contracts: Blue dashed arrow labeled **"Reads contracts"**
- From Right (execute_ssot) down to Shared Contracts: Blue dashed arrow labeled **"Reads + updates contracts"**
- From Right Box 4 (Certifies) → diagonal arrow to Left side labeled **"Certification makes next CI run pass"** (green dashed)

---

---

## PNG 4 — Healing Wave Model

### Page Title

```
HEALING WAVE MODEL: Bounded Mutation with Blast-Radius Control
```

### Canvas Size

1920×1200 (slightly taller for wave visualization)

### Layout

**Three zones**: Repository box (top), Wave sequence (center), Hard-stop conditions (bottom).

### Top Zone: Repository State Box

**Large rounded rectangle** (~1600×200px), fill `#ECEFF1`:
- Title: **"REPOSITORY STATE"**
- Inside: scatter of small colored dots representing violations:
  - Red dots = layer violations
  - Orange dots = misplaced files
  - Yellow dots = naming violations
  - Purple dots = import issues
- Label: **"N violations detected"** in red pill badge
- Subtitle: "Violations clustered by type and blast-radius"

### Center Zone: Wave Sequence

**Three wave boxes** arranged left-to-right, connected by arrows.
Each wave box is ~380×400px.

#### Wave 1 Box

- Fill: `#E8F5E9` (very light green — safest)
- Border: `#2E7D32` 2px
- Header: **"WAVE 1: Safe Renames"** on green bar `#66BB6A`

**Inside box — structured layout**:

| Property | Value |
|---|---|
| `wave_id` | `1` |
| `allow_action_types` | `[rename, move_to_correct_folder]` |
| `max_actions_per_wave` | `10` |
| `confidence_threshold` | `0.95` |
| `requires_human_review` | `false` |

**Visual**: 10 small file-icon slots (like progress bar), first few filled green

**Post-wave validation box** (nested, blue fill):
- "Re-scan all affected files"
- "Verify no import breakage"
- "Confirm zero regressions"
- Arrow: ✔ → Wave 2 | ✖ → ROLLBACK

#### Wave 2 Box

- Fill: `#FFF8E1` (very light yellow — moderate risk)
- Border: `#F9A825` 2px
- Header: **"WAVE 2: Import Fixes"** on yellow bar `#FFD54F`

| Property | Value |
|---|---|
| `wave_id` | `2` |
| `allow_action_types` | `[update_import, add_shim, update_init]` |
| `max_actions_per_wave` | `15` |
| `confidence_threshold` | `0.90` |
| `requires_human_review` | `false` |

**Visual**: 15 small import-icon slots, partially filled yellow

**Post-wave validation box** (nested, blue fill):
- "Run import cycle detection"
- "Verify all imports resolve"
- "Run affected test subset"
- Arrow: ✔ → Wave 3 | ✖ → ROLLBACK

#### Wave 3 Box

- Fill: `#FFF3E0` (very light orange — highest risk)
- Border: `#E65100` 2px
- Header: **"WAVE 3: Structural Changes"** on orange bar `#FFB74D`

| Property | Value |
|---|---|
| `wave_id` | `3` |
| `allow_action_types` | `[merge_agent, retire_agent, create_executor]` |
| `max_actions_per_wave` | `5` |
| `confidence_threshold` | `0.98` |
| `requires_human_review` | `true` |

**Visual**: 5 large agent-icon slots, requires approval badge

**Post-wave validation box** (nested, blue fill):
- "Full discovery re-run"
- "Full test suite"
- "Baseline snapshot comparison"
- Arrow: ✔ → CERTIFY | ✖ → ROLLBACK

### Arrows Between Waves

- Wave 1 → Wave 2: Green-to-yellow gradient arrow, labeled **"All 10 actions clean"**
- Wave 2 → Wave 3: Yellow-to-orange gradient arrow, labeled **"All 15 actions clean"**
- After Wave 3 → Green certification seal icon, labeled **"Emit certification"**

### Bottom Zone: Hard Stop Conditions

**Red-bordered box** spanning full width (~1600×160px):
- Fill: `#FFEBEE`
- Header: **"HARD STOP CONDITIONS"** on red bar `#EF5350`

**Three sub-boxes** in a row:

**Stop 1 — "Collision Detected"**
- Two files claim same target path
- Icon: Two arrows pointing at same spot
- Action: "ABORT wave, rollback ALL"

**Stop 2 — "Import Impact Too High"**
- Action affects >25 downstream files
- Icon: Explosion / blast radius circle
- Action: "ABORT wave, escalate to HIL"

**Stop 3 — "Wave Cap Exceeded"**
- Actions exceed `max_actions_per_wave`
- Icon: Gauge in red zone
- Action: "Split into sub-waves, re-queue"

### Rollback Arrows

- From each wave's validation failure: Red dashed arrow curving down to a **"ROLLBACK ENGINE"** box at bottom-left
- Rollback box: Teal fill `#B2EBF2`, contains:
  - "Restore from pre-wave snapshot"
  - "Byte-for-byte file restoration"
  - "Re-run validators to confirm clean state"

### Legend

- Wave risk gradient: Green → Yellow → Orange (safest → riskiest)
- ✔ = Post-wave validation passed
- ✖ = Post-wave validation failed → rollback
- Red border = hard stop / abort condition
- Blue nested box = validation checkpoint

---

---

## PNG 5 — Agent Responsibility Matrix

### Page Title

```
AGENT RESPONSIBILITY MATRIX: Target-State Authority Map
```

### Canvas Size

1920×1080 (landscape, table-optimized)

### Layout

**Primary structure**: Large data table (grid) centered on canvas.
Surrounding annotation boxes for context.

### Grid Specification

**8 rows × 6 columns** + header row + header column

#### Column Headers (Top Row)

| Col | Header | Color | Width |
|-----|--------|-------|-------|
| 0 | (Agent name col) | `#ECEFF1` | 260px |
| 1 | **Detect** | `#D4EDFC` (blue) | 140px |
| 2 | **Plan** | `#FFF3C4` (yellow) | 140px |
| 3 | **Authorize** | `#FFF3C4` (yellow) | 140px |
| 4 | **Heal** | `#FFCDD2` (red) | 140px |
| 5 | **Certify** | `#C8E6C9` (green) | 140px |
| 6 | **Mutate Files Directly** | `#FFCDD2` (red) | 180px |

Column headers: 14px bold, centered, on colored header bar matching semantic color.

#### Row Headers (Left Column)

Each row 60px tall. Agent name in bold 13px, with layer badge (e.g., "[L5]") as colored pill.

#### Grid Data

| Agent | Layer | Detect | Plan | Authorize | Heal | Certify | Mutate Files |
|-------|-------|--------|------|-----------|------|---------|-------------|
| **FileClassificationAgent (FCA)** | L5 | ✔ | ✖ | ✖ | ✖ | ✖ | ✖ |
| **HierarchyAgent** | L5 | ✔ | ✔ | ✖ | ✖ | ✖ | ✖ |
| **LocationAgent** | L5 | ✔ | ⚠ Deprecated | ✖ | ✖ | ✖ | ✖ |
| **ArchitectureGovernor** | L5 | ✔ | ✔ | ⚠ Advisory | ✖ | ✖ | ✖ |
| **SystemArchitect** | L5 | ✔ | ✔ | ✔ | ✖ | ✔ | ✖ |
| **RootHygiene** | L5 | ✔ | ✖ | ✖ | ✖ | ✖ | ✖ |
| **execute_ssot** | L3 | ✔ | ✔ | ⚠ Delegates to L5 | ⚠ Delegates to L2 | ⚠ Delegates to L5 | ✖ |
| **Guardian (CI)** | CI | ✔ | ✖ | ✖ | ✖ | ✖ | ✖ |

### Cell Styling

| Symbol | Background | Text Color | Font |
|--------|-----------|------------|------|
| ✔ Allowed | `#E8F5E9` | `#2E7D32` | 20px bold checkmark + "Allowed" 10px |
| ✖ Forbidden | `#FFEBEE` | `#C62828` | 20px bold cross + "Forbidden" 10px |
| ⚠ Conditional | `#FFF8E1` | `#F57F17` | 20px bold warning + qualifier text 10px |

### Grid Styling

- Cell borders: 1px `#B0BEC5`
- Alternating row tint: odd rows white, even rows `#FAFAFA`
- Header row: 50px tall, bold text, stronger background
- Header column: 60px tall per row, left-aligned

### Annotation Boxes

**Top-right callout** (teal box):
> **"KEY PRINCIPLE"**: Only L2 may mutate files. Only L5 may authorize. Only L5 may certify. execute_ssot orchestrates but owns nothing.

**Bottom-left callout** (red box):
> **"INVARIANT"**: No agent appears in BOTH the "Authorize" and "Heal" columns as ✔. Separation of authorization and mutation is constitutional.

**Bottom-right callout** (blue box):
> **"Guardian (CI)"**: The ONLY row with ALL ✖ except Detect. CI detects, never repairs. This is §24.

### Row Grouping Indicators

Left margin brackets grouping:
- Rows 1–6: Bracket labeled **"L5 Safety Agents"**
- Row 7: Bracket labeled **"L3 Orchestrator"**
- Row 8: Bracket labeled **"CI Enforcement"**

### Optional Enhancement

Below the main grid, a smaller **"Target-State Migration Notes"** table:

| Agent | Current Status | Target Status |
|-------|---------------|---------------|
| LocationAgent | Active (deprecated) | Retire → FCA absorbs detection |
| ArchitectureGovernor | Active | Advisory-only authority |
| execute_ssot | Active | Phase engine, zero direct ownership |

---

---

## Figma Component Library Setup

Before building the PNGs, create these reusable Figma components:

### Auto-Layout Components

1. **LayerBand** — Horizontal auto-layout, layer color header, 3-zone content
2. **PipelineStage** — Vertical auto-layout, colored header, bullet list, output label
3. **AuthorityCell** — Fixed-size cell with ✔/✖/⚠ icon + qualifier text
4. **WaveBox** — Vertical auto-layout, property table + validation sub-box
5. **CalloutBox** — Auto-layout, colored border, icon + quote text
6. **LegendBox** — Auto-layout, arrow samples + color swatches + labels
7. **ArrowConnector** — Line with configurable dash pattern + head type

### Color Styles (Figma)

Create named color styles matching the semantic palette:
- `Core/Fill`, `Core/Border`, `Core/Header`
- `Knowledge/Fill`, `Knowledge/Border`, `Knowledge/Header`
- `Cognition/Fill`, `Cognition/Border`, `Cognition/Header`
- `Execution/Fill`, `Execution/Border`, `Execution/Header`
- `Orchestration/Fill`, `Orchestration/Border`, `Orchestration/Header`
- `Governance/Fill`, `Governance/Border`, `Governance/Header`
- `Observability/Fill`, `Observability/Border`, `Observability/Header`
- `Certification/Fill`, `Certification/Border`, `Certification/Header`
- `Neutral/Fill`, `Neutral/Border`, `Neutral/Header`
- `Cell/Allowed`, `Cell/Forbidden`, `Cell/Conditional`

### Text Styles (Figma)

- `Heading/PageTitle` — 28px 800
- `Heading/SectionHeader` — 18px 700
- `Heading/BoxTitle` — 15px 700
- `Body/Default` — 12px 500
- `Body/ArrowLabel` — 10px 600 Italic
- `Body/Legend` — 11px 500
- `Symbol/CellIcon` — 20px bold (for ✔/✖/⚠)

---

## Build Order Recommendation

1. **PNG 5 (Matrix)** — Fastest to build, immediately resolves agent confusion
2. **PNG 1 (Authority Stack)** — Second priority, resolves layer confusion
3. **PNG 3 (CI vs Runtime)** — Third, resolves execute_ssot vs Guardian
4. **PNG 2 (Pipeline)** — Fourth, ties validation-healing-certification together
5. **PNG 4 (Wave Model)** — Last, requires understanding from PNGs 1-3 first

---

## Export Settings

| Setting | Value |
|---------|-------|
| Format | PNG |
| Scale | 2x (retina) |
| Background | Include (`#F5F0E1`) |
| Suffix | `_2x` |
| Naming | `PNG1_Authority_Stack_2x.png`, etc. |

---

*Generated 2026-02-11 for Agentic-Workflow architectural training set.*

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

