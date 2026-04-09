from pathlib import Path
import time

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "ai.log"


def log_error(source, message):
    try:
        entry = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{source}] {message}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except:
        pass