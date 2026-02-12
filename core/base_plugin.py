from abc import ABC, abstractmethod


class BasePlugin(ABC):
    """Base class for all bot plugins.

    To create a new plugin:
    1. Create a file in plugins/
    2. Define a class extending BasePlugin
    3. Implement the required properties and get_handlers()
    4. The registry will auto-discover it on startup
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable plugin name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description shown in /help."""

    @abstractmethod
    def get_handlers(self) -> list:
        """Return list of telegram handler objects to register."""
