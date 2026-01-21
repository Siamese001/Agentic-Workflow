┌─────────────────────────────┐
│   L1.PY (The Caller)        │
│                             │
│  "I need a strategy plan."  │
│  "Use 'Reflexion' logic."   │
└──────────────┬──────────────┘
               │
   (1) CALL    │  gateway.call_model(
               │      prompt_id="l1_strategy",
               │      inputs={"objective": "Cloud Migration"},
               │      strategy="reflexion"  <-- THE TRIGGER
               │  )
               ▼
┌───────────────────────────────────────────────────────────────┐
│                 LLM_GATEWAY.PY (The Brain)                    │
│                                                               │
│  Step A: FETCH STATIC TEMPLATE                                │
│     │                                                         │
│     │ (2) GET "l1_strategy"                                   │
│     │                                                         │
│     │    ┌──────────────────────────────────────────────┐     │
│     └────▶  REGISTRY.PY (The Golden Source)             │     │
│          │                                              │     │
│          │  [PROMPT: l1_strategy]                       │     │
│          │  "You are a VP of Strategy."                 │     │
│          │  "Objective: {objective}"                    │     │
│          │  "Output strictly formatted JSON."           │     │
│          └───────────────────────┬──────────────────────┘     │
│                                  │                            │
│                                  │ (3) RETURN TEMPLATE        │
│                                  │                            │
│  Step B: RENDER CONTEXT          ▼                            │
│     • Replaces {objective} with "Cloud Migration"             │
│                                                               │
│  Step C: APPLY DYNAMIC WRAPPER (The Injection)                │
│     • Checks `strategy="reflexion"`                           │
│     • Pulls logic from `_inject_reasoning()`                  │
│     • Appends the cognitive scaffolding                       │
│                                                               │
└──────────────────────────────┬────────────────────────────────┘
                               │
                               │ (4) SEND FINAL COMPOSITE
                               ▼
┌───────────────────────────────────────────────────────────────┐
│                  FINAL PROMPT (Sent to LLM)                   │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ [STATIC PART - FROM REGISTRY]                           │  │
│  │ "You are a VP of Strategy."                             │  │
│  │ "Objective: Cloud Migration"                            │  │
│  │ "Output strictly formatted JSON."                       │  │
│  └─────────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ [DYNAMIC PART - FROM GATEWAY LOGIC]                     │  │
│  │                                                         │  │
│  │ >>> INJECTION START <<<                                 │  │
│  │ "STOP. Do not answer yet."                              │  │
│  │ "1. DRAFT your response."                               │  │
│  │ "2. CRITIQUE the draft for missing risks."              │  │
│  │ "3. REVISE and output only the final JSON."             │  │
│  │ >>> INJECTION END <<<                                   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
