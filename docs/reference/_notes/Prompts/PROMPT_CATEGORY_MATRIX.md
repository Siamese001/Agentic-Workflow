PROMPT CATEGORY MATRIX
apps_rg CLI -> Agentic Core governed prompt lifecycle

PURPOSE
=======

Resolve prompt ownership confusion by separating four different prompt-like objects:

1. Sub-agent prompts
   - L1P = Core-owned planning prompt/template
   - Route = Core-owned route prompt/rules

2. Raw material
   - AppAsset = apps_rg domain prompt material
   - ToolAsset = tool specs, schemas, tool descriptions, constraints

3. Compiled artifact
   - Final = provider-ready compiled prompt artifact

4. Slots inside Final
   - S0, D0, I0, E0, C0, M0, U0, H0, R0, T0, Y0, V0


LEGEND
======

A = authors / composes with authority
X = actively consumes and acts on
M = produces material for later assembly
R = read-only inspection, validation, or audit
S = stores / persists durably
- = not used here


CANONICAL MATRIX
================

                    | Sub-agent prompts |        Material         | Compiled |                  Slots inside Final Prompt                  |
+-------------------+------+------------+----------+-----------+----------+----+----+----+----+----+----+----+----+----+----+----+----+
| Spine stage       | L1P  | Route      | AppAsset | ToolAsset | Final    | S0 | D0 | I0 | E0 | C0 | M0 | U0 | H0 | R0 | T0 | Y0 | V0 |
+-------------------+------+------------+----------+-----------+----------+----+----+----+----+----+----+----+----+----+----+----+----+
| apps_rg CLI       | -    | -          | -        | -         | -        | -  | -  | -  | -  | -  | -  | M  | -  | -  | -  | -  | -  |
| AppAsset apps_rg  | -    | -          | A        | M         | -        | -  | -  | M  | M  | -  | -  | -  | M  | M  | M  | -  | M  |
| U0 Intake         | -    | -          | -        | -         | -        | -  | M  | -  | -  | -  | -  | A  | -  | -  | -  | -  | -  |
| L1 Plan           | X    | -          | R        | R         | -        | -  | R  | -  | -  | -  | -  | R  | -  | R  | R  | R* | R  |
| L0 Route          | -    | X          | -        | R         | -        | -  | R  | -  | -  | -  | -  | R  | -  | -  | R  | -  | -  |
| C0 Context        | -    | -          | -        | -         | -        | -  | R  | -  | -  | M  | -  | -  | -  | -  | -  | -  | -  |
| Prompt Assembly   | R    | R          | R        | R         | A        | A  | A  | A  | A  | A  | A  | A  | A  | A  | A  | A  | A  |
| L2 E1 Prep        | -    | R          | -        | R         | R        | R  | R  | -  | -  | -  | X  | -  | -  | R  | R  | -  | -  |
| L2 E2 Validate    | -    | R          | -        | X         | R        | R  | X  | R  | -  | R  | -  | R  | -  | X  | X  | -  | X  |
| L2 E3 Execute     | -    | -          | -        | X         | X        | X  | X  | X  | X  | X  | X  | X  | -  | X  | X  | X  | X  |
| L2 E4 Heal        | -    | -          | -        | R         | R        | R  | R  | R  | -  | R  | -  | -  | X  | X  | R  | -  | X  |
| L2 E5 Seal        | -    | -          | -        | R         | R        | -  | -  | -  | -  | -  | -  | -  | -  | X  | R  | -  | X  |
| Exit              | -    | -          | -        | R         | R        | R  | X  | X  | -  | X  | -  | -  | R  | X  | R  | -  | X  |
| UWG / L4          | -    | -          | S        | S         | -        | -  | -  | R  | R  | -  | -  | -  | R  | R  | R  | M  | R  |
| L6 Shadow Eval    | R    | R          | R        | R         | R        | R  | R  | R  | R  | R  | R  | R  | R  | R  | R  | R  | R  |
+-------------------+------+------------+----------+-----------+----------+----+----+----+----+----+----+----+----+----+----+----+----+


IMPORTANT FOOTNOTE
==================

Y0 in L1 Plan is marked R*.

Meaning:
  L1 may read approved L4 planning priors.

Not meaning:
  L1 consumes PA.Y0 as a final prompt slot.

