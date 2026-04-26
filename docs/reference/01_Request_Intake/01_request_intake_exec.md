========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 01_Request_Intake
Canonical file: 01_request_intake_exec.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: 01_request_intake_exec.md
Owner summary: U0 intake only. Owns transport/envelope validation, identity/session/tenant baseline, quota, schema normalization, origin labels, and ValidatedRequest/RejectedRequest handoff.

GLOBAL NO-OVERLAP LAW
- 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission.
- 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics.
- 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence.
- 00X owns traceability and no-loss mapping only.
- 01 Intake owns request envelope validation and identity/session/tenant baseline only.
- 02 L1 owns advisory interpretation and planning only.
- 03 L0/L3 owns deterministic route selection and optional workflow orchestration only.
- C0 owns retrieval/evidence contracts only.
- PA owns prompt packet construction only.
- 04 L2 owns bounded execution and sealing only.
- 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only.
- 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only.
- 99 owns proof harnesses only; it does not own runtime behavior.

REFERENCE POINTERS
- Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/
- Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/
- Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/
- Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md
- End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/
========================================================================================================================

======================================================================================================================================
[1] REQUEST INTAKE + ENVELOPE CHECK
[1] THE FRONT DESK | CHECKING THE REQUEST SLIP
======================================================================================================================================
- The front door of the library where every request is initially received, checked for basic validity, identity, quotas,
  and structural correctness before any actual thinking, retrieval, routing, or execution begins.
- The library security guard and front desk greeter who checks your library card, screens for banned items, starts the
  tracking ticket, normalizes the form, and stamps a bounded request slip that later staff are allowed to read.

                                                                  [ arrive ]
                                                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ U0 HOW PATRONS CONTACT US                                                                                                          │
│ ┌────────────────────────────────┐ ┌────────────────────────────────┐ ┌────────────────────────────────┐ ┌───────────────────────┐ │
│ │ U1 WALKING IN / CALLING        │ │ U2 OTHER LIBRARIES             │ │ U3 THE MAIL ROOM               │ │ U4 AUTOMATED ALERTS   │ │
│ │ - direct conversation          │ │ - formal transfers             │ │ - scheduled deliveries         │ │ - callbacks/webhooks  │ │
│ │ - chat / UI sessions           │ │ - service-to-service handoff   │ │ - recurring jobs               │ │ - async notices       │ │
│ │ - live front desk requests     │ │ - official forms / APIs        │ │ - batch drop-offs              │ │ - system alarm pings  │ │
│ └───────────────┬────────────────┘ └───────────────┬────────────────┘ └───────────────┬────────────────┘ └───────────┬───────────┘ │
│                 │                                  │                                  │                            │               │
│             [source]                           [source]                           [source]                     [source]            │
│                 └──────────────────────────────────┴───────────────┬──────────────────┴────────────────────────────┘               │
│                                                                    │                                                               │
│                                                                [ queue ]                                                           │
│                                                                    ▼                                                               │
│                                 [ people, forms, callbacks, alerts, and batched letters waiting in line ]                          │
└────────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                                                 [ intake ]
                                                                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ THE FRONT DESK / SECURITY CHECK                                                                                                    │
│ Rule: We do not answer, reason, retrieve, or route here. We only validate the envelope, normalize the slip, and stamp ingress.     │
│ invariant: No semantic routing, no L1 planning, no C0 retrieval, no external calls, no mutation authority.                         │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────┐ ┌────────────────────────────────────────┐ ┌────────────────────────────────────────┐  │
│  │ E1 IS IT A REAL REQUEST?               │ │ E2 CHECKING LIBRARY CARDS              │ │ E3 CHECKING DAILY LIMITS               │  │
│  │ - accepted transport / form            │ │ - auth / identity verification         │ │ - quota enforcement                    │  │
│  │ - request shell exists                 │ │ - caller / tenant binding              │ │ - burst / abuse control                │  │
│  │ - request_id / session_id assigned     │ │ - access-rights baseline               │ │ - duplicate suppression                │  │
│  │ - trace_root started                   │ │ - banned / allowed class               │ │ - same-ask spam guard                  │  │
│  │ - ingress envelope opened              │ │ - region / scope baseline              │ │ - early deny before load               │  │
│  └───────────────────┬────────────────────┘ └───────────────────┬────────────────────┘ └───────────────────┬────────────────────┘  │
│                   [verify]                                     [verify]                                     [check]                    │
│                      │                                            │                                            │                       │
│                      ▼                                            ▼                                            ▼                       │
│  ┌────────────────────────────────────────┐ ┌────────────────────────────────────────┐ ┌────────────────────────────────────────┐  │
│  │ E4 DID YOU FILL OUT THE FORM?          │ │ E5 FIXING MESSY HANDWRITING            │ │ E6 STAMPING THE TICKET                 │  │
│  │ - schema / envelope validity           │ │ - encoding normalization               │ │ - validated_request                    │  │
│  │ - required fields present              │ │ - bounded clean payload                │ │ - request_id / trace_root              │  │
│  │ - malformed requests rejected          │ │ - tidy malformed spacing               │ │ - caller scope baseline                │  │
│  │ - supported request shape only         │ │ - normalize delimiters / casing        │ │ - ingress_time / tenancy stamp         │  │
│  │ - attach rejection reason if fail      │ │ - strip unsupported transport noise    │ │ - safe for staff to read               │  │
│  └───────────────────┬────────────────────┘ └───────────────────┬────────────────────┘ └───────────────────┬────────────────────┘  │
│                  [validate]                                    [clean]                                      [stamp]                    │
│                      └──────────────────────────────────────────┴──────────────────────────────────────────┘                       │
│                                                                    ▼                                                               │
│                            [ a clean, stamped request slip with tracking number and bounded caller scope ]                         │
└──────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                   │
                                                                   ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ INGRESS OUTPUT CONTRACT                                                                                                            │
│ - validated_request                                                                                                                │
│ - request_id / session_id / trace_root                                                                                             │
│ - caller_scope_baseline / tenant bind / access baseline                                                                            │
│ - normalized payload                                                                                                               │
│ - rejection reason if denied                                                                                                       │
│ - enough structure for L1 to read, but not enough authority for any execution                                                      │
│ invariant: ingress stamps the slip but does not decide the route or answer the patron                                              │
└──────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                                   │
                                                   ┌───────────────┴───────────────┐
                                          [ pass ] │                               │ [ fail ]
                                                   ▼                               ▼
                                     ┌───────────────────────────┐   ┌─────────────────────────────┐
                                     │ Send to Research Desk [2] │   │ Reject / Ask to Refill Form │
                                     └───────────────────────────┘   └─────────────────────────────┘