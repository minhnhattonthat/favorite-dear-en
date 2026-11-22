"""Hero status Equip box (asm/equip.inc, issue #2): every equippable item's English name renders in the caps4x7 font
within the 76 px between x 77 and the box's inner edge (x 152), with no character the font lacks."""
import re
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import btname  # noqa: E402

EXE = btname.TREE / "PSX.EXE"
ITEMS, ITEM_SIZE = 0x800213D0, 20      # item records: +1 type (0-18 = equipment)
NAMES = 0x80169778                     # u32 string pointers; item code c -> entry c + 0x8C (c < 0xED)
ROOM = 152 - 77 + 1


def off(va):
    return va - 0x80010000 + 0x800


def equipment_names():
    exe = EXE.read_bytes()
    rows = {}
    for line in (ROOT / "script" / "exe.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        cols = line.split("\t")
        rows[cols[0]] = cols
    names = []
    for code in range(0xED):
        if exe[off(ITEMS + ITEM_SIZE * code) + 1] > 18:
            continue
        ptr = struct.unpack_from("<I", exe, off(NAMES + 4 * (code + 0x8C)))[0]
        names.append((code, re.sub(r"\{[^}]*\}", "", rows[f"PSX.{off(ptr):X}"][2]).rstrip()))
    return names


@pytest.mark.skipif(not EXE.is_file(), reason="no unpacked disc")
def test_equipment_names_fit_caps_font():
    f = btname.font()
    names = equipment_names()
    assert len(names) > 150
    bad = [(c, n) for c, n in names if any(ch not in f for ch in n.upper()) or btname.width(n, f) > ROOM]
    assert bad == []
