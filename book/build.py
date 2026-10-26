"""Build the Verity reference: book/src/*.html fragments -> site/public/book/*.html (Vite copies public/ into the build),
plus plain-text versions for language models and other tools: llms.txt (index) and verity.txt (everything).

No dependencies. Run from anywhere:  python3 book/build.py

Each fragment is the body of one page. The build adds the page shell
(sidebar, header, "on this page" list, prev/next links), numbers the
<h2> sections, and syntax-highlights code blocks:

  <pre class="ity">  Verity source   (write raw < > &; they are escaped here)
  <pre class="out">  program output / testimony
  <pre class="py">   generated Python
  <pre class="sh">   shell commands
"""

import html
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT.parent / "site" / "public" / "book"
REPO = "https://github.com/Henrik66/verity"

BOOK_TITLE = "Verity Programming"

# (slug, title, number). number None = front matter, int = section, str = appendix.
TOC = [
    ("cover", "Cover", None),
    ("about", "About These Docs", None),
    ("overview", "Overview", 1),
    ("lexical", "Lexical Analysis", 2),
    ("data-model", "Data Model", 3),
    ("expressions", "Expressions", 4),
    ("testimony", "Testimony Semantics", 5),
    ("statements", "Statements", 6),
    ("python", "Python Interoperability", 7),
    ("stdlib", "Standard Library", 8),
    ("cli", "Command-Line Interface", 9),
    ("machine", "Machine Interface", 10),
    ("implementation", "Implementation", 11),
    ("grammar", "Grammar", "A"),
    ("glossary", "Glossary", "B"),
]

# Pages from the first edition, redirected to their closest replacement.
REDIRECTS = {
    "preface": "about",
    "introduction": "overview",
    "basics": "lexical",
    "quantifiers": "expressions",
    "functions": "expressions",
    "data": "statements",
    "under-the-hood": "implementation",
    "testimony-reference": "testimony",
}

STATUS = {"settled": "Settled", "proposed": "Proposed", "open": "Open"}

SMILEY = (
    '<svg class="smiley" viewBox="0 0 100 100" aria-hidden="true">'
    '<circle cx="50" cy="50" r="48" fill="#ffda46"/>'
    '<g fill="#243e30"><ellipse cx="35" cy="41" rx="4.1" ry="7.5"/><ellipse cx="65" cy="41" rx="4.1" ry="7.5"/></g>'
    '<path d="M25 57 C35 78 66 78 77 55" fill="none" stroke="#243e30" stroke-width="4" stroke-linecap="round"/>'
    "</svg>"
)

# --- syntax highlighting -------------------------------------------------

CODE_TOKEN = re.compile(
    r"""
    (?P<com>\#[^\n]*)
  | (?P<str>(?<![\w])[rRbBfF]{0,2}(?:\"\"\"[\s\S]*?\"\"\"|'[^'\n]*'|"[^"\n]*"))
  | (?P<truth>\b(?:verity|falsity)\b)
  | (?P<test>\b(?:because|forall|exists)\b)
  | (?P<kw>\b(?:def|match|case|if|elif|else|for|in|while|return|assert
               |import|from|as|and|or|not|is|None|True|False|lambda|pass|yield
               |with|try|except|raise|class|async|await|global|nonlocal|del)\b)
  | (?P<deco>^\s*@[\w.]+)
  | (?P<num>\b\d+(?:\.\d+)?\b)
  | (?P<sh>^\$(?=\s))
    """,
    re.VERBOSE | re.MULTILINE,
)

EBNF_TOKEN = re.compile(
    r"(?P<com>\(\*[\s\S]*?\*\))"
    r"|(?P<str>\"[^\"\n]*\"|'[^'\n]*')"
    r"|(?P<test>::=)"
    r"|(?P<kw>\b[A-Z][A-Z_]+\b)"
    r"|(?P<op>[|*+?\[\]])",
)

