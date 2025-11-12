.
                              +-------------------------------------------------------------------------+
                              | 📚 "THE LIBRARIAN" (Offline Nightly Agent)                              |
                              |   Class: `IntelligenceLibrarian`                                        |
                              |   File: `intelligence_service_LIC.py`                                   |
                              |                                                                         |
                              |   1. Runs deep research RAG on target companies/executives.             |
                              |   2. Analyzes content using `GeminiLLMClient`.                          |
                              |   3. Embeds findings (via `google.generativeai.embed_content`).         |
                              |   4. Writes vectors to persistent "memory".                             |
                              +----------------------------------+--------------------------------------+
                                                                 |
                                                                 v
                                             [ 🧠 The Memory (ChromaDB) ]
                                            Class: `VectorMemoryStore`
                                            File: `memory_LIC.py`
                                (Persistent Vector Store of High-Signal Company Intel)
                                                                 ^
                                                                 | (READS FIRST)
+----------------------------------------------------------------+----------------------------------------------------------------+
| 🧑‍💻 "THE CLIENT" (User)                                            | 📐 "THE ARCHITECT" (Static JSON Configs - "The What")           |
|                                                                |                                                                |
|   • Runs `workflow_LIC_v13.py`                                 |   • `agent_specs_LIC.json` (HOP order, agent params) |
|   • Provides `mission_input_LIC.json`                          |   • `prompts_LIC.json` (All LLM scripts)     |
|   • Provides `target_brief.pdf` (e.g., Citi/DoorDash)          |   • `validator_rules_LIC.json` (Inspector rules) |
|                                                                |   • `master_resume.json` (Static Asset Intel)  |
|                                                                |   • `sender_knowledge_base.json` (Static Asset Intel) |
+------------------+---------------------------------------------+----------------------------------+-----------------------------+
                   |                                                                                 | (READS)
                   v                                                                                 v
+------------------+---------------------------------------------------------------------------------+-----------------------------+
| 👷 "THE FOREMAN" (Class: `HOPOrchestrator` in `workflow_LIC_v13.py`)                           |
|                                                                                                                              |
|   • Manages all HOPs via `hop_execution_order` (from `agent_specs_LIC.json`)                      |
|   • Manages state via `state_manager_LIC.py` (Reads/writes to `state/` dir)                       |
|   • Loads all JSON configs ("The Architect" files).                                                 |
|   • Manages the "Slow Factual Loop" (HOP-7 -> HOP-2) and "Fast Creative Loop" (HOP-7 -> HOP-5).   |
+--------------------------------------------------+-----------------------------------------------------------------------------+
                                                   |
                                                   v
+------------------+-------------------------------+-----------------------------------------------------------------------------+
| 🧐 **HOP-1: "THE PROFILE ANALYST"** (Class: `HOP1_ProfileAnalysisAgent` in `hop_agents_LIC.py`) |
|                                                                                                                              |
|   1. **Read:** Reads `mission_input_LIC.json` (passed by Foreman).                                  |
|   2. **Read Rules:** Reads `profile_analysis_agent` rules from `agent_specs_LIC.json`.            |
|   3. **Classify:** Determines `Archetype` (e.g., C_LEVEL) and `Confidence`.                         |
|                                                                                                                              |
|   ➡️ **Output:** `state/1_profile_analysis.json`                                                   |
+--------------------------------------------------+-----------------------------------------------------------------------------+
                                                   |
                                                   v
+------------------+-------------------------------+-----------------------------------------------------------------------------+
| 🎯 **HOP-2: "THE RESEARCH AGENT"** (Class: `HOP2_ResearchAgent` in `workflow_LIC_v13.py`)        |
|                                                                                                                              |
|   1. **Read:** Reads `state/1_profile_analysis.json`.                                               |
|   2. **Memory Query (Tool Call):** Queries `[🧠 The Memory]` *first* for high-signal intel. |
|   3. **Cache Critique:** Analyzes memory results for gaps (e.g., stale news, missing brief).    |
|   4. **Fallback RAG (Tool Call):** *Only if gaps exist*, calls `GoogleSearchClient` to fill them. |
|                                                                                                                              |
|   ➡️ **Output:** `state/2_research_context.json` (Merged intel: Memory + Fallback RAG)     |
+--------------------------------------------------+-----------------------------------------------------------------------------+
                                                   |
                                                   v
+------------------+-------------------------------+-----------------------------------------------------------------------------+
| 🔎 **HOP-3: "THE SENDER ARCHIVIST"** (Class: `HOP3_SenderGroundingAgent` in `hop_agents_LIC.py`)|
|                                                                                                                              |
|   1. **Read:** Reads `master_resume.json` and `sender_knowledge_base.json`.                     |
|   2. **Extract:** Transforms sender capabilities (products, metrics, team) into structured data. |
|                                                                                                                              |
|   ➡️ **Output:** `state/3_sender_grounding.json`                                                 |
+--------------------------------------------------+-----------------------------------------------------------------------------+
                                                   |
                                                   v
