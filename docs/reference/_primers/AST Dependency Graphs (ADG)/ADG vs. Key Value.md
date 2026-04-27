ADG (AST DEPENDENCY GRAPH)                                       KEY–VALUE STORE
==========================                                       =================


CORE TECHNICAL ROLE                                              CORE TECHNICAL ROLE
-------------------                                              -------------------
Static structural analysis model                                 Data storage and retrieval engine
built from Abstract Syntax Trees                                 optimized for O(1) key lookup

Library analogy beside concept:                                  Library analogy beside concept:
library building map of how rooms connect                        labeled drawer system at front desk



STRUCTURAL FLOW & INTEGRATION (HOW THEY WORK TOGETHER)
------------------------------------------------------


      SOURCE CODE FILES                                          APPLICATION / RUNTIME
      (Python, JS, etc)                                          needs state or cached data
      librarian reading books                                    librarian requesting book

      +----------------------+                                   +------------------------+
      | Source Code          |                                   | Client / Service       |
      | functions, classes   |                                   | runtime request        |
      +----------+-----------+                                   +-----------+------------+
                 |                                                           |
                 | parse source                                              | GET(key)
                 | librarian analyzing text                                  | librarian checks label
                 v                                                           v

        +------------------+                                     +--------------------------+
        | AST PARSER       |                                     | KEY LOOKUP               |
        | builds AST tree  |                                     | hash table index search  |
        | librarian builds |                                     | librarian scans drawer   |
        | syntax tree map  |                                     | labels                   |
        +---------+--------+                                     +-----------+--------------+
                  |                                                          |
                  | extract relationships                                    |
                  | (imports, calls, writes)                                 |
                  v                                                          |
                                                                             |
       +---------------------------+                                         |
       | AST DEPENDENCY GRAPH      |                                         |
       | nodes + edges             |                                         |
       | code relationship network |                                         |
       | librarian's building map  |                                         |
       +------------+--------------+                                         |
                    |                                                        |
                    | store fragment / routing hint                          |
                    | librarian stores copy of map page                      |
                    v                                                        |
                                                                             |
              +--------------------------+                                   |
              | KEY–VALUE STORE          | <=================================+
              | Redis / etc              |
              | hash lookup table        |
              | library drawer           | ==================================+
              +--------------------------+                                   |
                                                                             | fast retrieval
                                                                             | librarian pulls map page
                                                                             v

                                                                 +--------------------------+
                                                                 | RUNTIME / EXECUTION      |
                                                                 | serialized object        |
                                                                 | JSON / binary / object   |
                                                                 | librarian hands book     |
                                                                 +--------------------------+


ADG GRAPH STRUCTURE                                              KEY–VALUE DATA STRUCTURE
-------------------                                              ------------------------

Nodes = program elements                                         Hash table / dictionary

   +-----------+                                                 "session:123" -> session state
   |  Agent A  |                                                 "prompt:hash" -> cached LLM output
   +-----+-----+                                                 "user:42"     -> user object
         |
         | function call edge
         v
   +-----------+
   | Gateway B |
   +-----+-----+
         |
         | write edge
         v
   +-----------+
   | UWG       |
   +-----------+

Library analogy beside concept:                                  Library analogy beside concept:
rooms connected by hallways                                      drawer slots labeled with IDs



TECHNICAL DATA MODEL                                             TECHNICAL DATA MODEL
--------------------                                             --------------------
Directed graph                                                   Key-value dictionary

Node types:                                                      Entry types:
• files                                                          • session state
• classes                                                        • cached computation
• functions                                                      • counters
• agents                                                         • metadata blobs

Edge types:
• imports
• function calls
• inheritance
• data writes
• data reads



ALGORITHMIC PURPOSE                                              ALGORITHMIC PURPOSE
-------------------                                              -------------------
Dependency analysis                                              Constant-time retrieval

Used for:                                                        Used for:
• architecture validation                                        • caching
• dependency tracing                                             • session storage
• mutation authority analysis                                    • queues
• code impact analysis                                           • distributed coordination



FINAL TECHNICAL DISTINCTION
---------------------------

ADG
Graph representation of relationships between program elements.

KEY–VALUE STORE
Storage engine that retrieves values using direct key indexing.

Library analogy beside distinction:
ADG = building map showing room connections
KV store = drawer system storing labeled cards
