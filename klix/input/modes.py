"""Input mode enum shared across the input subsystem.

Modes let Klix describe the kind of interaction currently active without
every caller having to configure prompt behavior from scratch.
"""

from enum import Enum

class InputMode(Enum):
    COMMAND = "command"
    MULTILINE = "multiline"
    SELECT = "select"
    SEARCH = "search"
    CONFIRM = "confirm"
    PASSWORD = "password"
    INTERRUPT = "interrupt"
