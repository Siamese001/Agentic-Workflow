1. RUNTIME = protect the current run
   apps_rg executes one request
   → X1 checks
   → X2 aggregates
   → X3 decides
   → Exit

2. apps_eval = test the app across scenarios
   replay snapshots or controlled live-adapter cases
   → run graders
   → score scenarios
   → detect regressions
   → build flywheel of known failure modes

3. L6 SHADOW OBSERVABILITY = audit the completed evidence
   consume completed run/eval artifacts only
   → prove run is closed
   → prove evidence is complete
   → prove observer stayed read-only
   → enforce no current-run mutation / no X3 change / no L4 or BUS_U write

4. SYSTEM / META LEARNING = improve future runs only
   use approved completed evidence
   → propose better tests, prompts, policies, rubrics, guardrails
   → route through governed review/promotion
   → affect future behavior, never the current run

Shortest version:

Runtime protects one run.
apps_eval tests many scenarios.
L6 shadow obs guards the evidence.
System learning improves future runs.

Even shorter:

Run safely → test broadly → observe safely → learn later.
