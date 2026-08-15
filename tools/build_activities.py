#!/usr/bin/env python3
"""
Dotfit activity pages
=====================

    python3 tools/build_activities.py

Reads content/activities.json and writes one page per entry:

    site/activity-sinhagad-trek.html

Each page reuses the header, footer, navigation and SEO block from
site/activity.html, so it stays in step with the rest of the site
automatically. Pages for entries that were deleted from the JSON are
removed. site/activity.html itself is left alone — it is the
documentation page.

Every generated page carries: hero image, name, tagline, description,
details, highlights, a gallery pulled from the matching folder, related
activities, a WhatsApp button and the hashtag.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
TEMPLATE = os.path.join(SITE, "activity.html")
DATA = os.path.join(ROOT, "content", "activities.json")


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def chrome():
    """Everything outside <main> from the template page."""
    with open(TEMPLATE, encoding="utf-8") as fh:
        html = fh.read()
    head = html[: html.index("<main id=\"main\">")]
    tail = html[html.index("</main>") + len("</main>"):]
    return head, tail


def retitle(head, a):
    title = "%s | Dotfit Fitness" % a["title"]
    desc = a.get("summary", "")[:158]
    url = "https://dotfitfitness.in/activity-%s.html" % a["id"]
    head = re.sub(r"<title>.*?</title>", "<title>%s</title>" % esc(title), head, flags=re.S)
    head = re.sub(r'(<meta name="description" content=")[^"]*(")',
                  lambda m: m.group(1) + esc(desc) + m.group(2), head)
    head = re.sub(r'(<link rel="canonical" href=")[^"]*(")',
                  lambda m: m.group(1) + url + m.group(2), head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
                  lambda m: m.group(1) + esc(title) + m.group(2), head)
    head = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
                  lambda m: m.group(1) + esc(desc) + m.group(2), head)
    head = re.sub(r'(<meta property="og:url" content=")[^"]*(")',
                  lambda m: m.group(1) + url + m.group(2), head)
    return head


def body(a):
    hero = a.get("image")
    hero_html = (
        '<div class="story__hero rv"><img src="%s" alt="%s" width="1600" height="686" '
        'loading="eager" decoding="async"></div>' % (esc(hero), esc(a["title"]))
    ) if hero else '<div class="story__hero rv" role="img" aria-label="%s"></div>' % esc(a["title"])

    meta = " · ".join(filter(None, [a.get("date"), a.get("location")]))

    details = a.get("details") or []
    details_html = ""
    if details:
        details_html = (
            '    <h4>Details</h4>\n    <div class="tiles">%s</div>\n' %
            "".join('<div class="tile"><span class="tile__n">%s</span>'
                    '<h3>%s</h3></div>' % (esc(d["label"]), esc(d["value"]))
                    for d in details)
        )

    highlights = a.get("highlights") or []
    high_html = ""
    if highlights:
        high_html = (
            '    <h4>Highlights</h4>\n    <ul class="ticks">%s</ul>\n' %
            "".join("<li>%s</li>" % esc(h) for h in highlights)
        )

    related = a.get("related") or []
    rel_html = ""
    if related:
        rel_html = ('    <h4>Related activities</h4>\n    <div class="rel">%s</div>\n' %
                    "".join('<a href="%s">%s</a>' % (esc(u), esc(t)) for t, u in related))

    return """<main id="main">

<section class="phero">
  <div class="shell phero__in">
    <p class="crumb"><a href="index.html">Home</a> · <a href="activities.html">Activities</a> · {title}</p>
    <p class="eyebrow">{cat}</p>
    <h1 class="display">{title}</h1>
    <p class="lede" style="margin-top:1.25rem">{tagline}</p>
    {meta}
  </div>
</section>

<section class="band">
  <div class="shell">
    {hero}
    <div class="split split--wide">
      <div class="rv">
        <h4 style="font-family:var(--f-display);text-transform:uppercase;font-size:.76rem;letter-spacing:.14em;color:var(--muted);margin:0 0 .9rem">About the activity</h4>
        <p class="lede">{summary}</p>
        {body}
      </div>
      <div class="rv">
{details}{high}{rel}      </div>
    </div>
  </div>
</section>

<section class="band band--mist">
  <div class="shell">
    <div class="head rv">
      <p class="eyebrow">Gallery</p>
      <h2 class="display">Photo gallery</h2>
    </div>
    <div class="gwrap rv" data-gallery="{gal}" data-more="gallery.html#{gal}"></div>
    <p class="hashtag rv" style="margin-top:2.25rem">#stayfitwithdotfit</p>
  </div>
</section>

<section class="cta">
  <div class="shell">
    <h2 class="display">Come to the next one.</h2>
    <p>Dates, meeting points and what to bring — ask and we will send the details.</p>
    <div class="btnrow">
      <a class="btn btn--dark" href="#" data-wa>Chat on WhatsApp</a>
      <a class="btn btn--ghost" href="tel:+919822843366" data-tel>Call Dotfit</a>
      <a class="btn btn--ghost" href="activities.html">All activities</a>
    </div>
    <a class="hashtag" href="https://www.instagram.com/dotfit.fitness/" target="_blank" rel="noopener">#stayfitwithdotfit</a>
  </div>
</section>

<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Photo viewer">
  <button class="lb__btn lb__close" id="lbClose" aria-label="Close"><svg viewBox="0 0 24 24"><path d="M18 6 6 18M6 6l12 12"/></svg></button>
  <button class="lb__btn lb__prev" id="lbPrev" aria-label="Previous photo"><svg viewBox="0 0 24 24"><path d="M15 18 9 12l6-6"/></svg></button>
  <button class="lb__btn lb__next" id="lbNext" aria-label="Next photo"><svg viewBox="0 0 24 24"><path d="m9 6 6 6-6 6"/></svg></button>
  <img id="lbImg" src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" alt="">
  <p class="lb__cap" id="lbCap"></p>
</div>

</main>""".format(
        title=esc(a["title"]),
        cat=esc(a.get("category", "Activity").replace("-", " ").title()),
        tagline=esc(a.get("tagline") or a.get("summary", "")),
        meta=('<p class="chips"><span class="chip">%s</span></p>' % esc(meta)) if meta else "",
        hero=hero_html,
        summary=esc(a.get("summary", "")),
        body="".join("<p>%s</p>" % esc(p) for p in (a.get("body") or [])),
        details=details_html, high=high_html, rel=rel_html,
        gal=esc(a.get("category", "events")),
    )


def main():
    if not os.path.exists(DATA):
        sys.exit("No content/activities.json — nothing to generate.")
    with open(DATA, encoding="utf-8") as fh:
        activities = json.load(fh).get("activities", [])

    head, tail = chrome()
    wanted = set()

    for a in activities:
        if not a.get("id") or not a.get("title"):
            print("  ! entry without an id or title — skipped")
            continue
        name = "activity-%s.html" % a["id"]
        wanted.add(name)
        with open(os.path.join(SITE, name), "w", encoding="utf-8") as fh:
            fh.write(retitle(head, a) + body(a) + tail)
        print("  wrote  %s" % name)

    for f in os.listdir(SITE):
        if f.startswith("activity-") and f.endswith(".html") and f not in wanted:
            os.remove(os.path.join(SITE, f))
            print("  removed  %s  (no longer in activities.json)" % f)

    if not activities:
        print("  activities.json is empty — no pages generated yet.")
    else:
        print("\n%d activity pages. Link them from activities.html." % len(wanted))


if __name__ == "__main__":
    main()
