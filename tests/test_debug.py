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
    assert head == ["scene", "kind", "arg", "after", "frames", "card", "post", "proof", "note"]
    names = set()
    for r in rows[1:]:
        if not r or r.startswith("#"):
            continue
        c = r.split("\t")
        assert len(c) == 9, r
        assert c[0] not in names, c[0]
        names.add(c[0])
        assert c[1] in {"title", "load", "option", "newgame", "week", "map", "event", "exec", "save", "battle"}, r
        assert (c[1] in {"event", "exec", "save", "battle"}) == bool(c[2]), r
        if c[1] == "battle":
            assert int(c[2]) >= 0, r
        if c[1] == "exec":
            assert c[2] in {"GOVER", "FD_BALL", "EPILOG", "FIN", "FD_MOV", "PS_MOV"}, r
        if c[1] == "save":
            assert c[2] in {"1", "2", "3"} and c[5], r
        assert c[3] in {"hold", "mash"}, r
        assert int(c[4]) > 0
        assert not c[7] or int(c[7]) > 0, r


def test_save_editor_roundtrip(tmp_path):
    """save.py on a synthetic card: edits land in both copies, checksums verify, --bad-sum is caught."""
    mcd = load("mcd", ROOT / "tools/debug/mcd.py")
    save = load("save", ROOT / "tools/debug/save.py")
    card = bytearray(mcd.blank())
    o = 1 * mcd.FRAME
    card[o:o + 4] = (0x51).to_bytes(4, "little")
    card[o + 4:o + 8] = (16384).to_bytes(4, "little")
    card[o + 10:o + 30] = b"BISLPS-0175900\0\0\0\0\0\0"
    card[o + 127] = mcd.xor(card[o:o + 127])
    f = bytearray(16384)
    f[0x204:0x210] = b"\xff" * 12
    save.fix(f)
    card[mcd.BLOCK:mcd.BLOCK + 16384] = f
    src = tmp_path / "in.mcd"
    src.write_bytes(card)
    enc, dec = save.table()
    found = save.saves(card)
    assert [n for n, _ in found] == [1]
    g = bytearray(f)
    save.set_name(g, "ラビエル", enc)
    assert save.name_of(g, dec) == "ラビエル"
    assert g[0x204:0x20C] == bytes.fromhex("b600a1007900b800") and g[0x19AE:0x19B6] == g[0x204:0x20C]
    save.fix(g)
    assert tuple(save.sums(g)) == tuple(int.from_bytes(g[0x200 + i:0x202 + i], "little") for i in (0, 2))
    save.fix(g, bad=True)
    assert save.sums(g)[0] != int.from_bytes(g[0x200:0x202], "little")


@pytest.mark.skipif(not (ROOT / "work/saves/week2.mcd").exists(), reason="game-written card not present")
def test_game_written_cards_checksum():
    save = load("save", ROOT / "tools/debug/save.py")
    for name in ("week1", "week2"):
        card = (ROOT / f"work/saves/{name}.mcd").read_bytes()
        for _, at in save.saves(card):
            f = card[at:at + 16384]
            assert tuple(save.sums(f)) == (int.from_bytes(f[0x200:0x202], "little"),
                                           int.from_bytes(f[0x202:0x204], "little")), name


@pytest.mark.skipif(not EXE.exists(), reason="unpacked disc not present")
def test_event_name_table():
    ev = load("events", ROOT / "tools/events.py")
    names = ev.event_names(EXE.read_bytes())
    assert len(names) == 462
    assert names[32] == "MYH16" and names[150] == "MAPSYS" and names[461] == "SEND12"
    rows = (ROOT / "tools/debug/scenes.tsv").read_text(encoding="utf-8").splitlines()[1:]
    for r in rows:
        c = r.split("\t")
        if len(c) == 9 and c[1] == "event":
            assert c[2] in names, f"scene {c[0]}: unknown event {c[2]}"


def test_blank_card():
    mcd = load("mcd", ROOT / "tools/debug/mcd.py")
    d = mcd.blank()
    assert len(d) == mcd.SIZE and d[:2] == b"MC"
    assert all(ok and state == 0xA0 for _, state, _, _, _, ok in mcd.entries(d))
