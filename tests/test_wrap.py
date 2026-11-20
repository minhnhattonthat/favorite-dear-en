import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import batches  # noqa: E402
import wrap  # noqa: E402


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
    assert out.startswith("Hey,{name:0080}!")  # 'Hey, ' is odd: the encoder's pad space stands in


def test_family_args_put_back():
    rep_jp, jp = "{fb:0080}{n}あ{n}{wait}{clear}{end}", "{fb:0180}{n}あ{n}{wait}{clear}{end}"
    assert batches.with_args("{fb:0080}{n}Ah{n}{wait}{clear}{end}", rep_jp, jp).startswith("{fb:0180}")


def test_check_catches_code_mismatch_and_glyphs():
    errs = batches.check_row("x", "{spk:0080}{n}あ{n}{wait}{clear}{end}", "{n}Ah{n}{wait}{clear}{end}", [])
    assert any("codes differ" in e for e in errs)
    errs = batches.check_row("x", "あ{n}{wait}{clear}{end}", "Ahあ{n}{wait}{clear}{end}", [])
    assert any("not in the font" in e for e in errs)
    assert batches.check_row("x", "あ{n}{wait}{clear}{end}", "-", []) == []


def test_choice_glyphs_become_escapes():
    assert batches.to_printer("　｛Go｝") == "[00][00][DA][05]Go[DB][05]"
