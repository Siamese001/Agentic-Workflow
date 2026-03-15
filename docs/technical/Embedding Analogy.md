===========================================================================================================================================================
STAGE PIPELINE        LAYER (AGENTIC CORE)                 LIBRARY SYSTEM (ANALOGY)                            AGENTIC WORKFLOW SYSTEM
===========================================================================================================================================================

RAW SIGNAL            [L2]                                 📚 [ PATRON ARRIVES WITH QUERY ]                    🎯 [ AGENT REQUEST INITIATED ]
                                                           (Complex research problem)                          (Task requiring agent execution)
                                                                 │                                                   │
                                                                 ▼                                                   ▼
                                                     ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         📝 Reference Query Initiated      │       │         � Request Context Collected      │
                                                     │                                           │       │                                           │
                                                     │ * vague keywords, topic hints             │       │ * user intent / task description          │
                                                     │ * patron research history                 │       │ * execution context / constraints         │
                                                     │ * academic level / constraints            │       │ * capability requirements                 │
                                                     │                                           │       │ * historical success patterns             │
                                                     │                                           │       │ * repo context / file paths               │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘


ENCODER               [L2]                           ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         🗃️ Subject Cataloging Analysis    │       │         🧹 Request Normalization          │
                                                     │                                           │       │                                           │
                                                     │ * keyword extraction                      │       │ * parse task requirements                 │
                                                     │ * semantic mapping                        │       │ * extract capability needs                │
                                                     │                                           │       │ * collect execution context               │
                                                     │ -> produces query signal                  │       │ * normalize request signal                │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘


VECTOR                [L1]                           ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         🧠 Classification Encoding Model  │       │         🧠 Embedding Model (bge-m3)       │
                                                     │         (Library of Congress / DDC)       │       │                                           │
                                                     │                                           │       │ INPUT                                     │
                                                     │ INPUT                                     │       │ "generate RFP response for client X"      │
                                                     │ "medieval trade routes silk road"         │       │ + capability requirements                 │
                                                     │                                           │       │ + execution constraints                   │
                                                     │                                           │       │                                           │
                                                     │ OUTPUT                                    │       │ OUTPUT                                    │
                                                     │ query_vector = [v1..vN]                   │       │ request_vector = [v1..vN]                 │
                                                     │                                           │       │                                           │
                                                     │ NOTE:                                     │       │ NOTE:                                     │
                                                     │ classification model rarely changes       │       │ embedding model rarely changes            │
                                                     │ knowledge grows via catalog expansion     │       │ knowledge grows via execution memory      │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘


MEMORY                [L1]                           ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         📚 Search Past Reference Queries  │       │         📚 Search Similar Historical Requests
                                                     │                                           │       │                                           │
                                                     │ VECTOR SEARCH                             │       │ VECTOR SEARCH                             │
                                                     │ query_vector                              │       │ request_vector                            │
                                                     │                                           │       │                                           │
                                                     │ RETURNS TOP MATCHES                       │       │ RETURNS TOP MATCHES                       │
                                                     │                                           │       │                                           │
                                                     │ Query A → trade guild ledgers             │       │ Request A → RFP generation                │
                                                     │ Query B → silk road maps                  │       │ Request B → resume optimization           │
                                                     │ Query C → maritime logs                   │       │ Request C → campaign planning             │
                                                     │                                           │       │                                           │
                                                     │ IF NO CLOSE MATCH                         │       │ IF NO CLOSE MATCH                         │
                                                     │ flag "novel research request"             │       │ flag "novel request pattern"              │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘


ROUTING               [L0]                           ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         🧭 Reference Desk Triage          │       │         🧭 Capability Routing Engine      │
                                                     │                                           │       │                                           │
                                                     │ USES RETRIEVED METADATA                   │       │ USES RETRIEVED METADATA                   │
                                                     │                                           │       │                                           │
                                                     │ * topic classification                    │       │ * capability requirements                 │
                                                     │ * collections used previously             │       │ * agent used previously                   │
                                                     │ * librarian success rate                  │       │ * execution strategy applied              │
                                                     │ * patron outcomes                         │       │ * success / failure history               │
                                                     │ * cluster statistics                      │       │ * cluster statistics                      │
                                                     │                                           │       │                                           │
                                                     │ Determines core subject + specialist      │       │ Determines capability + agent             │
                                                     │                                           │       │ (embeddings are advisory only)            │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘


