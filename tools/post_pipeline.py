#!/usr/bin/env python3
"""Download an Instagram image post (carousel): slides + caption, to a scratch dir.

Uses the post's embed page (with the session cookies) to read the slide URLs and
the caption. Prints only a summary; slides and caption stay on disk.

  python3 tools/post_pipeline.py <post_url> <name> [cookies.txt]
"""
import html
import re
import subprocess
import sys
from pathlib import Path

SCRATCH = Path("/tmp/reels_scratch")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
_DISPLAY = re.compile(r'display_url\\":\\"((?:[^"\\]|\\[^"])+?)\\"')


def slide_urls(embed_html: str) -> list:
    """Unique slide image URLs from an embed page (JSON escaped inside the HTML)."""
    urls = []
    for raw in _DISPLAY.findall(embed_html):
        url = raw.replace("\\\\\\/", "/").replace("\\\\/", "/").replace("\\/", "/").replace("&amp;", "&")
        if url not in urls:
            urls.append(url)
    return urls


def single_image_urls(embed_html: str) -> list:
    """Fallback for single-image posts: the embedded media <img src>."""
    m = re.search(r'class="EmbeddedMediaImage"[^>]*src="([^"]+)"', embed_html)
    return [html.unescape(m.group(1))] if m else []


def caption(embed_html: str) -> str:
    """Caption text from the embed's Caption block, HTML-unescaped, tags stripped."""
    m = re.search(r'class="Caption">(.*?)</div>\s*</div>', embed_html, re.S)
    block = m.group(1) if m else ""
    text = re.sub(r"<br\s*/?>", "\n", block)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def post_key(url: str) -> str:
    m = re.search(r"/(?:p|reel|reels)/([^/?#]+)", url)
    if not m:
        raise SystemExit(f"not a post url: {url}")
    return m.group(1)


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip())
        return 2
    url, name = argv[0], argv[1]
    cookies = argv[2] if len(argv) > 2 else None
    out = SCRATCH / name
    out.mkdir(parents=True, exist_ok=True)

    embed_url = f"https://www.instagram.com/p/{post_key(url)}/embed/captioned/"
    cmd = ["curl", "-sL", "-A", UA, embed_url]
    if cookies:
        cmd[1:1] = ["-b", cookies]
    page = subprocess.run(cmd, capture_output=True, text=True, check=False).stdout
    if not page:
        print("EMBED_FAILED")
        return 1

    (out / "caption.txt").write_text(caption(page), encoding="utf-8")
    urls = slide_urls(page) or single_image_urls(page)
    if not urls:
        print("NO_SLIDES_FOUND")
        return 1
    ok = 0
    for i, img in enumerate(urls, 1):
        res = subprocess.run(["curl", "-sL", "-A", UA, "-o", str(out / f"slide_{i:02d}.webp"), img], check=False)
        ok += res.returncode == 0
    print(f"DIR={out}")
    print(f"SLIDES={ok}/{len(urls)}")
    print(f"CAPTION_CHARS={len((out / 'caption.txt').read_text(encoding='utf-8'))}")
    return 0 if ok == len(urls) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
