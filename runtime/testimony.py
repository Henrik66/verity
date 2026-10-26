"""Verity's testimony runtime: truth values that explain themselves.

Compiled Verity programs import this module (as ``_v``), and Python code can
use it directly (``pip install verity-testimony``). It implements the
``truth`` type, testimony nodes, the combinators the compiler lowers
operators to, text and JSON rendering, reasons, secrets and bounds. The
reference documentation, *Verity Programming*, specifies all of it; section
numbers below refer to it.

Only the Python standard library is used.
"""

from __future__ import annotations

import operator
import re
from typing import Any, Callable, Iterable

__all__ = [
    "SCHEMA",
    "Node",
    "Reason",
    "Secret",
    "TestimonyError",
    "Truth",
    "all_of",
    "and_",
    "assert_",
    "because",
    "check",
    "configure",
    "exists",
    "explain",
    "falsity",
    "forall",
    "lift",
    "not_",
    "or_",
    "reason",
    "reveal",
    "secret",
    "text",
    "to_bool",
    "to_json",
    "verity",
]

SCHEMA = "verity.testimony/0"

# --- bounds (section 5.8) ------------------------------------------------

_LIMITS = {"max_repr": 80, "max_children": 50, "max_depth": 32}


def configure(max_repr: int | None = None, max_children: int | None = None, max_depth: int | None = None) -> None:
    """Set the testimony bounds for this process. Arguments not given keep their values."""
    for key, value in (("max_repr", max_repr), ("max_children", max_children), ("max_depth", max_depth)):
        if value is None:
            continue
        if not isinstance(value, int) or isinstance(value, bool) or value < (4 if key == "max_repr" else 1):
            raise ValueError(f"{key} must be an integer of at least {4 if key == 'max_repr' else 1}, got {value!r}")
        _LIMITS[key] = value


_ADDRESS = re.compile(r" at 0x[0-9a-fA-F]+")


def _snap(value: Any) -> str:
    """Capture a value as a bounded, address-free repr string."""
    if isinstance(value, Secret):
        return "<secret>"
    try:
        text_ = repr(value)
    except Exception as exc:  # a broken __repr__ must not break testimony
        text_ = f"<unrepresentable {type(value).__name__}: {type(exc).__name__}>"
    text_ = _ADDRESS.sub("", text_)
    limit = _LIMITS["max_repr"]
    if len(text_) > limit:
        text_ = text_[: limit - 3] + "..."
    return text_


# --- spans ---------------------------------------------------------------

_SPAN_KEYS = ("file", "line", "col", "end_line", "end_col")


def _span(span: Any) -> tuple | None:
    if span is None:
        return None
    if isinstance(span, dict):
        span = tuple(span[k] for k in _SPAN_KEYS)
    span = tuple(span)
    if len(span) != 5:
        raise ValueError(f"a span is (file, line, col, end_line, end_col), got {span!r}")
    return span


# --- nodes (section 5.1) -------------------------------------------------

_FIELDS = {
    "comparison": ("src", "left", "rel", "right"),
    "all": (),
    "none": (),
    "failures": ("failed", "total"),
    "not": (),
    "because": ("claim", "reason", "hint"),
    "counterexample": ("name", "element", "position", "index"),
    "universal": ("count", "iterable", "body"),
    "witness": ("name", "element", "position", "index"),
    "no-element": ("iterable", "body"),
    "literal": (),
    "lifted": ("src", "result"),
    "text": ("text",),
    "truncated": ("omitted",),
}

_ASSERTED = frozenset({"because", "literal"})


