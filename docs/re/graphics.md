# Graphics text survey (phase 1)

How: every GDATA.BIN directory entry (PSX.EXE 0x4C50, 423 entries) decoded as TIM (`tools/tim.py dump work/gfx/gdata`,
187 TIMs) or as an LZSS raw image (108: 12-byte header `u32 ?, u32 0, u16 w_halfwords, u16 h`, read as 4bpp when
w = 64 halfwords, else 8bpp; palettes live elsewhere, so sheets were grey), plus every *.PSS / *.TIM on the disc root,
TITLE/ and DATA/. The other EXEs embed no TIMs. Sheets: work/gfx/{small_a,small_b,big_0..2,lz_0..3,other}.png
(regenerate with the commands above; work/ is gitignored).
Phase 8 addition: GDATA also holds ~800 TIMs outside that directory (event pictures, portraits and their eye/mouth
parts), found by a sector scan: `python -X utf8 tools/timscan.py` (work/gfx/scan/, one PNG per TIM, named by
sector). All 342 640x240 pictures, the 320x240 one, the 92 480x240 portraits and the 365 small ones (eye/mouth parts) were
looked at (2026-11-21): only the three tutorial charts and the GAME OVER pictures carry Japanese.

Japanese drawn as graphics (each row must be English in a zoomed cold-boot shot by phase 8, D5):

