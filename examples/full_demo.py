import klix
from pydantic import BaseModel, Field
from dataclasses import dataclass, field
import asyncio
import time
import random
from typing import List, Dict, Any

@dataclass
class UserState(klix.SessionState):
    authenticated: bool = False
    username: str = "guest"
    settings: Dict[str, Any] = field(default_factory=dict)
    active_tasks: List[str] = field(default_factory=list)
    run_count: int = 0
    progress_total: int = 0
    progress_completed: int = 0

class DeployArgs(BaseModel):
    env: str = Field(description="Environment to deploy to (e.g., prod, staging)")
    force: bool = Field(False, description="Force the deployment")
    tag: str = Field("latest", description="Docker image tag")

class SearchArgs(BaseModel):
    query: str = Field(description="Query string to search for")
    limit: int = Field(10, description="Maximum number of results")

app = klix.App(
    name="FullDemo",
    version="1.0.0",
    description="A comprehensive demonstration of Klix framework features.",
    state_schema=UserState,
    persist_session=True # Enable session persistence
)

# --- Event Handlers ---
@app.on("start")
async def on_start(session: klix.Session):
    session.ui.clear()
    session.ui.layout.header.set(f"Klix Full Demo v{app.version}", color="accent")
    session.ui.layout.status.set(f"User: {session.state.username}", "Ready", color="muted")
    session.ui.print(f"Welcome to the Klix Full Demo, {session.state.username}!", color="success", bold=True)
    if session.state.authenticated:
        session.ui.print("You are authenticated.", color="success")
    else:
        session.ui.print("You are not authenticated. Try /login.", color="warning")
    session.ui.print("Type /help for available commands.")
    session.ui.newline()
    # Test cursor positioning
    # session.ui.move_cursor(1, 2) # This would move cursor away from prompt

@app.on("exit")
def on_exit(session: klix.Session):
    session.ui.print(f"Thank you for using Klix. Total commands run: {session.state.run_count}")

@app.on("error")
def on_error(exc: klix.KlixError, session: klix.Session):
    session.ui.print(f"Error: {exc}", color="error")

@app.on("interrupt")
def on_interrupt(session: klix.Session):
    session.ui.print("Interrupted current operation.", color="warning")

@app.on("state_migration")
def migrate_state(old_version: int, raw_state: dict) -> dict:
    # Example migration: if old state had 'user_name' rename to 'username'
    if old_version < 2 and 'user_name' in raw_state:
        raw_state['username'] = raw_state.pop('user_name')
    return raw_state

# --- Middlewares ---
@app.middleware
async def log_middleware(ctx: klix.MiddlewareContext, next: klix.NextFn):
    start_time = time.time()
    await next(ctx)
    elapsed = time.time() - start_time
    # session.ui might not be available if an error occurs very early or CI.
    if ctx.session.ui:
        ctx.session.ui.print(f"[Middleware: Log] Command '{ctx.raw_input}' took {elapsed:.4f}s", dim=True)
    else:
        print(f"[Middleware: Log] Command '{ctx.raw_input}' took {elapsed:.4f}s")

@app.middleware
async def auth_check(ctx: klix.MiddlewareContext, next: klix.NextFn):
    if ctx.command and ctx.command.name == "/deploy" and not ctx.session.state.authenticated:
        ctx.session.ui.print("Authentication required for /deploy.", color="error")
        ctx.cancelled = True
        return
    await next(ctx)

# --- Commands ---
@app.command("/help", help="Show this help message")
def show_help(session: klix.Session):
    session.ui.print(app.generate_help(), color="dim")

@app.command("/login", help="Authenticate a user")
async def login_cmd(session: klix.Session):
    username = await session.ui.input.text("Username:", default="guest")
    password = await session.ui.input.secret("Password:")

    if username == "admin" and password == "secret":
        session.state.authenticated = True
        session.state.username = username
        session.ui.print("Login successful!", color="success")
    else:
        session.ui.print("Invalid credentials.", color="error")
    session.ui.layout.status.set(f"User: {session.state.username}", "Ready", color="muted")

@app.command("/logout", help="Log out current user", aliases=["/exit", "/quit"])
async def logout_cmd(session: klix.Session):
    confirm = await session.ui.input.confirm("Are you sure you want to log out?")
    if confirm:
        session.state.authenticated = False
        session.state.username = "guest"
        session.ui.print("Logged out.", color="success")
    else:
        session.ui.print("Logout cancelled.", color="warning")
    session.ui.layout.status.set(f"User: {session.state.username}", "Ready", color="muted")