OUT_TOKEN = re.compile(
    r"(?P<truth>^(?:verity|falsity)\b)"
    r"|(?P<label>\b(?:witnessed|refuted|counterexample|witness|all of|none of|not|literal|hint)(?=:|$)|\bfailed \d+ of \d+:)"
    r"|(?P<test>\[[a-z0-9_]+(?:\.[a-z0-9_]+)*\]$)",
    re.MULTILINE,
)


def highlight(code: str, pattern: re.Pattern) -> str:
    out, pos = [], 0
    for m in pattern.finditer(code):
        out.append(html.escape(code[pos : m.start()], quote=False))
        out.append(f'<span class="t-{m.lastgroup}">{html.escape(m.group(), quote=False)}</span>')
        pos = m.end()
    out.append(html.escape(code[pos:], quote=False))
    return "".join(out)


def render_code(match: re.Match) -> str:
    kind, code = match.group(1), match.group(2).strip("\n")
    pattern = {"out": OUT_TOKEN, "ebnf": EBNF_TOKEN}.get(kind, CODE_TOKEN)
    label = {"ity": "verity", "out": "output", "py": "python", "sh": "shell", "ebnf": "grammar"}[kind]
    return (
        f'<div class="code code-{kind}"><span class="code-label">{label}</span>'
        f"<pre><code>{highlight(code, pattern)}</code></pre></div>"
    )


# --- page assembly -------------------------------------------------------


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def number_sections(body: str, number) -> tuple[str, list[tuple[str, str]]]:
    sections = []

    def repl(m: re.Match) -> str:
        attrs, inner = m.group(1), m.group(2)
        ident = re.search(r'id="([^"]+)"', attrs)
        ident = ident.group(1) if ident else slugify(inner)
        prefix = ""
        if number is not None:
            prefix = f'<span class="secnum">{number}.{len(sections) + 1}</span> '
        sections.append((ident, re.sub(r"<[^>]+>", "", inner)))
        return f'<h2 id="{ident}">{prefix}{inner}<a class="anchor" href="#{ident}" aria-label="Link to this section">#</a></h2>'

    body = re.sub(r"<h2([^>]*)>(.*?)</h2>", repl, body)
    return body, sections


def label(number, title: str) -> str:
    if number is None:
        return title
    if isinstance(number, str):
        return f"Appendix {number}. {title}"
    return f"{number}. {title}"


def sidebar(current: str) -> str:
    groups = [
        ("Front matter", [e for e in TOC if e[2] is None]),
        ("Reference", [e for e in TOC if isinstance(e[2], int)]),
        ("Appendices", [e for e in TOC if isinstance(e[2], str)]),
    ]
    parts = []
    for heading, entries in groups:
        parts.append(f'<p class="toc-heading">{heading}</p><ul>')
        for slug, title, number in entries:
            cur = ' aria-current="page"' if slug == current else ""
            num = f'<span class="toc-num">{number}</span>' if number is not None else ""
            parts.append(f'<li><a href="{slug}.html"{cur}>{num}{title}</a></li>')
        parts.append("</ul>")
    return "\n".join(parts)


