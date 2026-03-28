======================================================================================================================
TOKEN EMBEDDING MATRIX (COMPONENT INSIDE TRANSFORMER)   │ EMBEDDING MODEL + VECTOR DATABASE PIPELINE
======================================================================================================================

Purpose                                                 │ Purpose
────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────
Convert tokens to initial vectors                       │ Generate semantic vectors and search them
(Base card catalog mapping words to shelf coords)       │ (Reference librarian summarizing context for the archive)

Location                                                │ Location
────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────
Inside the transformer model                            │ BGE = embedding model (The Reference Librarian)
                                                        │ FAISS = vector database (The Master Architectural Archive)

Model Parameters (Delivered via Hugging Face)           │ Model Parameters (Delivered via Hugging Face)
────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────
Mechanism: Downloaded from Hub to ~/.cache/huggingface/ │ Mechanism: Downloaded from Hub to ~/.cache/huggingface/
Identity: These ARE the specific values in the matrix   │ Identity: These ARE the BGE model's trained neural network
Role: They dictate exactly how tokens map to vectors    │ Role: They dictate how context is compressed into embeddings

Pipeline                                                │ Pipeline
────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────
                                                        │
text (the raw book text)                                │ text (the user query or document)
 │                                                      │  │
 ▼                                                      │  ▼
tokenizer (the cataloging clerk)                        │ tokenizer
 │                                                      │  │
 ▼                                                      │  ▼
tokens (discrete catalog entries)                       │ tokens
 │                                                      │  │
 │  ┌──────────────────────────────────────────────┐    │  │  ┌────────────────────────────────────────────────────┐
 │  │ TRAINED PARAMETERS (Delivered via HF Cache)  │    │  │  │ TRAINED PARAMETERS (Delivered via HF Cache)        │
 │  └──────────────────────┬───────────────────────┘    │  │  └────────────────────────┬───────────────────────────┘
 │                         │ instantiate the model      │  │                           │ instantiate the model
 ▼                         ▼                            │  ▼                           ▼
┌──────────────────────────────────────────────────┐    │ ┌──────────────────────────────────────────────────────────┐
│ TRANSFORMER MODEL                                │    │ │ EMBEDDING MODEL (BGE-M3 / The Librarian)                 │
│                                                  │    │ │                                                          │
│ internal component highlighted:                  │    │ │ TRANSFORMER MODEL                                        │
│                                                  │    │ │                                                          │
│  ┌────────────────────────────────────────────┐  │    │ │  token embedding matrix (base shelf coords)              │
│  │ TOKEN EMBEDDING MATRIX                     │  │    │ │  │                                                       │
│  │                                            │  │    │ │  ▼                                                       │
│  │ rows = tokens in vocab (index cards)       │  │    │ │  transformer attention layers (reading context)          │
│  │ columns = hidden dims (shelf coordinates)  │  │    │ │  │                                                       │
│  │                                            │  │    │ │  ▼                                                       │
│  │ token_id ► vector                          │  │    │ │  contextual token representations (understood meaning)   │
│  │                                            │  │    │ │  │                                                       │
│  │ example:                                   │  │    │ │  ▼                                                       │
│  │ "yaml" ► [0.21, -0.33, ...]                │  │    │ │  pooling / projection (final summary formulation)        │
│  └────────────────────────────────────────────┘  │    │ └──────────────────────────────────────────────────────────┘
│                                                  │    │  │
│ (other transformer layers run after this)        │    │  ▼
└──────────────────────────────────────────────────┘    │ ┌──────────────────────────────────────────────────────────┐
 │                                                      │ │ FINAL EMBEDDING VECTOR (Semantic Call Number)            │
 ▼                                                      │ │                                                          │
token vectors (initial shelf coordinates)               │ │ sentence_vector = [v1, v2 ... vN]                        │
 │                                                      │ │                                                          │
 ▼                                                      │ │ example:                                                 │
transformer layers (contextual reading room)            │ │ [0.12, -0.87, 0.41 ...]                                  │
 │                                                      │ └──────────────────────────────────────────────────────────┘
 ▼                                                      │  │
contextualized token representations                    │  ▼
                                                        │ ┌──────────────────────────────────────────────────────────┐
Matrix Structure                                        │ │ VECTOR DATABASE (FAISS / Master Archive)                 │
────────────────────────────────────────────────────────┤ │                                                          │
                                                        │ │ Stores vectors + metadata (Archival records)             │
vocab_size × hidden_dimension                           │ │                                                          │
(Total Index Cards × Coordinate Granularity)            │ │ vector = [0.12, -0.87, ...]                              │
                                                        │ │ metadata:                                                │
example:                                                │ │  reference_desk_checked: true                            │
100000 × 1024                                           │ │  checkout_status: success                                │
                                                        │ │  shelf_location_id: /archives/section7/                  │
                                                        │ │                                                          │
                                                        │ │ Performs similarity search (Find similar books)          │
                                                        │ │ nearest_neighbor(vector)                                 │
                                                        │ └──────────────────────────────────────────────────────────┘

Stored in Vector DB?                                    │ Stored in Vector DB?
────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────
No (Strictly internal to the reading model)             │ Yes (permanently stored in FAISS archive)

Used for                                                │ Used for
────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────
internal transformer computation (reading the text)     │ semantic search / similarity lookup (finding text)
