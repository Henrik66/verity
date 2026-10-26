# Verity

**Code that tells the truth.**

Verity is a quirky functional take on Python. It borrows its syntax from [Coconut](https://coconut-lang.org/): `x -> x + 1` lambdas, `|>` pipes, `$` partial application, `match`, `data` types and pattern-matched `def`. It compiles to plain Python, so all of CPython and its libraries come along. Verity's booleans are different. They are called `verity` and `falsity`, and they *testify*: every verity carries a witness, and every falsity carries a refutation. `and`, `or`, `not`, comparisons, `forall` and `exists` assemble that testimony for you, and `because` lets you write your own. When something is false, Verity can tell you why. When nobody asks, the compiler erases the testimony, so ordinary control flow costs nothing extra.

```coconut
from testimony import explain

primes = [2, 3, 5, 7, 11, 13]

(forall p in primes, p % 2 == 1) |> explain |> print
```

```
falsity
  counterexample: p = 2 (primes[0])
    p % 2 == 1: 0 != 1
```

More in [`examples/`](examples/).

## Status

**Early design.** Nothing compiles yet. The compiler is being written in Rust (hand-written lexer and parser) and will emit Python plus a small embedded runtime. See [CLAUDE.md](CLAUDE.md) for the spec and milestones.

## License

Apache-2.0