def page(index: int) -> str:
    slug, title, number = TOC[index]
    body = (SRC / f"{slug}.html").read_text()
    body = re.sub(r'<pre class="(ity|out|py|sh|ebnf)">(.*?)</pre>', render_code, body, flags=re.S)
    body = body.replace("<!--smiley-->", SMILEY)
    body = re.sub(
        r"\[\[(settled|proposed|open)\]\]",
        lambda m: f'<span class="status status-{m.group(1)}">{STATUS[m.group(1)]}</span>',
        body,
    )
    body, sections = number_sections(body, number if isinstance(number, (int, str)) else None)

    if slug != "cover":
        num = f'<span class="h1-num">{"Appendix " + number if isinstance(number, str) else "Section " + str(number)}</span>' if number is not None else ""
        body = f"<h1>{num}{title}</h1>\n{body}"

    on_page = ""
    if sections:
        items = "".join(f'<li><a href="#{i}">{html.escape(t)}</a></li>' for i, t in sections)
        on_page = f'<nav class="on-page" aria-label="On this page"><p>On this page</p><ul>{items}</ul></nav>'

    prev_link = next_link = ""
    if index > 0:
        p = TOC[index - 1]
        prev_link = f'<a class="pager-prev" href="{p[0]}.html"><span>Previous</span>{label(p[2], p[1])}</a>'
    if index < len(TOC) - 1:
        n = TOC[index + 1]
        next_link = f'<a class="pager-next" href="{n[0]}.html"><span>Next</span>{label(n[2], n[1])}</a>'

    page_title = BOOK_TITLE if slug == "cover" else f"{label(number, title)} | {BOOK_TITLE}"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<script>document.documentElement.classList.add("js")</script>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
<meta name="description" content="{BOOK_TITLE}: the reference documentation for Verity, a functional language that compiles to Python and whose booleans testify.">
<link rel="icon" href="../favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Oxygen+Mono&display=swap" rel="stylesheet">
<link rel="stylesheet" href="book.css">
</head>
<body class="page-{slug}">
<a class="skip" href="#content">Skip to content</a>
<header class="topbar">
  <button class="menu-btn" type="button" aria-controls="sidebar" aria-expanded="false">
    <span aria-hidden="true">&#9776;</span> Contents
  </button>
  <a class="topbar-title" href="cover.html">{SMILEY}<span>{BOOK_TITLE}</span></a>
  <a class="topbar-link" href="../index.html">Verity home</a>
</header>
<div class="layout">
  <aside class="sidebar" id="sidebar" aria-label="Book contents">
    <a class="sidebar-cover" href="cover.html">{SMILEY}<span>{BOOK_TITLE}</span></a>
    <nav>{sidebar(slug)}</nav>
  </aside>
  <main id="content" class="content">
    <article>
{body}
    </article>
    <nav class="pager" aria-label="Previous and next pages">{prev_link}{next_link}</nav>
    <footer class="page-footer">
      <p>{BOOK_TITLE} &middot; Henrik Gombos and Pranav Balakrishnan &middot; <a href="{REPO}/blob/main/book/src/{slug}.html">Source for this page</a></p>
    </footer>
  </main>
  {on_page}
