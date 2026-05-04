from typing import Any


class ToolResultHolder:
    _results: dict[str, dict[str, Any]] = {}

    @classmethod
    def put(cls, request_id: str, key: str, value: Any):
        if request_id not in cls._results:
            cls._results[request_id] = {}
        cls._results[request_id][key] = value

    @classmethod
    def get(cls, request_id: str) -> dict[str, Any]:
        return cls._results.get(request_id, {})

    @classmethod
    def remove(cls, request_id: str):
        cls._results.pop(request_id, None)