class Node:
    """One immutable testimony node.

    Attributes: ``kind``, ``value`` (bool), ``asserted``, ``line``,
    ``children`` (tuple), ``span`` (tuple or None) and the fields of its kind.
    """

    __slots__ = ("kind", "value", "_fields", "children", "span", "_op")

    def __init__(self, kind: str, value: bool, fields: tuple = (), children: tuple = (), span: Any = None, op: str | None = None):
        names = _FIELDS[kind]
        if len(fields) != len(names):
            raise ValueError(f"{kind} node takes fields {names}, got {fields!r}")
        set_ = object.__setattr__
        set_(self, "kind", kind)
        set_(self, "value", bool(value))
        set_(self, "_fields", dict(zip(names, fields)))
        set_(self, "children", tuple(children))
        set_(self, "span", _span(span))
        set_(self, "_op", op)  # "and"/"or" when built by that operator, for flattening

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("testimony nodes are immutable")

    def __getattr__(self, name: str) -> Any:
        try:
            return object.__getattribute__(self, "_fields")[name]
        except KeyError:
            raise AttributeError(f"{self.kind} node has no field {name!r}") from None

    @property
    def asserted(self) -> bool:
        return self.kind in _ASSERTED

    @property
    def fields(self) -> dict:
        return dict(self._fields)

    @property
    def line(self) -> str:
        f, k = self._fields, self.kind
        if k == "comparison":
            return f"{f['src']}: {f['left']} {f['rel']} {f['right']}"
        if k == "all":
            return "all of:"
        if k == "none":
            return "none of:"
        if k == "failures":
            return f"failed {f['failed']} of {f['total']}:"
        if k == "not":
            return "not:"
        if k == "because":
            head = f"{'witnessed' if self.value else 'refuted'}: {f['claim']}"
            return f"{head} [{f['reason']}]" if f["reason"] else head
        if k in ("counterexample", "witness"):
            return f"{k}: {f['name']} = {f['element']} ({f['position']})"
        if k == "universal":
            return f"all {f['count']} elements of {f['iterable']} satisfy {f['body']}"
        if k == "no-element":
            return f"no element of {f['iterable']} satisfies {f['body']}"
        if k == "literal":
            return "literal"
        if k == "lifted":
            return f"{f['src']} returned {f['result']}"
        if k == "text":
            return f["text"]
        return f"... {f['omitted']} more nodes omitted"

    def __repr__(self) -> str:
        return f"<{self.kind} node: {self.line}>"


def _cap(children: Iterable[Node], value: bool) -> tuple:
    """Keep at most max_children children; summarize the rest in one truncated node."""
    children = tuple(children)
    limit = _LIMITS["max_children"]
    if len(children) <= limit:
        return children
    return children[:limit] + (Node("truncated", value, (len(children) - limit,)),)


def _size(node: Node) -> int:
    return 1 + sum(_size(c) for c in node.children)


# --- truths (section 3.2) ------------------------------------------------


class Truth:
    """A truth value, ``verity`` or ``falsity``, carrying testimony."""

    __slots__ = ("_value", "_testimony")

    def __init__(self, value: bool, testimony: Node):
        object.__setattr__(self, "_value", bool(value))
        object.__setattr__(self, "_testimony", testimony)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("truths are immutable")

    @property
    def value(self) -> bool:
        return self._value

    @property
    def testimony(self) -> Node:
        return self._testimony

    def __bool__(self) -> bool:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Truth):
            return self._value == other._value
        if isinstance(other, bool):
            return self._value == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return "verity" if self._value else "falsity"

    __str__ = __repr__

    def because(self, message: Any) -> "Truth":
        return because(self, message)

    def expect(self) -> "Truth":
        """Return this truth if it is a verity; raise TestimonyError if it is a falsity."""
        if not self._value:
            raise TestimonyError(self)
        return self


verity = Truth(True, Node("literal", True))
falsity = Truth(False, Node("literal", False))


def _as_truth(value: Any, src: str | None = None, span: Any = None, where: str = "a truth") -> Truth:
    if isinstance(value, Truth):
        return value
    if isinstance(value, bool):
        return lift(value, src, span)
    raise TypeError(f"{where} must be a truth or a bool, got {type(value).__name__}")


def lift(value: Any, src: str | None = None, span: Any = None) -> Truth:
    """Lift a Python bool into a truth (section 7.2). A truth is returned unchanged."""
    if isinstance(value, Truth):
        return value
    if not isinstance(value, bool):
        raise TypeError(f"only a bool can be lifted, got {type(value).__name__}")
    return Truth(value, Node("lifted", value, (src or "<bool>", value), span=span))