Namespace rule:
  L1.priors = planning priors read by L1
  PA.Y0     = approved learning-prior slot inside the final compiled prompt


COLUMN DEFINITIONS
==================

L1P
  Core-owned internal L1 planning prompt/template.
  Used only by L1 to interpret the ValidatedRequest and emit L1PlanContract.
  Not a Prompt Assembly slot.

Route
  Core-owned routing prompt/rules/policy surface.
  Used by L0 to select exactly one RouteContract.
  Not a final execution prompt.

AppAsset
  apps_rg domain prompt material.
  Examples:
    - resume rewrite instructions
    - executive summary rules
    - resume examples
    - output schema candidate
    - domain rubric candidate
    - same-authority repair hint candidate

ToolAsset
  tool prompt surface and tool contract material.
  Examples:
    - tool definitions
    - tool schemas
    - tool descriptions
    - tool constraints
    - tool-use examples
    - allowed side effects
    - argument rules

Final
  Final compiled provider-ready prompt artifact.
  Created only by Prompt Assembly.
  Executed only by L2 E3.

S0
  Core system invariants.
  Source: Agentic Core.
  Author: Prompt Assembly.

D0
  Defensive fences and prompt-injection boundaries.
  Source: Agentic Core.
  Author: Prompt Assembly.

I0
  Task instructions.
  Source material: apps_rg AppAsset.
  Author: Prompt Assembly.
  Example: resume-specific rewrite instructions.

E0
  Approved examples.
  Source material: apps_rg AppAsset, approved through L4.
  Author: Prompt Assembly.

C0
  Grounded evidence, citations, contradictions, and gaps.
  Source material: C0 FinalEvidenceContract.
  Author: Prompt Assembly.

M0
  Provider-safe control hints.
  Source: Agentic Core.
  Author: Prompt Assembly.

U0
  Neutralized user task and CLI payload.
  Source material: apps_rg CLI through U0 Intake.
  Author: U0 creates neutralized material; Prompt Assembly slots it.

H0
  Repair hints.
  Source material: Core and optional apps_rg same-authority repair hints.
  Author: Prompt Assembly.
  Consumed only when repair is allowed.

R0
  Output schema.
  Source material: apps_rg AppAsset.
  Author: Prompt Assembly binds as schema, not loose prose.

T0
  Tool definitions, tool schemas, and tool-use constraints.
  Source material: Tool Registry and optional apps_rg tool specs.
  Author: Prompt Assembly / provider renderer.
  Prefer provider-native tool fields over loose prose.

Y0
  Approved learning priors.
  Source material: L4/UWG-promoted state only.
  Author: Prompt Assembly.
  Never raw L6 output.

V0
  Validation and evaluation expectations.
  Source material: Core policy plus apps_rg rubric input.
  Author: Prompt Assembly.
  Consumed by L2 validation, L2 heal, Exit, and L6 audit.


END-TO-END FLOW
===============

[ apps_rg CLI ]
  produces:
    U0 material only:
      resume
      role
      company
      briefing
      user options

  does not author:
    I0
    E0
    R0
    T0
    V0
    final prompt

        |
        v

[ AppAsset apps_rg ]
  produces domain material:
    I0 material = resume instructions
    E0 material = resume examples
    H0 material = repair hints
    R0 material = output schema
    T0 material = app tool specs, if any
    V0 material = domain rubric

  does not author final slots.

        |
        v

[ U0 Intake - Agentic Core ]
  validates envelope.
  labels origin.
  neutralizes user task.
  emits ValidatedRequest.

  produces:
    U0 material
    D0 signal material for injection risk

        |
        v

[ L1 Plan - Agentic Core ]
  uses:
    L1P Core planning prompt/template
    ValidatedRequest
    approved L4 planning priors
    optional AppAsset refs for deliverable shape
    optional R0/V0 refs as planning context

  emits:
    L1PlanContract

  does not use:
    final compiled prompt
    PA.I0
    PA.S0-D0-I0-E0-C0-M0-U0-H0-R0-T0-Y0-V0 as a compiled stack

        |
        v

[ L0 Route - Agentic Core ]
  uses:
    Route prompt/rules/policy
    L1PlanContract
    risk and route constraints

  emits:
    exactly one RouteContract

  does not compile or execute prompts.

        |
        v

