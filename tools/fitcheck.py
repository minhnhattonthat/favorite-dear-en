"""fitcheck.py: romdiff every file the English build edits against its allowed write ranges (phase 7 gate).

    python -X utf8 tools/fitcheck.py [--build build/files_favorite_dear_en]

Allowed ranges, derived from the inputs rather than the build output:
- PSX.EXE: each `script/exe.tsv` string slot (the JP string's byte length; the name-entry grid is skipped), the bytes
  armips changes when asm/font.asm is assembled onto the untouched EXE, and moved scripts' table entries.
- TITLE/EPILOG.EXE: the bytes asm/epilog.asm changes on the untouched EXE (incl. its appended sector), table entries.
- GOVER/FD_BALL/PS_MOV.EXE: moved scripts' (sector, size) table entries only.
- GDATA.BIN: the slot of every script that has rows in `script/events/`, plus the appended tail (moved scripts).
- DATA/STAFF.TXT: the whole file (re-joined lines).
Exit 1 when any file has a changed byte outside its ranges (romdiff.check)."""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import evscript  # noqa: E402
import extract  # noqa: E402
import insert  # noqa: E402
import romdiff  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TREE = insert.TREE


def diff_ranges(a, b):
    """inclusive-exclusive ranges where a and b differ (b may be longer)"""
    out, start = [], None
    n = max(len(a), len(b))
    for i in range(n):
        same = i < len(a) and i < len(b) and a[i] == b[i]
        if not same and start is None:
            start = i
        elif same and start is not None:
            out.append(range(start, i))
            start = None
    if start is not None:
        out.append(range(start, n))
    return out


def moved(orig_exe, new_exe):
    """[(table offset, old sector)] entries of the script tables that differ between the EXEs"""
    out = []
    for tab, n in evscript.events.TABLES:  # 0x4C50 included: scripts 3529-3555 sit in its last entries
        for i in range(n):
            o = tab + 8 * i
            if orig_exe[o:o + 8] != new_exe[o:o + 8]:
                out.append(o)
    return out


def entries(exe, patterns):
    """ranges of the 4-aligned 8-byte table entries in `exe` equal to one of `patterns` (old sector, size)"""
    return [range(i, i + 8) for p in patterns for i in range(0, len(exe) - 7, 4) if exe[i:i + 8] == p]


def allowed(name, orig, new, orig_psx, patterns):
    if name == "DATA/STAFF.TXT":
        return [range(0, max(len(orig), len(new)))]
    if name == "GDATA.BIN":
        secs = {int(p.stem, 16) for p in (extract.SCRIPT / "events").glob("*.tsv")}
        r = [range(sec * insert.SECTOR, sec * insert.SECTOR + size)
             for sec, size, _, _ in evscript.script_files(orig_psx, orig) if sec in secs]
        return r + [range(len(orig), max(len(orig), len(new)))]
    r = entries(orig, patterns)
    if name == "PSX.EXE":
        table = extract.exe_table()
        for row in extract.read_tsv(extract.SCRIPT / "exe.tsv"):
            if "name-entry grid" in row["notes"]:
                continue
            off = int(row["id"].split(".")[1], 16)
            r.append(range(off, off + len(table.encode(row["jp"]))))
        r += diff_ranges(orig, insert.assemble(orig))
    elif name == "TITLE/EPILOG.EXE":
        r += diff_ranges(orig, insert.assemble(orig, "epilog.asm"))
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", default=str(ROOT / "build" / "files_favorite_dear_en"))
    a = ap.parse_args()
    build = Path(a.build)
    orig_psx = (TREE / "PSX.EXE").read_bytes()
    new_psx = (build / "PSX.EXE").read_bytes()
    patterns = [orig_psx[o:o + 8] for o in moved(orig_psx, new_psx)]
    print(f"moved scripts: {' '.join('%04X' % struct.unpack('<I', p[:4])[0] for p in patterns) or 'none'}")
    bad = 0
    for path in sorted(p for p in build.rglob("*") if p.is_file()):
        name = path.relative_to(build).as_posix()
        orig, new = (TREE / name).read_bytes(), path.read_bytes()
        errs, ok = romdiff.check(orig, new, allowed(name, orig, new, orig_psx, patterns), [])
        print(f"{name}: {'FAIL' if errs else 'ok'} ({ok} allowed diffs, {len(new) - len(orig):+d} bytes)")
        for e in errs[:10]:
            print("   ", e)
        bad += bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
