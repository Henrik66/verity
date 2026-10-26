# Dev-tool homepages that present code well

References for Verity's lead demo, where a falsity explains itself. These pages were picked because they show code next to its output or effect, and especially because some treat explanatory output (errors, diagnostics, results) as a feature in its own right. All URLs were checked and loaded on 2026-10-26.

1. **Elm**: https://elm-lang.org/
   The "No Runtime Exceptions" panel puts a real compiler error on the homepage: `-- TYPE MISMATCH --- Main.elm`, the offending line, red `^^^^` carets, "This `toInt` call produces: Maybe Int / But `drop` needs: Int", and then a green `Hint:`. The diagnostic itself is the selling point. It uses a small set of meaningful colors (cyan header, red caret, yellow type, green fix) on monospace text, sitting beside a single line of prose. This is the closest analogue to Verity's indented refutation.

2. **Gleam**: https://gleam.run/
   Each section pairs one heading, one sentence and one short snippet. The "friendly errors" section shows a diagnostic with a file:line, a caret and "Did you mean `name`?". The tooling section shows a terminal transcript (`gleam add`, `gleam test`) with its real output. Snippets stay short and are never shown with output they don't need.

3. **Julia**: https://julialang.org/
   A carousel of REPL transcripts with titles like "Multiple Dispatch" and "Broadcasting". Input sits behind a `julia>` prompt and output appears directly below it with no prompt, in the REPL's own formatting. Because input and output live in one block, the reader sees the effect right where the code is. This is a good model for showing `all_odd |> explain` followed by its testimony.

4. **Unison**: https://www.unison-lang.org/
   The examples are interactive: you can click any dependency to see its definition and docs. A separate demo plays back an editor pane next to a UCM terminal pane, so the code and the tool's response sit side by side. The click-to-reveal idea could apply to Verity, where clicking a falsity would expand its refutation.

5. **Bun**: https://bun.sh/
   The "A minute with Bun" section is a fake terminal window with a `01 / 05` step indicator. It auto-plays real (abridged) output for each step, pauses on hover and has a replay control. This shows how to stage an "aha" over time without making the visitor type anything.

6. **Pyret**: https://pyret.org/
   Small embedded editors each have a "Run it!" button, so the code runs in place and image results appear next to the snippet. Its `examples:` blocks (`cb(3) is 27`) present tests as documentation. It is a close peer for a teaching-oriented functional language, although the page never actually shows a test failure, which is a gap Verity can fill.

7. **Lean 4**: https://lean-lang.org/
   Short `example ... := by grind` proofs, plus one longer annotated proof that there are infinitely many primes. Each block has a one-line caption and an "open in Playground" link. Lean's site also shows the limit of this approach: proofs appear only as source, with no goal state or checker output. The "why it holds" is invisible, and Verity's demo should make it visible.

8. **Tailwind CSS**: https://tailwindcss.com/
   The hero places a roughly 15-line snippet directly above its rendered album-cover card, so each class (`size-48`, `shadow-xl`, `rounded-2xl`) can be traced to a visible effect. It is a clear example of a one-to-one match between source and result. Verity could do the same by linking `primes[0]` in the refutation back to the list in the source.

Notes for showing explanatory output:
- Elm and Gleam show that a diagnostic can be the hero if it is calm, colored sparingly and written in plain sentences.
- A REPL transcript (Julia) or an auto-playing terminal (Bun) gets output on screen with no interaction required. Run buttons (Pyret) and click-to-expand (Unison) add depth for people who want it.
- None of these pages shows a counterexample. Lean and Dafny (https://dafny.org/, which shows only an IDE screenshot) leave the "why" out, so that space is open for Verity.

## Likes / hates (human)

