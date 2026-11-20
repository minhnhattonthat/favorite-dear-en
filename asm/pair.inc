; pair.inc: the pair-glyph hook body shared by asm/font.asm (PSX.EXE) and asm/epilog.asm (EPILOG.EXE).
; Both renderers take a1 = font cell code (row = code >> 4, column = code & 15, 12x12 cells), a0 = 1bpp image with
; 24-byte rows. Codes 0x2020-0xFEFF are two English letters (low byte left, high byte right): their 6x12 glyphs are
; ORed into cell 0 of `pair_scratch` and the renderer runs on that instead (a0 = pair_scratch, a1 = 0). Codes below
; 0x2000 fall through unchanged. The includer defines `pair_orig` (the displaced instructions + jump back) right
; after this body, and includes pair_data.inc (font + scratch) somewhere it can.

pair_hook:
    andi    t0, a1, 0xFFFF
    sltiu   t1, t0, 0x2000
    bnez    t1, pair_orig
    nop
    li      t2, pair_scratch
    andi    t3, t0, 0xFF           ; left letter
    srl     t4, t0, 8              ; right letter
    addiu   t3, t3, -0x20
    addiu   t4, t4, -0x20
    sll     t5, t3, 1              ; *12 = *8 + *4
    addu    t3, t5, t3
    sll     t3, t3, 2
    sll     t5, t4, 1
    addu    t4, t5, t4
    sll     t4, t4, 2
    li      t5, pair_font
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
    addiu   t2, t2, 24             ; next scratch row
    addiu   t6, t6, -1
    bnez    t6, @@row
    addiu   t4, t4, 1
    li      a0, pair_scratch
    move    a1, zero
