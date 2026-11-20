"""Compact view of translation batches: frequent control-code runs become one symbol each.

    python -X utf8 tools/compact.py show bNNN [--from N --to M]   print the batch (JP) in compact form, numbered rows
    python -X utf8 tools/compact.py expand FILE bNNN               FILE: compact `id<TAB>en` rows -> trans/en/bNNN.tsv

The mapping is exact both ways (asserted: no symbol occurs in the source text). Used by a translating agent to cut
tokens; `trans/en/bNNN.tsv` stays the source of truth and `tools/batches.py check` validates it as usual.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# longest first; symbols never occur in the game text (checked at runtime)
SUBS = [
    ("{n}{wait}{clear}{e0:E0FF}", "¶"),
    ("{n}{wait}{clear}", "¬"),
    ("{e0:E0FF}", "§"),
    ("{spk:E783}", "Å"),
    ("{spk:0080}", "Ø"),
    ("{name:0080}", "Ñ"),
]


def compact(s: str) -> str:
    for sym in ("¶", "¬", "§", "Å", "Ø", "Ñ"):
        if sym in s:
            raise SystemExit(f"symbol {sym} already in text: {s[:60]}")
    for code, sym in SUBS:
        s = s.replace(code, sym)
    return s


def expand(s: str) -> str:
    for code, sym in SUBS:
        s = s.replace(sym, code)
    return s


def rows(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(r)
        return [row for row in r if row]


def main(argv):
    if len(argv) >= 2 and argv[0] == "show":
        lo, hi = 1, 10**9
        if "--from" in argv:
            lo = int(argv[argv.index("--from") + 1])
        if "--to" in argv:
            hi = int(argv[argv.index("--to") + 1])
        for i, (rid, jp) in enumerate(rows(ROOT / "trans/batches" / f"{argv[1]}.tsv"), 1):
            if lo <= i <= hi:
                print(f"{rid}\t{compact(jp)}")
        return 0
    if len(argv) == 3 and argv[0] == "expand":
        src = Path(argv[1])
        out = ROOT / "trans/en" / f"{argv[2]}.tsv"
        lines = ["id\ten"]
        text = src.read_text(encoding="utf-8").splitlines()
        if text and text[0].startswith("id\t"):
            text = text[1:]
        for line in text:
            if not line.strip():
                continue
            rid, en = line.split("\t", 1)
            if "\t" in en:
                raise SystemExit(f"extra tab in {rid}")
            lines.append(f"{rid}\t{expand(en)}")
        out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {out} ({len(lines) - 1} rows)")
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
