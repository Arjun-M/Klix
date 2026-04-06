import asyncio
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import klix
from klix.autocomplete import KlixCompleter
from klix.compat import get_renderer
from klix.input.engine import InputEngine
from klix.middleware import MiddlewareContext, build_middleware_chain
from klix.ui import UINamespace


WELCOME_TEXT = (
    "Talk to the demo like a ai chat app. Type normal text to send a message, "
    "or use /help, /clear, /theme, or /exit."
)


@dataclass
class Message:
    role: str
    text: str


@dataclass
class ChatState(klix.SessionState):
    messages: list[Message] = field(default_factory=list)
    model: str = "klix-1"
    theme_mode: str = "dark"
    turn_count: int = 0


app = klix.App(
    name="Klix Assistant",
    version="0.1.0",
    description="AI-style conversational demo built with Klix.",
    state_schema=ChatState,
    theme=klix.ThemeConfig(
        accent="#6EA8FE",
        text="#F7F9FC",
        muted="#7C8698",
        info="#8AB4F8",
        border="#2D3B55",
        success="#7BD88F",
        warning="#F6C177",
        error="#FF7B72",
    ),
)


def set_theme(session: klix.Session) -> None:
    theme = session.ui.renderer.theme
    if session.state.theme_mode == "light":
        theme.accent = "#2B6CB0"
        theme.text = "#1F2937"
        theme.muted = "#6B7280"
        theme.info = "#2563EB"
        theme.border = "#CBD5E1"
    else:
        theme.accent = "#6EA8FE"
        theme.text = "#F7F9FC"
        theme.muted = "#7C8698"
        theme.info = "#8AB4F8"
        theme.border = "#2D3B55"


def update_status(session: klix.Session, detail: str = "chat ready") -> None:
    session.ui.layout.status.set(
        left=f"model: {session.state.model}",
        right=f"theme: {session.state.theme_mode} | {detail}",
        color="muted",
    )


def print_message(role: str, text: str, session: klix.Session) -> None:
    if role == "user":
        label = "You:"
        color = "accent"
    else:
        label = "Assistant:"
        color = "info"

    session.ui.layout.main.print(f"{label} ", color=color, bold=True, end="")
    session.ui.layout.main.print(text, color="text")
    session.ui.layout.main.print("")


def render_transcript(session: klix.Session) -> None:
    set_theme(session)
    session.ui.clear()
    session.ui.layout.header.set("Klix Assistant", color="accent")
    update_status(session)
    session.ui.layout.redraw_ui()

    if not session.state.messages:
        session.ui.layout.main.print(WELCOME_TEXT, color="muted")
        session.ui.layout.main.print("")
        return

    for message in session.state.messages:
        print_message(message.role, message.text, session)


def remember(role: str, text: str, session: klix.Session) -> None:
    session.state.messages.append(Message(role=role, text=text))


def assistant_reply(text: str, session: klix.Session) -> str:
    cleaned = text.strip()
    lower = cleaned.lower()

    if lower.startswith("explain "):
        topic = cleaned[8:].strip() or "that"
        return (
            f"{topic} looks manageable. I would break it into a small core, "
            f"verify the constraints, and iterate from the simplest working path."
        )

    if lower.startswith("summarize "):
        topic = cleaned[10:].strip() or "it"
        return (
            f"Short version: {topic} matters because it changes the main tradeoff, "
            "and the safest move is usually to simplify before optimizing."
        )

    if "compare" in lower and " and " in lower:
        return (
            "The first option feels faster to start, while the second usually scales "
            "better once the requirements get messy."
        )

    if lower.endswith("?"):
        starters = [
            "My best guess is",
            "The practical answer is",
            "I would frame it like this:",
        ]
        return (
            f"{random.choice(starters)} {cleaned[:-1].strip().lower() or 'it'} "
            "depends on what you optimize for, but clarity beats cleverness."
        )

    variants = [
        f"I hear you. A tighter version of that is: {cleaned}",
        f"That sounds reasonable. If I continued the thought, I would say: {cleaned[::-1]}",
        f"Echoing back with a bit more structure: {cleaned.title()}",
        f"Noted. The interesting part is usually hidden in this phrase: {cleaned}",
    ]
    return variants[session.state.turn_count % len(variants)]


