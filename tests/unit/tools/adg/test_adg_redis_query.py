from __future__ import annotations

from tools.adg.adg_redis_query import ADGRedisClient


class FakeRedis:
    def __init__(self) -> None:
        self.hashes = {
            "adg:meta": {"snapshot_id": "06282026_1945", "cache_version": "v1"},
            "adg:v1:06282026_1945:node:1": {
                "id": "1",
                "adg_name": "ADG::Module::agentic_core/foo.py",
                "resolved_path": "agentic_core/foo.py",
                "layer": "L2",
                "entity_type": "module",
            },
            "adg:v1:06282026_1945:node:2": {
                "id": "2",
                "adg_name": "ADG::Class::Foo",
                "resolved_path": "agentic_core/foo.py",
                "layer": "L2",
                "entity_type": "class",
            },
        }
        self.sets = {
            "adg:v1:06282026_1945:edge:1:imports": {"e1"},
            "adg:v1:06282026_1945:fanin:2:imports": {"e1"},
        }
        self.values = {"adg:status": "06282026_1945", "adg:v1:06282026_1945:_hot": "1"}

    def ping(self) -> bool:
        return True

    def exists(self, key: str) -> bool:
        return key in self.hashes or key in self.sets or key in self.values

    def hgetall(self, key: str) -> dict[str, str]:
        return self.hashes.get(key, {})

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def smembers(self, key: str) -> set[str]:
        return self.sets.get(key, set())

    def lrange(self, key: str, start: int, end: int) -> list[str]:  # noqa: ARG002
        return []

    def scan(self, cursor: int, match: str, count: int):  # noqa: ANN001, ARG002
        if cursor != 0:
            return 0, []
        if match == "adg:v1:06282026_1945:node:*":
            return 0, [k for k in self.hashes if k.startswith("adg:v1:06282026_1945:node:")]
        if match == "adg:v1:06282026_1945:edge:1:*":
            return 0, ["adg:v1:06282026_1945:edge:1:imports"]
        return 0, []


def test_query_helper_uses_versioned_snapshot_keys():
    client = ADGRedisClient(client=FakeRedis())

    assert client.ping() is True
    assert client.get_node("1")["resolved_path"] == "agentic_core/foo.py"
    assert client.fan_out("1", "imports") == {"e1"}
    assert client.fan_in("2", "imports") == {"e1"}
    assert client.all_edge_relations_from("1") == ["imports"]


def test_query_helper_searches_versioned_node_hashes():
    client = ADGRedisClient(client=FakeRedis())

    assert client.nodes_in_file("agentic_core/foo.py") == {"1", "2"}
    assert client.nodes_in_layer("L2") == {"1", "2"}
    assert client.search_files("foo.py") == ["agentic_core/foo.py"]
    assert [n["id"] for n in client.search_nodes("Foo", entity_type="class")] == ["2"]