@app.command("/deploy", aliases=["/d"], args_schema=DeployArgs, help=DeployArgs.__doc__)
async def deploy_cmd(args: DeployArgs, session: klix.Session):
    session.ui.print(f"Initiating deployment for {args.env} with tag {args.tag} (force: {args.force})", color="muted")
    session.ui.output.panel(f"Deployment to {args.env}", title=f"Deploying {args.tag}", border_color="accent")
    
    session.state.progress_total = 10
    session.state.progress_completed = 0
    spinner = session.ui.output.spinner(f"Deploying {args.tag} to {args.env}...")
    spinner.start()

    progress_bar = session.ui.output.progress(total=session.state.progress_total, label="Overall Progress", color="muted")
    # For now, progress is a placeholder
    # progress_bar.start()

    for i in range(session.state.progress_total):
        await asyncio.sleep(0.5) # Simulate work
        session.state.progress_completed = i + 1
        # progress_bar.update(1) # In a real impl, update this
    
    spinner.stop()
    # progress_bar.stop()

    session.ui.print("Deployment complete!", color="success")
    session.ui.output.json({"env": args.env, "status": "success", "tag": args.tag})
    session.state.run_count += 1
    session.state.active_tasks.append(f"Deploy {args.env}")

@app.command("/settings", help="Manage user settings")
async def settings_cmd(session: klix.Session):
    session.ui.print("Current settings:", dim=True)
    session.ui.output.json(session.state.settings or {"theme": "default"})
    new_theme = await session.ui.input.select(["dark", "light", "auto"], "Select theme:")
    session.state.settings["theme"] = new_theme
    session.ui.print(f"Theme set to {new_theme}", color="muted")

@app.command("/code", help="Display code example")
def code_cmd(session: klix.Session):
    code_str = """
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)
print(factorial(5))
"""
    session.ui.output.code(code_str, lang="python", theme="solarized-dark")

@app.command("/tree", help="Display a tree structure")
def tree_cmd(session: klix.Session):
    data = {"root": {"folder1": {"file1.txt": None, "file2.md": None}, "folder2": {"subfolder": {"config.json": None}}}}
    session.ui.output.tree(data, color="yellow")

@app.command("/diff", help="Show a text diff")
def diff_cmd(session: klix.Session):
    old_text = "Line 1\nLine 2 changed\nLine 3"
    new_text = "Line 1\nLine 2 updated\nLine 4 new"
    session.ui.output.diff(old_text, new_text)

@app.command("/stream_test", help="Test streaming output")
async def stream_test_cmd(session: klix.Session):
    session.ui.print("Streaming output:", dim=True)
    async def generate_chunks():
        for i in range(5):
            yield f"Chunk {i+1}... "
            await asyncio.sleep(0.3)
        yield "Done."
    await session.ui.stream(generate_chunks(), color="blue")
    session.ui.newline()

@app.command("/background_task", help="Run a task in the background")
async def background_task_cmd(session: klix.Session):
    async def long_running_task():
        session.ui.print("Background task started...", color="dim")
        for i in range(3):
            await asyncio.sleep(1)
            session.ui.print(f"Background task: {i+1}/3", dim=True)
        session.ui.print("Background task finished!", color="muted")
        session.state.active_tasks.remove("long_task")

    session.ui.print("Scheduling background task.", color="muted")
    session.create_task(long_running_task())
    session.state.active_tasks.append("long_task")

@app.command("/show_tasks", help="Show active background tasks")
def show_tasks_cmd(session: klix.Session):
    if session.state.active_tasks:
        session.ui.print(f"Active tasks: {', '.join(session.state.active_tasks)}", color="muted")
    else:
        session.ui.print("No active background tasks.", color="dim")

# --- Completers ---
@app.completer("/deploy")
def deploy_completer(text: str, session: klix.Session) -> list[str]:
    # Custom completion for the 'env' argument
    # If the user has typed an argument, complete it
    args = text.split()
    if len(args) == 2: # user is typing the env argument
        return [e for e in ["prod", "staging", "dev", "test"] if e.startswith(args[1])]
    return []

if __name__ == "__main__":
    app.run()
