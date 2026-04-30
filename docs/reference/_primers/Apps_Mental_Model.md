Bottom line: **`agentic_core` is the runtime, `apps_rg` is a plug-in pack that the runtime uses at specific stations.**

ONE TRAIN. MANY SPECIALIZED CARS.

┌──────────────────────────────────────────────────────────────────────────────┐
│                         AGENTIC_CORE RUNTIME SPINE                           │
│                                                                              │
│  U0 ──► L1 ──► L0 ──► C0 ──► PA ──► L3 ──► L2 ──► EXIT ──► UWG/L4 ──► L6     │
│                                                                              │
│  intake plan  route evidence prompt workflow execute checkout write   learn  │
└──────────────────────────────────────────────────────────────────────────────┘
             ▲          ▲       ▲       ▲        ▲       ▲        ▲       ▲
             │          │       │       │        │       │        │       │
             └────────────── apps_rg plugs in where needed ───────────────┘

## The mental model

agentic_core = operating system
apps_rg      = installed app

agentic_core = airport
apps_rg      = airline

agentic_core = train track + dispatcher + signals
apps_rg      = cargo + specialized railcar

agentic_core = runtime law
apps_rg      = domain behavior


The mistake is thinking:

agentic_core runtime + apps_rg runtime


The right model is:

agentic_core runtime containing apps_rg participation


## The simplest version

User request
   ↓
agentic_core decides what kind of run this is
   ↓
agentic_core calls apps_rg only where apps_rg has specialized value
   ↓
agentic_core keeps control of routing, gates, execution envelope, exit, write, and learning

## Where `apps_rg` can show up

U0  Intake          core only
L1  Planning        apps_rg may help interpret/domain-plan
L0  Routing         core decides route; apps_rg may be selected
C0  Retrieval       apps_rg may provide source adapters/search config
PA  Prompt Assembly apps_rg may provide domain prompt slots
L3  Orchestration   apps_rg may provide workflow templates
L2  Execution       apps_rg agents/tools/skills actually run here
Exit Evaluation     apps_rg may provide rubric/checks
UWG/L4              core only for durable writes
L6  Shadow Learning apps_rg may provide eval pack/future improvement signals

## The high-signal OTel rule

If apps_rg emits a span, it must be a child of a core span.

Bad trace:

trace_1: agentic_core.U0 → L1 → L0 → Exit

trace_2: apps_rg.agent.run

Good trace:

trace_1:
agentic_core.U0
  agentic_core.L1
    apps_rg.planner_overlay
  agentic_core.L0
  agentic_core.C0
    apps_rg.retrieval_adapter
  agentic_core.PA
    apps_rg.prompt_overlay
  agentic_core.L3
    apps_rg.workflow_template
  agentic_core.L2
    apps_rg.agent.run
      apps_rg.tool.call
  agentic_core.Exit
    apps_rg.eval_overlay
  agentic_core.L6
    apps_rg.shadow_eval_pack

## The one-line lock

**`apps_rg` is not a second runtime. It is an app-specific payload carried through the single `agentic_core` runtime, and OTel should prove every `apps_rg` span is parented by the core spine.**
