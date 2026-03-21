from pathlib import Path
import re

BASE_DIR = Path(__file__).parent
HTML_FILES = [
    "index.html",
    "apps.html",
    "about.html",
    "privacy.html",
    "support.html",
]
ALL_FILES = HTML_FILES + ["styles.css"]


def read_file(name: str) -> str:
    return (BASE_DIR / name).read_text(encoding="utf-8")


def test_all_required_files_exist():
    for name in ALL_FILES:
        assert (BASE_DIR / name).exists(), f"Missing required file: {name}"


def test_all_html_have_doctype():
    for file_name in HTML_FILES:
        content = read_file(file_name).lstrip().lower()
        assert content.startswith("<!doctype html>"), f"{file_name} missing HTML5 doctype"


def test_all_html_have_viewport_meta():
    pattern = re.compile(r'<meta\s+name="viewport"\s+content="width=device-width,\s*initial-scale=1"\s*/?>', re.I)
    for file_name in HTML_FILES:
        content = read_file(file_name)
        assert pattern.search(content), f"{file_name} missing viewport meta tag"


def test_each_page_has_navigation_links():
    nav_pattern = re.compile(r"<nav[^>]*>.*?</nav>", re.I | re.S)
    for file_name in HTML_FILES:
        content = read_file(file_name)
        nav_match = nav_pattern.search(content)
        assert nav_match, f"{file_name} missing <nav>"
        nav_content = nav_match.group(0)
        for link in HTML_FILES:
            assert f'href="{link}"' in nav_content, f"{file_name} nav missing link to {link}"


def test_index_mentions_all_app_names():
    content = read_file("index.html")
    for name in ["QRion", "Calmos", "Preciq", "VoxIQ"]:
        assert name in content, f"index.html missing app name: {name}"


def test_apps_page_has_four_app_cards():
    content = read_file("apps.html")
    cards = re.findall(r'class="[^"]*app-card[^"]*"', content)
    assert len(cards) == 4, "apps.html should contain exactly 4 app cards"


def test_privacy_mentions_gdpr():
    content = read_file("privacy.html")
    assert "GDPR" in content, "privacy.html must mention GDPR"


def test_support_has_faq_section():
    content = read_file("support.html")
    assert re.search(r'id="faq"', content, re.I), "support.html missing FAQ section id"
    assert re.search(r">\s*FAQ\s*<", content, re.I), "support.html missing FAQ heading"


def test_styles_has_dark_mode_variables():
    content = read_file("styles.css")
    assert ":root" in content
    assert "--bg" in content
    assert ":root.theme-light" in content


def test_styles_has_responsive_media_queries():
    content = read_file("styles.css")
    assert "@media (min-width:" in content or "@media (max-width:" in content


def test_internal_links_reference_existing_files():
    href_pattern = re.compile(r'href="([^"]+)"', re.I)
    for file_name in HTML_FILES:
        content = read_file(file_name)
        for href in href_pattern.findall(content):
            if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                continue
            target = href.split("#", 1)[0].split("?", 1)[0]
            # Root pages must link to known root files, but allow links into subfolders
            # (e.g. /qrion/ landing pages).
            if target in ALL_FILES:
                assert (BASE_DIR / target).exists(), f"{file_name} links to missing file: {target}"
            else:
                assert (BASE_DIR / target).exists(), f"{file_name} has unknown internal link: {href}"


def test_all_pages_include_shared_stylesheet():
    for file_name in HTML_FILES:
        content = read_file(file_name)
        assert 'href="styles.css"' in content, f"{file_name} should include styles.css"
