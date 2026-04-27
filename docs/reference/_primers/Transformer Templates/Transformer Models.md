=============================================================================================================
TRANSFORMER MODEL EVOLUTION
=============================================================================================================

EARLY TRANSFORMER TASK MODELS          | EMBEDDING MODELS                         | GENERATIVE LLMs
(2018–2021)                            | (2019–present)                           | (2022–present)
-------------------------------------------------------------------------------------------------------------
Primary Purpose                        | Primary Purpose                          | Primary Purpose
---------------------------------------|------------------------------------------|------------------------------------------
Solve specific NLP tasks               | Represent semantic meaning               | Generate text / code

Typical Tasks                          | Typical Tasks                            | Typical Tasks
---------------------------------------|------------------------------------------|------------------------------------------
classification                         | semantic search                          | chat
translation                            | retrieval                                | writing
sentiment analysis                     | clustering                               | coding
question answering                     | document similarity                      | reasoning

Example Models                         | Example Models                           | Example Models
---------------------------------------|------------------------------------------|------------------------------------------
BERT                                   | sentence-transformers                    | GPT-3.5
RoBERTa                                | BGE-M3                                   | GPT-4
T5                                     | OpenAI text-embedding models             | LLaMA
DistilBERT                             | E5 embeddings                            | Claude
                                       |                                          | Qwen

Transformer Usage                      | Transformer Usage                        | Transformer Usage
---------------------------------------|------------------------------------------|------------------------------------------
text                                   | text                                     | text
 ↓                                     | ↓                                        | ↓
tokenizer                              | tokenizer                                | tokenizer
 ↓                                     | ↓                                        | ↓
tokens                                 | tokens                                   | tokens
 ↓                                     | ↓                                        | ↓
token embedding matrix                 | token embedding matrix                   | token embedding matrix
 ↓                                     | ↓                                        | ↓
transformer layers                     | transformer layers                       | transformer layers
 ↓                                     | ↓                                        | ↓
task-specific head                     | pooling / projection                     | next-token prediction head
 ↓                                     | ↓                                        | ↓
task output                            | sentence embedding vector                | probability distribution

Output Example                         | Output Example                           | Output Example
---------------------------------------|------------------------------------------|------------------------------------------
label = "positive sentiment"           | [0.12, -0.87, 0.41 ...]                  | next token probabilities

Vector Database Usage                  | Vector Database Usage                    | Vector Database Usage
---------------------------------------|------------------------------------------|------------------------------------------
No                                     | Yes (FAISS / Pinecone / etc)             | No
