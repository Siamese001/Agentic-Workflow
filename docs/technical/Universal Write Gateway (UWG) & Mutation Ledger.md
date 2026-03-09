============================================================================================================================================================
                                DRILL-DOWN 6: THE UNIVERSAL WRITE GATEWAY (UWG) & MUTATION LEDGER (QUINTUPLE-CLICK)
     (TENSOR-LEVEL VIEW: VIRTIO-VSOCK INTERCEPTION, DENY-BY-DEFAULT EGRESS, RFC 6902 JSON PATCHING, 2-PHASE COMMITS, & RAG EMBEDDING SYNC)
============================================================================================================================================================

                                   [ FROM: L2.2 FIRECRACKER MICRO-VM (GUEST OS) ]
                                   +---------------------------------------------------------------------------------+
                                   | SandboxEnvelope: { "trace_id": "hex_9f", "tool_id": "sql_write",                |
                                   |                    "sanitized_args": "UPDATE users SET status='active'...",     |
                                   |                    "stdout_byte_limit": 2048, "compute_ms_limit": 5000 }        |
                                   +---------------------------------------------------------------------------------+
                                                         ||
                                                         || (Push: Guest tries to execute a durable write)
                                                         v
+==========================================================================================================================================================+
| \\\ L2 BOUNDARY: THE UNIVERSAL WRITE GATEWAY (UWG) (HOST-LEVEL DAEMON)                                                                              /// |
| \\\ Authority: SOLE MUTATION BROKER. Evaluates all outgoing state changes. Denies by default. Translates raw writes into cryptographic traces.      /// |
|==========================================================================================================================================================|
|                                                                                                                                                          |
|  +-------------------------------------------------------------------------------------------+                                                           |
|  | 1.0 PHYSICAL INTERCEPTION & ISOLATION LAYER (THE AIRGAP)                                  |                                                           |
|  |-------------------------------------------------------------------------------------------|                                                           |
|  | [1.1] Network Blackhole: The Firecracker VM has NO external network interface (eth0 is    |                                                           |
|  |       null-routed). It cannot reach the internet, databases, or the L4 State Bus.         |                                                           |
|  | [1.2] Virtio-Vsock Bridge: The ONLY egress path is a specialized virtio-vsock socket      |                                                           |
|  |       connecting the Guest OS to the UWG Daemon running on the Host OS.                   |                                                           |
|  | [1.3] Syscall Proxy: Tools inside the VM (e.g., Python `requests` or `psycopg2`) are      |                                                           |
|  |       monkey-patched/proxied to route payloads over the vsock to the UWG.                 |                                                           |
|  +-------------------------------------------------------------------------------------------+                                                           |
|                                         ||                                                                                                               |
|                                         v (Raw Write Intent Payload)                                                                                     |
|  +-------------------------------------------------------------------------------------------+                                                           |
|  | 2.0 INTENT VALIDATION & POLICY ENFORCEMENT (DENY-BY-DEFAULT)                              |                                                           |
|  |-------------------------------------------------------------------------------------------|                                                           |
|  | [2.1] Target Resolution: Maps the requested raw write (e.g., `db.execute()`) to a defined |                                                           |
|  |       L4 Capability schema (e.g., `capability_id: 401_user_db_update`).                   |                                                           |
|  | [2.2] RBAC Verification: Cross-references the target capability against the original      |                                                           |
|  |       `InstructionPacket`'s `allowed_tools[]` array. IF NOT IN ARRAY -> Hard Reject.      |                                                           |
|  | [2.3] Blast Radius Check: Limits row-count mutations. (e.g., IF `affected_rows` > 100 AND |                                                           |
|  |       `route_mode` != 'PATH_D' -> Block and Escalate).                                    |                                                           |
|  |                                                                                           |                                                           |
|  | IF REJECTED: UWG throws `ExecutionAccessError` back over vsock to the                     |                                                           |
|  |              Healer Agent [♦ I::IHealer ♦] for recovery or escalation.                    |                                                           |
|  +-------------------------------------------------------------------------------------------+                                                           |
|                                         || (Passes Validation)                                                                                           |
|                                         v                                                                                                                |
|  +-------------------------------------------------------------------------------------------+                                                           |
|  | 3.0 DIFFERENTIAL PACKAGING & CRYPTOGRAPHIC SIGNING                                        |                                                           |
|  |-------------------------------------------------------------------------------------------|                                                           |
|  | [3.1] RFC 6902 Diffing: Compares the `boundary_snapshot.json` (captured at L2.0) with     |                                                           |
|  |       the proposed post-execution state to generate a strict JSON Patch payload.          |                                                           |
|  | [3.2] ExecutionTrace Assembly: Packages the mutation into the strict audit contract:      |                                                           |
|  |       [trace_id, plan_hash, actor, target_resource, state_diff, timestamp, replay_key]    |                                                           |
|  | [3.3] Replay Key Gen: Computes deterministic hash of `(trace + plan + stdout transcript)`.|                                                           |
|  | [3.4] HMAC-SHA256 Signing: UWG signs the `ExecutionTrace` using the L2 Service Key to     |                                                           |
|  |       ensure authenticity when committing to L4.                                          |                                                           |
|  +-------------------------------------------------------------------------------------------+                                                           |
|                                         ||                                                                                                               |
|                                         v (Signed ExecutionTrace Artifact)                                                                               |
|  +-------------------------------------------------------------------------------------------+                                                           |
|  | 4.0 THE 2-PHASE COMMIT (2PC) & DISTRIBUTION ENGINE                                        |                                                           |
|  |-------------------------------------------------------------------------------------------|                                                           |
|  | Phase 1 (Prepare): UWG acquires necessary locks on external target (e.g., API/DB) and     |                                                           |
|  |                    sends intent to L4.B Immutable Ledger. Waits for ACKs.                 |                                                           |
|  | Phase 2 (Commit):  Upon dual-ACK, UWG issues the execute command.                         |                                                           |
|  |                                                                                           |                                                           |
|  | [4.1] To Target Resource: Executes the actual REST/SQL/gRPC call to mutate the world.     |                                                           |
|  | [4.2] To L4 Ledger: Commits the `ExecutionTrace` to the Master State Bus.                 |                                                           |
|  | [4.3] Rollback Rule: IF Phase 2 fails on the Target Resource, UWG emits a `COMPENSATING   |                                                           |
|  |       TRANSACTION` to L4 to reverse the ledger entry and routes failure to                |                                                           |
|  |       the Healer Agent [♦ I::IHealer ♦].                                                  |                                                           |
|  +-------------------------------------------------------------------------------------------+                                                           |
|                                         ||                                                                                                               |
|                                         v (Commit Successful)                                                                                            |
|  +-------------------------------------------------------------------------------------------+                                                           |
|  | 5.0 RAG EMBEDDING SYNC & KNOWLEDGE DRIFT PREVENTION                                       |                                                           |
|  |-------------------------------------------------------------------------------------------|                                                           |
|  | [5.1] Content Type Check: Did this mutation alter a text document, resume, or wiki?       |                                                           |
|  | [5.2] Asynchronous Extraction: If YES, UWG fires an async payload to L4 Labeling Services.|                                                           |
|  | [5.3] Embedding Recalculation: L4 generates new dense vectors (float32 arrays) for the    |                                                           |
|  |       mutated text chunks.                                                                |                                                           |
|  | [5.4] Vector Store Swap: Old chunks are tombstoned; new chunks are upserted to Pinecone/  |                                                           |
|  |       Milvus in a single transaction, preventing "stale context" in subsequent runs.      |                                                           |
|  +-------------------------------------------------------------------------------------------+                                                           |
|                                                                                                                                                          |
+==========================================================================================================================================================+
                                         ||
                                         || (Returns Exit Code 0 & STDOUT to Sandbox)
                                         v
+==========================================================================================================================================================+
| \\\ TEARDOWN & SYNTHESIS (L2.4)                                                                                                                     /// |
|==========================================================================================================================================================|
| - L2.2 Sandbox is physically destroyed (Firecracker `kill`).                                                                                             |
| - Filtered STDOUT is passed back up the chain to L1 for final User Context generation.                                                                   |
+==========================================================================================================================================================+

+==========================================================================================================================================================+
| CRITICAL UWG INVARIANTS (THE AIRLOCK RULES)                                                                                                              |
|==========================================================================================================================================================|
| 1. NO DIRECT EGRESS: Code executing inside the sandbox cannot reach the internet or external APIs directly. All traffic routes through virtio-vsock.     |
| 2. NO UNSIGNED WRITES: External databases and the L4 State Bus will reject any payload that lacks a valid UWG HMAC-SHA256 signature.                     |
| 3. DIFFS, NOT COMMANDS: The UWG records *what changed* (RFC 6902), not just the command that was executed, ensuring perfect replayability.               |
| 4. ATOMIC VECTOR SYNC: A text file cannot be updated without simultaneously triggering an embedding update. State and Vector memory move as one.         |
+==========================================================================================================================================================+
