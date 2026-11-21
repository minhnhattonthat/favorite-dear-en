"""Load-delay hazards in the hand-written MIPS (tools/asmlint.py): none in asm/, and the lint catches the forms that
crashed or could crash (name_latin's `lw ra` + `jr ra`, a load feeding a branch, a store or an ALU op)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import asmlint  # noqa: E402


def test_repo_asm_has_no_load_delay_hazards():
    files = sorted((ROOT / "asm").glob("*.asm")) + sorted((ROOT / "asm").glob("*.inc"))
    assert files
    assert [p for f in files for p in asmlint.lint(f)] == []


@pytest.mark.parametrize("body, hazards", [
    ("lw ra, 4(sp)\njr ra\naddiu sp, sp, 8", 1),            # the name_latin crash
    ("lw ra, 4(sp)\naddiu sp, sp, 8\njr ra\nnop", 0),
    ("lhu t5, 0(t0)\nsrl t6, t5, 8", 1),
    ("lhu t5, 0(t0)\naddiu t0, t0, 2\nsrl t6, t5, 8", 0),
    ("lbu t7, 0(t3)\nsb t7, 0(t2)", 1),                     # stored value
    ("lw t0, 0(a0)\nlw t1, 0(t0)", 1),                      # base register
    ("lw t0, 0(a0)\nbnez t0, @@x\nnop\n@@x:", 1),
    ("lw t0, 0(a0)\naddiu t0, zero, 1", 0),                 # overwritten, not read
    ("lw t0, 0(a0)\n@@x:\nmove t1, t0", 1),                 # a label does not break the pair
    ("lw t0, 0(a0)\n.org 0x80010000\nmove t1, t0", 0),      # a new block does
    ("lw t0, 0(a0) ; comment t1\nmove t1, t2 ; t0", 0),
])
def test_lint_cases(tmp_path, body, hazards):
    f = tmp_path / "x.inc"
    f.write_text(body + "\n", encoding="utf-8")
    assert len(asmlint.lint(f)) == hazards
