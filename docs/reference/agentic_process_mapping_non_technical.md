====================================================================================================================================
                                      THE GRAND LIBRARY: SYSTEM PROCESS MAP
 PRIMARY PATH: [1] The Front Door -> [2] Reference Librarian -> [3] Dispatch Desk -> [4] The Vault -> [5] Checkout Desk 
                                 (Night Shift [6] reviews everything after hours to improve tomorrow)
====================================================================================================================================

[ THE LAWS OF THE LIBRARY ]
- Dispatch Desk (L0)   : Directs traffic. Decides WHERE a request goes, but doesn't do the actual research.
- Librarian (L1)       : Talks to the Patron, figures out what they need, and writes a "Research Plan".
- Section Head (L3)    : Manages complex, multi-step research projects. Keeps track of the checklist.
- Security Chief (L5)  : The ultimate authority. Stamps every plan for safety. No stamp = no entry to the Vault.
- Vault Staff (L2)     : Does the actual work in a closed room. Follows the stamped plan exactly. No guessing allowed.
- Master Clerk (UWG)   : The only person allowed to file official, permanent records into the Library Archive.
- The Archive (L4)     : The official library records, facts, and rulebooks.
- The Night Watch (L6) : Reviews the day's work to improve rules for tomorrow. Cannot change today's answers.
- The Golden Rule      : If we can't find factual proof, we must ask the Patron for clarity. Never guess or make things up.
- The Human Rule       : If a Human Manager fixes a problem, the Security Chief MUST re-stamp it before it moves forward.

====================================================================================================================================
[1] THE FRONT DOOR (Intake & Security)
====================================================================================================
- The entrance to the library. The Greeter checks ID and ensures no banned items are brought inside.
- No actual research or thinking happens here; just basic safety and membership checks.

                                               │ [ A Patron Arrives ]
                                               ▼
                    ┌────────────────────────────────────────────────────┐
                    │ REQUEST SOURCES                                    │
                    │ - A Patron walks up to the desk (Chat/UI)          │
                    │ - A courier drops off a letter (API call)          │
                    │ - A scheduled daily reminder                       │
                    └──────────────────────────┬─────────────────────────┘
                                               │
                                               ▼
                    ┌────────────────────────────────────────────────────┐
                    │ THE GREETER (Basic Checks)                         │
                    │ - Are you a member? (Identity Check)               │
                    │ - Is your request too massive? (Quota Check)       │
                    │ - Is this a banned or dangerous topic? (Reject)    │
                    │ Strict Rule: No deep reading or solving yet.       │
                    └──────────────────────────┬─────────────────────────┘
                                               │ [ Approved to enter ]
                                               ▼
                                     [ Sent to Librarian ]


