"""Tests for the portfolio. Run with:  pytest"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.content import loader
from app.main import app

client = TestClient(app)


def _keys(obj, prefix=""):
    """Every dotted path in a nested dict/list (structure only)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _keys(v, f"{prefix}{k}.")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _keys(v, f"{prefix}{i}.")
    else:
        yield prefix.rstrip(".")


def test_arabic_and_english_have_the_same_keys():
    ar = set(_keys(loader.load_json("ar.json")))
    en = set(_keys(loader.load_json("en.json")))
    assert ar - en == set(), f"Missing in en.json: {sorted(ar - en)}"
    assert en - ar == set(), f"Missing in ar.json: {sorted(en - ar)}"


def test_every_project_and_artwork_has_text_in_both_languages():
    for lang in loader.LANGUAGES:
        c = loader.copy(lang)
        for p in loader.projects():
            assert p["id"] in c["projects"]["items"], (lang, p["id"])
            assert p["status"] in c["projects"]["filters"], (lang, p["status"])
        for a in loader.site()["artworks"]:
            assert a["id"] in c["creative"]["artworks"], (lang, a["id"])
        for area in loader.experience()["areas"]:
            assert area["id"] in c["experience"]["areas"], (lang, area["id"])


def test_no_certification_is_marked_earned_without_details():
    for cert in loader.credentials()["earned"]:
        assert cert.get("name") and cert.get("issuer"), cert


@pytest.mark.parametrize("lang,direction", [("ar", "rtl"), ("en", "ltr")])
def test_home_page_renders_in_both_languages(lang, direction):
    res = client.get(f"/?lang={lang}")
    assert res.status_code == 200
    assert f'lang="{lang}" dir="{direction}"' in res.text
    assert loader.copy(lang)["experience"]["title"] in res.text
    for section in ["hero", "experience", "projects", "troubleshooting", "learning", "credentials",
                    "ideas", "creative", "teaching", "contact"]:
        assert f'id="{section}"' in res.text


def test_default_language_is_english_and_unknown_falls_back():
    assert 'lang="en" dir="ltr"' in client.get("/").text
    assert 'lang="en"' in client.get("/?lang=fr").text
    assert 'lang="ar" dir="rtl"' in client.get("/?lang=ar").text


def test_youtube_link_is_on_the_page():
    assert loader.site()["links"]["teaching_video"] in client.get("/").text


def test_static_images_exist():
    site = loader.site()
    paths = list(site["images"].values()) + [a["image"] for a in site["artworks"]] + [p["image"] for p in loader.projects() if p["image"]]
    for path in paths:
        assert client.get(path).status_code == 200, path


def test_sections_appear_in_priority_order():
    html = client.get("/?lang=en").text
    order = ["hero", "experience", "projects", "troubleshooting", "learning", "credentials", "ideas",
             "creative", "teaching", "contact"]
    positions = [html.index(f'<section id="{s}"') for s in order]
    assert positions == sorted(positions)


def test_preparing_certification_is_not_shown_as_earned():
    html = client.get("/?lang=en").text
    assert "AWS Certified Machine Learning Engineer" in html
    # the "earned" step is only rendered once a verified certificate is added
    assert ('growth-dot done' in html) == bool(loader.credentials()["earned"])


def test_wps_is_never_shown_without_its_full_name():
    for lang in loader.LANGUAGES:
        html = client.get(f"/?lang={lang}").text.split('<script id="i18n-data"')[0]
        full = "حماية الأجور" if lang == "ar" else "Wage Protection System"
        assert html.count("WPS") <= html.count(full)


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_content_api():
    assert client.get("/api/content/en").json()["name"] == loader.site()["name"]["en"]
    assert client.get("/api/content/xx").status_code == 404


def test_projects_api_filters_by_status():
    data = client.get("/api/projects?status=in_progress&lang=en").json()
    assert data and all(p["status"] == "in_progress" for p in data)
    assert "title" in data[0]


def test_learning_ideas_endpoint_returns_30_bilingual_ideas():
    res = client.get("/api/learning-ideas")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 30 == len(data["ideas"])
    ids = [i["id"] for i in data["ideas"]]
    assert len(set(ids)) == 30, "idea ids must be unique"
    for idea in data["ideas"]:
        for lang in loader.LANGUAGES:
            assert idea[lang]["title"].strip() and idea[lang]["text"].strip(), (idea["id"], lang)
            assert idea["topic"][lang].strip(), (idea["id"], lang)


@pytest.mark.parametrize("lang", loader.LANGUAGES)
def test_learning_ideas_can_be_flattened_to_one_language(lang):
    data = client.get(f"/api/learning-ideas?lang={lang}").json()
    assert data["lang"] == lang and data["count"] == 30
    assert {"id", "topic", "title", "text"} <= set(data["ideas"][0])
    assert client.get("/api/learning-ideas?lang=fr").status_code == 404


def test_ideas_section_is_on_the_page_without_the_old_notebook():
    html = client.get("/?lang=en").text
    assert 'id="idea-card"' in html and 'id="idea-next"' in html
    assert "run-all" not in html and "kernel" not in html


def test_process_section_is_removed():
    html = client.get("/?lang=ar").text
    assert 'id="process"' not in html


def test_creative_bridge_block_is_removed():
    html = client.get("/?lang=en").text
    assert 'id="creative"' in html and 'class="gallery"' in html
    assert "bridge" not in html.split('<script id="i18n-data"')[0]


def test_experience_areas_have_no_status_badges():
    for lang in loader.LANGUAGES:
        html = client.get(f"/?lang={lang}").text
        aside = html.split('class="exp-areas')[1].split("</aside>")[0]
        assert "area-status" not in aside
        assert aside.count('class="area"') == len(loader.experience()["areas"])
