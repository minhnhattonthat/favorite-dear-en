# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-20 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-11-20 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-20 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-20 | Abbreviations | engine work first (default), abbreviate | Engine work first (skill default; not overridden). |
| D5 | 2026-11-20 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); leave the original Japanese logo only if it has no official English version. |
| D6 | 2026-11-20 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through every checkpoint, report at the end. |
| D7 | 2026-11-20 | Existing saves / memory cards / savestates | use the user's, build the debug tool | None provided; build the debug tool as usual. |
| D9 | 2026-11-20 | English font/encoding (pre-approved, D6: agent's call) | VWF (printer rewrite: glyphs go to VRAM one by one at 4-px steps), 8-px fixed cells, two 6-px letters per 12-px cell | Pair glyphs: 2 letters per halfword/cell, original 6x12 font (`fonts/en6x12.txt`), hook at 0x800FDCA8. Doubles letters per line, keeps the engine's layout logic, and costs 1 byte per letter, which the 0x7000 script buffer needs. |
| D8 | 2026-11-20 | Publishing | publish, hold | Never run `gh release create` or change repo visibility; the run ends at a built and verified release zip. Commit and push to main at each phase end. |
