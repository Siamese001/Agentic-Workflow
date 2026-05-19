# One-spine no-two-path proof (Wave 9)

**STATUS: PASS**

## Global claims

- **1** proof_pool cannot run before U0/L1/L0: PASS
- **2** PA cannot consume raw proof_pool directly: PASS
- **3** L2 cannot run without compiled prompt + FEC: PASS
- **4** Exit cannot run without SealedL2: PASS
- **5** RuntimeExhaust after ExitDispositionReceipt: PASS
- **6** L6 after RuntimeExhaustBundle: PASS
- **7** fixture/dev cannot claim product certification: PASS
- **8** missing chain artifact blocks certification: PASS
- **9** section X3 mirror only: PASS
- **10** no product-visible second pipeline for --section: PASS

two_paths_found=true at Wave 1: Path A=section CLI, Path B=integrated R4 whole-run. W9 proves Path A is the sole product-visible --section pipeline with canonical spine artifacts; Path B is not invoked by python -m apps_rg --section <lane>.
