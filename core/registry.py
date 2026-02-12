import importlib
import inspect
import pkgutil
from pathlib import Path

from core.base_plugin import BasePlugin


class PluginRegistry:
    """Auto-discovers and manages plugins from the plugins/ directory."""

    def __init__(self):
        self._plugins: list[BasePlugin] = []

    @property
    def plugins(self) -> list[BasePlugin]:
        return list(self._plugins)

    def discover(self, package_name: str = "plugins"):
        """Scan the plugins package and instantiate all BasePlugin subclasses."""
        package_path = Path(__file__).resolve().parent.parent / package_name
        for module_info in pkgutil.iter_modules([str(package_path)]):
            module = importlib.import_module(f"{package_name}.{module_info.name}")
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BasePlugin) and obj is not BasePlugin:
                    plugin = obj(self)
                    self._plugins.append(plugin)

    def register_all(self, application):
        """Register all discovered plugin handlers with the Telegram application."""
        for plugin in self._plugins:
            for handler in plugin.get_handlers():
                application.add_handler(handler)