def text(value: bool, sentence: str) -> Truth:
    """A truth whose testimony is a sentence in the library's own words."""
    return Truth(value, Node("text", value, (str(sentence),)))


# --- comparisons (section 4.3) -------------------------------------------

_OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "in": lambda a, b: a in b,
    "not in": lambda a, b: a not in b,
    "is": operator.is_,
    "is not": operator.is_not,
}

_NEGATE = {"==": "!=", "!=": "==", "<": ">=", "<=": ">", ">": "<=", ">=": "<", "in": "not in", "not in": "in", "is": "is not", "is not": "is"}


def check(left: Any, op: str, right: Any, src: str | None = None, span: Any = None) -> Any:
    """Apply a comparison. Returns a truth if Python's result is a bool, else the result unchanged."""
    try:
        apply = _OPS[op]
    except KeyError:
        raise ValueError(f"unknown comparison operator {op!r}") from None
    result = apply(reveal(left), reveal(right))
    if type(result) is not bool:
        return result  # numpy arrays, pandas series, ...: pass through (section 7.4)
    left_s, right_s = _snap(left), _snap(right)
    rel = op if result else _NEGATE[op]
    return Truth(result, Node("comparison", result, (src or f"{left_s} {op} {right_s}", left_s, rel, right_s), span=span))


# --- boolean operations (section 4.4) ------------------------------------


def _force(operand: Any) -> Any:
    if callable(operand) and not isinstance(operand, (Truth, bool)):
        return operand()
    return operand


def _junction(operands: tuple, conjunction: bool) -> Any:
    kind, op = ("all", "and") if conjunction else ("none", "or")
    collected: list[Truth] = []
    python_mode, last = False, None
    for operand in operands:
        value = _force(operand)
        if not isinstance(value, (Truth, bool)):
            python_mode = True  # Python semantics for non-truth operands (section 7.5)
        if python_mode:
            if bool(value) != conjunction:
                return value
            last = value
            continue
        t = _as_truth(value)
        if t.value != conjunction:
            return t  # short circuit: the deciding operand's testimony
        collected.append(t)
    if python_mode:
        return last
    children: list[Node] = []
    for t in collected:
        node = t.testimony
        children.extend(node.children if node.kind == kind and node._op == op else (node,))
    return Truth(conjunction, Node(kind, conjunction, children=_cap(children, conjunction), op=op))


def and_(*operands: Any) -> Any:
    """Short-circuit conjunction. Operands may be zero-argument callables, called only when needed."""
    return _junction(operands, True)


def or_(*operands: Any) -> Any:
    """Short-circuit disjunction. Operands may be zero-argument callables, called only when needed."""
    return _junction(operands, False)


def not_(operand: Any, src: str | None = None, span: Any = None) -> Truth:
    """Negation. A non-truth, non-bool operand gets Python's ``not``, lifted."""
    if not isinstance(operand, (Truth, bool)):
        return lift(not operand, src, span)
    t = _as_truth(operand)
    return Truth(not t.value, Node("not", not t.value, children=(t.testimony,)))


def all_of(*operands: Any) -> Truth:
    """The accumulating conjunction: report every failing operand (section 5.2)."""
    truths = [_as_truth(o, where="an all_of operand") for o in operands]
    failing = [t for t in truths if not t.value]
    if not failing:
        return Truth(True, Node("all", True, children=_cap((t.testimony for t in truths), True)))
    return Truth(False, Node("failures", False, (len(failing), len(truths)), children=_cap((t.testimony for t in failing), False)))


# --- because and reasons (section 5.3) -----------------------------------

_REASON_ID = re.compile(r"[a-z0-9_]+(\.[a-z0-9_]+)*")


