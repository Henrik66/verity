"""Rebuild each conformance example's output by calling the runtime directly.

Milestone 1 has no compiler, so these tests do by hand what compiled code
will do: each comparison, quantifier and `because` becomes the runtime call
the compiler emits, with the same source text and spans. The printed output
must equal examples/NAME.expected byte for byte.
"""

import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path

RUNTIME = Path(__file__).resolve().parent.parent
EXAMPLES = RUNTIME.parent / "examples"
sys.path.insert(0, str(RUNTIME))

import string_ops  # noqa: E402
import testimony as _v  # noqa: E402
from testimony import all_of, configure, explain, reason, secret, to_json  # noqa: E402


def expected(name: str) -> str:
    return (EXAMPLES / f"{name}.expected").read_text()


def captured(program) -> str:
    out = io.StringIO()
    with redirect_stdout(out):
        program()
    return out.getvalue()


def span_of(name: str, snippet: str, line_hint: str | None = None) -> tuple:
    """The span the compiler would record for `snippet` in examples/NAME.ity (1-based, end exclusive)."""
    lines = (EXAMPLES / f"{name}.ity").read_text().split("\n")
    for number, line in enumerate(lines, 1):
        if line_hint is not None and line_hint not in line:
            continue
        col = line.find(snippet)
        if col >= 0:
            return (f"examples/{name}.ity", number, col + 1, number, col + 1 + len(snippet))
    raise AssertionError(f"{snippet!r} not found in {name}.ity")


# Module level, so their reprs are Circle(r=1) and not Examples.test_shapes.<locals>.Circle(r=1).
@dataclass(frozen=True)
class Circle:
    r: float


@dataclass(frozen=True)
class Rect:
    w: float
    h: float


@dataclass(frozen=True)
class Square:
    side: float


class Examples(unittest.TestCase):
    def setUp(self):
        configure(max_repr=80, max_children=50, max_depth=32)

    def test_counterexample(self):
        def program():
            primes = [2, 3, 5, 7, 11, 13]
            all_odd = _v.forall(primes, lambda p: _v.check(p % 2, "==", 1, src="p % 2 == 1"), name="p", src="primes", body_src="p % 2 == 1")
            has_big = _v.exists(primes, lambda p: _v.check(p, ">", 10, src="p > 10"), name="p", src="primes", body_src="p > 10")
            print(explain(all_odd))
            print(explain(has_big))
            if not all_odd:
                print("not every prime is odd, and Verity can tell you why")

        self.assertEqual(captured(program), expected("counterexample"))

    def test_shapes(self):
        def area(shape):
            match shape:
                case Circle(r):
                    return 3.14159 * r**2
                case Rect(w, h):
                    return w * h
                case Square(s):
                    return s * s

        def is_square(shape):
            match shape:
                case Square(_):
                    return _v.because(_v.verity, lambda: "it was built as a Square")
                case Rect(w, h):
                    return _v.check(w, "==", h, src="w == h")
                case _:
                    return _v.because(_v.falsity, lambda: f"{shape} is a rectangle")

        def program():
            shapes = [Circle(1), Rect(2, 3), Square(4), Rect(5, 5)]
            print([area(s) for s in shapes])
            for s in shapes:
                print(f"{s}: {explain(is_square(s))}")
            print(explain(_v.forall(shapes, lambda s: _v.check(area(s), ">", 3, src="area(s) > 3"), name="s", src="shapes", body_src="area(s) > 3")))

        self.assertEqual(captured(program), expected("shapes"))

    def test_validate(self):
        def valid_username(name):
            return _v.and_(
                lambda: _v.because(_v.check(len(name), ">=", 3, src="len(name) >= 3"), lambda: f"{name!r} has at least 3 characters"),
                lambda: _v.because(_v.check(len(name), "<=", 16, src="len(name) <= 16"), lambda: f"{name!r} has at most 16 characters"),
                lambda: _v.because(string_ops.is_alnum(name), lambda: f"{name!r} is alphanumeric"),
            )

        def program():
            for name in ["ada", "al", "grace_hopper"]:
                print(f"{name!r}: {explain(valid_username(name))}")

        self.assertEqual(captured(program), expected("validate"))

    def test_signup(self):
        def s(snippet, hint=None):
            return span_of("signup", snippet, hint)

        INVITE = secret("garden-42")

        def valid_signup(name, age, invite):
            return all_of(
                _v.because(
                    _v.check(len(name), ">=", 3, src="len(name) >= 3", span=s("len(name) >= 3")),
                    lambda: reason("name.length", f"{name!r} has at least 3 characters"),
                    span=s('len(name) >= 3 because reason("name.length", f"{name!r} has at least 3 characters")'),
                ),
                _v.because(
                    _v.lift(name.isalnum(), src="name.isalnum()", span=s("name.isalnum()")),
                    lambda: reason("name.charset", f"{name!r} is alphanumeric", hint="use only letters and digits"),
                    span=s('name.isalnum() because reason("name.charset", f"{name!r} is alphanumeric", hint="use only letters and digits")'),
                ),
                _v.because(
                    _v.check(age, ">=", 13, src="age >= 13", span=s("age >= 13")),
                    lambda: reason("age.minimum", "the user is at least 13"),
                    span=s('age >= 13 because reason("age.minimum", "the user is at least 13")'),
                ),
                _v.because(
                    _v.check(invite, "==", INVITE, src="invite == INVITE", span=s("invite == INVITE")),
                    lambda: reason("invite.valid", "the invite code is valid"),
                    span=s('invite == INVITE because reason("invite.valid", "the invite code is valid")'),
                ),
            )

        def program():
            result = valid_signup("ada_l", 12, "garden-41")
            print(explain(result))
            print(explain(result, audience="user"))
            print(json.dumps(to_json(result), indent=2))

        self.assertEqual(captured(program), expected("signup"))


if __name__ == "__main__":
    unittest.main()