| Source | Kind | Japanese in it | Where seen |
|---|---|---|---|
| GDATA e008 | LZSS 4bpp 256 px | command buttons 予定 訪問 能力 地図 スカウト システム 戻る 任務 会話 贈る | angel/hero menus. **English** (phase 8, gfx/e008.tsv: PLAN VISIT STATUS MAP SCOUT SYSTEM BACK MISSION TALK GIFT, upper case so no descender meets the border; the calendar's 4月22 is now 4/22; `warp.py hub`) |
| GDATA e009 (not seen on any screen yet; the status screens draw e012-e014) | LZSS 4bpp 256 px | labels 信頼度 正義感 ストレス 攻撃力 防御力 体力 信仰心 知力 勇者 天使 妖精 行方不明 家出中 (English Name/Birth/Level/Class/Sex/Hobby/WEAPON/ARMOR/SPECIAL/EQUIP/PLEASANT already) | status screens |
| GDATA e012-e014 | TIM 8bpp 320x240 (raw, one copy on the disc) | status-screen backgrounds: e012 fairy, e013 angel, e014 hero; labels in one ink index (43/203/154) on a textured panel | **English** (phase 8, gfx/e012-e014.tsv, ink erased by row inpainting, `warp.py hub_ability2/3`). Status-screen values: 男/女 is PSX.EXE 0x80183FA4, one cell on screen ("M"/"F") |
| GDATA e015, e016 | LZSS 4bpp 256 px | name entry: カタカナ ひらがな 英字 END YES NO (months/zodiac English) | new game name entry. **English** (phase 8, gfx/e015.tsv: Katakana Hiragana ABC, erase `>=10` on the textured buttons; `warp.py newgame_grid`, `work/qa/warp/newgame_grid/post.png`). e016 holds no Japanese. The grid itself is PSX.EXE: `asm/name.inc` |
| GDATA e142 | TIM 4bpp | fairy panel: ストレス 発見 索敵 移動中 待機中 行方不明 | week screen (seen f10000 of ng2). **English** (phase 8, gfx/e142.tsv: Stress (narrow 3x7 font, the label sprite is 24 px), Hero, Foe, Moving, Standby, Missing, Dead; `warp.py week1` shows the first three; the four status plates checked as an image only) |
| GDATA e143 | TIM 8bpp | status icons 失 死 (and "Data.1-6") | map/battle sprites. **English** (phase 8, gfx/e143.tsv: MIA / KIA in the narrow font, D16; checked as an image, `gfx.py png 143`: no warp shows a lost or dead hero yet) |
| GDATA e144 | TIM 4bpp | patterned background with the logo and フェイバリット・ディア kana | load screen? |
| GDATA e145 | TIM 4bpp | save/load: この「Data」はこわれています 新規作成 容量がたりません 「Data」がありません | memory-card screens. **English** (phase 8, gfx/e145.tsv, D16; in game: `warp.py load_list` "No Data", `hub_save_list` "New Data") |
| GDATA e203 | TIM 8bpp 320x240 | game-flow chart (the tutorial's "全体のながれ") | tutorial option at the start (the choice "1. Start now. 2. See the overall flow." is PSX.EXE 0x80166390, pointed to from 0x80169798; not reached by any warp yet). **English** (phase 8, gfx/e203.tsv: outlined label font (`oN` shadow), the 予定命令/説得/依頼 boxes widened with `copy` rows, big 勇者 erased with a texture offset; checked as an image, `gfx.py png 203`) |
| GDATA sectors 40127, 40203, 40279 (outside the directory; `tools/timscan.py`) | TIM 8bpp 640x240 hi-res | tutorial charts ゲームの流れ 其の一/二/三 (white serif lettering, teal titles, over paintings) | SETUMEI event (`warp.py ev_setumei`, f13650-f13950). **English** (phase 8, gfx/s40127.tsv s40203.tsv s40279.tsv: `label2` font (double width), `lum:` erase; in game `work/qa/warp/ev_setumei/f013800.png`) |
| GDATA sectors 15228, 41039, 41115 (outside the directory) | TIM 8bpp 320x240 / 640x240 | GAME OVER logo with a ゲーム・オーバー kana reading | game over: no game-over screen is reachable (`debug.md` §Programs, Battles), left as is |
| GDATA e243 | LZSS 4bpp | battle status ポイズン チャーム スリープ コンフュ パライズ (e225 has English Poison/Charm/...) | battles. **English** (phase 8, gfx/e243.tsv: POISON CHARM SLEEP CONFUSE PARALYZE, narrow font, D16; checked as an image only: no warp inflicts a status yet) |
| GDATA e204-e206 (bt_font1-3.pss) | LZSS 4bpp 256x16 x3 | 8x8 battle font: A-Z 0-9 katakana hiragana, no kanji | battle name plates (unit names) and the HUD's digits. **English** (phase 8, §Battle name plates below: the names are now drawn by `asm/btname.inc` in caps4x7, D17; the font images stay, the HUD still uses their digits and Latin; in game `warp.py battle_t0101` f015150 BANDIT / CHIEF, `battle_castle` f014700 WIGHT and the hero plate REIV) |
| PSX.EXE 0x1747B4 (RAM 0x80183FB4) | string `平和度{end}`, text-engine drawn (VRAM dump `v11150` on the map: next to the other map labels), outside extract.py's EXE_REGIONS | world-map coordinate box "X: Y: 平和度" | **English** (phase 8, asm/font.asm: pair cells "Peace", `warp.py hub_map` post.png "X: 41 Y: 23 Peace 150") |
| TITLE.PSS, TITLE/TTL_LOGO.PSS | LZSS 8bpp | フェイバリット・ディア kana under the English logo | title, load |
| TITLE/TTL_OPT.PSS | LZSS 4bpp 256x256 (same form as the GDATA LZSS images; no CLUT in the file) | memory-card notice メモリーカードの / チェック中です。/ 抜かないでください。 | title Option. **English** (phase 8, gfx/TTL_OPT.tsv: "Checking the / memory card. / Don't remove it."; checked as an image, `gfx.py png TTL_OPT`: `warp.py option_exit` (card in) and `option_omake` never show it) |
| TITLE/TTL_OPT2.PSS, TITLE/TTL_INFO.PSS | LZSS 4bpp 256x256 | Slime Ball instructions (方向キーで勇者を動かし、...) | Slime Ball. **English** (phase 8, gfx/TTL_INFO.tsv, TTL_OPT2.tsv; TTL_INFO's box in game: `warp.py minigame` f12450; TTL_OPT2's blue box (X button: speed up) checked as an image only) |

Already English: title menu (TTL_COM.PSS, OPM1.PSS), Now Loading (NOWLOAD.PSS/.TIM), options labels (TTL_OPT/OPT2
apart from the boxes), NEC Interchannel logos, "Fin." (EPI_OBJ.PSS), credits pictures DATA/01-13.TIM (no text).

Seen on screen, source not found yet (may be font-drawn, check in phase 5 by corrupting the font): fairy action menu
休暇 / 勇者の発見 (ex1 f000140), confirm box これでよろしいですか？ はい いいえ (ex2 f001000), name plates (シェリー),
the AP/LV panel on the angel column.

Movies: NEIC.STR / SOFIX1.STR are the company logos (English); OP.STR sampled every 150 frames of a cold boot
(work/qa/opmovie, f2550-f3300) showed no text, but it was cut short by the title. Not checked yet: the rest of
OP.STR, DEMO.STR, ENDING.STR (burned-in text, lyrics); graphics of
GOVER.EXE (game over; never shown in play, `debug.md` §Programs: OVER_*.TIM need no translation), FD_BALL.EXE (Slime Ball), EPILOG.EXE, PS_MOV.EXE, FIN.EXE beyond what they load from the disc
root; the 107 non-image GDATA entries (maps, 3D, battle data). Do these with the debug tool's warps (phase 2/8).

## Battle name plates (found 2026-11-21, phase 8)

- Each unit's plate (enemies top left, heroes bottom right) shows a 64x8 name label from VRAM. The battle init
  (0x80042180) LoadImages bt_font1-3.pss (GDATA e204-e206) to VRAM (320/384/448, 240); routine 0x80042448 (called
  from 0x80046098 and 0x8005D5C8) then MoveImaged 8 font cells per unit slot (6 slots, records of 0x78 bytes at
  0x80196A20, +0x16 > 0 = shown) to x 0x1E0 + (slot&1)*16 halfwords, y 0x40 + (slot>>1)*8.
- Names are 8 one-byte codes (0 = blank): heroes at the start of the record that 0x80146210[hero id] points to
  (19 entries; the record also names the hero's battle sprite file), enemies at 0x8013BFCC + type*8 (201 types,
  type = u16 at 0x80182B2C + (slot-3)*2). A code picks a 0x1C-byte descriptor through 0x80154CF4[code] (page,
  u, v, ..., w, h) at 0x801537F4 + code*0x1C; `tools/btname.py` decodes them (A-Z = 0x0B-0x24, 0-9 = 0x01-0x0A).
- The HUD (LV digits, HP; 0x8005AF20, 0x8005B208 -> 0x8003C8A8) reads only codes 0x00-0x24 and the pointer table:
  a read watch (`probes/watch.lua`, from `work/states/battle_t0101.sstate`, 1800 frames) saw no read of the
  descriptors 0x80153BE0-0x80154CF3 (codes 0x25-0xBF) while the same watch over the whole table logged the HUD.
- English (D17): `asm/btname.inc` replaces 0x80042448 in place with a renderer that draws the name from
  `trans/btname.tsv` (upper case, `fonts/caps4x7.txt`, <= 64 px, `btname.py check`) into a 4bpp buffer and
  LoadImages it (LoadImage 0x800EC6C0, then DrawSync 0x800EC414, since LoadImage keeps the pointer). Data: the
  font, hero names and the buffer over the old enemy table, the 16-byte enemy records over descriptors 0x25-0xBF.
