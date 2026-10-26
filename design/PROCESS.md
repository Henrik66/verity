# Verity Homepage: Design Process

This file is the standing design process for the Verity homepage ('site/'). Read it, and 'design/taste.md', before doing any design work. Follow it exactly unless a human tells you otherwise in the current session.

## The goal

Redesign the homepage into a garden-themed, botanical page with yellow smiley faces throughout. It should feel handmade and specific, never generic. We get there through many small, fast iterations steered by explicit human taste, not by one big generation.

## The anchor image

The visual starting point is 'design/reference/anchor.png', a concept image made with an image model.

- Treat it as the north star for mood, palette, and density. It is not a spec to trace pixel for pixel.
- Before the first variant round, study it and write 'design/tokens.md'. Extract the palette as hex values, type character (serif or sans, weight, feel), line quality of illustrations, smiley style, texture, and the amount of empty space.
- Every variant uses those tokens. If a round shows a token is wrong, propose the change in your summary; don't silently drift.
- Image-model output often has details that don't survive as real UI: illegible text, impossible layouts, inconsistent lighting. Keep the feeling and drop the artifacts. Note in tokens.md which parts of the image you treated as artifacts.

## Files

```
design/
  reference/anchor.png   the anchor image
  tokens.md              extracted design tokens (from the anchor)
  taste.md               likes and hates from humans; append-only
  research/              reference notes from research rounds
  render.py              screenshots every variant at 1440px and 390px
  gallery.html           side-by-side view of the latest renders
  shots/                 screenshot output (gitignored)
site/
  variants/<section>/<letter>.html   variant files, one per idea
  index.html             assembled page; only locked sections go here
```

## The loop

1. Read taste.md and tokens.md. Every time, even mid-session.
2. Generate variants for one section only. Default is 4 to 6 variants, labeled a, b, c... Variants must differ in concept or layout, not just color or spacing.
3. Render all of them with render.py at both widths and rebuild gallery.html.
4. Look at your own screenshots before reporting. Fix anything broken (overflow, overlapping text, missing assets, illegible contrast) before a human sees it.
5. Report in under 10 lines: one line per variant saying what idea it explores, plus anything you're unsure about.
6. Stop and wait for the human's likes and hates. Don't start the next round on your own.
7. Append the human's feedback to taste.md, verbatim and dated.
8. Generate the next round by combining the winners' strengths and avoiding everything in the hates list.

Plan on 3 to 5 rounds per section. A section is locked only when a human says it's locked.

## Order of work

1. Research round (once). Use subagents with three lenses: botanical illustration (seed catalogs, herbarium plates, garden guides), playful brands that use a recurring motif without clutter, and language or dev-tool homepages that present code well. Each returns 6 to 8 references with one line on what specifically works. Save to design/research/ and wait for the human to mark likes and hates.
2. The testimony demo first. It leads the page: a falsity explaining itself is the one thing no other language's homepage can show. Every other section serves it.
3. Then the hero, the why section, the roadmap (seed, sprout, bloom per milestone), and the footer.
4. Detail passes after a section locks. One detail per round, 4 variants each: smiley density and placement, vine line weight and endings, hover and scroll motion, heading type, code block styling.
5. Assemble the locked sections into site/index.html, then run one or two whole-page rounds on rhythm and spacing.

## Rules

- Never regenerate the whole page. Work one section or one detail at a time.
- Never edit a locked section unless asked.
- The smiley faces are simple, original, round, and yellow. Don't copy any existing smiley logo or brand mark.
- Illustrations are inline SVG, hand-drawn in feel. No stock photos, no emoji as decoration, no generic gradient blobs.
- Fonts come from Google Fonts. Code uses a monospace font and real Verity syntax ('verity'/'falsity', Coconut-style pipes, testimony output).
- Responsive at 390px, WCAG AA contrast, and respect prefers-reduced-motion.
- When in doubt, pick the more specific, stranger option over the safe, generic one. Generic is the failure mode.

## Working as two people

- Claim a section before working on it by adding a line at the top of taste.md: 'CLAIMED: <section> by <name>'. Remove it when the section locks.
- Both humans' feedback goes in the same taste.md, with names. If two entries conflict, flag it rather than picking one.
- Commit after every round with a message like 'design(hero): round 3, variants a-e'.
- The gallery deploys with the site at '/design/' so either person can review rounds asynchronously.

## Definition of done

A section is done when a human has locked it, it renders cleanly at both widths, and it uses only tokens from tokens.md. The page is done when every section is locked and the whole-page passes are approved.
