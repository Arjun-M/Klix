"""Core application object for Klix.

This file owns the top-level framework wiring: command registration,
middleware composition, event dispatch, session creation, renderer/input
selection, and the main interactive loop used by generated apps and examples.

If another file defines a single subsystem, `App` is where those subsystems
get stitched together into one runtime.
"""

import asyncio
import inspect
import os
import signal
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Optional, Type, Dict, List
from pydantic import BaseModel

from .command import Command
from .session import Session, SessionState, TerminalMetadata
from .state import SessionStateManager # Import the new manager
from .events import EventBus
from .router import Router, ParsedCommand
from .middleware import MiddlewareContext, build_middleware_chain
from .errors import KlixError
from .output.theme import ThemeConfig
from .autocomplete import KlixCompleter
from .input.engine import InputEngine
from .input.modes import InputMode
from .compat import get_renderer
from .ui import UINamespace
from .args import CLIArgsParser # Import the new CLIArgsParser
from .help import HelpGenerator


# Small app-wide settings live here so the public constructor can stay readable
# without pushing every concern into keyword arguments.
@dataclass
class AppConfig:
    history_path: Optional[str] = None
    log_path: Optional[str] = None
    clear_input_on_submit: bool = False
    max_history_size: Optional[int] = None


# App is the framework entry point. It collects developer registrations first,
# then builds a concrete session and event loop when `run()` is called.
class App:
    def __init__(
        self,
        name: str,
        version: str = "0.1.0",
        description: str = "",
        theme: Optional[ThemeConfig] = None,
        config: Optional[AppConfig] = None,
        state_schema: Optional[Type[SessionState]] = None,
        persist_session: bool = False,
        **kwargs
    ):
        self.name = name
        self.version = version
        self.description = description
        self.theme = theme or ThemeConfig()
        self.config = config or AppConfig()
        self.state_schema = state_schema or SessionState
        self.persist_session = persist_session
        
        self._commands: Dict[str, Command] = {}
        self._middlewares: List[Callable] = []
        self._event_bus = EventBus()
        self._router = Router(self._commands)
        self._custom_completers: Dict[str, Callable] = {}
        
        self._state_manager = SessionStateManager(
            app_name=self.name,
            state_schema=self.state_schema,
            event_bus=self._event_bus,
            persist_enabled=self.persist_session
        )
        self._help_generator = HelpGenerator(self) # Instantiate HelpGenerator with App instance

    # Registration keeps aliases in the same lookup table as canonical names so
    # the router can stay simple and treat both paths the same way.
    def register(self, command: Command):
        self._commands[command.name] = command
        for alias in command.aliases:
            self._commands[alias] = command

    # The decorator API is intentionally thin sugar over `Command(...)`. The
    # framework still stores explicit command objects internally.
    def command(
        self,
        name: str,
        help: str = "",
        aliases: Optional[List[str]] = None,
        args_schema: Optional[Type[BaseModel]] = None,
    ):
        def decorator(func: Callable):
            cmd = Command(
                name=name,
                handler=func,
                help=help,
                aliases=aliases,
                args_schema=args_schema
            )
            self.register(cmd)
            return func
        return decorator

    def on(self, event_name: str):
        return self._event_bus.on(event_name)

    def middleware(self, func: Callable):
        self._middlewares.append(func)
        return func

    def completer(self, command_name: str):
        """Decorator to register a custom autocomplete function."""
        def decorator(func: Callable):
            self._custom_completers[command_name] = func
            return func
        return decorator

    def generate_help(self) -> str:
        return self._help_generator.generate_help()

    # Metadata is captured once per session so handlers can inspect the terminal
    # environment without reaching back into `os.environ`.
    def _build_terminal_metadata(self) -> TerminalMetadata:
        env_keys = ("TERM", "TERM_PROGRAM", "COLORTERM", "CI", "SSH_CONNECTION")
        env = {key: os.environ[key] for key in env_keys if key in os.environ}

        try:
            terminal_size = os.get_terminal_size()
            width, height = terminal_size.columns, terminal_size.lines
        except OSError:
            width, height = 0, 0

        return TerminalMetadata(
            env=env,
            width=width,
            height=height,
            start_time=datetime.now(timezone.utc).isoformat(),
            term_program=os.environ.get("TERM_PROGRAM"),
            interactive=os.isatty(0) and os.isatty(1),
        )

    # Middleware runs after parsing, so command-aware middleware can inspect
    # `ctx.command` before the handler executes.
    async def _invoke_command(self, ctx: MiddlewareContext):
        if ctx.cancelled:
            return

        try:
            if ctx.command is None:
                raise KlixError("Command context was not parsed before dispatch.")

            command = self._commands[ctx.command.name]
            await self._event_bus.emit("command", ctx.command, ctx.session)

            args = self._router.validate_args(command, ctx.command)

            kwargs = {}
            sig = inspect.signature(command.handler)
            if "session" in sig.parameters:
                kwargs["session"] = ctx.session
            
            for param_name, param in sig.parameters.items():
                if param_name != "session" and command.args_schema:
                    kwargs[param_name] = args
                    
            if inspect.iscoroutinefunction(command.handler):
                await command.handler(**kwargs)
            else:
                command.handler(**kwargs)

        except KlixError as e:
            await self._event_bus.emit("error", e, ctx.session)
            print(f"Error: {e}")

    # `_run_async` is the concrete session lifecycle. It creates the session,
    # binds renderer/input/ui objects, emits lifecycle events, then drives the
    # read/parse/middleware/dispatch loop until exit.
    async def _run_async(self):
        print(f"Starting {self.name} v{self.version}")

        session_id = None
        if self.persist_session:
            import uuid
            session_id = str(uuid.uuid4())

        state_instance = self._state_manager.load_session_state(session_id=session_id)
        session = Session(
            id=session_id,
            state=state_instance,
            metadata=self._build_terminal_metadata(),
        )
        
        completer = KlixCompleter(self._commands, self._custom_completers, session)
        renderer = get_renderer(self.theme)
        
        # CI mode avoids interactive prompt_toolkit behavior and falls back to
        # line-based stdin/stdout so tests and pipes keep working.
        is_ci = renderer.__class__.__name__ == "CIRenderer"
        
        session.input_engine = InputEngine(
            completer=completer,
            is_ci=is_ci,
            clear_input_on_submit=self.config.clear_input_on_submit,
            session_history=session.history,
            max_history_size=self.config.max_history_size,
            theme=renderer.theme,
        )
        session.ui = UINamespace(renderer, session.input_engine)

        loop = asyncio.get_running_loop()
        resize_installed = False
        if hasattr(signal, "SIGWINCH"):
            loop.add_signal_handler(
                signal.SIGWINCH,
                lambda: asyncio.create_task(self._handle_resize(session)),
            )
            resize_installed = True

        await self._event_bus.emit("start", session)

        session.ui.print("Type a command (or /exit to quit):", dim=True)
        
        while True:
            try:
                session.input_engine.set_mode(InputMode.COMMAND)
                raw_input = await session.input_engine.prompt_async("> ")
                raw_input = raw_input.strip()
                
                if raw_input in ("/exit", "/quit"):
                    break
                    
                if not raw_input:
                    continue
                
                await self._event_bus.emit("input", raw_input, session)

                # Parsing happens before middleware so middleware can make
                # routing decisions with the same parsed representation the
                # handler will eventually receive.
                parsed, _ = self._router.parse(raw_input)
                ctx = MiddlewareContext(raw_input=raw_input, session=session, command=parsed)
                chain = build_middleware_chain(self._middlewares, self._invoke_command)
                await chain(ctx)

            except EOFError:
                break
            except KeyboardInterrupt:
                await self._event_bus.emit("interrupt", session)
                print("\nInterrupted.")
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")

        await self._event_bus.emit("exit", session)
        if resize_installed:
            loop.remove_signal_handler(signal.SIGWINCH)
        # Save state using the manager
        self._state_manager.save_session_state(session.id, session.state)
        
        if session._tasks:
            await asyncio.gather(*session._tasks, return_exceptions=True)
            
        print("Goodbye.")

    async def _handle_resize(self, session: Session) -> None:
        try:
            terminal_size = os.get_terminal_size()
            width, height = terminal_size.columns, terminal_size.lines
        except OSError:
            width, height = session.metadata.width, session.metadata.height

        session.metadata.width = width
        session.metadata.height = height

        session.ui.layout.trigger_redraw()
        session.ui.layout.redraw_ui()

        await self._event_bus.emit("resize", width, height, session)

    # `run()` remains synchronous from the caller's perspective. Klix owns the
    # event loop boundary so app code does not need to call `asyncio.run()`.
    def run(self):
        # Parse global CLI arguments first
        arg_parser = CLIArgsParser(self.name, self.version, self.description)
        global_args = arg_parser.parse_args()
        
        # You might want to store global_args in self.config or session.metadata
        # For now, just ensuring they are parsed.
        if global_args.debug:
            print("Debug mode enabled.")

        try:
            asyncio.run(self._run_async())
        except KeyboardInterrupt:
            pass
