import asyncio
import os
import subprocess
from pathlib import Path
import sys
from unittest.mock import AsyncMock

import klix
from klix.compat import get_renderer
from klix.input.engine import InputEngine
from klix.input.history import SessionHistory
from klix.output.theme import ThemeConfig
from klix.session import Session, SessionState, TerminalMetadata
from klix.ui import UINamespace

# Ensure the klix package is installed in editable mode for tests
# pytest will typically run in an environment where current dir is not part of PYTHONPATH
# To make 'klix' discoverable by the generated test app, it needs to be installed first.
# This should ideally be handled by the test runner setup or CI.

def test_klix_init_and_run(tmp_path):
    """Test if klix init generates a working project."""
    project_name = "my_temp_klix_app"
    project_path = tmp_path / project_name
    
    # Run klix init
    # Use python -m to call the klix init command module directly
    result = subprocess.run(
        [sys.executable, "-m", "klix.cli.init_cmd", "init", project_name],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
        env={"PATH": os.environ["PATH"], "PYTHONPATH": str(Path(__file__).parent.parent)} # Ensure klix is discoverable
    )
    assert f"Successfully initialized {project_name}!" in result.stdout
    assert project_path.exists()
    assert (project_path / "main.py").exists()
    assert (project_path / "pyproject.toml").exists()

    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", "."],
        cwd=project_path,
        capture_output=True,
        text=True,
        check=True
    )
    
    # Run the generated project with some input
    input_data = "/hello test_message\\n/exit\\n"
    # Use python -m to call the main module of the generated app
    run_result = subprocess.run(
        [sys.executable, "-m", "main"], # 'main' is the module name in the generated project
        cwd=project_path,
        input=input_data,
        capture_output=True,
        text=True,
        check=True
    )
    
    assert "Welcome to my_temp_klix_app!" in run_result.stdout
    assert "[Log] Incoming: /hello test_message" in run_result.stdout
    assert "test_message" in run_result.stdout
    assert "Goodbye." in run_result.stdout


def test_input_engine_clear_input_on_submit_opt_in():
    async def run_test():
        engine = InputEngine(clear_input_on_submit=True)
        engine.pt_session.prompt_async = AsyncMock(return_value="/hello")

        result = await engine.prompt_async("> ")

        assert result == "/hello"
        engine.pt_session.prompt_async.assert_awaited_once()
        assert engine.pt_session.prompt_async.await_args.kwargs["erase_when_done"] is True

    import asyncio
    asyncio.run(run_test())


def test_input_engine_clear_input_on_submit_defaults_off():
    async def run_test():
        engine = InputEngine()
        engine.pt_session.prompt_async = AsyncMock(return_value="/hello")

        result = await engine.prompt_async("> ")

        assert result == "/hello"
        engine.pt_session.prompt_async.assert_awaited_once()
        assert engine.pt_session.prompt_async.await_args.kwargs["erase_when_done"] is False

    import asyncio
    asyncio.run(run_test())


def test_session_history_avoids_duplicate_consecutive_entries():
    entries = []
    history = SessionHistory(entries)

    history.append_string('/help')
    history.append_string('/help')
    history.append_string('/deploy prod')

    assert entries == ['/help', '/deploy prod']


def test_session_history_applies_max_size():
    entries = []
    history = SessionHistory(entries, max_size=2)

    history.append_string('/one')
    history.append_string('/two')
    history.append_string('/three')

    assert entries == ['/two', '/three']


def test_input_engine_uses_session_history_backing():
    entries = ['/help']
    engine = InputEngine(session_history=entries, max_history_size=3)

    assert engine.history.get_strings() == ['/help']

    engine.history.append_string('/deploy prod')

    assert entries == ['/help', '/deploy prod']


def test_input_engine_multiline_mode_sets_submit_and_newline_bindings():
    async def run_test():
        engine = InputEngine(completer=object())
        engine.pt_session.prompt_async = AsyncMock(return_value="line 1\nline 2")
        engine.set_mode(engine.mode.MULTILINE)

        result = await engine.prompt_async("> ")
        kwargs = engine.pt_session.prompt_async.await_args.kwargs
        bindings = {tuple(key.value for key in binding.keys) for binding in kwargs["key_bindings"].bindings}

        assert result == "line 1\nline 2"
        assert kwargs["multiline"] is True
        assert kwargs["completer"] is None
        assert ("c-m",) in bindings
        assert ("escape", "c-m") in bindings
        assert ("c-j",) in bindings

    import asyncio
    asyncio.run(run_test())


def test_input_engine_command_mode_remains_single_line():
    async def run_test():
        completer = object()
        engine = InputEngine(completer=completer)
        engine.pt_session.prompt_async = AsyncMock(return_value="/help")

        result = await engine.prompt_async("> ")
        kwargs = engine.pt_session.prompt_async.await_args.kwargs
        bindings = {tuple(key.value for key in binding.keys) for binding in kwargs["key_bindings"].bindings}

        assert result == "/help"
        assert kwargs["multiline"] is False
        assert kwargs["completer"] is completer
        assert ("c-m",) not in bindings
        assert ("escape", "c-m") not in bindings
        assert ("c-j",) not in bindings

    import asyncio
    asyncio.run(run_test())


