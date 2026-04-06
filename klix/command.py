from typing import Callable, Optional, List, Type, Any
from pydantic import BaseModel

class Command:
    def __init__(
        self,
        name: str,
        handler: Callable,
        help: str = "",
        aliases: Optional[List[str]] = None,
        args_schema: Optional[Type[BaseModel]] = None,
    ):
        self.name = name
        self.handler = handler
        self.help = help
        self.aliases = aliases or []
        self.args_schema = args_schema