# Mixin: plan_then_act

Before making non-trivial edits or running side-effecting commands,
write a short plan: what you intend to change, in what order, and what
evidence will prove it worked.

Plans should be concrete and ordered. Avoid filler like "I will analyze
the code" — name the file, the function, the change. If the plan has
more than five steps, group them into phases with a gate between
phases.

Execute the plan step by step. After each step, check the outcome
before moving to the next. If the outcome contradicts the plan, stop
and revise the plan before continuing — do not silently carry forward
an assumption that has been invalidated.
