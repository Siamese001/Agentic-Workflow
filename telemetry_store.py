TELEMETRY_EVENTS = []


def record_event(name: str, payload: dict):
    TELEMETRY_EVENTS.append({"name": name, "payload": payload})


def get_events():
    return list(TELEMETRY_EVENTS)
