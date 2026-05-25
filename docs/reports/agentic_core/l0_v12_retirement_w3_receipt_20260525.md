# L0 v12 retirement W3 receipt

**Plan:** [l0-routing-v15-only-cutover-c9e2f1](../../.cursor/plans/l0-routing-v15-only-cutover-c9e2f1.md)

## Archived (production hot path removed)

| Former path | New path |
|-------------|----------|
| `reasoning/v12_route_selector.py` | [`_archive/v12/reasoning/v12_route_selector.py`](../../../agentic_core/L0_routing/_archive/v12/reasoning/v12_route_selector.py) |
| `reasoning/cold_start_safeguard.py` | [`_archive/v12/reasoning/cold_start_safeguard.py`](../../../agentic_core/L0_routing/_archive/v12/reasoning/cold_start_safeguard.py) |
| `config/fallback_chains_loader.py` | [`_archive/v12/config/fallback_chains_loader.py`](../../../agentic_core/L0_routing/_archive/v12/config/fallback_chains_loader.py) |

## Retained for replay

- `types/route_contract_v12_extensions.py`
- `types/route_contract_v15_bridge.py` (`v12_to_v15`)

## v15 SSOT

- [`config/routing/fallback_chains_v15.yaml`](../../../config/routing/fallback_chains_v15.yaml)
- `v15_route_selector._default_fallback_for` → `get_fallback_chain_v15`

## Gates

```bash
python ops_scripts/ci/check_l0_v15_no_v12_hotpath.py
python ops_scripts/ci/check_l0_parent_invariants.py
```
