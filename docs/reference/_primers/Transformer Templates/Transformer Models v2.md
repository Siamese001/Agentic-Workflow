========================================================================================================================================================
MODEL EVOLUTION ROADMAP
From static NLP features -> static embeddings -> contextual transformer understanding -> embedding transformers -> generative LLMs -> ChatGPT / agents
========================================================================================================================================================


TIME ─────────────────────►   pre-2013                  2013-2017                      2018-2021                         2019-present                     2018-present                    2022-present


┌──────────────────────────────┬──────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┬──────────────────────────────────┬─────────────────────────────────┐
│ 1. CLASSICAL NLP             │ 2. STATIC EMBEDDINGS        │ 3. EARLY TRANSFORMER TASK MODELS │ 4. TRANSFORMER EMBEDDING MODELS  │ 5. GENERATIVE LLMs              │ 6. CHATGPT / GENAI / AGENTS     │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ Primary purpose              │ Primary purpose              │ Primary purpose                  │ Primary purpose                  │ Primary purpose                  │ Primary purpose                 │
│ Count / label / match text   │ Give words learned vectors   │ Understand text for tasks        │ Compress meaning into vectors    │ Generate next tokens             │ Converse, create, act           │
│                              │                              │                                  │ for search / retrieval           │                                  │ with tools and workflows        │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ Core idea                    │ Core idea                    │ Core idea                        │ Core idea                        │ Core idea                        │ Core idea                       │
│ Text as counts / patterns    │ One word = one main vector   │ Transformer reads context        │ Transformer reads context        │ Transformer predicts             │ LLM wrapped with instruction,   │
│                              │                              │ then outputs task result         │ then outputs an embedding vector │ next token repeatedly            │ memory, tools, orchestration    │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ Context sensitivity          │ Context sensitivity          │ Context sensitivity              │ Context sensitivity              │ Context sensitivity              │ Context sensitivity             │
│ Low                          │ Low                          │ High                             │ High                             │ High                             │ Very high                       │
│ "bank" mostly literal stats  │ "bank" mostly same vector    │ "bank" changes by context        │ sentence / chunk meaning changes │ next token depends on prompt     │ long context + retrieval +      │
│                              │ everywhere                   │                                  │ with surrounding tokens          │ history                          │ tool outputs                    │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ Transformer?                 │ Transformer?                 │ Transformer?                     │ Transformer?                     │ Transformer?                     │ Transformer?                    │
│ No                           │ No                           │ Yes                              │ Yes                              │ Yes                              │ Yes                             │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ Attention heads?             │ Attention heads?             │ Attention heads?                 │ Attention heads?                 │ Attention heads?                 │ Attention heads?                │
│ No                           │ No                           │ Yes                              │ Yes                              │ Yes                              │ Yes                             │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ Typical outputs              │ Typical outputs              │ Typical outputs                  │ Typical outputs                  │ Typical outputs                  │ Typical outputs                 │
│ label / score / keyword hit  │ word vectors                 │ labels / spans / task answers    │ sentence / chunk / doc vectors   │ generated text / code            │ responses + actions + artifacts │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ Example models               │ Example models               │ Example models                   │ Example models                   │ Example models                   │ Example products / systems      │
│ TF-IDF                       │ word2vec                     │ BERT                             │ SBERT / sentence-transformers    │ GPT-1                            │ ChatGPT                         │
│ LSA                          │ GloVe                        │ RoBERTa                          │ E5                               │ GPT-2                            │ Copilots                        │
│ HMM / CRF / n-grams          │ doc2vec                      │ DistilBERT                       │ BGE / BGE-M3                     │ GPT-3 / GPT-3.5                  │ RAG assistants                  │
│ topic models                 │ fastText                     │ ALBERT                           │ OpenAI embedding models          │ GPT-4 class models               │ agentic systems                 │
│                              │                              │ T5                               │ MiniLM / MPNet / Jina / Nomic    │ Claude / LLaMA / Qwen            │ tool-using assistants           │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ Typical use cases            │ Typical use cases            │ Typical use cases                │ Typical use cases                │ Typical use cases                │ Typical use cases               │
│ classification               │ semantic similarity          │ classification                   │ semantic search                  │ writing                          │ chat                            │
│ retrieval by exact words     │ clustering                   │ sentiment analysis               │ retrieval / RAG                  │ coding                           │ research                        │
│ topic detection              │ document similarity          │ NER                              │ clustering                       │ summarization                    │ planning                        │
│ ranking                      │ input features for ML        │ extractive QA                    │ reranking                        │ generation                       │ action dispatch                 │
│                              │                              │ sentence pair tasks              │ memory / cache / recommendations │ reasoning                        │ workflow orchestration          │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ Vector DB usage              │ Vector DB usage              │ Vector DB usage                  │ Vector DB usage                  │ Vector DB usage                  │ Vector DB usage                 │
│ No                           │ not usually the main pattern │ Usually no                       │ Yes                              │ Usually no                       │ Often yes, via retrieval layer  │
│                              │                              │                                  │ FAISS / Pinecone / Chroma / etc  │ unless separate embeddings used  │ for memory / grounding          │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼──────────────────────────────────┼─────────────────────────────────┤
│ Main limitation              │ Main limitation              │ Main limitation                  │ Main limitation                  │ Main limitation                  │ Main limitation                 │
│ weak semantics               │ no true context awareness    │ not a free-form chat generator   │ not a text generator             │ can hallucinate / drift          │ needs governance, retrieval,    │
│ brittle lexical matching     │ one word, one vector         │ BERT is not a next-token LLM     │ vector is the product            │ without grounding                │ memory, evaluation, tooling     │
└──────────────────────────────┴──────────────────────────────┴──────────────────────────────────┴──────────────────────────────────┴──────────────────────────────────┴─────────────────────────────────┘



