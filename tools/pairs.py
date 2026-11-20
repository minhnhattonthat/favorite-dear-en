"""Review pairs: one file per translation batch, JP and EN side by side with control codes stripped.

    python -X utf8 tools/pairs.py [bNNN ...]     write work/qa/review/pairs/bNNN.txt (all batches if none given)

Each entry is `>> id` then `JP: ...` and `EN: ...`; ` ¦ ` marks a new text box, `<name>` a runtime name.
Rows kept as `-` (not text / glyph soup) are skipped. Read by the phase-6 review pass (qa_gate manifest in
work/qa/review/).
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "work" / "qa" / "review" / "pairs"


def flat(s: str) -> str:
    s = s.replace("{wait}{clear}", " ¦ ").replace("{wait}", " ¦ ")
    s = re.sub(r"\{name:[0-9A-F]+\}", "<name>", s)
    s = re.sub(r"\{n\}", " ", s)
    s = re.sub(r"\{[^}]*\}", "", s)
    s = re.sub(r"\[[0-9A-F]{2}\]", "", s)
    return re.sub(r"\s+", " ", s).strip(" ¦")


def load(path: Path) -> dict:
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(r)
        return {row[0]: row[-1] for row in r if row}


SEEN: set = set()


def write(b: str) -> int:
    """Boxes (JP, EN) already shown in an earlier entry are dropped (gender twins, repeated stock lines); an entry
    with nothing new left is skipped. Box lists of unequal length are shown whole."""
    jp = load(ROOT / "trans" / "batches" / f"{b}.tsv")
    en = load(ROOT / "trans" / "en" / f"{b}.tsv")
    lines, n = [], 0
    for i, j in jp.items():
        e = en.get(i, "-")
        if e.strip() == "-":
            continue
        jb, eb = flat(j).split(" ¦ "), flat(e).split(" ¦ ")
        if len(jb) == len(eb):
            keep = [(x, y) for x, y in zip(jb, eb) if (x, y) not in SEEN]
            SEEN.update(zip(jb, eb))
            if not keep:
                continue
            jb, eb = [x for x, _ in keep], [y for _, y in keep]
        lines += [f">> {i}", f"JP: {' ¦ '.join(jb)}", f"EN: {' ¦ '.join(eb)}", ""]
        n += 1
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{b}.txt").write_text("\n".join(lines), encoding="utf-8")
    return n


def main(argv):
    names = argv or sorted(p.stem for p in (ROOT / "trans" / "en").glob("b*.tsv"))
    total = sum(write(b) for b in names)
    print(f"{len(names)} pair files, {total} entries -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
