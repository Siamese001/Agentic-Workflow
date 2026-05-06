=======================================================================================
             TRANSFORMER SELF-ATTENTION: TOKEN CONTEXTUALIZATION PIPELINE
=======================================================================================

[1] EMBEDDING LOOKUP
Token: "bank" ──▶ [ EMBEDDING MATRIX ] ──▶  x_i  (Baseline Vector, ℝ^{d_model})
                                            e.g., [ 0.12, -0.88, 0.45, ... ]

───────────────────────────────────────────────────────────────────────────────────────
[2] LINEAR PROJECTIONS (The 3 Roles)
The baseline vector x_i is multiplied by learned weight matrices to project it into 
three distinct representational spaces.

  [ x_i ] × [ W_Q ] = [ q_i ]  QUERY  "What context am I looking for right now?"
  [ x_i ] × [ W_K ] = [ k_i ]  KEY    "What structural/semantic clue do I advertise?"
  [ x_i ] × [ W_V ] = [ v_i ]  VALUE  "What core meaning can I contribute?"

───────────────────────────────────────────────────────────────────────────────────────
[3] ATTENTION SCOREBOARD (The Matching Phase)
The Query (q_i) seeks matches by taking the dot product with all visible Keys (k_j).
Scores are scaled down by √d_k for stability, then pushed through a Softmax.

                RAW MATCHING ( q_i · k_j )              SOFTMAX( score / √d_k )
              ┌────────────────────────────┐           ┌───────────────────────┐
              │ q_bank · k_she   =  1.2    │           │ weight_she   =  0.05  │
  [ q_bank ] ─┼ q_bank · k_sat   =  1.9    │ ──Scale ─▶│ weight_sat   =  0.10  │
              │ q_bank · k_by    =  0.3    │   & Norm  │ weight_by    =  0.02  │
              │ q_bank · k_river =  4.0    │           │ weight_river =  0.83  │ ◀ (High!)
              └────────────────────────────┘           └───────────────────────┘

───────────────────────────────────────────────────────────────────────────────────────
[4] WEIGHTED VALUE MIX (The Context Update)
Multiply each token's Value (v_j) by its earned Attention Weight, then sum them together.

   z_i = ∑ ( weight_i,j × v_j )
       = (0.05 × v_she) + (0.10 × v_sat) + (0.02 × v_by) + (0.83 × v_river)

   [ z_i ] ──▶ The aggregated "Context Update" for "bank" (heavy on "river" features).

───────────────────────────────────────────────────────────────────────────────────────
[5] RESIDUAL CONNECTION & FEED-FORWARD (Integration)

       [ x_i ] (Original Identity)
          +
       [ z_i ] (New Context Learned from Neighbors)
          │
          ▼
  ┌───────────────┐
  │  LAYER NORM   │ ──▶ Centers and scales the vector, stabilizing learning dynamics.
  └───────────────┘
          │
          ▼
  ┌───────────────┐     FFN(x) = max(0, x·W_1 + b_1)·W_2 + b_2
  │ FEED-FORWARD  │ ──▶ Privately processes and sharpens the newly contextualized
  └───────────────┘     meaning across different dimensions.
          │
          ▼
[6] OUTPUT STATE
     [ x'_i ] ──▶ Updated Vector: "bank" is now represented mathematically as a
                  "river edge" rather than a "financial institution".

=======================================================================================
MATHEMATICAL SUMMARY:
Attention(Q, K, V) = softmax( (Q · K^T) / √d_k ) · V
Layer_Output(x_i)  = FFN( LayerNorm( x_i + Attention_Output(x_i) ) )
=======================================================================================