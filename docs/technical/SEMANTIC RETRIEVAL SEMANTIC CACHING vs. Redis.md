SEMANTIC RETRIEVAL                         SEMANTIC CACHING                         REDIS
(Analogy beside terms)                     (Analogy beside terms)                   (Analogy beside terms)

WHAT IT IS                                 WHAT IT IS                               WHAT IT IS
-----------                                -----------                              -----------
Retrieve relevant knowledge                Reuse previously computed answers        Fast in-memory datastore
from documents                             when a similar question appears          used to store cached answers
Librarian searching the library            Librarian recognizing a past question    Bookshelf / filing cabinet
for relevant books                         is almost the same                       where written answers live


CORE FUNCTION                              CORE FUNCTION                            CORE FUNCTION
-------------                              -------------                            -------------
Find relevant documents                    Decide if a previous result              Store and retrieve cached
using similarity                           can be reused                            answers quickly
Librarian locating useful books            Librarian recognizing a repeated         Bookshelf holding the answers
                                           or very similar question


HOW IT WORKS                               HOW IT WORKS                             HOW IT WORKS
------------                               ------------                              ------------
query → embedding                          query → embedding                         key → value lookup
        │                                           │                                        │
        ▼                                           ▼                                        ▼
vector similarity search                   vector similarity search                   in-memory hash table
        │                                           │                                        │
        ▼                                           ▼                                        ▼
return relevant documents                  reuse cached answer if similar             return stored value
librarian pulls relevant books             librarian recalls a prior answer           bookshelf hands back the answer


ASCII FLOW                                 ASCII FLOW                                ASCII FLOW
-----------                                -----------                               ----------
User Query                                 User Query                                Key Request
     │                                          │                                          │
     ▼                                          ▼                                          ▼
Embedding Model                            Embedding Model                            Redis Lookup
     │                                          │                                          │
     ▼                                          ▼                                          ▼
Vector Similarity                         Vector Similarity                           Value Returned
     │                                          │
     ▼                                          ▼
Relevant Documents Returned                Cached Answer Returned


ROLE IN AN AI SYSTEM                       ROLE IN AN AI SYSTEM                       ROLE IN AN AI SYSTEM
-------------------                        -------------------                        -------------------
Knowledge retrieval layer                  Latency / cost optimization layer          Storage layer
Research phase of librarian                Librarian remembering similar              Library shelves or
                                           questions already answered                 filing cabinet storing answers
