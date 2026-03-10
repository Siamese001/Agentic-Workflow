"""Generate full ADG with entities and relations in the comprehensive format."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
from agentic_core.adg.extraction.graph_persister import persist_scan_result
from agentic_core.adg.client.mcp_client import ADGMCPClient


def generate_full_adg(output_path: Path) -> None:
    """Generate full ADG with entities, relations, and metadata."""
    print("[ADG] Starting full scan...")

    # Create scanner and run full scan
    scanner = ADGStaticScanner(repo_root=ROOT)
    result = scanner.scan(commit_sha="")

    print(f"[ADG] Scan complete. Digest: {result.digest}")
    print(f"[ADG] Modules: {len(result.modules)}")
    print(f"[ADG] Edges: {len(result.edges)}")

    # Create MCP client and persist the scan result
    print("[ADG] Persisting to graph...")
    client = ADGMCPClient(use_mcp=False)
    persist_scan_result(result, client)

    # Read back the full graph
    print("[ADG] Reading graph...")
    graph_data = client.read_graph()

    # Build comprehensive output format
    entities_with_metadata = []
    for entity in graph_data["entities"]:
        # Parse observations to extract metadata
        obs_dict = {}
        for obs in entity.get("observations", []):
            if ":" in obs:
                key, value = obs.split(":", 1)
                obs_dict[key] = value

        entity_with_meta = {
            "adg_name": entity["name"],
            "entity_type": entity["entityType"],
            "identity_kind": "repo_module" if entity["entityType"] == "module" else "symbol",
            "confidence": "HIGH",
            "observations": entity.get("observations", []),
        }

        # Add layer if present
        if "layer" in obs_dict:
            entity_with_meta["layer"] = obs_dict["layer"]

        # Add path if present
        if "path" in obs_dict:
            entity_with_meta["resolved_path"] = obs_dict["path"]

        entities_with_metadata.append(entity_with_meta)

    # Calculate artifact digest
    canonical_str = json.dumps(
        {
            "entities": sorted([e["adg_name"] for e in entities_with_metadata]),
            "relations": sorted([(r["from"], r["relationType"], r["to"]) for r in graph_data["relations"]])
        },
        sort_keys=True
    )
    artifact_digest = hashlib.sha256(canonical_str.encode()).hexdigest()

    # Build final output
    output = {
        "artifact_digest": artifact_digest,
        "scanner_digest": result.digest,
        "schema_version": "2.0",
        "commit_sha": "",
        "entities": entities_with_metadata,
        "relations": graph_data["relations"],
        "blind_spots": {
            "parse_failure_count": 0,
            "parse_failure_files": [],
            "dynamic_import_count": 0,
            "dynamic_import_locations": [],
            "star_import_count": 0,
            "star_import_locations": [],
        },
        "structural_metrics": {
            "total_modules": len(result.modules),
            "total_edges": len(result.edges),
            "total_entities": len(entities_with_metadata),
            "total_relations": len(graph_data["relations"]),
        },
        "unresolved_imports": [],
        "identity_health": {
            "total_entities": len(entities_with_metadata),
            "high_confidence": len([e for e in entities_with_metadata if e.get("confidence") == "HIGH"]),
        },
    }

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[ADG] Writing {output_path}...")
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[ADG] Done. {output_path.name} ({size_mb:.1f} MB)")
    print(f"      entities={len(entities_with_metadata)}  relations={len(graph_data['relations'])}")
    print(f"      artifact_digest={artifact_digest[:16]}...")


def main() -> None:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = ROOT / "artifacts" / "adg" / f"adg_full_{ts}.json"
    generate_full_adg(output_path)


if __name__ == "__main__":
    main()
