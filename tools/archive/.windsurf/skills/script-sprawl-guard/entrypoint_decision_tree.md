# Entrypoint Decision Tree

When you need to invoke a Python file or module, follow this decision tree in order.
STOP at the first matching branch.

---

## Decision Flow

```
Need to invoke a Python file or module?
│
├─► 1. Does the file have `if __name__ == "__main__":`?
│       YES → invoke directly:
│             python path/to/file.py [args]
│             DONE.
│
├─► 2. Is direct invocation blocked, AND does the module/docs
│       specify `python -m module.path` as the sanctioned entrypoint?
│       YES → invoke via -m:
│             python -m module.path [args]
│             DONE.
│
├─► 3. Does the file have no __main__ and no -m entrypoint?
│       YES → Add to the SAME canonical file:
│               def main(): ...
│               if __name__ == "__main__": main()
│             Then invoke directly (branch 1).
│             Do NOT create a new file.
│             DONE.
│
└─► 4. None of the above apply?
        → STOP. Do not create a wrapper.
          Document the blocker in evidence.
          Escalate to phase plan revision.
```

---

## Hard Rules

- Branches 1–3 are the ONLY valid paths.
- Branch 4 is a STOP — not a license to create a wrapper.
- A new file is NEVER the answer to an invocation problem.
- If you find yourself writing `import X; X.run()` in a new file → STOP, use branch 3.
