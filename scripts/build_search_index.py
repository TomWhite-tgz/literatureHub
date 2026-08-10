#!/usr/bin/env python3
"""Build the deterministic browser-side full-text index for the static site."""

from __future__ import annotations

import html
import json
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote


DEFAULT_SITE = Path("site")
OUTPUT_NAME = "search-index.js"
MAX_BODY_CHARS = 24_000
SKIP_PARTS = {"assets"}
SKIP_NAMES = {"_未包含的内容.html", "OpenScholar_official_blog.html"}


class PageParser(HTMLParser):
    """Extract visible prose without pulling CSS, scripts, or embedded SVG into the index."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: list[str] = []
        self.headings: list[str] = []
        self.body: list[str] = []
        self._ignored_depth = 0
        self._capture_title = False
        self._capture_heading = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"}:
            self._ignored_depth += 1
            return
        if self._ignored_depth:
            return
        if tag == "title":
            self._capture_title = True
        if tag in {"h1", "h2", "h3", "h4"}:
            self._capture_heading = True

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"} and self._ignored_depth:
            self._ignored_depth -= 1
            return
        if tag == "title":
            self._capture_title = False
        if tag in {"h1", "h2", "h3", "h4"}:
            self._capture_heading = False

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        text = clean(data)
        if not text:
            return
        self.body.append(text)
        if self._capture_title:
            self.title.append(text)
        if self._capture_heading:
            self.headings.append(text)


def clean(value: str) -> str:
    value = unicodedata.normalize("NFKC", html.unescape(value))
    return re.sub(r"\s+", " ", value).strip()


def page_url(relative: Path) -> str:
    return "/".join(quote(part) for part in relative.parts)


def category(relative: Path) -> str:
    return " › ".join(relative.parts[:-1]) or "首页"


def should_index(relative: Path) -> bool:
    if relative == Path("index.html"):
        return False
    if relative.name in SKIP_NAMES:
        return False
    return not any(part in SKIP_PARTS for part in relative.parts)


def build(site: Path) -> list[dict[str, str]]:
    documents: list[dict[str, str]] = []
    for path in sorted(site.rglob("*.html")):
        relative = path.relative_to(site)
        if not should_index(relative):
            continue
        parser = PageParser()
        try:
            parser.feed(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as error:
            print(f"WARN: skipped {relative}: {error}", file=sys.stderr)
            continue

        title = clean(" ".join(parser.title)) or clean(relative.stem.replace("_", " "))
        headings = clean(" · ".join(dict.fromkeys(parser.headings)))
        body = clean(" ".join(parser.body))[:MAX_BODY_CHARS]
        documents.append(
            {
                "title": title,
                "url": page_url(relative),
                "category": category(relative),
                "headings": headings,
                "text": body,
            }
        )
    return documents


def main() -> int:
    site = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SITE
    documents = build(site)
    output = site / OUTPUT_NAME
    payload = json.dumps(documents, ensure_ascii=False, separators=(",", ":"))
    output.write_text(f"window.__SITE_SEARCH_INDEX__={payload};\n", encoding="utf-8")
    print(f"Indexed {len(documents)} HTML pages into {output} ({output.stat().st_size:,} bytes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
