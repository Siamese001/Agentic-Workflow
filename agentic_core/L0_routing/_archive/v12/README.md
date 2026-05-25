# v12 L0 routing archive

Retired from production hot path (plan `l0-routing-v15-only-cutover-c9e2f1` W3).

| Module | Replacement |
|--------|-------------|
| `reasoning/v12_route_selector.py` | `reasoning/v15_route_selector.select_route_v15` |
| `config/fallback_chains_loader.py` | `config/fallback_chains_loader_v15.get_fallback_chain_v15` |
| `reasoning/cold_start_safeguard.py` | Inline in `v15_route_selector` |

`route_contract_v12_extensions` and `route_contract_v15_bridge.v12_to_v15` remain under `types/` for historical replay manifests.
