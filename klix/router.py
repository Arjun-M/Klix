"""Command parsing and schema validation.

The router turns raw slash-command input into a structured `ParsedCommand`,
resolves aliases to canonical command names, and validates arguments against
Pydantic models before handlers run.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, ValidationError

from .command import Command
from .errors import ArgValidationError, CommandNotFoundError


# ParsedCommand is the stable handoff object used by middleware, events, and
# handlers. It gives the rest of the framework a parsed view of the raw line.
@dataclass
class ParsedCommand:
    name: str
    positional: List[str] = field(default_factory=list)
    flags: Dict[str, Any] = field(default_factory=dict)
    raw: str = ""

class Router:
    def __init__(self, commands: Dict[str, Command]):
        self.commands = commands

    # Parsing is intentionally shallow here: tokenization plus alias lookup.
    # Schema-aware coercion happens later in `validate_args`.
    def parse(self, raw_input: str) -> Tuple[ParsedCommand, Command]:
        """Parses a raw input string, resolves aliases, and returns ParsedCommand and Command."""
        parts = raw_input.strip().split()
        if not parts:
            raise CommandNotFoundError("Empty command.")
            
        cmd_name = parts[0]
        if cmd_name not in self.commands:
            raise CommandNotFoundError(f"Command '{cmd_name}' not found.")
            
        command = self.commands[cmd_name]
        
        # Middleware and help generation expect the canonical command name, so
        # aliases are normalized here rather than later during dispatch.
        parsed = self._parse_args(command.name, parts[1:], raw_input)
        
        return parsed, command

    # The parser keeps shell-like behavior intentionally minimal. It supports
    # positional values plus flag/value pairs without trying to become a full
    # shell parser.
    def _parse_args(self, name: str, args_list: List[str], raw: str) -> ParsedCommand:
        positional = []
        flags = {}
        
        i = 0
        while i < len(args_list):
            arg = args_list[i]
            if arg.startswith("--"):
                key = arg[2:]
                if i + 1 < len(args_list) and not args_list[i+1].startswith("-"):
                    flags[key] = args_list[i+1]
                    i += 1
                else:
                    flags[key] = True
            elif arg.startswith("-"):
                key = arg[1:]
                if i + 1 < len(args_list) and not args_list[i+1].startswith("-"):
                    flags[key] = args_list[i+1]
                    i += 1
                else:
                    flags[key] = True
            else:
                positional.append(arg)
            i += 1
            
        return ParsedCommand(name=name, positional=positional, flags=flags, raw=raw)

    # Validation is where parsed tokens become a typed handler payload. Positional
    # values are mapped onto still-missing schema fields in declaration order.
    def validate_args(self, command: Command, parsed: ParsedCommand) -> Optional[BaseModel]:
        """Validates ParsedCommand against the command's Pydantic args_schema."""
        if not command.args_schema:
            return None
            
        schema = command.args_schema
        
        # Merge positional and flags into a dictionary
        data = {}
        data.update(parsed.flags)
        
        # This keeps simple commands ergonomic without asking developers to
        # manually decode positional lists in every handler.
        if parsed.positional:
            fields = schema.model_fields
            missing_keys = [k for k in fields.keys() if k not in data]
            for val, key in zip(parsed.positional, missing_keys):
                data[key] = val

        try:
            return schema(**data)
        except ValidationError as e:
            # Klix surfaces one clean error at a time instead of dumping the
            # full Pydantic payload directly into the terminal.
            error = e.errors()[0]
            loc = ".".join(str(l) for l in error["loc"])
            msg = error["msg"]
            raise ArgValidationError(field=loc, message=msg)
