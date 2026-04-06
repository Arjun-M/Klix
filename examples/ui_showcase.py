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


app = klix.App(
    name="UIShowcase",
    version="0.1.0",
    description="Reusable Klix component showcase.",
    state_schema=ShowcaseState,
)


@app.on("start")
def on_start(session: klix.Session) -> None:
    session.ui.clear()
    session.ui.layout.header.set("Klix UI Showcase", color="accent")
    session.ui.layout.status.set("Ready", "Use /help", color="muted")
    session.ui.layout.redraw_ui()
    session.ui.print("Explore reusable input and output widgets.", color="accent", bold=True)
    session.ui.print("Try /help, /render, /choose, /forms, /loading, or /exit.", color="muted")


@app.command("/help", help="Show available showcase commands")
def help_cmd(session: klix.Session) -> None:
    session.ui.output.panel(
        app.generate_help(),
        title="Commands",
        border_color="border",
        title_color="accent",
    )


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


@app.command("/loading", help="Show spinner and progress widgets")
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
