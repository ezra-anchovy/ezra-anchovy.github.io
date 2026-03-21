from pathlib import Path
import re

BASE = Path(__file__).parent
QRION_DIR = BASE / "qrion"

PAGES = [
    QRION_DIR / "index.html",
    QRION_DIR / "faq" / "index.html",
    QRION_DIR / "privacy" / "index.html",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_qrion_pages_exist():
    for p in PAGES:
        assert p.exists(), f"Missing {p}"


def test_qrion_pages_have_doctype_and_viewport():
    viewport = re.compile(r'<meta\s+name="viewport"\s+content="width=device-width,\s*initial-scale=1"\s*/?>', re.I)
    for p in PAGES:
        content = read(p).lstrip().lower()
        assert content.startswith("<!doctype html>"), f"{p} missing HTML5 doctype"
        assert viewport.search(read(p)), f"{p} missing viewport meta"


def test_qrion_pages_reference_existing_assets():
    href_src = re.compile(r'(?:href|src)="([^"]+)"', re.I)
    for p in PAGES:
        content = read(p)
        for ref in href_src.findall(content):
            if ref.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                continue
            ref_path = (p.parent / ref).resolve()
            # allow query/hash
            ref_path = Path(str(ref_path).split("#", 1)[0].split("?", 1)[0])
            assert ref_path.exists(), f"{p} references missing asset: {ref} -> {ref_path}"
