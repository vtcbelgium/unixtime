import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
    "X-Content-Type-Options: nosniff",
    "X-Frame-Options: DENY",
    "Referrer-Policy: strict-origin-when-cross-origin",
]
PAGES = [ROOT / "index.html", *[ROOT / l / "index.html" for l in ("nl", "fr", "de", "es", "pt")]]


def blocks(html):
    return [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


def test_headers_files():
    for f in (ROOT / "_headers", ROOT / "public" / "_headers"):
        text = f.read_text(encoding="utf-8")
        for line in REQUIRED:
            assert line in text, (f, line)


def test_og_image_and_twitter():
    assert (ROOT / "public" / "og-image.svg").exists()
    for f in PAGES:
        html = f.read_text(encoding="utf-8")
        assert '<meta property="og:image" content="https://unixtime.othrys.be/og-image.svg">' in html, f
        assert '<meta name="twitter:card" content="summary_large_image">' in html, f
        assert 'name="twitter:image"' in html, f


def test_jsonld_types():
    for f in PAGES:
        types = [b["@type"] for b in blocks(f.read_text(encoding="utf-8"))]
        assert "WebApplication" in types and "FAQPage" in types, f
        faq = next(b for b in blocks(f.read_text(encoding="utf-8")) if b["@type"] == "FAQPage")
        assert len(faq["mainEntity"]) == 3


def test_no_person_or_anti_ad_claims():
    for f in PAGES:
        html = f.read_text(encoding="utf-8")
        assert '"Person"' not in html, f
        assert not re.search(r"zero ads|never ads|no ads", html, re.I), f


def test_build_outputs_headers_and_og_image():
    src = (ROOT / "build.py").read_text(encoding="utf-8")
    assert "'_headers'" in src and "og-image.svg" in src
