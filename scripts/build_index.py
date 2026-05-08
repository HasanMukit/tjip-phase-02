#!/usr/bin/env python3
"""Generate search-index.json for the TJIP Phase 02 site.

Walks the repo, parses every served HTML page with stdlib html.parser, and
writes a JSON array of search records to search-index.json at the repo root.

Run from the repo root: `python3 scripts/build_index.py`
"""

import json
import re
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

THEME_DIRS = (
    "distribution", "execution", "hardware", "interfaces", "performance",
    "reliability", "craft", "case-studies",
)
ROOT_PAGES = ("index.html", "classes.html", "glossary.html")

TITLE_SUFFIX = re.compile(r"\s*[—–-]\s*TJIP Phase 02\s*$")
WHITESPACE = re.compile(r"\s+")

THEME_LABELS = {
    "distribution": "Distribution",
    "execution":    "Execution",
    "hardware":     "Hardware",
    "interfaces":   "Interfaces",
    "performance":  "Performance",
    "reliability":  "Reliability",
    "craft":        "Craft",
    "case-studies": "Case Studies",
}

BODY_EXCLUDE_CLASSES = {
    "site-nav", "site-footer",
    "toc", "terms-block", "related-topics",
    "site-search", "site-search-results",
}
BODY_EXCLUDE_TAGS = {"script", "style", "svg", "nav", "footer"}


def squash(text: str) -> str:
    return WHITESPACE.sub(" ", text).strip()


class PageParser(HTMLParser):
    """Single-pass extractor for title, h1, deck, headings, lede, and body text.

    Uses two parallel state machines:

    - `_capture` collects text for short-lived targets (title, h1, h2, h3,
      deck, lede). Only one capture is active at a time.
    - `_body_depth` tracks whether the parser is currently inside the article
      body. Body collection skips known cross-page chrome (nav/footer/toc/
      terms-block/related-topics) and SVG figure labels.

    `_skip_depth` lets either machine drop a subtree (e.g. <span class="num">
    inside an h2, or .toc inside the body).
    """

    BODY_ROOT_CLASSES = ("container", "theme-page", "themes-section",
                         "classes-section", "glossary-page", "hero")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.h1 = ""
        self.deck = ""
        self.lede = ""
        self.headings: list[str] = []
        self.body_chunks: list[str] = []

        self._capture = None
        self._cap_buf: list[str] = []
        self._cap_skip = 0

        self._body_depth = 0
        self._body_skip = 0

    # ---------- helpers ----------

    def _start(self, kind: str):
        self._capture = kind
        self._cap_buf = []
        self._cap_skip = 0

    def _finish(self):
        text = squash("".join(self._cap_buf))
        kind = self._capture
        self._capture = None
        self._cap_buf = []
        self._cap_skip = 0
        return kind, text

    @staticmethod
    def _classes(attrs: dict) -> set:
        return set(attrs.get("class", "").split())

    # ---------- HTMLParser hooks ----------

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        cls = self._classes(attrs_d)

        # If we're skipping a subtree of the body, just track depth so we can
        # find the matching close.
        if self._body_skip > 0:
            self._body_skip += 1
            return

        # Skip whole subtrees that pollute body text.
        if self._body_depth > 0 and (
            tag in BODY_EXCLUDE_TAGS or (cls & BODY_EXCLUDE_CLASSES)
        ):
            self._body_skip = 1
            return

        # Capture-mode skip (e.g. <span class="num"> inside an h2).
        if self._capture is not None and self._cap_skip > 0:
            if tag == "span":
                self._cap_skip += 1
            return

        # Enter body when we hit one of the known content roots. Accept both
        # <div class="container"> on topic pages and <section class="hero"|...>
        # on the homepage / theme indexes / glossary.
        if (self._body_depth > 0
                or (tag in ("div", "section")
                    and (cls & set(self.BODY_ROOT_CLASSES)))):
            self._body_depth += 1

        # Start a new short-lived capture if we're idle.
        if self._capture is None:
            if tag == "title":
                self._start("title")
            elif tag == "h1" and not self.h1:
                self._start("h1")
            elif tag in ("h2", "h3"):
                self._start("h2")  # both feed into headings list
            elif tag == "p":
                if not self.deck and (cls & {"deck", "hero-deck"}):
                    self._start("deck")
                elif not self.lede and "lede" in cls:
                    self._start("lede")
            return

        # Inside an h2, skip the leading <span class="num">..</span>.
        if (self._capture == "h2" and tag == "span" and "num" in cls):
            self._cap_skip = 1

    def handle_endtag(self, tag):
        # Body subtree-skip unwind first.
        if self._body_skip > 0:
            self._body_skip -= 1
            return

        if self._capture is not None and self._cap_skip > 0:
            if tag == "span":
                self._cap_skip -= 1
            return

        if self._capture is not None:
            ends = {
                ("title", "title"),
                ("h1",    "h1"),
                ("h2",    "h2"),
                ("h3",    "h2"),
                ("p",     "deck"),
                ("p",     "lede"),
            }
            if (tag, self._capture) in ends:
                kind, text = self._finish()
                if kind == "title":
                    self.title = TITLE_SUFFIX.sub("", text)
                elif kind == "h1":
                    self.h1 = text
                elif kind == "h2":
                    if text:
                        self.headings.append(text)
                elif kind == "deck":
                    self.deck = text
                elif kind == "lede":
                    self.lede = text

        # Exit body region last.
        if self._body_depth > 0:
            self._body_depth -= 1

    def handle_data(self, data):
        if not data:
            return

        if self._capture is not None and self._cap_skip == 0:
            self._cap_buf.append(data)

        if self._body_depth > 0 and self._body_skip == 0:
            # Avoid appending pure whitespace runs that bloat the body string.
            if data.strip():
                self.body_chunks.append(data)


def discover_pages():
    pages = []
    for name in ROOT_PAGES:
        p = REPO_ROOT / name
        if p.is_file():
            pages.append(p)
    for theme in THEME_DIRS:
        d = REPO_ROOT / theme
        if not d.is_dir():
            continue
        pages.extend(sorted(d.glob("*.html")))
    return pages


def theme_for(path: Path) -> str:
    if path.parent == REPO_ROOT:
        return "Site"
    return THEME_LABELS.get(path.parent.name, path.parent.name.title())


def index_page(path: Path) -> dict:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()

    rel = path.relative_to(REPO_ROOT).as_posix()
    body = squash(" ".join(parser.body_chunks))

    return {
        "url":      rel,
        "title":    parser.title or parser.h1 or rel,
        "h1":       parser.h1,
        "theme":    theme_for(path),
        "deck":     parser.deck,
        "lede":     parser.lede,
        "headings": parser.headings,
        "body":     body,
    }


def main():
    pages = discover_pages()
    index = [index_page(p) for p in pages]
    out = REPO_ROOT / "search-index.json"
    out.write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    total_kb = out.stat().st_size / 1024
    print(f"Wrote {out.name}: {len(index)} entries, {total_kb:.1f} KB")


if __name__ == "__main__":
    main()
