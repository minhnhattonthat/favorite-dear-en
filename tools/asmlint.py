"""asmlint.py: load-delay hazards in the hand-written MIPS (asm/*.asm, asm/*.inc).

The R3000A has no load interlock: the instruction right after a load still sees the register's OLD value. Real
hardware and DuckStation behave that way; this repo's PCSX-Redux run does not for `jr` (it read the new ra), so a
hazard there passes every emulator test and crashes players. `lw ra, 4(sp)` + `jr ra` in name.inc's name_latin
jumped back into name_latin, left sp 8 bytes off and crashed the game at name entry (DuckStation, 2026-11-21).

    python -X utf8 tools/asmlint.py [FILE..]      exit 1 if any load's next instruction reads the loaded register

Flow is followed in source order inside one `.org` block (a label in between does not break the pair). A load in a
branch delay slot is checked against the next source line too, which is conservative."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LOADS = {"lb", "lbu", "lh", "lhu", "lw", "lwl", "lwr"}
# mnemonics whose first operand is written, not read (everything else reads all its register operands)
WRITES_FIRST = LOADS | {
    "addiu", "addi", "addu", "add", "subu", "sub", "and", "andi", "or", "ori", "xor", "xori", "nor", "slt", "slti",
    "sltu", "sltiu", "sll", "srl", "sra", "sllv", "srlv", "srav", "lui", "li", "la", "move", "neg", "negu", "not",
    "mfhi", "mflo", "mfc0", "mfc2", "cfc2", "lwc2",
}
REG = re.compile(r"\b(zero|at|v[01]|a[0-3]|t[0-9]|s[0-8]|k[01]|gp|sp|fp|ra|r\d{1,2})\b")


def strip(line):
    return line.split(";", 1)[0].split("//", 1)[0].strip()


def instructions(path):
    """Yield (lineno, mnemonic, operand text) per instruction; None marks a block break (.org, .incbin, data)."""
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = strip(raw)
        while True:  # labels, possibly several, before an instruction
            m = re.match(r"^[@\w.]+:\s*", line)
            if not m:
                break
            line = line[m.end():]
        if not line:
            continue
        if line.startswith("."):
            if line.split()[0].lower() in (".org", ".orga", ".incbin", ".fill", ".ascii", ".asciiz", ".halfword",
                                           ".word", ".byte", ".dh", ".dw", ".db", ".include", ".close", ".open"):
                yield None
            continue
        if re.match(r"^\w+\s+equ\b", line, re.I) or line.lower().startswith(("if ", "endif")):
            continue
        parts = line.split(None, 1)
        yield n, parts[0].lower(), parts[1] if len(parts) > 1 else ""


def reads(mnem, ops):
    regs = REG.findall(ops)
    if mnem in WRITES_FIRST and regs:
        first = ops.split(",", 1)[0]
        if REG.search(first):
            regs = regs[1:]
    return set(regs)


def lint(path):
    out = []
    prev = None
    for ins in instructions(path):
        if ins is None:
            prev = None
            continue
        n, mnem, ops = ins
        if prev is not None:
            pn, pm, pops = prev
            dest = REG.findall(pops.split(",", 1)[0])
            if dest and dest[0] not in ("zero", "r0") and dest[0] in reads(mnem, ops) and not (
                    pm in ("lwl", "lwr") and mnem in ("lwl", "lwr")):
                out.append(f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}:{n}: "
                           f"'{mnem} {ops}' reads {dest[0]} in the load delay slot of line {pn} '{pm} {pops}'")
        prev = ins if mnem in LOADS else None
    return out


def main(argv):
    files = [Path(a).resolve() for a in argv] or sorted((ROOT / "asm").glob("*.asm")) + sorted(
        (ROOT / "asm").glob("*.inc"))
    problems = [p for f in files for p in lint(f)]
    for p in problems:
        print(p)
    print(f"asmlint: {len(files)} files, {len(problems)} load-delay hazards")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
