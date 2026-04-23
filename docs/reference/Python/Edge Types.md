====================================================================================================
EDGE TYPES: WHAT DOES EACH ARROW MEAN?
====================================================================================================

1) IMPORT EDGE
Question: "Who depends on whose code being present?"

[ service.py ] ----------------imports----------------> [ db.py ]

Meaning:
- service.py pulls db.py into its namespace
- static file/module dependency
- if db.py moves or breaks, service.py may break before runtime flow even starts

Think:
"Needs this code loaded"


2) CALL EDGE
Question: "Who invokes whose function?"

[ get_user() ] ----------------calls------------------> [ query_db() ]

Meaning:
- one function actively invokes another
- behavioral/runtime relationship
- narrower than import: a file can import many things but call only some

Think:
"Actually executes this"


3) CONTROL-FLOW EDGE
Question: "Where can execution go next?"

                    +----------------------> [ reject ]
                    |
[ validate_input ]--+
                    |
                    +----------------------> [ execute ]

Meaning:
- branch or next-step possibility
- shows path decisions, not data contents
- often comes from if/else, match, loops, workflow routing

Think:
"Next possible step"


4) DATA-FLOW EDGE
Question: "Where does the information move?"

[ raw_payload ] ---------------flows_to---------------> [ validator ]
[ validated_obj ] ------------flows_to---------------> [ executor ]

Meaning:
- value/object/result moves from one place to another
- not about who called whom, but where the payload goes
- useful for tracing state, secrets, mutations, lineage

Think:
"This data travels here"


5) INHERITANCE EDGE
Question: "Who is a specialized version of whom?"

[ RedisAgent ] ----------------extends----------------> [ BaseAgent ]

Meaning:
- subclass inherits behavior/contract from parent class
- structural OOP relationship
- not execution by itself

Think:
"Is built on top of this class"


6) IMPLEMENTATION EDGE
Question: "Who satisfies this interface/contract?"

[ ToolExecutor ] ------------implements---------------> [ IExecutable ]

Meaning:
- class promises to provide required methods of an interface
- contract relationship
- useful for architecture compliance and substitution

Think:
"Fulfills this contract"


7) CONTAINMENT EDGE
Question: "What lives inside what?"

[ module.py ] ----------------contains----------------> [ MyClass ]
[ MyClass ] ------------------contains----------------> [ run() ]

Meaning:
- ownership / nesting / hierarchy
- not dependency, not runtime behavior
- used to organize symbols inside files/classes

Think:
"Physically or logically inside"


8) READ EDGE
Question: "Who is allowed to read from where?"

[ L1 ] ------------------------reads-------------------> [ L4 ]
[ C0 ] ------------------------reads-------------------> [ L4 ]

Meaning:
- component consumes state/info from another store/system
- authority relationship
- important in your architecture because broad read is allowed, but write is tightly controlled :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1}

Think:
"Can look at truth"


9) WRITE EDGE
Question: "Who is allowed to change truth?"

[ Universal Write Gate ] ------writes-----------------> [ L4 ]

Meaning:
- mutation authority
- strongest edge in governance terms
- in your process maps, durable writes go through the Universal Write Gate into L4, not directly from random runtime components :contentReference[oaicite:2]{index=2} :contentReference[oaicite:3]{index=3}

Think:
"Can change truth"


10) ROUTE / DISPATCH EDGE
Question: "Who chooses the next path?"

[ L0 Routing ] ---------------route_to---------------> [ Cache ]
[ L0 Routing ] ---------------route_to---------------> [ RAG / C0 ]
[ L0 Routing ] ---------------route_to---------------> [ Action ]
[ L0 Routing ] ---------------route_to---------------> [ Fallback ]

Meaning:
- decision handoff
- not the same as control-flow inside a function
- higher-level system routing / workflow switching :contentReference[oaicite:4]{index=4} :contentReference[oaicite:5]{index=5}

Think:
"Chooses which lane to enter"


====================================================================================================
VISUAL DIFFERENCE: SAME SYSTEM, DIFFERENT EDGE TYPES
====================================================================================================