====================================================================================================================================
[2] THE REFERENCE LIBRARIAN (Understanding & Planning)
====================================================================================================================================
- The Librarian listens to the Patron, understands the goal, and writes a step-by-step "Research Plan".
- They check the library's rulebooks to make sure the plan is safe, but they cannot give the final security stamp.

                                          │ [ Patron's Goal ]
                                          ▼
 ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ LIBRARIAN'S DESK (Figuring out what is needed)                                                                                   │
 │ - Understand the goal, the format needed, and any strict limits set by the Patron.                                               │
 │ - Figure out what tools, books, actions, and deadlines are required.                                                             │
 └───────────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────┘
                                                                 │
                                                                 ▼
                   ┌─────────────────────────────────────────────┴─────────────────────────────────────────────┐
                   │ CHECKING THE CATALOG (Read-only)                                                          │<──[reads]──┐
                   │ - Look up how we solved similar problems before.                                          │            │
                   │ - Check the general rulebooks and safety guidelines.                                      │            │
                   │ - See what tools the Vault Staff are allowed to use.                                      │            │
                   └─────────────────────────────────────────────┬─────────────────────────────────────────────┘            │
                                                                 │                                                          │
                                                                 ▼                                                          │
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴──┐
│ WRITING THE RESEARCH PLAN                                                                                                      │
│                                                                                                                                │
│    [ DRAFTING THE PLAN ] -------------------------------------------------------------------------------------------------┐    │
│    - Break the big question into a simple checklist of tasks.                                                             │    │
│    - Decide what needs to happen first, second, and third.                                                                │    │
│    - Note down if we need strict facts, or if we need to take an outside action (like sending an email).                  │    │
│    - Set a time limit and budget so we don't research forever.                                                            │    │
│                                                                                                                           │    │
│    [ REVIEWING THE PLAN ]                                                                                                 │    │
│    - Does this actually answer the Patron's question?                                                                     │    │
│    - Is it logical? Can the Vault Staff actually do this?                                                                 │    │
│    - Are there any safety risks? (Flag them for the Security Chief).                                                      │    │
│                                                                                                                           │    │
│    If the request is confusing or impossible --------------------------------------------------------------------------┐  │    │
│                                                                                                                        │  │    │
│    [ ASK THE PATRON FOR CLARITY OR DECLINE ] <-------------------------------------------------------------------------┘  │    │
│                                                                                                                           │    │
│    If the plan is solid and ready to go                                                                                   │    │
│                                                                                                                           ▼    │
│                                              ┌──────────────────────────────────────────────────────────────────────────┐      │
│                                              │ THE OFFICIAL RESEARCH PLAN                                               │      │
│                                              │ - The exact checklist of tasks and questions to ask.                     │      │
│                                              │ - Notes on required facts, actions, and risks.                           │      │
│                                              │ - Time limits and what to do if we get stuck.                            │      │
│                                              └──────────────────────────────┬───────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┘
                                                                             │ [ Hand off the Plan ]
                                                                             ▼
                                                                [ Sent to Dispatch Desk ]


====================================================================================================================================
[3] THE DISPATCH DESK (Deciding Where to Send the Plan)
====================================================================================================================================
- The Dispatcher looks at the Research Plan and decides exactly which department needs to handle it.
- Do we already know the answer? Do we need to pull background books? Or do we need to take an action?

                                      ┌──────────────────────────────────────────────┐
                                      │ DISPATCH DESK                                │
                                      │ Looks at the Research Plan and decides path. │
                                      └────────────────┬─────────────────────────────┘
                                                       │
                                                       ▼
                              ┌──────────────────────────────────────────────────────────────┐
                              │ QUESTION 1: DO WE ALREADY HAVE THIS EXACT ANSWER ON FILE?    │
                              │ (Has the Security Chief already approved this recently?)     │
                              └───────────────┬──────────────────────────────────────────────┘
                                          yes │                                  no
                                              ▼                                  ▼
                                 ┌─────────────────────────┐          ┌──────────────────────────────────────┐
                                 │ QUICK ANSWER DESK       │          │ QUESTION 2: DO WE NEED FACTS?        │
                                 │ Hand answer to Patron.  │          │ Does this need background reading?   │
                                 └─────────────┬───────────┘          └───────────────┬──────────────────────┘
                                               │                                  yes │                  no
                                               │                                      ▼                  ▼
                                               │               ┌──────────────────────────────┐  ┌──────────────────────────────────┐
                                               │               │ THE REFERENCE DESK (C0)      │  │ QUESTION 3: DO WE NEED ACTION?   │
                                               │               │ - Go fetch the right books.  │  │ (Like using a tool or workflow)  │
                                               │               │ - Return a pile of facts.    │  └───────────────┬──────────────────┘
                                               │               │ - Do NOT answer the patron.  │              yes │              no
                                               │               └──────────────┬───────────────┘                  │              ▼
                                               │                              │ [ Pile of Facts ]                ▼         ┌───────────────────────┐
                                               │                              ▼                        ┌──────────────────┐│ ASK FOR CLARITY       │
                                               │               ┌──────────────────────────────┐        │ TOOL DEPARTMENT  ││ We don't have enough  │
                                               │               │ READING PACKET ASSEMBLY      │        │ Send the plan to ││ info or it is unsafe. │
                                               │               │ - Put the facts and the plan │        │ the action desk. ││ Decline or ask patron.│
                                               │               │   into a neat folder.        │        └────────┬─────────┘└──────────┬────────────┘
                                               │               └──────────────┬───────────────┘                 │                     │
                                               │                              │                                 │                     │
                                               └──────────────────────────────┴───────────────┬─────────────────┴─────────────────────┘
                                                                                              │ [ The Final Work Folder ]
                                                                                              ▼
                                                                                   [ Sent to The Vault ]


====================================================================================================================================
[4] THE VAULT & ORCHESTRATION (Doing the Actual Work)
====================================================================================================================================
- Simple requests go straight to the Security Chief for a stamp, then into the Vault.
- Complex requests go to the Section Head first, who manages the multi-step checklist.
- The Vault Staff actually read the books, write the answers, or use the tools.

                                                   │ [ The Work Folder arrives ]
                                                   ▼
                                  ┌───────────────────────────────────────────────┐
                                  │ IS THIS A SIMPLE OR COMPLEX TASK?             │
                                  └───────────────┬───────────────────────────────┘
                                          Simple  │                               Complex
                                                  ▼                               ▼
                                   ┌──────────────────────────┐          ┌─────────────────────────────────────────────────────┐
                                   │ DIRECT TO VAULT          │          │ SECTION HEAD (Complex Orchestration)                │
                                   │ Ready for one quick task.│          │ - Manages the multi-step checklist.                 │
                                   └─────────────┬────────────┘          │ - Tracks the budget and time for each step.         │
                                                 │                       │ - Decides when to move to the next step.            │
                                                 │                       │ - Hands one step at a time to Security.             │
                                                 │                       └───────────────────────┬─────────────────────────────┘
                                                 │                                               │
                                                 └───────────────────────────┬───────────────────┘
                                                                             │ [ Proposed Step to take ]
                                                                             ▼
                                          ┌───────────────────────────────────────────────────────────────────────────────────────┐
                                          │ SECURITY CHIEF (The Commandant's Stamp)                                               │
                                          │ - Checks the rulebooks one last time before work begins.                              │
                                          │ - Is the Vault Staff allowed to use this tool? Will it break anything?                │
                                          │ - Rejects bad steps, or Stamps the step with an "Execution Token".                    │
                                          └──────────────────────────────────────┬────────────────────────────────────────────────┘
                                                                                 │ [ Stamped, Approved Task ]
                                                                                 ▼

        ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ THE VAULT (Restricted Execution Room)                                                                                                  │
        │ Strict Rules: No talking to the patron. No writing to the permanent archive. Follow the Security Stamp exactly.                        │
        └────────────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────┘
                                                                         ▼

        ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ STEP 1: LOCK THE DOORS                                                                                                                 │
        │ - Lock in the tools, the budget, and the exact paperwork trail. Nothing can be swapped out now.                                        │
        └──────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────┘
                                                           │
                                                           ▼
        ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ STEP 2: FINAL DOUBLE CHECK                                                                                                             │
        │ - Verify the Security Stamp isn't forged.                                                                                              │
        │ - If it fails, stop immediately. If it passes, proceed.                                                                                │
        └──────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────┘
                                                           │
                                                      pass │   fail
                                                           ▼
        ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ STEP 3: DO THE WORK                                                                                                                    │
        │ - Read the text, run the tool, or write the answer.                                                                                    │
        │ - Record exactly what happened, how long it took, and what the result was.                                                             │
        │ - Did it work perfectly? Did it kinda break? Or did it completely fail?                                                                │
        └───────────────────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                         ┌──────────────────────┼───────────────────────────────┐
                         │                      │                               │
                         ▼                      ▼                               ▼
                  [ SUCCESS ]          [ MINOR MISTAKE ]                [ MAJOR FAILURE ]
                         │                      │                               │
                         │                      ▼                               │
                         │      ┌───────────────────────────────────────────┐   │
                         │      │ FIX IT INTERNALLY                         │   │
                         │      │ - Try a quick repair using approved tools.│   │
                         │      │ - Don't change the goal, just fix the typo│   │
                         │      └───────────────┬───────────────────────────┘   │
                         │               fixed  │      could not fix            │
                         │                      ▼                               ▼
                         │               [ Back to Work ]             [ ESCALATE FOR HELP ]
                         └───────────────────────────────────────────────┬──────┘
                                                                         │
                                                                         ▼
        ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ STEP 4: SEAL THE FOLDER                                                                                                                │
        │ - Put the final answer (or the failure notice) into a sealed folder.                                                                   │
        │ - Attach all receipts, notes, and proof of work.                                                                                       │
        └──────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────┘
                                                           │ [ Sealed Folder ]
                                                           ▼
                                                    [ Sent to Checkout Desk ]


====================================================================================================================================
[5] THE CHECKOUT DESK (Final Review & Human Intervention)
====================================================================================================================================
- The final checkpoint before handing the answer to the Patron or filing it in the permanent Archive.

                                                   │ [ Sealed Folder ]
                                                   ▼
                    ┌──────────────────────────────────────────────────────────────────────────────────────────┐
                    │ FINAL EXIT REVIEW                                                                        │
                    │ - Is the answer complete and backed by facts?                                            │
                    │ - Did the Vault Staff follow all rules and stay under budget?                            │
                    │ - Score the work: Pass, Fail, or Needs Human Manager.                                    │
                    └─────────────────────────────┬────────────────────────────────────────────────────────────┘
                                                  │
                         ┌────────────────────────┼─────────────────────────────┬───────────────────────────────┐
                         ▼                        ▼                             ▼                               ▼
               ┌───────────────────┐   ┌────────────────────┐        ┌────────────────────┐          ┌──────────────────────┐
               │ DECLINE / REDO    │   │ SEND TO MANAGER    │        │ HAND TO PATRON     │          │ FILE IN ARCHIVE      │
               │ Send it back to   │   │ (Secure Reading Rm)│        │ Answer the         │          │ Propose a permanent  │
               │ the drawing board.│   │ Too risky to send. │        │ Patron's question. │          │ update to library.   │
               └───────────────────┘   └──────────┬─────────┘        └────────────────────┘          └──────────┬───────────┘
                                                  │                                                             │
                                                  ▼                                                             ▼

      ┌──────────────────────────────────────────────────────────────────────┐      ┌─────────────────────────────────────┐
      │ THE SECURE READING ROOM (Human Manager)                              │      │ MASTER CLERK (Archive Gatekeeper)   │
      │ - A human steps in to look at the broken or risky request.           │      │ - Verifies all security stamps.     │
      │ - The human can Approve it, Reject it, or Fix the answer manually.   │      │ - The ONLY person allowed to put    │
      │                                                                      │      │   new records into the Archive.     │
      │ STRICT RULE: If the human fixes it, it MUST be sent back to the      │      └───────────────────┬─────────────────┘
      │ Security Chief (L5) to be re-stamped before it is official.          │                          │
      └─────────────────────────────────────────────┬────────────────────────┘                          ▼
                                                    │                                       ┌────────────────────┐
                      ┌─────────────────────────────┼────────────────────────────┐          │ THE ARCHIVE (L4)   │
                      ▼                             ▼                            ▼          │ Official Records   │
              [ STOP / REJECT ]           [ FIXED -> Send back     [ APPROVED -> Security   └─────────┬──────────┘
                                            to Security Chief ]      Stamps it ]                      │
                                                                                                      ▼
                                                                                              [ Request Complete ]


====================================================================================================================================
[6] THE NIGHT WATCH (Shadow Evaluation & Learning)
====================================================================================================================================
- After the library closes, the Night Watch reviews all the folders from the day.
- They cannot change today's answers, but they figure out how to make tomorrow better.

        ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ THE NIGHT WATCH (Observability & Clock)                                                                                          │
        │ - Collect all the sealed folders, complaints, and receipts from the day.                                                         │
        └──────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────┘
                                                       │
                                                       ▼
                    ┌──────────────────────────────────────────────────────────────────────────────────────┐
                    │ NIGHTLY GRADING                                                                      │
                    │ - Did we give good answers? Were they factual?                                       │
                    │ - Did we waste time using the wrong tools?                                           │
                    │ - Did we accidentally break any minor rules?                                         │
                    │ - Grade everything and flag big mistakes for the Head Librarian.                     │
                    └───────────────────────────────┬──────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
                           ┌─────────────────────────────────────────────────────────────┐
                           │ UPDATING THE LIBRARY RULES                                  │
                           │ - Figure out WHY mistakes happened (Root Cause Analysis).   │
                           │ - Draft new guidelines, better prompts, or clearer rules.   │
                           │ - Get the new rules approved by human experts.              │
                           └───────────────────────────────┬─────────────────────────────┘
                                                           │
                                                           ▼
                                         ┌───────────────────────────────────────────┐
                                         │ MASTER CLERK (Again)                      │
                                         │ Files the newly approved rules into the   │
                                         │ Archive.                                  │
                                         └──────────────────────┬────────────────────┘
                                                                │
                                                                ▼
                                         ┌───────────────────────────────────────────┐
                                         │ TOMORROW'S RULEBOOK                       │
                                         │ These new rules will apply to all future  │
                                         │ requests, making the library smarter.     │
                                         └───────────────────────────────────────────┘