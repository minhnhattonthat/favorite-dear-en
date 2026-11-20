; epilog.asm: English pair glyphs in TITLE/EPILOG.EXE (the endings). armips, run by tools/insert.py:
;   armips asm/epilog.asm -strequ EXE_IN <EPILOG.EXE> -strequ EXE_OUT <out> -strequ FONT_BIN <en6x12.bin>
;
; EPILOG's glyph renderer 0x800526E8 has PSX.EXE's interface (asm/font.asm) but no free space inside its image
; (docs/re/space.md §EPILOG). The file grows by one sector: a stub at the old image end (0x8009F800, the new pc0)
; copies the hook blob to BLOB, flushes the I-cache and jumps to the original entry 0x80013BD0. 0x80099180+ is
; overwritten once main runs, so the blob can't stay where it loads.

.psx
.open EXE_IN, EXE_OUT, 0x8000F800

GLYPH     equ 0x800526E8
ENTRY     equ 0x80013BD0
BLOB      equ 0x80170000          ; untouched in all 23 endings (trap.lua, docs/re/space.md §EPILOG)
STUB      equ 0x8009F800          ; old image end = file offset 0x90000
BLOB_FILE equ 0x90100             ; file offset of the blob (the stub is < 0x100 bytes)

.org 0x8000F810
    .word   STUB                   ; pc0
.org 0x8000F81C
    .word   0x90000                ; t_size: 0x8F800 + one sector

.org GLYPH
    j       pair_hook
    nop                            ; replaced: addiu sp,-0x40 / sw ra,0x3c(sp) (redone in the hook)

.org STUB
copy_stub:                         ; (armips names are case-insensitive: not `stub`)
    li      t0, STUB + (BLOB_FILE - 0x90000)
    li      t1, BLOB
    li      t2, (blob_end - BLOB + 3) / 4
@@copy:
    lw      t3, 0(t0)
    addiu   t0, t0, 4
    addiu   t2, t2, -1
    sw      t3, 0(t1)
    bnez    t2, @@copy
    addiu   t1, t1, 4
    la      t0, stub_ra
    sw      ra, 0(t0)
    li      t2, 0xA0               ; BIOS A(44h) FlushCache
    jalr    t2
    li      t1, 0x44
    la      t0, stub_ra
    lw      ra, 0(t0)
    j       ENTRY
    nop
stub_ra:
    .word   0
stub_end:
.if stub_end > STUB + (BLOB_FILE - 0x90000)
    .error "stub overlaps the blob"
.endif

.headersize BLOB - BLOB_FILE
.org BLOB
.include "pair.inc"
pair_orig:
    addiu   sp, sp, -0x40
    j       GLYPH + 8
    sw      ra, 0x3c(sp)
.include "pair_data.inc"
blob_end:
.if blob_end - BLOB > 0x700
    .error "hook blob overflows its sector"
.endif

.orga 0x907FF                      ; pad the file to 0x90800
    .byte   0

.close
