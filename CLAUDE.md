# Verity: standing spec

Verity is Python whose truth values explain themselves, built so that agents and people can read and check programs. Its pitch is **checks that explain themselves**: when a check fails, Verity reports which comparison, element or claim decided it, both as an indented tree for people and as JSON for tools and agents. This file is the spec. If code and this file disagree, either fix the code or update this file on purpose. Don't let them drift.

## The language

- **Syntax is Python 3.12**, plus a few keywords. Agents and people who know Python can write Verity without learning new syntax. The extensions are the whole list:
  - `verity` and `falsity`, the two truth literals. `True`/`False` in Verity source are a compile error whose diagnostic carries a machine-applicable fix (`True` → `verity`).
  - `p because m`: attach a claim to a truth. `m` is a string or a `reason(...)`.
  - `forall x in xs, body` and `exists x in xs, body`: quantifiers that return truths.
  - `assert p` (and `assert p, m`, which means `assert (p because m)`) raises `TestimonyError` carrying the falsity.
  - Nothing else. No Coconut syntax: lambdas are `lambda`, data types are `@dataclass`, and pattern matching is Python's `match`.
- **Booleans are `verity` and `falsity`**, the two constructors of the type `truth`.
- **Testimony (the unique feature).** Every `truth` carries testimony. A verity carries a *witness* and a falsity carries a *refutation*.
  - `and`, `or` and `not`, comparisons, `forall`/`exists`, `because` and `testimony.all_of(...)` compose testimony automatically.
  - `p because msg`: on a verity it renders as `witnessed: msg`, on a falsity as `refuted: msg`, with the underlying testimony nested beneath it.
  - `p because reason(id, msg, hint=None)` adds a stable dotted reason ID, rendered `refuted: msg [id]`, and an optional hint, rendered as a `hint: ...` line under a falsity. IDs match `[a-z0-9_]+(\.[a-z0-9_]+)*`.
  - `and` short-circuits. A falsity from `and` reports only the first failing conjunct, and a verity reports all conjuncts. `or` is the mirror image.
  - `all_of(p, q, ...)` is the **accumulating conjunction**. It evaluates every operand. A falsity reports every failing operand under `failed k of n:`. A verity reports all operands under `all of:`.
  - `forall` stops at the first counterexample and `exists` stops at the first witness. Each reports the bound value and its position (`xs[i]` for a plain name, otherwise `element i`). The counterexample is the first one, not the smallest.
  - Comparison testimony quotes the source expression and the evaluated operands, e.g. `len(name) >= 3: 2 < 3`.
  - A Python `bool` used as a truth is *lifted*: `name.isalnum() returned False`, quoting the source text.
  - `because` text is an unchecked claim. Testimony marks such nodes `asserted` so tools can tell claims from computed evidence.
- **Rendering.** `testimony.explain(t, audience="developer")` renders `verity`/`falsity` followed by an indented tree. `audience="user"` shows only the outermost `because` claims with their reason IDs and hints, never source text or values. The `.expected` files in `examples/` define the format.
- **JSON.** `testimony.to_json(t, audience="developer")` returns a JSON-serializable dict in the published schema `verity.testimony/0`. Every node has `kind`, `value`, `asserted`, `line`, its kind's fields, an optional `span`, and `children`. The book's Testimony chapter defines the schema exactly, including key order.
- **Secrets.** `secret(x)` wraps a value. It compares and hashes like `x`, but renders as `<secret>` in every audience and format. Secrets don't propagate: other operations need `reveal(s)`, which returns an ordinary value.
- **Bounds and determinism.** Operand `repr`s are captured when a node is built (not at render time), truncated to 80 characters, and stripped of memory addresses (` at 0x...`). A node keeps at most 50 children; the rest become one `... k more nodes omitted` line. Rendering stops at depth 32. `testimony.configure(...)` changes the limits. `verity run` and `verity test` set `PYTHONHASHSEED=0`, so the same program and input produce byte-identical output.
- **Erasure by dual compilation.** Each function that returns a truth is compiled twice: an evidence version, which builds testimony, and a value version, which computes plain booleans. A call whose result is only branched on (an `if`/`elif`/`while` condition, a conditional-expression test, a `case` guard, a comprehension filter, `bool()`, `to_bool()`) calls the value version. Every other use calls the evidence version. Output must be identical with erasure disabled (`VERITY_NO_ERASE=1`).
- **Standard library** modules and functions use snake_case: `testimony`, `string_ops`, `list_ops`.
- **Source files** use the `.ity` extension.

## Non-goals

Testimony is explanation, not proof. Verity does not target authorization engines (explanations leak policy) or data-frame quality pipelines (vectorised comparisons pass through without testimony). It does not replace Python syntax.

