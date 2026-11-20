"""stafftext.py: English credits (DATA/STAFF.TXT, drawn by FIN.EXE) from trans/staff/en.tsv into script/staff.tsv.

    python -X utf8 tools/stafftext.py check    validate trans/staff/en.tsv; prints OK or errors
    python -X utf8 tools/stafftext.py merge    check, then write `en` into script/staff.tsv

trans/staff/en.tsv: `id<TAB>en`, one row per script/staff.tsv row. FIN.EXE draws only double-byte codes, so
insert.py turns the ASCII into pair codes (two 6-px letters per code, asm/fin.asm); a line shows 28 letters from
x=148, leading spaces included (docs/windows.tsv `credits`), each Japanese full-width space of indent = 2 spaces.
A leading '&' (closing cards STAFF.457-460) is a single-byte code kept as is. '|' splits a row into lines of its own
(insert.staff_en: the two-name painter rows get one name per line; later rows keep their ids). Never a leading '%':
FIN reads it as "line at x=64", but the roll stops there for good (tested phase 8, `docs/re/text.md` §Credits).
Letters: font_en.FIN_CHARSET. Names: given name first, Hepburn without macrons (decision D2).
`-` keeps the Japanese line."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import batches  # noqa: E402
import extract  # noqa: E402
import font_en  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STAFF = ROOT / "script" / "staff.tsv"
SRC = ROOT / "trans" / "staff" / "en.tsv"
LETTERS = 28
CHARSET = set(font_en.FIN_CHARSET)


def check():
    rows = {r["id"]: r for r in extract.read_tsv(STAFF)}
    out = batches.read_tsv(SRC)
    errs = []
    ids = [r["id"] for r in out]
    if set(ids) != set(rows) or len(ids) != len(set(ids)):
        errs.append(f"ids differ: missing {sorted(set(rows) - set(ids))} extra {sorted(set(ids) - set(rows))}")
    for r in out:
        text = r["en"]
        if text == "-":  # keep the Japanese line (a name with no English form that fits)
            continue
        body = text[1:] if r["id"] in rows and rows[r["id"]]["jp"].startswith("&") and text.startswith("&") else text
        if body.startswith("%"):
            errs.append(f"{r['id']}: a leading '%' stops the roll; split the line with '|' instead")
        for line in body.split("|"):
            if not line.strip():
                errs.append(f"{r['id']}: empty line in {body!r}")
            if len(line) > LETTERS:
                errs.append(f"{r['id']}: {len(line)} letters > {LETTERS}: {line!r}")
            if set(line) - CHARSET:
                errs.append(f"{r['id']}: letters FIN's font lacks {sorted(set(line) - CHARSET)} in {line!r}")
    return errs


def main(argv):
    if not argv or argv[0] not in ("check", "merge"):
        print(__doc__)
        return 2
    errs = check()
    if errs:
        print("\n".join(errs))
        return 1
    if argv[0] == "check":
        print("staff: OK")
        return 0
    en = {r["id"]: "" if r["en"] == "-" else r["en"] for r in batches.read_tsv(SRC)}
    rows = extract.read_tsv(STAFF)
    changed = 0
    for r in rows:
        if r["en"] != en[r["id"]]:
            r["en"] = en[r["id"]]
            changed += 1
    extract.write_tsv(STAFF, rows)
    print(f"staff: {changed} rows changed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
