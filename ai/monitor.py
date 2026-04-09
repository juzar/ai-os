import time
from pathlib import Path

LOG = Path("logs/execution.log")
LOG.parent.mkdir(exist_ok=True)


def track(event):
    with open(LOG, "a") as f:
        f.write(f"{time.time()} :: {event}\n")