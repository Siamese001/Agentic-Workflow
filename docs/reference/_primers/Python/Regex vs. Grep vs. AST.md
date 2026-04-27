┌──────────────────────────────┬──────────────────────────────┬────────────────────────────────────┐
│            REGEX             │             GREP             │                 AST                │
├──────────────────────────────┼──────────────────────────────┼────────────────────────────────────┤
│ WHAT IT IS                   │ WHAT IT IS                   │ WHAT IT IS                         │
│ Pattern language             │ Search tool                  │ Code structure parser              │
│ (analogy: recognizing        │ (analogy: clerk sent to      │ (analogy: linguist reading         │
│ letter shapes on a page)     │ scan every book for a word)  │ grammar and meaning)               │
├──────────────────────────────┼──────────────────────────────┼────────────────────────────────────┤
│ WHAT IT SEES                 │ WHAT IT SEES                 │ WHAT IT SEES                       │
│ Raw characters               │ Raw lines in files           │ Real code objects                  │
│ (analogy: letters only)      │ (analogy: lines in books)    │ (analogy: sentences + structure)   │
│                              │                              │                                    │
│ "class HierarchyAgent"       │ "class HierarchyAgent"       │ ClassDef(name="HierarchyAgent")    │
│ treated as text              │ treated as text              │ parsed as a class node             │
│ (analogy: just letters)      │ (analogy: line containing    │ (analogy: recognized as a          │
│                              │ the phrase)                  │ sentence defining a role)          │
├──────────────────────────────┼──────────────────────────────┼────────────────────────────────────┤
│ HOW IT WORKS                 │ HOW IT WORKS                 │ HOW IT WORKS                       │
│ Match pattern in string      │ Scan many files for matches  │ Parse code → build syntax tree     │
│ (analogy: compare shapes)    │ (analogy: search every page) │ (analogy: diagram the sentence)    │
│                              │                              │                                    │
│ text ──pattern match──► hit  │ files ──search──► matches    │ code ──parse──► AST tree           │
├──────────────────────────────┼──────────────────────────────┼────────────────────────────────────┤
│ EXAMPLE                      │ EXAMPLE                      │ EXAMPLE                            │
│ ^SYSTEM_LEARNING_DIR.*=      │ grep -R SYSTEM_LEARNING_DIR  │ ClassDef                           │
│                              │                              │ ├─ name: HierarchyAgent            │
│ find assignment pattern      │ search repo for string       │ └─ methods: heal_hierarchy()       │
│ (analogy: find a word        │ (analogy: search every       │ (analogy: understand the           │
│ starting a sentence)         │ book for that word)          │ role defined in the sentence)      │
├──────────────────────────────┼──────────────────────────────┼────────────────────────────────────┤
│ GOOD FOR                     │ GOOD FOR                     │ GOOD FOR                           │
│ naming patterns              │ fast repo searches           │ dependency graphs                  │
│ (analogy: spelling checks)   │ (analogy: quick library      │ (analogy: mapping relationships    │
│ lint rules                   │ lookup)                      │ between characters in a story)     │
│ quick checks                 │ debugging                    │ architecture mapping               │
│                              │ confirming references        │ refactoring safety                 │
│                              │                              │ file classification                │
├──────────────────────────────┼──────────────────────────────┼────────────────────────────────────┤
│ WEAKNESS                     │ WEAKNESS                     │ WEAKNESS                           │
│ no understanding of code     │ still text only              │ language-specific                  │
│ (analogy: sees letters       │ (analogy: finds sentences    │ (analogy: must know the language   │
│ but not meaning)             │ but not meaning)             │ grammar)                           │
│ false positives              │ can't detect structure       │ slower than text search            │
│ can't detect imports/classes │ comments look like code      │ requires parsing                   │
├──────────────────────────────┼──────────────────────────────┼────────────────────────────────────┤
│ ANALOGY                      │ ANALOGY                      │ ANALOGY                            │
│ looking for letter shapes    │ sending clerk to scan books  │ reading grammar + meaning          │
│                              │                              │                                    │
│ "find this pattern"          │ "find it everywhere"         │ "understand the sentence"          │
└──────────────────────────────┴──────────────────────────────┴────────────────────────────────────┘


POWER FOR CODE ANALYSIS
────────────────────────────────────────────────────────

Regex  <  Grep  <  AST


MEMORY TRICK
────────────────────────────────────────────────────────

Regex → finds patterns  (like spotting letter shapes)
Grep  → finds lines     (like searching every page in a library)
AST   → understands code (like reading grammar and meaning)