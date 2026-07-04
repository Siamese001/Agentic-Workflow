# Hugging Face Public Intelligence Refresh

This Codex automation owns the weekly public Hugging Face intelligence pull.

## Schedule

`RRULE:FREQ=WEEKLY;BYHOUR=8;BYMINUTE=0;BYDAY=FR`

## Source

Public Hugging Face metadata only:

- models
- datasets
- Spaces
- daily papers where reachable by the scanner

No Hugging Face token, Jobs credit, model-weight download, or dataset download is required.

## Command

```powershell
python -m pip install --upgrade pip
python -m pip install huggingface_hub requests python-dateutil
$env:SCAN_DAYS = "7"
$env:TOP_N = "10"
python scripts/hf_public_intel_scan.py
```

## Outputs

- `docs/intelligence/huggingface/latest_agentic_public_signal.md`
- `docs/intelligence/huggingface/archive/<date>.md`
- `data/huggingface/latest_agentic_public_signal.json`
- `data/huggingface/archive/<date>.json`

## Publication

Generated diffs are published through a PR from `codex-hf-public-intel-automation` to `main`. Direct main pushes are not allowed.
