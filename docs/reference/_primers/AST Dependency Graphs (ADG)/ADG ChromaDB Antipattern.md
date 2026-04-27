ADG -> ChromaDB ANTIPATTERN: SIMPLE MENTAL MODEL

GOOD SHAPE
----------
[ ADG GRAPH = THE MAP ]
cities = symbols/nodes
roads  = edges
routes = paths
bridges/chokepoints = graph structure

Question:
"Show me the risky route from L3 to L4"


BAD SHAPE
---------
Take the map and shred it into tiny cards:

"City A connects to City B"
"City B connects to City C"
"Bridge X touches City B"
"Road Y appears in file:line"

Then put all cards into ChromaDB and ask:

"Find me the risky route from L3 to L4"

Chroma can only say:
"These cards sound kind of related"


WHY ANTI-PATTERN
----------------
A GRAPH QUESTION needs:
- route tracing
- path structure
- chokepoints
- exact connectivity

But RAW EDGE EMBEDDINGS give:
- tiny fragments
- semantic similarity
- no full route
- weak global picture


ONE-LINE MENTAL MODEL
---------------------
ADG is a MAP.
Raw edge Chroma ingestion shreds the map into sentence scraps.
Vector search can find similar scraps, but it cannot naturally reason over the full road system.