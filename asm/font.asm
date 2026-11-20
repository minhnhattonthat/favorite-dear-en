; font.asm: English pair glyphs (docs/re/text.md §English). armips, run by tools/insert.py:
;   armips asm/font.asm -strequ EXE_IN <PSX.EXE> -strequ EXE_OUT <out> -strequ FONT_BIN <en6x12.bin>
;
; 0x800FDCA8 renders font cell `code` (a1) from a 1bpp image (a0, 24-byte rows, bit 0 = leftmost pixel) into a
; 2bpp buffer (a2). Every printer path (event scripts, PSX.EXE strings, menus) goes through it. Codes 0x2020-0xFEFF
; are two English letters (low byte left, high byte right): the hook ORs their 6x12 glyphs into cell 0 of a
; scratch image and renders that instead. Codes below 0x2000 fall through to the original font unchanged.

.psx
.open EXE_IN, EXE_OUT, 0x8000F800

FREE      equ 0x80124E60          ; zero run 0x80124E5D-0x80125AF0, no code references (docs/re/space.md)
GLYPH     equ 0x800FDCA8
FIRSTCH   equ 0x20

.org GLYPH
    j       pair_hook
    nop                            ; replaced: addiu sp,-0x40 / sw s7 (redone in the hook)

.org FREE
pair_hook:
    andi    t0, a1, 0xFFFF
    sltiu   t1, t0, 0x2000
    bnez    t1, @@orig
    nop
    li      t2, scratch
    andi    t3, t0, 0xFF           ; left letter
    srl     t4, t0, 8              ; right letter
    addiu   t3, t3, -FIRSTCH
    addiu   t4, t4, -FIRSTCH
    sll     t5, t3, 1              ; *12 = *8 + *4
    addu    t3, t5, t3
    sll     t3, t3, 2
    sll     t5, t4, 1
    addu    t4, t5, t4
    sll     t4, t4, 2
    li      t5, font
    addu    t3, t3, t5
    addu    t4, t4, t5
    li      t6, 12
@@row:
    lbu     t7, 0(t3)
    lbu     t8, 0(t4)
    addiu   t3, t3, 1
    sll     t8, t8, 6
    or      t7, t7, t8
    sb      t7, 0(t2)
    srl     t7, t7, 8
    sb      t7, 1(t2)
    addiu   t6, t6, -1
    bnez    t6, @@row
    addiu   t4, t4, 1
    li      a0, scratch
    move    a1, zero
@@orig:
    addiu   sp, sp, -0x40
    j       GLYPH + 8
    sw      s7, 0x34(sp)

.align 4
font:
    .incbin FONT_BIN
.align 4
scratch:                           ; 12 rows x 24 bytes; only bytes 0-1 of each row are written
    .fill 12 * 24, 0
pair_end:

.if pair_end > 0x80125AF0
    .error "font hook overflows the free run"
.endif

.close
