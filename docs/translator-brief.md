# Translator brief (event scripts)

Read in parts (offset/limit): context-mode trims whole-file Reads above ~4 KB.

1. Read `glossary.md` (rulings, style rules, name tables) and `docs/style-reference.md` once it exists; until then
   `trans/en/b001.tsv` is the reference for voice (archangel formal; the advisor teasing and feminine; Ryudral casual,
   "See ya!"; the angel polite and plain).
2. Input `trans/batches/bNNN.tsv`: `id<TAB>jp`. The JP has its soft line breaks removed: each `{n}` left is
   structural. Rows are in sector (script file) order, so neighbours are context.
3. Output `trans/en/bNNN.tsv` (header `id<TAB>en`), written with the file-write tool, one row per input id:
   - keep every control code (`{spk:..}`, `{e0:..}`, `{n}`, `{wait}`, `{clear}`, `{end}`, `{name:..}`, `{f7:..}`...)
     in the same order; only the Japanese text between them changes. Do not add `{n}`: `tools/wrap.py` breaks lines
     at 40 letters and adds continuation pages itself.
   - plain ASCII plus … — ♥ ♪ é. No ASCII braces in text. Choices keep `　｛Option　｝` (see glossary).
   - `{name:0080}` is the angel (up to 10 letters), `{name:0180}`/`{name:0280}` heroes or items (runtime). No suffix
     glued to a name code except `'s`; never "a/an" right before one; keep them gender-neutral ("them").
   - `-` alone for a row that is data, not text (garbled kana/kanji soup, item-name lists run together); add a line
     to glossary "Decisions from earlier batches" saying why.
4. Run `python -X utf8 tools/batches.py check bNNN` until it prints `bNNN: OK`, then
   `python -X utf8 tools/batches.py merge` (writes the wrapped `en` into `script/events/*.tsv`).
5. Quality bar (past mistakes in other projects): names exactly as in the glossary; jokes and character quirks kept
   (rough speech stays rough); no "1th"-style suffixes; no stock "GET!" phrasing; repeated variants of one message
   (rows that differ by one word) translated consistently.
6. Report `NEW TERM: jp -> en`, `UNSURE: id - note`, `CUT: id - what was dropped`; terms go into glossary.md tables.
