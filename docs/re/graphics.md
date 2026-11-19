# Graphics text survey (phase 1)

How: every GDATA.BIN directory entry (PSX.EXE 0x4C50, 423 entries) decoded as TIM (`tools/tim.py dump work/gfx/gdata`,
187 TIMs) or as an LZSS raw image (108: 12-byte header `u32 ?, u32 0, u16 w_halfwords, u16 h`, read as 4bpp when
w = 64 halfwords, else 8bpp; palettes live elsewhere, so sheets were grey), plus every *.PSS / *.TIM on the disc root,
TITLE/ and DATA/. The other EXEs embed no TIMs. Sheets: work/gfx/{small_a,small_b,big_0..2,lz_0..3,other}.png
(regenerate with the commands above; work/ is gitignored).

Japanese drawn as graphics (each row must be English in a zoomed cold-boot shot by phase 8, D5):

| Source | Kind | Japanese in it | Where seen |
|---|---|---|---|
| GDATA e008 | LZSS 4bpp 256 px | command buttons 予定 訪問 能力 地図 スカウト システム 戻る 任務 会話 贈る | angel/hero menus |
| GDATA e009 | LZSS 4bpp 256 px | labels 信頼度 正義感 ストレス 攻撃力 防御力 体力 信仰心 知力 勇者 天使 妖精 行方不明 家出中 (English Name/Birth/Level/Class/Sex/Hobby/WEAPON/ARMOR/SPECIAL/EQUIP/PLEASANT already) | status screens |
| GDATA e012-e014 | TIM 8bpp 320x240 | status-screen backgrounds with printed labels (体力 攻撃力 ... 信頼度 ... 経験値) | hero/fairy status |
| GDATA e015, e016 | LZSS 4bpp 256 px | name entry: カタカナ ひらがな 英字 END YES NO (months/zodiac English) | new game name entry |
| GDATA e142 | TIM 4bpp | fairy panel: ストレス 発見 索敵 移動中 待機中 行方不明 | week screen (seen f10000 of ng2) |
| GDATA e143 | TIM 8bpp | status icons 失 死 (and "Data.1-6") | map/battle sprites |
| GDATA e144 | TIM 4bpp | patterned background with the logo and フェイバリット・ディア kana | load screen? |
| GDATA e145 | TIM 4bpp | save/load: この「Data」はこわれています 新規作成 容量がたりません 「Data」がありません | memory-card screens |
| GDATA e203 | TIM 8bpp 320x240 | game-flow chart (the tutorial's "全体のながれ") | tutorial option at the start |
| GDATA e243 | LZSS 4bpp | battle status ポイズン チャーム スリープ コンフュ パライズ (e225 has English Poison/Charm/...) | battles |
| GDATA e204-e206 | LZSS 4bpp 256x16 x3 | a second, 8x8 font: A-Z 0-9 katakana hiragana (encoding not found yet) | small labels (battle/map?) |
| TITLE.PSS, TITLE/TTL_LOGO.PSS | LZSS 8bpp | フェイバリット・ディア kana under the English logo | title, load |
| TITLE/TTL_OPT.PSS | LZSS 8bpp | memory-card notice (メモリーカードのチェックをして...) | title Option |
| TITLE/TTL_OPT2.PSS, TITLE/TTL_INFO.PSS | LZSS 8bpp | Slime Ball minigame instructions (方向キーで勇者を動かし、...) | title Option > Slime Ball |

Already English: title menu (TTL_COM.PSS, OPM1.PSS), Now Loading (NOWLOAD.PSS/.TIM), options labels (TTL_OPT/OPT2
apart from the boxes), NEC Interchannel logos, "Fin." (EPI_OBJ.PSS), credits pictures DATA/01-13.TIM (no text).

Seen on screen, source not found yet (may be font-drawn, check in phase 5 by corrupting the font): fairy action menu
休暇 / 勇者の発見 (ex1 f000140), confirm box これでよろしいですか？ はい いいえ (ex2 f001000), name plates (シェリー),
the AP/LV panel on the angel column.

Movies: NEIC.STR / SOFIX1.STR are the company logos (English); OP.STR sampled every 150 frames of a cold boot
(work/qa/opmovie, f2550-f3300) showed no text, but it was cut short by the title. Not checked yet: the rest of
OP.STR, DEMO.STR, ENDING.STR (burned-in text, lyrics); graphics of
GOVER.EXE (game over), FD_BALL.EXE (Slime Ball), EPILOG.EXE, PS_MOV.EXE, FIN.EXE beyond what they load from the disc
root; the 107 non-image GDATA entries (maps, 3D, battle data). Do these with the debug tool's warps (phase 2/8).
