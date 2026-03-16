===========================================================================================================================================================
STAGE PIPELINE        LAYER (AGENTIC CORE)                 AGENTIC WORKFLOW SYSTEM                             LIBRARY SYSTEM (ANALOGY)
===========================================================================================================================================================

RAW SIGNAL            [L2]                                 🎯 [ AGENT REQUEST INITIATED ]                      📚 [ PATRON ARRIVES WITH QUERY ]
                                                           (Task requiring agent execution)                    (Complex research problem)
                                                                 │                                                   │
                                                                 ▼                                                   ▼
                                                     ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         📋 Request Context Collected      │       │         📝 Reference Query Initiated      │
                                                     │                                           │       │                                           │
                                                     │ * user intent / task description          │       │ * vague keywords, topic hints             │
                                                     │ * execution context / constraints         │       │ * patron research history                 │
                                                     │ * capability requirements                 │       │ * academic level / constraints            │
                                                     │ * historical success patterns             │       │                                           │
                                                     │ * repo context / file paths               │       │                                           │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘


ENCODER               [L0]                           ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         🧹 Request Normalization          │       │         🗃️ Subject Cataloging Analysis    │
                                                     │                                           │       │                                           │
                                                     │ * parse task requirements                 │       │ * keyword extraction                      │
                                                     │ * extract capability needs                │       │ * semantic mapping                        │
                                                     │ * collect execution context               │       │                                           │
                                                     │ * normalize request signal                │       │ -> produces query signal                  │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘


VECTOR                [L1]                           ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         🧠 Embedding Model (openai)       │       │         🧠 Classification Encoding Model  │
                                                     │         text-embedding-3-large            │       │         (Library of Congress / DDC)       │
                                                     │                                           │       │                                           │
                                                     │ INPUT                                     │       │ INPUT                                     │
                                                     │ "generate RFP response for client X"      │       │ "medieval trade routes silk road"         │
                                                     │ + capability requirements                 │       │                                           │
                                                     │ + execution constraints                   │       │                                           │
                                                     │                                           │       │                                           │
                                                     │ OUTPUT                                    │       │ OUTPUT                                    │
                                                     │ request_vector = [v1..vN]                 │       │ query_vector = [v1..vN]                   │
                                                     │                                           │       │                                           │
                                                     │ NOTE:                                     │       │ NOTE:                                     │
                                                     │ embedding model rarely changes            │       │ classification model rarely changes       │
                                                     │ knowledge grows via execution memory      │       │ knowledge grows via catalog expansion     │
                                                     │ (bge-m3 used for healing context only)    │       │                                           │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘



MEMORY                [L1]                           ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         📚 Search Similar Historical Requests       │         📚 Search Past Reference Queries  │
                                                     │                                           │       │                                           │
                                                     │ VECTOR SEARCH                             │       │ VECTOR SEARCH                             │
                                                     │ request_vector                            │       │ query_vector                              │
                                                     │                                           │       │                                           │
                                                     │ RETURNS TOP MATCHES                       │       │ RETURNS TOP MATCHES                       │
                                                     │                                           │       │                                           │
                                                     │ Request A → RFP generation                │       │ Query A → trade guild ledgers             │
                                                     │ Request B → resume optimization           │       │ Query B → silk road maps                  │
                                                     │ Request C → campaign planning             │       │ Query C → maritime logs                   │
                                                     │                                           │       │                                           │
                                                     │ IF NO CLOSE MATCH                         │       │ IF NO CLOSE MATCH                         │
                                                     │ flag "novel request pattern"              │       │ flag "novel research request"             │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘


ROUTING               [L0]                           ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         🧭 Capability Routing Engine      │       │         🧭 Reference Desk Triage          │
                                                     │                                           │       │                                           │
                                                     │ USES RETRIEVED METADATA                   │       │ USES RETRIEVED METADATA                   │
                                                     │                                           │       │                                           │
                                                     │ * capability requirements                 │       │ * topic classification                    │
                                                     │ * agent used previously                   │       │ * collections used previously             │
                                                     │ * execution strategy applied              │       │ * librarian success rate                  │
                                                     │ * success / failure history               │       │ * patron outcomes                         │
                                                     │ * cluster statistics                      │       │ * cluster statistics                      │
                                                     │                                           │       │                                           │
                                                     │ Determines capability + agent             │       │ Determines core subject + specialist      │
                                                     │ (embeddings are advisory only)            │       │                                           │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘


