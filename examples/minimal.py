import klix
from pydantic import BaseModel

class AppState(klix.SessionState):
    run_count: int = 0

class DeployArgs(BaseModel):
    env: str
    force: bool = False

app = klix.App(name="UIDemo", state_schema=AppState)

@app.on("start")
def on_start(session: klix.Session):
    session.ui.print("Welcome to Klix! Testing rich output.", color="accent", bold=True)
    session.ui.output.panel("Try commands like: /deploy, /ask, /login, /markdown")

@app.command("/deploy", aliases=["/d"], args_schema=DeployArgs, help="Deploy app")
async def deploy(args: DeployArgs, session: klix.Session):
    session.ui.print(f"Deploying to {args.env}... force={args.force}", color="success")
    session.ui.output.table(
        headers=["Env", "Force"],
        rows=[[args.env, str(args.force)]],
        header_color="accent"
    )

@app.command("/ask", help="Test MULTILINE and CONFIRM input modes")
async def ask_mode(session: klix.Session):
    session.ui.print("Enter multiline text (Shift+Enter where supported, otherwise Esc-Enter):", dim=True)
    session.input_engine.set_mode(klix.InputMode.MULTILINE)
    text = await session.input_engine.prompt_async()
    
    proceed = await session.ui.input.confirm(f"You entered {len(text)} chars. Proceed?")
    
    if proceed:
        session.ui.print("Confirmed!", color="success")
    else:
        session.ui.print("Cancelled.", color="error")

@app.command("/login", help="Test PASSWORD input mode")
async def login_mode(session: klix.Session):
    pw = await session.ui.input.secret("Enter password:")
    session.ui.print(f"{pw}", color="success")
    session.ui.print(f"Password length: {len(pw)}", color="success")

@app.command("/markdown", help="Test markdown rendering")
def md_render(session: klix.Session):
    session.ui.output.markdown("# Hello Markdown\n* item 1\n* item 2\n\n**Bold text**")

@app.completer("/deploy")
def deploy_completer(text: str, session: klix.Session) -> list[str]:
    return ["prod", "staging", "dev", "test"]

if __name__ == "__main__":
    app.run()