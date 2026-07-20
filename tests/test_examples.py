import runpy
from pathlib import Path


def test_environment_example_runs(monkeypatch, capsys) -> None:
    monkeypatch.setenv("API_TOKEN", "example-token")
    runpy.run_path(Path("examples/environment.py"))
    assert capsys.readouterr().out == "example-token\n"
