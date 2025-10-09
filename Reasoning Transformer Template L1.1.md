╔══════════════════════════════════════════════════════════════════════════════════════╗
║                    🔥 REASONING TRANSFORMER TEMPLATE v1.1                            ║
║                         Multi-Stage CoT + ToT Framework                              ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                      ║
║  STAGE 0: INITIALIZATION & CONTEXT LOADING                                          ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                                      ║
║  ⚙️  Configuration:                                                                  ║
║      • Temperature: [VALUE]                                                          ║
║      • ToT Branches: [VALUE]                                                         ║
║      • CoT Min Paths: [VALUE]                                                        ║
║      • Min ToT Depth: [VALUE]                                                        ║
║      • ToT Ambiguity Threshold: [VALUE]                                              ║
║      • Reflexion Enabled: [YES/NO] at stages [1,2,3,4]                               ║
║      • RAG Type: [Internal/External/Hybrid]                                          ║
║                                                                                      ║
║  🔥 Input Query: "[INSERT QUERY]"                                                    ║
║                                                                                      ║
║  🎪 CONTEXT WINDOW                                                                   ║
║  ┌────────────────────────────────────────────────────────────────────────────────┐ ║
║  │ 🏟️  Capacity: [MAX_TOKENS] | Current: [USED_TOKENS]                            │ ║
║  │                                                                                  │ ║
║  │ CoT PATH ASSIGNMENTS (Baseline - Always Active):                                 │ ║
║  │  🪙 CoT-1: [PERSONA_TYPE_1]     ID:[####] Embedding:[...] 🎟️  Seat 0           │ ║
║  │     Persona: [PERSONA_DESC_1] (e.g., "Strategic Planner")                       │ ║
║  │     Focus: [EXPERTISE_1]                                                         │ ║
║  │                                                                                  │ ║
║  │  🪙 CoT-2: [PERSONA_TYPE_2]     ID:[####] Embedding:[...] 🎟️  Seat 1           │ ║
║  │     Persona: [PERSONA_DESC_2] (e.g., "Risk Analyst")                            │ ║
║  │     Focus: [EXPERTISE_2]                                                         │ ║
║  │                                                                                  │ ║
║  │  🪙 CoT-3: [PERSONA_TYPE_3]     ID:[####] Embedding:[...] 🎟️  Seat 2           │ ║
║  │     Persona: [PERSONA_DESC_3] (e.g., "Technical Expert")                        │ ║
║  │     Focus: [EXPERTISE_3]                                                         │ ║
║  └────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                      ║
║  SPECIALIST ANALYSTS (ToT - 🔴 IDLE until ambiguity spike):                          ║
║  • 🔴 ToT-A (Sp 0-2):   [SPECIALIST_GROUP_1]                                         ║
║       Persona: [SPECIALIST_PERSONA_A] (e.g., "Compliance Officer")                  ║
║       Focus: [SPECIALTY_A]                                                           ║
║  • 🔴 ToT-B (Sp 3-5):   [SPECIALIST_GROUP_2]                                         ║
║       Persona: [SPECIALIST_PERSONA_B] (e.g., "Financial Modeler")                   ║
║       Focus: [SPECIALTY_B]                                                           ║
║  • 🔴 ToT-C (Sp 6-8):   [SPECIALIST_GROUP_3]                                         ║
║       Persona: [SPECIALIST_PERSONA_C] (e.g., "Operations Manager")                  ║
║       Focus: [SPECIALTY_C]                                                           ║
║  • 🔴 ToT-D (Sp 9-11):  [SPECIALIST_GROUP_4]                                         ║
║       Persona: [SPECIALIST_PERSONA_D] (e.g., "Market Researcher")                   ║
║       Focus: [SPECIALTY_D]                                                           ║
║                                                                                      ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                      ║
║  STAGE 1: FOUNDATION CONSENSUS (Slides 1-2)                                         ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║  Mode: CONVERGENCE → All paths align on shared foundation                           ║
║  Principle: ROWS = Depth (slides) | COLUMNS = Breadth (paths)                       ║
║                                                                                      ║
║  ┌────────────────────────────────────────────────────────────────────────────────┐ ║
║  │              │    CoT-1           │    CoT-2           │    CoT-3           │  ║
║  │              │    [APPROACH_1]    │    [APPROACH_2]    │    [APPROACH_3]    │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 👤 Persona   │ [PERSONA_1]        │ [PERSONA_2]        │ [PERSONA_3]        │  ║
║  │ Lens         │ [LENS_DESC_1]      │ [LENS_DESC_2]      │ [LENS_DESC_3]      │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 📊 Slide 1   │                    │                    │                    │  ║
║  │ Initial      │ [UNDERSTANDING_1]  │ [UNDERSTANDING_2]  │ [UNDERSTANDING_3]  │  ║
║  │ Problem      │ [EVIDENCE_1]       │ [EVIDENCE_2]       │ [EVIDENCE_3]       │  ║
║  │ Decomp       │ [ANALYSIS_1]       │ [ANALYSIS_2]       │ [ANALYSIS_3]       │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 🎭 Persona   │ "From [P1]         │ "From [P2]         │ "From [P3]         │  ║
║  │ Contribution │  perspective: ..." │  perspective: ..." │  perspective: ..." │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 📊 Slide 2   │                    │                    │                    │  ║
║  │ Consensus    │ [REFINED_1]        │ [REFINED_2]        │ [REFINED_3]        │  ║
║  │ Foundation   │ [IMPLICATIONS_1]   │ [IMPLICATIONS_2]   │ [IMPLICATIONS_3]   │  ║
║  │              │ [SYNTHESIS_1]      │ [SYNTHESIS_2]      │ [SYNTHESIS_3]      │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 🎭 Persona   │ "[P1] identifies:  │ "[P2] highlights:  │ "[P3] emphasizes:  │  ║
║  │ Insight      │  [KEY_POINT_1]"    │  [KEY_POINT_2]"    │  [KEY_POINT_3]"    │  ║
║  └────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                      ║
║  ✅ CONVERGENCE CHECKPOINT:                                                          ║
║  ┌────────────────────────────────────────────────────────────────────────────────┐ ║
║  │ Metrics:                                                                         │ ║
║  │   • Entropy collapsed: [START_VALUE] → [END_VALUE]                              │ ║
║  │   • Inter-path similarity: [VALUE]% (target: >70%)                              │ ║
║  │   • Agreement score: [VALUE]% (threshold: >75%)                                 │ ║
║  │   • Token overlap: [VALUE]%                                                     │ ║
║  │                                                                                  │ ║
║  │ 🎭 Persona Alignment:                                                            │ ║
║  │   • [PERSONA_1] & [PERSONA_2] & [PERSONA_3] agree on: [SHARED_FOUNDATION]      │ ║
║  │   • Complementary strengths: [HOW_PERSONAS_COMPLEMENT]                          │ ║
║  │                                                                                  │ ║
║  │ Vertical Convergence Visual:                                                     │ ║
║  │         CoT-1          CoT-2          CoT-3                                      │ ║
║  │       (Persona1)     (Persona2)     (Persona3)                                   │ ║
║  │           ↓              ↓              ↓         Slide 1: Divergent            │ ║
║  │           └──────────────┴──────────────┘         Slide 2: Aligned              │ ║
║  │                      ↓                                                           │ ║
║  │               ✅ Foundation Set                                                  │ ║
║  └────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                      ║
║  🧠 REFLEXION (Stage 1): Self-Consistency Check                                      ║
║  ┌────────────────────────────────────────────────────────────────────────────────┐ ║
║  │ Trigger: IF consensus < 75% OR entropy reduction < threshold                     │ ║
║  │                                                                                  │ ║
║  │ Self-Critique Questions:                                                         │ ║
║  │   • Is the foundation truly shared across all paths?                             │ ║
║  │   • Are there hidden disagreements in the "consensus"?                           │ ║
║  │   • Should we re-run Slides 1-2 with different framing?                          │ ║
║  │   • Are personas actually converging or just appearing to?                       │ ║
║  │                                                                                  │ ║
║  │ Action: [PROCEED / RETRY SLIDES 1-2 / ADJUST PERSONAS]                          │ ║
║  │ Reasoning: [WHY_THIS_ACTION]                                                     │ ║
║  └────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                      ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                      ║
║  STAGE 2: DEPTH DEVELOPMENT & CONDITIONAL BRANCHING (Slides 3-N)                    ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║  Mode: EXPLORATION → Develop implications from consensus foundation                 ║
║  Principle: ROWS = Depth (slides) | COLUMNS = Breadth (3 baseline, +4 if ToT)       ║
║                                                                                      ║
║  BASELINE: 3 CoT Columns (Always Active)                                            ║
║  CONDITIONAL: +4 ToT Columns (If ambiguity > threshold at any slide)                ║
║                                                                                      ║
║  ┌────────────────────────────────────────────────────────────────────────────────┐ ║
║  │              │  CoT-1         │  CoT-2         │  CoT-3         │  [ToT if ⚡]  │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 👤 Persona   │ [PERSONA_1]    │ [PERSONA_2]    │ [PERSONA_3]    │              │  ║
║  │ Evolution    │ [HOW_P1_ADAPT] │ [HOW_P2_ADAPT] │ [HOW_P3_ADAPT] │              │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 📊 Slide 3   │                │                │                │              │  ║
║  │              │ [IMPLICATION_1]│ [IMPLICATION_2]│ [IMPLICATION_3]│              │  ║
║  │              │ [EVIDENCE_1]   │ [EVIDENCE_2]   │ [EVIDENCE_3]   │              │  ║
║  │              │ [ANALYSIS_1]   │ [ANALYSIS_2]   │ [ANALYSIS_3]   │              │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 🎭 Persona   │ "[P1] explores:│ "[P2] examines:│ "[P3] develops:│              │  ║
║  │ Deep Dive    │  [DEPTH_1]"    │  [DEPTH_2]"    │  [DEPTH_3]"    │              │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 🔍 Check:    │ Ambiguity: [VALUE] vs [THRESHOLD]                               │  ║
║  │              │ Dynamics: [DIVERGING/STABLE/CONVERGING]                          │  ║
║  │              │ ToT Trigger: [NO ✅ / YES ⚡ → Add 4 columns from next slide]    │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 🧠 Reflexion │ IF quality issues detected at this slide:                        │  ║
║  │ (Optional)   │   • Content quality: [ASSESSMENT]                                │  ║
║  │              │   • Logic gaps: [IDENTIFIED_GAPS]                                │  ║
║  │              │   • Action: [ACCEPT / REVISE / BRANCH_FURTHER]                   │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 📊 Slide 4   │                │                │                │              │  ║
║  │              │ [SYNTHESIS_1]  │ [SYNTHESIS_2]  │ [SYNTHESIS_3]  │              │  ║
║  │              │ [IMPLICATIONS_1│ [IMPLICATIONS_2│ [IMPLICATIONS_3│              │  ║
║  │              │ [REASONING_1]  │ [REASONING_2]  │ [REASONING_3]  │              │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 🎭 Persona   │ "[P1] integrates│ "[P2] validates│ "[P3] expands: │              │  ║
║  │ Synthesis    │  [SYNTH_1]"    │  [SYNTH_2]"    │  [SYNTH_3]"    │              │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 🔍 Check:    │ Ambiguity: [VALUE] vs [THRESHOLD]                               │  ║
║  │              │ Dynamics: [DIVERGING/STABLE/CONVERGING]                          │  ║
║  │              │ ToT Trigger: [NO ✅ / YES ⚡ → Add 4 columns from next slide]    │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 🧠 Reflexion │ IF quality issues detected at this slide:                        │  ║
║  │ (Optional)   │   • Reasoning depth: [ASSESSMENT]                                │  ║
║  │              │   • Evidence strength: [ASSESSMENT]                              │  ║
║  │              │   • Action: [ACCEPT / REVISE / BRANCH_FURTHER]                   │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ [...continues for slides 5-N with same pattern including optional reflexion]     │  ║
║  └────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                      ║
║  ⚡ IF ToT TRIGGERED (Horizontal Expansion):                                         ║
║  ┌────────────────────────────────────────────────────────────────────────────────┐ ║
║  │ 🚨 Fork at Slide [X]: Ambiguity = [VALUE] > [THRESHOLD]                         │ ║
║  │                                                                                  │ ║
║  │ 🟢 Specialists Activated:                                                        │ ║
║  │    ToT-A (Sp0-2):  Persona: [SPECIALIST_PERSONA_A] - [DESC_A]                   │ ║
║  │    ToT-B (Sp3-5):  Persona: [SPECIALIST_PERSONA_B] - [DESC_B]                   │ ║
║  │    ToT-C (Sp6-8):  Persona: [SPECIALIST_PERSONA_C] - [DESC_C]                   │ ║
║  │    ToT-D (Sp9-11): Persona: [SPECIALIST_PERSONA_D] - [DESC_D]                   │ ║
║  │                                                                                  │ ║
║  │ From Slide X+1 onward, table expands to 7 columns:                              │ ║
║  │              │ CoT-1 │ CoT-2 │ CoT-3 │ ToT-A │ ToT-B │ ToT-C │ ToT-D │         │ ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 👤 Persona   │ [P1]  │ [P2]  │ [P3]  │ [SP-A]│ [SP-B]│ [SP-C]│ [SP-D]│         │ ║
║  │ Active       │       │       │       │       │       │       │       │         │ ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 📊 Slide X+1 │ [C1]  │ [C2]  │ [C3]  │ [S-A] │ [S-B] │ [S-C] │ [S-D] │         │ ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 🎭 Persona   │"[P1]: │"[P2]: │"[P3]: │"[SP-A]│"[SP-B]│"[SP-C]│"[SP-D]│         │ ║
║  │ Contribution │[CONT1]│[CONT2]│[CONT3]│brings │brings │brings │brings │         │ ║
║  │              │       │       │       │[NEW-A]│[NEW-B]│[NEW-C]│[NEW-D]│         │ ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 🔍 Check:    │ Ambiguity: [VALUE] | Dynamics: [STATE] | ToT: [STATUS]          │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 🧠 Reflexion │ Check specialist contribution quality:                           │  ║
║  │ (Optional)   │   • Are specialists adding value or noise?                       │  ║
║  │              │   • Should any specialist paths be pruned?                       │  ║
║  │              │   • Action: [CONTINUE_ALL / PRUNE_PATHS / ADJUST]                │  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 📊 Slide X+2 │ [C1]  │ [C2]  │ [C3]  │ [S-A] │ [S-B] │ [S-C] │ [S-D] │         │ ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 🎭 Persona   │"[P1]: │"[P2]: │"[P3]: │"[SP-A]│"[SP-B]│"[SP-C]│"[SP-D]│         │ ║
║  │ Deep Spec    │[CONT1]│[CONT2]│[CONT3]│refines│refines│refines│refines│         │ ║
║  │              │       │       │       │[REF-A]│[REF-B]│[REF-C]│[REF-D]│         │ ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ [...all remaining slides use 7 columns with checks and optional reflexion]      │ ║
║  └────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                      ║
║  📈 Per-Slide Monitoring:                                                            ║
║     • Entropy, drift, compliance, head diversity, token uniformity                   ║
║     • Inter-path similarity, dominant path, ambiguity threshold                      ║
║     • Persona coherence: Each persona maintains consistent voice/focus               ║
║     • Reflexion triggers: Quality thresholds per slide                               ║
║                                                                                      ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                      ║
║  STAGE 3: PATH SELECTION & CONVERGENCE (Reflexion)                                  ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║  Mode: SYNTHESIS → Select best slide content per position                           ║
║  Principle: ROWS = Slide positions | COLUMNS = Candidate paths                      ║
║                                                                                      ║
║  Input: [3 CoT] OR [3 CoT + 4 ToT = 7] candidates per slide (depends on Stage 2)    ║
║                                                                                      ║
║  🗳️  VOTING MATRIX:                                                                  ║
║  ┌────────────────────────────────────────────────────────────────────────────────┐ ║
║  │              │  CoT-1  │  CoT-2  │  CoT-3  │  ToT-A* │  ToT-B* │  ToT-C* │ToT-D*│  ║
║  │              │ [P1]    │ [P2]    │ [P3]    │ [SP-A]* │ [SP-B]* │ [SP-C]* │[SP-D]│  ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 📊 Slide 1   │  [SCR]  │  [SCR]  │  [SCR]  │   n/a   │   n/a   │   n/a   │ n/a │  ║
║  │ Winner: [PATH_ID] with [VOTES] → Content locked                                 │ ║
║  │ 🎭 Why: "[PERSONA_X]'s [SPECIFIC_STRENGTH] was most compelling"                 │ ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 📊 Slide 2   │  [SCR]  │  [SCR]  │  [SCR]  │   n/a   │   n/a   │   n/a   │ n/a │  ║
║  │ Winner: [PATH_ID] with [VOTES] → Content locked                                 │ ║
║  │ 🎭 Why: "[PERSONA_Y]'s [SPECIFIC_STRENGTH] provided best foundation"            │ ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ 📊 Slide 3   │  [SCR]  │  [SCR]  │  [SCR]  │  [SCR]* │  [SCR]* │  [SCR]* │[SCR]*│  ║
║  │ Winner: [PATH_ID] with [VOTES] → Content locked                                 │ ║
║  │ 🎭 Why: "[PERSONA_Z]'s [SPECIFIC_STRENGTH] addressed ambiguity best"            │ ║
║  ├────────────────────────────────────────────────────────────────────────────────┤ ║
║  │ [...continues for all N slides with persona reasoning per winner]                │  ║
║  └────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                      ║
║  🏆 ASSEMBLED PATH (Hybrid):                                                         ║
║  ┌────────────────────────────────────────────────────────────────────────────────┐ ║
║  │ Slide 1: From [PATH] ([PERSONA]) → [REASONING]                                  │ ║
║  │ Slide 2: From [PATH] ([PERSONA]) → [REASONING]                                  │ ║
║  │ Slide 3: From [PATH] ([PERSONA]) → [REASONING]                                  │ ║
║  │ [etc. for all N slides]                                                          │ ║
║  │                                                                                  │ ║
║  │ 🎭 Persona Impact Summary:                                                       │ ║
║  │   • [PERSONA_1] contributed: [COUNT] slides → [IMPACT_DESC_1]                   │ ║
║  │   • [PERSONA_2] contributed: [COUNT] slides → [IMPACT_DESC_2]                   │ ║
║  │   • [PERSONA_3] contributed: [COUNT] slides → [IMPACT_DESC_3]                   │ ║
║  │   • [SP_PERSONA_A] contributed: [COUNT] slides → [IMPACT_DESC_A] (if ToT)       │ ║
║  │   • [SP_PERSONA_B] contributed: [COUNT] slides → [IMPACT_DESC_B] (if ToT)       │ ║
║  │   • [SP_PERSONA_C] contributed: [COUNT] slides → [IMPACT_DESC_C] (if ToT)       │ ║
║  │   • [SP_PERSONA_D] contributed: [COUNT] slides → [IMPACT_DESC_D] (if ToT)       │ ║
║  └────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                      ║
║  🧠 REFLEXION (Stage 3): Assembly Quality Check                                      ║
║  ┌────────────────────────────────────────────────────────────────────────────────┐ ║
║  │ Assembled Output: "[FULL_ANSWER]"                                               │ ║
║  │                                                                                  │ ║
║  │ Self-Critique Questions:                                                         │ ║
║  │   • Query fully answered?                                                        │ ║
║  │   • Logical gaps between slides from different paths?                            │ ║
║  │   • Overlooked superior reasoning from runner-ups?                               │ ║
║  │   • Hybrid coherent or disjointed?                                               │ ║
║  │   • Persona transitions smooth?                                                  │ ║
║  │   • Should we reconsider any slide selections?                                   │ ║
║  │                                                                                  │ ║
║  │ 🎭 Persona Coherence Check:                                                      │ ║
║  │   • Do persona transitions make narrative sense? [ANALYSIS]                      │ ║
║  │   • Was each persona used to their strength? [ANALYSIS]                          │ ║
║  │   • Are there jarring voice changes? [ANALYSIS]                                  │ ║
║  │                                                                                  │ ║
║  │ Re-evaluation Result: [ANALYSIS]                                                 │ ║
║  │ Adjustments Made: [NONE / SPECIFIC CHANGES WITH RATIONALE]                       │ ║
║  │                                                                                  │ ║
║  │ IF MAJOR ISSUES: Can trigger re-vote on specific slides or entire assembly       │ ║
║  └────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                      ║
║  📉 ENTROPY VISUALIZATION:                                                           ║
║  ┌────────────────────────────────────────────────────────────────────────────────┐ ║
║  │ Stage 1:  ▇▇▇▇ → ▇▇        (CONVERGING - 3 personas align vertically)          │ ║
║  │ Stage 2:  ▇▇▇ → ▇▇ → ▇▇    (EXPLORING - 3 or 7 personas develop depth)         │ ║
║  │ Stage 3:  ▇ → ▇             (LOCKING - Collapse to 1 hybrid multi-persona path) │ ║
║  └────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                      ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                      ║
║  STAGE 4: DELIVERY VALIDATION & LOCK-IN                                             ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║                                                                                      ║
║  ✅ QA VALIDATION:                                                                   ║
║  ┌────────────────────────────────────────────────────────────────────────────────┐ ║
║  │ ✅ Confidence > [THRESHOLD]?    ([YES/NO], [VALUE])                             │ ║
║  │ ✅ Logit Gap > [THRESHOLD]?     ([YES/NO], [VALUE])                             │ ║
║  │ ✅ Vote Entropy Low?             ([YES/NO], [VALUE])                             │ ║
║  │ ✅ Ambiguity Resolved?           ([YES/NO], [START]→[END])                       │ ║
║  │ ✅ Slide Coherence?              (No contradictions)                             │ ║
║  │ ✅ Hybrid Consistency?           (Smooth transitions)                            │ ║
║  │ ✅ Persona Consistency?          (Each voice maintained identity)                │ ║
║  └────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                      ║
║  🧠 REFLEXION (Stage 4): Final Delivery Check                                        ║
║  ┌────────────────────────────────────────────────────────────────────────────────┐ ║
║  │ Pre-Delivery Validation:                                                         │ ║
║  │   • Does this actually answer the user's query? [YES/NO]                         │ ║
║  │   • Are there any remaining quality issues? [ASSESSMENT]                         │ ║
║  │   • Is the confidence justified by the evidence? [ANALYSIS]                      │ ║
║  │   • Would a human expert approve this answer? [PREDICTION]                       │ ║
║  │                                                                                  │ ║
║  │ Final Action: [DELIVER / REVISE_AND_RECHECK / ESCALATE_UNCERTAINTY]             │ ║
║  │ Reasoning: [WHY_THIS_ACTION]                                                     │ ║
║  └────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                      ║
║  🎯 FINAL OUTPUT:                                                                    ║
║  ┌────────────────────────────────────────────────────────────────────────────────┐ ║
║  │ 🔒 Lock-In: Logit Gap = [VALUE]                                                 │ ║
║  │                                                                                  │ ║
║  │ 🏆 Final Answer: "[OUTPUT]"                                                      │ ║
║  │                                                                                  │ ║
║  │ 📊 Metrics:                                                                      │ ║
║  │    • Confidence: [VALUE]                                                         │ ║
║  │    • Logit Gap: [VALUE]                                                          │ ║
║  │    • Consensus: [PERCENTAGE]                                                     │ ║
║  │                                                                                  │ ║
║  │ 🗺️  Path Composition:                                                            │ ║
║  │    • CoT-1 ([PERSONA_1]): [SLIDE_LIST]                                           │ ║
║  │    • CoT-2 ([PERSONA_2]): [SLIDE_LIST]                                           │ ║
║  │    • CoT-3 ([PERSONA_3]): [SLIDE_LIST]                                           │ ║
║  │    • ToT-A ([SP_PERSONA_A]): [SLIDE_LIST or "N/A"]                               │ ║
║  │    • ToT-B ([SP_PERSONA_B]): [SLIDE_LIST or "N/A"]                               │ ║
║  │    • ToT-C ([SP_PERSONA_C]): [SLIDE_LIST or "N/A"]                               │ ║
║  │    • ToT-D ([SP_PERSONA_D]): [SLIDE_LIST or "N/A"]                               │ ║
║  │                                                                                  │ ║
║  │ 🎭 PERSONA IMPACT ANALYSIS:                                                      │ ║
║  │    ┌────────────────────────────────────────────────────────────────────────┐  │ ║
║  │    │ Dominant Persona: [PERSONA_NAME] ([X]% of final answer)                │  │ ║
║  │    │   Why dominant: [REASON_FOR_DOMINANCE]                                  │  │ ║
║  │    │                                                                          │  │ ║
║  │    │ Supporting Personas:                                                     │  │ ║
║  │    │   • [PERSONA_2]: [Y]% → [CONTRIBUTION_SUMMARY]                          │  │ ║
║  │    │   • [PERSONA_3]: [Z]% → [CONTRIBUTION_SUMMARY]                          │  │ ║
║  │    │   • [SP_PERSONA_*]: [W]% → [CONTRIBUTION_SUMMARY] (if ToT activated)   │  │ ║
║  │    │                                                                          │  │ ║
║  │    │ Persona Synergies:                                                       │  │ ║
║  │    │   • [PERSONA_X] + [PERSONA_Y]: [HOW_THEY_COMPLEMENTED]                  │  │ ║
║  │    │   • [PERSONA_Y] + [PERSONA_Z]: [HOW_THEY_COMPLEMENTED]                  │  │ ║
║  │    └────────────────────────────────────────────────────────────────────────┘  │ ║
║  │                                                                                  │ ║
║  │ 🗝️  KEY DECISION SUMMARY:                                                        │ ║
║  │    ┌────────────────────────────────────────────────────────────────────────┐  │ ║
║  │    │ Stage 1 (Foundation):                                                   │  │ ║
║  │    │   [PERSONA_1], [PERSONA_2], [PERSONA_3] converged on:                   │  │ ║
║  │    │   [FOUNDATION_SUMMARY]                                                   │  │ ║
║  │    │   Reflexion: [PASSED / REVISED / N/A]                                   │  │ ║
║  │    │                                                                          │  │ ║
║  │    │ Stage 2 (Exploration):                                                   │  │ ║
║  │    │   3 personas explored [DEPTH_SUMMARY]                                   │  │ ║
║  │    │   [ToT triggered at Slide X: Added [SP_PERSONAS] / Not needed]          │  │ ║
║  │    │   Reflexion checks: [COUNT] performed, [OUTCOME_SUMMARY]                │  │ ║
║  │    │                                                                          │  │ ║
║  │    │ Stage 3 (Selection):                                                     │  │ ║
║  │    │   Voting favored [DOMINANT_PERSONA]'s approach because:                 │  │ ║
║  │    │   [RATIONALE_FOR_SELECTIONS]                                             │  │ ║
║  │    │   Reflexion: [ASSEMBLY_QUALITY_CHECK_RESULT]                            │  │ ║
║  │    │                                                                          │  │ ║
║  │    │ Stage 4 (Validation):                                                    │  │ ║
║  │    │   Final reflexion: [DELIVERY_CHECK_RESULT]                              │  │ ║
║  │    │   All QA checks: [PASSED / ISSUES_IDENTIFIED_AND_RESOLVED]              │  │ ║
║  │    │                                                                          │  │ ║
║  │    │ Why This Answer Won:                                                     │  │ ║
║  │    │   [NARRATIVE_EXPLAINING_REASONING_JOURNEY_AND_PERSONA_CONTRIBUTIONS]    │  │ ║
║  │    └────────────────────────────────────────────────────────────────────────┘  │ ║
║  └────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