## Agent interface

- **Diagnostics** have stable codes (`E0101`), a span, a message, an optional hint and an optional machine-applicable fix.
- **`--json`** on `verity check`, `verity run` and `verity test` writes machine records as JSON Lines: diagnostics, uncaught `TestimonyError` failures with their testimony, and test results.
- **`verity test`** runs `test_*` functions in `test_*.ity` files and reports each failure's testimony.
- **Tracebacks map to `.ity` lines** (milestone 3).
- **The docs ship plain-text versions for agents:** `book/llms.txt` and `book/verity.txt`, generated by `book/build.py`.

## Architecture

- **Compiler: 100% Rust.** A Cargo binary called `verity`, with a **hand-written lexer and parser**. There is no parser generator, because the parser must handle Python-style indentation (INDENT/DEDENT tokens) and the extra keywords.
  - `src/lexer.rs`: tokens and indentation
  - `src/parser.rs`: recursive descent for statements, Pratt parsing for expressions
  - `src/ast.rs`: syntax tree with source spans
  - `src/compiler.rs`: AST to Python source, plus dual compilation
  - `src/cli.rs`: `verity run`, `verity compile`, `verity check`, `verity test`
  - `src/runtime.rs`: embeds the Python runtime
- **Target: Python.** The compiler emits Python source that runs on CPython (`python3` must be installed to run programs).
- **Runtime: `runtime/testimony.py`** (plus `runtime/string_ops.py`). It implements `truth`, testimony, rendering and JSON. It is two things at once:
  - **embedded** in the Rust binary with `include_str!` and written next to generated code (ahead of `sys.path`), so `.ity` programs need no install and always get the matching runtime;
  - **a pip-installable Python package**, `verity-testimony` (`runtime/pyproject.toml`), so plain Python code and pytest can use testimony without `.ity` files.
- Python can't overload `and`, `or` or `not`, so the compiler rewrites them, along with comparisons, quantifiers and `because`, into testimony-composing runtime calls.

### Python interop rules

1. **Python to Verity:** plain `bool` results from Python code are lifted into truths with minimal testimony, e.g. `name.isalnum() returned False`.
2. **Verity to Python:** `Truth` implements `__bool__`, so it works in `if`, `while`, `all()` and similar. Code that strictly needs a `bool` (`json.dumps`, `isinstance(x, bool)`) calls `to_bool(t)`.
3. **Non-bool comparisons pass through untouched.** If a comparison returns something that isn't a `bool` (numpy arrays, pandas series), the runtime returns it unchanged instead of wrapping it. This needs a test from milestone 2 onwards.
4. **Non-truth operands of `and`/`or`** (neither a truth nor a `bool`) get Python semantics, so `name or "anonymous"` still works.
5. **Python is a runtime requirement.** The `verity` binary itself is standalone.

## Build milestones (in order)

1. **Runtime library:** `runtime/testimony.py` and `runtime/string_ops.py`. It covers `Truth`, the node kinds, combinators (comparison, `and`/`or`/`not`, `because`, `forall`/`exists`, `all_of`, lifting), `reason`, `secret`/`reveal`, `explain` with audiences, `to_json`, bounds, `to_bool` and `TestimonyError`. It is packaged as `verity-testimony`, with `unittest` tests in `runtime/tests/`.
2. **Tiny language:** literals, names, calls, attributes, arithmetic, comparisons, `and`/`or`/`not`, assignment, `def`/`return`, `if`/`for`/`while`, imports and f-strings, lexed, parsed and compiled to Python by the Rust compiler. Includes `verity run`, `verity compile` and `verity check --json`, with the `True`/`False` diagnostic and its fix.
3. **`forall`/`exists`, `because`/`reason`, `assert`:** source spans in testimony, `verity test` with `--json`, and traceback mapping to `.ity` lines.
4. **pytest plugin and `@testify`:** `pytest-verity`, which explains failing asserts (including `all()`/`any()` over generators) with testimony, plus a `@testify` decorator for plain Python predicate functions.
5. **Python coverage:** classes and `@dataclass`, `match`, comprehensions, `lambda`, `try`/`with` and the rest of Python 3.12's syntax.
6. **Dual compilation (erasure).**
7. **Proposed: tail calls with recorded tracebacks.** Rewrite direct self-recursive tail calls into loops and keep a call counter plus the arguments of the first and last few calls, so escaped errors show a rebuilt traceback. Not spec until adopted; details at `site/public/roadmap.html`.

## The book