class Reason:
    """A claim with a stable dotted ID and an optional hint."""

    __slots__ = ("id", "message", "hint")

    def __init__(self, id: str, message: str, hint: str | None = None):
        if not isinstance(id, str) or not _REASON_ID.fullmatch(id):
            raise ValueError(f"reason IDs are dotted lowercase identifiers like 'name.too_short', got {id!r}")
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "message", str(message))
        object.__setattr__(self, "hint", None if hint is None else str(hint))

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("reasons are immutable")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Reason) and (self.id, self.message, self.hint) == (other.id, other.message, other.hint)

    def __hash__(self) -> int:
        return hash((self.id, self.message, self.hint))

    def __repr__(self) -> str:
        return f"reason({self.id!r}, {self.message!r}" + (f", hint={self.hint!r})" if self.hint else ")")


def reason(id: str, message: str, hint: str | None = None) -> Reason:
    """Build a Reason for use with ``because``."""
    return Reason(id, message, hint)


def because(truth: Any, message: Any, span: Any = None) -> Truth:
    """Attach a claim to a truth. ``message`` may be a str, a Reason or a zero-argument callable."""
    t = _as_truth(truth, where="the left operand of because")
    if callable(message) and not isinstance(message, Reason):
        message = message()
    if isinstance(message, Reason):
        fields = (message.message, message.id, message.hint)
    else:
        fields = (str(message), None, None)
    children = () if t.testimony.kind == "literal" else (t.testimony,)
    return Truth(t.value, Node("because", t.value, fields, children, span=span))


# --- quantifiers (section 4.6) -------------------------------------------


def _position(src: str | None, index: int) -> str:
    return f"{src}[{index}]" if src and src.isidentifier() else f"element {index}"


def _quantify(iterable: Iterable, body: Callable, name: str, src: str | None, body_src: str | None, universal: bool) -> Truth:
    count = 0
    for index, element in enumerate(iterable):
        result = _as_truth(body(element), body_src, where="a quantifier body")
        if result.value != universal:
            kind = "counterexample" if universal else "witness"
            node = Node(kind, result.value, (name, _snap(element), _position(src, index), index), (result.testimony,))
            return Truth(result.value, node)
        count += 1
    if universal:
        return Truth(True, Node("universal", True, (count, src or "<iterable>", body_src or "<body>")))
    return Truth(False, Node("no-element", False, (src or "<iterable>", body_src or "<body>")))


def forall(iterable: Iterable, body: Callable, name: str = "x", src: str | None = None, body_src: str | None = None) -> Truth:
    """``forall name in iterable, body``: stops at the first counterexample."""
    return _quantify(iterable, body, name, src, body_src, True)


def exists(iterable: Iterable, body: Callable, name: str = "x", src: str | None = None, body_src: str | None = None) -> Truth:
    """``exists name in iterable, body``: stops at the first witness."""
    return _quantify(iterable, body, name, src, body_src, False)


# --- secrets (section 5.7) -----------------------------------------------


class Secret:
    """A value that testimony shows as <secret>. It compares and hashes like its value; nothing else."""

    __slots__ = ("_value",)

    def __init__(self, value: Any):
        object.__setattr__(self, "_value", value)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("secrets are immutable")

    def __repr__(self) -> str:
        return "<secret>"

    __str__ = __repr__

    def __eq__(self, other: object) -> bool:
        return self._value == reveal(other)

    def __ne__(self, other: object) -> bool:
        return self._value != reveal(other)

    def __lt__(self, other: Any) -> bool:
        return self._value < reveal(other)

    def __le__(self, other: Any) -> bool:
        return self._value <= reveal(other)

    def __gt__(self, other: Any) -> bool:
        return self._value > reveal(other)

    def __ge__(self, other: Any) -> bool:
        return self._value >= reveal(other)

    def __hash__(self) -> int:
        return hash(self._value)

    def __contains__(self, item: Any) -> bool:
        return reveal(item) in self._value

    def __bool__(self) -> bool:
        raise TypeError("a secret has no truth value; use reveal()")

    def __format__(self, spec: str) -> str:
        return format("<secret>", spec)


