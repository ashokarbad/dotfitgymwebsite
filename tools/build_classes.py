#!/usr/bin/env python3
"""
Dotfit classes builder
=======================

    python3 tools/build_classes.py

Reads content/classes.json and writes the full schedule into
docs/classes.html (inside the DOTFIT:CLASSES markers), the category and
day filter pills, and a short preview into docs/index.html (inside
DOTFIT:CLASSES-PREVIEW). Safe to re-run.

Add a class or a batch: edit content/classes.json, run this script.
The Category / Day / Morning-Evening filters on classes.html read the
data straight off each card — no filter list to maintain separately.
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "docs")
DATA = os.path.join(ROOT, "content", "classes.json")

BEGIN = "<!-- DOTFIT:%s BEGIN -->"
END = "<!-- DOTFIT:%s END -->"

DAY_ORDER = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DAY_LABEL = {"mon": "Monday", "tue": "Tuesday", "wed": "Wednesday", "thu": "Thursday",
             "fri": "Friday", "sat": "Saturday", "sun": "Sunday"}
DAY_SHORT = {"mon": "Mon", "tue": "Tue", "wed": "Wed", "thu": "Thu",
             "fri": "Fri", "sat": "Sat", "sun": "Sun"}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def put(html, name, body):
    block = BEGIN % name + "\n" + body + "\n" + END % name
    pattern = re.compile(re.escape(BEGIN % name) + r".*?" + re.escape(END % name), re.S)
    if pattern.search(html):
        return pattern.sub(lambda _: block, html), True
    return html, False


def batch_html(b):
    days_str = " • ".join(DAY_LABEL[d] for d in b["days"])
    return (
        '  <div class="batch" data-batch="%s" data-days="%s">\n'
        '    <p class="batch__label">%s</p>\n'
        '    <p class="batch__days">%s</p>\n'
        '    <p class="batch__time">%s – %s</p>\n'
        '    <p class="batch__instr">Instructor: <span>%s</span></p>\n'
        "  </div>" % (
            esc(b["time_of_day"]), " ".join(b["days"]),
            esc(b["label"]), esc(days_str), esc(b["start"]), esc(b["end"]),
            esc(b["instructor"]),
        )
    )


def class_card(c):
    all_days = sorted({d for b in c["batches"] for d in b["days"]}, key=DAY_ORDER.index)
    batches = "\n".join(batch_html(b) for b in c["batches"])
    return (
        '<article class="classcard rv" data-cat="%s" data-days="%s">\n'
        '  <div class="classcard__top">\n'
        "    <h3>%s</h3>\n"
        '    <span class="classcard__level">%s</span>\n'
        "  </div>\n"
        '  <div class="classcard__batches">\n'
        "%s\n"
        "  </div>\n"
        "</article>" % (
            esc(c["category"]), " ".join(all_days),
            esc(c["name"]), esc(c["level"]), batches,
        )
    )


def filter_pills(categories):
    cat_pills = ['<button type="button" class="filter" data-classcat="all" aria-pressed="true">All classes</button>']
    cat_pills += ['<button type="button" class="filter" data-classcat="%s" aria-pressed="false">%s</button>'
                  % (esc(k), esc(v)) for k, v in categories]

    day_pills = ['<button type="button" class="filter" data-classday="all" aria-pressed="true">All days</button>']
    day_pills += ['<button type="button" class="filter" data-classday="%s" aria-pressed="false">%s</button>'
                  % (d, DAY_SHORT[d]) for d in DAY_ORDER]

    time_pills = (
        '<button type="button" class="filter" data-classtime="all" aria-pressed="true">Any time</button>'
        '<button type="button" class="filter" data-classtime="morning" aria-pressed="false">Morning</button>'
        '<button type="button" class="filter" data-classtime="evening" aria-pressed="false">Evening</button>'
    )

    return (
        '<div class="sched__filters">\n'
        '  <div class="sched__filterrow"><span>Class</span><div class="filters" id="classCatFilters">%s</div></div>\n'
        '  <div class="sched__filterrow"><span>Day</span><div class="filters" id="classDayFilters">%s</div></div>\n'
        '  <div class="sched__filterrow"><span>Batch</span><div class="filters" id="classTimeFilters">%s</div></div>\n'
        "</div>" % ("".join(cat_pills), "".join(day_pills), time_pills)
    )


def preview_card(c):
    b = c["batches"][0]
    days_str = " • ".join(DAY_SHORT[d] for d in b["days"])
    return (
        '<article class="classcard rv"><div class="classcard__top"><h3>%s</h3>'
        '<span class="classcard__level">%s</span></div>'
        '<div class="classcard__batches"><div class="batch">'
        '<p class="batch__label">%s</p><p class="batch__days">%s</p>'
        '<p class="batch__time">%s</p></div></div></article>' % (
            esc(c["name"]), esc(b["time_of_day"].title()),
            esc(b["label"]), esc(days_str), esc(b["start"]),
        )
    )


def main():
    with open(DATA, encoding="utf-8") as fh:
        data = json.load(fh)
    classes = data["classes"]
    categories = data["categories"]

    # classes.html — filters + full grid
    grid = "\n".join(class_card(c) for c in classes)
    body = filter_pills(categories) + '\n<div class="classgrid" id="classGrid">\n' + grid + \
           '\n<p class="sched__empty small" id="classEmpty" hidden>No classes match those filters. ' \
           'Try clearing one.</p>\n</div>'

    path = os.path.join(SITE, "classes.html")
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    html, found = put(html, "CLASSES", body)
    if not found:
        raise SystemExit("No DOTFIT:CLASSES markers in docs/classes.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("  classes.html   %d classes, %d categories" % (len(classes), len(categories)))

    # index.html — short preview (first 3 classes, first batch only)
    preview = classes[:3]
    if preview:
        preview_grid = '<div class="classgrid rv">\n' + "\n".join(preview_card(c) for c in preview) + "\n</div>"
        path = os.path.join(SITE, "index.html")
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        html, found = put(html, "CLASSES-PREVIEW", preview_grid)
        if found:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(html)
            print("  index.html     %d preview classes" % len(preview))
        else:
            print("  ! no DOTFIT:CLASSES-PREVIEW markers in index.html — skipped")


if __name__ == "__main__":
    main()
