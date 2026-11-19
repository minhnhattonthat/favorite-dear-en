"""Debug tool (phase 2): scene list shape, the event-name table the warp patches, the memory-card helper."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXE = ROOT / "work/disc/tree/PSX.EXE"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_scenes_tsv_shape():
    rows = (ROOT / "tools/debug/scenes.tsv").read_text(encoding="utf-8").splitlines()
    head = rows[0].split("\t")
    assert head == ["scene", "kind", "event", "after", "frames", "note"]
    names = set()
    for r in rows[1:]:
        if not r or r.startswith("#"):
            continue
        c = r.split("\t")
        assert len(c) == 6, r
        assert c[0] not in names, c[0]
        names.add(c[0])
        assert c[1] in {"title", "load", "option", "newgame", "week", "map", "event"}, r
        assert (c[1] == "event") == bool(c[2]), r
        assert c[3] in {"hold", "mash"}, r
        assert int(c[4]) > 0


@pytest.mark.skipif(not EXE.exists(), reason="unpacked disc not present")
def test_event_name_table():
    ev = load("events", ROOT / "tools/events.py")
    names = ev.event_names(EXE.read_bytes())
    assert len(names) == 462
    assert names[32] == "MYH16" and names[150] == "MAPSYS" and names[461] == "SEND12"
    rows = (ROOT / "tools/debug/scenes.tsv").read_text(encoding="utf-8").splitlines()[1:]
    for r in rows:
        c = r.split("\t")
        if len(c) == 6 and c[1] == "event":
            assert c[2] in names, f"scene {c[0]}: unknown event {c[2]}"


def test_blank_card():
    mcd = load("mcd", ROOT / "tools/debug/mcd.py")
    d = mcd.blank()
    assert len(d) == mcd.SIZE and d[:2] == b"MC"
    assert all(ok and state == 0xA0 for _, state, _, _, _, ok in mcd.entries(d))
