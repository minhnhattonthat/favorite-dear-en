# Text engine

## Script location (verified: decoded the on-screen line "実はあなたにとても重要な任務を／まかせたいのです。")

The opening event's dialogue is plain (uncompressed) 16-bit LE codes inside PSX.EXE, e.g. that line at file
0x15A8C8 (a second copy at 0x15B888). At runtime it sits at RAM 0x8016xxxx with pointer tables of 0x8016xxxx words
just before it (e.g. RAM 0x169F00). Unknown yet: how much of the game's script is in PSX.EXE vs. loaded from GDATA.BIN,
and the pointer table format. Next step: find the script's pointer tables (xref their vaddrs, `tools/retools.py`) and
whether other event banks are loaded from GDATA (watch RAM 0x8016xxxx writes across a scene change).

Reading the script in RAM: read breakpoints on the line (0x8016A2C0) never fired, so the engine likely copies or reads
the text through another path; write breakpoints work (see below).

## Encoding (verified on the line above)

16-bit little-endian codes = font cell index.
- 0xFFFE newline, 0xFFFC wait for button / next page, 0xFFFF end of message (often followed by 0x0000).
  Event VM at ~0x800CA500-0x800CCC80 also compares against 0xFFFD and 0xFFFB (meaning unknown).
- 0x0000-0x001F punctuation and symbols (、。・：？！ゞ ー～ “” （） ｛｝ 「」 『』 － ＄), 0x0016-0x001F? digits ０-９ (read
  from the sheet; exact offsets to be confirmed in tbl).
- 0x0020+ : a few Latin letters (K O X), then hiragana from ぁ in gojuon order with gaps (no ぢ, ゎ, ゐ, ゑ seen:
  あ=0x24 い=0x26 か=0x2D せ=0x3D た=0x41 な=0x4B に=0x4C は=0x50 ま=0x5F も=0x63 を=0x70), then katakana from ~0x76.
- 0x00C0-0x05CC: kanji, only the ones the game uses, in Shift-JIS order (哀 愛 挨 握 圧 扱 安 暗 案 闇 以 伊 位 依 偉 囲 委 威 ...).
- 0x05CD-0x05DD: more punctuation (。=0x05CE, 、=0x05CD, ……=0x05CF?, 「」 etc.) - confirm in tbl.

Plan for `tbl/jp.tbl`: render each glyph (`tools/font.py`), match against MS Gothic 12 px (C:/Windows/Fonts/msgothic.ttc,
FreeType embedded bitmaps) with the Shift-JIS order as a monotonic constraint for kanji (DP alignment), then eyeball
low-score cells on a labelled sheet. Cross-check by decoding the opening event and comparing with screenshots.

## Font (verified: traced the glyph writer)

12x12 1bpp, one image 192 px wide (16 cells per row), 24 bytes per row, bit 0 = leftmost pixel. Code c -> cell
(c & 15, c >> 4). RAM 0x80130BC0 = PSX.EXE 0x1213C0; ~0x5E0 cells = ~27 KB.
- 0x800FC97C draw-glyph: calls 0x800FDCA8(font=0x80130BC0, code, buf) which reads 12x12 pixels through 0x800FDDF0
  (bit fetch) into a 2bpp buffer, then expands to 4bpp halfwords into the line buffer.
- Line buffer: RAM 0x8017C320, 120 bytes (240 px 4bpp) per pixel row; writers 0x800FD81C (clear), 0x800FCB24 (glyph).
  Uploaded to VRAM ~(960,256) as a 4bpp texture (values 0/1). Found with `watch.lua` write mode from
  `work/qa/ng/s007500.sstate`.
- Box: 2-3 lines; line 1 of the first event holds 15 full-width glyphs ("実はあなたにとても重要な任務を").

English plan (phase 5): the cell is 12 px; a half-width or VWF font drawn through the same 1bpp image path is the
obvious route (widths per glyph in a new table; the glyph writer already takes a per-call width in $s0).
