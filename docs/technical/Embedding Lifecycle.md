================================================================================================================================================================
                                        EXECUTE_SSOT EMBEDDING LIFECYCLE — CONSOLIDATED VIEW
================================================================================================================================================================


RAW SIGNAL
[L2]
+---------------------------------------------------+
| 💥 SYSTEM INCIDENT OCCURS                         |
|---------------------------------------------------|
| Failure signals collected:                        |
| * stack traces (ImportError etc.)                 |
| * invariant violations                            |
| * territory violations                            |
| * test failures                                   |
| * repository context / file path                  |
+---------------------------------------------------+



ENCODER  (METADATA EXTRACTION — NO EMBEDDINGS YET)
[L2]
+---------------------------------------------------+
| 🧹 FAILURE NORMALIZATION                          |
|---------------------------------------------------|
| * parse stack trace                               |
| * extract error signature                         |
| * collect execution + repository context          |
| * normalize failure text                          |
|                                                   |
| METADATA CAPTURED                                 |
| * territory / invariant identifiers               |
| * repository path / files involved                |
+---------------------------------------------------+



VECTOR  (EMBEDDING GENERATED HERE)
[L1]
+---------------------------------------------------+
| 🧠 EMBEDDING MODEL (bge-m3)                        |
|---------------------------------------------------|
| INPUT                                             |
| normalized failure text                           |
|                                                   |
| Example                                           |
| "ImportError yaml config loader"                  |
|                                                   |
| OUTPUT                                            |
| failure_vector = [v1 ... vd]                      |
|                                                   |
| IMPORTANT                                         |
| The embedding model rarely changes.               |
|                                                   |
| The embedding model generates vectors but         |
| does NOT store them.                              |
|                                                   |
| System knowledge does NOT grow by retraining      |
| the embedding model.                              |
|                                                   |
| System knowledge grows because new vectors are    |
| inserted into the vector index during the         |
| learning loop.                                    |
+---------------------------------------------------+



MEMORY  (VECTOR INDEX STORAGE)
[L1]
+---------------------------------------------------+
| 📚 INCIDENT MEMORY — VECTOR INDEX                 |
|---------------------------------------------------|
| Vector storage format                             |
|                                                   |
| vector_id → embedding_vector                      |
|                                                   |
| Example                                           |
|                                                   |
| id_1 → e1                                         |
| id_2 → e2                                         |
| id_3 → e3                                         |
| ...                                               |
| id_N → eN                                         |
|                                                   |
| These vectors are organized internally using      |
| Approximate Nearest Neighbor structures such as:  |
|                                                   |
| * HNSW graphs                                     |
| * IVF clusters                                    |
| * PQ partitions                                   |
|                                                   |
| CRITICAL SYSTEM PROPERTY                          |
|                                                   |
| The embedding model stays fixed.                  |
|                                                   |
| The vector index accumulates vectors.             |
|                                                   |
| As new incidents occur, new vectors are inserted  |
| into this index, expanding the searchable memory  |
| of the system.                                    |
+---------------------------------------------------+



VECTOR SEARCH
[L1]
+---------------------------------------------------+
| 🔎 SIMILARITY SEARCH                              |
|---------------------------------------------------|
| query_vector = embed(normalized_failure_text)     |
|                                                   |
| similarity(query_vector, e_i)                     |
|                                                   |
| ANN navigation retrieves                          |
|                                                   |
| top_k nearest vectors                             |
|                                                   |
| Example results                                   |
|                                                   |
| Incident A → yaml dependency issue                |
| Incident B → configuration loader error           |
| Incident C → path resolution failure              |
|                                                   |
| If no close match → novel failure cluster         |
+---------------------------------------------------+



ROUTING
[L0]
+---------------------------------------------------+
| 🧭 HEALING DECISION ENGINE                        |
|---------------------------------------------------|
| Uses retrieved metadata                           |
|                                                   |
| * violation type                                  |
| * healer used previously                          |
| * repair actions                                  |
| * historical success / failure                    |
| * cluster statistics                              |
|                                                   |
| Determines root cause + healer                    |
|                                                   |
| (embeddings are advisory signals only)            |
+---------------------------------------------------+



ORCHESTRATION
[L3]
+---------------------------------------------------+
| 🗺 PATH SELECTION ENGINE                          |
|---------------------------------------------------|
| Routes execution to appropriate repair path       |
|                                                   |
| Examples                                          |
| * Path A                                          |
| * Path B                                          |
| * Path C                                          |
| * Path D                                          |
+---------------------------------------------------+



EXECUTION + HEALING
[L2]
+---------------------------------------------------+
| 🛠 EXECUTION + HEALING AGENTS                     |
|---------------------------------------------------|
| * DependencyRepairAgent                           |
| * ArchitectureGovernorAgent                       |
| * GravityRepairAgent                              |
| * TestRepairAgent                                 |
|                                                   |
| System mutation performed and validated           |
+---------------------------------------------------+



LEARNING LOOP  (VECTOR INSERTION)
[L4 STORAGE | L6 TELEMETRY]
+---------------------------------------------------+
| 🗂 HEALING EVENT STORED                           |
|---------------------------------------------------|
| When a healing event completes:                   |
|                                                   |
| failure_vector_new = embed(normalized_failure)    |
|                                                   |
| Insert vector into index:                         |
|                                                   |
| id_new → failure_vector_new                       |
|                                                   |
| Vector index becomes:                             |
|                                                   |
| {e1, e2, e3, ... eN, e_new}                       |
|                                                   |
| This expands the system's searchable incident     |
| memory.                                           |
|                                                   |
| The embedding model remains unchanged.            |
|                                                   |
| The vector index grows over time.                 |
+---------------------------------------------------+



SYSTEM LEARNING
[CORE CAPABILITY]
+---------------------------------------------------+
| 🧠 META-LEARNING SYSTEM                           |
|---------------------------------------------------|
| Analyzes vectors stored in the vector index       |
| together with incident metadata.                  |
|                                                   |
| Identifies:                                       |
| * recurring failure signatures                    |
| * effective healers per failure type              |
| * regression patterns                             |
| * routing improvements                            |
|                                                   |
| The meta-learning system consumes vectors from    |
| memory but does not retrain the embedding model.  |
+---------------------------------------------------+


================================================================================================================================================================
KEY PRINCIPLE

Embedding model stays fixed.

Vector index accumulates vectors and becomes the system's growing memory.
================================================================================================================================================================