SPECIALIST            [L2]                           ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         🧑‍🏫 Specialist Librarian Assigned│       │         🤖 Specialized Agent Dispatched   │
                                                     │                                           │       │                                           │
                                                     │ * Archivist                               │       │ * RfpOrchestrator                         │
                                                     │ * Map/GIS Specialist                      │       │ * CampaignPlannerAgent                    │
                                                     │ * Periodicals Expert                      │       │ * ResearchOrchestrator                    │
                                                     │                                           │       │ * LocationHealerAgent                     │
                                                     │                                           │       │                                           │
                                                     │ -> resources applied                      │       │ -> governed execution performed           │
                                                     │                                           │       │                                           │
                                                     │ * rare manuscripts 📜                     │       │ * generate proposal 📄                    │
                                                     │ * microfilm archives 🎞️                     │       │ * optimize campaign 📊                    │
                                                     │ * digital databases 💻                      │       │ * conduct research �                     │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘


LEARNING LOOP         [L4 + L6 FEEDS]                ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         🗂️ Reference Transaction Logged   │       │         🗂️ Execution Event Stored in Memory │
                                                     │                                           │       │                                           │
                                                     │ VECTOR STORED                             │       │ VECTOR STORED                             │
                                                     │ query_vector                              │       │ request_vector                            │
                                                     │                                           │       │                                           │
                                                     │ METADATA STORED                           │       │ METADATA STORED                           │
                                                     │ * query text                              │       │ * request summary                         │
                                                     │ * classified topic                        │       │ * capability requirements                 │
                                                     │ * librarian assigned                      │       │ * agent dispatched                        │
                                                     │ * resources provided                      │       │ * execution strategy                      │
                                                     │ * success / failure outcome               │       │ * success / failure outcome               │
                                                     │ * patron type                             │       │ * execution context / files touched       │
                                                     │ * transaction id                          │       │ * replay_key / trace_id                   │
                                                     │                                           │       │ * confidence score                        │
                                                     │                                           │       │ * novelty flag / cluster id               │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘


SYSTEM LEARNING       [CORE CAPABILITY]              ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         🔬 Collection Development / Admin │       │         🧠 Meta-Learning System           │
                                                     │                                           │       │                                           │
                                                     │ Uses vectors + metadata                   │       │ Uses vectors + metadata                   │
                                                     │ * cluster research patterns               │       │ * cluster execution patterns              │
                                                     │ * best resource per topic                 │       │ * best agent per capability cluster       │
                                                     │ * best librarian per topic                │       │ * success rate per agent cluster          │
                                                     │ * detect recurring research trends        │       │ * detect recurring request patterns       │
                                                     │ * improve reference protocols             │       │ * improve routing decisions               │
                                                     │                                           │       │                                           │
                                                     │ ⚠️ ARCHITECTURE NOTE                      │       │ ⚠️ ARCHITECTURE NOTE                      │
                                                     │ Admin uses transaction records            │       │ Meta-learning reads signals from          │
                                                     │ but does not operate inside               │       │ observability (L6) + state (L4)           │
                                                     │ the reference desk workflow itself        │       │ but must NOT be implemented               │
                                                     │                                           │       │ as an L6 observability component          │
                                                     │                                           │       │ (common mistake in agentic systems)       │
                                                     │                                           │       │                                           │
                                                     │ OPTIONAL (rare)                           │       │ OPTIONAL (rare)                           │
                                                     │ new classification system                 │       │ new embedding model                       │
                                                     │ requires re-cataloging collection         │       │ requires re-indexing vectors              │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘

===========================================================================================================================================================
