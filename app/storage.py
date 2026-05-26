import threading
from typing import Optional

_store: dict[str, dict] = {}
_lock = threading.Lock()


def save(snippet_id: str, data: dict) -> None:
    with _lock:
        _store[snippet_id] = data


def get(snippet_id: str) -> Optional[dict]:
    with _lock:
        return _store.get(snippet_id)


def update(snippet_id: str, partial: dict) -> bool:
    with _lock:
        if snippet_id not in _store:
            return False
        _store[snippet_id].update(partial)
        return True


def exists(snippet_id: str) -> bool:
    with _lock:
        return snippet_id in _store
