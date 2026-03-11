SCRIPT                                           AGENT
======                                           =====


FLOW MODEL                                      FLOW MODEL
----------                                      ----------

start                                            goal = objective
  │                                              │
  ▼                                              ▼
step 1                                      observe environment
  │                                              │
  ▼                                              ▼
step 2                                      reason / plan
  │                                           │
  ▼                                           │  task = classify_request(input)
step 3                                        │
  │                                           │  if task == "structured_decision":
  ▼                                           │      use rule_engine
end                                           │
                                              │  elif task == "prediction":
                                              │      use ML_model
                                              │
                                              │  elif task == "optimization":
                                              │      use solver
                                              │
                                              │  elif task == "planning":
                                              │      use search_algorithm
                                              │
                                              │  elif task == "open_ended_reasoning":
                                              │      call LLM
                                              │
                                              ▼
                                          choose action
                                              │
                                              ▼
                                          execute
                                              │
                                              ▼
                                          evaluate result
                                              │
                                              ▼
                                      goal reached? ── no ──┐
                                              │              │
                                              yes            │
                                              ▼              │
                                             end ◄───────────┘


ANALOGY                                        ANALOGY
-------                                        -------

Vending Machine                                 Chef in a Kitchen

press B4                                        look in fridge
dispense snack                                  decide recipe
no thinking                                       ├─ recipe knowledge
                                                   ├─ taste memory
                                                   ├─ cooking rules
                                                   └─ creativity
                                                 choose ingredients
                                                 cook dish
                                                 taste food
                                                 adjust seasoning
                                                 serve meal


STATE + DECISIONS                                STATE + DECISIONS
-----------------                                -----------------

input → process → output                        observe → decide → act → learn
no memory                                       maintains state / context
no adaptation                                   adapts each loop


ERROR BEHAVIOR                                  ERROR BEHAVIOR
--------------                                  --------------

step fails → program stops                      action fails
                                                │
                                                ▼
                                          retry / change strategy
                                                │
                                                ▼
                                            continue toward goal