# Verity

**Checks that explain themselves.**

Verity is Python whose truth values explain themselves, to people and to agents. It is Python 3.12 plus a few keywords: the truth literals `verity` and `falsity`, `p because m`, and the quantifiers `forall` and `exists`. Every truth carries *testimony*: a verity carries a witness, and a falsity carries a refutation. Comparisons, `and`, `or`, `not`, `forall`, `exists` and `all_of` assemble it for you, and `because` lets you state your own claims, with stable reason IDs and hints. Testimony renders as an indented tree for people and as JSON (schema `verity.testimony/0`) for tools and coding agents. When nobody looks, the compiler skips building it, so ordinary control flow costs nothing extra.

```python
from testimony import explain

primes = [2, 3, 5, 7, 11, 13]

print(explain(forall p in primes, p % 2 == 1))
```

```
falsity
  counterexample: p = 2 (primes[0])
    p % 2 == 1: 0 != 1
```

Verity compiles to plain Python, so all of CPython and its libraries come along. The runtime is also a Python package, `verity-testimony`, so Python code and test suites can use testimony without `.ity` files.

More in [`examples/`](examples/), and in the reference documentation, [*Verity Programming*](https://www.verity.garden/book/cover.html) (also as plain text for language models: [`llms.txt`](https://www.verity.garden/book/llms.txt), [`verity.txt`](https://www.verity.garden/book/verity.txt)).

## Status

**Early.** The compiler is being written in Rust (hand-written lexer and parser) and will emit Python. Milestone 1, the runtime library in [`runtime/`](runtime/), comes first. See [CLAUDE.md](CLAUDE.md) for the spec and milestones.

## Homepage development

The garden homepage uses React, Vite, and Three.js. Botanical illustrations are
editable SVG, and only the smiling character needs WebGL. A matching SVG character
remains available when WebGL cannot start. Motion respects the system's reduced
motion preference. The current frontend is the garden scene alone, without text,
controls, or facial animation.

```sh
npm install
npm run dev
```

Open the local URL printed by Vite. `npm run build` creates the static site in
`site/dist`, and `npm run preview` serves that build. GitHub Pages builds and deploys
this directory through `.github/workflows/pages.yml`.

The frontend's dependencies and lockfile live in `site/`. Root-level commands
forward to that package, and `npm ci` installs it automatically. It also builds
independently with `cd site && npm ci && npm run build`.

`verity.garden` is hosted on Vercel. Both the repository root and `site/` include
explicit Vercel configuration, supporting either project root selection. Vercel
must serve the generated `dist` directory, never the unbuilt source `index.html`.

With the dev server running, `npm run test:site` runs the browser smoke checks.
It uses an installed Chrome on macOS, or Playwright Chromium elsewhere (install
with `npx playwright install chromium`). Set `SITE_URL` or `CHROME_PATH` to override
the defaults. Screenshots are saved under `site/test-results/`.

## License

Apache-2.0
