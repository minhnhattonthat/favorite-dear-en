# Glossary - Favorite Dear

Binding for every translator and reviewer. Translators propose additions in reports; only the controller edits this
file. `tools/batches.py check` enforces the tables: a row whose JP holds a term (whole katakana run) must contain the
EN form (first word group before " ("), and never a spelling from the Avoid column.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Ernest-san). Name order: Western (given name first).
- Romanisation source: no official English exists (D10): Western-style spellings of the katakana names, demon and
  angel names in their standard English forms (Apollyon, Gabriel, Belphegor).
- Credits: English.
- Register: warm fantasy drama, natural modern English, no archaisms except for the higher angels (formal, measured).
  Sound effects and interjections: English equivalents (うふふ "Hehe", ククク "Heh heh heh", えっ "Huh?").
- Abbreviations: full names and terms everywhere, prefer engine changes over shortening.

## Style rules
- Punctuation: 「」 -> "...", 『』 -> '...', ・・・ / ・・・・・・ -> "..." (one ellipsis, never more than "......"),
  ！？ -> "?!", （...） inner monologue -> (...). Plain ASCII plus … — ♥ ♪ é only.
- Choice lines keep the full-width layout: `　｛Go to them　｝` (full-width space, ｛ ｝, the option inside; pad both
  options of one choice to the same width with full-width spaces after the text).
- The player is the angel `{name:0080}`: keep every line about the angel gender-neutral (no he/she).
  天使様 -> "Angel" (capitalised as an address), voiced by the speaker ("Hey, Angel!").
