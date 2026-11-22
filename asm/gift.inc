; gift.inc: hero visit -> GIFT, the item stat window and the "Give it?" prompt (GitHub issue #1).
;
; 0x800C24DC renders three pool strings (u16 table 0x8002DBEC entries 4-6, string = 0x80175B34 + 2*entry, i.e.
; script/exe.tsv PSX.166398 and PSX.1663C4) into VRAM at (0x3C0 halfwords, 0x100 + 12*row) with 0x800FD8C4.
; 0x800C27F0 (stat window) and the prompt then draw pieces of that strip with 0x801186E4(0, x, y, index, ..),
; where index picks a descriptor through the pointer table 0x8002DB84 (+4 u, +8 v, +0x14 w, +0x18 h, 4bpp px).
; Japanese layout, 12 px per glyph cell:
;   0 贈りますか？ (prompt)  1 装備  2 不可  3 可  4 攻撃力  5 防御力  6 素早さ          (row v=0)
;   8 正義感  9 ストレス  7 体　力  10 アイテム  11 中です。                          (row v=12)
; Header: equippable item: 1 at x 0xDA, then 2 (can't) at 0xF2 or 3 (can) at 0xFE; already equipped: 1 at 0xD4
; and 11 at 0xEC; consumable: 10 at 0xDA. Labels 4-6 / 7-9 at x 0xBB, numbers from 0xF5.
;
; English letters are 6 px (two per pair cell), so the rows are packed with no padding and each descriptor's u and
; w point at its word (6 * letter index). Piece 2 / 11 start 24 px into piece 1 ("Equip:"), so they begin with the
; same "p:" and overdraw it pixel for pixel; piece 3 starts 36 px in:
;   row 0  "Give this?Equip:p: No OKAttackGuardSpeed  "  -> Equip: No / Equip: OK
;   row 1  "JusticeStressStaminaItemsp: Using         "  -> Equip: Using (the hero already has it on)

.macro gift_piece, desc, u, w
    .org desc + 4
    .word u
    .org desc + 0x14
    .word w
.endmacro

    gift_piece 0x8002DA34,   0, 60     ; 0  Give this?
    gift_piece 0x8002DA50,  60, 36     ; 1  Equip:
    gift_piece 0x8002DA6C,  96, 30     ; 2  p: No   (drawn 24 px into piece 1)
    gift_piece 0x8002DA88, 126, 18     ; 3   OK    (drawn 36 px into piece 1)
    gift_piece 0x8002DAA4, 144, 36     ; 4  Attack
    gift_piece 0x8002DAC0, 180, 30     ; 5  Guard
    gift_piece 0x8002DADC, 210, 30     ; 6  Speed
    gift_piece 0x8002DAF8,   0, 42     ; 8  Justice (row 1)
    gift_piece 0x8002DB14,  42, 36     ; 9  Stress
    gift_piece 0x8002DB30,  78, 42     ; 7  Stamina
    gift_piece 0x8002DB4C, 120, 30     ; 10 Items
    gift_piece 0x8002DB68, 150, 48     ; 11 p: Using (drawn 24 px into piece 1)
