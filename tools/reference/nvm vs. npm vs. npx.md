┌─────────────────────────────────────────────────────────────────────────────┐
│                      COMPARISON: nvm vs npm vs npx                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┬─────────────────────────┬─────────────────────────┐
│           nvm           │           npm           │           npx           │
│ (Node Version Manager)  │ (Node Package Manager)  │ (Node Package eXecute)  │
├─────────────────────────┼─────────────────────────┼─────────────────────────┤
│ PURPOSE:                │ PURPOSE:                │ PURPOSE:                │
│ Manages which version   │ Downloads and installs  │ Executes Node packages  │
│ of Node.js is active    │ packages onto disk for  │ without requiring a     │
│ on your machine.        │ your application.       │ global install first.   │
├─────────────────────────┼─────────────────────────┼─────────────────────────┤
│ FLOWCHART:              │ FLOWCHART:              │ FLOWCHART:              │
│                         │                         │                         │
│     [Start Task]        │     [Need Package]      │    [Need to Run CMD]    │
│          │              │           │             │            │            │
│          ▼              │           ▼             │            ▼            │
│  Check Node Version     │  Run: npm install X     │       Run: npx X        │
│          │              │           │             │            │            │
│          ▼              │           ▼             │            ▼            │
│  Is correct version     │  Downloads package      │  Is X installed locally?│
│  active?                │  from npm registry      │    ┌──────┴──────┐      │
│   ┌──────┴──────┐       │           │             │   YES            NO     │
│  YES            NO      │           ▼             │    │             │      │
│   │             │       │  Saves to node_modules/ │    ▼             ▼      │
│   │             ▼       │           │             │  Runs X     Downloads X │
│   │        nvm use 20   │           ▼             │             temporarily │
│   │             │       │  Updates package.json   │                  │      │
│   ▼             ▼       │           │             │                  ▼      │
│  Ready to run scripts   │           ▼             │                Runs X   │
│                         │  Package is ready       │                  │      │
│                         │  to be imported into    │                  ▼      │
│                         │  your code.             │             Deletes X   │
│                         │                         │                         │
├─────────────────────────┼─────────────────────────┼─────────────────────────┤
│ PRIMARY USE CASE:       │ PRIMARY USE CASE:       │ PRIMARY USE CASE:       │
│ Switching engines       │ Adding code dependency  │ Running one-off CLI     │
│ between older and newer │ to build your software  │ tools (like scaffolding │
│ projects.               │ (e.g., React, Express). │ or formatting scripts). │
└─────────────────────────┴─────────────────────────┴─────────────────────────┘