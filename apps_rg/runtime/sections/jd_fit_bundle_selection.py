"""JD-fit role-episode bundle selection for experience lanes.

Shared by the unify_/ibm_ bullet formatters. Ranks an employer's section-eligible
role-episode bundles by their bound skills' functional pillar weights under the
JD-resolved projection profile, keeps the top-N (= number of bullet slots), and
preserves each retained bundle's original slot so base-bullet metric coupling is
unchanged. Newly-promoted bundles (e.g. a partner/co-sell bundle for a partnerships
JD) fill the slot(s) freed by bundles that dropped out of the top-N.

Falls back to the static default map when no profile is resolvable, so an engineering
JD (partner pillars deprioritized → partner bundle ranks last → drops) reproduces the
prior static behavior exactly: zero regression off the partnerships path.
"""
from __future__ import annotations

from typing import Any, Callable

# Mirrors track_weighted_graph_expansion functional-weight defaults.
DEFAULT_FUNCTIONAL_PILLAR_WEIGHT = 0.55
DEPRIORITIZED_PILLAR_WEIGHT = 0.10


def profile_pillar_weights(
    role_family_key: str, graph: dict[str, Any]
) -> tuple[dict[str, float], set[str]]:
    """(pillar_id -> weight, deprioritized pillar ids) for a projection profile."""
    if not role_family_key:
        return {}, set()
    profile = (graph.get("role_family_projection_profiles") or {}).get(role_family_key) or {}
    weights = {
        str(p.get("pillar_id")): float(p.get("weight") or 0.0)
        for p in (profile.get("top_weighted_pillars") or [])
        if isinstance(p, dict) and p.get("pillar_id")
    }
    deprio = {str(x) for x in (profile.get("deprioritize_pillars") or [])}
    return weights, deprio


def bundle_jd_fit_score(
    bundle: dict[str, Any],
    pillar_weights: dict[str, float],
    deprio: set[str],
    skill_index: dict[str, dict[str, Any]],
) -> float:
    """Mean functional pillar weight of a bundle's bound skills under the active profile."""
    sids = [str(s) for s in (bundle.get("graph_skill_node_ids") or [])]
    if not sids:
        return 0.0
    total = 0.0
    for sid in sids:
        pillar = str((skill_index.get(sid) or {}).get("pillar") or "")
        if pillar in deprio:
            total += DEPRIORITIZED_PILLAR_WEIGHT
        else:
            total += pillar_weights.get(pillar, DEFAULT_FUNCTIONAL_PILLAR_WEIGHT)
    return total / len(sids)


def resolve_jd_fit_slot_bundle_map(
    *,
    role_family_key: str,
    default_map: dict[str, str],
    slot_ids: tuple[str, ...],
    bundles_for_section: Callable[[str], list[dict[str, Any]]],
    section_id: str,
    skill_index: dict[str, dict[str, Any]],
    graph: dict[str, Any],
) -> dict[str, str]:
    """Generic JD-fit slot→bundle map; static default when no profile resolvable."""
    pillar_weights, deprio = profile_pillar_weights(role_family_key, graph)
    if not pillar_weights:
        return dict(default_map)
    eligible = bundles_for_section(section_id)
    ranked = sorted(
        eligible,
        key=lambda b: (
            -bundle_jd_fit_score(b, pillar_weights, deprio, skill_index),
            str(b.get("role_episode_bundle_id")),
        ),
    )
    top_ids = [str(b.get("role_episode_bundle_id")) for b in ranked[: len(slot_ids)]]
    top_set = set(top_ids)
    retained = {slot: bid for slot, bid in default_map.items() if bid in top_set}
    freed = [slot for slot in slot_ids if slot not in retained]
    promoted = [bid for bid in top_ids if bid not in default_map.values()]
    new_map = dict(retained)
    for slot, bid in zip(freed, promoted):
        new_map[slot] = bid
    for slot in slot_ids:
        new_map.setdefault(slot, default_map[slot])
    return new_map


__all__ = [
    "DEFAULT_FUNCTIONAL_PILLAR_WEIGHT",
    "DEPRIORITIZED_PILLAR_WEIGHT",
    "bundle_jd_fit_score",
    "profile_pillar_weights",
    "resolve_jd_fit_slot_bundle_map",
]
