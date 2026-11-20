; font.asm: English pair glyphs in PSX.EXE (docs/re/text.md §English). armips, run by tools/insert.py:
;   armips asm/font.asm -strequ EXE_IN <PSX.EXE> -strequ EXE_OUT <out> -strequ FONT_BIN <en6x12.bin>
;
; 0x800FDCA8 renders font cell `code` (a1) from a 1bpp image (a0, 24-byte rows, bit 0 = leftmost pixel) into a
; 2bpp buffer (a2). Every printer path (event scripts, PSX.EXE strings, menus) goes through it. The hook body is
; asm/pair.inc (shared with asm/epilog.asm).

.psx
.open EXE_IN, EXE_OUT, 0x8000F800

FREE      equ 0x80124E60          ; zero run 0x80124E5D-0x80125AF0, no code references (docs/re/space.md)
GLYPH     equ 0x800FDCA8

.org GLYPH
    j       pair_hook
    nop                            ; replaced: addiu sp,-0x40 / sw s7 (redone in the hook)

.org FREE
.include "pair.inc"
pair_orig:
    addiu   sp, sp, -0x40
    j       GLYPH + 8
    sw      s7, 0x34(sp)
.include "pair_data.inc"
pair_end:

NAME_FREE equ 0x80125980          ; tail of the same zero run, after the grown strings (tools/insert.py REPOINT)
.include "name.inc"

; Status screens' Sex value (function 0x80110FC0 copies these two 4-byte slots, 男{end} 女{end}, to its stack and
; draws one). Only one 12-px cell of that field reaches the screen: "Male" pointed to from free space drew as "Ma"
; (2026-11-21, work/qa/p8/sexz.png), so the value is one pair cell: "M" / "F" (docs/decisions.md D15).
.org 0x80183FA4
    .ascii  "M "                   ; a pair code is two ASCII bytes per halfword (tools/en.py)
    .halfword 0xFFFF
    .ascii  "F "
    .halfword 0xFFFF

.if pair_end > 0x80125500
    .error "font hook overflows into the grown-string space (tools/insert.py REPOINT)"
.endif
.if name_end > 0x80125AF0
    .error "name-entry code overflows the zero run (docs/re/space.md)"
.endif

.close
