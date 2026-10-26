# How practical is testimony? A skeptical review of booleans that carry evidence

*Research report, October 2026. Part 2 of 2. The companion report is [language-fitness.md](language-fitness.md).*

**How to read this report.** Every factual claim has an inline link to a source I opened and checked. Paragraphs marked **(inference)** are my own reasoning. Three small experiments I ran are labelled **(my measurement)**, with versions and hardware given. Verity's behaviour is taken from `CLAUDE.md`, `examples/*.expected` and the book chapters `book/src/testimony.html` and `book/src/stdlib.html` in this repository.

---

## Executive summary

1. **The idea has strong ancestry, but Verity's version is runtime explanation, not proof.** Harper's "Boolean blindness" essay says a Boolean has "no information… beyond its value." It defines truth as having a proof and falsity as having a refutation, the same vocabulary Verity uses ([Harper 2011](https://existentialtype.wordpress.com/2011/03/15/boolean-blindness/)). Agda's standard library even names its decision constructor `_because_`, pairing a `does : Bool` with a `proof` ([agda-stdlib](https://github.com/agda/agda-stdlib/blob/master/src/Relation/Nullary/Decidable/Core.agda)). But proof assistants *erase* proofs at runtime ([Lean reference](https://lean-lang.org/doc/reference/latest/Basic-Types/Booleans/)). Verity keeps evidence at runtime for humans, and `because` text is an unchecked claim. It should be marketed as **explanation**, not as proof.
2. **The most valuable, least-served use case is explaining quantified checks in tests.** pytest 9.1.1 explains `and` and comparisons but prints only `assert False` for `all(...)`/`any(...)` over a generator **(my measurement)**. Its issue asking to unroll `all`/`any` has been open since 2019, and an implementation was reverted after it caused NameErrors and wrong results ([#5062](https://github.com/pytest-dev/pytest/issues/5062), [#5373](https://github.com/pytest-dev/pytest/pull/5373)). Verity's `forall`/`exists` testimony closes this exact gap.
3. **For validation, Verity's current semantics are worse than incumbents.** Verity's `and` reports only the first failing conjunct ([CLAUDE.md](../CLAUDE.md)). Cats `Validated` exists precisely because fail-fast "will have the downside of showing only the first error" ([Cats docs](https://typelevel.org/cats/datatypes/validated.html)). pydantic returns *all* errors with `loc`/`type`/`msg`/`input` fields ([pydantic docs](https://pydantic.dev/docs/validation/latest/errors/errors/)), and so do zod ([zod](https://zod.dev/error-formatting)) and pandera's `lazy=True` ([pandera](https://pandera.readthedocs.io/en/stable/lazy_validation.html)). Verity needs an accumulating conjunction to compete here.
4. **Erasure is essential, and as currently specified it will rarely fire.** In my CPython prototype, eager testimony for a three-clause check cost about 16× a plain boolean expression (1,114 ns vs 69 ns). Merely boxing the result in a `Truth` object cost about 2.9× **(my measurement)**. The book's draft rules treat any `return` of a truth as "observed" ([book §Observation](../book/src/testimony.html)), so ordinary predicate functions such as `valid_username` always pay. Prior art shows the fix: separate the value from the evidence (Agda's `does`/`proof` split exists for "better computational behaviour"), or recompute evidence only on demand (icontract re-executes the condition's AST only when it fails; [icontract docs](https://icontract.readthedocs.io/en/latest/usage.html)).
5. **Explanations leak.** OWASP requires generic login failures ("Login failed; Invalid user ID or password") to prevent account enumeration ([OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)). Verity's short-circuit `and` would testify *which* conjunct failed. XACML warns that exposing policy contents lets subjects "determine how to gain unauthorized access" ([XACML 3.0 §9.2.2](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html)). pydantic has `hide_input_in_errors`, and OPA masks decision logs ([OPA](https://www.openpolicyagent.org/docs/management-decision-logs)). Verity needs redaction by design.
6. **Raw evaluation traces are not good explanations.** MYCIN's WHY/HOW rule traces could not "justify the rules" or articulate strategy ([Clancey, ch. 29](https://people.dbmi.columbia.edu/~ehs7001/Buchanan-Shortliffe-1984/Chapter-29.pdf)). Developers prefer error messages structured as arguments, but will accept weaker structure if the message gives a resolution ([Barik et al. FSE 2018](https://www.microsoft.com/en-us/research/publication/how-should-compilers-explain-problems-to-developers/)). Testimony should carry claims (`because`), grounds (operand values) and, ideally, hints.
7. **Most mature explanation systems are opt-in, leveled and structured.** OPA's `explain=notes|fails|full|debug` is a query parameter, and instrumentation "can add significant overhead" ([OPA REST API](https://www.openpolicyagent.org/docs/rest-api)). Great Expectations has `BOOLEAN_ONLY`/`BASIC`/`SUMMARY`/`COMPLETE` result formats ([GX](https://docs.greatexpectations.io/docs/reference/learn/expectations/result_format/)). JSON Schema specifies Flag/Basic/Detailed/Verbose outputs and recommends short-circuiting in Flag mode ([JSON Schema 2020-12 §12](https://json-schema.org/draft/2020-12/json-schema-core)). Verity should copy this design.
8. **"Why not a library?" deserves an honest answer: for most uses, a library gets most of the way.** Libraries already exist. py-predicate has an `explain()` producing nested reasons, but gets about 19 downloads a month. icontract renders "x > 3: x was 1" by AST re-execution and gets about 273,000 downloads a month **(my pypistats pull)**. pytest rewrites asserts via an import hook. The language-level advantages are real but narrow: zero-API capture of *all* boolean structure, quantifiers as syntax (which pytest could not retrofit safely), compile-time source spans and static erasure.
9. **Data-quality pipelines are a poor fit.** Verity's interop rule passes numpy/pandas comparison results through *without* testimony ([CLAUDE.md](../CLAUDE.md)). Incumbents (Great Expectations, pandera) already return vectorised failure tables.
10. **Explainable end-user decisions are a real but demanding niche.** US Regulation B requires "specific and accurate" adverse-action reasons, even for complex algorithms ([CFPB Circular 2022-03](https://www.consumerfinance.gov/compliance/circulars/circular-2022-03-adverse-action-notification-requirements-in-connection-with-credit-decisions-based-on-complex-algorithms/)). The CJEU has held that GDPR explanations must cover "the procedure and principles" actually applied ([European Law Blog on C-203/22](https://www.europeanlawblog.eu/pub/lwchuopd)). Raw testimony containing source code and repr values is the wrong artefact for this audience. Stable reason codes derived from testimony could be the right one.
11. **An emerging use: machine-readable testimony as feedback for LLMs.** Instructor re-asks the model with validation errors ([Instructor docs](https://python.useinstructor.com/concepts/reask_validation/)). Self-Debugging improved code generation by up to 12% using execution feedback ([Chen et al.](https://arxiv.org/abs/2304.05128)). Structured testimony suits this loop **(inference)**.
12. **Bottom line.** Testimony is genuinely useful for **tests and specifications** (highest value), **rule-based decisions needing reason codes** (medium, with redaction and stable IDs), and **LLM/agent feedback** (emerging). It is weak for form validation (unless it accumulates errors), data-frame quality checks and authorization engines. Build the runtime as a usable Python library, add accumulating conjunction, redaction and JSON output, and integrate with pytest and Hypothesis before anything else.

---

## 1. What Verity's testimony is, and what it is not

Verity's `truth` values carry a *witness* (verity) or a *refutation* (falsity). Comparisons, `and`/`or`/`not`, `forall`/`exists` and `because` compose testimony automatically, and `explain` renders a tree ([CLAUDE.md](../CLAUDE.md); [examples/validate.expected](../examples/validate.expected)). The book specifies node kinds: comparison, all, none, not, because, counterexample, universal, witness, no-element, literal, lifted and text. It also gives draft observation, erasure and cost rules ([book/src/testimony.html](../book/src/testimony.html)), and a proposed `as_dict` JSON form whose nodes carry only `kind`, `line` and `children` ([book/src/stdlib.html](../book/src/stdlib.html)).

**Three distinctions frame the rest of this report (inference):**

1. **Evidence for humans vs. evidence for the program.** Harper's complaint is about *programs* losing information: "The only thing you can do with a bit is to branch on it." His remedy is to pattern-match on data that carries what you learned ([Harper](https://existentialtype.wordpress.com/2011/03/15/boolean-blindness/)). Alexis King's "parse, don't validate" makes the same point: "the difference between validation and parsing lies almost entirely in how information is preserved," and a validator returning `()` "just throws it away" ([King 2019](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/)). Verity's testimony is mainly evidence for *humans* (rendered text). Unless `exists` hands the witness value back to the program in a usable way, testimony does not cure boolean blindness in Harper's sense. It cures *explanation* blindness.
2. **Proof vs. testimony.** In Curry–Howard systems, the type checker *checks* evidence, then throws it away. Lean's reference: "both propositions and their proofs are erased in the code generator," while `Bool` "carries precisely one bit of run-time information" ([Lean reference](https://lean-lang.org/doc/reference/latest/Basic-Types/Booleans/)). Verity's evidence is never checked. `verity because "it was built as a Square"` is a claim the runtime accepts at face value ([examples/shapes.ity](../examples/shapes.ity)). Computed testimony (comparison operands, quantifier positions) is trustworthy. Asserted testimony (`because`) is only as trustworthy as its author.
3. **Certificates vs. narratives.** Certifying algorithms produce, with each output, "a certificate or witness (easy-to-verify proof) that the particular output has not been compromised by a bug," which a checker can validate ([McConnell et al., *Certifying algorithms*, abstract](https://researchportalplus.anu.edu.au/en/publications/certifying-algorithms/)). A Verity witness from `exists` *is* a certificate: you can re-check `p(x)` for the reported `x`. A Verity verity from `forall` is a *count* ("all 4 elements … satisfy"), which cannot be re-checked without re-running the whole check.

---

## 2. Prior art

### 2.1 Type theory: decision procedures that return evidence

- **Agda.** `record Dec (A : Set a) where constructor _because_; field does : Bool; proof : Reflects A does`. The library comment explains the split: it "allows the boolean part of the decision procedure to compute independently from the proof. This leads to better computational behaviour when we only care about the result and not the proof" ([agda-stdlib source](https://github.com/agda/agda-stdlib/blob/master/src/Relation/Nullary/Decidable/Core.agda)). This is the closest prior art to Verity, down to the keyword, and it already contains the answer to Verity's erasure problem (§3.1).
- **Lean 4.** `class inductive Decidable (p : Prop) | isFalse (h : ¬p) | isTrue (h : p)`. `if p then a else b` requires `Decidable p` ([Theorem Proving in Lean 4](https://lean-lang.org/theorem_proving_in_lean4/Type-Classes/)). `Decidable.decide` "converts a proof-carrying Decidable result into a Bool" ([Lean reference](https://lean-lang.org/doc/reference/latest/Basic-Types/Booleans/)).
- **Rocq/SSReflect.** `reflect P b` asserts that the proposition `P` "holds iff the formula b : bool is equal to true." Such lemmas are called "views" ([Rocq ssrbool](https://rocq-prover.org/doc/v8.19/stdlib/Coq.ssr.ssrbool.html)).
- **Idris 2.** Quantitative Type Theory lets a type "state clearly… which arguments are erased." Brady motivates it by noting that in Idris 1 it was often unclear which arguments were erased at run time ([Brady, ECOOP 2021](https://arxiv.org/abs/2104.00480)). **Inference:** Verity's implicit, analysis-driven erasure risks the same unpredictability. Users will not know when they are paying for testimony.

### 2.2 Validation that accumulates errors

| Library | What it returns | Accumulates? |
|---|---|---|
| Haskell `validation` | "A data type like `Either` but with an accumulating `Applicative` instance" ([Hackage](https://hackage.haskell.org/package/validation)) | Yes |
| Scala Cats `Validated` | Applicative, deliberately not a monad, so all errors are reported; a fail-fast `Either` "will have the downside of showing only the first error" ([Cats](https://typelevel.org/cats/datatypes/validated.html)) | Yes |
| pydantic | `ValidationError.errors()`: list of `{type, loc, msg, input, ctx, url}`; `.json()`; options `include_input`, `include_context`, `include_url`; config `hide_input_in_errors` ([pydantic errors](https://pydantic.dev/docs/validation/latest/errors/errors/); [ConfigDict](https://docs.pydantic.dev/latest/api/config/)) | Yes |
| zod | `issues: [{code, path, message}]`, plus `treeifyError`, `prettifyError`, `flattenError` ([zod](https://zod.dev/error-formatting)) | Yes |
| pandera | `lazy=True` collects all failures into a `failure_cases` DataFrame ([pandera](https://pandera.readthedocs.io/en/stable/lazy_validation.html)) | Opt-in |
| clojure.spec | `explain-data` returns problems with `:path :pred :val :via :in` ([Clojure spec guide](https://clojure.org/guides/spec)) | Yes |

**Inference.** Every mature validator (1) accumulates errors, (2) reports a *data path* (`loc`, `path`, `:in`) separately from the *rule* that failed (`type`, `code`, `:pred`), and (3) offers machine-readable output. Verity's `forall` already reports a position (`primes[0]`), but its `and` is fail-fast and its proposed JSON carries only rendered lines.

### 2.3 Testing: counterexamples, shrinking and assertion rewriting

- **QuickCheck** introduced random property testing of Haskell functions ([Claessen & Hughes, ICFP 2000](https://www.cs.tufts.edu/comp/150FP/archive/john-hughes/quick.pdf)). **Hypothesis** brought it to Python ([Hypothesis docs](https://hypothesis.readthedocs.io/en/latest/)). It reduces failures by working on the sequence of random choices made during generation, rather than shrinking finished test inputs ([MacIver & Donaldson, ECOOP 2020](https://www.doc.ic.ac.uk/~afd/papers/2020/ECOOP_Hypothesis.pdf)).
- **pytest** "rewrites test modules on import by using an import hook," but "only rewrites test modules directly discovered by its test collection process." Rewriting can be extended with `register_assert_rewrite` ([pytest docs](https://docs.pytest.org/en/stable/how-to/assert.html)).
- **Power assert.** Groovy's `assert` prints the value of every subexpression and is "enabled by default" ([Groovy testing guide](https://groovy-lang.org/testing.html)). power-assert-js's slogan is "No API is the best API." It requires transforming test code through AST instrumentation ([power-assert](https://github.com/power-assert-js/power-assert)). Kotlin 2.0 shipped an experimental Power-assert *compiler plugin*. It transforms `assert()` by default (and optionally `require`, `check`, `assertTrue`), and applies to test source sets unless configured otherwise ([Kotlin docs](https://kotlinlang.org/docs/power-assert.html); [What's new in Kotlin 2.0](https://kotlinlang.org/docs/whatsnew20.html)).
- **Contracts.** icontract's violation message includes "the source code of the contract condition as well as variable values at the time of the breach." An example is `x must not be small: x > 3: x was 1`, which is strikingly close to Verity's `because`. It gets those values "by re-executing the condition function programmatically by traversing its abstract syntax tree," which is why conditions must be side-effect-free ([icontract docs](https://icontract.readthedocs.io/en/latest/usage.html)).

**My measurement (pytest 9.1.1, Hypothesis 6.170.11, CPython 3.12.10).**

```text
assert len(name) >= 3 and name.isalnum()      ->  assert (2 >= 3)  +  where 2 = len('al')
assert all(x % 2 == 1 for x in xs)            ->  assert False  +  where False = all(<generator object ...>)
@given(st.lists(st.integers())) assert all(x < 100 for x in xs)
                                              ->  Falsifying example: xs=[100]   ...   assert False
```

pytest explains Boolean structure well but cannot explain quantifiers. Hypothesis finds a minimal counterexample but cannot say *which element* failed or *why*. The pytest feature request ([#5062](https://github.com/pytest-dev/pytest/issues/5062), opened April 2019, still open) shows this exact output. An `all()`-unrolling implementation was merged and then reverted in June 2019 ([#5373](https://github.com/pytest-dev/pytest/pull/5373)) after reports titled "Assertions on nested comprehensions can give NameError" and "all(...) rewrite produces incorrect results" ([#5370](https://github.com/pytest-dev/pytest/issues/5370), [#5372](https://github.com/pytest-dev/pytest/issues/5372)).

Under the spec, Verity would render the equivalent as follows (format from [examples/counterexample.expected](../examples/counterexample.expected)):

```text
falsity
  counterexample: x = 100 (xs[0])
    x < 100: 100 >= 100
```

**Inference.** This is the strongest evidence in either report that testimony fills a real, felt, unsolved need. It is also strong evidence for the *language-level* approach. pytest's rewrite failed because `all` is just a name, generator scoping is subtle, and semantics must be preserved exactly. A dedicated `forall` syntax does not have those problems.

### 2.4 Rule engines, policy languages and authorization

- **MYCIN** (1970s) let users ask WHY (the rule being evaluated) and HOW (how a conclusion was reached) via simple commands ([Buchanan & Shortliffe, ch. 15](https://people.dbmi.columbia.edu/shortliffe/Buchanan-Shortliffe-1984/Chapter-15.pdf)). Clancey later found that these traces fell short for teaching: "GUIDON cannot justify the rules because MYCIN does not have an encoding of how the concepts in a rule fit together," and strategy was "implicit in the ordering of rule concepts" ([Clancey, ch. 29](https://people.dbmi.columbia.edu/~ehs7001/Buchanan-Shortliffe-1984/Chapter-29.pdf)).
- **OPA/Rego.** The REST API offers `explain` with values `notes`, `fails`, `full` and `debug`: "Return query explanation in addition to result." Instrumentation "can add significant overhead," and OPA recommends leaving it off unless debugging ([OPA REST API](https://www.openpolicyagent.org/docs/rest-api)). Decision logs record input, result, decision ID and bundle revision. A `system.log.mask` policy can erase or overwrite sensitive fields before upload ([OPA decision logs](https://www.openpolicyagent.org/docs/management-decision-logs)).
- **Cedar.** Responses carry a decision plus diagnostics. The diagnostics list the *determining policies* (the satisfied `permit`s for Allow, the satisfied `forbid`s for Deny) and the IDs of policies that errored ([Cedar docs](https://docs.cedarpolicy.com/auth/authorization.html)). Cedar was designed so policies are "efficiently analyzable by reduction to SMT" ([Cedar paper, OOPSLA 2024](https://arxiv.org/abs/2403.04651)). **Inference:** Cedar explains at the granularity of *policy IDs*, not expression trees. That is coarse, cheap and safer to expose.
- **XACML 3.0** offers `<StatusDetail>` (e.g. missing attributes) and advice/obligations. Its security section warns: "If the contents of policies are exposed outside of the access control system, potential subjects may use this information to determine how to gain unauthorized access." It adds that missing-attribute details should be returned "only when exposure of the identities of those attributes will not compromise security" ([XACML 3.0 core](https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html)).
- **AWS IAM** access-denied messages name a policy type that caused the denial, but when several policies deny, the message "doesn't specify the number of policies evaluated" ([AWS docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html)). Real systems deliberately limit how much explanation they expose.

### 2.5 Provenance, query plans, model checking and solvers

- **Why-provenance** identifies the source data that influenced an output, while where-provenance identifies the locations it was copied from ([Buneman, Khanna & Tan, ICDT 2001](https://repository.upenn.edu/cis_papers/210)). **Provenance semirings** unify why-provenance, bag semantics and probabilistic databases as annotations in a commutative semiring ([Green, Karvounarakis & Tannen, PODS 2007](https://www.cs.ucdavis.edu/~green/papers/pods07.pdf)).
- **Soufflé** builds provenance proof trees lazily on query and shows trees of minimal height, with `setdepth` limits. For *non-existence* it says "it is not technically feasible to automatically generate explanations," so the user must supply the rule and values ([Soufflé provenance](https://souffle-lang.github.io/provenance)). Tracking provenance annotations cost "1.27x on average" at the scale of tens of millions of tuples ([Zhao, Subotić & Scholz](https://arxiv.org/abs/1907.05045)). **Inference:** this asymmetry applies directly to Verity. A refutation of `exists` (and a witness for `forall`) is a universal statement. It can only be summarised ("no element of row satisfies…") or made expensive. The book's draft `no-element` and `universal` nodes already summarise, which is the right choice.
- **SQL EXPLAIN** is opt-in, and `EXPLAIN ANALYZE` "actually executes the query." Its "measurement overhead … can be significant" ([PostgreSQL docs](https://www.postgresql.org/docs/current/using-explain.html)).
- **Model checkers** return counterexample traces. "TLC's default breadth-first search (BFS) ensures shortest-length counter-examples and is most informative for debugging" ([Cirstea, Kuppe, Loillier & Merz 2024](https://arxiv.org/abs/2404.16075)). **SMT solvers** return unsat cores, and Z3's guide shows how to enumerate *minimal* cores ([Z3 guide](https://microsoft.github.io/z3guide/programming/Example%20Programs/Cores%20and%20Satisfying%20Subsets/)). **Inference:** both stress *minimality*. A good explanation is the smallest sufficient one. Verity's "first counterexample" is cheap but not minimal; Hypothesis's shrinking is.

### 2.6 Standards for structured explanation output

- **JSON Schema 2020-12 §12.** An output "MUST be an object containing a boolean property named 'valid'." Four structures (Flag, Basic, Detailed, Verbose) carry `keywordLocation`, `absoluteKeywordLocation`, `instanceLocation` and an error or annotations. For Flag it is "RECOMMENDED that implementations use short-circuiting logic," and message wording is left to implementations "tailored for their audience" ([JSON Schema core](https://json-schema.org/draft/2020-12/json-schema-core)).
- **Great Expectations** offers `result_format` levels `BOOLEAN_ONLY` (no result), `BASIC` (counts plus a partial list of unexpected values), `SUMMARY` (the default) and `COMPLETE` (full lists and index queries) ([GX docs](https://docs.greatexpectations.io/docs/reference/learn/expectations/result_format/)).

**Inference.** These two standards are the best templates for Verity's testimony API. They have (a) a value-only mode that permits short-circuiting and erasure, (b) graded verbosity, and (c) separate pointers into the *rule* (Verity: source span of the expression) and into the *data* (Verity: `xs[0]`, field paths).

---

## 3. Practical concerns

### 3.1 Performance and erasure

**My measurement** (Apple M3, CPython 3.12.10, naive prototype in which each truth is a `__slots__` object holding a tuple node):

| Variant | Cost |
|---|---|
| Plain Python `len(n) >= 3 and len(n) <= 16 and n.isalnum()` | 69 ns/call |
| Same, wrapped in a `Truth` object with no testimony | 197 ns/call (≈2.9×) |
| Eager testimony (comparison nodes plus `all` node, lambdas for short-circuit) | 1,114 ns/call (≈16×) |
| `all(x % 2 == 1 for x in xs)`, 1,000 elements | 42 µs |
| Same with a per-element `Truth` and counterexample bookkeeping | 197 µs (≈4.7×) |

A tuned runtime would do better than this prototype, but the shape of the result is robust **(inference)**. Building testimony costs an order of magnitude more than a plain boolean expression, and even the wrapper alone is expensive. So "erased" must mean *plain Python booleans*, not `Truth(value, None)`.

**When does erasure actually fire?** The book's draft says testimony is observed if a truth reaches "a `return` statement, `yield`, or the value of a short-form `def`," or "an argument to any function that the compiler cannot see into, including all Python functions." Only uses as `if`/`while`/guard conditions are unobserved ([book/src/testimony.html](../book/src/testimony.html)). The canonical Verity predicate, `def valid_username(name) = ... and ...`, *returns* its truth, so it is always observed and always pays the 16× cost, even when every caller writes `if valid_username(n):` **(inference)**. In practice, erasure will mostly fire on inline `if` conditions, which are already cheap.

**Fixes from prior art:**
1. **Value/evidence split (Agda).** Compile every truth-returning function twice: a `_value` version returning `bool`, and a `_testify` version returning `Truth`. Call sites in condition position call the value version. That is the Agda `does`/`proof` design, which exists "when we only care about the result and not the proof" ([agda-stdlib](https://github.com/agda/agda-stdlib/blob/master/src/Relation/Nullary/Decidable/Core.agda)).
2. **Lazy re-execution (icontract).** Return a plain bool and recompute the testimony only when someone asks (`explain`, attribute access). This is cheap on the happy path, but it requires the expression to be pure and its inputs unchanged ([icontract](https://icontract.readthedocs.io/en/latest/usage.html)). Soufflé also builds proof trees lazily on query ([Soufflé](https://souffle-lang.github.io/provenance)).
3. **Explicit opt-in (OPA, EXPLAIN, Kotlin's TESTS-only default).** Every production-grade explainer reviewed here makes full explanation opt-in or test-scoped ([OPA](https://www.openpolicyagent.org/docs/rest-api); [PostgreSQL](https://www.postgresql.org/docs/current/using-explain.html); [Kotlin](https://kotlinlang.org/docs/power-assert.html)).
4. **Predictability (Idris 2).** Make erasure visible: a compiler flag or lint that reports "testimony constructed here" ([Brady](https://arxiv.org/abs/2104.00480)).

### 3.2 Memory, retention and mutation

The book's draft cost model says an observed comparison "holds references to its two operands" ([book](../book/src/testimony.html)). **Inference, with three consequences:**
- **Retention.** Truths that are stored (in a list of results, a cache or a log record) keep large operands alive, such as DataFrames or request bodies.
- **Mutation.** If an operand is a mutable object and it changes before `explain` runs, the rendered `repr` shows the *later* state, so the testimony lies. pytest avoids this by formatting at failure time. Verity should snapshot `repr` (bounded length) at construction, or document the hazard.
- **Sensitive data at rest.** Retained operands are retained secrets (§3.4).

### 3.3 Testimony explosion in loops and recursion

- The book's draft bounds quantifiers to "only the deciding element (or, for `universal`, a count)" and says conjunctions grow "with the number of operands, not with the number of evaluations of an enclosing loop" ([book](../book/src/testimony.html)). That is sound.
- **Unbounded cases remain (inference).** A recursive predicate (`def sorted_(xs) = len(xs) < 2 or (xs[0] <= xs[1] and sorted_(xs[1:]))`) builds testimony of depth *n* on a verity, since `and`-verities keep all conjuncts. A user-written loop that folds truths with `and` grows linearly. Soufflé and GX answer this with depth limits (`setdepth`) and partial lists (`partial_unexpected_list`) ([Soufflé](https://souffle-lang.github.io/provenance); [GX](https://docs.greatexpectations.io/docs/reference/learn/expectations/result_format/)). Verity should cap depth and width in `explain` and say "(17 more…)".
- **Polarity asymmetry.** Testimony for the *deciding* side is small: one counterexample for `forall`-false, one witness for `exists`-true. Testimony for the universal side is either a summary or huge. Soufflé's note on non-existence is the general version of this point ([Soufflé](https://souffle-lang.github.io/provenance)).

### 3.4 Privacy and security

- **Enumeration via short-circuit testimony (inference, grounded in OWASP).** OWASP: "an application must respond with a generic error message regardless of whether" the user ID or password was wrong, the account does not exist, or it is locked. It also warns that processing-time differences create a "discrepancy factor" ([OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)). `user_exists(u) and password_ok(u, p)` in Verity produces testimony naming the failing conjunct and quoting the operands. If that testimony reaches a response or a client-visible log, it is an enumeration oracle. Short-circuiting is also a timing channel, though that is true of plain Python too.
- **Policy disclosure.** XACML §9.2.2 (quoted in §2.4) and AWS's deliberately limited deny messages ([AWS](https://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html)) show that authorization explanations are routinely *withheld* from the requester, even when they are logged for administrators.
- **Values in explanations.** pydantic shows `input_value=…` by default and offers `hide_input_in_errors` and `include_input=False` ([pydantic](https://docs.pydantic.dev/latest/api/config/)). OPA masks decision-log fields by policy ([OPA](https://www.openpolicyagent.org/docs/management-decision-logs)). Verity's comparison nodes quote evaluated operands with `repr()` by design ([book](../book/src/testimony.html)), so a password comparison would print the password.
- **Regulated explanations demand the opposite.** GDPR Article 22 gives people the right not to be subject to decisions "based solely on automated processing" with legal or similarly significant effects, subject to exceptions with safeguards including the right "to contest the decision" ([GDPR Art. 22](https://gdpr-info.eu/art-22-gdpr/)). Credit regulators require specific reasons ([CFPB](https://www.consumerfinance.gov/compliance/circulars/circular-2022-03-adverse-action-notification-requirements-in-connection-with-credit-decisions-based-on-complex-algorithms/)). The CJEU requires an intelligible account of "the procedure and principles" applied, and lets trade secrets go to a court or authority for balancing ([European Law Blog](https://www.europeanlawblog.eu/pub/lwchuopd)). **Inference:** one explanation cannot serve the end user, the auditor and the developer. Verity needs *audiences*, each with its own redaction.

### 3.5 Readability and how people actually consume explanations

- Developers do read error messages. In an eye-tracking study, reading them took 13–25% of task time, and reading difficulty "significantly predicts participants' task performance" ([Barik et al. ICSE 2017, via Never Work in Theory](https://neverworkintheory.org/2021/09/20/do-developers-read-compiler-error-messages.html)).
- Barik et al. (FSE 2018, 68 professional developers) found that developers prefer messages with proper argument structure (Toulmin-style), but accept weaker structure if the message "provides a resolution to the problem" ([MSR page](https://www.microsoft.com/en-us/research/publication/how-should-compilers-explain-problems-to-developers/)).
- A 2019 ITiCSE working group surveyed the error-message literature (Becker et al., DOI [10.1145/3344429.3372508](https://doi.org/10.1145/3344429.3372508)). Its recommendations include increasing readability, reducing cognitive load, providing context, using a positive tone, showing solutions or hints, and using logical argumentation ([review](https://neverworkintheory.org/2021/09/02/compiler-error-messages-considered-unhelpful.html)).
- Elm's "Compiler Errors for Humans" and Rust's Elm-inspired redesign show that investing in explanation UX pays off in reputation ([Elm](https://elm-lang.org/news/compiler-errors-for-humans); [Rust](https://blog.rust-lang.org/2016/08/10/Shape-of-errors-to-come.html)).

**Inference, applied to Verity's format:**
- Testimony trees map naturally onto Toulmin arguments: the claim is the `because` message, the grounds are the comparison operands, and the warrant is the source expression. That is a good foundation. What is missing is a **resolution** slot (a hint such as "use 3–16 letters or digits").
- **Polarity confusion.** `because m` renders as `witnessed: m` or `refuted: m`, where `m` states the claim ([CLAUDE.md](../CLAUDE.md)). Authors will naturally write negative messages on falsities (`falsity because "not a square"`), which renders as `refuted: not a square` and reads as the opposite of what was meant. The shapes example already reads oddly: `refuted: Circle(r=1) is a rectangle` ([examples/shapes.expected](../examples/shapes.expected)). Consider a lint for negations inside `because` strings, or let authors attach separate success and failure messages.
- **Source text is for developers, not end users.** `len(name) >= 3: 2 < 3` is excellent in a test log and baffling on a sign-up form.

---

## 4. Use cases ranked by value

Ranking criteria: size of the unmet need, how much better built-in testimony is than the incumbent, and fit with Verity's semantics. All rankings are **inference** from the evidence above.

| Rank | Use case | Incumbents and how they do it | Does language-level testimony beat a library? | Verdict |
|---|---|---|---|---|
| 1 | **Tests, properties, specifications** | pytest (assert rewriting), Hypothesis (shrinking), icontract (contract messages), Pyret `check` blocks | **Yes, partly.** Quantifier explanation is unsolved in pytest after 7 years and a failed retrofit (#5062/#5373). Zero-API capture of all boolean structure inside helper predicates, not just in `assert` lines, is something pytest does not do outside test modules. | **High.** Build this first, integrated *with* pytest and Hypothesis |
| 2 | **Rule-based decisions needing reasons** (eligibility, pricing, underwriting rules, feature gating) | Hand-written reason codes; business-rules engines; regulatory adverse-action workflows | **Somewhat.** `because` plus automatic composition gives reason trees "for free" from ordinary code. But regulators need *stable reason codes* and audience-appropriate wording, not source text ([CFPB](https://www.consumerfinance.gov/compliance/circulars/circular-2022-03-adverse-action-notification-requirements-in-connection-with-credit-decisions-based-on-complex-algorithms/)) | **Medium**, if Verity adds reason IDs, redaction and accumulating conjunction |
| 3 | **LLM/agent output checks and repair loops** | pydantic plus Instructor re-ask ([Instructor](https://python.useinstructor.com/concepts/reask_validation/)); eval frameworks | **Marginally.** JSON testimony is good feedback (execution feedback helps: [Chen et al.](https://arxiv.org/abs/2304.05128)), but pydantic errors already serve the loop | **Medium, emerging.** A good demo domain |
| 4 | **Teaching logic and specification** | Pyret, Racket teaching languages, proof assistants | **Yes for pedagogy.** Witnesses and counterexamples for `forall`/`exists` are exactly what discrete-maths students need to see | **Medium** (small market, good fit) |
| 5 | **Input and form validation** | pydantic, zod, Cats `Validated` | **No, currently.** Fail-fast `and` loses to accumulate-all, and incumbents have paths, codes, JSON and redaction | **Low** unless an accumulating `all_of` is added |
| 6 | **Authorization and policy audit** | OPA (explain, decision logs, masking), Cedar (determining policies, SMT analysis), XACML | **No.** Policy engines need analyzability, termination and separation from app code. Verity compiles to arbitrary Python. Testimony also raises leakage risk | **Low** as an engine; acceptable for app-internal audit logs with redaction |
| 7 | **Production debugging** | Logging, tracing, OPA-style decision logs | **Weak.** Overhead (§3.1), retention (§3.2), privacy (§3.4). Useful only with sampling and opt-in | **Low** |
| 8 | **Data-quality pipelines** | Great Expectations, pandera (vectorised failure tables) | **No.** Verity passes numpy/pandas comparisons through without testimony ([CLAUDE.md](../CLAUDE.md)), and per-row testimony would be far too slow anyway | **Very low** |

---

## 5. "Why not just a library?": an honest answer

### 5.1 What a Python library can already do

- **Explicit combinators.** py-predicate's `explain(ge_p(2) & le_p(5), 8)` returns `{'reason': 'Right predicate failed', 'right': {'reason': 'Expected 8 <= 5'}}`, and its compiled predicates delegate explanation to the original ([py-predicate](https://github.com/mrijk/py-predicate)). That is testimony with erasure, as a library. PyHamcrest's `all_of`/`any_of` matchers print "Expected: … got: …" ([PyHamcrest](https://github.com/hamcrest/PyHamcrest)).
- **AST re-execution.** icontract recovers the source and every subexpression value from a plain lambda ([icontract](https://icontract.readthedocs.io/en/latest/usage.html)).
- **Import-hook rewriting.** pytest rewrites whole modules ([pytest](https://docs.pytest.org/en/stable/how-to/assert.html)). A `@testify` decorator or import hook could, in principle, rewrite every `and`/`or`/`not`/comparison in selected Python functions into testimony-building calls. That is what Verity's compiler does, but for ordinary `.py` files.

**Adoption signal (my pypistats pull, 30 days to 26 Oct 2026):** py-predicate ≈ 19 downloads, icontract ≈ 273,000, PyHamcrest ≈ 2.6 million, pydantic ≈ 842 million, pytest ≈ 762 million ([pypistats](https://pypistats.org/packages/icontract)). **Inference:** generic "explainable predicate" libraries have not found demand. Explanation succeeds when it is embedded in a tool people already need (a test runner, a validator, a contract checker). That is a warning for a language whose pitch is generic explainable booleans.

### 5.2 What only a language (or compiler) can do

1. **Zero-API, pervasive capture.** Every comparison and connective in every function testifies, with no wrapper types and no lambdas. power-assert's "No API is the best API" ([power-assert](https://github.com/power-assert-js/power-assert)) and Kotlin's move to a compiler plugin ([Kotlin](https://kotlinlang.org/docs/power-assert.html)) show that the industry values this.
2. **Quantifiers as syntax.** `forall`/`exists` have fixed semantics that the compiler controls. pytest's attempt to infer them from `all(<genexpr>)` broke on scoping and shadowing and was reverted ([#5373](https://github.com/pytest-dev/pytest/pull/5373)).
3. **Static knowledge.** Source spans and expression text are known at compile time, at no runtime cost. Erasure decisions can be made statically, and testimony can cross function boundaries without the caller wrapping anything.
4. **Python cannot do this natively.** Overloadable `and`/`or`/`not` were rejected ([PEP 335](https://peps.python.org/pep-0335/)), so a plain library cannot intercept connectives without AST rewriting.

### 5.3 What a library does better

No new file type, toolchain or editor support. It works in existing code, with existing type checkers, debuggers and coverage tools, and it can be adopted gradually by one function at a time.

### 5.4 Verdict (inference)

- For **validation, policy, data quality and production debugging**, a library or existing tool delivers most of the value. Verity offers no decisive advantage there.
- For **tests and specifications that use quantifiers**, and for **code where every predicate should explain itself without ceremony**, the compiler-level approach is genuinely better. The evidence is the failed pytest retrofit and the open issue.
- **Therefore**, the testimony *runtime* should exist as a first-class Python library (a `Truth` type, combinators, quantifier helpers, `explain`/`as_dict`), with an optional decorator that rewrites a plain Python function. The Verity *language* is the best way to write testimony-heavy code, not the only way. This maximises trialability (Part 1, §1.2) and lets Verity's ideas spread even if few people adopt `.ity` files.

---

## 6. Design implications for Verity's testimony

### 6.1 Copy from prior art

1. **Value/evidence split** (Agda `does`/`proof`): compile value-only and testimony variants of every truth-returning function (§3.1).
2. **Graded output** (JSON Schema Flag/Basic/Detailed/Verbose; GX `BOOLEAN_ONLY`…`COMPLETE`; OPA `explain=`): `explain(t, level="fails"|"summary"|"full")`.
3. **Two pointers per node** (JSON Schema `keywordLocation` + `instanceLocation`; pydantic `type` + `loc`; spec `:pred` + `:in`): a *rule pointer* (file, line and column span, expression text, optional rule ID) and a *data pointer* (`xs[0]`, `user.address.zip`).
4. **Accumulate-all mode** (Cats `Validated`, pydantic, pandera `lazy=True`): an explicit non-short-circuiting conjunction (`all_of(...)` or a keyword such as `also`) that evaluates every conjunct and reports every failure. Keep `and` short-circuiting, since it must match Python's evaluation semantics.
5. **Redaction** (pydantic `hide_input_in_errors`/`include_input`; OPA `system.log.mask`): mark values as sensitive (`secret(x)`, or a `@redact` field annotation on `data` types) and render them as `<redacted>` in every non-developer audience.
6. **Bounded rendering** (Soufflé `setdepth`; GX partial lists): depth and width caps with "(n more)" markers.
7. **Minimal counterexamples** (Hypothesis shrinking; TLC shortest traces; minimal unsat cores): integrate `forall x in strategy` with Hypothesis so the reported counterexample is shrunk.
8. **Lazy messages** (already in the draft: `because` messages are evaluated only when observed): keep it.
9. **Resolutions** (Barik 2018): an optional `hint` on `because`, rendered as "fix: …".

### 6.2 Pitfalls to avoid

1. **Calling testimony "proof."** It is unchecked for `because`. Document the difference between computed and asserted testimony, and consider marking asserted nodes visibly in the JSON form.
2. **Implicit, unpredictable erasure.** Provide `--report-testimony` or a lint so users know where they pay (the Idris 1 lesson).
3. **Holding live references.** Snapshot bounded `repr` strings at construction, or document the mutation hazard.
4. **Leaking through short-circuit testimony.** Default to developer-only rendering. Ship an `audience="end_user"` mode that emits only `because` messages and reason IDs, never source text or operand values.
5. **Polarity confusion in `because`.** Lint for negations, or allow separate pass and fail messages.
6. **Silently losing testimony at the Python boundary.** Interop rule 3 (numpy/pandas pass-through) and rule 1 (lifted bools carry only "returned False") mean testimony quality drops exactly where data scientists work. Say so in the docs and in `explain` output ("no testimony: value came from numpy").
7. **Trace dumps instead of explanations.** Clancey's MYCIN critique: a full evaluation trace is not a justification. Prefer `because`-led summaries, and show mechanics only on request.

### 6.3 Features that would make testimony decisively useful

1. **A pytest plugin plus Hypothesis integration** that renders testimony trees for failing `.ity` properties and for Python tests calling Verity predicates. This is the killer feature (§2.3).
2. **A structured, versioned JSON schema** for testimony, richer than the current `as_dict` draft. Include `kind`, `value`, `rule` {span, source, id}, `data_path`, `operands` (JSON-encoded or redacted), `asserted` (true for `because`), `hint` and `children`. Publish it so other tools (CI annotators, IDEs, LLM agents) can consume it.
3. **Reason codes.** `because "too short" as "USERNAME_LEN"` gives stable identifiers for regulated decisions, localisation and analytics.
4. **Audience-aware rendering**: developer (full), auditor (rules plus redacted values) and end user (reason messages only).
5. **An LLM-repair helper**: `testimony.as_feedback(t)` emits a compact, model-friendly description of what failed and where (Instructor and Self-Debug pattern).
6. **A testimony runtime usable from plain Python**, with an optional `@testify` decorator (§5.4).

---

## 7. Recommendations for Verity

All recommendations are **inference** from the evidence above, in priority order.

1. **Reframe the pitch from "booleans that testify" to "checks that explain themselves."** Lead with the pytest gap: show `assert all(...)` → `assert False` next to Verity's counterexample tree.
2. **Make the first real deliverable a pytest/Hypothesis integration**, not more Coconut syntax. Success metric: outside projects running it in CI.
3. **Fix the erasure design before writing the erasure pass.** Adopt the Agda-style value/evidence split for truth-returning functions, or lazy recomputation. Otherwise erasure will rarely fire under the draft observation rules (any `return` counts as observed), and predicate-heavy code will run about an order of magnitude slower than Python in the testimony-building paths (my measurement: 16× for a three-clause check).
4. **Add an accumulating conjunction** before marketing validation at all.
5. **Design redaction and audiences in from milestone 1.** At minimum: a `secret`/redacted value wrapper, `explain(..., audience=...)`, and no operand values in end-user output.
6. **Replace the `as_dict` draft with a published JSON schema** containing rule spans, data paths, an asserted flag, reason IDs and hints. Model it on JSON Schema's output units.
7. **Ship the runtime as a Python library** with an optional `@testify` rewriting decorator, so Python users can try testimony without `.ity` files. This conflicts with the current CLAUDE.md principle that users never install a Python package. I recommend revisiting that principle for adoption reasons (Part 1, §6).
8. **Bound everything** (depth and width caps), snapshot `repr`s, and document that `forall` reports the *first* counterexample, not the minimal one, unless Hypothesis is involved.
9. **Be honest in the book**: testimony is explanation, `because` is an unchecked claim, and some boundaries (numpy, pandas, opaque Python calls) carry little or no testimony.
10. **Do not target authorization engines or data-quality pipelines.** Incumbents are better there, and testimony adds risk (policy and data leakage) or doesn't apply (vectorised data).

---

## Sources

1. Harper, *Boolean Blindness* (2011). https://existentialtype.wordpress.com/2011/03/15/boolean-blindness/
2. King, *Parse, don't validate* (2019). https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
3. Agda standard library, `Relation.Nullary.Decidable.Core`. https://github.com/agda/agda-stdlib/blob/master/src/Relation/Nullary/Decidable/Core.agda
4. Lean Language Reference, Booleans. https://lean-lang.org/doc/reference/latest/Basic-Types/Booleans/
5. *Theorem Proving in Lean 4*, Type Classes (Decidable). https://lean-lang.org/theorem_proving_in_lean4/Type-Classes/
6. Rocq `ssrbool` (reflect). https://rocq-prover.org/doc/v8.19/stdlib/Coq.ssr.ssrbool.html
7. Brady, *Idris 2: Quantitative Type Theory in Practice* (ECOOP 2021). https://arxiv.org/abs/2104.00480
8. McConnell, Mehlhorn, Näher & Schweitzer, *Certifying algorithms* (2011), abstract. https://researchportalplus.anu.edu.au/en/publications/certifying-algorithms/
9. Hackage `validation`. https://hackage.haskell.org/package/validation
10. Typelevel Cats, `Validated`. https://typelevel.org/cats/datatypes/validated.html
11. pydantic, error handling. https://pydantic.dev/docs/validation/latest/errors/errors/
12. pydantic, `ConfigDict` (`hide_input_in_errors`). https://docs.pydantic.dev/latest/api/config/
13. zod, error formatting. https://zod.dev/error-formatting
14. pandera, lazy validation. https://pandera.readthedocs.io/en/stable/lazy_validation.html
15. Clojure spec guide. https://clojure.org/guides/spec
16. Claessen & Hughes, *QuickCheck* (ICFP 2000). https://www.cs.tufts.edu/comp/150FP/archive/john-hughes/quick.pdf
17. Hypothesis documentation. https://hypothesis.readthedocs.io/en/latest/
18. MacIver & Donaldson, *Test-Case Reduction via Test-Case Generation* (ECOOP 2020). https://www.doc.ic.ac.uk/~afd/papers/2020/ECOOP_Hypothesis.pdf
19. pytest, assertion rewriting. https://docs.pytest.org/en/stable/how-to/assert.html
20. pytest issue #5062, PR #5373, issues #5370 and #5372. https://github.com/pytest-dev/pytest/issues/5062 · https://github.com/pytest-dev/pytest/pull/5373 · https://github.com/pytest-dev/pytest/issues/5370 · https://github.com/pytest-dev/pytest/issues/5372
21. Groovy testing guide (power assertions). https://groovy-lang.org/testing.html
22. power-assert-js. https://github.com/power-assert-js/power-assert
23. Kotlin Power-assert plugin; What's new in Kotlin 2.0. https://kotlinlang.org/docs/power-assert.html · https://kotlinlang.org/docs/whatsnew20.html
24. icontract usage docs. https://icontract.readthedocs.io/en/latest/usage.html
25. Buchanan & Shortliffe (eds.), *Rule-Based Expert Systems*, ch. 15 (EMYCIN explanation). https://people.dbmi.columbia.edu/shortliffe/Buchanan-Shortliffe-1984/Chapter-15.pdf
26. Clancey, *Extensions to Rules for Explanation and Tutoring*, ch. 29. https://people.dbmi.columbia.edu/~ehs7001/Buchanan-Shortliffe-1984/Chapter-29.pdf
27. OPA REST API (explain, instrument). https://www.openpolicyagent.org/docs/rest-api
28. OPA decision logs and masking. https://www.openpolicyagent.org/docs/management-decision-logs
29. Cedar, how authorization works. https://docs.cedarpolicy.com/auth/authorization.html
30. Cutler et al., *Cedar* (OOPSLA 2024, extended version). https://arxiv.org/abs/2403.04651
31. OASIS XACML 3.0 core specification. https://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html
32. AWS IAM, troubleshoot access denied. https://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html
33. Buneman, Khanna & Tan, *Why and Where* (ICDT 2001). https://repository.upenn.edu/cis_papers/210
34. Green, Karvounarakis & Tannen, *Provenance Semirings* (PODS 2007). https://www.cs.ucdavis.edu/~green/papers/pods07.pdf
35. Soufflé provenance documentation. https://souffle-lang.github.io/provenance
36. Zhao, Subotić & Scholz, *Provenance for Large-scale Datalog*. https://arxiv.org/abs/1907.05045
37. PostgreSQL, Using EXPLAIN. https://www.postgresql.org/docs/current/using-explain.html
38. Cirstea, Kuppe, Loillier & Merz, *Validating Traces of Distributed Programs Against TLA+ Specifications* (2024). https://arxiv.org/abs/2404.16075
39. Z3 guide, Cores and Satisfying Subsets. https://microsoft.github.io/z3guide/programming/Example%20Programs/Cores%20and%20Satisfying%20Subsets/
40. JSON Schema 2020-12 Core (§12 Output Formatting). https://json-schema.org/draft/2020-12/json-schema-core
41. Great Expectations, result format. https://docs.greatexpectations.io/docs/reference/learn/expectations/result_format/
42. OWASP Authentication Cheat Sheet. https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
43. CFPB Circular 2022-03. https://www.consumerfinance.gov/compliance/circulars/circular-2022-03-adverse-action-notification-requirements-in-connection-with-credit-decisions-based-on-complex-algorithms/
44. GDPR Article 22. https://gdpr-info.eu/art-22-gdpr/
45. European Law Blog on CJEU C-203/22 *Dun & Bradstreet Austria*. https://www.europeanlawblog.eu/pub/lwchuopd
46. Barik et al., *Do Developers Read Compiler Error Messages?* (ICSE 2017), review. https://neverworkintheory.org/2021/09/20/do-developers-read-compiler-error-messages.html
47. Barik et al., *How Should Compilers Explain Problems to Developers?* (FSE 2018). https://www.microsoft.com/en-us/research/publication/how-should-compilers-explain-problems-to-developers/
48. Becker et al., *Compiler Error Messages Considered Unhelpful* (ITiCSE-WGR 2019), DOI and review. https://doi.org/10.1145/3344429.3372508 · https://neverworkintheory.org/2021/09/02/compiler-error-messages-considered-unhelpful.html
49. Czaplicki, *Compiler Errors for Humans*. https://elm-lang.org/news/compiler-errors-for-humans
50. Rust blog, *Shape of errors to come*. https://blog.rust-lang.org/2016/08/10/Shape-of-errors-to-come.html
51. Instructor, re-asking and validation. https://python.useinstructor.com/concepts/reask_validation/
52. Chen et al., *Teaching Large Language Models to Self-Debug*. https://arxiv.org/abs/2304.05128
53. py-predicate. https://github.com/mrijk/py-predicate
54. PyHamcrest. https://github.com/hamcrest/PyHamcrest
55. pypistats (icontract; also py-predicate, pyhamcrest, pydantic, pytest via the same API). https://pypistats.org/packages/icontract
56. PEP 335 (Rejected). https://peps.python.org/pep-0335/
57. Verity repository files: `CLAUDE.md`, `examples/*.ity` and `.expected`, `book/src/testimony.html`, `book/src/stdlib.html` (local).
