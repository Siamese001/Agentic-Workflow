SEMANTIC RETRIEVAL                         SEMANTIC CACHING                         REDIS
(Analogy beside terms)                     (Analogy beside terms)                   (Analogy beside terms)

WHAT IT IS                                 WHAT IT IS                               WHAT IT IS
-----------                                -----------                              -----------
Retrieve relevant knowledge                Reuse previously computed answers        Fast in-memory datastore
from documents                             when a similar question appears          used to store cached answers
Librarian searching the catalog            Librarian recognizing a question         Physical shelving system
by topic similarity                        already answered earlier                 storing written reference cards
to locate relevant books                   in the library logbook                   for fast retrieval


CORE FUNCTION                              CORE FUNCTION                            CORE FUNCTION
-------------                              -------------                            -------------
Find relevant documents                    Decide if a previous result              Store and retrieve cached
using similarity                           can be reused                            answers quickly
Librarian matching topic keywords          Librarian checking the                   Librarian pulling a card
and subject classification                 “previous questions ledger”              from the reference drawer
to select the most relevant books          to see if the same question              and handing it back immediately
                                           was answered before


TOOLS COMMONLY USED                        TOOLS COMMONLY USED                      TOOLS COMMONLY USED
-------------------                        -------------------                      -------------------
Vector DBs + embedding models              Semantic cache frameworks                Redis datastore / clients
FAISS, Pinecone, Milvus, Chroma            GPTCache, LangChain cache, LlamaIndex    Redis Server, Redis Stack
OpenAI embeddings, BGE models              embedding similarity cache               redis-py, ioredis, Jedis
Librarian using the subject catalog        Librarian referencing the                Library shelving and card index
system to locate books                     “answered questions log”                 where prepared answers are stored


HOW IT WORKS + EXECUTION FLOW              HOW IT WORKS + EXECUTION FLOW            HOW IT WORKS + EXECUTION FLOW
------------------------------             ------------------------------           ------------------------------
User Query                                 User Query                               Key Request
     │                                          │                                         │
     ▼                                          ▼                                         ▼
Create query embedding                      Create query embedding                    Lookup key
(embedding model)                           (embedding model)                         in Redis
     │                                          │                                         │
     ▼                                          ▼                                         ▼
Vector similarity search                    Vector similarity search                  In-memory hash table lookup
against document vectors                    against cached query vectors              (O(1) key lookup)
     │                                          │                                         │
     ▼                                          ▼                                         ▼
Top-K relevant documents                    If similar query found →                  Stored value returned
returned                                   return cached answer                      immediately
     │                                          │
     ▼                                          ▼
LLM reads documents                         Skip LLM + retrieval
to produce answer                           return cached result
Librarian retrieves books                   Librarian recognizes the same
from the subject catalog                    question in the answered-log
and brings them to the reader               and provides the prior answer


ROLE IN AN AI SYSTEM                       ROLE IN AN AI SYSTEM                       ROLE IN AN AI SYSTEM
-------------------                        -------------------                        -------------------
Knowledge retrieval layer                  Latency / cost optimization layer          Storage layer
Research phase of librarian                Librarian remembering similar              Library shelves or
                                           questions already answered                 card catalog storing answers