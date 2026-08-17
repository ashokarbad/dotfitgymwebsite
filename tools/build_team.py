#!/usr/bin/env python3
"""
Dotfit team builder
====================

    python3 tools/build_team.py

Reads content/team.json and writes the team grid into docs/team.html
(inside the DOTFIT:TEAM markers) and a 3-4 person preview into
docs/index.html (inside DOTFIT:TEAM-PREVIEW). Safe to re-run — both
blocks are replaced in place, nothing else on either page is touched.

Add a team member: add an entry to content/team.json, run this script.
Remove one: delete the entry, run this script.
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "docs")
DATA = os.path.join(ROOT, "content", "team.json")

BEGIN = "<!-- DOTFIT:%s BEGIN -->"
END = "<!-- DOTFIT:%s END -->"


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def put(html, name, body):
    block = BEGIN % name + "\n" + body + "\n" + END % name
    pattern = re.compile(re.escape(BEGIN % name) + r".*?" + re.escape(END % name), re.S)
    if pattern.search(html):
        return pattern.sub(lambda _: block, html), True
    return html, False


def card(m, compact=False):
    tags = ""
    spec = m.get("specialization") or []
    if spec and not compact:
        tags = ('<div class="team__tags">' +
                "".join('<span class="team__tag">%s</span>' % esc(s) for s in spec) +
                "</div>")
    return (
        '<article class="team__card">\n'
        '  <div class="team__photo" style="background-image:url(\'%s\'),var(--dots)">\n'
        '    <img src="%s" alt="%s, %s at Dotfit Fitness" loading="lazy" decoding="async"\n'
        '         onerror="this.remove()">\n'
        '  </div>\n'
        '  <div class="team__body">\n'
        '    <h3 class="team__name">%s</h3>\n'
        '    <p class="team__role">%s</p>\n'
        '    <p class="team__bio">%s</p>\n'
        "    %s\n"
        "  </div>\n"
        "</article>" % (
            esc(m["photo"]), esc(m["photo"]), esc(m["name"]), esc(m["role"]),
            esc(m["name"]), esc(m["role"]), esc(m["bio"]), tags,
        )
    )


def main():
    with open(DATA, encoding="utf-8") as fh:
        data = json.load(fh)
    members = data["members"]
    featured = [m for m in members if m.get("featured")][:4]

    # team.html — full roster
    team_grid = "\n".join(card(m) for m in members)
    path = os.path.join(SITE, "team.html")
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    html, found = put(html, "TEAM", '<div class="team rv">\n' + team_grid + "\n</div>")
    if not found:
        raise SystemExit("No DOTFIT:TEAM markers in docs/team.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("  team.html      %d members" % len(members))

    # index.html — featured preview
    if featured:
        preview_grid = "\n".join(card(m, compact=True) for m in featured)
        path = os.path.join(SITE, "index.html")
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        html, found = put(html, "TEAM-PREVIEW", '<div class="team team--preview rv">\n' + preview_grid + "\n</div>")
        if found:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(html)
            print("  index.html     %d featured" % len(featured))
        else:
            print("  ! no DOTFIT:TEAM-PREVIEW markers in index.html — skipped")


if __name__ == "__main__":
    main()
