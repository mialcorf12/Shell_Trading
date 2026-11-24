import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import post_pipeline  # noqa: E402


def test_post_key_from_urls():
    assert post_pipeline.post_key("https://www.instagram.com/p/Ddd43P8lD2j/") == "Ddd43P8lD2j"
    assert post_pipeline.post_key("https://www.instagram.com/reel/DfAmobOMBgE/?hl=es") == "DfAmobOMBgE"


def test_video_urls_unescapes_and_deduplicates():
    sample = (
        r'prefix video_url\":\"https:\\\/\\\/cdn.net\\\/v1.mp4?a=1&amp;b=2\"'
        r' middle video_url\":\"https:\\\/\\\/cdn.net\\\/v1.mp4?a=1&amp;b=2\"'
        r' other video_url\":\"https:\\\/\\\/cdn.net\\\/v2.mp4\"'
    )
    urls = post_pipeline.video_urls(sample)
    assert urls == ["https://cdn.net/v1.mp4?a=1&b=2", "https://cdn.net/v2.mp4"]


def test_slide_urls_unescapes_and_deduplicates():
    sample = (
        r'display_url\":\"https:\\\/\\\/cdn.net\\\/img1.jpg\" '
        r'display_url\":\"https:\\\/\\\/cdn.net\\\/img1.jpg\" '
        r'display_url\":\"https:\\\/\\\/cdn.net\\\/img2.jpg\"'
    )
    urls = post_pipeline.slide_urls(sample)
    assert urls == ["https://cdn.net/img1.jpg", "https://cdn.net/img2.jpg"]


def test_caption_strips_html_and_unescapes():
    sample = '<div class="Caption"><b>User</b><br>Line 1 &amp; Line 2</div></div>'
    assert post_pipeline.caption(sample) == "User\nLine 1 & Line 2"


def test_plan_slides_images_only():
    plan = post_pipeline.plan_slides(["i1.jpg", "i2.jpg"], [])
    assert plan == [("img", "i1.jpg"), ("img", "i2.jpg")]


def test_plan_slides_animated_with_cover_image():
    plan = post_pipeline.plan_slides(["cover.jpg", "other.jpg"], ["v1.mp4", "v2.mp4"])
    assert plan == [("img", "cover.jpg"), ("vid", "v1.mp4"), ("vid", "v2.mp4")]


def test_plan_slides_animated_without_images_avoids_index_error():
    plan = post_pipeline.plan_slides([], ["v1.mp4"])
    assert plan == [("vid", "v1.mp4")]

