import uuid
from datetime import datetime


def generate_session_id() -> str:
    return uuid.uuid4().hex


def generate_request_id() -> str:
    return uuid.uuid4().hex


def group_sessions_by_time(sessions: list[dict]) -> list[dict]:
    now = datetime.now()
    today = now.date()
    groups: dict[str, list] = {"今天": [], "最近30天": [], "最近一年": [], "更早": []}

    for s in sessions:
        delta = (today - s["update_time"].date()).days
        if delta == 0:
            groups["今天"].append(s)
        elif delta <= 30:
            groups["最近30天"].append(s)
        elif delta <= 365:
            groups["最近一年"].append(s)
        else:
            groups["更早"].append(s)

    return [{"group": k, "sessions": v} for k, v in groups.items() if v]
