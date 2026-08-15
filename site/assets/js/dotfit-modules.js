/* ═══════════════════════════════════════════════════════════════
   DOTFIT FITNESS — activity selector + gallery system
   Loads after dotfit.js. Reads photo data from gallery-manifest.js.

   You should not need to edit this file. Photos come from the
   manifest, which tools/scan_gallery.py regenerates from the
   folders inside images/gallery/.
   ═══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var G  = window.DOTFIT_GALLERY || { order: [], labels: {}, categories: {} };

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
  function label(cat) { return G.labels[cat] || cat.replace(/-/g, ' '); }

  /* ─────────────────────────────────────────────────────────────
     1. GALLERY
     Markup:
       <div data-gallery="all"  data-filters="true" data-limit="24"></div>
       <div data-gallery="yoga" data-limit="8" data-more="gallery.html#yoga"></div>
     ───────────────────────────────────────────────────────────── */

  function photosFor(cat) {
    if (cat === 'all') {
      var out = [];
      (G.order || Object.keys(G.categories)).forEach(function (c) {
        (G.categories[c] || []).forEach(function (p) {
          out.push(Object.assign({ category: c }, p));
        });
      });
      return out;
    }
    return (G.categories[cat] || []).map(function (p) {
      return Object.assign({ category: cat }, p);
    });
  }

  function nonEmpty() {
    return (G.order || Object.keys(G.categories)).filter(function (c) {
      return (G.categories[c] || []).length > 0;
    });
  }

  function cardHTML(p, scoped) {
    var title = p.title || label(p.category);
    var cat   = label(p.category);
    /* A filename like yoga-01.jpg gives a title of "Yoga", which is just
       the category again. When that happens the title is dropped rather
       than printed twice. The category is also dropped when the whole
       gallery is already one category. */
    var generic = title.toLowerCase() === cat.toLowerCase();
    var showCat = !scoped && !generic;
    var meta  = [p.date, showCat ? cat : ''].filter(Boolean).join(' · ');
    var thumb = p.thumb || p.src;
    var srcset = p.thumb && p.thumb !== p.src
      ? ' srcset="' + esc(p.thumb) + ' 480w, ' + esc(p.src) + ' 1600w"' +
        ' sizes="(max-width:400px) 92vw, (max-width:760px) 46vw, (max-width:1024px) 31vw, 23vw"'
      : '';
    var dims = (p.w && p.h) ? ' width="' + p.w + '" height="' + p.h + '"' : '';
    var alt  = p.caption || title;

    return '<button type="button" class="gcard gitem"' +
      ' data-full="' + esc(p.src) + '"' +
      (generic ? '' : ' data-title="' + esc(title) + '"') +
      ' data-caption="' + esc(p.caption || '') + '"' +
      ' data-date="' + esc(p.date || '') + '"' +
      ' data-category="' + esc(label(p.category)) + '"' +
      ' data-cat="' + esc(p.category) + '"' +
      ' aria-label="Open photo: ' + esc(title) + '">' +
        '<span class="gcard__img">' +
          '<img src="' + esc(thumb) + '"' + srcset + dims +
          ' alt="' + esc(alt) + '" loading="lazy" decoding="async">' +
          '<span class="gcard__badge">' + esc(label(p.category)) + '</span>' +
        '</span>' +
        '<span class="gcard__cap">' +
          '<span class="gcard__t">' + esc(title) + '</span>' +
          (meta ? '<span class="gcard__m">' + esc(meta) + '</span>' : '') +
        '</span>' +
      '</button>';
  }

  function emptyHTML(cat, adminHint) {
    var where = cat === 'all' ? 'images/gallery/' : 'images/gallery/' + cat + '/';
    return '<div class="empty empty--slim">' +
      '<!-- FOR THE DOTFIT TEAM: drop photos into ' + where +
      ' then run  python3 tools/scan_gallery.py -->' +
      '<div class="empty__dot" aria-hidden="true"></div>' +
      '<h3>Photos coming soon</h3>' +
      '<p>' + (adminHint
        ? 'Add images to <code>' + esc(where) + '</code> and run the gallery script.'
        : 'This one has not been photographed yet. There is always a next session.') +
      '</p></div>';
  }

  function buildGallery(host) {
    var start   = host.dataset.gallery || 'all';
    var limit   = parseInt(host.dataset.limit || '0', 10) || 0;
    var pills   = host.dataset.filters === 'true';
    var admin   = /^(file:|localhost|127\.)/.test(location.protocol + location.hostname);
    var current = start;
    var shown   = limit;

    var bar  = document.createElement('div');
    bar.className = 'gfilters';
    bar.setAttribute('role', 'group');
    bar.setAttribute('aria-label', 'Filter photos by activity');

    var grid = document.createElement('div');
    var more = document.createElement('div');
    more.className = 'gmore';

    function render() {
      var all = photosFor(current);
      var list = shown ? all.slice(0, shown) : all;

      if (!all.length) {
        grid.className = '';
        grid.innerHTML = emptyHTML(current, admin);
        more.innerHTML = '';
      } else {
        grid.className = 'ggrid';
        if (host.dataset.cols) grid.style.setProperty('--gcols', host.dataset.cols);
        var scoped = current !== 'all';
        grid.innerHTML = list.map(function (p) { return cardHTML(p, scoped); }).join('');
        more.innerHTML = (shown && all.length > shown)
          ? '<button type="button" class="btn btn--ghost btn--sm" data-gmore>' +
            'Show more photos (' + (all.length - shown) + ')</button>'
          : (host.dataset.more
              ? '<a class="btn btn--ghost btn--sm" href="' + esc(host.dataset.more) + '">' +
                'See the full ' + esc(label(current)) + ' gallery</a>'
              : '');
      }
      if (window.DOTFIT_LB) window.DOTFIT_LB.refresh();
    }

    if (pills) {
      var cats = ['all'].concat(nonEmpty());
      /* Only categories that actually hold photos get a pill. An empty
         filter that returns nothing is worse than no filter at all. */
      bar.innerHTML = cats.map(function (c) {
        return '<button type="button" class="filter" data-gfilter="' + esc(c) + '"' +
               ' aria-pressed="' + (c === current) + '">' +
               esc(c === 'all' ? 'All' : label(c)) + '</button>';
      }).join('');
      if (cats.length > 1) host.appendChild(bar);
    }

    host.appendChild(grid);
    host.appendChild(more);
    render();

    bar.addEventListener('click', function (e) {
      var b = e.target.closest('[data-gfilter]');
      if (!b) return;
      current = b.dataset.gfilter;
      shown = limit;
      $$('[data-gfilter]', bar).forEach(function (x) {
        x.setAttribute('aria-pressed', String(x === b));
      });
      if (history.replaceState) {
        history.replaceState(null, '', current === 'all' ? location.pathname : '#' + current);
      }
      render();
    });

    more.addEventListener('click', function (e) {
      if (!e.target.closest('[data-gmore]')) return;
      shown = 0;
      render();
    });

    /* gallery.html#yoga opens on that category */
    if (pills) {
      var h = location.hash.replace('#', '');
      if (h && G.categories[h] && (G.categories[h] || []).length) {
        var btn = $('[data-gfilter="' + h + '"]', bar);
        if (btn) btn.click();
      }
    }
  }

  $$('[data-gallery]').forEach(buildGallery);

  /* ─────────────────────────────────────────────────────────────
     2. ACTIVITY SELECTOR
     The panels are already in the HTML — this only handles
     selection, keyboard navigation and the address bar.
     ───────────────────────────────────────────────────────────── */

  $$('.svcx').forEach(function (root) {
    var tabs   = $$('.svcnav__item', root);
    var panels = $$('.svcpanel', root);
    if (!tabs.length) return;

    function select(key, focus, push) {
      tabs.forEach(function (t) {
        var on = t.dataset.svc === key;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        if (on && focus) t.focus();
        if (on && root.classList.contains('is-scrolly')) {
          t.scrollIntoView({ block: 'nearest', inline: 'center', behavior: 'smooth' });
        }
      });
      panels.forEach(function (p) { p.hidden = p.dataset.svc !== key; });
      if (push && history.replaceState) history.replaceState(null, '', '#svc-' + key);
      if (window.DOTFIT_LB) window.DOTFIT_LB.refresh();
    }

    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(t.dataset.svc, false, true); });
      t.addEventListener('keydown', function (e) {
        var n = null;
        if (e.key === 'ArrowDown' || e.key === 'ArrowRight') n = (i + 1) % tabs.length;
        if (e.key === 'ArrowUp'   || e.key === 'ArrowLeft')  n = (i - 1 + tabs.length) % tabs.length;
        if (e.key === 'Home') n = 0;
        if (e.key === 'End')  n = tabs.length - 1;
        if (n === null) return;
        e.preventDefault();
        select(tabs[n].dataset.svc, true, true);
      });
    });

    if (matchMedia('(max-width:900px)').matches) root.classList.add('is-scrolly');

    var hash = (location.hash.match(/^#svc-(.+)$/) || [])[1];
    var first = tabs[0].dataset.svc;
    var valid = hash && tabs.some(function (t) { return t.dataset.svc === hash; });
    select(valid ? hash : first, false, false);

    /* Deep link from another page: services.html#svc-yoga */
    if (valid) {
      requestAnimationFrame(function () {
        root.scrollIntoView({ block: 'start', behavior: 'auto' });
      });
    }
  });
})();
