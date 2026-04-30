UPSTREAM WORK ARRIVES AT EXIT
────────────────────────────────────────────────────────────────────
Exit can receive work from four places:

 L2 finished one bounded task
 L3 finished a managed workflow
 L0 returned a cache / fallback result
 HITL returned a human-reviewed packet that was re-cleared

        │
        ▼

┌──────────────────────────────────────────────────────────────────┐
│ 05.1 GET THE PACKET INTO ONE STANDARD SHAPE                       │
│                                                                  │
│ Take whatever sealed work arrived and convert it into one         │
│ standard ExitReviewPacket.                                       │
│                                                                  │
│ Keep the proof attached: where it came from, who had authority,   │
│ receipts, hashes, route references, and trace history.            │
└───────────────┬──────────────────────────────────────────────────┘
                │
                ▼

┌──────────────────────────────────────────────────────────────────┐
│ 05.2 CHECK THE ACTUAL WORK                                        │
│                                                                  │
│ X1A Current rules       Were the right policy, thresholds, and     │
│                         graders used?                            │
│                                                                  │
│ X1B Completed task      Did it answer the task in the required     │
│                         format without overclaiming?              │
│                                                                  │
│ X1C Safe to release     Is it safe, within sandbox limits, and     │
│                         free of direct write attempts?            │
│                                                                  │
│ X1D Evidence supported  Is it grounded, cited, and backed by       │
│                         enough support?                          │
│                                                                  │
│ X1E Process was sound   Were tool choices, retries, and handoffs   │
│                         reasonable?                              │
│                                                                  │
│ X1F Attack resistant    Did it handle injection, leakage, and      │
│                         adversarial content safely?               │
└───────────────┬──────────────────────────────────────────────────┘
                │
                ▼

┌──────────────────────────────────────────────────────────────────┐
│ 05.3 CHECK THAT THE RUN CAN BE TRUSTED                            │
│                                                                  │
│ X1G Replayable         Can the run be replayed from the same       │
│                        receipts and manifests?                    │
│                                                                  │
│ X1H Observable         Do the traces, counters, and logs prove     │
│                        what happened?                            │
│                                                                  │
│ X1I Consistent         If repeated checks are active, is the       │
│                        result stable enough?                      │
└───────────────┬──────────────────────────────────────────────────┘
                │
                ▼

┌──────────────────────────────────────────────────────────────────┐
│ 05.4 CHECK WHETHER A WRITE IS EVEN ALLOWED                        │
│                                                                  │
│ Only runs if the packet wants to change durable state.            │
│                                                                  │
│ Check the proposed change, blast radius, rollback path, and        │
│ clearance evidence.                                               │
│                                                                  │
│ Exit may prepare a CommitRequest, but Exit does not commit.       │
└───────────────┬──────────────────────────────────────────────────┘
                │
                ▼

┌──────────────────────────────────────────────────────────────────┐
│ 05.5 COMBINE THE CHECK RESULTS                                    │
│                                                                  │
│ Bring all checkout results together in one deterministic decision │
│ step: work quality, evidence, policy, route risk, HITL status,     │
│ live anomaly signals, and write eligibility.                      │
└───────────────┬──────────────────────────────────────────────────┘
                │
                ▼

┌──────────────────────────────────────────────────────────────────┐
│ 05.5 CHOOSE EXACTLY ONE EXIT OUTCOME                              │
│                                                                  │
│ X3A Stop or reroute safely                                        │
│ X3B Escalate to human review                                      │
│ X3C Send commit request to UWG only                               │
│ X3D Allow the answer or result to finish                          │
│ X3E Safely abstain or ask for clarification                       │
│                                                                  │
│ Hard rule: one run gets one Exit outcome.                         │
└───────┬───────────────┬───────────────┬───────────────┬──────────┘
        │               │               │               │
        ▼               ▼               ▼               ▼

   STOP / REROUTE     HUMAN REVIEW      UWG ONLY        RETURN
   no hidden retry    freeze run        request commit  final or safe payload
                      re-clear by L5    no direct L4 write

        │               │               │               │
        └───────────────┴───────────────┴───────────────┘
                                │
                                ▼

┌──────────────────────────────────────────────────────────────────┐
│ 05.7 RETURN THE SAFE RESULT AND SEAL THE RUN RECORD               │
│                                                                  │
│ Only return what is allowed after the X3 outcome is final.        │
│                                                                  │
│ Seal the RuntimeExhaustManifest so the completed run can be        │
│ reviewed later.                                                   │
│                                                                  │
│ Hand the sealed exhaust to L6 only after the live run is closed.  │
└──────────────────────────────────────────────────────────────────┘


CROSS-CUTTING PROOF
────────────────────────────────────────────────────────────────────
05.8 proves the checkout really happened.

It verifies:
- required traces and attributes exist
- anti-bypass tests passed
- replay evidence is present
- Exit did not write directly to L4
- L6 did not rescue or mutate the live run
- no hidden or missing disposition occurred