; name.inc: English name entry (included by asm/font.asm; docs/re/text.md §Name entry).
;
; The new-game name entry (PSX.EXE 0x80104A00-0x80106B40) has three grid pages built from one table at 0x800275A4
; (7 rows x 16 halfword cells per page: page 2 = Latin at 0x800275A4, page 0 = katakana 0x80027684, page 1 = hiragana
; 0x80027764; 0xFFFF = no cell; row 6 = the page/END buttons). Picking a cell appends its code to a name buffer
; (count 0x8002752C, page 0x8002752E) and a sprite (u, v of the cell's glyph in the VRAM page image) to a parallel
; array; the on-screen name is those sprites, 16 px apart. On END + YES 0x801054D4 copies the codes to the save's
; name (0x8001F5F6, 8 halfwords, cleared to 0xFFFF first).
;
; English: the Latin page holds single-letter pair codes ("A " = 0x2041), so a cell draws one 6-px letter; it is the
; page shown first, with the default name Raviel; a name holds 10 cells (buffers moved here), drawn 8 px apart; on
; commit, runs of single letters are packed two per halfword (what the text printer expects, docs/re/text.md
; §English) and the stored name is capped at 5 halfwords (10 letters, the week-screen tag, docs/windows.tsv).

NAME_MAX   equ 10
NAME_SAVE  equ 0x8001F5F6         ; the save's name field (0x8001F5E4 + 0x12)

; Latin page: pair codes, one letter in the left half of each cell
.org 0x800275A4
    .ascii "A B C D E F G H a b c d e f g h "
    .ascii "I J K L M N O P i j k l m n o p "
    .ascii "Q R S T U V W X q r s t u v w x "
    .ascii "Y Z "
    .halfword 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF
    .ascii "y z "
    .halfword 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF
    .ascii "1 2 3 4 5 6 7 8 "
    .halfword 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF
    .ascii "9 0 "
    .halfword 0xFFFF
    .ascii "! ? - . ' "
    .halfword 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF

; append: room for NAME_MAX cells; buffers moved
.org 0x80104C98
    sltiu   v0, v0, NAME_MAX
.org 0x80104CA0
    lui     a3, hi(name_buf)
    addiu   a3, a3, lo(name_buf)
.org 0x80104CF0
    lui     v0, hi(name_spr)
    addiu   v0, v0, lo(name_spr)
; backspace
.org 0x80104D5C
    lui     v1, hi(name_buf)
.org 0x80104D6C
    addiu   v1, v1, lo(name_buf)
.org 0x80104D7C
    lui     v0, hi(name_spr)
    addiu   v0, v0, lo(name_spr)
; init 0x80104E24 (runs when the grid opens; cursor on END): default name from name_default, its sprites looked up
; on the Latin page, Latin page first, count 6
.org 0x80104EC4
    lui     v0, hi(name_buf)
    addiu   t1, v0, lo(name_buf)
    lui     v0, hi(name_default)
    addiu   t4, v0, lo(name_default)
    lui     v0, 0x8002
    addiu   t2, v0, 0x75A4
    lui     v0, hi(name_spr)
    addiu   t3, v0, lo(name_spr)
    addiu   v0, zero, 2            ; page 2 = Latin
    lui     at, 0x8002
    sh      v0, 0x752E(at)
    addiu   v0, zero, 6            ; count = len("Raviel"); at is still 0x8002
    sh      v0, 0x752C(at)
; grid open (0x800C0F58, after the init): drew the katakana page (0x80105844) and set page 0; now the Latin page
.org 0x800C0F58
    jal     name_latin
.org 0x800C0F68
    nop                            ; was: sh zero, page
; commit: pack and copy (replaces the copy loop 0x801054D4-0x80105510)
.org 0x801054D4
    jal     name_pack
    nop
    j       0x80105514
    nop
; name sprites: NAME_MAX of them, 8 px apart
.org 0x801069B0
    lui     v0, hi(name_spr)
.org 0x801069B8
    addiu   s0, v0, lo(name_spr)
.org 0x80106A28
    lui     v0, 8
.org 0x80106A34
    slti    v0, s1, NAME_MAX
; underline marks under the name: NAME_MAX, 8 px apart and 8 px wide
.org 0x80106A7C
    addiu   s3, zero, 8
.org 0x80106AB0
    addiu   v0, zero, NAME_MAX + 1   ; original "count == 6" case (never reached with 5 cells): keep it unreachable
.org 0x80106B1C
    lui     v0, 8
.org 0x80106B28
    slti    v0, s0, NAME_MAX

.org NAME_FREE
; name_pack: name_buf[0..count) -> NAME_SAVE, single-letter pair codes ("X " = 0x20XX) packed two per halfword
; (an odd last letter keeps its space), other codes (kana) copied; at most 5 halfwords written. Leaf, t-registers.
name_pack:
    lui     t0, hi(name_buf)
    addiu   t0, t0, lo(name_buf)
    lui     t1, 0x8002
    lhu     t1, 0x752C(t1)         ; cells left
    lui     t2, hi(NAME_SAVE)
    addiu   t2, t2, lo(NAME_SAVE)
    move    t3, zero               ; pending letter (0 = none)
    addiu   t4, zero, 5            ; halfwords left to write
@@loop:
    beqz    t1, @@flush
    nop
    lhu     t5, 0(t0)
    addiu   t0, t0, 2
    addiu   t1, t1, -1
    srl     t6, t5, 8
    addiu   t7, zero, 0x20
    bne     t6, t7, @@other
    nop
    bnez    t3, @@merge
    nop
    b       @@loop
    andi    t3, t5, 0xFF
@@merge:
    andi    t5, t5, 0xFF
    sll     t5, t5, 8
    or      t5, t5, t3             ; pending letter left, this one right
    b       @@emit
    move    t3, zero
@@other:
    beqz    t3, @@emit
    nop
    ori     t6, t3, 0x2000         ; flush the pending letter first
    move    t3, zero
    beqz    t4, @@done
    nop
    sh      t6, 0(t2)
    addiu   t2, t2, 2
    addiu   t4, t4, -1
@@emit:
    beqz    t4, @@done
    nop
    sh      t5, 0(t2)
    addiu   t2, t2, 2
    b       @@loop
    addiu   t4, t4, -1
@@flush:
    beqz    t3, @@done
    nop
    ori     t5, t3, 0x2000
    b       @@emit
    move    t3, zero
@@done:
    jr      ra
    nop

; name_latin: draw the Latin page (0x8010567C, what the 英字 button calls) and make it the current page.
; Keep an instruction between `lw ra` and `jr ra`: the R3000A has no load interlock, so a `jr ra` right after the
; load jumps to the old ra (back into this function), runs the epilogue twice and leaves sp 8 bytes off. That crashed
; the game at name entry on DuckStation and real hardware; PCSX-Redux hid it (tools/asmlint.py checks for it).
name_latin:
    addiu   sp, sp, -8
    sw      ra, 4(sp)
    jal     0x8010567C
    nop
    lw      ra, 4(sp)
    addiu   v0, zero, 2
    lui     at, 0x8002
    sh      v0, 0x752E(at)
    jr      ra
    addiu   sp, sp, 8

name_default:                    ; glossary: the default angel name ラビエル = Raviel
    .ascii "R a v i e l "
    .halfword 0xFFFF
.align 4
name_buf:
    .fill (NAME_MAX + 2) * 2, 0
name_spr:
    .fill (NAME_MAX + 2) * 4, 0
name_end:
