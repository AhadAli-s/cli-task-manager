"""
Lab 2 — Part A: Singleton — ConfigManager
"""

import threading


class ConfigManager:
    """Singleton configuration manager."""

    _instance: "ConfigManager | None" = None
    _lock: threading.Lock = threading.Lock()

    # Default settings
    DEFAULT_PRIORITY: str = "MEDIUM"
    STORAGE_PATH: str = "tasks.json"
    DATE_FORMAT: str = "%Y-%m-%d"

    def __new__(cls) -> "ConfigManager":
        if cls._instance is None:
            with cls._lock:                  
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def get(self, key: str):
        return getattr(self, key, None)

    def set(self, key: str, value) -> None:
        setattr(self, key, value)