SPECIALIST            [L3/L_APP]                     ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         🤖 Specialized Agent Dispatched   │       │         🧑‍🏫 Specialist Librarian Assigned│
                                                     │                                           │       │                                           │
                                                     │ * RfpOrchestrator                         │       │ * Archivist                               │
                                                     │ * CampaignPlannerAgent                    │       │ * Map/GIS Specialist                      │
                                                     │ * ResearchOrchestrator                    │       │ * Periodicals Expert                      │
                                                     │ * LocationHealerAgent                     │       │                                           │
                                                     │                                           │       │                                           │
                                                     │ -> governed execution performed           │       │ -> resources applied                      │
                                                     │                                           │       │                                           │
                                                     │ * generate proposal 📄                    │       │ * rare manuscripts 📜                     │
                                                     │ * optimize campaign 📊                    │       │ * microfilm archives 🎞️                     │
                                                     │ * conduct research 🔍                     │       │ * digital databases 💻                      │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘


LEARNING LOOP         [L4 + L6 FEEDS]                ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         🗂️ Execution Event Stored in Memory │       │         🗂️ Reference Transaction Logged   │
                                                     │                                           │       │                                           │
                                                     │ VECTOR STORED                             │       │ VECTOR STORED                             │
                                                     │ request_vector                            │       │ query_vector                              │
                                                     │                                           │       │                                           │
                                                     │ METADATA STORED                           │       │ METADATA STORED                           │
                                                     │ * request summary                         │       │ * query text                              │
                                                     │ * capability requirements                 │       │ * classified topic                        │
                                                     │ * agent dispatched                        │       │ * librarian assigned                      │
                                                     │ * execution strategy                      │       │ * resources provided                      │
                                                     │ * success / failure outcome               │       │ * success / failure outcome               │
                                                     │ * execution context / files touched       │       │ * patron type                             │
                                                     │ * replay_key / trace_id                   │       │ * transaction id                          │
                                                     │ * confidence score                        │       │                                           │
                                                     │ * novelty flag / cluster id               │       │                                           │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘



SYSTEM LEARNING       [CORE CAPABILITY]              ┌───────────────────────────────────────────┐       ┌───────────────────────────────────────────┐
                                                     │         🧠 Meta-Learning System           │       │         🔬 Collection Development / Admin │
                                                     │                                           │       │                                           │
                                                     │ Uses vectors + metadata                   │       │ Uses vectors + metadata                   │
                                                     │ * cluster execution patterns              │       │ * cluster research patterns               │
                                                     │ * best agent per capability cluster       │       │ * best resource per topic                 │
                                                     │ * success rate per agent cluster          │       │ * best librarian per topic                │
                                                     │ * detect recurring request patterns       │       │ * detect recurring research trends        │
                                                     │ * improve routing decisions               │       │ * improve reference protocols             │
                                                     │                                           │       │                                           │
                                                     │ ⚠️ ARCHITECTURE NOTE                      │       │ ⚠️ ARCHITECTURE NOTE                      │
                                                     │ Meta-learning reads signals from          │       │ Admin uses transaction records            │
                                                     │ observability (L6) + state (L4)           │       │ but does not operate inside               │
                                                     │ but must NOT be implemented               │       │ the reference desk workflow itself        │
                                                     │ as an L6 observability component          │       │                                           │
                                                     │ (common mistake in agentic systems)       │       │                                           │
                                                     │                                           │       │                                           │
                                                     │ OPTIONAL (rare)                           │       │ OPTIONAL (rare)                           │
                                                     │ new embedding model                       │       │ new classification system                 │
                                                     │ requires re-indexing vectors              │       │ requires re-cataloging collection         │
                                                     └───────────────────────────────────────────┘       └───────────────────────────────────────────┘

===========================================================================================================================================================