"""pagesplit.py: continuation pages (added by wrap.py) that open on a mid-sentence fragment of 1-3 words.

    python -X utf8 tools/pagesplit.py          batch<TAB>id<TAB>fragment, one line each; exit 1 if any

A battle or event box that scrolls on to a page holding only "shows up." / "if you would." reads badly (phase 8
visual QA). wrap._page_cut picks the break; reword the row if one is listed here. tests/test_wrap.py runs this.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batches as B  # noqa: E402
import wrap as W  # noqa: E402


def fragments():
    src = {}
    for p in sorted(B.OUT.glob("b*.tsv")):
        for r in B.read_tsv(p):
            src[r["id"]] = (p.stem, r["en"])
    out = []
    for p in B.event_files():
        for r in B.read_tsv(p):
            if r["id"] not in src:
                continue
            b, en = src[r["id"]]
            for page in en.split("{clear}"):
                parts = re.split(r"\{wait\}\{clear\}(?:\{spk:[0-9A-F]+\}\{n\})?", W.wrap_for(r["jp"], page))
                for cont in parts[1:]:
                    text = re.sub(r"\{[^}]*\}", " ", cont).strip()
                    if text and len(text.split()) <= 3 and not re.match(r"[A-Z.\"'(]", text):
                        out.append((b, r["id"], text))
    return out


if __name__ == "__main__":
    fs = fragments()
    for f in fs:
        print("\t".join(f))
    sys.exit(1 if fs else 0)
