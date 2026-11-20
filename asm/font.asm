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

.if pair_end > 0x80125500
    .error "font hook overflows into the grown-string space (tools/insert.py REPOINT)"
.endif

.close