[ C0 Context - Agentic Core, if grounding required ]
  retrieves and verifies evidence.

  produces:
    C0 material:
      evidence
      citations
      support gaps
      contradictions
      source lineage

  does not answer.
  does not assemble prompt.
  does not treat retrieved text as instruction.

        |
        v

[ Prompt Assembly - Agentic Core ]
  reads:
    L1PlanContract
    RouteContract
    FinalEvidenceContract, if grounding required
    AppAsset refs
    ToolAsset refs
    U0 material
    L5 governance refs
    L4 approved priors, if any

  authors/composes:
    Final compiled prompt artifact

  slots:
    S0 -> D0 -> I0 -> E0 -> C0 -> M0 -> U0 -> H0 -> R0 -> T0 -> Y0 -> V0

  emits:
    CompiledPromptArtifact

        |
        v

[ L2 Execute - Agentic Core ]

  E1 Prep:
    reads Final artifact refs.
    freezes prompt hash, provider lane, replay key, schema refs, tool refs.

  E2 Validate:
    checks D0, R0, T0, V0, route authority, tool authority, evidence readiness.

  E3 Execute:
    consumes rendered Final prompt and provider-native tool/schema bindings.
    performs actual model/tool call.

  E4 Heal:
    consumes H0, R0, V0 only for same-authority repair.
    may inspect D0/I0/C0.
    cannot add authority.
    cannot add new facts without C0 support.

  E5 Seal:
    seals output, prompt lineage, prompt hash, output hash, evidence refs, trace refs.
    checks R0 and V0.

        |
        v

[ Exit - Agentic Core ]
  reads final artifact and sealed L2 result.

  checks:
    S0 invariant preservation
    D0 safety and injection resistance
    I0 task instruction compliance
    C0 grounding and support
    R0 schema compliance
    T0 tool-use compliance, if tools affected output
    V0 quality and evaluation expectations

  emits:
    exactly one X3 disposition

        |
        v

[ UWG / L4 ]
  stores approved AppAssets and ToolAssets.
  stores approved prompt schemas, examples, rubrics, and learning priors.
  produces future Y0 material only after UWG approval.

        |
        v

[ L6 Shadow Evaluation ]
  reads completed-run exhaust.
  audits all prompt surfaces.
  may propose future AppAsset, ToolAsset, V0, or Y0 improvements.
  cannot change current run.
  cannot write L4 directly.


HARD RULES
==========

1. L1P is not I0.
   L1P is a Core planning prompt/template used only by L1.

2. Route is not Final.
   Route is a Core route-selection surface used only by L0.

3. AppAsset is material, not authority.
   apps_rg can produce material for I0/E0/H0/R0/T0/V0.
   Prompt Assembly authors the governed slot instances.

4. CLI produces U0 only.
   apps_rg CLI collects user/domain payload.
   It does not author final prompt instructions.

5. Prompt Assembly is the only final prompt author.
   Every final slot has exactly one A:
     Prompt Assembly.

6. Material source is not slot authority.
   A slot can have upstream M sources, but Core owns final slot authority.

7. D0 owns prompt-injection defense.
   Injection attempts may arrive in U0 or C0 data.
   Defense is Core-owned D0, enforced through Prompt Assembly, L2 Validate, and Exit.

8. C0 is evidence only until slotted.
   C0 retrieves and verifies evidence.
   Prompt Assembly turns that evidence into the C0 slot.

9. T0 is first-class prompt surface.
   Tool definitions and schemas are prompt-relevant.
   Prefer provider-native tool bindings over loose prose.

10. Y0 is future-run only.
    Y0 comes from L4/UWG-approved learning priors.
    Raw L6 proposals are never Y0.

11. L2 consumes, validates, heals, and seals.
    L2 does not invent prompt assets.
    L2 does not widen authority.

12. Exit validates final output against prompt obligations.
    Required checks include S0, D0, I0, C0, R0, T0 when applicable, and V0.

13. L6 observes after runtime only.
    L6 can propose future improvements.
    L6 cannot rescue or mutate the current run.


ONE-LINE MENTAL MODEL
=====================

L1P and Route are upstream Core prompts.
AppAsset and ToolAsset are raw materials.
Prompt Assembly authors the Final prompt.
L2 executes it.
Exit checks it.
UWG/L4 stores approved future materials.
L6 learns only after the run.