`book/src/*.html` holds *Verity Programming*, the reference documentation (authors: Henrik Gombos and Pranav Balakrishnan), structured like a traditional language reference with [[settled]]/[[proposed]]/[[open]] status markers. Run `python3 book/build.py` to regenerate `site/public/book/` (Vite copies it into the site build), including the plain-text `llms.txt` and `verity.txt`, and commit the generated output. Book examples must agree with this spec and with `examples/*.expected`. Rules marked proposed or open are not spec until adopted here; when a proposal is adopted, mark it settled in the docs. When a milestone changes behavior, update the affected chapters.

## Working rules

- **One milestone per session.** Don't start the next one in the same session.
- **`examples/` must pass before a milestone counts as done.** Each `examples/*.ity` must produce exactly its `.expected` output under `verity run`. An example can only be skipped if it uses features from a later milestone, and the skip must be explicit. Milestone 1 has no compiler, so its tests reproduce each example's testimony by calling the runtime directly.
- **Commit after each working milestone.**
- `cargo test` and the runtime's Python tests (`python3 -m unittest discover runtime/tests`) must pass before committing.

## Session log

Newest first. Each entry records what changed, what was decided and what is open, so the next session can start without the transcript.

### 2026-10-26: agent-first redesign, milestone 1

**Commits:** `63cc358` (spec, docs, examples), `0c31a66` (milestone 1). Earlier the same day: the docs redesign rounds (`ec6b4af` to `9e60973`).

**Decisions (from Henrik, via questions):**
- Rework Verity to be optimized for agents to read and check. Syntax is Python 3.12 plus a few keywords; the Coconut syntax is dropped.
- Ship the runtime as a pip library, `verity-testimony`. This replaces the old rule that users never install a package.
- Scope for the session: spec + docs, then milestone 1 only.
- Adopt all ten recommendations from section 7 of `research/testimony-practicality.md`:
  1. the pitch "checks that explain themselves";
  2. a pytest plugin (milestone 4);
  3. erasure by dual compilation, replacing the old "any `return` forces testimony" rule;
  4. `all_of` for reporting every failure;
  5. audiences (developer/user) and `secret()`;
  6. a published JSON schema `verity.testimony/0` with reason IDs, hints, spans and `asserted`;
  7. the pip library;
  8. bounds and determinism;
  9. a "what testimony is not" honesty section (book 5.12);
  10. non-goals.

**Done:**
- CLAUDE.md rewritten as the spec above.
- Every book chapter rewritten for the Python syntax. There is a new Section 10, Machine Interface (`book/src/machine.html`), and Implementation moved to Section 11.
- `book/build.py` also writes `site/public/book/llms.txt` and `verity.txt`.
- The examples are rewritten in Python syntax, and `examples/signup.ity` + `.expected` is new.
- Milestone 1: `runtime/testimony.py`, `runtime/string_ops.py`, `runtime/pyproject.toml` and `runtime/README.md`.
  - 54 unittest tests pass, including `runtime/tests/test_examples.py`, which rebuilds all four examples byte for byte through runtime calls.
  - The wheel builds and installs. System Python has no setuptools, so build it in a scratch venv.
- `src/runtime.rs` embeds `TESTIMONY_PY` and `STRING_OPS_PY`. `runtime/truth.py` is deleted. `cargo test` passes.
- `.gitattributes` maps `*.ity` to Python. The Coconut operators are removed from the TextMate grammar.

**Open:**
- **Milestone 2 (the Rust compiler) is next.** Start it in a new session. `verity run`/`check` don't work yet.
- **PyPI:** `verity-testimony` is not published. That needs Henrik's account, and nobody has checked whether the name is free.
- **Stale homepage mockups:** the testimony-demo variants (a–f, round 1) still show the old Coconut syntax and Fraunces text. Update them before the next homepage round. Round 1 is still waiting for Henrik's feedback.
- **Docs design:** variant docs/a is liked but not locked. Its font picker defaults to Atkinson Hyperlegible (text) and Oxygen Mono (code). The live book uses those fonts but still has the old layout. Porting the docs/a layout into `book.css` waits for Henrik's go-ahead.

**Design taste (Henrik, also in `design/taste.md`):**
- Banned fonts: JetBrains Mono, IBM Plex Mono, any monospace with the same vibe, and "square-ey" monos, including Courier Prime.
- Dislikes the "AI-ey" design most people like; it reads as sloppy to him.
- Likes docs/a: a plain-text, RFC-style layout with a margin index and an 80-column page.

**Working notes:**
- Always `git fetch` and compare with origin/main before committing.
- Design rounds follow `design/PROCESS.md`: record feedback verbatim and dated in `design/taste.md`, then stop and wait after each round.
- `design/render.py` renders variants to `site/public/design/`, and headless Chrome takes screenshots.
- npm needs a cache directory in the scratchpad.
