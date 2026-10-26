# Language fitness: what makes programming languages survive, and what it means for Verity

*Research report, October 2026. Part 1 of 2. The companion report is [testimony-practicality.md](testimony-practicality.md).*

**How to read this report.** Every factual claim has an inline link to a source I opened and checked. Where I give my own reasoning rather than reporting evidence, the paragraph is marked **(inference)**. A few figures come from my own quick measurements (PyPI download counts and GitHub metadata pulled on 26 October 2026). Those are labelled as such, and their caveats are given.

---

## Executive summary

1. **Ecosystem and familiarity win, intrinsic features come second.** The largest empirical study of language adoption (Meyerovich & Rabkin, OOPSLA 2013: 200,000+ SourceForge projects, 590,000 Ohloh projects, surveys of 1,000–13,000 developers) found that "open source libraries, existing code, and experience strongly influence developers," while "performance, reliability, and simple semantics do not" ([paper](https://lmeyerov.github.io/projects/socioplt/papers/oopsla2013.pdf)). Verity's main selling point, testimony, is an intrinsic feature. On its own it will not carry adoption.
2. **Developer attention really is a limited resource.** The same study found that developers "forget as many languages as they learn," which makes familiarity "a limited resource for which languages must compete." The authors explicitly tie this to ecological theories of adoption ([paper](https://lmeyerov.github.io/projects/socioplt/papers/oopsla2013.pdf)). The evolutionary framing in this report is therefore an analogy the field already uses, not just a metaphor I imposed.
3. **Popularity follows a power law, and the long tail is niche-shaped.** A few languages take most usage, but "the programming market supports many languages with niche user bases." Unpopular languages concentrate in particular domains ([paper](https://lmeyerov.github.io/projects/socioplt/papers/oopsla2013.pdf)). Realistically Verity aims to be a niche survivor, not a mainstream language.
4. **Hosted languages live or die by their relationship with the host.** TypeScript's design goals were to emit idiomatic JS, add no runtime overhead, and "align with current and future ECMAScript proposals" ([TypeScript wiki](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals)). It tracked its host and won. CoffeeScript saw its best ideas absorbed into ES2015 ([CoffeeScript 2 announcement](https://coffeescript.org/announcing-coffeescript-2/)) and fell out of RedMonk's top 20 in 2015 ([InfoWorld](https://www.infoworld.com/article/2870801/javascript-java-lead-the-way-in-redmonk-language-rankings.html)).
5. **Transpile-to-Python languages have a poor track record as general-purpose languages.** Coconut, whose syntax Verity borrows, gets about 8,000 PyPI downloads a month after 11+ years, against Hy's 41,000 and Cython's 77 million (my pull from [pypistats](https://pypistats.org/packages/coconut)). Almost all of Coconut's commits come from one maintainer (GitHub API). The success story is Cython, which complements Python rather than replacing it ([cython.org](https://cython.org/)). Mojo has drifted the same way: its roadmap now says it "may or may not evolve into a full superset of Python, and it's okay if it doesn't," and frames itself as a way to "extend and speed up existing Python code" ([Mojo roadmap](https://mojolang.org/docs/roadmap)).
6. **Python has already absorbed the most visible Coconut feature.** Pattern matching arrived in Python 3.10 ([PEP 634](https://peps.python.org/pep-0634/)). Coconut now advertises itself as running Python 3.10-style matching "on all Python versions" ([coconut-lang.org](http://coconut-lang.org/)). Any Verity feature that is only nicer syntax is at risk of the same fate.
7. **Testimony is unusually hard for Python to absorb at the language level.** Python rejected overloadable `and`/`or`/`not` ([PEP 335, Rejected](https://peps.python.org/pep-0335/)) and deferred the follow-up ([PEP 532, Deferred](https://peps.python.org/pep-0532/)). But libraries could still absorb the use cases: pytest already rewrites asserts ([pytest docs](https://docs.pytest.org/en/stable/how-to/assert.html)). The real absorption threat is from the Python ecosystem, not from the language itself **(inference)**.
8. **Platforms and killer apps are the strongest mechanism in the historical record.** Ritchie: "Doubtless the success of Unix itself was the most important factor" in C's success ([Ritchie, HOPL-II](https://csapp.cs.cmu.edu/2e/docs/chistory.html)). Kotlin became "Kotlin-first" on Android ([Android Developers Blog](https://android-developers.googleblog.com/2019/05/google-io-2019-empowering-developers-to-build-experiences-on-Android-Play.html)). Dart was rescued by Flutter after Google dropped the Dart VM from Chrome ([Dart blog](https://news.dartlang.org/2015/03/dart-for-entire-web.html); [The Register](https://www.theregister.com/2019/11/08/google_dart_build/)). Verity has no platform. It needs a *use-case* anchor instead.
9. **AI coding assistants are a new selection pressure, and they work against new languages.** GitHub attributes TypeScript's rise to #1 in August 2025 partly to typed languages making "agent-assisted coding more reliable" ([Octoverse 2025](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/)). Code LLMs do markedly worse on low-resource languages ([Cassano et al.](https://arxiv.org/abs/2308.09895)), and Verity would be a "no-resource" language ([Giagnorio et al. 2026](https://arxiv.org/abs/2606.16827)).
10. **Governance and tooling failures kill languages that are technically fine.** Elm went from 0.19.1 (October 2019) to 0.19.2 (July 2026) with no compiler release in between ([GitHub releases](https://github.com/elm/compiler/releases)), and alienated contributors with a closed process ([Luke Plant](https://lukeplant.me.uk/blog/posts/why-im-leaving-elm/)). Stack Overflow ties Rust's growth to its package manager Cargo, the most admired tool in its category at 71% ([SO 2025](https://survey.stackoverflow.co/2025/technology/)).
11. **Candid odds.** By the evidence above, Verity as a general-purpose "functional Python" has very poor odds. Coconut already occupies that niche and barely survives there. Verity's realistic path is a narrow one: **an explanation-first testing and specification tool for existing Python codebases.** Ship the testimony runtime as a plain Python library from day one, and treat the `.ity` language as an optional, nicer front end. Plain Python users should be able to adopt testimony without switching languages **(inference, argued in §6)**.
12. **What would change the odds:** one concrete integration that existing Python users want (a pytest/Hypothesis plugin that explains quantified properties is the strongest candidate), a second maintainer, a machine-readable testimony format that other tools adopt, and LLM-friendly documentation **(inference)**.

---

## 1. Empirical evidence on adoption

### 1.1 Meyerovich & Rabkin: the strongest dataset

The most-cited quantitative work is Leo Meyerovich and Ariel Rabkin's *Empirical Analysis of Programming Language Adoption* (OOPSLA 2013). It analysed "over 200,000 SourceForge projects, 590,000 projects tracked by Ohloh, and multiple surveys of 1,000-13,000 programmers" ([paper PDF](https://lmeyerov.github.io/projects/socioplt/papers/oopsla2013.pdf)). Findings relevant to Verity, all from that paper:

- **Power law with niches.** "Language adoption follows a power law; a small number of languages account for most language use, but the programming market supports many languages with niche user bases." The less popular a language, the more its usage is concentrated in particular domains.
- **Libraries dominate.** The availability of open source libraries was "'strong' or 'medium' for over 60% of respondents," while simplicity, the least influential factor, was rated that way by only 25%. "Existing code or expertise with the language are four of the top five factors for adoption." The authors' advice: "Developing high-value open source libraries is likely to have a large influence to language adoption… Simplicity will not attract many programmers."
- **Switching follows domains, not syntax or semantics.** When developers moved between SourceForge projects, they kept the same language 18% of the time and moved to one of the six most popular languages 52% of the time. The authors saw "a relatively low probability of switching between Scheme and LISP, or between Ruby, Python, and Perl," and concluded that advocates "should focus on a domain and try to convince programmers in that domain, instead of trying to convince programmers who use languages with semantic" similarity.
- **Attention is finite.** Older and younger developers know a similar number of languages, so "developers are losing languages as well as gaining them." This means "immediate developer familiarity is a limited resource for which languages must compete. Such competition is the basis for ecological theories of adoption."
- **Developers value testing more than types.** In a small sample of professional developers (n = 96), only 36% "see the value" of static types, compared with 62% for unit testing.

**Implications for Verity (inference).** Verity's pitch is an intrinsic feature (testimony) plus syntax (Coconut-style), and both rank low in this data. Verity's main structural asset is that it inherits Python's libraries, which is the factor that ranks highest. That asset is shared by every Python-hosted language, so it does not differentiate Verity. The testing finding is mildly encouraging: if testimony helps testing, it touches something developers say they value.

### 1.2 The Socio-PLT agenda

The same authors' Onward! 2012 paper, *Socio-PLT: Principles for Programming Language Adoption*, applies diffusion-of-innovation research to languages ([paper PDF](https://lmeyerov.github.io/projects/socioplt/papers/onward2012.pdf)). Points that matter here:

- It lists Rogers' five adoption factors: relative advantage, compatibility, simplicity, trialability and observability. It notes that PL researchers "concentrate heavily on the first of these."
- **Observability is a barrier.** Many features "provide benefits that programmers cannot directly or immediately observe." Static typing is the paper's example: users explore with small programs and cannot see the large-system benefits.
- **Trial cost.** Minimising it "means, for example, making a language similar to one that the programmer already knows."
- **Ecological niches.** Citing Mark's ecological theory of music genres, it argues that "a DSL is more likely to be adopted if it solves a problem for a community rather than an equally sized group of socially disconnected individuals."
- It proposes that embedded DSLs are more likely to be adopted than standalone ones (Hypothesis 10).

**Inference.** Testimony is *unusually observable*: the benefit shows up the first time a check fails and prints a reason. That is a genuine advantage under Rogers' model, and Verity should design its first-five-minutes experience around it. Trialability argues for letting people try testimony from inside Python before they adopt a new file type.

### 1.3 Surveys and indices, with their caveats

- **Stack Overflow 2025.** JavaScript (66%), HTML/CSS, SQL and Python (57.9%) are the most-used languages. Python "saw a 7 percentage point increase from 2024 to 2025." Rust is again the most admired language (72%), followed by Gleam (70%), Elixir (66%) and Zig (64%) ([SO 2025 technology](https://survey.stackoverflow.co/2025/technology/)). Of respondents, 84% use or plan to use AI tools, and more developers distrust AI accuracy (46%) than trust it (33%) ([SO 2025 AI](https://survey.stackoverflow.co/2025/ai/)). Caveat: this is a self-selected sample of Stack Overflow users.
- **GitHub Octoverse 2025.** TypeScript became the most used language on GitHub in August 2025, overtaking Python and JavaScript. The ranking is "by the number of distinct monthly contributors who committed code in that language." Python "remains dominant in AI and data science" ([Octoverse 2025](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/)). Caveat: it counts contributors on GitHub, not code volume or private code.
- **TIOBE** counts search-engine hits for `+"<language> programming"` across 25 engines and normalises them. Groups of related languages use the maximum hit count among members ([TIOBE definition](https://www.tiobe.com/tiobe-index/programminglanguages_definition/)). It measures online mentions, not use.
- **RedMonk** combines GitHub and Stack Overflow data. It says plainly that "the idea is not to offer a statistically valid representation of current usage" ([RedMonk, 2024](https://redmonk.com/sogrady/2024/09/12/language-rankings-6-24/)). In 2025 it warned that "the arrival of AI has had a significant and accelerating impact on Stack Overflow." The top 20 showed "by far the least movement… that we have seen," and whether Stack Overflow "should continue to be used" is undecided ([RedMonk, June 2025](https://redmonk.com/sogrady/2025/06/18/language-rankings-1-25/)).

**Inference.** None of these indices can see a language of Verity's size. The useful lesson from them is about *stasis*: the top tier is extremely stable, and newcomers enter through a niche or a platform shift, not by head-on competition.

---

## 2. Mechanisms of success

### 2.1 Platforms and killer apps

| Language | Anchor | Evidence |
|---|---|---|
| C | Unix | Ritchie: "Doubtless the success of Unix itself was the most important factor; it made the language available to hundreds of thousands of people." He also calls C "quirky, flawed, and an enormous success" ([Ritchie, HOPL-II](https://csapp.cs.cmu.edu/2e/docs/chistory.html)). |
| JavaScript | The browser | Its history is documented in Wirfs-Brock & Eich, *JavaScript: The First 20 Years* (HOPL-IV) ([Zenodo](https://zenodo.org/record/4960086)). |
| Ruby, Python (science) | Rails, NumPy | Meyerovich & Rabkin cite "numpy for numerical programming in Python, and Ruby on Rails for web applications" as libraries "that had major influence on language adoption within niches" ([paper](https://lmeyerov.github.io/projects/socioplt/papers/oopsla2013.pdf)). |
| Kotlin | Android | First-class Android support was announced at I/O 2017 ([JetBrains blog](https://blog.jetbrains.com/kotlin/2017/05/kotlin-on-android-now-official/)). In 2019 Google said "Android development will become increasingly Kotlin-first" and reported "over 50% of professional Android developers now use Kotlin" ([Android Developers Blog](https://android-developers.googleblog.com/2019/05/google-io-2019-empowering-developers-to-build-experiences-on-Android-Play.html)). |
| Swift | iOS / Apple | Lattner describes executives fearing Swift would fragment the community. ARC, modules and literals entered Objective-C partly to enable Swift's interop ([Hacking with Swift interview](https://www.hackingwithswift.com/interviews/chris-lattner-could-apple-have-improved-objective-c-instead-of-making-swift)). |
| Dart | Flutter | In 2015 the Dart team "decided not to integrate the Dart VM into Chrome" and refocused on compiling to JS ([Dart blog](https://news.dartlang.org/2015/03/dart-for-entire-web.html)). The Register describes the later revival as driven by Flutter ([The Register](https://www.theregister.com/2019/11/08/google_dart_build/)). |

**Inference.** Every clear case of a new language entering the mainstream since 1990 rode a platform or a framework. Verity cannot create a platform. The closest substitute is a *workflow anchor*: a task that people already do daily in Python, where Verity's output is visibly better. Section 6 argues that this task is testing and specification.

### 2.2 Interop with an incumbent

Hosting on an incumbent runtime is the dominant strategy for new languages, and the strategy is explicit in the designers' own words:

- **Clojure:** "Clojure is the language, JVM the platform." "Platforms are dictated by clients." "Ability to call/consume Java is critical" ([Clojure rationale](https://clojure.org/about/rationale)).
- **Kotlin:** "Kotlin is designed with Java interoperability in mind" ([Kotlin docs](https://kotlinlang.org/docs/java-interop.html)).
- **Elixir** credits "decades of Erlang reliability" and the Erlang VM ([elixir-lang.org](https://elixir-lang.org/)).
- **F#:** Syme writes that early F# "was essentially an effort to address each of" Wadler's obstacles (libraries, portability, availability, packagability, tools, training, popularity). He adds that failed commercial ML implementations "left the community with the feeling that the support of a 'big player' in the industry was needed" ([Syme, HOPL-IV](https://fsharp.org/history/hopl-final/hopl-fsharp.pdf)). Wadler's original column lists those eight reasons and rejects performance and "they just don't get it" as explanations ([Wadler](https://homepages.inf.ed.ac.uk/wadler/topics/functional-programming.html)).
- **TypeScript** is the most successful hosted language. Its stated goals include "Impose no runtime overhead on emitted programs," "Emit clean, idiomatic, recognizable JavaScript code," "Align with current and future ECMAScript proposals," and "Preserve runtime behavior of all JavaScript code" ([TypeScript design goals](https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals)).

**Inference.** TypeScript and CoffeeScript ran the same experiment on the same host with opposite outcomes. TypeScript *added* something the host lacked (static types) and kept everything else identical, so it never competed with JS's own evolution. CoffeeScript mostly *re-skinned* syntax, and JS caught up. Verity is in the same position. Its Coconut-style syntax is CoffeeScript-like. Testimony is TypeScript-like: an orthogonal addition the host does not have.

### 2.3 Corporate sponsorship

Kotlin (JetBrains, then Google), Swift (Apple), TypeScript and F# (Microsoft), Go and Dart (Google) all had corporate backing. Rust's foundation launched in February 2021 with AWS, Huawei, Google, Microsoft and Mozilla as founding members ([Rust Foundation](https://rustfoundation.org/news/2021-02-08-hello-world/)). Syme's account of F# says outright that the community came to believe a "big player" was needed ([Syme](https://fsharp.org/history/hopl-final/hopl-fsharp.pdf)). Verity will not have this, and nothing in this report changes that.

### 2.4 Education pipelines

Python's position in education is well documented. A 2014 survey by Philip Guo found Python in the intro courses of 27 of 39 top US CS departments, and in 8 of the top 10 ([Computerworld](https://www.computerworld.com/article/1382433/more-evidence-that-python-is-the-best-starter-programming-language.html)). Critics noted that counting intro courses for non-CS majors inflated Python's share (same source). Teaching languages can survive indefinitely in their niche. Racket began in 1995 as "an outreach project for novice programmers" ([Racket Manifesto](https://users.cs.northwestern.edu/~robby/pubs/papers/manifesto.pdf)). Pyret exists because "we need better languages for introductory computing" and builds testing into the language, borrowing from Racket's `check-expect` ([Pyret](https://pyret.org/pyret-code/); [Pyret testing docs](https://pyret.org/docs/latest/testing.html)).

**Inference.** Verity's authors are students, and `forall`/`exists` with witnesses and counterexamples map directly onto discrete-mathematics and logic teaching. Education is a credible *secondary* niche, and the Racket/Pyret precedent shows it can sustain a language for decades without mainstream adoption.

### 2.5 Tooling: package managers, LSP, error messages

- Stack Overflow 2025: "Rust's growth is directly tied to the success of its build tool and package manager, Cargo, which is the most admired (71%)" tool in its category ([SO 2025](https://survey.stackoverflow.co/2025/technology/)). That is Stack Overflow's interpretation, not a causal study.
- Elm's "Compiler Errors for Humans" (June 2015) set a widely copied standard ([Elm blog](https://elm-lang.org/news/compiler-errors-for-humans)). Rust's 2016 redesign says its new `--explain` messages "draw heavy inspiration from the Elm approach" ([Rust blog](https://blog.rust-lang.org/2016/08/10/Shape-of-errors-to-come.html)). This is horizontal transfer of a *tooling* trait between languages.
- The Language Server Protocol turned editor support from an M×N problem into an M+N problem ([langserver.org](https://langserver.org/)). For a two-person project, an LSP server is the cheapest way to appear "real" in VS Code, Neovim and others **(inference)**.

### 2.6 Community and governance

- **Elm** is the cautionary tale. Luke Plant (April 2020): "In Elm, you cannot even see any records of the core team's decision making process, let alone contribute to it." In 0.19, "the compiler itself limits the feature [native code] to certain official libraries" ([Luke Plant](https://lukeplant.me.uk/blog/posts/why-im-leaving-elm/)). The compiler's releases show 0.19.1 in October 2019, then nothing until 0.19.2 in July 2026 and 0.19.3 in October 2026, neither with language changes ([GitHub releases](https://github.com/elm/compiler/releases)).
- **Reason/ReScript.** In August 2020 BuckleScript rebranded as ReScript. The announcement cited the "sheer amount of extra incongruent tools and learning overhead" newcomers faced and admitted "it'll be confusing to temporarily have different syntaxes in the same codebase" ([ReScript blog](https://rescript-lang.org/blog/bucklescript-is-rebranding)). The split left Reason as a native-OCaml syntax layer.
- **Steele and Stroustrup on growth.** Steele's *Growing a Language* argues that "a small language with warts will beat a well designed language because users will not wait for the right thing." He adds that "once a small language fills a niche, it is hard to take its place," and that growth is fastest when users can add to the language ([Steele, OOPSLA 1998](https://www.cs.virginia.edu/~evans/cs655/readings/steele.pdf)). Stroustrup: "All successful languages are grown and not merely designed from first principles." He also has the famous line: "There are only two kinds of languages: the ones people complain about and the ones nobody uses" ([Stroustrup quotes page](https://www.stroustrup.com/quotes.html)).
- **Rust's founder accepts that the community steered away from him.** Graydon Hoare wrote that "the Rust We Got is many, many miles away from The Rust I Wanted." He said he "would have traded performance and expressivity away for simplicity," and concluded that his preferred Rust had no future ([quoted by Michael Tsai](https://mjtsai.com/blog/2023/06/08/the-rust-i-wanted-had-no-future/); the original at graydon2.dreamwidth.org/307291.html returned 404 when I checked).

---

## 3. Extinctions and niche survivors

### 3.1 Compile-to-host languages that faded or stalled

**CoffeeScript.** The CoffeeScript 2 announcement says that "many new JavaScript features, such as `=>`, were informed by CoffeeScript and are one-to-one compatible, or very nearly so" ([CoffeeScript 2](https://coffeescript.org/announcing-coffeescript-2/)). In RedMonk's February 2012 analysis, CoffeeScript had jumped from #19 to #13 in GitHub popularity, the largest move of any language ([RedMonk 2012](https://redmonk.com/sogrady/2012/02/08/language-rankings-2-2012/)). In January 2015 Go "displaces CoffeeScript entirely" from the top 20 ([InfoWorld](https://www.infoworld.com/article/2870801/javascript-java-lead-the-way-in-redmonk-language-rankings.html)). The project is still maintained: release 2.7.1 came out in October 2026 (GitHub API). This is the clearest case of **absorption**: the host took the guest's best traits, and the guest's reason to exist shrank to its syntax.

**Elm** stagnated for governance reasons rather than technical ones (§2.6).

**Dart** came close to extinction as a browser language and was revived by a new niche, Flutter mobile apps ([Dart blog](https://news.dartlang.org/2015/03/dart-for-entire-web.html); [The Register](https://www.theregister.com/2019/11/08/google_dart_build/)). The Register reported a 532% rise in Dart interest in Octoverse at the time. This is **niche shift**: the same organism survived by moving to a new habitat.

**ReasonML** split in two (§2.6).

**Coconut** and **Hy** are covered in §4.

### 3.2 What niche survival looks like

- **OCaml at Jane Street.** The OCaml.org success story reports over 500 OCaml programmers and 30+ million lines of OCaml at the firm ([OCaml.org](https://ocaml.org/success-stories/large-scale-trading-system)). A single committed industrial user can sustain a language's ecosystem.
- **Clojure.** The 2024 State of Clojure survey reports 73% of respondents using Clojure at work, with finance the top sector. It names Nubank as having "well over 1000 Clojure developers" ([State of Clojure 2024](https://clojure.org/news/2024/12/02/state-of-clojure-2024)).
- **Racket** survives through education and "language-oriented programming" ([Racket Manifesto](https://users.cs.northwestern.edu/~robby/pubs/papers/manifesto.pdf)).
- **Influence without dominance.** F# had a large influence on C#: generics, `var`, async/await, tuples and pattern matching were "all heavily influenced by F#" ([Syme](https://fsharp.org/history/hopl-final/hopl-fsharp.pdf)). Java later added records ([JEP 395](https://openjdk.org/jeps/395), Java 16) and pattern matching for switch ([JEP 441](https://openjdk.org/jeps/441), Java 21). Kotlin survived that absorption because Android anchored it **(inference)**.

**Inference.** Niche survivors share three traits: a cohesive community with a real job to do (trading systems, fintech backends, teaching), a stable core team, and a willingness to stay small. "Success" for Verity should be defined in these terms, not in index rankings.

---

## 4. Lessons from transpile-to-Python languages

### 4.1 The numbers

My pull from the pypistats API on 26 October 2026 (downloads in the last 30 days; these include CI and mirrors, so treat them as order-of-magnitude only):

| Package | Downloads / month | Notes |
|---|---|---|
| `coconut` | ~8,000 | Repo created 2014; v3.2.0 Dec 2025; top contributor has 4,833 commits, the next has 19 (GitHub API) |
| `hy` | ~41,000 | Repo created 2012; 1.0.0 released September 2024 (GitHub API), about 12 years after the repo was created |
| `cython` | ~77,000,000 | Build-time dependency of much of the scientific stack |
| `pydantic` (for scale) | ~842,000,000 | Library, not a language |

Sources: [pypistats coconut](https://pypistats.org/packages/coconut), [pypistats hy](https://pypistats.org/packages/hy), [pypistats cython](https://pypistats.org/packages/cython), [pypistats pydantic](https://pypistats.org/packages/pydantic); repository metadata from the GitHub API for [evhub/coconut](https://github.com/evhub/coconut) and [hylang/hy](https://github.com/hylang/hy).

### 4.2 What each got right and wrong

**Coconut** ([coconut-lang.org](http://coconut-lang.org/)).
- *Right:* "all valid Python is valid Coconut," so the trial cost for Python users is minimal. It produces version-independent output and has a rich FP feature set.
- *Wrong (inference):* its value is mostly syntax, the category that hosts absorb or users shrug off. It also has a bus factor of one. After Python 3.10 added `match`, part of Coconut's pitch became "Python's own feature, on older Pythons."

**Hy** ([hylang.org](https://hylang.org/)) is "a Lisp dialect that's embedded in Python." It has a loyal, small community. Taking about 12 years to reach 1.0 (GitHub releases) shows how long stability takes when the user base is small **(inference)**.

**Cython** describes itself as "an optimising static compiler for both the Python programming language and the extended Cython programming language." It makes C extensions "as easy as Python itself" and lists SciPy, scikit-learn, lxml and spaCy among its users ([cython.org](https://cython.org/)). *Right:* it solves a problem Python cannot solve for itself (speed and C interop) and *complements* Python. You use Cython for 3% of a codebase and Python for the rest. It never asked anyone to switch languages.

**Mojo.** Modular's current roadmap: "Mojo may or may not evolve into a full superset of Python, and it's okay if it doesn't." Phase 1's goal was to be "an approachable way to extend and speed up existing Python code" ([Mojo roadmap](https://mojolang.org/docs/roadmap)). InfoWorld (November 2025) notes that "Mojo's goal is not to provide inherent compatibility with Python" and that "every call across the Mojo/Python boundary incurs a performance cost" ([InfoWorld](https://www.infoworld.com/article/4081105/revisiting-mojo-a-faster-python.html)). Even with Chris Lattner and venture funding, Mojo moved from a "superset" pitch toward the Cython-like "extend Python" pitch. That is strong evidence about where the fitness peak lies for Python-adjacent languages **(inference)**.

**Pyret** is a teaching language rather than a Python transpiler. Its lesson for Verity is that built-in testing (`check:`/`where:` blocks with `is`, `satisfies`, `raises`) can be a language's central identity ([Pyret testing](https://pyret.org/docs/latest/testing.html)).

### 4.3 When the host absorbs the guest

- **JS absorbing CoffeeScript** (§3.1).
- **Python absorbing pattern matching.** PEP 622 credits Scala, Erlang, F#, Haskell, Rust, Elixir and Ruby as inspirations, without naming Coconut ([PEP 622](https://peps.python.org/pep-0622/)). Absorption does not even bring credit.
- **Java absorbing Kotlin/Scala ideas** and **C# absorbing F#** (§3.2).

**What Python is unlikely to absorb.** Overloadable boolean operators were rejected ([PEP 335](https://peps.python.org/pep-0335/)), and the circuit-breaking protocol is deferred ([PEP 532](https://peps.python.org/pep-0532/)). Python therefore gives *libraries* no hook into `and`/`or`/`not`, which is exactly the hook testimony needs **(inference)**. That does not make testimony safe. pytest shows that a library can rewrite the AST of whole modules through an import hook ([pytest docs](https://docs.pytest.org/en/stable/how-to/assert.html)). Ecosystem absorption is the realistic threat; language absorption is not. The companion report covers this in detail.

---

## 5. The evolutionary framing

### 5.1 Who has written about language evolution

- **Valverde & Solé**, *Punctuated equilibrium in the large-scale evolution of programming languages* (J. R. Soc. Interface, 2015). They built phylogenetic networks of 347 languages from 1952 to 2010 and found evolution "highly uneven, marked by innovation events" where new languages recombine components of older ones. They report "high levels of horizontal transfer" and bursts tied to new technological niches, including personal computing, which "triggered this second wave of languages" ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4590513/)).
- **Crafa**, *Modelling the Evolution of Programming Languages* (2015), checks how far Darwinian ingredients apply. Variation and selection are shaped by *intentional* design. "Genetic and language drift have no parallel… because there is no random sampling effect in the replication mechanism." Economic pressures "might overcome 'natural' selection and determine the dominance of sub-optimal solutions." She identifies **niche construction** (HTML/CSS/JS "mutually affect their evolution") and **exaptation**: functional programming's higher-order functions moved into C++11 and Java 8 because they suited parallel programming ([arXiv:1510.04440](https://arxiv.org/abs/1510.04440)).
- **Meyerovich & Rabkin** frame developer familiarity as a resource that languages compete for, and cite ecological adoption theory ([OOPSLA 2013](https://lmeyerov.github.io/projects/socioplt/papers/oopsla2013.pdf); [Onward! 2012](https://lmeyerov.github.io/projects/socioplt/papers/onward2012.pdf)).
- **Gabriel's "Worse is Better"** is explicitly viral and evolutionary: "Unix and C are the ultimate computer viruses." His advice is "get half of the right thing available so that it spreads like a virus. Once people are hooked on it, take the time to improve it to 90%" ([The Rise of Worse is Better](https://www.dreamsongs.com/RiseOfWorseIsBetter.html)). Gabriel later argued both sides of his own thesis ([dreamsongs.com](https://www.dreamsongs.com/WorseIsBetter.html)).
- **Steele** applies the same logic to growth: small languages win the race to fill a niche, then must be grown by their users ([Steele](https://www.cs.virginia.edu/~evans/cs655/readings/steele.pdf)).
- I found no peer-reviewed model that fits Lotka–Volterra or Abrams–Strogatz-style competition dynamics to programming-language data. Such models exist for human languages. I am leaving this gap open rather than citing a weak source.

### 5.2 Mapping the framing onto Verity (inference throughout)

| Evolutionary concept | Language-world analogue | What it means for Verity |
|---|---|---|
| **Fitness** | Users and developer attention (Meyerovich's "limited resource") | Count weekly active users and dependent projects, not stars |
| **Variation** | New language features | Testimony is a real variation. Coconut syntax is not, because it is inherited |
| **Inheritance** | Syntax, semantics, runtime, libraries | Inheriting Python's runtime and libraries is Verity's biggest fitness asset, but every Python guest has it |
| **Horizontal transfer** | Features copied across lineages (Elm errors to Rust; F# to C#; CoffeeScript to ES2015) | Verity's ideas may survive in other tools even if Verity does not. Plan for that |
| **Selection pressure** | Libraries, familiarity, platform, tooling, and now AI assistants | AI assistants are a strong new pressure against no-resource languages |
| **Niche** | A domain with a cohesive community | Python developers who write tests and specifications; logic/discrete-maths teaching |
| **Niche construction** | A language that reshapes its environment (JS/HTML/CSS) | A testimony *format* that other tools consume would be niche construction |
| **Punctuated equilibrium** | Bursts at platform shifts (PCs, web, mobile, AI) | The AI-agent shift is a punctuation event. Explainable checks fed back to agents fit it |
| **Exaptation** | A trait reused for a new function (closures for parallelism) | Testimony built for human explanation could be exapted as machine-readable feedback for LLM repair loops (Part 2) |
| **Absorption / extinction** | Host takes the guest's traits (CoffeeScript) | Syntax features will be absorbed or ignored. Only testimony is defensible |

### 5.3 AI assistants as a new selection pressure

GitHub links the rise of typed languages to the reliability of "agent-assisted coding" ([Octoverse 2025](https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/)). Andrea Griffiths (GitHub) calls this a "convenience loop": "Reduced friction becomes a preference—and preferences at scale can shift ecosystems." She warns language builders that "AI support can't be an afterthought" ([GitHub blog, Feb 2026](https://github.blog/news-insights/octoverse/how-ai-is-reshaping-developer-choice-and-octoverse-data-proves-it/)). Code LLMs "produce impressive results on programming languages that are well represented in their training data" and much weaker results elsewhere ([Cassano et al.](https://arxiv.org/abs/2308.09895)). A 2026 TSE paper studies "no-resource languages" with "virtually no training data" and finds continued pre-training is the most effective remedy ([Giagnorio et al.](https://arxiv.org/abs/2606.16827)). No individual project can afford that.

**Inference.** For Verity this pressure is mixed. The bad news: an agent asked to write Verity will hallucinate. The good news: Verity is close enough to Python and Coconut that a short reference document in context should go a long way, and its *output* (testimony) is exactly the kind of structured, checkable feedback agents use. The companion report gives the evidence that execution feedback improves LLM code generation.

---

## 6. Recommendations for Verity (prioritised)

Everything in this section is **inference** from the evidence above. Where a recommendation conflicts with the current CLAUDE.md, I say so.

### Candid assessment first

- As a general-purpose "functional Python," Verity has **very poor odds**. Coconut has occupied that exact niche for over a decade with a talented maintainer and still has about 8,000 downloads a month. Python keeps absorbing the syntax that would differentiate it. The adoption research says syntax and paradigm barely move developers.
- Testimony is the **only differentiated trait**, and it is observable, which helps. But an intrinsic feature without a library, platform or workflow anchor ranks low in every dataset above.
- Two student authors with no sponsor puts Verity in the Hy/Coconut resource class, not the Kotlin/Swift class. Governance and continuity risk (Elm, bus factor one) is the most likely way Verity dies, ahead of technical failure.

### What would change the odds

1. **One workflow anchor that existing Python users want.** The strongest candidate, from Part 2, is explained property-based testing. pytest's own issue asking it to unroll `all()`/`any()` for better reports has been open since 2019. An attempt to implement it was reverted for correctness bugs ([#5062](https://github.com/pytest-dev/pytest/issues/5062), [#5373](https://github.com/pytest-dev/pytest/pull/5373)). Verity's `forall`/`exists` testimony addresses exactly that gap.
2. **Trialability inside Python.** People should be able to use testimony without adopting `.ity` files.
3. **A second committed maintainer** and visible, open governance.
4. **A testimony format other tools consume.** That would be niche construction, and it means the idea survives even if the language does not.

### Prioritised recommendations

1. **Pick a niche: "explanation-first tests and specifications for Python code."** Position Verity as Cython is positioned: a complement you add to a Python project, not a replacement. Concretely, `.ity` files for properties, invariants, validation rules and test oracles that import and test ordinary Python modules.
2. **Build the killer use case first: a pytest plugin.** It should collect `.ity` test files, run `forall`/`exists` properties (optionally drawing inputs from Hypothesis strategies, so you get shrinking and testimony together), and print the testimony tree on failure. Measure success by how many outside projects keep it in CI.
3. **Ship the runtime as a Python package early** (`pip install verity-truth` or similar), with a small, explicit API: `verity.check(...)`, quantifier helpers and `explain`. *This conflicts with the CLAUDE.md principle that "users never install a Python package."* The reasons are trialability, the "embedded DSLs are adopted more" hypothesis from Socio-PLT, and the TypeScript lesson of letting people adopt gradually. The `.ity` syntax then becomes the ergonomic layer for people already sold on testimony. Keep the embedded-runtime path for `verity run`.
4. **De-emphasise Coconut syntax in marketing.** Lambdas, pipes and `addpattern` are fine to keep, but they are inherited traits that Python can absorb or users can ignore. Lead every page, README and talk with a failing check and its testimony, the observable benefit.
5. **Invest in tooling that signals seriousness, in this order:** (a) source maps from generated Python tracebacks back to `.ity` lines; CLAUDE.md currently defers this to after all milestones, and I would pull it forward, because tracebacks pointing at generated code are a daily cost for transpiled languages; (b) Elm/Rust-quality compiler errors; (c) a minimal LSP (diagnostics plus go-to-definition); (d) a formatter.
6. **Make Verity AI-legible.** Publish a single-page language reference and an examples corpus that fit in an LLM context window. Make compiler errors and testimony available as JSON so agents can act on them. Treat "an agent can write correct Verity from the reference page" as a release criterion.
7. **Define and publish a structured testimony format** (see Part 2: JSON with node kinds, source spans, data paths, redaction markers). Invite other tools to emit or consume it, so Verity's ideas can spread by horizontal transfer.
8. **Secondary niche: teaching logic and specification.** Package a set of discrete-maths exercises where students write `forall`/`exists` claims about Python data and read counterexamples. The Racket and Pyret precedents show this niche can sustain a language indefinitely.
9. **Governance from day one.** Use a public design-decision log (CLAUDE.md and the book's "design note" boxes are a good start), a CONTRIBUTING guide, and an explicit stability promise once 0.1 ships. Avoid long silent gaps (Elm) and avoid rebrands and splits (Reason).
10. **Avoid these:** competing head-on with Coconut or Hy on syntax; claiming to be "Python, but better" (Mojo retreated from that claim); breaking compatibility with plain Python libraries; building features no user has asked for before the pytest plugin works; and letting interop rule 3 (numpy/pandas comparisons pass through untouched) silently remove testimony where users expect it. Document that limit loudly.

### How to avoid being absorbed by Python

- **Make the defensible part the core.** Python cannot overload `and`/`or`/`not` (PEP 335 rejected), so a compiler-level rewrite of boolean structure is a durable reason for Verity to exist. Syntax sugar is not.
- **Expect absorption by the ecosystem rather than the language.** If pytest fixes #5062, or pydantic adds explanation trees, Verity's testing pitch weakens. The defence is to be the reference implementation and format for testimony, and to integrate with those tools rather than compete with them.
- **Redefine success as influence plus a niche.** CoffeeScript's ideas live on in ES2015 and F#'s in C#. If Verity's testimony format, or explained quantifiers, end up in pytest or Hypothesis, that is a real outcome for a student language, and a much likelier one than mainstream adoption.

---

## Sources

1. Meyerovich & Rabkin, *Empirical Analysis of Programming Language Adoption*, OOPSLA 2013. https://lmeyerov.github.io/projects/socioplt/papers/oopsla2013.pdf
2. Meyerovich & Rabkin, *Socio-PLT: Principles for Programming Language Adoption*, Onward! 2012. https://lmeyerov.github.io/projects/socioplt/papers/onward2012.pdf
3. Stack Overflow Developer Survey 2025, Technology. https://survey.stackoverflow.co/2025/technology/
4. Stack Overflow Developer Survey 2025, AI. https://survey.stackoverflow.co/2025/ai/
5. GitHub Octoverse 2025. https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/
6. Griffiths, *How AI is reshaping developer choice*, GitHub Blog, Feb 2026. https://github.blog/news-insights/octoverse/how-ai-is-reshaping-developer-choice-and-octoverse-data-proves-it/
7. TIOBE index definition. https://www.tiobe.com/tiobe-index/programminglanguages_definition/
8. RedMonk language rankings, June 2024 (published Sept 2024). https://redmonk.com/sogrady/2024/09/12/language-rankings-6-24/
9. RedMonk language rankings, January 2025 (published June 2025). https://redmonk.com/sogrady/2025/06/18/language-rankings-1-25/
10. RedMonk language rankings, February 2012. https://redmonk.com/sogrady/2012/02/08/language-rankings-2-2012/
11. InfoWorld on RedMonk January 2015 rankings. https://www.infoworld.com/article/2870801/javascript-java-lead-the-way-in-redmonk-language-rankings.html
12. Cassano et al., *Knowledge Transfer from High-Resource to Low-Resource Programming Languages for Code LLMs*. https://arxiv.org/abs/2308.09895
13. Giagnorio, Martin-Lopez & Bavota, *No Resource, No Benchmarks, No Problem?* (2026). https://arxiv.org/abs/2606.16827
14. Ritchie, *The Development of the C Language* (HOPL-II), mirror. https://csapp.cs.cmu.edu/2e/docs/chistory.html
15. Wirfs-Brock & Eich, *JavaScript: The First 20 Years* (HOPL-IV). https://zenodo.org/record/4960086
16. JetBrains, *Kotlin on Android. Now official* (2017). https://blog.jetbrains.com/kotlin/2017/05/kotlin-on-android-now-official/
17. Android Developers Blog, Google I/O 2019. https://android-developers.googleblog.com/2019/05/google-io-2019-empowering-developers-to-build-experiences-on-Android-Play.html
18. Lattner interview, Hacking with Swift. https://www.hackingwithswift.com/interviews/chris-lattner-could-apple-have-improved-objective-c-instead-of-making-swift
19. Bak & Lund, *Dart for the Entire Web* (2015). https://news.dartlang.org/2015/03/dart-for-entire-web.html
20. The Register on Dart and Flutter (2019). https://www.theregister.com/2019/11/08/google_dart_build/
21. Clojure rationale. https://clojure.org/about/rationale
22. Kotlin Java interop docs. https://kotlinlang.org/docs/java-interop.html
23. Elixir homepage. https://elixir-lang.org/
24. Syme, *The Early History of F#* (HOPL-IV). https://fsharp.org/history/hopl-final/hopl-fsharp.pdf
25. Wadler, Functional programming papers page (*Why no one uses functional languages*). https://homepages.inf.ed.ac.uk/wadler/topics/functional-programming.html
26. TypeScript Design Goals. https://github.com/microsoft/TypeScript/wiki/TypeScript-Design-Goals
27. Rust Foundation launch announcement. https://rustfoundation.org/news/2021-02-08-hello-world/
28. Computerworld on Guo's 2014 intro-language survey. https://www.computerworld.com/article/1382433/more-evidence-that-python-is-the-best-starter-programming-language.html
29. Felleisen et al., *The Racket Manifesto*. https://users.cs.northwestern.edu/~robby/pubs/papers/manifesto.pdf
30. Pyret, *Why Pyret*. https://pyret.org/pyret-code/
31. Pyret testing documentation. https://pyret.org/docs/latest/testing.html
32. Czaplicki, *Compiler Errors for Humans* (2015). https://elm-lang.org/news/compiler-errors-for-humans
33. Rust blog, *Shape of errors to come* (2016). https://blog.rust-lang.org/2016/08/10/Shape-of-errors-to-come.html
34. langserver.org. https://langserver.org/
35. Plant, *Why I'm leaving Elm* (2020). https://lukeplant.me.uk/blog/posts/why-im-leaving-elm/
36. Elm compiler releases. https://github.com/elm/compiler/releases
37. ReScript, *BuckleScript & Reason rebranding* (2020). https://rescript-lang.org/blog/bucklescript-is-rebranding
38. Steele, *Growing a Language* (OOPSLA 1998). https://www.cs.virginia.edu/~evans/cs655/readings/steele.pdf
39. Stroustrup quotes page. https://www.stroustrup.com/quotes.html
40. Tsai, *The Rust I Wanted Had No Future* (quoting Hoare). https://mjtsai.com/blog/2023/06/08/the-rust-i-wanted-had-no-future/
41. CoffeeScript 2 announcement. https://coffeescript.org/announcing-coffeescript-2/
42. OCaml.org success story: Jane Street. https://ocaml.org/success-stories/large-scale-trading-system
43. State of Clojure 2024. https://clojure.org/news/2024/12/02/state-of-clojure-2024
44. JEP 395: Records. https://openjdk.org/jeps/395
45. JEP 441: Pattern Matching for switch. https://openjdk.org/jeps/441
46. pypistats: coconut, hy, cython, pydantic. https://pypistats.org/packages/coconut · https://pypistats.org/packages/hy · https://pypistats.org/packages/cython · https://pypistats.org/packages/pydantic
47. Coconut homepage. http://coconut-lang.org/
48. Coconut repository. https://github.com/evhub/coconut
49. Hy homepage and repository. https://hylang.org/ · https://github.com/hylang/hy
50. Cython homepage. https://cython.org/
51. Mojo roadmap. https://mojolang.org/docs/roadmap
52. InfoWorld, *Revisiting Mojo* (Nov 2025). https://www.infoworld.com/article/4081105/revisiting-mojo-a-faster-python.html
53. PEP 622, 634: Structural pattern matching. https://peps.python.org/pep-0622/ · https://peps.python.org/pep-0634/
54. PEP 335 (Rejected) and PEP 532 (Deferred). https://peps.python.org/pep-0335/ · https://peps.python.org/pep-0532/
55. pytest assertion docs. https://docs.pytest.org/en/stable/how-to/assert.html
56. pytest issue #5062 and PR #5373. https://github.com/pytest-dev/pytest/issues/5062 · https://github.com/pytest-dev/pytest/pull/5373
57. Valverde & Solé, *Punctuated equilibrium in the large-scale evolution of programming languages* (2015). https://pmc.ncbi.nlm.nih.gov/articles/PMC4590513/
58. Crafa, *Modelling the Evolution of Programming Languages* (2015). https://arxiv.org/abs/1510.04440
59. Gabriel, *The Rise of Worse is Better*, and retrospective. https://www.dreamsongs.com/RiseOfWorseIsBetter.html · https://www.dreamsongs.com/WorseIsBetter.html
