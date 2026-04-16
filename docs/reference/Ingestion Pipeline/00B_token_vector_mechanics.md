==============================================================================================================================
[00B] 🧠 TOKEN-TO-VECTOR MECHANICS
     Scope: Deep drill-down into embedding generation internals.
     Purpose: Show exactly where Hugging Face weights, tokenization, and pooling happen.
==============================================================================================================================

      [ ASYNC INITIALIZATION PATH ]                                      [ LIVE EXECUTION PATH ]
      ─────────────────────────────                                      ───────────────────────
                                                                                [ INPUT ]
                                                                           Enriched chunk text
                                                                                    │
                                                                                    │ [ selected text ]
                                                                                    ▼
┌─────────────────────────────────────────────────────┐        ┌────────────────────────────────────────────────────────────┐
│ B1. TOKENIZER LOAD                                  │        │ B2. TOKENIZATION                                           │
│ - Load model-compatible tokenizer                   │        │ - text -> tokens -> token ids                              │
│ - Same model family as embedding encoder            │───[ tokenizer obj ]──► apply truncation / padding / special tokens  │
│ - Output contract: token ids + attention mask       │        │ - Result: discrete model inputs                            │
└─────────────────────────────────────────────────────┘        └────────────────────────┬───────────────────────────────────┘
                                                                                        │
┌─────────────────────────────────────────────────────┐                                 │ [ token ids & mask ]
│ B3. MODEL CHECKPOINT RESOLUTION                     │                                 │
│ - Example: BAAI/bge-m3                              │                                 │
│ - Source: Hugging Face Hub or local cache           │                                 │
│ - Cache path ex: ~/.cache/huggingface/              │                                 │
│ - Result: pretrained checkpoint files located       │                                 │
└──────────────────────────┬──────────────────────────┘                                 │
                           │                                                            │
                           │ [ checkpoint files ]                                       │
                           ▼                                                            │
┌─────────────────────────────────────────────────────┐                                 │
│ B4. WEIGHT LOAD / RAM ALLOCATION                    │                                 │
│ - Trained neural network weights imported into RAM  │                                 │
│ - Model is now executable for forward pass          │───[ loaded weights ]────────────┤
│ - This is the concrete step of "weights coming in"  │                                 │
└─────────────────────────────────────────────────────┘                                 │
                                                                                        ▼
                                                               ┌────────────────────────────────────────────────────────────┐
                                                               │ B5. FORWARD PASS                                           │
                                                               │ - token ids + attn mask + weights -> context hidden states │
                                                               │ - Every token now has a learned contextual representation  │
                                                               └────────────────────────┬───────────────────────────────────┘
                                                                                        │
                                                                                        │ [ hidden states ]
                                                                                        ▼
                                                               ┌────────────────────────────────────────────────────────────┐
                                                               │ B6. POOLING / PROJECTION                                   │
                                                               │ - Mean pool / CLS pool / model-specific projection         │
                                                               │ - Token hidden states -> one chunk-level semantic vector   │
                                                               │ - Output names: fact_vec / chunk_vec / raw_text_vector     │
                                                               └────────────────────────┬───────────────────────────────────┘
                                                                                        │
                                                                                        │ [ chunk vector ]
                                                                                        ▼
                                                               ┌────────────────────────────────────────────────────────────┐
                                                               │ B7. NORMALIZATION                                          │
                                                               │ - L2 normalize vector for cosine-friendly search           │
                                                               │ - Produces stable retrieval-ready embedding                │
                                                               └────────────────────────┬───────────────────────────────────┘
                                                                                        │
                                                                                        │ [ normalized vec ]
                                                                                        ▼
                                                               ┌────────────────────────────────────────────────────────────┐
                                                               │ B8. OUTPUT CONTRACT                                        │
                                                               │ - chunk_id, vector, embedding schema / model id            │
                                                               │ - text hash, metadata pointer                              │
                                                               └────────────────────────────────────────────────────────────┘

==============================================================================================================================
TOKEN-LEVEL VIEW
==============================================================================================================================

text
  │
  │ [ raw string ]
  ▼
[t1][t2][t3][t4][t5]...[tn]
  │   │   │   │   │       │
  └───┴───┴───┴───┴───────┴───────► encoder with pretrained weights
                                                │
                                                │ [ encoded tokens ]
                                                ▼
                                    [h1][h2][h3][h4][h5]...[hn]
                                                │
                                                └──────────────► pooling / projection
                                                                        │
                                                                        │ [ aggregated ]
                                                                        ▼
                                                               [ one chunk vector ]

==============================================================================================================================
BOTTOM LINE
- Hugging Face does not usually hand you one vector directly.
- It provides the tokenizer + checkpoint weights.
- The model uses those weights during the forward pass.
- Pooling converts token-level hidden states into one chunk embedding.
- The vector DB usually stores this chunk embedding, not each token vector.
==============================================================================================================================