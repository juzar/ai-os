import importlib
import os

PLUGIN_DIR = "ai.plugins"


def load_plugins():
    plugins = []

    path = os.path.dirname(__file__)

    for file in os.listdir(path):
        if file.endswith(".py") and file not in ["loader.py", "base.py"]:

            name = file[:-3]

            try:
                module = importlib.import_module(f"{PLUGIN_DIR}.{name}")

                if hasattr(module, "Plugin"):
                    plugins.append(module.Plugin())

            except Exception as e:
                print(f"[PLUGIN ERROR] {name}: {e}")

    return plugins