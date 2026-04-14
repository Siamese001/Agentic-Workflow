import hashlib
import json

from system_learning.meta_learning.meta_learning_bus import MetaLearningChangePackage as _Impl


class MetaLearningChangePackage:
    @staticmethod
    def create(*, kind: str, payload: dict, proposal_only: bool = True):
        trace_id = hashlib.sha256(
            json.dumps(
                {"kind": kind, "payload": payload, "proposal_only": proposal_only},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()[:16]
        normalized_payload = dict(payload)
        normalized_payload.setdefault("proposal_only", proposal_only)
        return _Impl.create(trace_id=trace_id, kind=kind, payload=normalized_payload)
