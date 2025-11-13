# Clean Refactor Preparation

Use the `scripts/prepare_clean_refactor.sh` helper to guarantee a reproducible baseline
before beginning a large refactor. The script performs three core actions:

1. Verifies the working tree is clean (unless you opt into `--force`).
2. Fetches the latest history from the selected remote/branch and hard resets to it when available.
3. Deletes all ignored/untracked artifacts so new runs start from scratch.

## Usage

```bash
./scripts/prepare_clean_refactor.sh
```

Key options:

- `--remote <name>` – override the remote to fetch from (`origin` by default).
- `--branch <name>` – reset to a specific branch (`git rev-parse --abbrev-ref HEAD` by default).
- `--force` – discard local modifications when you are sure they are no longer needed.

If the requested remote branch does not exist the script will skip the hard reset while still
cleaning the working tree, making it safe to run even in detached HEAD states.

## Recommended workflow

1. Run the script to guarantee a clean baseline.
2. Reinstall any development dependencies or virtual environments as needed.
3. Execute the quality gates (`python -m compileall`, schema validation, `pytest`) to ensure the repo passes before refactoring.
4. Begin the refactor with confidence that no historical artifacts influence the diff.
