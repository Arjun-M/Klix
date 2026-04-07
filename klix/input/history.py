"""Session-backed history helpers for prompt_toolkit.

Klix keeps command history per session while letting prompt_toolkit handle the
actual arrow-key navigation. This adapter applies Klix-specific policies such as
skipping empty values, avoiding duplicate consecutive entries, and enforcing an
optional maximum size.
"""

from __future__ import annotations

from typing import Iterable, Optional

from prompt_toolkit.history import History


class SessionHistory(History):
    def __init__(self, entries: Optional[list[str]] = None, max_size: Optional[int] = None) -> None:
        super().__init__()
        self._entries = entries if entries is not None else []
        self.max_size = max_size
        self._trim_to_max_size()
        self._loaded = True
        self._sync_loaded_strings()

    def _trim_to_max_size(self) -> None:
        if self.max_size is None:
            return
        if self.max_size <= 0:
            self._entries.clear()
            return
        if len(self._entries) > self.max_size:
            overflow = len(self._entries) - self.max_size
            del self._entries[:overflow]

    def _sync_loaded_strings(self) -> None:
        self._loaded_strings = list(reversed(self._entries))

    def _normalize(self, string: str) -> str:
        return string.rstrip("\n")

    def _should_store(self, string: str) -> bool:
        if not string.strip():
            return False
        if self.max_size is not None and self.max_size <= 0:
            return False
        if self._entries and self._entries[-1] == string:
            return False
        return True

    def load_history_strings(self) -> Iterable[str]:
        yield from reversed(self._entries)

    def store_string(self, string: str) -> None:
        cleaned = self._normalize(string)
        if not self._should_store(cleaned):
            return

        self._entries.append(cleaned)
        self._trim_to_max_size()
        self._sync_loaded_strings()

    def append_string(self, string: str) -> None:
        self.store_string(string)
