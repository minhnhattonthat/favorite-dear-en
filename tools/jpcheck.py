"""jpcheck.py: release gate for Japanese left in the English build (`$SKILL/scripts/jp_left.py` plus the row sources).

    python -X utf8 tools/jpcheck.py [--build build/files_favorite_dear_en]

1. Rows: every row in script/ whose JP has kana/kanji must have an English `en` with no kana/kanji, unless the row is
   in docs/text_unshown_unloaded.tsv or docs/text_unshown_proven.tsv (files no event id loads, or code that can't
   reach the row) or in docs/jp_kept.tsv (Japanese kept on purpose, with the reason).
2. Binaries: `jp_left.py --orig` on the built DATA/STAFF.TXT (Shift-JIS credits) and on the built PSX.EXE limited to
   the spans of the script/exe.tsv rows (the EXE's text; the rest of the EXE holds SDK and kana-conversion tables
   that only look like text). Event scripts are rebuilt whole, so rows (step 1) cover GDATA.BIN.
Exit 1 when anything unintended is left."""
import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

JP = re.compile(r"[぀-ヿ一-鿿]")
WAIVES = ["docs/text_unshown_unloaded.tsv", "docs/text_unshown_proven.tsv", "docs/jp_kept.tsv"]


def ids(path):
    p = ROOT / path
    if not p.is_file():
        return set()
    return {line.split("\t", 1)[0].strip() for line in p.read_text(encoding="utf-8").splitlines() if line.strip()}


def rows():
    for p in sorted((ROOT / "script").rglob("*.tsv")):
        with p.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
                yield p, r


def loaded_sectors():
    """Sectors of the event scripts some event id loads (textcover_map: event names x GDATA name directory)."""
    import textcover_map
    exe = (ROOT / "work" / "disc" / "tree" / "PSX.EXE").read_bytes()
    return set(textcover_map.id_sectors(exe).values())


def check_rows():
    waived = set().union(*(ids(w) for w in WAIVES))
    loaded = loaded_sectors()
    bad, unloaded = [], 0
    for p, r in rows():
        jp, en = r.get("jp") or "", (r.get("en") or "").strip()
        if not JP.search(re.sub(r"\{[^}]*\}", "", jp)):
            continue
        if r["id"] in waived:
            continue
        if p.parent.name == "events" and int(p.stem, 16) not in loaded:
            unloaded += 1
            continue
        if not en or en == "-" or JP.search(re.sub(r"\{[^}]*\}", "", en)):
            bad.append(f"{p.relative_to(ROOT).as_posix()} {r['id']}: en={en[:40]!r}")
    print(f"rows: {unloaded} Japanese rows skipped in files no event id loads (unused leftovers)")
    return bad


def jp_left(*args):
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "jp_left.py"), *map(str, args)]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return res.returncode, res.stdout.strip()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", default=str(ROOT / "build" / "files_favorite_dear_en"))
    a = ap.parse_args(argv)
    build, orig = Path(a.build), ROOT / "work" / "disc" / "tree"
    fail = 0
    bad = check_rows()
    print(f"rows: {len(bad)} with Japanese and no English (not waived)")
    for line in bad[:50]:
        print("  " + line)
    fail |= bool(bad)

    rc, out = jp_left(build / "DATA" / "STAFF.TXT", "--sjis", "--orig", orig / "DATA" / "STAFF.TXT", "--limit", 20)
    print("STAFF.TXT: " + out.splitlines()[-1] if out else "STAFF.TXT: no output")
    if rc:
        print(out)
    fail |= rc != 0

    kept = ids("docs/jp_kept.tsv")
    spans = []  # (start, rough end, translated): each span is cut at the next row's start
    for p, r in rows():
        if p.name == "exe.tsv" and r["id"].startswith("PSX."):
            o = int(r["id"].split(".")[1], 16)
            spans.append((o, o + 2 * len(r["jp"]) + 2, (r.get("en") or "").strip() not in ("", "-")
                          and r["id"] not in kept))
    spans.sort()
    ranges = []
    for i, (o, end, live) in enumerate(spans):
        if live:
            nxt = spans[i + 1][0] if i + 1 < len(spans) else end
            ranges.append(f"{o:X}-{min(end, nxt):X}")
    if ranges:
        args = [build / "PSX.EXE", "--tbl", ROOT / "tbl" / "jp.tbl", "--orig", orig / "PSX.EXE", "--limit", 20]
        for rg in ranges:
            args += ["--range", rg]
        rc, out = jp_left(*args)
        print("PSX.EXE text rows: " + (out.splitlines()[-1] if out else "no output"))
        if rc:
            print(out)
        fail |= rc != 0
    print("jpcheck: " + ("FAIL" if fail else "ok"))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
