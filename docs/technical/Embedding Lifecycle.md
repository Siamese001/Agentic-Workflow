===========================================================================================================================================================
STAGE PIPELINE                          HOSPITAL SYSTEM (ANALOGY)                            EXECUTE_SSOT SYSTEM
===========================================================================================================================================================

RAW SIGNAL
[L2]                                    🏥 [ PATIENT ARRIVES ]                                 💥 [ SYSTEM INCIDENT OCCURS ]
                                        (Individual patient case)                             (Specific runtime failure)
                                                |                                                     |
                                                v                                                     v
                                    +-------------------------------------------+       +-------------------------------------------+
                                    |           🤒 Symptoms Reported            |       |        🚨 Failure Signals Collected      |
                                    |                                           |       |                                           |
                                    | * cough, chest pain, fever                |       | * stack traces (ImportError etc.)        |
                                    | * patient history                         |       | * invariant violations                   |
                                    | * age / risk factors                      |       | * territory violations                   |
                                    |                                           |       | * test failures                          |
                                    |                                           |       | * repo context / file path               |
                                    +-------------------------------------------+       +-------------------------------------------+


ENCODER  (METADATA EXTRACTED HERE; EMBEDDINGS NOT GENERATED HERE)
[L2]                                    +-------------------------------------------+       +-------------------------------------------+
                                    |        🩻 Medical Imaging Device            |       |        🧹 Failure Normalization           |
                                    |                                           |       |                                           |
                                    | * X-ray                                   |       | * parse stack trace                      |
                                    | * MRI                                     |       | * extract error signature                |
                                    |                                           |       | * collect repo + execution context       |
                                    | -> produces scan signal                   |       | * normalize signal text                  |
                                    |                                           |       |                                           |
                                    | METADATA CAPTURED                          |       | METADATA CAPTURED                          |
                                    | * patient history                          |       | * territory / invariant ids               |
                                    | * age / risk factors                       |       | * repo context / file path                |
                                    +-------------------------------------------+       +-------------------------------------------+


VECTOR  (EMBEDDINGS GENERATED HERE; INPUT IS NORMALIZED TEXT, NOT METADATA)
[L1]                                    +-------------------------------------------+       +-------------------------------------------+
                                    |        🧠 Diagnostic Encoding Model        |       |        🧠 Embedding Model (bge-m3)        |
                                    |        (Radiology Interpretation)         |       |                                           |
                                    |                                           |       | INPUT                                     |
                                    | INPUT                                     |       | "ImportError yaml config loader"         |
                                    | "cough fever chest pain infection"        |       |                                           |
                                    |                                           |       | (territory / invariant ids are metadata   |
                                    |                                           |       |  stored separately, not embedded)         |
                                    |                                           |       |                                           |
                                    | OUTPUT                                    |       | OUTPUT                                    |
                                    | symptom_vector = [v1..vN]                 |       | failure_vector = [v1..vN]                |
                                    |                                           |       |                                           |
                                    | NOTE:                                     |       | NOTE:                                     |
                                    | imaging model rarely changes              |       | embedding model rarely changes            |
                                    | knowledge grows via case database         |       | knowledge grows via incident memory       |
                                    +-------------------------------------------+       +-------------------------------------------+


MEMORY  (EMBEDDINGS USED HERE)
[L1]                                    +-------------------------------------------+       +-------------------------------------------+
                                    |       📚 Search Medical Case History       |       |    📚 Search Similar Historical Incidents |
                                    |                                           |       |                                           |
                                    | VECTOR SEARCH                             |       | VECTOR SEARCH                             |
                                    | symptom_vector                            |       | failure_vector                            |
                                    |                                           |       |                                           |
                                    | RETURNS TOP MATCHES                       |       | RETURNS TOP MATCHES                       |
                                    |                                           |       |                                           |
                                    | Case A → pneumonia                        |       | Incident A → yaml dependency              |
                                    | Case B → bronchitis                       |       | Incident B → path issue                   |
                                    | Case C → infection                        |       | Incident C → config failure               |
                                    |                                           |       |                                           |
                                    | IF NO CLOSE MATCH                         |       | IF NO CLOSE MATCH                         |
                                    | flag "novel presentation"                 |       | flag "novel failure cluster"              |
                                    +-------------------------------------------+       +-------------------------------------------+


ROUTING  (EMBEDDINGS USED DOWNSTREAM VIA MEMORY OUTPUT)
[L0]                                    +-------------------------------------------+       +-------------------------------------------+
                                    |    🧑‍⚕️ Hospital Triage / Diagnostician     |       |        🧭 Healing Decision Engine          |
                                    |                                           |       |                                           |
                                    | USES RETRIEVED METADATA                   |       | USES RETRIEVED METADATA                   |
                                    |                                           |       |                                           |
                                    | * disease label                           |       | * violation type(s)                       |
                                    | * treatments used                         |       | * healer used previously                  |
                                    | * doctor success rate                     |       | * patch applied previously                |
                                    | * patient outcomes                        |       | * success / failure history               |
                                    | * cluster statistics                      |       | * cluster statistics                      |
                                    |                                           |       |                                           |
                                    | Determines disease + specialist           |       | Determines root cause + healer            |
                                    |                                           |       | (embeddings are advisory only)            |
                                    +-------------------------------------------+       +-------------------------------------------+


