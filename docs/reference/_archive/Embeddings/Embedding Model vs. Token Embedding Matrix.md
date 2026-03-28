================================================================================================================
TOKEN EMBEDDING MATRIX (COMPONENT INSIDE TRANSFORMER) | EMBEDDING MODEL + VECTOR DATABASE PIPELINE
================================================================================================================

Purpose                                              | Purpose
-----------------------------------------------------|-------------------------------------------------
Convert tokens to initial vectors                    | Generate semantic vectors and search them

Location                                             | Location
-----------------------------------------------------|-------------------------------------------------
Inside the transformer model                         | BGE = embedding model
                                                     | FAISS = vector database

Pipeline                                             | Pipeline
-----------------------------------------------------|-------------------------------------------------

text                                                 | text
 ↓                                                   | ↓
tokenizer                                            | tokenizer
 ↓                                                   | ↓
tokens                                               | tokens
 ↓                                                   | ↓
+-----------------------------------------------+    | +-----------------------------------------------+
| TRANSFORMER MODEL                             |    | | EMBEDDING MODEL (BGE-M3)                      |
|                                               |    | |                                               |
| internal component highlighted:               |    | | TRANSFORMER MODEL                             |
|                                               |    | |                                               |
|  +-----------------------------------------+  |    | |  token embedding matrix                       |
|  | TOKEN EMBEDDING MATRIX                  |  |    | |  ↓                                            |
|  |                                         |  |    | |  transformer attention layers                 |
|  | rows = tokens in vocabulary             |  |    | |  ↓                                            |
|  | columns = hidden dimensions             |  |    | |  contextual token representations             |
|  |                                         |  |    | |  ↓                                            |
|  | token_id → vector                       |  |    | |  pooling / projection                         |
|  |                                         |  |    | +-----------------------------------------------+
|  | example:                                |  |    | ↓
|  | "yaml" → [0.21, -0.33, ...]             |  |    | +-----------------------------------------------+
|  +-----------------------------------------+  |    | | FINAL EMBEDDING VECTOR                        |
|                                               |    | |                                               |
| (other transformer layers run after this)     |    | | sentence_vector = [v1, v2 ... vN]             |
+-----------------------------------------------+    | |                                               |
 ↓                                                   | | example:                                      |
token vectors                                        | | [0.12, -0.87, 0.41 ...]                       |
 ↓                                                   | +-----------------------------------------------+
transformer layers                                   | ↓
 ↓                                                   | +-----------------------------------------------+
contextualized token representations                 | | VECTOR DATABASE (FAISS)                       |
                                                     | |                                               |
Matrix Structure                                     | | Stores vectors + metadata                     |
-----------------------------------------------------| |                                               |
vocab_size × hidden_dimension                        | | vector = [0.12, -0.87, ...]                   |
example:                                             | | metadata:                                     |
100000 × 1024                                        | |   healer_used                                 |
                                                     | |   success                                     |
                                                     | |   repo_path                                   |
                                                     | |                                               |
                                                     | | Performs similarity search                    |
                                                     | | nearest_neighbor(vector)                      |
                                                     | +-----------------------------------------------+

Stored in Vector DB?                                  | Stored in Vector DB?
-----------------------------------------------------|-------------------------------------------------
No                                                   | Yes (stored in FAISS)

Used for                                             | Used for
-----------------------------------------------------|-------------------------------------------------
internal transformer computation                      | semantic search / similarity lookup
