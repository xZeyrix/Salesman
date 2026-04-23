import hashlib
import inspect
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, Optional


class Cassette:
    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self.base_dir = base_dir or Path(__file__).resolve().parent / "cassettes"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.mode = os.getenv("TEST_CACHE_MODE", "replay").lower()

    def _key_path(self, name: str, payload: Dict[str, Any]) -> Path:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        return self.base_dir / f"{name}-{digest}.json"

    def _read(self, path: Path) -> Any:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data["value"]

    def _write(self, path: Path, payload: Dict[str, Any], value: Any) -> None:
        payload_wrapper = {"payload": payload, "value": value}
        path.write_text(
            json.dumps(payload_wrapper, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get_or_set(
        self,
        name: str,
        payload: Dict[str, Any],
        producer: Callable[[], Any],
    ) -> Any:
        path = self._key_path(name, payload)
        if path.exists():
            return self._read(path)
        if self.mode == "replay":
            raise FileNotFoundError(
                f"Cache missing for '{name}'. Run with TEST_CACHE_MODE=record."
            )
        value = producer()
        if inspect.isawaitable(value):
            raise RuntimeError("Use async_get_or_set for awaitable producers.")
        self._write(path, payload, value)
        return value

    async def async_get_or_set(
        self,
        name: str,
        payload: Dict[str, Any],
        producer: Callable[[], Any],
    ) -> Any:
        path = self._key_path(name, payload)
        if path.exists():
            return self._read(path)
        if self.mode == "replay":
            raise FileNotFoundError(
                f"Cache missing for '{name}'. Run with TEST_CACHE_MODE=record."
            )
        value = producer()
        if inspect.isawaitable(value):
            value = await value
        self._write(path, payload, value)
        return value