async def stream_assistant_message(text: str, session: klix.Session) -> None:
    reply = assistant_reply(text, session)
    remember("assistant", reply, session)

    words = reply.split()

    async def chunks():
        for index, word in enumerate(words):
            suffix = " " if index < len(words) - 1 else ""
            yield word + suffix
            await asyncio.sleep(0.05)

    session.ui.layout.main.print("Assistant: ", color="info", bold=True, end="")
    await session.ui.stream(chunks(), color="text", end="\n\n")


@app.on("start")
def on_start(session: klix.Session) -> None:
    render_transcript(session)


@app.on("exit")
def on_exit(session: klix.Session) -> None:
    session.ui.layout.main.print("Session closed.", color="muted")


@app.on("input")
def on_input(text: str, session: klix.Session) -> None:
    if not text.startswith("/"):
        session.state.turn_count += 1


@app.middleware
async def command_status(ctx: klix.MiddlewareContext, next: klix.NextFn) -> None:
    console.log(f"running {ctx.command.name}")
    await next(ctx)
    update_status(ctx.session)


@app.command("/help", help="Show available commands")
def help_cmd(session: klix.Session) -> None:
    remember(
        "assistant",
        "Commands: /help shows this message, /clear resets the chat, "
        "/theme toggles the mock theme, and /exit closes the app.",
        session,
    )
    print_message("assistant", session.state.messages[-1].text, session)


@app.command("/clear", help="Clear the chat transcript")
def clear_cmd(session: klix.Session) -> None:
    session.state.messages.clear()
    render_transcript(session)


@app.command("/theme", help="Toggle the mock theme")
def theme_cmd(session: klix.Session) -> None:
    session.state.theme_mode = "light" if session.state.theme_mode == "dark" else "dark"
    render_transcript(session)
    remember("assistant", f"Theme switched to {session.state.theme_mode}.", session)
    print_message("assistant", session.state.messages[-1].text, session)


async def build_session() -> klix.Session:
    session = klix.Session(state=app.state_schema(), metadata=app._build_terminal_metadata())
    completer = KlixCompleter(app._commands, app._custom_completers, session)
    renderer = get_renderer(app.theme)
    is_ci = renderer.__class__.__name__ == "CIRenderer"

    session.input_engine = InputEngine(completer=completer, is_ci=is_ci)
    session.ui = UINamespace(renderer, session.input_engine)
    return session


async def dispatch_command(raw_input: str, session: klix.Session) -> bool:
    if raw_input in {"/exit", "/quit"}:
        return False

    try:
        parsed, _ = app._router.parse(raw_input)
    except klix.CommandNotFoundError:
        remember("assistant", f"Unknown command: {raw_input}", session)
        print_message("assistant", session.state.messages[-1].text, session)
        return True

    ctx = MiddlewareContext(raw_input=raw_input, session=session, command=parsed)
    chain = build_middleware_chain(app._middlewares, app._invoke_command)
    await chain(ctx)
    return True


async def chat_loop() -> None:
    session = await build_session()
    await app._event_bus.emit("start", session)

    running = True
    while running:
        try:
            session.input_engine.set_mode(klix.InputMode.COMMAND)
            raw_input = await session.input_engine.prompt_async("You > ")
            raw_input = raw_input.strip()

            if not raw_input:
                continue

            await app._event_bus.emit("input", raw_input, session)

            if raw_input.startswith("/"):
                running = await dispatch_command(raw_input, session)
                continue

            remember("user", raw_input, session)
            print_message("user", raw_input, session)
            update_status(session, "assistant typing")
            await stream_assistant_message(raw_input, session)
            update_status(session)
        except KeyboardInterrupt:
            await app._event_bus.emit("interrupt", session)
            session.ui.layout.main.print("Use /exit to close the demo.", color="warning")
        except EOFError:
            break

    await app._event_bus.emit("exit", session)


def main() -> None:
    asyncio.run(chat_loop())


if __name__ == "__main__":
    main()
