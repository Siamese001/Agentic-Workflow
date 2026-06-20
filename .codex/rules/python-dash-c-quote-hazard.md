# `python -c "..."` Quote-Hazard Ban — stub

> On-demand (plan `always-on-rule-surface-cut-c7f3a1`); enforcement unchanged (blocks at exec). **Invariant:** never run `python -c "..."` in a shell command whose body has escaped/triple double-quotes — on Windows/pwsh the shell mis-parses it, leaves the string unterminated, and the turn hangs forever (no Python `timeout=` can rescue a shell-level hang). Use `Grep`/`Read`, a temp `.py` file, or single-quote the body. Constitutional §0/§14/§26. Enforced: `pre_run_gate.py` `_check_python_dash_c_quote_hazard()`.
