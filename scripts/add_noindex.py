#!/usr/bin/env python3
"""Ensure every HTML page in the published archive opts out of indexing."""

from __future__ import annotations

import re
import sys
from pathlib import Path


DEFAULT_SITE = Path("site")
NOINDEX_META = '<meta name="robots" content="noindex, nofollow, noarchive">'
HEAD_RE = re.compile(r"<head\b[^>]*>", re.IGNORECASE)
ROBOTS_META_RE = re.compile(
    r"""<meta\b[^>]*\bname\s*=\s*(["'])robots\1[^>]*>""",
    re.IGNORECASE,
)


def update_page(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")

    if ROBOTS_META_RE.search(content):
        updated = ROBOTS_META_RE.sub(NOINDEX_META, content)
    else:
        updated, replacements = HEAD_RE.subn(
            lambda match: f"{match.group(0)}\n{NOINDEX_META}",
            content,
            count=1,
        )
        if replacements == 0:
            print(f"WARN: missing <head> element, skipped: {path}")
            return False

    if updated == content:
        return False

    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    site = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SITE
    pages = sorted(site.rglob("*.html"))
    changed = 0

    for page in pages:
        changed += update_page(page)

    print(f"Checked {len(pages)} HTML pages; updated {changed}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