========================================================================================================================================================
PROCESS FLOW BY COLUMN
========================================================================================================================================================

1) CLASSICAL NLP
text -> counts / features -> classifier / ranker

2) STATIC EMBEDDINGS
text -> tokenizer -> shallow training objective -> fixed word vector

3) EARLY TRANSFORMER TASK MODELS
text -> tokenizer -> token embedding matrix -> transformer layers -> task-specific head -> label / span / task output

4) TRANSFORMER EMBEDDING MODELS
text -> tokenizer -> token embedding matrix -> transformer layers -> pooling / projection -> embedding vector

5) GENERATIVE LLMs
text -> tokenizer -> token embedding matrix -> transformer layers -> next-token head -> probability distribution -> generated sequence

6) CHATGPT / GENAI / AGENTS
user ask -> LLM -> optional retrieval / tools / memory / policy / orchestration -> response or action



========================================================================================================================================================
THE KEY SPLITS TO REMEMBER
========================================================================================================================================================

STATIC EMBEDDINGS
word2vec / GloVe / fastText
= no attention heads
= no transformer
= same word gets mostly same vector everywhere

EARLY TRANSFORMER TASK MODELS
BERT / RoBERTa / T5
= transformer-based
= contextual understanding
= usually task output, not free-form generation

TRANSFORMER EMBEDDING MODELS
SBERT / E5 / BGE / OpenAI embedding models
= transformer-based
= contextual embeddings are the product
= used in retrieval, vector DBs, RAG

GENERATIVE LLMs
GPT / Claude / LLaMA / Qwen
= transformer-based
= next-token prediction
= used for text generation and chat

CHATGPT / GENAI / AGENTS
= product layer on top of LLMs
= instruction following + tools + retrieval + workflow behavior



========================================================================================================================================================
BERT VS GPT  |  THE MOST IMPORTANT 2018 SPLIT
========================================================================================================================================================

BERT PATH
text -> transformer -> task head
output = masked-token prediction / classification / QA / contextual representations

GPT PATH
text -> transformer -> next-token head
output = next-token probabilities -> generation

MEMORY TRICK
BERT = understand the sentence
GPT  = continue the sentence



========================================================================================================================================================
ONE-LINE TIMELINE
========================================================================================================================================================

pre-2013  = classical NLP
2013-2017 = static embeddings
2018      = contextual models arrive at scale
2018      = BERT opens transformer understanding path
2018      = GPT opens transformer generation path
2019+     = transformer embedding models become retrieval workhorses
2022+     = ChatGPT makes the generative path mainstream