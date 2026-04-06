"""Middleware primitives and chain construction.

Middleware in Klix is just an ordered async call chain around command
dispatch. This file keeps that mechanism small: a context object, a `NextFn`
type, and the function that composes multiple middleware functions together.
"""

from dataclasses import dataclass
from typing import Callable, Optional, Awaitable, Any

from .session import Session
from .router import ParsedCommand


# Middleware gets the raw line, parsed command, and live session object in one
# place so cross-cutting concerns do not have to leak into handlers.
@dataclass
class MiddlewareContext:
    raw_input: str
    session: Session
    command: Optional[ParsedCommand] = None
    cancelled: bool = False

NextFn = Callable[['MiddlewareContext'], Awaitable[None]]


# Composition happens in reverse so middleware executes in registration order:
# the first middleware registered is the first one the request enters.
def build_middleware_chain(middlewares: list[Callable], final_handler: NextFn) -> NextFn:
    """Composes a list of middleware into a single awaitable chain."""
    chain = final_handler
    
    for mw in reversed(middlewares):
        def _create_next(current_mw, next_fn):
            async def _next(context: MiddlewareContext):
                if context.cancelled:
                    return
                await current_mw(context, next_fn)
            return _next
        chain = _create_next(mw, chain)
        
    return chain
