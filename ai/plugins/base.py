class Plugin:
    name = "base"

    def run(self, query: str):
        raise NotImplementedError("Plugin must implement run()")