CODE VIEW
---------
[ service.py ] --imports--> [ db.py ]
[ service.py ] --contains--> [ get_user() ]
[ get_user() ] --calls-----> [ query_db() ]


RUNTIME PATH VIEW
-----------------
[ validate ] --control-----> [ execute ]
[ validate ] --control-----> [ reject ]


DATA MOVEMENT VIEW
------------------
[ request json ] --data-----> [ parser ] --data-----> [ typed object ] --data-----> [ executor ]


AUTHORITY VIEW
--------------
[ L1 ] --reads-------------> [ L4 ]
[ UWG ] --writes-----------> [ L4 ]


ROUTING VIEW
------------
[ L0 ] --route_to----------> [ RAG ]
[ L0 ] --route_to----------> [ Action ]


====================================================================================================
MOST IMPORTANT DIFFERENCES
====================================================================================================

A) IMPORT vs CALL
-----------------

[ file A ] --imports--> [ file B ]
    |
    +-- may or may not call anything inside B

[ fn A ] ---calls-----> [ fn B ]

Difference:
- import = dependency exists
- call   = execution actually invokes

Visual:

[ service.py ] --imports--> [ db.py ]
[ service.py ] --imports--> [ cache.py ]

[ get_user() ] --calls----> [ query_db() ]
(no call to cache.py even though imported)


B) CALL vs DATA-FLOW
--------------------

[ fn A ] --calls-----> [ fn B ]
[ result ] --flows---> [ fn C ]

Difference:
- call edge = who invoked whom
- data edge = where the value went

Visual:

[ parse() ] --calls-----> [ validate() ]
      |
      +----produces obj----flows_to----> [ execute() ]

One is invocation.
One is payload movement.


C) CONTROL-FLOW vs ROUTE
------------------------

Function-level control flow:

[ if check ] --yes----> [ do_work ]
[ if check ] --no-----> [ reject ]

System-level route dispatch:

[ L0 ] --route_to-----> [ Cache ]
[ L0 ] --route_to-----> [ RAG ]
[ L0 ] --route_to-----> [ Action ]

Difference:
- control-flow = local branching inside logic
- route edge   = higher-level path selection across subsystems


D) READ vs WRITE
----------------

[ component ] --reads-----> [ store ]
[ component ] --writes----> [ store ]

Difference:
- read = can observe truth
- write = can mutate truth

This distinction is one of the most important governance boundaries in your architecture. :contentReference[oaicite:6]{index=6} :contentReference[oaicite:7]{index=7}


====================================================================================================
ONE COMBINED EXAMPLE
====================================================================================================

[ api.py ] ----------------imports----------------> [ service.py ]
[ service.py ] ------------imports----------------> [ db.py ]

[ service.py ] ------------contains---------------> [ get_user() ]
[ db.py ] -----------------contains---------------> [ query_db() ]

[ get_user() ] ------------calls------------------> [ query_db() ]

[ query result ] ----------flows_to---------------> [ formatter ]

[ auth check ] ------------control----------------> [ allow ]
[ auth check ] ------------control----------------> [ deny ]


====================================================================================================
MENTAL MODEL
====================================================================================================

import edge     = "I need this code available"
call edge       = "I execute this function"
control edge    = "Execution can go here next"
data edge       = "This value moves here"
inherit edge    = "I am a specialized version of this"
implements edge = "I satisfy this contract"
contains edge   = "This lives inside this"
read edge       = "I can observe this state"
write edge      = "I can change this state"
route edge      = "I choose this system path"


====================================================================================================
ULTRA-SHORT CHEAT SHEET
====================================================================================================

STRUCTURE
[ A ] --imports--> [ B ]
[ ClassX ] --extends--> [ Base ]
[ ClassX ] --implements--> [ Interface ]
[ module ] --contains--> [ symbol ]

BEHAVIOR
[ fn1 ] --calls--> [ fn2 ]
[ step1 ] --control--> [ step2 ]
[ obj ] --flows_to--> [ consumer ]

AUTHORITY
[ agent ] --reads--> [ state ]
[ UWG ] --writes--> [ L4 ]

SYSTEM TOPOLOGY
[ L0 ] --route_to--> [ RAG / Action / Fallback ]