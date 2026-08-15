#!/usr/bin/env python3
"""
Dotfit section builder
======================

    python3 tools/build_sections.py

Writes the activity-selector markup and the gallery blocks into the pages
inside site/. Safe to run as many times as you like — every block it
writes is fenced with an HTML comment marker and replaced in place, so a
second run updates rather than duplicates.

What it touches
---------------
  every page      the two extra <script> tags, and the lightbox markup
  services.html   the activity selector, generated from content/services.json
  gallery.html    the filterable all-categories gallery
  a few pages     a single-category gallery band before the closing CTA

What it does not touch
----------------------
Everything else. Headings, copy, navigation and SEO tags in the existing
pages are left exactly as they are.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

BEGIN = "<!-- DOTFIT:%s BEGIN -->"
END = "<!-- DOTFIT:%s END -->"

# Which pages get a single-category gallery band, and which category.
PAGE_GALLERIES = {
    "trekking.html": ("trekking", "Trek gallery", "Every trek gets photographed."),
    "dpl.html": ("dpl", "DPL gallery", "Matches, teams and the celebrations after."),
    "fitness-challenges.html": ("fitness-challenges", "Challenge gallery", "The people who showed up and finished."),
    "group-fitness.html": ("yoga", "Class gallery", "Yoga, Zumba, cycling and the rest of the floor."),
    "sports-performance.html": ("sports-training", "Sports gallery", "Athletes training for their own sport."),
    "nutrition.html": ("nutrition", "Nutrition gallery", "Consults, plans and the shop counter."),
    "sports-wear.html": ("sports-wear", "Sports wear gallery", "What is on the rack right now."),
    "activities.html": ("all", "Activity gallery", "Treks, events, challenges and community days."),
    "training.html": ("personal-training", "Training gallery", "Sessions on the floor, as they happen."),
    "index.html": ("all", "Latest from<br>the floor.", "Training, sport, treks and everything the community shows up for."),
}

LIGHTBOX = """<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Photo viewer">
  <button class="lb__btn lb__close" id="lbClose" aria-label="Close"><svg viewBox="0 0 24 24"><path d="M18 6 6 18M6 6l12 12"/></svg></button>
  <button class="lb__btn lb__prev" id="lbPrev" aria-label="Previous photo"><svg viewBox="0 0 24 24"><path d="M15 18 9 12l6-6"/></svg></button>
  <button class="lb__btn lb__next" id="lbNext" aria-label="Next photo"><svg viewBox="0 0 24 24"><path d="m9 6 6 6-6 6"/></svg></button>
  <img id="lbImg" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" alt="">
  <p class="lb__cap" id="lbCap"></p>
