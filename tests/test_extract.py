"""Phase 4 gate: script/*.tsv against the original disc (work/disc/tree; skipped when absent).

- roundtrip: every row's `jp` re-encodes to the original bytes at its id's address;
- coverage: every event script sweeps end to end (ops, messages, padding), every message halfword with a glyph is in
  exactly one row, the PSX.EXE text regions hold nothing but rows, codes-only strings, 0x0000 and EXE_DATA, and
  STAFF.TXT rebuilds from its lines;
- the TSVs on disk list exactly the rows tools/extract.py produces (a stale or hand-damaged jp column fails).
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import evscript  # noqa: E402
import extract  # noqa: E402

TREE = ROOT / "work" / "disc" / "tree"
pytestmark = pytest.mark.skipif(not (TREE / "PSX.EXE").is_file(), reason="disc not unpacked to work/disc/tree")
SCRIPT = ROOT / "script"


@pytest.fixture(scope="module")
def disc():
    return (TREE / "PSX.EXE").read_bytes(), (TREE / "GDATA.BIN").read_bytes()


@pytest.fixture(scope="module")
def events(disc):
    return extract.event_rows(*disc)


def test_every_script_parses(disc):
    files = evscript.script_files(*disc)
    assert len(files) == 513  # 468 event-table entries + 43 battle scripts (data table 0x4C50) + 2 orphans
    for sec, size, data, where in files:
        evscript.Script(data)  # raises ParseError


def test_event_coverage(events):
    rows, scripts = events
    for sec, (sc, where) in scripts.items():
        pc = sc.start
        for kind, s, e in sc.items:  # contiguous from the first op to the last used halfword
            assert s == pc, (hex(sec), kind, s)
            pc = e
        assert pc == sc.n
        assert sc.code[sc.n:] == (0,) * (len(sc.code) - sc.n)
        msgs = [(s, e) for kind, s, e in sc.items if kind == "msg"]
        segs = sc.segments
        assert [a for a, _ in segs if a in {s for s, _ in msgs}] == [s for s, _ in msgs]
        assert sum(b - a for a, b in segs) == sum(e - s for s, e in msgs)  # segments tile the messages
        ids = {r["id"] for r in rows[sec]}
        for a, b in segs:
            rid = f"{sec:04X}.{sc.byte(a):04X}"
            assert (rid in ids) == extract.has_text(sc.code[a:b]), rid


def test_event_tsv_roundtrip(disc, events):
    rows, scripts = events
    table = extract.event_table()
    files = {sec: data for sec, _, data, _ in evscript.script_files(*disc)}
    on_disk = sorted((SCRIPT / "events").glob("*.tsv"))
    assert {int(p.stem, 16) for p in on_disk} == {sec for sec, r in rows.items() if r}
    for p in on_disk:
        sec = int(p.stem, 16)
        sc = scripts[sec][0]
        ends = {sc.byte(a): sc.byte(b) for a, b in sc.segments}
        tsv = extract.read_tsv(p)
        assert [r["id"] for r in tsv] == [r["id"] for r in rows[sec]], p.name
        for r in tsv:
            off = int(r["id"].split(".")[1], 16)
            assert table.encode(r["jp"]) == files[sec][off:ends[off]], r["id"]


def test_exe_coverage_and_roundtrip(disc):
    exe = disc[0]
    table = extract.exe_table()
    rows = extract.exe_rows(exe)
    tsv = extract.read_tsv(SCRIPT / "exe.tsv")
    assert [r["id"] for r in tsv] == [r["id"] for r in rows]
    spans = []
    for r in tsv:
        off = int(r["id"].split(".")[1], 16)
        raw = table.encode(r["jp"])
        assert exe[off:off + len(raw)] == raw, r["id"]
        spans.append((off, off + len(raw)))
    for lo, hi in extract.EXE_REGIONS:
        cov = bytearray(hi - lo)
        for s, e in extract.exe_strings(exe, lo, hi):  # rows plus codes-only strings ({end} alone, blanks)
            cov[s - lo:e - lo] = b"\1" * (e - s)
        for s, e in extract.EXE_DATA:
            if lo <= s < hi:
                cov[s - lo:e - lo] = b"\1" * (e - s)
        loose = [lo + i for i in range(0, hi - lo, 2) if not cov[i] and exe[lo + i:lo + i + 2] != b"\0\0"]
        assert not loose, [hex(x) for x in loose[:10]]
    for s, e in spans:  # every string row is in a region or a grid
        assert any(lo <= s and e <= hi for lo, hi in extract.EXE_REGIONS + extract.EXE_GRIDS), hex(s)


def test_staff_roundtrip():
    data = (TREE / "DATA/STAFF.TXT").read_bytes()
    lines = extract.staff_lines(data)
    assert extract.STAFF_NL.join(extract.staff_encode(extract.staff_decode(x)) for x in lines) == data
    tsv = extract.read_tsv(SCRIPT / "staff.tsv")
    assert [r["id"] for r in tsv] == [r["id"] for r in extract.staff_rows(data)]
    for r in tsv:
        assert extract.staff_encode(r["jp"]) == lines[int(r["id"].split(".")[1])], r["id"]


def test_sjis_titles():
    tsv = extract.read_tsv(SCRIPT / "sjis.tsv")
    assert len(tsv) == len(extract.SJIS)
    for (name, off), r in zip(extract.SJIS, tsv):
        raw = r["jp"].encode("cp932")
        data = (TREE / name).read_bytes()
        assert data[off:off + len(raw) + 1] == raw + b"\0", r["id"]


def test_tsv_columns():
    for p in SCRIPT.rglob("*.tsv"):
        extract.read_tsv(p)  # raises on a wrong column count or header


def test_known_lines(events):
    rows, _ = events
    # lines seen on screen: Reiv's scouting scene (docs/re/events.md), EPILOG's save prompt (warp epilog_end1)
    for line in ("あの、あなたはヴォーラス騎士団の", "クリアデータを保存しますか？"):
        assert any(line in r["jp"].replace("､", "、") for rs in rows.values() for r in rs), line
    staff = extract.read_tsv(SCRIPT / "staff.tsv")
    assert any(r["jp"] == "シーヴァス・フォルクガング" for r in staff)
