# Verity: standing spec

Verity is a quirky functional version of Python. This file is the spec. If code and this file disagree, either fix the code or update this file on purpose. Don't let them drift.

## The language

- **Syntax mostly borrowed from Coconut** (https://coconut-lang.org/):
  - `x -> x + 1` lambdas
  - `|>` pipes
  - `$` partial application (`map$(area)`)
  - `..>` composition
  - `match` pattern matching
  - `data` algebraic types
  - pattern-matched `def` extended with `addpattern def`
- **Booleans are `verity` and `falsity`**, the two constructors of the type `truth`. Never `True`/`False` in Verity source.
- **Testifying booleans (the unique feature).** Every `truth` carries testimony. A verity carries a *witness* and a falsity carries a *refutation*.
  - `and`, `or` and `not`, comparisons, `forall x in xs, p` and `exists x in xs, p` compose testimony automatically.
  - `p because msg` attaches custom testimony. `msg` states the claim, so on a verity it renders as `witnessed: msg` and on a falsity as `refuted: msg`, with the underlying testimony nested beneath it.
  - `and` short-circuits. A falsity from `and` reports only the first failing conjunct, while a verity reports all conjuncts. `or` is the mirror image.
  - `forall` stops at the first counterexample and `exists` stops at the first witness. Each reports the bound value and its position.
  - Comparison testimony quotes the source expression and the evaluated operands, e.g. `len(name) >= 3: 2 < 3`.
  - `testimony.explain(t)` renders a truth as `verity`/`falsity` followed by an indented testimony tree. The `.expected` files in `examples/` define the format.
  - The compiler **erases unused testimony**, so plain control flow costs nothing.
- **Standard library** modules and functions use snake_case: `list_ops`, `string_ops`, `testimony`.
- **Source files** use the `.ity` extension.

## Architecture

- **Compiler: 100% Rust.** A Cargo binary called `verity`, with a **hand-written lexer and parser**. There is no parser generator, because the parser must handle Python-style indentation (INDENT/DEDENT tokens) and custom operator precedence.
  - `src/lexer.rs`: tokens and indentation
  - `src/parser.rs`: recursive descent for statements, Pratt parsing for expressions
  - `src/ast.rs`: syntax tree with source spans
  - `src/compiler.rs`: AST to Python source, plus testimony erasure
  - `src/cli.rs`: `verity run file.ity` and `verity compile file.ity`
  - `src/runtime.rs`: embeds the Python runtime
- **Target: Python.** The compiler emits Python source that runs on CPython (`python3` must be installed to run programs).
- **Runtime: `runtime/truth.py`.** This small Python module implements `truth` and testimony. It is embedded in the Rust binary with `include_str!` and written next to the generated code. Users never install a Python package.
- Python can't overload `and`, `or` or `not`, so the compiler rewrites them, along with comparisons, quantifiers and `because`, into testimony-composing runtime calls.

### Python interop rules

1. **Python to Verity:** plain `bool` results from Python code are lifted into truths with minimal testimony, e.g. `str.isdigit('4a') returned False`.
2. **Verity to Python:** `Truth` implements `__bool__`, so it works in `if`, `while`, `all()` and similar. Code that strictly needs a `bool` (`json.dumps`, `isinstance(x, bool)`) calls `to_bool(t)`.
3. **Non-bool comparisons pass through untouched.** If a comparison returns something that isn't a `bool` (numpy arrays, pandas series), the runtime returns it unchanged instead of wrapping it. This needs a test from milestone 2 onwards.
4. **Python is a runtime requirement.** The `verity` binary itself is standalone.
5. **Tracebacks:** errors initially point at the generated Python. Mapping them back to `.ity` line numbers is planned for later and is not part of any milestone yet.

## Build milestones (in order)

1. **Runtime only:** the `Truth` class, testimony nodes, combinators, `explain` rendering and the interop helpers in `runtime/truth.py`, with Python tests for the runtime.
2. **Tiny language:** literals, `def`, comparisons and `and`/`or`/`not`, lexed, parsed and compiled to Python by the Rust compiler. Includes a working `verity run file.ity` CLI.
3. **`forall`/`exists` and `because`.**
4. **Coconut features, one at a time:** lambdas, pipes, partial application, composition, `data`, `match`, `addpattern`.
5. **Testimony erasure pass.**

## The book

`book/src/*.html` holds *Verity Programming*, the reference documentation (authors: Henrik Gombos and Pranav Balakrishnan), structured like a traditional language reference with [[settled]]/[[proposed]]/[[open]] status markers. Run `python3 book/build.py` to regenerate `site/public/book/` (Vite copies it into the site build), and commit the generated output. Book examples must agree with this spec and with `examples/*.expected`. Rules marked proposed or open are not spec until adopted here; when a proposal is adopted, mark it settled in the docs. When a milestone changes behavior, update the affected chapters.

## Working rules

- **One milestone per session.** Don't start the next one in the same session.
- **`examples/` must pass before a milestone counts as done.** Each `examples/*.ity` must produce exactly its `.expected` output under `verity run`. An example can only be skipped if it uses features from a later milestone, and the skip must be explicit.
- **Commit after each working milestone.**
- `cargo test` and the runtime's Python tests must pass before committing.
