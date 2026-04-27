LLM AS JUDGE = THE MODEL THAT GRADES THE WORKER MODEL'S OUTPUT, NOT THE MODEL THAT DOES THE WORK

[ USER REQUEST ]
       |
       v
+---------------------------+
| L1 / L0 / [opt L3]        |
| plan, route, orchestrate  |
+---------------------------+
       |
       v
+---------------------------+
| L2 WORKER LLM / TOOLS     |
| "Do the task"             |
| - reason                  |
| - retrieve/use evidence   |
| - call tools              |
| - draft answer / action   |
+---------------------------+
       |
       |  sealed output: answer / artifact / tool result / proposed action
       v
+---------------------------+
| EXIT EVAL / CONTROL       |
| LLM AS JUDGE LIVES HERE   |
| "Was the work good enough?" 
+---------------------------+
       |
       +--> checks correctness
       +--> checks groundedness
       +--> checks completeness
       +--> checks policy / safety
       +--> checks schema / format
       +--> checks whether commit is allowed
       |
       v
  +------------------- DECISION RAIL --------------------+
  |                                                      |
  |   PASS / ALLOW                                       |
  |      |                                               |
  |      v                                               |
  |   return answer                                      |
  |   or send commit request                             |
  |                                                      |
  |   FAIL / WEAK / RISK                                 |
  |      |                                               |
  |      +--> retry / heal                               |
  |      +--> reroute                                    |
  |      +--> escalate to HITL                           |
  |      +--> deny                                       |
  +------------------------------------------------------+

MENTAL MODEL
------------
WORKER LLM = student writing the answer
JUDGE LLM  = teacher grading the answer

IMPORTANT BOUNDARY
------------------
WORKER generates
JUDGE evaluates

The judge is downstream of execution, not the main execution engine.
It is part of exit control, deciding whether the produced result is acceptable.