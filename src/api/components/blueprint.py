import os
import importlib

from sanic import Sanic


class BlueprintLoader:
    """
    Loads the blueprints for different API versions
    """

    def __init__(self, app: Sanic) -> None:
        """
        Constructor

        :param app: Sanic
        :type app: Sanic
        """
        self.app = app

        self.loaded = False

    def register(self) -> None:
        """
        Registers the routes for different API versions
        """
        self.app.ctx.logs.info("Registering routes...")

        for version in os.listdir("routes"):
            if version.startswith("v"):
                self.app.ctx.logs.info(f"Loading routes for version {version}")

                blueprint = importlib.import_module(f"routes.{version}")

                if (
                    not hasattr(blueprint, "__routes__")
                    or len(blueprint.__routes__) == 0
                ):
                    self.app.ctx.logs.warning(
                        f"Blueprint {version} ({blueprint.__version__}) does not contain any defined routes! Ignored..."
                    )
                    continue

                self.app.ctx.logs.debug(
                    f"Blueprint {version} ({blueprint.__version__}) has {len(blueprint.__routes__)} routes: {', '.join([route.name for route in blueprint.__routes__])}"
                )

                for route in blueprint.__routes__:
                    if route.url_prefix:
                        suffix = f"(/{version}{route.url_prefix})"
                    else:
                        suffix = ""

                    self.app.ctx.logs.debug(
                        f"Loading route: {route.name} {suffix}"
                    )

                    self.app.blueprint(route)