def secret(value: Any) -> Secret:
    """Wrap a value so that it never appears in testimony."""
    return value if isinstance(value, Secret) else Secret(value)


def reveal(value: Any) -> Any:
    """Return a secret's wrapped value. Any other value is returned unchanged."""
    return object.__getattribute__(value, "_value") if isinstance(value, Secret) else value


# --- errors and assert (section 6.2) -------------------------------------


class TestimonyError(AssertionError):
    """Raised by a failing assert or Truth.expect(); ``truth`` holds the falsity."""

    __test__ = False  # not a pytest test class

    def __init__(self, truth: Truth, span: Any = None):
        self.truth = truth
        self.span = _span(span)
        super().__init__(explain(truth))

    def __str__(self) -> str:
        return explain(self.truth)


def assert_(value: Any, message: Any = None, span: Any = None, src: str | None = None) -> None:
    """The lowering of ``assert value, message``. The message is evaluated only on failure."""
    if isinstance(value, (Truth, bool)):
        t = _as_truth(value, src, span)
    else:
        t = lift(bool(value), src, span)
    if t.value:
        return
    if message is not None:
        t = because(t, message, span)
    raise TestimonyError(t, span)


def to_bool(value: Any) -> bool:
    """A plain bool: the truth value of a truth, or Python truthiness for anything else."""
    return bool(value)


# --- rendering (sections 5.4 and 5.5) ------------------------------------

_AUDIENCES = ("developer", "user")


def _audience(audience: str) -> str:
    if audience not in _AUDIENCES:
        raise ValueError(f"audience must be one of {_AUDIENCES}, got {audience!r}")
    return audience


def _claims(node: Node) -> list[Node]:
    if node.kind == "because":
        return [node]
    return [c for child in node.children for c in _claims(child)]


def _hint(node: Node) -> str | None:
    return node.hint if node.kind == "because" and not node.value else None


def explain(truth: Any, audience: str = "developer") -> str:
    """Render a truth and its testimony as indented text."""
    t = _as_truth(truth, where="the argument of explain")
    lines = ["verity" if t.value else "falsity"]
    if _audience(audience) == "user":
        for claim in _claims(t.testimony):
            lines.append("  " + claim.line)
            if _hint(claim):
                lines.append("    hint: " + claim.hint)
        return "\n".join(lines)

    max_depth = _LIMITS["max_depth"]

    def walk(node: Node, depth: int) -> None:
        pad = "  " * depth
        if depth > max_depth:
            lines.append(f"{pad}... {_size(node)} more nodes omitted")
            return
        lines.append(pad + node.line)
        if _hint(node):
            lines.append(f"{pad}  hint: {node.hint}")
        for child in node.children:
            walk(child, depth + 1)

    walk(t.testimony, 1)
    return "\n".join(lines)


# --- JSON (section 5.6) --------------------------------------------------


def _word(value: bool) -> str:
    return "verity" if value else "falsity"


def _node_json(node: Node, depth: int) -> dict:
    if depth > _LIMITS["max_depth"]:
        node = Node("truncated", node.value, (_size(node),))
    out: dict = {"kind": node.kind, "value": _word(node.value), "asserted": node.asserted, "line": node.line}
    out.update(node._fields)
    if node.span is not None:
        out["span"] = dict(zip(_SPAN_KEYS, node.span))
    out["children"] = [_node_json(c, depth + 1) for c in node.children]
    return out


def to_json(truth: Any, audience: str = "developer") -> dict:
    """The testimony as a JSON-serializable dict in the schema verity.testimony/0."""
    t = _as_truth(truth, where="the argument of to_json")
    doc: dict = {"schema": SCHEMA, "value": _word(t.value)}
    if _audience(audience) == "user":
        doc["claims"] = [
            {"value": _word(c.value), "claim": c.claim, "reason": c.reason, "hint": _hint(c)} for c in _claims(t.testimony)
        ]
    else:
        doc["testimony"] = _node_json(t.testimony, 1)
    return doc
