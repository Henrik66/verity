"""Render every homepage variant and rebuild the design gallery.

Usage:  python3 design/render.py [section]

* Screenshots site/variants/<section>/<letter>.html at 1440px and 390px
  into design/shots/ (gitignored) for review.
* Rebuilds design/gallery.html (local review, live iframes).
* Publishes the gallery and variants to site/public/design/ so they deploy
  with the site at /design/.

Each variant declares its idea with <meta name="variant-idea" content="...">.
Needs Google Chrome (set CHROME_PATH to override) and, for the 390px crop,
Pillow (falls back to an uncropped screenshot without it).
"""

import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VARIANTS = ROOT / "site" / "variants"
SHOTS = ROOT / "design" / "shots"
GALLERY = ROOT / "design" / "gallery.html"
PUBLISH = ROOT / "site" / "public" / "design"
CHROME = os.environ.get("CHROME_PATH", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

DESKTOP = (1440, 1100)
PHONE_W, PHONE_H = 390, 1500


def chrome_shot(url: str, out: Path, width: int, height: int) -> None:
    subprocess.run(
        [
            CHROME, "--headless=new", "--hide-scrollbars", "--allow-file-access-from-files",
            f"--window-size={width},{height}", "--virtual-time-budget=4000",
            f"--screenshot={out}", url,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def render(variant: Path) -> None:
    section, letter = variant.parent.name, variant.stem
    SHOTS.mkdir(parents=True, exist_ok=True)
    chrome_shot(variant.as_uri(), SHOTS / f"{section}-{letter}-1440.png", *DESKTOP)

    # Headless Chrome enforces a minimum window width above 390px, so render
    # the phone view inside a 390px iframe and crop to it.
    wrapper = SHOTS / f"_{section}-{letter}-390.html"
    wrapper.write_text(
        f'<!doctype html><body style="margin:0"><iframe src="{variant.as_uri()}" '
        f'style="width:{PHONE_W}px;height:{PHONE_H}px;border:0;display:block"></iframe>'
    )
    phone = SHOTS / f"{section}-{letter}-390.png"
    chrome_shot(wrapper.as_uri(), phone, 600, PHONE_H)
    wrapper.unlink()
    try:
        from PIL import Image

        Image.open(phone).crop((0, 0, PHONE_W, PHONE_H)).save(phone)
    except ImportError:
        pass


def idea(variant: Path) -> str:
    m = re.search(r'<meta name="variant-idea" content="([^"]*)"', variant.read_text())
    return m.group(1) if m else ""


def gallery(sections: dict[str, list[Path]], base: str) -> str:
    blocks = []
    for section, variants in sections.items():
        cards = []
        for v in variants:
            src = f"{base}{section}/{v.name}"
            cards.append(f"""
      <article class="card">
        <header><h3>{section} / {v.stem}</h3><a href="{src}" target="_blank" rel="noopener">open</a></header>
        <p>{html.escape(idea(v))}</p>
        <div class="frames">
          <div class="desk"><iframe src="{src}" title="{section} {v.stem} at 1440px" loading="lazy"></iframe></div>
          <div class="phone"><iframe src="{src}" title="{section} {v.stem} at 390px" loading="lazy"></iframe></div>
        </div>
      </article>""")
        blocks.append(f'<section><h2>{section}</h2>{"".join(cards)}</section>')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Verity design gallery</title>
<style>
  :root {{ --ink: #243e30; --paper: #f7f6ec; --line: #c9d3bd; }}
  body {{ margin: 0; padding: 24px 16px 64px; background: var(--paper); color: var(--ink); font: 15px/1.5 system-ui, sans-serif; }}
  h1 {{ margin: 0 0 4px; font-size: 22px; }}
  .sub {{ margin: 0 0 24px; color: #4b5f50; }}
  h2 {{ font-size: 18px; border-bottom: 1.5px solid var(--ink); padding-bottom: 4px; margin-top: 32px; }}
  .card {{ border: 1px solid var(--line); border-radius: 8px; padding: 12px 14px; margin: 16px 0; background: #fff; }}
  .card header {{ display: flex; justify-content: space-between; align-items: baseline; }}
  .card h3 {{ margin: 0; font-size: 16px; }}
  .card p {{ margin: 4px 0 10px; color: #4b5f50; }}
  .frames {{ display: flex; gap: 14px; align-items: flex-start; overflow-x: auto; }}
  .desk {{ flex: none; width: 720px; height: 550px; overflow: hidden; border: 1px solid var(--line); }}
  .desk iframe {{ width: 1440px; height: 1100px; border: 0; transform: scale(.5); transform-origin: 0 0; }}
  .phone {{ flex: none; width: 390px; height: 550px; overflow: hidden; border: 1px solid var(--line); }}
  .phone iframe {{ width: 390px; height: 550px; border: 0; }}
</style>
</head>
<body>
<h1>Verity design gallery</h1>
<p class="sub">Latest variants, live at 1440px (scaled to half size) and 390px. Feedback goes in design/taste.md, dated and with your name.</p>
{"".join(blocks)}
</body>
</html>
"""


def main() -> None:
    only = sys.argv[1] if len(sys.argv) > 1 else None
    sections: dict[str, list[Path]] = {}
    for d in sorted(p for p in VARIANTS.iterdir() if p.is_dir()):
        sections[d.name] = sorted(d.glob("*.html"))

    for section, variants in sections.items():
        if only and section != only:
            continue
        for v in variants:
            render(v)
            print(f"rendered {section}/{v.stem}")

    GALLERY.write_text(gallery(sections, "../site/variants/"))
    if PUBLISH.exists():
        shutil.rmtree(PUBLISH)
    shutil.copytree(VARIANTS, PUBLISH / "variants")
    (PUBLISH / "index.html").write_text(gallery(sections, "variants/"))
    print(f"gallery: {GALLERY.relative_to(ROOT)} and {PUBLISH.relative_to(ROOT)}/index.html")


if __name__ == "__main__":
    main()