</div>"""

SCRIPTS = """<script src="assets/js/gallery-manifest.js"></script>
<script src="assets/js/dotfit-modules.js"></script>"""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def fence(name, body):
    return BEGIN % name + "\n" + body + "\n" + END % name


def put(html, name, body):
    """Insert or replace a fenced block. Returns (html, was_present)."""
    block = fence(name, body)
    pattern = re.compile(re.escape(BEGIN % name) + r".*?" + re.escape(END % name),
                         re.S)
    if pattern.search(html):
        return pattern.sub(lambda _: block, html), True
    return html, False


# ── activity selector ────────────────────────────────────────────────

def build_selector(activities):
    tabs, panels = [], []
    for i, a in enumerate(activities):
        key = a["key"]
        tabs.append(
            '<button type="button" class="svcnav__item" role="tab"'
            ' id="svctab-{k}" aria-controls="svcpanel-{k}"'
            ' aria-selected="{sel}" tabindex="{ti}" data-svc="{k}">'
            '<span class="svcnav__name" data-text="{n}">{n}</span>'
            '<span class="svcnav__tag">{t}</span>'
            "</button>".format(k=key, n=esc(a["name"]), t=esc(a["tagline"]),
                               sel="true" if i == 0 else "false",
                               ti="0" if i == 0 else "-1")
        )

        benefits = "".join("<li>%s</li>" % esc(b) for b in a.get("benefits", []))
        related = "".join('<a href="%s">%s</a>' % (esc(u), esc(t))
                          for t, u in a.get("related", []))

        panels.append(
            '<section class="svcpanel" role="tabpanel" id="svcpanel-{k}"'
            ' aria-labelledby="svctab-{k}" data-svc="{k}"{hid}>\n'
            '  <div class="svcpanel__media" style="background-image:var({slot}),var(--dots)"'
            ' role="img" aria-label="{n}"></div>\n'
            '  <h3 class="svcpanel__name">{n}</h3>\n'
            '  <p class="svcpanel__tag">{t}</p>\n'
            '  <p class="svcpanel__body">{b}</p>\n'
            "{ben}"
            '  <h4>Related at Dotfit</h4>\n  <div class="rel">{rel}</div>\n'
            '  <h4>{n} gallery</h4>\n'
            '  <div data-gallery="{k}" data-limit="4" data-cols="4"'
            ' data-more="gallery.html#{k}"></div>\n'
            '  <div class="btnrow" style="margin-top:2rem">\n'
            '    <a class="btn btn--wa" href="#" data-wa>Ask about {n} on WhatsApp</a>\n'
            '    <a class="btn btn--ghost" href="join.html">Join Dotfit</a>\n'
            "  </div>\n"
            "</section>".format(
                k=key, n=esc(a["name"]), t=esc(a["tagline"]), b=esc(a["body"]),
                slot=a.get("slot", "--img-group"),
                ben=('  <h4>What it gives you</h4>\n  <ul class="ticks">%s</ul>\n'
                     % benefits) if benefits else "",
                rel=related,
                hid="" if i == 0 else " hidden",
            )
        )

    return (
        '<section class="band band--mist">\n  <div class="shell">\n'
        '    <div class="head rv">\n'
        '      <p class="eyebrow">Pick one</p>\n'
        '      <h2 class="display">Choose an activity.<br>See what it involves.</h2>\n'
        '      <p class="lede">Every activity on this list has its own description, its own '
        "benefits and its own photographs. Select one to read it.</p>\n"
        "    </div>\n"
        '    <div class="svcx rv" id="activitySelector">\n'
        '      <div class="svcnav" role="tablist" aria-label="Dotfit activities" '
        'aria-orientation="vertical">\n        ' + "\n        ".join(tabs) + "\n      </div>\n"
        '      <div class="svcpanels">\n        ' + "\n        ".join(panels) + "\n      </div>\n"
        "    </div>\n  </div>\n</section>"
    )


def gallery_band(cat, heading, lede, filters=False, limit=8):
    """heading may contain a <br>; it is written by this file, not by users."""
    return (
        '<section class="band">\n  <div class="shell">\n'
        '    <div class="head rv">\n'
        '      <p class="eyebrow">Gallery</p>\n'
        '      <h2 class="display">%s</h2>\n'
        '      <p class="lede">%s</p>\n'
        "    </div>\n"
        '    <div class="gwrap rv" data-gallery="%s" data-limit="%d"%s></div>\n'
        '    <p class="hashtag rv" style="margin-top:2.25rem">#stayfitwithdotfit</p>\n'
        "  </div>\n</section>" % (
            heading, esc(lede), cat, limit,
            ' data-filters="true"' if filters else
            ' data-more="gallery.html#%s"' % cat if cat != "all" else "",
        )
    )


def main():
    with open(os.path.join(ROOT, "content", "services.json"), encoding="utf-8") as fh:
        data = json.load(fh)

    pages = sorted(f for f in os.listdir(SITE) if f.endswith(".html"))
    if not pages:
        sys.exit("No pages found in %s" % SITE)

    for page in pages:
        path = os.path.join(SITE, page)
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        before = html

        # 1. scripts, on every page, right after the existing one
        html, found = put(html, "SCRIPTS", SCRIPTS)
        if not found:
            if '<script src="assets/js/dotfit.js"></script>' not in html:
                print("  ! %s has no dotfit.js tag — skipped" % page)
                continue
            html = html.replace(
                '<script src="assets/js/dotfit.js"></script>',
                '<script src="assets/js/dotfit.js"></script>\n' + fence("SCRIPTS", SCRIPTS),
                1,
            )

        # 2. lightbox, on every page, so any gallery block works anywhere
        if 'id="lightbox"' not in html:
            html, found = put(html, "LIGHTBOX", LIGHTBOX)
            if not found and "</main>" in html:
                html = html.replace("</main>", fence("LIGHTBOX", LIGHTBOX) + "\n\n</main>", 1)

        # 3. per-page blocks
        if page == "services.html":
            block = build_selector(data["activities"])
            html, found = put(html, "SELECTOR", block)
            if not found:
                html = html.replace('<section class="cta">',
                                    fence("SELECTOR", block) + '\n\n<section class="cta">', 1)

        elif page == "gallery.html":
            block = gallery_band(
                "all", "Every session.<br>Every summit.",
                "Filter by activity. Click any photo to open it full size.",
                filters=True, limit=24)
            html, found = put(html, "GALLERY", block)
            if not found:
                # replace the original placeholder band, keep everything else
                old = re.search(
                    r'<section class="band">\s*<div class="shell">\s*'
                    r'<div class="filters rv" data-filterset="galleryGrid".*?</section>',
                    html, re.S)
                if old:
                    html = html[:old.start()] + fence("GALLERY", block) + html[old.end():]
                else:
                    html = html.replace('<section class="cta">',
                                        fence("GALLERY", block) + '\n\n<section class="cta">', 1)

        elif page in PAGE_GALLERIES:
            cat, heading, lede = PAGE_GALLERIES[page]
            block = gallery_band(cat, heading, lede, filters=(cat == "all"))
            html, found = put(html, "GALLERY", block)
            if not found:
                html = html.replace('<section class="cta">',
                                    fence("GALLERY", block) + '\n\n<section class="cta">', 1)

        if html != before:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(html)
            print("  updated  %s" % page)
        else:
            print("  no change %s" % page)

    print("\nDone. Now run  python3 tools/scan_gallery.py  if you have added photos.")


if __name__ == "__main__":
    main()
