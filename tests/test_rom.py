"""The pinned dump: rom.sha1 lists every disc file, and check_rom accepts the dump when it is present."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402


def entries():
    lines = (ROOT / "rom.sha1").read_text(encoding="utf-8").splitlines()
    return [l.split(None, 1) for l in lines if l.strip() and not l.startswith("#")]


def test_listing_is_filled_in():
    rows = entries()
    assert rows, "rom.sha1 lists no files"
    for sha, name in rows:
        assert len(sha) == 40 and int(sha, 16) >= 0, sha
        assert name.startswith("rom/"), name


@pytest.mark.skipif(not (ROOT / "rom" / "Favorite Dear (Japan).bin").is_file(), reason="no dump in rom/")
def test_dump_matches():
    check_rom.check()
