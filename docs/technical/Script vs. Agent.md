SCRIPT                                                   AGENT
======                                                   =====


FLOW MODEL                                              FLOW MODEL
----------                                              ----------

start                                                    goal = objective
  │                                                      │
  ▼                                                      ▼
step 1                                                   observe environment
  │                                                      │
  │  librarian analogy:                                  │  librarian analogy:
  │  follow the next line on a fixed                     │  scan the library floor, desk queue,
  │  procedure sheet                                     │  patron request, and shelf status
  ▼                                                      ▼
step 2                                                   reason / plan
  │                                                      │
  │  librarian analogy:                                  │  librarian analogy:
  │  follow the second line on the                       │  decide which library method fits
  │  same procedure sheet                                │  this situation before acting
  ▼                                                      │
step 3                                                   │  task = classify_request(input)
  │                                                      │
  │  librarian analogy:                                  │  │  librarian analogy:
  │  follow the third line on the                        │  │  first identify the kind of help
  │  same procedure sheet                                │  │  the patron actually needs
  ▼                                                      │
end                                                      │  if task == "structured_decision":
                                                         │      use rule_engine
                                                         │
                                                         │      librarian analogy:
                                                         │      consult the catalog policy
                                                         │      or circulation rulebook
                                                         │
                                                         │  elif task == "prediction":
                                                         │      use ML_model
                                                         │
                                                         │      librarian analogy:
                                                         │      use historical borrowing
                                                         │      patterns to predict likely need
                                                         │
                                                         │  elif task == "optimization":
                                                         │      use solver
                                                         │
                                                         │      librarian analogy:
                                                         │      compute the best shelf route,
                                                         │      staffing plan, or packing order
                                                         │
                                                         │  elif task == "planning":
                                                         │      use search_algorithm
                                                         │
                                                         │      librarian analogy:
                                                         │      explore possible sequences of
                                                         │      actions to reach the goal
                                                         │
                                                         │  elif task == "open_ended_reasoning":
                                                         │      call LLM
                                                         │
                                                         │      librarian analogy:
                                                         │      handle an ambiguous research
                                                         │      question requiring synthesis
                                                         ▼
                                                     choose action
                                                         │
                                                         │  librarian analogy:
                                                         │  pick the next concrete move:
                                                         │  check catalog, pull book, ask patron,
                                                         │  reserve room, escalate to archivist
                                                         ▼
                                                     execute
                                                         │
                                                         │  librarian analogy:
                                                         │  actually perform the chosen task
                                                         ▼
                                                     evaluate result
                                                         │
                                                         │  librarian analogy:
                                                         │  verify whether the patron got the
                                                         │  right book, answer, or outcome
                                                         ▼
                                             goal reached? ── no ──┐
                                                         │          │
                                                         │          │  librarian analogy:
                                                         │          │  if not solved, reassess and
                                                         │          │  try a different approach
                                                         yes        │
                                                         ▼          │
                                                        end ◄───────┘


ANALOGY                                                ANALOGY
-------                                                -------

Printed checkout procedure                             Reference librarian handling a complex request

read step card                                        assess patron need
do step 1                                             decide lookup strategy
do step 2                                               ├─ catalog rules
do step 3                                               ├─ prior case knowledge
stop                                                    ├─ library policies
                                                        └─ judgment under ambiguity
                                                      choose source or action
                                                      perform lookup / retrieval / escalation
                                                      check whether request is satisfied
                                                      adjust approach if needed
                                                      finish when objective is met


STATE + DECISIONS                                      STATE + DECISIONS
-----------------                                      -----------------

input → process → output                              observe → decide → act → learn
no memory                                             maintains state / context
no adaptation                                         adapts each loop

librarian analogy:                                    librarian analogy:
a clerk following a laminated                         a librarian who remembers what
desk script with no deviation                         has already been checked and
                                                      updates the search strategy


ERROR BEHAVIOR                                        ERROR BEHAVIOR
--------------                                        --------------

step fails → program stops                            action fails
                                                      │
                                                      │  librarian analogy:
                                                      │  first attempt did not solve
                                                      │  the patron's problem
                                                      ▼
                                                 retry / change strategy
                                                      │
                                                      │  librarian analogy:
                                                      │  try a different index, source,
                                                      │  policy path, or specialist
                                                      ▼
                                                 continue toward goal

script-side librarian analogy:
if the procedure sheet breaks at line 2,
the clerk stops because there is no built-in
decision authority

agent-side librarian analogy:
if the first lookup fails, the librarian can
reformulate the search, consult another system,
or escalate while still pursuing the same goal
