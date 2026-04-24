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
        """Return the value of a configuration setting by name."""
        return getattr(self, key, None)

    def set(self, key: str, value) -> None:
        """Override a configuration setting at runtime."""
        setattr(self, key, value)


# ---------------------------------------------------------------------------
# Demonstration
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    a = ConfigManager()
    b = ConfigManager()
    c = ConfigManager()

    print("=== Singleton Demonstration ===")
    print(f"id(a) = {id(a)}")
    print(f"id(b) = {id(b)}")
    print(f"id(c) = {id(c)}")
    assert id(a) == id(b) == id(c), "FAIL: multiple instances created!"
    print("✓ All three ids are identical — only one instance was created.\n")

    print(f"DEFAULT_PRIORITY : {a.get('DEFAULT_PRIORITY')}")
    print(f"STORAGE_PATH     : {a.get('STORAGE_PATH')}")
    print(f"DATE_FORMAT      : {a.get('DATE_FORMAT')}")

    # Mutating via one reference is visible through all others
    a.set("DEFAULT_PRIORITY", "HIGH")
    print(f"\nAfter a.set('DEFAULT_PRIORITY', 'HIGH'):")
    print(f"  b.get('DEFAULT_PRIORITY') = {b.get('DEFAULT_PRIORITY')}  ← same instance")

    # Thread-safety proof: spin up 50 threads all calling ConfigManager()
    results: list[int] = []

    def grab_id() -> None:
        results.append(id(ConfigManager()))

    threads = [threading.Thread(target=grab_id) for _ in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(set(results)) == 1, "FAIL: thread-safety broken!"
    print(f"\n✓ 50 concurrent threads all received the same instance id.")