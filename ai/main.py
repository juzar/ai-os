
import typer
from ai.router import detect_mode
from ai.executor import run_model
from ai.plugins.kubernetes import analyze_kube

app = typer.Typer()

@app.command()
def run(mode: str, task: str):
    if mode == "auto":
        mode = detect_mode(task)

    if mode == "kube":
        print(analyze_kube(task))
        return

    print(run_model(mode, task))

if __name__ == "__main__":
    app()
