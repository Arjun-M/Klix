import os
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Type, Any, Optional

from .session import SessionState


class SessionStateManager:
    def __init__(self, app_name: str, state_schema: Type[SessionState], event_bus: Any, persist_enabled: bool):
        self.app_name = app_name
        self.state_schema = state_schema
        self.event_bus = event_bus
        self.persist_enabled = persist_enabled

    def _get_session_dir(self) -> Path:
        return Path(os.path.expanduser(f"~/.klix/sessions/{self.app_name}"))

    def _get_session_file(self, session_id: str) -> Path:
        return self._get_session_dir() / f"{session_id}.json"

    def load_session_state(self, session_id: Optional[str] = None) -> SessionState:
        state_instance = self.state_schema()

        if not self.persist_enabled or not session_id:
            return state_instance

        session_file = self._get_session_file(session_id)
        if session_file.exists():
            try:
                data = json.loads(session_file.read_text())
                raw_state = data.get("state", {})
                
                # Emit state_migration hook - dev modifies raw_state in place
                if "state_migration" in self.event_bus._listeners:
                    version = data.get("version", 1)
                    # Note: currently assumes migration is synchronous.
                    # Async migration would need a different mechanism or to be awaited.
                    for handler in self.event_bus._listeners["state_migration"]:
                        raw_state = handler(version, raw_state)

                if is_dataclass(state_instance):
                    # Update dataclass instance attributes
                    for k, v in raw_state.items():
                        if hasattr(state_instance, k):
                            setattr(state_instance, k, v)
                else:
                    # Fallback for non-dataclass state
                    if hasattr(state_instance, '__dict__'):
                        state_instance.__dict__.update(raw_state)
            except Exception as e:
                print(f"Failed to load persistent session: {e}")
        
        return state_instance

    def save_session_state(self, session_id: str, state: SessionState):
        if not self.persist_enabled:
            return
            
        try:
            session_dir = self._get_session_dir()
            session_dir.mkdir(parents=True, exist_ok=True)
            session_file = self._get_session_file(session_id)
            
            state_dict = asdict(state) if is_dataclass(state) else getattr(state, "__dict__", {})
            
            data = {
                "id": session_id,
                "version": 1, # TODO: Versioning mechanism for schema evolution
                "state": state_dict
            }
            session_file.write_text(json.dumps(data))
        except Exception as e:
            print(f"Failed to save persistent session: {e}")