class _FakeRenderer:
    def __init__(self):
        self.calls = []

    def print(self, text, color=None, bold=False, dim=False, italic=False, end="\n"):
        self.calls.append(("print", text, color, bold, dim, italic, end))

    def clear(self):
        self.calls.append(("clear",))


def test_layout_header_set_triggers_sticky_redraw():
    ui = UINamespace(_FakeRenderer(), InputEngine(is_ci=True))

    ui.layout.header.set("Build: ready", color="accent")

    assert ui.renderer.calls[0] == ("clear",)
    assert ui.renderer.calls[1][:3] == ("print", "Build: ready", "accent")


def test_layout_header_keeps_main_output_under_sticky_header():
    ui = UINamespace(_FakeRenderer(), InputEngine(is_ci=True))
    ui.layout.header.set("Status", color="accent")
    ui.renderer.calls.clear()

    ui.print("first line", color="text")
    ui.print("second line", color="muted")

    printed_text = [call[1] for call in ui.renderer.calls if call[0] == "print"]
    assert printed_text.count("Status") == 2
    assert "first line" in printed_text
    assert "second line" in printed_text


def test_layout_header_api_available_on_session_ui():
    ui = UINamespace(_FakeRenderer(), InputEngine(is_ci=True))

    assert hasattr(ui.layout.header, "set")


def test_input_engine_build_prompt_style_defaults_off():
    engine = InputEngine()

    assert engine.build_prompt_style() is None


def test_input_engine_build_prompt_style_uses_theme_colors():
    engine = InputEngine(
        theme=ThemeConfig(
            input_background="#1e1e1e",
            input_text_color="#f9fafb",
            background="#111111",
            border="#374151",
        )
    )

    style = engine.build_prompt_style()

    assert style is not None
    rules = dict(style.style_rules)
    assert rules[""] == "bg:#1e1e1e #f9fafb"
    assert rules["prompt"] == "#f9fafb"
    assert rules["selected"] == "bg:#374151 #f9fafb"


def test_input_engine_prompt_async_passes_input_style():
    async def run_test():
        engine = InputEngine(theme=ThemeConfig(input_background="#1e1e1e"))
        engine.pt_session.prompt_async = AsyncMock(return_value="/help")

        result = await engine.prompt_async("> ")

        assert result == "/help"
        assert engine.pt_session.prompt_async.await_args.kwargs["style"] is not None

    import asyncio
    asyncio.run(run_test())


def test_layout_split_buffers_capture():
    ui = UINamespace(_FakeRenderer(), InputEngine(is_ci=True))

    ui.layout.split(direction="horizontal", ratio=0.4)
    ui.layout.left.print("left pane")
    ui.layout.right.print("right pane")

    assert ui.layout.split_active
    assert ui.layout.left.buffer[-1]["text"] == "left pane"
    assert ui.layout.right.buffer[-1]["text"] == "right pane"


def test_layout_split_disable_restores_main():
    ui = UINamespace(_FakeRenderer(), InputEngine(is_ci=True))
    ui.layout.split(direction="horizontal")
    ui.layout.disable_split()

    assert not ui.layout.split_active


def test_resize_handler_updates_metadata_and_triggers_event(monkeypatch):
    async def run_test():
        app = klix.App(name="resize_test", state_schema=klix.SessionState)
        session = Session(
            state=SessionState(),
            metadata=TerminalMetadata(width=80, height=24),
        )
        renderer = get_renderer(app.theme)
        session.input_engine = InputEngine(is_ci=True)
        session.ui = UINamespace(renderer, session.input_engine)

        events = []
        @app.on("resize")
        def capture(width, height, sess):
            events.append((width, height))

        monkeypatch.setattr(os, "get_terminal_size", lambda: os.terminal_size((120, 40)))
        await app._handle_resize(session)

        assert session.metadata.width == 120
        assert session.metadata.height == 40
        assert events and events[-1][0] == 120

    asyncio.run(run_test())


def test_input_engine_prompt_async_filters_unsupported_kwargs():
    async def run_test():
        engine = InputEngine(clear_input_on_submit=True, theme=ThemeConfig(input_background="#1e1e1e"))

        calls = {}

        async def legacy_prompt_async(message, *, is_password=None, multiline=None, key_bindings=None, completer=None):
            calls["message"] = message
            calls["is_password"] = is_password
            calls["multiline"] = multiline
            calls["key_bindings"] = key_bindings
            calls["completer"] = completer
            return "/help"

        engine.pt_session.prompt_async = legacy_prompt_async
        result = await engine.prompt_async("> ")

        assert result == "/help"
        assert calls["message"] == "> "
        assert "key_bindings" in calls

    import asyncio
    asyncio.run(run_test())
