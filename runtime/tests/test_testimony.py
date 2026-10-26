"""Unit tests for the testimony runtime. Run: python3 -m unittest discover runtime/tests"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import string_ops  # noqa: E402
import testimony as t  # noqa: E402
from testimony import (  # noqa: E402
    SCHEMA,
    TestimonyError,
    Truth,
    all_of,
    and_,
    assert_,
    because,
    check,
    configure,
    exists,
    explain,
    falsity,
    forall,
    lift,
    not_,
    or_,
    reason,
    reveal,
    secret,
    text,
    to_bool,
    to_json,
    verity,
)


class Defaults(unittest.TestCase):
    def setUp(self):
        configure(max_repr=80, max_children=50, max_depth=32)

    tearDown = setUp


class TruthTests(Defaults):
    def test_literals(self):
        self.assertTrue(verity)
        self.assertFalse(falsity)
        self.assertEqual(repr(verity), "verity")
        self.assertEqual(str(falsity), "falsity")
        self.assertEqual(explain(verity), "verity\n  literal")

    def test_equality_ignores_testimony(self):
        self.assertEqual(check(1, "<", 2), verity)
        self.assertEqual(check(1, ">", 2), False)
        self.assertEqual(hash(check(1, "<", 2)), hash(verity))
        self.assertNotEqual(verity, falsity)

    def test_not_an_int(self):
        with self.assertRaises(TypeError):
            verity + 1
        self.assertFalse(isinstance(verity, int))

    def test_immutable(self):
        with self.assertRaises(AttributeError):
            verity._value = False
        with self.assertRaises(AttributeError):
            verity.testimony.kind = "x"

    def test_expect(self):
        self.assertIs(verity.expect(), verity)
        with self.assertRaises(TestimonyError) as ctx:
            check(3, ">", 5, src="3 > 5").expect()
        self.assertEqual(str(ctx.exception), "falsity\n  3 > 5: 3 <= 5")
        self.assertIsInstance(ctx.exception, AssertionError)

    def test_to_bool(self):
        self.assertIs(to_bool(verity), True)
        self.assertIs(to_bool(falsity), False)
        self.assertIs(to_bool([]), False)
        self.assertIs(to_bool("x"), True)


class ComparisonTests(Defaults):
    def test_relation_and_negation(self):
        cases = [
            (2, "==", 3, "2 == 3: 2 != 3"),
            (2, "!=", 2, "2 != 2: 2 == 2"),
            (2, "<", 1, "2 < 1: 2 >= 1"),
            (2, "<=", 1, "2 <= 1: 2 > 1"),
            (1, ">", 2, "1 > 2: 1 <= 2"),
            (1, ">=", 2, "1 >= 2: 1 < 2"),
            (3, "in", [1, 2], "3 in [1, 2]: 3 not in [1, 2]"),
            (1, "not in", [1, 2], "1 not in [1, 2]: 1 in [1, 2]"),
            (None, "is", 0, "None is 0: None is not 0"),
            (None, "is not", None, "None is not None: None is None"),
        ]
        for a, op, b, line in cases:
            with self.subTest(op=op):
                result = check(a, op, b)
                self.assertFalse(result)
                self.assertEqual(result.testimony.line, line)

    def test_source_text(self):
        result = check(2, "<", 3, src="len(name) >= 3")
        self.assertTrue(result)
        self.assertEqual(result.testimony.line, "len(name) >= 3: 2 < 3")

    def test_non_bool_results_pass_through(self):
        class Vector:
            def __gt__(self, other):
                return ["elementwise"]

        self.assertEqual(check(Vector(), ">", 0), ["elementwise"])

    def test_unknown_operator(self):
        with self.assertRaises(ValueError):
            check(1, "<>", 2)

    def test_snapshot_does_not_follow_mutation(self):
        xs = [1]
        result = check(xs, "==", [1, 2], src="xs == [1, 2]")
        xs.append(2)
        self.assertEqual(result.testimony.line, "xs == [1, 2]: [1] != [1, 2]")


class BooleanTests(Defaults):
    def test_and_reports_first_failure_and_short_circuits(self):
        calls = []

        def third():
            calls.append("third")
            return verity

        result = and_(check(1, "<", 2, src="a"), check(5, "<", 2, src="b"), third)
        self.assertFalse(result)
        self.assertEqual(explain(result), "falsity\n  b: 5 >= 2")
        self.assertEqual(calls, [])

    def test_and_verity_lists_and_flattens(self):
        inner = and_(check(1, "<", 2, src="a"), check(2, "<", 3, src="b"))
        result = and_(inner, check(3, "<", 4, src="c"))
        self.assertEqual(explain(result), "verity\n  all of:\n    a: 1 < 2\n    b: 2 < 3\n    c: 3 < 4")

    def test_because_is_not_flattened(self):
        inner = because(and_(verity, verity), "both")
        result = and_(inner, verity)
        self.assertEqual([c.kind for c in result.testimony.children], ["because", "literal"])

    def test_or(self):
        self.assertEqual(explain(or_(check(1, ">", 2, src="a"), check(2, ">", 3, src="b"))), "falsity\n  none of:\n    a: 1 <= 2\n    b: 2 <= 3")
        self.assertEqual(explain(or_(check(1, ">", 2, src="a"), check(3, ">", 2, src="b"))), "verity\n  b: 3 > 2")

    def test_not(self):
        self.assertEqual(explain(not_(check(1, "<", 2, src="a"))), "falsity\n  not:\n    a: 1 < 2")
        self.assertEqual(explain(not_([], src="not xs")), "verity\n  not xs returned True")

    def test_bools_are_lifted(self):
        self.assertEqual(explain(and_(True, False)), "falsity\n  <bool> returned False")

    def test_python_semantics_for_other_operands(self):
        self.assertEqual(or_("", "anonymous"), "anonymous")
        self.assertEqual(and_("x", 0), 0)
        self.assertEqual(and_(verity, "x"), "x")
        self.assertEqual(or_(lambda: None, lambda: "fallback"), "fallback")


class AllOfTests(Defaults):
    def test_reports_every_failure(self):
        result = all_of(check(1, "<", 2, src="a"), check(5, "<", 2, src="b"), check(6, "<", 2, src="c"))
        self.assertEqual(explain(result), "falsity\n  failed 2 of 3:\n    b: 5 >= 2\n    c: 6 >= 2")

    def test_verity_and_empty(self):
        self.assertEqual(explain(all_of(verity, verity)), "verity\n  all of:\n    literal\n    literal")
        self.assertEqual(explain(all_of()), "verity\n  all of:")

    def test_not_flattened(self):
        result = and_(all_of(verity, verity), verity)
        self.assertEqual([c.kind for c in result.testimony.children], ["all", "literal"])

    def test_rejects_non_truths(self):
        with self.assertRaises(TypeError):
            all_of(verity, "yes")


class BecauseTests(Defaults):
    def test_messages(self):
        self.assertEqual(explain(because(check(7 % 2, "==", 0, src="n % 2 == 0"), "7 is even")), "falsity\n  refuted: 7 is even\n    n % 2 == 0: 1 != 0")
        self.assertEqual(explain(verity.because("built that way")), "verity\n  witnessed: built that way")

    def test_lazy_message(self):
        self.assertEqual(because(verity, lambda: "late").testimony.claim, "late")

    def test_reason_and_hint(self):
        r = reason("age.minimum", "the user is at least 13", hint="ask a parent")
        failed = because(check(12, ">=", 13, src="age >= 13"), r)
        self.assertEqual(explain(failed), "falsity\n  refuted: the user is at least 13 [age.minimum]\n    hint: ask a parent\n    age >= 13: 12 < 13")
        passed = because(check(14, ">=", 13, src="age >= 13"), r)
        self.assertEqual(explain(passed), "verity\n  witnessed: the user is at least 13 [age.minimum]\n    age >= 13: 14 >= 13")

    def test_reason_ids(self):
        for good in ("a", "name.too_short", "x1.y_2.z"):
            reason(good, "m")
        for bad in ("", "Name", "a..b", ".a", "a.", "a-b", "a b", 3):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                reason(bad, "m")

    def test_asserted(self):
        self.assertTrue(because(verity, "x").testimony.asserted)
        self.assertTrue(verity.testimony.asserted)
        self.assertFalse(check(1, "<", 2).testimony.asserted)


class QuantifierTests(Defaults):
    def test_forall(self):
        primes = [2, 3, 5]
        result = forall(primes, lambda p: check(p % 2, "==", 1, src="p % 2 == 1"), name="p", src="primes", body_src="p % 2 == 1")
        self.assertEqual(explain(result), "falsity\n  counterexample: p = 2 (primes[0])\n    p % 2 == 1: 0 != 1")
        self.assertEqual(result.testimony.index, 0)
        ok = forall(primes, lambda p: check(p, ">", 1), name="p", src="primes", body_src="p > 1")
        self.assertEqual(explain(ok), "verity\n  all 3 elements of primes satisfy p > 1")

    def test_exists(self):
        result = exists([2, 11], lambda p: check(p, ">", 10, src="p > 10"), name="p", src="primes", body_src="p > 10")
        self.assertEqual(explain(result), "verity\n  witness: p = 11 (primes[1])\n    p > 10: 11 > 10")
        none = exists([1], lambda x: check(x, "==", 0), name="x", src="row", body_src="x == 0")
        self.assertEqual(explain(none), "falsity\n  no element of row satisfies x == 0")

    def test_position_for_non_names(self):
        result = forall([1, -1], lambda x: check(x, ">", 0), src="order.items", body_src="x > 0")
        self.assertEqual(result.testimony.position, "element 1")

    def test_empty_and_infinite(self):
        self.assertTrue(forall([], lambda x: falsity))
        self.assertFalse(exists([], lambda x: verity))

        def naturals():
            n = 0
            while True:
                yield n
                n += 1

        self.assertTrue(exists(naturals(), lambda n: check(n, ">", 5)))

    def test_nested(self):
        grid = [[1, 0], [0, 2], [3, 4]]
        result = forall(
            grid,
            lambda row: exists(row, lambda x: check(x, "==", 0, src="x == 0"), name="x", src="row", body_src="x == 0"),
            name="row",
            src="grid",
            body_src="exists x in row, x == 0",
        )
        self.assertEqual(explain(result), "falsity\n  counterexample: row = [3, 4] (grid[2])\n    no element of row satisfies x == 0")


class SecretTests(Defaults):
    def test_compares_but_never_shows(self):
        expected = secret("garden-42")
        result = check("garden-41", "==", expected, src='"garden-41" == expected')
        self.assertEqual(explain(result), "falsity\n  \"garden-41\" == expected: 'garden-41' != <secret>")
        self.assertNotIn("garden-42", json.dumps(to_json(result)))
        self.assertTrue(check("garden-42", "==", expected))
        self.assertTrue("garden-42" == expected)
        self.assertEqual(hash(expected), hash("garden-42"))
        self.assertEqual(f"{expected}", "<secret>")

    def test_does_not_propagate(self):
        s = secret("abc")
        with self.assertRaises(TypeError):
            len(s)
        with self.assertRaises(TypeError):
            s + "d"
        with self.assertRaises(TypeError):
            bool(s)
        self.assertEqual(reveal(s), "abc")
        self.assertEqual(reveal(5), 5)
        self.assertIs(secret(s), s)

    def test_default_source_text_hides_secret(self):
        self.assertEqual(check(1, "==", secret(2)).testimony.line, "1 == <secret>: 1 != <secret>")


class RenderingTests(Defaults):
    def setUp(self):
        super().setUp()
        self.result = all_of(
            because(lift(False, src="name.isalnum()"), reason("name.charset", "'a_b' is alphanumeric", hint="use only letters and digits")),
            because(check(12, ">=", 13, src="age >= 13"), reason("age.minimum", "the user is at least 13")),
            because(check(1, "<", 2, src="ok"), "fine"),
        )

    def test_user_audience(self):
        self.assertEqual(
            explain(self.result, audience="user"),
            "falsity\n  refuted: 'a_b' is alphanumeric [name.charset]\n    hint: use only letters and digits\n  refuted: the user is at least 13 [age.minimum]",
        )
        self.assertEqual(explain(check(1, ">", 2), audience="user"), "falsity")

    def test_unknown_audience(self):
        with self.assertRaises(ValueError):
            explain(verity, audience="robot")

    def test_explain_lifts_bools(self):
        self.assertEqual(explain(False), "falsity\n  <bool> returned False")


class JsonTests(Defaults):
    def test_document_and_key_order(self):
        doc = to_json(check(4, "==", 5, src="2 + 2 == 5", span=("demo.ity", 3, 5, 3, 15)))
        self.assertEqual(list(doc), ["schema", "value", "testimony"])
        self.assertEqual(doc["schema"], SCHEMA)
        node = doc["testimony"]
        self.assertEqual(list(node), ["kind", "value", "asserted", "line", "src", "left", "rel", "right", "span", "children"])
        self.assertEqual(node["span"], {"file": "demo.ity", "line": 3, "col": 5, "end_line": 3, "end_col": 15})
        self.assertEqual(node["left"], "4")
        json.dumps(doc)

    def test_every_kind_serializes(self):
        values = [
            check(1, "<", 2),
            and_(verity, verity),
            or_(falsity, falsity),
            all_of(falsity),
            not_(verity),
            because(verity, reason("a.b", "m", hint="h")),
            forall([1], lambda x: falsity),
            forall([1], lambda x: verity),
            exists([1], lambda x: verity),
            exists([], lambda x: verity),
            verity,
            lift(True),
            text(True, "sentence"),
        ]
        kinds = set()
        for v in values:
            doc = to_json(v)
            json.dumps(doc)
            kinds.add(doc["testimony"]["kind"])
        self.assertEqual(kinds, set(t._FIELDS) - {"truncated"})

    def test_lifted_result_is_boolean(self):
        self.assertIs(to_json(lift(False, src="f()"))["testimony"]["result"], False)

    def test_user_claims(self):
        doc = to_json(because(falsity, reason("a.b", "m", hint="h")), audience="user")
        self.assertEqual(doc, {"schema": SCHEMA, "value": "falsity", "claims": [{"value": "falsity", "claim": "m", "reason": "a.b", "hint": "h"}]})


class BoundsTests(Defaults):
    def test_repr_truncation(self):
        configure(max_repr=10)
        self.assertEqual(check("x" * 50, "==", 1).testimony.left, "'xxxxxx...")

    def test_addresses_removed(self):
        obj = object()
        self.assertEqual(check(obj, "is", None).testimony.left, "<object object>")

    def test_children_cap(self):
        configure(max_children=3)
        result = all_of(*[falsity] * 5)
        self.assertEqual(explain(result).splitlines()[-1], "    ... 2 more nodes omitted")
        self.assertEqual(result.testimony.failed, 5)

    def test_depth_cap(self):
        configure(max_depth=2)
        deep = not_(not_(not_(verity)))
        self.assertEqual(explain(deep), "falsity\n  not:\n    not:\n      ... 2 more nodes omitted")
        self.assertEqual(to_json(deep)["testimony"]["children"][0]["children"][0]["kind"], "truncated")

    def test_configure_validates(self):
        with self.assertRaises(ValueError):
            configure(max_depth=0)
        with self.assertRaises(ValueError):
            configure(max_repr=True)


class AssertTests(Defaults):
    def test_assert_message_only_on_failure(self):
        calls = []
        assert_(verity, lambda: calls.append(1) or "m")
        self.assertEqual(calls, [])
        with self.assertRaises(TestimonyError) as ctx:
            assert_(check(80, "<=", 50, src="amount <= balance"), lambda: "the balance covers 80", span=("w.ity", 2, 5, 2, 30))
        self.assertEqual(str(ctx.exception), "falsity\n  refuted: the balance covers 80\n    amount <= balance: 80 > 50")
        self.assertEqual(ctx.exception.span, ("w.ity", 2, 5, 2, 30))

    def test_assert_non_truths(self):
        assert_([1])
        with self.assertRaises(TestimonyError) as ctx:
            assert_([], src="items")
        self.assertEqual(str(ctx.exception), "falsity\n  items returned False")


class StringOpsTests(Defaults):
    def test_is_alnum(self):
        self.assertEqual(explain(string_ops.is_alnum("grace_hopper")), "falsity\n  '_' at index 5 is not alphanumeric")
        self.assertEqual(explain(string_ops.is_alnum("ada")), "verity\n  every character of 'ada' is alphanumeric")
        self.assertEqual(explain(string_ops.is_alnum("")), "falsity\n  '' is empty")


if __name__ == "__main__":
    unittest.main()