ORCHESTRATION  (EMBEDDINGS USED DOWNSTREAM VIA ROUTING OUTPUT)
[L3]                                    +-------------------------------------------+       +-------------------------------------------+
                                    |     🧑‍⚕️ Care Path Selection               |       |        🗺️ Path Selection Engine           |
                                    |                                           |       |                                           |
                                    | Routes to the right                        |       | Routes to the right                        |
                                    | clinical pathway based on                  |       | execution pathway based on                 |
                                    | triage decision                            |       | routing decision                           |
                                    |                                           |       |                                           |
                                    | Examples:                                  |       | Examples:                                  |
                                    | * ER → imaging → admit                     |       | * Path A / Path B / Path C / Path D        |
                                    | * outpatient → follow-up                   |       |                                           |
                                    +-------------------------------------------+       +-------------------------------------------+


PRE-COMMIT
[L2 • L2.1]                             +-------------------------------------------+       +-------------------------------------------+
                                    |      📝 Pre-Procedure Setup               |       |        📝 Pre-Commit                       |
                                    |                                           |       |                                           |
                                    | * prepare orders / scope                  |       | * plan repair scope                        |
                                    | * confirm required resources              |       | * stage changes                             |
                                    |                                           |       | * identify files/targets                    |
                                    +-------------------------------------------+       +-------------------------------------------+


VALIDATION
[L2 • L2.2]                             +-------------------------------------------+       +-------------------------------------------+
                                    |      ✅ Safety Checks Before Treatment     |       |        ✅ Validation                        |
                                    |                                           |       |                                           |
                                    | * allergies / contraindications           |       | * invariant violations check               |
                                    | * confirm diagnosis criteria              |       | * territory violations check               |
                                    | * confirm procedure is permitted          |       | * policy checks (fail-closed)              |
                                    +-------------------------------------------+       +-------------------------------------------+


EXECUTION
[L2 • L2.3]                             +-------------------------------------------+       +-------------------------------------------+
                                    |      🏥 Treatment Performed               |       |        🛠️ Execution                         |
                                    |                                           |       |                                           |
                                    | * antibiotics 💊                          |       | * apply change / run command               |
                                    | * cast 🦴                                 |       | * run tests / build                         |
                                    | * surgery 🏥                              |       | * perform system mutation                   |
                                    +-------------------------------------------+       +-------------------------------------------+


HEALING
[L2 • L2.4]                             +-------------------------------------------+       +-------------------------------------------+
                                    |      🩹 Complication Response             |       |        🤖 Healing                           |
                                    |                                           |       |                                           |
                                    | * adjust treatment                        |       | * DependencyRepairAgent                    |
                                    | * escalate to specialist                   |       | * ArchitectureGovernorAgent                |
                                    | * retry with new protocol                 |       | * GravityRepairAgent                       |
                                    |                                           |       | * TestRepairAgent                          |
                                    +-------------------------------------------+       +-------------------------------------------+


LEARNING LOOP  (EMBEDDINGS STORED HERE FOR FUTURE MEMORY SEARCH; METADATA STORED WITH THE VECTOR)
[L4 storage | L6 telemetry feeds]        +-------------------------------------------+       +-------------------------------------------+
                                    |      🗂️ Case Stored in Hospital DB        |       |      🗂️ Healing Event Stored in State     |
                                    |                                           |       |                                           |
                                    | VECTOR STORED                             |       | VECTOR STORED                             |
                                    | symptom_vector                            |       | failure_vector                            |
                                    |                                           |       |                                           |
                                    | METADATA STORED                           |       | METADATA STORED                           |
                                    | * symptoms text                           |       | * failure summary                         |
                                    | * diagnosis                               |       | * violation types                         |
                                    | * doctor assigned                         |       | * healer used                             |
                                    | * treatment                               |       | * repair action                           |
                                    | * success / failure outcome               |       | * success / failure outcome               |
                                    | * demographics                            |       | * repo location / files touched           |
                                    | * episode id                              |       | * replay_key / routing_digest             |
                                    |                                           |       | * confidence score                        |
                                    |                                           |       | * novelty flag / cluster id               |
                                    +-------------------------------------------+       +-------------------------------------------+


SYSTEM LEARNING  (EMBEDDINGS CONSUMED FROM L4 STORAGE + L6 TELEMETRY)
[CORE CAPABILITY • consumes L4 memory + L6 telemetry]
                                    +-------------------------------------------+       +-------------------------------------------+
                                    |        🔬 Medical Research               |       |        🧠 Meta-Learning System             |
                                    |                                           |       |                                           |
                                    | Uses vectors + metadata                   |       | Uses vectors + metadata                   |
                                    | * cluster disease patterns                |       | * cluster failure patterns                |
                                    | * best treatment per disease              |       | * best healer per failure cluster         |
                                    | * best doctor per disease                 |       | * success rate per agent cluster          |
                                    | * detect recurring conditions             |       | * detect recurring regressions            |
                                    | * improve triage protocols                |       | * improve routing decisions               |
                                    |                                           |       |                                           |
                                    | ⚠️ ARCHITECTURE NOTE                      |       | ⚠️ ARCHITECTURE NOTE                      |
                                    | Research uses hospital records            |       | Meta-learning reads signals from          |
                                    | but does not operate inside               |       | observability (L6) + state (L4)           |
                                    | the clinical workflow itself              |       | but must NOT be implemented               |
                                    |                                           |       | as an L6 observability component          |
                                    |                                           |       | (common mistake in agentic systems)      |
                                    +-------------------------------------------+       +-------------------------------------------+

===========================================================================================================================================================
