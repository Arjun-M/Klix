import os
import subprocess
from pathlib import Path
import sys

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
