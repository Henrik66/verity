"""String predicates with character-level testimony (the ``string_ops`` module).

Each predicate returns a truth whose testimony names the deciding character,
in the library's own words (a *text* node).
"""

from __future__ import annotations

from testimony import Truth, _snap, text

__all__ = ["is_alnum"]


def is_alnum(s: str) -> Truth:
    """A verity if ``s`` is non-empty and every character is alphanumeric (``str.isalnum``)."""
    if s == "":
        return text(False, "'' is empty")
    for index, char in enumerate(s):
        if not char.isalnum():
            return text(False, f"{char!r} at index {index} is not alphanumeric")
    return text(True, f"every character of {_snap(s)} is alphanumeric")
