"""exetext.py: translation batches for the PSX.EXE strings (script/exe.tsv), the counterpart of batches.py.

    python -X utf8 tools/exetext.py split            write trans/exe/batches/xNNN.tsv (refuses if any exist)
    python -X utf8 tools/exetext.py check x001 [..]  validate trans/exe/en/xNNN.tsv; prints OK or errors
    python -X utf8 tools/exetext.py merge            check every output, write `en` into script/exe.tsv
    python -X utf8 tools/exetext.py todo             batches without an output file

PSX.EXE strings are rewritten in place (tools/insert.py exe_text) until phase 7 repoints them, so each English string
must encode (tools/en.py: two letters per halfword) to no more bytes than the Japanese slot. Batch input:
`id<TAB>bytes<TAB>jp` (bytes = the slot). Rows with the same JP form a family: only the first is batched and merge
copies its English to the rest. Output: `id<TAB>en`, every control code kept in order ({n} = a hard line break in the
original, kept where the layout needs it), or `-` to keep the Japanese (not text, or no fit until repointing).
The name-entry grids are not batched (fixed cells, phase 7)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import batches  # noqa: E402
import en  # noqa: E402
import extract  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXE = ROOT / "script" / "exe.tsv"
BATCHES = ROOT / "trans" / "exe" / "batches"
OUT = ROOT / "trans" / "exe" / "en"
PER_BATCH = 120
LINE = 40  # letters per line in the widest PSX.EXE window (docs/windows.tsv hub_help)
SKIP = "-"


def rows():
    return [r for r in extract.read_tsv(EXE) if "name-entry grid" not in r["notes"]]


def slot(jp, table):
    return len(table.encode(jp))


def families():
    fam = {}
    for r in rows():
        fam.setdefault(r["jp"], []).append(r)
    return fam


def split():
    if any(BATCHES.glob("x*.tsv")):
        sys.exit(f"{BATCHES} already has batches; refusing to overwrite")
    table = extract.exe_table()
    reps = [rs[0] for rs in families().values()]
    for k in range(0, len(reps), PER_BATCH):
        part = [{"id": r["id"], "bytes": str(slot(r["jp"], table)), "jp": r["jp"]} for r in reps[k:k + PER_BATCH]]
        batches.write_tsv(BATCHES / f"x{k // PER_BATCH + 1:03d}.tsv", part, ["id", "bytes", "jp"])
    print(f"{len(reps)} families in {(len(reps) + PER_BATCH - 1) // PER_BATCH} batches")


def check_row(rid, budget, jp, text, table, terms):
    if text == SKIP:
        return []
    errs = []
    codes = lambda s: re.findall(r"\{[^}]*\}", s)  # noqa: E731
    if [c for c in codes(jp) if c != "{n}"] != [c for c in codes(text) if c != "{n}"]:
        errs.append(f"{rid}: codes differ\n    jp {''.join(codes(jp))}\n    en {''.join(codes(text))}")
    plain = re.sub(r"\{[^}]*\}", "\n", text)
    bad = sorted(set(plain) - batches.ALLOWED - {"\n"})
    if bad:
        errs.append(f"{rid}: characters not in the font: {''.join(bad)!r}")
        return errs
    for ln in plain.split("\n"):
        if len(ln) > LINE:
            errs.append(f"{rid}: line over {LINE} letters: {ln}")
    try:
        n = len(en.encode(text, table))
        if n > budget:
            errs.append(f"{rid}: {n} bytes > slot {budget}")
    except ValueError as e:
        errs.append(f"{rid}: {e}")
    jpt = re.sub(r"\{[^}]*\}", "", jp)
    for tj, te, _ in terms:
        if batches.term_in(tj, jpt) and te.split(" (")[0] not in plain:
            errs.append(f"{rid}: glossary {tj} -> {te} missing")
    return errs


def check(name, table=None, terms=None):
    table = table or extract.exe_table()
    terms = batches.glossary() if terms is None else terms
    src = batches.read_tsv(BATCHES / f"{name}.tsv")
    outp = OUT / f"{name}.tsv"
    if not outp.exists():
        return [f"{name}: no output file {outp}"]
    out = batches.read_tsv(outp)
    ids = [r["id"] for r in out]
    errs = []
    if len(ids) != len(set(ids)):
        errs.append(f"{name}: duplicate ids")
    if set(ids) != {r["id"] for r in src}:
        want = {r["id"] for r in src}
        errs.append(f"{name}: missing {sorted(want - set(ids))} extra {sorted(set(ids) - want)}")
    got = {r["id"]: r.get("en") or "" for r in out}
    for r in src:
        if r["id"] in got:
            errs += check_row(r["id"], int(r["bytes"]), r["jp"], got[r["id"]], table, terms)
    return errs


def merge():
    table, terms = extract.exe_table(), batches.glossary()
    trans, failed = {}, []
    for p in sorted(OUT.glob("x*.tsv")):
        errs = check(p.stem, table, terms)
        if errs:
            failed.append(p.stem)
            print(f"{p.stem}: {len(errs)} errors, skipped")
            continue
        trans.update({r["id"]: r["en"] for r in batches.read_tsv(p)})
    by_jp = {}
    for jp, rs in families().items():
        t = trans.get(rs[0]["id"])
        if t and t != SKIP:
            by_jp[jp] = t
    all_rows = extract.read_tsv(EXE)
    changed = 0
    for r in all_rows:
        new = by_jp.get(r["jp"])
        if new is not None and "name-entry grid" not in r["notes"] and r["en"] != new:
            r["en"] = new
            changed += 1
    if changed:
        extract.write_tsv(EXE, all_rows)
    print(f"merged {len(trans)} translations -> {changed} rows changed; failed batches: {failed or 'none'}")
    return 1 if failed else 0


def main(argv):
    if not argv or argv[0] not in ("split", "check", "merge", "todo"):
        print(__doc__)
        return 2
    if argv[0] == "split":
        split()
        return 0
    if argv[0] == "merge":
        return merge()
    if argv[0] == "todo":
        todo = [p.stem for p in sorted(BATCHES.glob("x*.tsv")) if not (OUT / p.name).exists()]
        print(f"{len(todo)} to do: {' '.join(todo)}")
        return 0
    bad = 0
    for name in argv[1:]:
        errs = check(name)
        print(f"{name}: OK" if not errs else "\n".join(errs))
        bad += bool(errs)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
