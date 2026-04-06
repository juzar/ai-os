import os
from importlib import import_module
def load_plugins():
    plugins=[]
    for f in os.listdir("ai/plugins"):
        if f.endswith(".py") and f not in ["base.py","loader.py"]:
            plugins.append(import_module(f"ai.plugins.{f[:-3]}"))
    return plugins
