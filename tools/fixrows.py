"""fixrows.py: reviewed, exact substring fixes inside trans/en/bNNN.tsv rows (no regex, every hit counted).

    python -X utf8 tools/fixrows.py FIXES.tsv     lines: batch<TAB>id<TAB>old<TAB>new  (# comments allowed)

Each `old` must occur in that row (all occurrences are replaced; the count is printed). Run `batches.py check` and
`merge` afterwards. For review fixes found line by line; never for blind prose rewrites.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import batches as B  # noqa: E402


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    by = {}
    for line in Path(argv[0]).read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            b, i, old, new = line.split("\t")
            by.setdefault(b, []).append((i, old, new))
    for b, fs in by.items():
        p = B.OUT / f"{b}.tsv"
        rows = B.read_tsv(p)
        for i, old, new in fs:
            hit = [r for r in rows if r["id"] == i]
            if len(hit) != 1:
                sys.exit(f"{b} {i}: row not found")
            n = hit[0]["en"].count(old)
            if not n:
                sys.exit(f"{b} {i}: {old!r} not in the row")
            hit[0]["en"] = hit[0]["en"].replace(old, new)
            print(f"{b} {i} x{n}")
        B.write_tsv(p, rows, ["id", "en"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