+------------------+-------------------------------+-----------------------------------------------------------------------------+
| 🗺️ **HOP-4: "THE ROUTER & SCAFFOLDER"** (Class: `HOP4_RoutingAgent` in `hop_agents_LIC.py`)|
|                                                                                                                              |
|   1. **Read:** Reads `state/1_profile_analysis.json` and `mission_input_LIC.json`.                |
|   2. **Read Rules:** Reads `routing_agent` rules from `agent_specs_LIC.json`.                   |
|   3. **Decide:** Determines `Route` (e.g., INMAIL) and `Constraints` (e.g., word count).         |
|                                                                                                                              |
|   ➡️ **Output:** `state/4_routing_decision.json` (This file *is* the scaffold)               |
+--------------------------------------------------+-----------------------------------------------------------------------------+
                                                   |
                                                   v
+------------------+-------------------------------+-----------------------------------------------------------------------------+
| ✍️ **HOP-5: "THE WRITER"** (Class: `HOP5_GenerationAgent` in `workflow_LIC_v13.py`)             |
|                                                                                                                              |
|   1. **Read Intel:** Reads `state/2_research_context.json`, `state/3_sender_grounding.json`, `state/4_routing_decision.json`. |
|   2. **Read Prompts:** Reads `strategic_alignment_prompt_template` from `prompts_LIC.json`.     |
|   3. **Generate (LLM Call):** Generates **N drafts** (e.g., 3 for C_LEVEL, 1 for others).      |
|                                                                                                                              |
|   ➡️ **Output:** `state/5_generated_drafts.json` (Contains `List[str]` of all N drafts)          |
+--------------------------------------------------+-----------------------------------------------------------------------------+
                                                   |
                                                   v
+------------------+-------------------------------+-----------------------------------------------------------------------------+
| 🧐 **HOP-6: "THE VALIDATOR"** (Class: `HOP6_ValidationAgent` in `workflow_LIC_v13.py`)          |
|                                                                                                                              |
|   1. **Read:** Reads `state/5_generated_drafts.json` & `state/2_research_context.json`.         |
|   2. **Read Rules:** Reads all rules from `validator_rules_LIC.json`.                           |
|   3. **Evaluate (Tool Call / Fast Loop):** Uses `CodeInterpreterTool` to run "scoring competition" on N drafts. |
|   4. **Inspect:** Selects the *winning draft* and validates it against all JSON rules.           |
|                                                                                                                              |
|   ➡️ **Output:** `state/6_validation_report.json` (Pass/Fail, list of errors)                |
+--------------------------------------------------+-----------------------------------------------------------------------------+
                                                   |
                                                   v
+------------------+-------------------------------+-----------------------------------------------------------------------------+
| 🚦 **HOP-7: "THE GATEKEEPER"** (Class: `HOP7_GateDecisionAgent` in `hop_agents_LIC.py`)      |
|                                                                                                                              |
|   1. **Read:** Reads `state/6_validation_report.json`.                                        |
|   2. **Decide:** |
|      • `if FactualFailure:` -> **[🔥 SLOW LOOP]** (Tells Foreman to re-run HOP-2)               |
|      • `if CreativeFailure:` -> **[🔥 FAST LOOP]** (Tells Foreman to re-run HOP-5)              |
|      • `if Pass:` -> **[✅ PROCEED]** |
|                                                                                               |
|   ➡️ **Output:** `state/7_gate_decision.json` (The decision: PASS, RETRY_HOP5, or FACTUAL_FAILURE) |
+--------------------------------------------------+-----------------------------------------------------------------------------+
   |    ^                                              |
   |    | (Proceeds to HOP-8)                          |
   |    +----------------------------------------------+ (Triggers Slow Factual Loop back to HOP-2)
   |                                                   |
   +---------------------------------------------------+ (Triggers Fast Creative Loop back to HOP-5)
                                                   |
                                                   v
+------------------+-------------------------------+-----------------------------------------------------------------------------+
| 🧾 **HOP-8: "THE FINAL ARCHIVIST"** (Class: `HOP8_QAReportAgent` in `workflow_LIC_v13.py`)    |
|                                                                                                                              |
|   1. **Read:** Reads *all* files from `state/` directory (e.g., `state/1_...`, `state/2_...`, `state/6_...`, `state/7_...`). |
|   2. **Read Prompt:** Reads `qa_report_prompt` from `prompts_LIC.json`.                       |
|   3. **Generate (LLM Call):** Synthesizes all state files into a final summary report.      |
|                                                                                                                              |
|   ➡️ **Output:** Writes final `QA_Report_[mission_id].md` to `outputs/` directory              |
+--------------------------------------------------+-----------------------------------------------------------------------------+
                                                   |
                                                   v
                                             [ 🏁 END ]