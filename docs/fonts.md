# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/label14.txt | DejaVu Sans Condensed 2.37 (https://github.com/dejavu-fonts/dejavu-fonts/releases/tag/version_2_37, dejavu-fonts-ttf-2.37.zip sha1 bdc4350b771c6c23e8a40b2413595d1055cff2ab), rasterized at 14 px with no smoothing by `tools/labelfont.py make` | Bitstream Vera licence + public domain (DejaVu changes) | yes (the licence allows embedding and modified copies; bitmaps of it are not sold alone) | status-screen background labels (gfx/e012-e014.tsv) | rasterized to 1 bpp, ASCII 0x21-0x7E only |
| fonts/en6x12.txt | drawn for this project (2026-11-20), classic 5x7 dot-matrix shapes in a 6x12 half cell | MIT, same as repo | yes | every in-game English letter (pair glyphs, asm/font.asm) | - |