- Common terms (not lint-enforced): 天使 angel; 勇者 hero (the angel's chosen champion); 妖精 fairy; 堕天使 fallen
  angel; 天界 the Heavens; 地上 the surface / the world below; 魔物/怪物/モンスター monster; 災い calamity;
  魂 soul; 相性 compatibility (between heroes); 経験 experience; ボーナスＡＰ Bonus AP; 行方不明 missing.
- Voices: docs/style-reference.md.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| レイヴ | Reiv | | hero, Reiv Vincelras, knight of the Voras order | Rave |
| ヴィンセルラス | Vincelras | | Reiv's family name | |
| シーヴァス | Sievas | | hero, Sievas Volkgang | |
| フォルクガング | Volkgang | | | |
| アーシェ | Ashe | | hero, Ashe Bradarik | |
| ブレイダリク | Bradarik | | | |
| ティア | Tia | | hero, Tia Tangeri | |
| ターンゲリ | Tangeri | | | |
| ビーシア | Beasia | | hero, Beasia Gray | |
| フィアナ | Fiana | | hero, Fiana Ecliya | |
| エクリーヤ | Ecliya | | | |
| ヤルル | Yaruru | | hero, Yaruru Willing | |
| ルドック | Ludock | | Ludock Willing | |
| ウィリング | Willing | | family name | |
| リュドラル | Ryudral | | hero, Ryudral Algrane; human raised among monsters, friend of the dragon chief Aul | |
| アルグレーン | Algrane | | | |
| フェリミ | Felimi | | hero, Felimi MacDill | |
| マクディル | MacDill | | | |
| ディアン | Dian | | hero, Dian Alvis | |
| アルヴィース | Alvis | | | |
| ナーサディア | Nasadia | | | |
| グリフィン | Griffin | | | |
| ラスエル | Rasuel | | | |
| エレン | Ellen | | | |
| ミリアス | Milias | | | |
| アウル | Aul | | chief of the dragon clan (竜族の長) | Owl |
| シルフェ | Sylphe | | fairy | |
| シェリー | Shelly | | fairy | |
| フロリンダ | Florinda | | fairy | |
| フロリン | Florin | | Florinda's name for herself | |
| ミライヤ | Miraya | | | |
| ガブリエル | Gabriel | | archangel | |
| ミカエル | Michael | | archangel; lends the angel his golden sword (黄金の剣) against Apollyon | |
| レミエル | Remiel | | angel who keeps wandering souls | |
| リリィ | Lily | | | |
| アポルオン | Apollyon | | | |
| イウヴァート | Iuvart | | fallen angel | |
| アドラメレク | Adramelech | | | |
| ガープ | Gaap | | | |
| レライエ | Leraje | | | |
| ベルフェゴール | Belphegor | | | |
| ドラッケン | Drakken | | mountain bandit / monster preying on merchants in Hebron | |
| キメラ | Chimera | | monster in the Duminas marshes | |
| ケルピー | Kelpie | | water monster posing as a girl (Sievas event) | |
| マキュラ | Macula | | rogue dragon, マキュラドラゴン "Macula Dragon"; dealt with Iuvart | |
| ボルンガ | Borunga | | gentle Duminas monster (Ryudral event) | |
| トリシア | Tricia | | village chief's daughter below the Dragon's Den (Ryudral event) | |
| シエラ | Sierra | | witch serving Apollyon (Dian event) | |
| リーガル | Regal | | Reiv's old friend, the Knight in Black (黒衣の騎士) | |
| イダヴェル | Idavel | | (Griffin event) | |
| ビュシーク | Busik | | undead monster empowered by Apollyon | |
| バルバロッサ | Barbarossa | | bandit (Felimi event) | |
| ライザ | Liza | | Dian's lost love | |
| ジャックハウンド | Jackhound | | Rush's true name (sacred beast) | |
| ブロッケン | Brocken | | monster (Yaruru event) | |
| ゼビア | Zebia | | slaver bandit boss (Fiana event) | |
| バルト | Balt | | Apollyon's servant (Fiana event) | |
| ラッシュ | Rush | | Yaruru's sacred beast ("he") | |
| グレイ | Gray | | Beasia's family and her dojo ("the Gray-style dojo", グレイ流道場) | |
| ステレンス | Sterens | | usurper king of Fangam, empowered by Apollyon (Ashe event); "Lord Sterens" to his soldiers | |
| バーンズ | Barnes | | guardian beast of the fairy world, servant of Iuvart (Tia event); broken speech ("Me... beat you") | |
| ティタニア | Titania | | fairy queen ("Lady Titania") | |
| フェリス | Felice | | noblewoman Sievas jilts at a soiree (Sievas event) | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| インフォス | Infos | | the world the angel protects | |
| ヴォーラス | Voras | | Voras Knights (ヴォーラス騎士団) | |
| ラダール | Radal | | Lake Radal | |
| ヘブロン | Hebron | | Kingdom of Hebron (ヘブロン王国); capital Voras | |
| ヨースト | Joost | | town in Hebron (Sievas) | |
| キンバルト | Kimbalt | | Kingdom of Kimbalt | |
| ニーセン | Niesen | | town in Kimbalt (Griffin) | |
| カノーア | Kanoa | | the Kanoa Nation (カノーア国) | |
| フェデコ | Fedeco | | town in Kanoa (Felimi) | |
| エスパルダ | Esparda | | the Esparda Empire (エスパルダ皇国) | |
| ブルン | Brun | | town in Esparda (Dian) | |
| クヴァール | Kvaal | | region/nation (Yaruru, Fiana, Tia) | |
| ガルフ | Garf | | town in Kvaal (Yaruru) | |
| デュミナス | Duminas | | the Duminas Empire (デュミナス帝国) | |
| ラルース | Larousse | | town in Duminas (Ryudral) | |
| タンブール | Tambour | | town in Kvaal (Fiana) | |
| ファンガム | Fangam | | Kingdom of Fangam (Ashe's home) | |
| グルーチ | Gruche | | capital of Fangam | |
| ノバ | Nova | | town in Kimbalt (Beasia) | |
| トラスト | Trust | | town in Kanoa (Nasadia) | |
| オムロン | Omron | | village in Kvaal (Tia) | |
| コパ | Copa | | village in Fangam (slime thefts) | |
| サルファ | Sulfa | | region near Hebron where a rebellion breaks out (Reiv mission) | |
| トリニテ | Trinite | | town linked to Niesen by a highway (Griffin mission) | |
| ティアズ | Tiaz | | town where "that kid" lives (Griffin mission) | |
| ソルダム | Soldam | | village attacked by bandits (Dian mission) | |
| オフランド | Offland | | the Offland Mountains, spring for the epidemic cure (Dian) | |
| レーゼル | Resel | | Mount Resel near Garf, the riddle Fiend (Yaruru) | |
| アルプ | Alp | | place in Kimbalt with frequent monsters (Yaruru mission) | |
| アーテム | Artem | | town in Kvaal attacked by Leraje (Yaruru mission) | |
| ボルサ | Borsa | | the Borsa Forest, home of winged monsters (Nasadia mission) | |
| バルバ | Barba | | Barba Island (バルバ島), where Reiv is held captive | |
| シュランク | Schrank | | the Schrank Forest, where Yaruru met Rush | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 時の淀み | Stagnation of Time | | the calamity eroding Infos ("the Stagnation of Time") | |
| 神獣 | sacred beast | | Yaruru's companion | |
| 竜の使い | the Dragon's Messenger | | Ryudral's local title | |
| アストラル界 | the Astral Plane | | the inner world of a heart, where an angel can be attacked directly | |
| 竜の洞 | the Dragon's Den | | Aul's cave; only dragonkind may enter | |
| 闇馬車 | Dark Carriage | | slaver bandit ring, in quotes ("Dark Carriage") | |
| ダルク | Dalk | | currency ("1000 Dalk", Fiana's fee) | |
| 炎王 | Flame King | | Adramelech's title | |
| ガロンドランク | Gallon Drunk | | tavern where a dancer works (Griffin's mix-up) | |
| ベイオウルフ | Beowulf | | Griffin's band of noble thieves (義賊) | |
| 英霊祭 | Festival of Heroic Spirits | | Hebron festival with a soiree (Reiv event) | |

## Decisions from earlier batches
- b001 3498.1550 (the gift-name list, one run of names indexed by the script): kept Japanese (`-`), phase 7 must
  find how the names are cut before it can be translated.
- b009-b013 files 34F2 34F5 34F8 34FC 3500 3504 3507 350A (about 300 rows, all of each file): codes parse but the
  text decodes as kana/kanji soup under the main table (a substitution, not a constant shift: most frequent code
  0x000E sits where 。 belongs; likely a per-scene glyph set), so `-`. Same pattern in parts of 393D, 3976-3986
  (b099, b103-b105). Phase 7: find the glyph table these files use, re-extract, re-batch, translate.
- 様 after a hero's name (fairies, maids) is dropped: "I found {name:0180}!", "leave it to Sievas"; the politeness
  goes into the phrasing. 天使様 stays "Angel".
- b020 3576.06BE-0834 (6 rows): glyph soup like 34F2 etc., `-`; phase 7 re-extract.
- b046 36FB (47 rows) and 36FD (10 rows, continues in b047): short `{fb:..}` rows of soup ending in a repeated
  `高決｡》｡`/`･》･` pattern (looks like a mission-result table under another glyph set), `-`; phase 7 re-extract.
- Gendered addresses for the angel are neutralised: Yaruru's お姉ちゃん -> "you" (358B.2332), Griffin's
  ド派手姉ちゃん -> "Flashy", 娘/女 -> "that one"/"You sure can talk"; Dian's 天使さん -> "Angel".
- 姉さん (Felimi to Miraya, his elder sister; 356C, 3570, 35F0, 35F4): "Sister" / "my sister".
- Angel-gender variant files (e.g. 35BC = female-angel copy of 358B): where the line is about the angel's gender
  (Yaruru: お姉ちゃんでいいですよ), keep it ("Big Sis"); elsewhere stay neutral.
- Stock battle lines: 魔人 "Fiend", 魔族 "Demon", `{name:0180}はXを倒した` "{name:0180} defeated X.",
  `退けた` "drove off X."; 天使の手先 "the angel's lackey"; 天使の勇者 "the angel's hero".
