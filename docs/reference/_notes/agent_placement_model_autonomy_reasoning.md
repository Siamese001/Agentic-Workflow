AGENT PLACEMENT MODEL: AUTONOMY x REASONING
============================================

Core rule:
LLM use is a capability. Agent behavior is a control pattern.

Agent = dynamic next-action selection toward a bounded goal.
Not agent = fixed action, fixed workflow, retrieval, assembly, validation, judging, or storage.


                              HIGH REASONING / JUDGMENT
                                       ^
                                       |
                                       |
        +------------------------------+------------------------------+
        |                              |                              |
        |  LLM SCRIPT / JUDGE          |  BOUNDED AGENT               |
        |                              |                              |
        |  Low autonomy                |  High autonomy               |
        |  High reasoning              |  High reasoning              |
        |                              |                              |
        |  Uses model for one bounded  |  Uses model/tools to choose  |
        |  judgment or generation step |  next bounded action         |
        |                              |                              |
        |  Examples:                   |  Examples:                   |
        |  - L1 planning step          |  - L2 task agent             |
        |  - Exit groundedness judge   |  - L2 coding/tool agent      |
        |  - L5 classifier/certifier   |  - L2 underwriting reviewer  |
        |  - LLM summary/extraction    |  - L6 RCA/drift agent        |
        |                              |                              |
        |  Layers here:                |  Layers here:                |
        |  L1, Exit, L5                |  L2, L6 after run only       |
        |                              |                              |
        +------------------------------+------------------------------+
        |                              |                              |
        |  SCRIPT / VALIDATOR          |  ORCHESTRATOR / WORKFLOW     |
        |                              |                              |
        |  Low autonomy                |  Higher control              |
        |  Low reasoning               |  Low to medium reasoning     |
        |                              |                              |
        |  Runs fixed checks or fixed  |  Sequences known steps, DAGs,|
        |  deterministic actions       |  retries, joins, checkpoints |
        |                              |                              |
        |  Examples:                   |  Examples:                   |
        |  - schema validation         |  - workflow controller       |
        |  - quota/auth checks         |  - retry controller          |
        |  - parse/compute/normalize   |  - managed route expansion   |
        |  - state lookup/store        |  - fixed LLM workflow        |
        |                              |                              |
        |  Layers here:                |  Layers here:                |
        |  U0, C0, PA, L4/UWG          |  L0, L3                      |
        |                              |                              |
        +------------------------------+------------------------------+

          LOW AUTONOMY ------------------------------------> HIGH AUTONOMY
          fixed action / fixed check                         chooses next action


LAYER PLACEMENT SUMMARY
=======================

U0      = script / validator        no agent
L1      = LLM script                usually no agent
L0      = deterministic router      no agent
C0      = retrieval engine          no agent
PA      = prompt compiler           no agent
L3      = orchestrator              no agent
L2      = bounded worker            agents allowed here
Exit    = judge / evaluator         no agent
L4/UWG  = state / write gateway     no agent
L5      = certifier / guardrail     no agent
L6      = shadow evaluator          agents allowed after run only


FINAL RULE
==========

A script can call an LLM.
An orchestrator can call an LLM.
A judge can call an LLM.

None of those are agents unless they choose the next bounded action toward a goal.

Live agents belong in L2.
After-run learning agents belong in L6.
Everything else should stay script, validator, compiler, retriever, router, orchestrator, judge, certifier, or state store.