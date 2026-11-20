"""tbl/jp.tbl against the unpacked disc (work/disc/tree; skipped when absent): known lines decode, every string
round-trips byte-exact, and the event-script file tables resolve."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import events  # noqa: E402
import scantext  # noqa: E402
from tbl import Table  # noqa: E402

TREE = ROOT / "work" / "disc" / "tree"
need_tree = pytest.mark.skipif(not (TREE / "PSX.EXE").is_file(), reason="disc not unpacked to work/disc/tree")
TBL = Table.load(ROOT / "tbl" / "jp.tbl")


def test_table_unique_values():
    lines = [ln for ln in (ROOT / "tbl" / "jp.tbl").read_text(encoding="utf-8").splitlines()
             if ln and not ln.startswith("#")]
    vals = [ln.split("=", 1)[1] for ln in lines]
    assert len(vals) == len(set(vals))
    assert TBL.encode("あ") == b"\x24\x00" and TBL.encode("々") == b"\xd3\x05"


@need_tree
def test_opening_line():
    exe = (TREE / "PSX.EXE").read_bytes()
    text, used = TBL.decode(exe, 0x15A8C8)
    assert text == "実はあなたにとても重要な任務を{n}まかせたいのです。{n}{wait}{end}"


@need_tree
def test_exe_strings_roundtrip():
    for f in ["PSX.EXE", "FD_BALL.EXE", "GOVER.EXE", "TITLE/EPILOG.EXE"]:
        data = (TREE / f).read_bytes()
        strings = scantext.scan(data, 2)
        assert strings
        for s, e in strings:
            text, _ = TBL.decode(data, s, e - s)
            assert TBL.encode(text) == data[s:e], (f, hex(s), text)


@need_tree
def test_event_scripts():
    exe = (TREE / "PSX.EXE").read_bytes()
    gdata = (TREE / "GDATA.BIN").read_bytes()
    fs = events.files(exe, gdata)
    assert len(fs) == 511  # 468 in the event tables + 43 battle scripts in the data table 0x4C50
    # Reiv's scouting scene (event file 18), seen on screen at work/qa/ram5 (docs/re/events.md)
    data = [f for f in fs if f[0] != 0x4C50][18][4]
    line = "あの、あなたはヴォーラス騎士団の"
    off = data.find(TBL.encode(line))
    assert off == 0xD86
    for _, codes in events.text_runs(data):
        b = struct.pack("<%dH" % len(codes), *codes)
        assert TBL.encode(TBL.decode(b, 0, len(b))[0]) == b
