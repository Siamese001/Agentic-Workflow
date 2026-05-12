                    vLLM / MODEL CONTEXT WINDOW
                           max_model_len
                          16,384 tokens
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  PROMPT TOKENS            OUTPUT TOKENS                BUFFER        │
│  system + user + docs     max_tokens requested          headroom      │
│                                                                      │
│  ~4,000                   8,192                        ~4,192        │
│                                                                      │
├──────────────────────────┬────────────────────────────┬──────────────┤
│                          │                            │              │
└──────────────────────────┴────────────────────────────┴──────────────┘

PASS RULE:

    prompt_tokens + max_output_tokens + buffer <= max_model_len


BAD:

    ~4,000 prompt + 16,384 output + 0 buffer = ~20,384
    ~20,384 > 16,384
    FAIL


GOOD:

    ~4,000 prompt + 8,192 output + ~4,192 buffer = 16,384
    PASS