</div>
<script src="book.js" defer></script>
</body>
</html>
"""


# --- plain text (llms.txt, verity.txt) ----------------------------------

SITE = "https://www.verity.garden/book"


def to_text(fragment: str, number) -> str:
    """Render one page fragment as plain text: headings numbered like the HTML, code verbatim."""
    t = fragment.replace("<!--smiley-->", "")
    t = re.sub(r"\[\[(settled|proposed|open)\]\]", r"[\1]", t)
    count = [0]

    def h2(m: re.Match) -> str:
        count[0] += 1
        title = re.sub(r"<[^>]+>", "", m.group(1))
        head = f"{number}.{count[0]} {title}" if number is not None else title
        return f"\n\n{head}\n{'-' * len(head)}\n"

    def pre(m: re.Match) -> str:
        code = html.unescape(m.group(2)) if m.group(1) not in ("ity", "out", "py", "sh", "ebnf") else m.group(2)
        code = code.strip("\n")
        return "\n\n" + "\n".join("    " + line for line in code.split("\n")) + "\n\n"

    t = re.sub(r'<pre class="([a-z]+)">(.*?)</pre>', pre, t, flags=re.S)
    t = re.sub(r"<h2[^>]*>(.*?)</h2>", h2, t, flags=re.S)
    t = re.sub(r"<h3[^>]*>(.*?)</h3>", lambda m: "\n\n" + re.sub(r"<[^>]+>", "", m.group(1)) + "\n", t, flags=re.S)
    t = re.sub(r"<li[^>]*>", "\n- ", t)
    t = re.sub(r"<dt[^>]*>", "\n\n", t)
    t = re.sub(r"<dd[^>]*>", "\n  ", t)
    t = re.sub(r"<tr[^>]*>", "\n", t)
    t = re.sub(r"</t[dh]>\s*<t[dh][^>]*>", " | ", t)
    t = re.sub(r"</?(p|ul|ol|table|thead|tbody|div|aside|dl)[^>]*>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = re.sub(r"\n\n(?=- )", "\n", t)
    for _ in range(2):
        t = re.sub(r"(\n[^\n]* \| [^\n]*)\n\n(?=[^\n]* \| )", r"\1\n", t)
    return t.strip()


def plain_text() -> tuple[str, str]:
    parts, index = [], []
    for slug, title, number in TOC:
        if slug == "cover":
            continue
        heading = label(number, title)
        body = to_text((SRC / f"{slug}.html").read_text(), number if isinstance(number, (int, str)) else None)
        parts.append(f"{'=' * len(heading)}\n{heading}\n{'=' * len(heading)}\n\n{body}\n")
        lede = re.search(r"<p>(.*?)</p>", (SRC / f"{slug}.html").read_text(), re.S)
        first = re.sub(r"<[^>]+>|\s*\[\[\w+\]\]", "", lede.group(1)) if lede else f"{title} of Verity terms."
        index.append(f"- [{heading}]({SITE}/{slug}.html): {html.unescape(' '.join(first.split()))}")
    full = (
        f"{BOOK_TITLE}\nThe Verity language reference, by Henrik Gombos and Pranav Balakrishnan.\n"
        f"Generated from {REPO}/tree/main/book/src. HTML version: {SITE}/cover.html\n\n"
        + "\n\n".join(parts)
    )
    llms = (
        "# Verity\n\n"
        "> Verity is Python whose truth values explain themselves. Python 3.12 syntax plus the literals "
        "`verity`/`falsity`, `p because m`, and `forall`/`exists` quantifiers; every truth carries testimony "
        "(why it holds), rendered as text or as JSON (schema verity.testimony/0). Compiles to Python.\n\n"
        "Status markers: [settled] is spec, [proposed] and [open] are not yet.\n\n"
        "## Reference\n\n" + "\n".join(index) + "\n\n"
        f"## Optional\n\n- [Full reference as one text file]({SITE}/verity.txt)\n"
        f"- [Source repository]({REPO}): spec in CLAUDE.md, conformance examples in examples/\n"
    )
    return llms, full


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for asset in (ROOT / "assets").iterdir():
        shutil.copy2(asset, OUT / asset.name)
    for i, (slug, _, _) in enumerate(TOC):
        (OUT / f"{slug}.html").write_text(page(i))
    (OUT / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>Verity Programming</title>'
        '<meta http-equiv="refresh" content="0; url=cover.html">'
        '<link rel="canonical" href="cover.html"><a href="cover.html">Verity Programming</a>\n'
    )
    for old, new in REDIRECTS.items():
        (OUT / f"{old}.html").write_text(
            f'<!doctype html><meta charset="utf-8"><title>Moved</title>'
            f'<meta http-equiv="refresh" content="0; url={new}.html">'
            f'<link rel="canonical" href="{new}.html"><a href="{new}.html">This page has moved.</a>\n'
        )
    for stale in OUT.glob("*.html"):
        if stale.stem not in {e[0] for e in TOC} | set(REDIRECTS) | {"index"}:
            stale.unlink()
    llms, full = plain_text()
    (OUT / "llms.txt").write_text(llms)
    (OUT / "verity.txt").write_text(full)
    print(f"built {len(TOC)} pages, {len(REDIRECTS)} redirects, llms.txt and verity.txt into {OUT}")


if __name__ == "__main__":
    main()
