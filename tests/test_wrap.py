import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import batches  # noqa: E402
import wrap  # noqa: E402


def test_space_before_name_kept():
    # an odd run before {name} keeps its space ("My name isRaviel" in phase 8); before {n} it still goes
    assert wrap._fix_odd(["My name is ", "{name:0080}"]) == ["My name is ", "{name:0080}"]
    assert wrap._fix_odd(["Hello there ", "{n}"]) == ["Hello there ", "{n}"]  # even: untouched
    assert wrap._fix_odd(["Hi there ", "{wait}"]) == ["Hi there", "{wait}"]


def test_no_one_word_last_line():
    lines = wrap.wrap_line(["Together we overcame many hardships, and I was able to watch them grow."])
    texts = ["".join(ln) for ln in lines]
    assert len(texts) == 2 and " " in texts[-1], texts
    assert all(wrap.cells(ln) <= wrap.CELLS for ln in lines)


def test_page_break_at_clause_not_mid_sentence():
    # phase 8: greedy continuation left "shows up." alone on the next page; split at the last ', '/'. ' that fits
    en = ("{e0:E0FF}{spk:E783}{fa:0080}{n}{f7:0080}Bandit:{n}{f7:0380}{n}Tch... I finally get a fine batch of goods"
          " together, and some meddler shows up.{n}{wait}{clear}{end}")
    out = wrap.wrap(en)
    assert "together,{n}{wait}{clear}{spk:E783}{n}and some meddler shows up." in out, out
    for cells, _ in wrap.lines_report(out):
        assert cells <= wrap.CELLS


def test_page_break_moves_whole_sentence_when_no_clause_fits():
    en = ("{spk:0001}{n}Alpha beta.{n}Gamma delta.{n}Whose story would you like to hear today, my dear friend"
          " Angel?{n}{wait}{clear}{end}")
    out = wrap.wrap(en)
    assert "delta.{n}{wait}{clear}{spk:0001}{n}Whose story would you like to hear{n}today, my" in out, out


def test_simplify_drops_only_soft_breaks():
    jp = "{e0:1600}{spk:0080}{n}よく来ましたね。{n}何か？{n}{wait}{clear}{end}"
    assert wrap.simplify(jp) == "{e0:1600}{spk:0080}{n}よく来ましたね。何か？{n}{wait}{clear}{end}"


def test_wrap_fits_and_continues_with_speaker():
    en = "{e0:0001}{spk:0002}{n}" + " ".join(["word"] * 40) + "{n}{wait}{clear}{end}"
    out = wrap.wrap(en)
    for cells, _ in wrap.lines_report(out):
        assert cells <= wrap.CELLS
    assert "{n}{wait}{clear}{spk:0002}{n}word" in out
    assert wrap.codes(out) != wrap.codes(en)  # a continuation page was added
    assert out.endswith("{n}{wait}{clear}{end}")


def test_odd_run_before_code_drops_its_space():
    out = wrap.wrap("Hi, {name:0080}!{n}{wait}{clear}{end}")
    assert out.startswith("Hi, {name:0080}!")  # 'Hi, ' is 4 letters: kept as is
    out = wrap.wrap("Hey, {name:0080}!{n}{wait}{clear}{end}")
    # 'Hey, ' is odd, but dropping its space would leave 'Hey,' (even, no pad cell): "Hey,Raviel" on screen.
    # Before a name the space stays and the encoder pads it to a full cell.
    assert out.startswith("Hey, {name:0080}!")


def test_family_args_put_back():
    rep_jp, jp = "{fb:0080}{n}あ{n}{wait}{clear}{end}", "{fb:0180}{n}あ{n}{wait}{clear}{end}"
    assert batches.with_args("{fb:0080}{n}Ah{n}{wait}{clear}{end}", rep_jp, jp).startswith("{fb:0180}")


def test_check_catches_code_mismatch_and_glyphs():
    errs = batches.check_row("x", "{spk:0080}{n}あ{n}{wait}{clear}{end}", "{n}Ah{n}{wait}{clear}{end}", [])
    assert any("codes differ" in e for e in errs)
    errs = batches.check_row("x", "あ{n}{wait}{clear}{end}", "Ahあ{n}{wait}{clear}{end}", [])
    assert any("not in the font" in e for e in errs)
    assert batches.check_row("x", "あ{n}{wait}{clear}{end}", "-", []) == []


def test_no_stray_page_fragments_or_odd_runs_in_the_script():
    # phase 8 lints over the real script: a continuation page opening on "shows up." and an odd run before a name
    # ("My name is  Raviel") both read badly in game
    import subprocess
    import pagesplit
    root = Path(__file__).resolve().parent.parent
    assert pagesplit.fragments() == []
    r = subprocess.run([sys.executable, "-X", "utf8", str(root / "tools" / "oddname.py")], capture_output=True,
                       text=True, encoding="utf-8", cwd=root)
    assert r.returncode == 0 and r.stdout.strip() == "", r.stdout


@pytest.mark.skipif(not (Path(__file__).resolve().parent.parent / "work/disc/tree/PSX.EXE").is_file(),
                    reason="disc not unpacked to work/disc/tree")
def test_hero_visit_choices_fit_the_menu():
    # issue #4: the visit topic menu shows each option's first page on one 19-cell line ("...I'll hel" cut, a
    # two-line option pushed the next one under the wrong cursor slot)
    import menuopts
    assert len(menuopts.option_ids()) > 2000
    assert menuopts.overflows() == []


def test_choice_glyphs_become_escapes():
    assert batches.to_printer("　｛Go｝") == "[00][00][DA][05]Go[DB][05]"
