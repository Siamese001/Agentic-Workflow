"""ADG Redis analysis: HITL mixin integration with system_learning confidence infrastructure."""

import redis


def query_redis():
    """Query ADG Redis cache for HITL and system_learning integration points."""

    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    # Check cache status
    meta = r.hgetall("adg:meta")
    print("=" * 80)
    print("ADG CACHE STATUS")
    print("=" * 80)
    print(f"Timestamp: {meta.get('timestamp')}")
    print(f"Nodes: {meta.get('node_count')}")
    print(f"Edges: {meta.get('edge_count')}")
    print()

    # Query 1: Find HITLMixin node
    print("=" * 80)
    print("QUERY 1: HITLMixin Node")
    print("=" * 80)
    hitl_nodes = []
    for key in r.scan_iter("adg:node:*"):
        node = r.hgetall(key)
        if "HITL" in node.get("adg_name", ""):
            hitl_nodes.append(node)
            print(f"  {node.get('adg_name')} | {node.get('entity_type')} | {node.get('layer')}")
            print(f"    Path: {node.get('resolved_path')}")
    print(f"Found {len(hitl_nodes)} HITL nodes\n")

    # Query 2: Find system_learning confidence/scoring classes
    print("=" * 80)
    print("QUERY 2: System Learning Confidence/Scoring Classes")
    print("=" * 80)
    sl_confidence_nodes = []
    sl_layer_keys = r.smembers("adg:nodes:by_layer:L_SL")
    for node_id in sl_layer_keys:
        node = r.hgetall(f"adg:node:{node_id}")
        adg_name = node.get("adg_name", "")
        if any(pattern in adg_name for pattern in ["Confidence", "Scorer", "Score"]):
            if node.get("entity_type") == "class":
                sl_confidence_nodes.append(node)
                print(f"  {adg_name}")
                print(f"    Type: {node.get('entity_type')} | Path: {node.get('resolved_path')}")
    print(f"Found {len(sl_confidence_nodes)} confidence/scoring classes\n")

    # Query 3: Find system_learning adapter patterns
    print("=" * 80)
    print("QUERY 3: System Learning Adapter Patterns")
    print("=" * 80)
    sl_adapter_nodes = []
    for node_id in sl_layer_keys:
        node = r.hgetall(f"adg:node:{node_id}")
        adg_name = node.get("adg_name", "")
        if "Adapter" in adg_name and node.get("entity_type") == "class":
            sl_adapter_nodes.append(node)
            print(f"  {adg_name}")
            print(f"    Path: {node.get('resolved_path')}")
    print(f"Found {len(sl_adapter_nodes)} adapter classes\n")

    # Query 4: Find system_learning proposer patterns
    print("=" * 80)
    print("QUERY 4: System Learning Proposer Patterns")
    print("=" * 80)
    sl_proposer_nodes = []
    for node_id in sl_layer_keys:
        node = r.hgetall(f"adg:node:{node_id}")
        adg_name = node.get("adg_name", "")
        if "Proposer" in adg_name and node.get("entity_type") == "class":
            sl_proposer_nodes.append(node)
            print(f"  {adg_name}")
            print(f"    Path: {node.get('resolved_path')}")
    print(f"Found {len(sl_proposer_nodes)} proposer classes\n")

    # Query 5: Find Approval/Risk types
    print("=" * 80)
    print("QUERY 5: HITL Approval/Risk Types")
    print("=" * 80)
    approval_nodes = []
    for key in r.scan_iter("adg:node:*"):
        node = r.hgetall(key)
        adg_name = node.get("adg_name", "")
        if any(pattern in adg_name for pattern in ["Approval", "RiskLevel"]):
            approval_nodes.append(node)
            print(f"  {adg_name} | {node.get('entity_type')} | {node.get('layer')}")
    print(f"Found {len(approval_nodes)} approval/risk types\n")

    # Query 6: Find system_learning outcome/feedback patterns
    print("=" * 80)
    print("QUERY 6: System Learning Outcome/Feedback Patterns")
    print("=" * 80)
    sl_outcome_nodes = []
    for node_id in sl_layer_keys:
        node = r.hgetall(f"adg:node:{node_id}")
        adg_name = node.get("adg_name", "")
        if any(pattern in adg_name for pattern in ["Outcome", "Feedback", "Attempt"]):
            if node.get("entity_type") == "class":
                sl_outcome_nodes.append(node)
                print(f"  {adg_name}")
                print(f"    Type: {node.get('entity_type')} | Path: {node.get('resolved_path')}")
    print(f"Found {len(sl_outcome_nodes)} outcome/feedback classes\n")

    # Query 7: Find ChangePackage patterns (for recalibration proposals)
    print("=" * 80)
    print("QUERY 7: System Learning ChangePackage Patterns")
    print("=" * 80)
    change_package_nodes = []
    for node_id in sl_layer_keys:
        node = r.hgetall(f"adg:node:{node_id}")
        adg_name = node.get("adg_name", "")
        if "ChangePackage" in adg_name or "Change" in adg_name:
            if node.get("entity_type") == "class":
                change_package_nodes.append(node)
                print(f"  {adg_name}")
                print(f"    Path: {node.get('resolved_path')}")
    print(f"Found {len(change_package_nodes)} change package classes\n")

    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

    return {
        "hitl_nodes": hitl_nodes,
        "sl_confidence_nodes": sl_confidence_nodes,
        "sl_adapter_nodes": sl_adapter_nodes,
        "sl_proposer_nodes": sl_proposer_nodes,
        "approval_nodes": approval_nodes,
        "sl_outcome_nodes": sl_outcome_nodes,
        "change_package_nodes": change_package_nodes,
    }


if __name__ == "__main__":
    results = query_redis()
