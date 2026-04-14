"""
Focused: RLHF optimizer + SFT node details from Redis hot cache.
"""

import os

import redis
from tqdm import tqdm


def get_redis() -> redis.Redis:
    host = os.environ.get("REDIS_HOST", "localhost")
    port = int(os.environ.get("REDIS_PORT", "6379"))
    db = int(os.environ.get("REDIS_DB", "0"))
    client: redis.Redis = redis.Redis(
        host=host,
        port=port,
        db=db,
        socket_connect_timeout=5,
        socket_timeout=5,
    )
    client.ping()
    return client


def iter_keys(r: redis.Redis, pattern: str) -> list[bytes]:
    return list(r.scan_iter(pattern, count=1000))


def get_nodes_for_file(r: redis.Redis, filepath: str) -> list[dict[str, str]]:
    nodes = []
    for nid in r.sscan_iter(f"adg:nodes:by_file:{filepath}"):
        data = r.hgetall(f"adg:node:{nid.decode()}")
        if data:
            nodes.append({k.decode(): v.decode() for k, v in data.items()})
    return nodes


def node_has_covers(r: redis.Redis, node_id: str) -> bool:
    return bool(r.smembers(f"adg:edge:in:{node_id}:covers"))


RLHF_FILES = [
    "system_learning/engines/rlhf_optimizer.py",
    "system_learning/engines/rlhf_optimizer_impl.py",
    "system_learning/engines/governance_reward_model.py",
]


def main() -> None:
    r = get_redis()

    print("=== RLHF OPTIMIZER + REWARD MODEL NODE DETAILS ===")
    for fp in tqdm(RLHF_FILES, desc="Processing", unit="item"):
        nodes = get_nodes_for_file(r, fp)
        print(f"\n[{fp}]  ({len(nodes)} nodes)")
        for n in tqdm(nodes, desc="Processing", unit="item"):
            nid = n.get("id", "?")
            layer = n.get("layer", "?")
            etype = n.get("entity_type", "?")
            name = n.get("adg_name", "?").replace("ADG::Module::", "").replace("ADG::Symbol::", "")
            covered = node_has_covers(r, nid)
            # outbound edges
            edge_keys = iter_keys(r, f"adg:edge:{nid}:*")
            rels = sorted({k.decode().split(":")[-1] for k in edge_keys})
            # importers
            importers_raw = r.smembers(f"adg:edge:in:{nid}:imports")
            importer_layers = []
            for imp in tqdm(importers_raw, desc="Processing", unit="item"):
                d = r.hgetall(f"adg:node:{imp.decode()}")
                if d:
                    lyr = d.get(b"layer", b"?").decode()
                    nm = (
                        d.get(b"adg_name", b"?")
                        .decode()
                        .replace("ADG::Module::", "")
                        .replace("ADG::Symbol::", "")
                    )
                    importer_layers.append(f"[{lyr}] {nm}")
            print(f"  [{layer}] {name} | {etype} | covered={covered}")
            if rels:
                print(f"    edges: {rels}")
            if importer_layers:
                print(f"    imported_by: {importer_layers}")

    # Check meta_learning_pipeline.py — is RLHFOptimizer wired there?
    print("\n=== meta_learning_pipeline.py details ===")
    for n in tqdm(
        get_nodes_for_file(r, "system_learning/pipelines/meta_learning_pipeline.py"),
        desc="Processing",
        unit="item",
    ):
        nid = n.get("id", "?")
        layer = n.get("layer", "?")
        etype = n.get("entity_type", "?")
        name = n.get("adg_name", "?").replace("ADG::Module::", "").replace("ADG::Symbol::", "")
        covered = node_has_covers(r, nid)
        edge_keys = iter_keys(r, f"adg:edge:{nid}:*")
        rels = sorted({k.decode().split(":")[-1] for k in edge_keys})
        # What does it import?
        imports_out = r.smembers(f"adg:edge:{nid}:imports")
        import_names = []
        for imp in tqdm(imports_out, desc="Processing", unit="item"):
            d = r.hgetall(f"adg:node:{imp.decode()}")
            if d:
                lyr = d.get(b"layer", b"?").decode()
                nm = (
                    d.get(b"adg_name", b"?")
                    .decode()
                    .replace("ADG::Module::", "")
                    .replace("ADG::Symbol::", "")
                )
                if "UNKNOWN" not in lyr:
                    import_names.append(f"[{lyr}] {nm}")
        print(f"  [{layer}] {name} | {etype} | covered={covered}")
        if rels:
            print(f"    edges: {rels}")
        if import_names:
            print(f"    imports: {import_names}")

    # Check meta_learning_bus.py — uses GovernanceRewardModel
    print("\n=== meta_learning_bus.py details ===")
    for n in tqdm(
        get_nodes_for_file(r, "system_learning/engines/meta_learning_bus.py"), desc="Processing", unit="item"
    ):
        nid = n.get("id", "?")
        layer = n.get("layer", "?")
        etype = n.get("entity_type", "?")
        name = n.get("adg_name", "?").replace("ADG::Module::", "").replace("ADG::Symbol::", "")
        covered = node_has_covers(r, nid)
        edge_keys = iter_keys(r, f"adg:edge:{nid}:*")
        rels = sorted({k.decode().split(":")[-1] for k in edge_keys})
        imports_out = r.smembers(f"adg:edge:{nid}:imports")
        import_names = []
        for imp in tqdm(imports_out, desc="Processing", unit="item"):
            d = r.hgetall(f"adg:node:{imp.decode()}")
            if d:
                lyr = d.get(b"layer", b"?").decode()
                nm = (
                    d.get(b"adg_name", b"?")
                    .decode()
                    .replace("ADG::Module::", "")
                    .replace("ADG::Symbol::", "")
                )
                if "UNKNOWN" not in lyr:
                    import_names.append(f"[{lyr}] {nm}")
        print(f"  [{layer}] {name} | {etype} | covered={covered}")
        if rels:
            print(f"    edges: {rels}")
        if import_names:
            print(f"    imports (non-unknown): {import_names[:10]}")

    # What is SFT-absent? Scan for any sft/finetune/train* files
    print("\n=== SFT / fine-tune / trainer scan (Redis file index) ===")
    for pattern in tqdm(
        [
            "*sft*",
            "*fine_tun*",
            "*finetune*",
            "*trainer*",
            "*training*",
            "*feedback_collect*",
            "*human_feedback*",
            "*annotation*",
        ],
        desc="Processing",
        unit="item",
    ):
        keys = iter_keys(r, f"adg:nodes:by_file:{pattern}")
        if keys:
            for k in keys:
                print(f"  FOUND: {k.decode()}")
        else:
            print(f"  ABSENT: {pattern}")

    print("\nDONE")


if __name__ == "__main__":
    main()
