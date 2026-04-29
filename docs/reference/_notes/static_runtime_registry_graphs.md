┌──────────────────────────────┬──────────────────────────────┬──────────────────────────────┐
│ SHELF CATALOG                │ CHECKOUT LOG                 │ LIBRARY PERMISSION LIST       │
│ Static Graph                 │ Runtime Graph                │ Registry Graph                │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Question it answers:         │ Question it answers:         │ Question it answers:          │
│                              │                              │                               │
│ "What books are sitting      │ "What books were actually    │ "What books is this person    │
│ on the shelf or mentioned    │ borrowed today?"             │ allowed to borrow?"           │
│ in the catalog?"             │                              │                               │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Simple flowchart:            │ Simple flowchart:            │ Simple flowchart:             │
│                              │                              │                               │
│ Catalog mentions book        │ Person visits library        │ Person presents card          │
│          │                   │          │                   │          │                    │
│          ▼                   │          ▼                   │          ▼                    │
│ Check shelf                  │ Check checkout receipt       │ Check permission rules        │
│          │                   │          │                   │          │                    │
│          ▼                   │          ▼                   │          ▼                    │
│ Book found?                  │ Book borrowed?               │ Borrowing allowed?            │
│    │        │                │    │        │                │    │        │                 │
│    ▼        ▼                │    ▼        ▼                │    ▼        ▼                 │
│ Trusted   Warning            │ Proof     No proof           │ May use   Blocked             │
│ record    not proof          │ of use    of use             │          by rule              │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Example:                     │ Example:                     │ Example:                      │
│                              │                              │                               │
│ The catalog says the library │ The checkout desk says Amit  │ Amit's library card says he   │
│ has books about Search,      │ borrowed the Search book     │ may borrow Search books,      │
│ Email, and Calculator.       │ today.                       │ but not Email books.          │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ What it proves:              │ What it proves:              │ What it proves:               │
│                              │                              │                               │
│ The book is listed or        │ The book was actually used   │ The person is allowed or not  │
│ reachable in the library.    │ in this visit.               │ allowed to use that book.     │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ What it does NOT prove:      │ What it does NOT prove:      │ What it does NOT prove:       │
│                              │                              │                               │
│ It does not prove anyone     │ It does not prove every book │ It does not prove the person  │
│ borrowed the book.           │ in the library exists.       │ actually borrowed the book.   │
│                              │                              │                               │
│ It does not prove the person │ It does not prove what the   │ It does not prove the book    │
│ was allowed to borrow it.    │ person was allowed to use.   │ exists on the shelf.          │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Bad mistake:                 │ Bad mistake:                 │ Bad mistake:                  │
│                              │                              │                               │
│ "The Email book is listed,   │ "Amit did not borrow Email   │ "Amit is allowed to borrow   │
│ so Amit borrowed Email."     │ today, so Email does not     │ Search, so he definitely     │
│                              │ exist."                     │ borrowed Search."            │
├──────────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ Correct statement:           │ Correct statement:           │ Correct statement:            │
│                              │                              │                               │
│ "Email is listed, but we     │ "Amit did not borrow Email   │ "Amit may borrow Search,     │
│ need the checkout log to     │ during this visit."          │ but check the checkout log    │
│ prove it was used."          │                              │ to prove he used it."        │
└──────────────────────────────┴──────────────────────────────┴──────────────────────────────┘