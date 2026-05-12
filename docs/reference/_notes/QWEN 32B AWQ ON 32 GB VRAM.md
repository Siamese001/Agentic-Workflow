                         QWEN 32B AWQ ON 32 GB VRAM
                   tradeoff: model size vs quantization vs context

┌─────────────────────────────────────────────────────────────────────────────┐
│                           32 GB GPU VRAM BUDGET                             │
└─────────────────────────────────────────────────────────────────────────────┘

   MODEL PARAMETERS              QUANTIZATION                  CONTEXT WINDOW
   "How big/smart?"              "How compressed?"             "How long?"
   Qwen 32B                      AWQ 4-bit-ish                 max_model_len
        │                              │                              │
        ▼                              ▼                              ▼

┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
│ More parameters       │      │ More quantization     │      │ Longer context        │
│ = better capability   │      │ = smaller weights     │      │ = more KV cache       │
│                      │      │                      │      │                      │
│ But uses more VRAM    │      │ Frees VRAM for KV     │      │ Uses VRAM per token   │
└──────────┬───────────┘      └──────────┬───────────┘      └──────────┬───────────┘
           │                             │                             │
           └─────────────────────────────┼─────────────────────────────┘
                                         ▼

                         SAME 32 GB VRAM MUST HOLD ALL OF THIS

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  Quantized model weights     vLLM/CUDA overhead      KV cache for context    │
│  Qwen 32B AWQ                runtime workspace       prompt + output tokens  │
│                                                                             │
├───────────────────────────┬──────────────────────┬──────────────────────────┤
│ ~big fixed cost            │ fixed/variable cost   │ grows with max_model_len │
└───────────────────────────┴──────────────────────┴──────────────────────────┘


THE TRADEOFF

┌────────────────────┬────────────────────┬───────────────────────────────────┐
│ Setting             │ What improves       │ What gets squeezed                │
├────────────────────┼────────────────────┼───────────────────────────────────┤
│ Bigger model         │ reasoning quality   │ available VRAM for context        │
│ More quantization    │ model fits in VRAM  │ some precision/quality            │
│ Longer context       │ larger prompts      │ KV cache, batching, stability     │
│ Bigger output cap    │ longer answer       │ remaining prompt/context space    │
│ More concurrency     │ more parallel users │ KV cache per request              │
└────────────────────┴────────────────────┴───────────────────────────────────┘


FOR YOUR CASE

┌─────────────────────────────────────────────────────────────────────────────┐
│ Qwen 32B AWQ + 32 GB VRAM                                                    │
├──────────────────────────────┬──────────────────────────────────────────────┤
│ Model fits                   │ because AWQ compresses weights               │
│ 16K context works             │ because KV cache still has enough room       │
│ 32K context may be tight      │ because KV cache roughly doubles             │
│ 64K+ context likely bad       │ because KV cache dominates remaining VRAM    │
└──────────────────────────────┴──────────────────────────────────────────────┘


REQUEST RULE

    prompt_tokens + output_tokens + buffer <= max_model_len


EXAMPLE WITH 16,384 max_model_len

┌─────────────────────────────────────────────────────────────────────────────┐
│                         16,384 TOKEN CONTEXT WINDOW                         │
├───────────────────────┬────────────────────────┬────────────────────────────┤
│ prompt                │ generated output        │ buffer / safety headroom    │
│ repo/docs/instruction │ answer tokens            │ template/variance/overhead  │
│ ~4,000                │ 8,192                    │ ~4,192                      │
└───────────────────────┴────────────────────────┴────────────────────────────┘

GOOD:

    4,000 + 8,192 + 4,192 = 16,384

BAD:

    4,000 + 16,384 + 0 = 20,384 > 16,384