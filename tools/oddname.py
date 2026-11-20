"""List families whose wrapped English has an odd-length text run ending in a space right before {name}/{ins}.

    python -X utf8 tools/oddname.py > work/qa/oddname/odd.tsv      (batch<TAB>family id<TAB>run)

Such a run is padded to a whole cell by en.py, so the inserted name follows a 12-px gap ("My name is  Raviel").
Fix: reword the run (the text after the last {n}/code before the name) to an even length, then merge and re-run.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches as B  # noqa: E402

where = {}
for p in sorted(B.OUT.glob("b*.tsv")):
    for r in B.read_tsv(p):
        where[r["id"]] = (p.stem, r["en"])
en_rows = {}
for p in B.event_files():
    for r in B.read_tsv(p):
        en_rows[r["id"]] = r.get("en") or ""
seen = set()
for key, rows in B.families().items():
    rep = rows[0]
    if rep["id"] not in where:
        continue
    for r in rows:
        en = en_rows.get(r["id"], "")
        for m in re.finditer(r"(?:^|\})([^{}]*)\{(name|ins)[^}]*\}", en):
            run = m.group(1)
            if run.endswith(" ") and len(run) % 2 == 1 and (rep["id"], run) not in seen:
                seen.add((rep["id"], run))
                b, src = where[rep["id"]]
                print(f"{b}\t{rep['id']}\t{run}")
