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
| ミライヤ | Miraya | | | |
| ガブリエル | Gabriel | | archangel | |
| レミエル | Remiel | | angel who keeps wandering souls | |
| リリィ | Lily | | | |
| アポルオン | Apollyon | | | |
| イウヴァート | Iuvart | | fallen angel | |
| アドラメレク | Adramelech | | | |
| ガープ | Gaap | | | |
| レライエ | Leraje | | | |
| ベルフェゴール | Belphegor | | | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| インフォス | Infos | | the world the angel protects | |
| ヴォーラス | Voras | | Voras Knights (ヴォーラス騎士団) | |
| ラダール | Radal | | Lake Radal | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 時の淀み | Stagnation of Time | | the calamity eroding Infos ("the Stagnation of Time") | |

## Decisions from earlier batches
- b001 3498.1550 (the gift-name list, one run of names indexed by the script): kept Japanese (`-`), phase 7 must
  find how the names are cut before it can be translated.
