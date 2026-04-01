[ ⚙️ L2 SECURE CONSERVATION LAB (Restorer's Airgapped Vault) ]
                                                          │
                                                          │ (Restorer pushes work order through the single-direction pneumatic tube)
                                                          ▼
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ THE UNIVERSAL WRITE GATEWAY (UWG) - The Master Ledger Clerk                                                                                                          ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                                                                                                      ║
║  1.0 THE SOUNDPROOF VAULT & PNEUMATIC TUBE (L2 -> UWG Physical Isolation)                                                                                            ║
║  [1.1] Network Blackhole: The Restorer (L2) works in a sealed, windowless room with absolutely zero outside access. They cannot walk to                              ║
║        the Deep Archive (L4).                                                                                                                                        ║
║  [1.2] Virtio-Vsock Bridge: The ONLY egress path is sliding their work through a specialized, single-direction pneumatic tube to the Master Ledger Clerk             ║
║        (UWG) on the outside.                                                                                                                                         ║
║  [1.3] Syscall Proxy: Any tools the Restorer uses are automatically proxied and funneled directly into this tube.                                                    ║
║                                                                                                                                                                      ║
║                                                          │                                                                                                           ║
║                                                          ▼ (Raw Write Intent Payload)                                                                                ║
║                                                                                                                                                                      ║
║  2.0 THE COMMANDANT'S PERIMETER CHECK (L5 Intent Validation)                                                                                                         ║
║  [2.1] Target Resolution: The Master Ledger Clerk (UWG) maps the requested action to a specific restricted shelf (L4 Capability schema).                             ║
║  [2.2] RBAC Verification: The Armed Commandant (L5) checks if these tools were explicitly approved on the original routing slip; if not, it is a Hard Reject.        ║
║  [2.3] Blast Radius Check: The Commandant verifies the Restorer isn't trying to rewrite too many books at once.                                                      ║
║                                                                                                                                                                      ║
║    (IF REJECTED) ───────────────────────────────────────┐                                                                                                            ║
║                                                         │ (Passes Validation)                                                                                        ║
║                                                         ▼                                                                                                            ║
║                                                                                                                                                                      ║
║  3.0 THE EXACT WORD-FOR-WORD COMPARISON & WAX SEAL (UWG Record, L5 Seal, L6 Observe)                                                                                 ║
║  [3.1] RFC 6902 Diffing: The Master Ledger Clerk (UWG) creates a perfect, word-for-word "before and after" comparison rather than just summarizing the               ║
║        action.                                                                                                                                                       ║
║  [3.2] ExecutionTrace Assembly: This comparison is packaged into a strict official audit record.                                                                    ║
║  [3.3] Replay Key Gen: A deterministic, unforgeable hash of the events is generated.                                                                                 ║
║  [3.4] HMAC-SHA256 Signing: The Armed Commandant (L5) stamps the trace with the ultimate cryptographic wax seal. Meanwhile, the                                      ║
║        Compliance Office (L6) strictly observes without interfering, logging the "carbon copies" to the master security footage.                                     ║
║                                                                                                                                                                      ║
║                                                          │                                                                                                           ║
║                                                          ▼ (Signed ExecutionTrace Artifact)                                                                          ║
║                                                                                                                                                                      ║
║  4.0 THE TWO-STEP SHELF PLACEMENT (L4 Execution & 2-Phase Commit)                                                                                                    ║
║  The Master Ledger Clerk (UWG) is the sole authority to claim the write lock in the Deep Archive (L4).                                                                ║
║  [4.1] Phase 1 (Prepare): The Clerk places a "hold" on both the target shelf and the Ledger, waiting for acknowledgment.                                             ║
║  [4.2] Phase 2 (Commit): Upon dual-acknowledgment, the Clerk officially places the physical book and commits the record to the Master State Bus.                     ║
║  [4.3] Rollback Rule: If the book drops or fails halfway, the Clerk instantly issues a Compensating Transaction to reverse the ledger entry and routes               ║
║        the failure to the Healer Agent (L2.3).                                                                                                                       ║
║                                                                                                                                                                      ║
║    (IF ROLLBACK) ───────────────────────────────────────┤                                                                                                            ║
║                                                         │ (Commit Successful)                                                                                        ║
║                                                         ▼                                                                                                            ║
║                                                                                                                                                                      ║
║  5.0 THE INSTANT INDEX CARD SHRED & SYNC (C0 / L1 Knowledge Update)                                                                                                  ║
║  [5.1] Content Type Check: The Clerk checks if the mutation altered a text document, resume, or wiki.                                                                 ║
║  [5.2] Asynchronous Extraction: If yes, the Clerk immediately asks the L4 Labeling Services to extract the new information.                                         ║
║  [5.3] Embedding Recalculation: The library's Index Card Catalog is forced to recalculate its cross-references.                                                      ║
║  [5.4] Vector Store Swap: Old index cards are shredded and new ones swapped in atomically. This guarantees the Senior Research                                       ║
║        Librarian (L1) never pulls stale context from the ephemeral Hot Reserve Cart (C0) on their next cognitive pull.                                               ║
║                                                                                                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
                                                          │                                              ▲
                                                          │ (Change Confirmed & Logged in L4)            │ (UWG throws error back)
                                                          ▼                                              │
╔══════════════════════════════════════════════════════════════════════════╗    ╔══════════════════════════════════════════════════════════════════════╗
║ 🏁 OUTCOME & SYNTHESIS (Teardown & Update)                               ║    ║ 🏥 L2.3 HEALER AGENT (Senior Restorer / QC)                          ║
╠══════════════════════════════════════════════════════════════════════════╣    ╠══════════════════════════════════════════════════════════════════════╣
║ • Physically Demolish the L2 Vault (Teardown).                           ║    ║ The Senior Restorer steps in to fix the drafted work.                ║
║ • Return Filtered Summary to 🤖 L1 (Senior Research Librarian).          ║    ║ • Analyzes the FailureSignal from the UWG.                           ║
║                                                                          ║    ║ • If fixable locally, repairs the work and sends back to L2.1        ║
║                                                                          ║    ║ • If unfixable, pulls the Fire Alarm (BUS E) to escalate to Path D   ║
║                                                                          ║    ║   (Human Head Librarian Review).                                     ║
╚══════════════════════════════════════════════════════════════════════════╝    ╚══════════════════════════════════════════════════════════════════════╝
