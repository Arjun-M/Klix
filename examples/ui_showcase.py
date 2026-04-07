import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import klix


@dataclass
class ShowcaseState(klix.SessionState):
    theme_mode: str = "default"
    header_mode: str = "sticky"


app = klix.App(
    name="UIShowcase",
    version="0.1.0",
    description="Reusable Klix component showcase.",
    state_schema=ShowcaseState,
    config=klix.AppConfig(
        clear_input_on_submit=True,
        max_history_size=20,
    ),
    theme=klix.ThemeConfig(
        accent="#4F8CFF",
        text="#F5F7FA",
        muted="#8A93A6",
        info="#6CCFF6",
        border="#2E3445",
        success="#3FCF8E",
        warning="#F2C14E",
        error="#E85D75",
        input_background="#171B24",
        input_text_color="#F5F7FA",
    ),
)


@app.on("start")
def on_start(session: klix.Session) -> None:
    session.ui.clear()
    session.ui.layout.header.set("Klix UI Showcase", color="accent")
    session.ui.layout.status.set("Ready", "Use /help", color="muted")
    session.ui.print("Explore reusable input and output widgets.", color="accent", bold=True)
    session.ui.print(
        "Try /help, /render, /choose, /forms, /multiline, /history, /header, /loading, or /exit.",
        color="muted",
    )


@app.command("/help", help="Show available showcase commands")
def help_cmd(session: klix.Session) -> None:
    session.ui.output.panel(
        app.generate_help(),
        title="Commands",
        border_color="border",
        title_color="accent",
    )
    session.ui.print("Input clears after submit in this demo.", color="muted")
    session.ui.print("Command history uses Up/Down and keeps the last 20 entries.", color="muted")


@app.command("/render", help="Render output widgets")
def render_cmd(session: klix.Session) -> None:
    session.ui.output.panel(
        "Panels, cards, tables, diffs, and code are all reusable widgets.",
        title="Panel",
        border_color="accent",
    )
    session.ui.output.card(
        "Cards are the same primitive with a different semantic name.",
        title="Card",
        border_color="info",
    )
    session.ui.output.table(
        headers=["Component", "Status", "Latency"],
        rows=[
            ["Table", "ready", "12ms"],
            ["Panel", "ready", "8ms"],
            ["Spinner", "idle", "0ms"],
        ],
        header_color="accent",
        border_color="border",
        alignments=["left", "center", "right"],
    )
    session.ui.output.diff("old value\npending", "new value\ncomplete")
    session.ui.output.code("print('klix ui showcase')", lang="python")
    session.ui.print("The input bar uses themed background styling in capable terminals.", color="muted")


@app.command("/choose", help="Try selector inputs")
async def choose_cmd(session: klix.Session) -> None:
    flavor = await session.ui.input.select(
        ["Gemini", "Claude", "Klix", "Local"],
        label="Pick a profile",
    )
    tags = await session.ui.input.multiselect(
        ["fast", "safe", "cheap", "creative"],
        label="Pick attributes",
        default=["safe"],
    )
    enabled = await session.ui.input.toggle("Enable demo mode", default=True)
    fuzzy = await session.ui.input.fuzzy(
        ["alpha", "beta", "gamma", "delta", "epsilon"],
        label="Search a Greek letter",
    )
    session.ui.output.json(
        {
            "profile": flavor,
            "attributes": tags,
            "demo_enabled": enabled,
            "fuzzy_pick": fuzzy,
        }
    )


@app.command("/forms", help="Try text, number, confirm, and password inputs")
async def forms_cmd(session: klix.Session) -> None:
    name = await session.ui.input.text(
        "Name",
        placeholder="Type your name",
        validate=lambda value: len(value.strip()) > 0,
    )
    amount = await session.ui.input.number("Score", min_val=0, max_val=100)
    confirm = await session.ui.input.confirm("Proceed with the entered values?", default=True)
    password = await session.ui.input.secret("Password")
    session.ui.output.json(
        {
            "name": name,
            "score": amount,
            "confirmed": confirm,
            "password_length": len(password),
        }
    )


@app.command("/multiline", help="Try multiline input mode")
async def multiline_cmd(session: klix.Session) -> None:
    session.ui.print(
        "Multiline mode is active. Use Shift+Enter where supported, otherwise Esc-Enter, for a newline.",
        color="muted",
    )
    session.ui.print("Press Enter on its own to submit the full block.", color="muted")
    session.input_engine.set_mode(klix.InputMode.MULTILINE)
    body = await session.input_engine.prompt_async("Notes > ")
    session.input_engine.set_mode(klix.InputMode.COMMAND)
    session.ui.output.panel(body or "(empty)", title="Captured Multiline Input", border_color="accent")


@app.command("/history", help="Inspect session command history")
def history_cmd(session: klix.Session) -> None:
    recent = session.history[-5:] or ["(no command history yet)"]
    session.ui.output.panel(
        "\n".join(recent),
        title=f"Recent Commands ({len(session.history)} stored)",
        border_color="info",
    )
    session.ui.print("Use Up/Down arrows at the prompt to navigate session history.", color="muted")


@app.command("/header", help="Toggle sticky header text")
def header_cmd(session: klix.Session) -> None:
    if session.state.header_mode == "sticky":
        session.state.header_mode = "build"
        header_text = "Klix UI Showcase | sticky header active | build: ready"
    else:
        session.state.header_mode = "sticky"
        header_text = "Klix UI Showcase"

    session.ui.layout.header.set(header_text, color="accent")
    session.ui.print("Header updated without scrolling away.", color="success")


@app.command("/loading", help="Show spinner and progress widgets")
@app.command("/split", help="Toggle horizontal split layout")
def split_cmd(session: klix.Session) -> None:
    if session.ui.layout.split_active:
        session.ui.layout.disable_split()
        msg = "Split layout disabled."
    else:
        session.ui.layout.split(direction="horizontal", ratio=0.45)
        msg = "Split layout enabled. Left panel mirrors /main output."
    session.ui.print(msg, color="muted")


@app.command("/panels", help="Print demo content into left and right panels")
def panels_cmd(session: klix.Session) -> None:
    session.ui.layout.left.print("Left pane: primary log stream.", color="text")
    session.ui.layout.right.print("Right pane: secondary status.", color="muted")
    session.ui.print("Panels updated independently.", color="info")


async def loading_cmd(session: klix.Session) -> None:
    spinner = session.ui.output.spinner("Preparing showcase", color="accent")
    spinner.start()
    await asyncio.sleep(0.4)
    spinner.update("Loading progress demo")
    await asyncio.sleep(0.4)
    spinner.stop()

    progress = session.ui.output.progress(total=5, label="Warmup", color="success")
    progress.start()
    for _ in range(5):
        await asyncio.sleep(0.2)
        progress.update(advance=1)
    progress.stop()
    session.ui.print("Loading demo complete.", color="success")


if __name__ == "__main__":
    app.run()
