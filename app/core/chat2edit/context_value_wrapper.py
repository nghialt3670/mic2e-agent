from typing import Any


class NamedContextValue:
    """Wrap a value with an explicit varname prefix for contextualization."""

    def __init__(self, name: str, value: Any) -> None:
        self.name = name
        self.value = value

