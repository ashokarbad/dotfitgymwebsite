/* ═══════════════════════════════════════════════════════════════
   DOTFIT FITNESS — site behaviour
   Editable settings live in SITE SETTINGS below.
   ═══════════════════════════════════════════════════════════════ */

const DOTFIT = {
  phone: '+919822843366',
  whatsapp: '919822843366',
  waMessage: 'Hi Dotfit Fitness, I would like to know more about your fitness programs.',

  /* Paste a Formspree endpoint to receive enquiries by email, e.g.
     'https://formspree.io/f/xxxxxxxx'. Leave empty and the form hands
     the enquiry to WhatsApp instead. */
  formEndpoint: '',

  /* Opening hours, 24-hour decimal. Sunday = 0. null = closed. */
  hours: { 0:[7,11], 1:[6,22], 2:[6,22], 3:[6,22], 4:[6,22], 5:[6,22], 6:[6,22] }
};

(function () {
  'use strict';
  const $  = (s, c) => (c || document).querySelector(s);
  const $$ = (s, c) => Array.from((c || document).querySelectorAll(s));
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const DAYS = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

  /* ── Sticky nav shadow ── */
  const nav = $('#nav');
  if (nav) {
    const shade = () => nav.classList.toggle('is-stuck', window.scrollY > 8);
    shade(); addEventListener('scroll', shade, { passive: true });

    const burger = $('#burger');
    burger.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', String(open));
      burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      document.body.style.overflow = open ? 'hidden' : '';
    });
    $$('#menu a').forEach(a => a.addEventListener('click', () => {
      nav.classList.remove('is-open');
      burger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }));
    addEventListener('keydown', e => {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) burger.click();
    });
  }

  /* ── WhatsApp + phone links ── */
  const waHref = 'https://wa.me/' + DOTFIT.whatsapp + '?text=' + encodeURIComponent(DOTFIT.waMessage);
  $$('[data-wa]').forEach(el => { el.href = waHref; el.target = '_blank'; el.rel = 'noopener'; });
  $$('[data-tel]').forEach(el => { el.href = 'tel:' + DOTFIT.phone; });

  /* ── Scroll reveal ── */
  if ('IntersectionObserver' in window && !reduced) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
    }), { rootMargin: '0px 0px -6% 0px', threshold: .06 });
    $$('.rv').forEach((el, i) => {
      el.style.transitionDelay = (Math.min(i % 4, 3) * 65) + 'ms';
      io.observe(el);
    });
  } else $$('.rv').forEach(el => el.classList.add('is-in'));

  /* ── Counters ── */
  const cs = $$('[data-count]');
  if (cs.length && 'IntersectionObserver' in window) {
    const cio = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting) return;
      const el = e.target, end = +el.dataset.count, sfx = el.dataset.suffix || '';
      cio.unobserve(el);
      if (reduced) { el.textContent = end + sfx; return; }
      const t0 = performance.now();
      const step = t => {
        const p = Math.min((t - t0) / 1100, 1);
        el.textContent = Math.round(end * (1 - Math.pow(1 - p, 3))) + sfx;
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    }), { threshold: .5 });
    cs.forEach(el => cio.observe(el));
  }

  /* ── Generic filter pills (services, gallery, activities) ── */
  $$('[data-filterset]').forEach(set => {
    const targets = $$('[data-cat]', $('#' + set.dataset.filterset));
    $$('.filter', set).forEach(btn => btn.addEventListener('click', () => {
      const cat = btn.dataset.filter;
      $$('.filter', set).forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
      targets.forEach(t => {
        t.hidden = !(cat === 'all' || (t.dataset.cat || '').split(' ').includes(cat));
      });
      if (window.DOTFIT_LB) window.DOTFIT_LB.refresh();
    }));
  });

  /* ── Pune (IST) clock, independent of the visitor's timezone ── */
  function puneNow() {
    const p = new Intl.DateTimeFormat('en-GB', {
      timeZone: 'Asia/Kolkata', weekday: 'short', hour: '2-digit', minute: '2-digit', hour12: false
    }).formatToParts(new Date());
    const g = t => p.find(x => x.type === t).value;
    const map = { Sun:0, Mon:1, Tue:2, Wed:3, Thu:4, Fri:5, Sat:6 };
    return { day: map[g('weekday')], dec: +g('hour') + (+g('minute')) / 60 };
  }
  const fmt = h => {
    const hh = Math.floor(h), mm = Math.round((h - hh) * 60);
    const ap = hh >= 12 ? 'PM' : 'AM', h12 = hh % 12 === 0 ? 12 : hh % 12;
    return h12 + ':' + String(mm).padStart(2, '0') + ' ' + ap;
  };
  const now = puneNow(), today = DOTFIT.hours[now.day];

  /* ── Open / closed badge ── */
  const badge = $('#openBadge'), badgeTxt = $('#openText');
  if (badge && badgeTxt) {
    if (today && now.dec >= today[0] && now.dec < today[1]) {
      const left = today[1] - now.dec, h = Math.floor(left), m = Math.round((left - h) * 60);
      badge.classList.add('is-open');
      badgeTxt.innerHTML = '<b>Open now</b> <span>· closes ' + fmt(today[1]) +
        ' · ' + (h ? h + ' hr ' : '') + m + ' min left</span>';
    } else {
      let next = null, add = 0;
      if (today && now.dec < today[0]) { next = today; }
      else for (let i = 1; i <= 7; i++) {
        const h = DOTFIT.hours[(now.day + i) % 7];
        if (h) { next = h; add = i; break; }
      }
      badgeTxt.innerHTML = next
        ? '<b>Closed now</b> <span>· opens ' +
          (add === 0 ? 'today' : add === 1 ? 'tomorrow' : DAYS[(now.day + add) % 7]) +
          ' at ' + fmt(next[0]) + '</span>'
        : '<b>Closed now</b>';
    }
  }

  /* ── Opening-hours track ── */
  const table = $('#hoursTable');
  if (table) {
    const T0 = 5, SPAN = 24 - T0;
    [1,2,3,4,5,6,0].forEach(idx => {
      const hrs = DOTFIT.hours[idx], isToday = idx === now.day;
      const pct = ((now.dec - T0) / SPAN) * 100;
      const row = document.createElement('div');
      row.className = 'hrow' + (isToday ? ' is-today' : '');
      row.innerHTML =
        '<span class="hrow__day">' + DAYS[idx] + (isToday ? ' <em>Today</em>' : '') + '</span>' +
        '<span class="track">' +
          (hrs ? '<span class="track__band" style="left:' + ((hrs[0]-T0)/SPAN*100) +
                 '%;width:' + ((hrs[1]-hrs[0])/SPAN*100) + '%"></span>' : '') +
          (isToday && pct >= 0 && pct <= 100
            ? '<span class="track__now" style="left:' + pct + '%"></span>' : '') +
        '</span>' +
        '<span class="hrow__time">' + (hrs ? fmt(hrs[0]) + ' – ' + fmt(hrs[1]) : 'Closed') + '</span>';
      table.appendChild(row);
    });
  }

  /* ── Gallery lightbox ── */
  const lb = $('#lightbox');
  if (lb) {
    const img = $('#lbImg'), cap = $('#lbCap');
    let items = [], i = 0, lastFocus = null;

    const collect = () => { items = $$('.gitem').filter(el => !el.hidden); };
    const show = n => {
      if (!items.length) return;
      i = (n + items.length) % items.length;
      const el = items[i], src = el.dataset.full || $('img', el).src;
      const d = el.dataset;
      img.src = src; img.alt = d.caption || d.title || 'Dotfit Fitness photo';
      const meta = [d.date, items.length > 1 ? (i + 1) + ' of ' + items.length : '']
        .filter(Boolean).join(' · ');
      cap.innerHTML =
        (d.category ? '<b>' + d.category + '</b>' : '') +
        (d.title ? '<strong>' + d.title + '</strong> ' : '') +
        (d.caption || '') +
        (meta ? '<i>' + meta + '</i>' : '');
    };
    const open = el => {
      collect(); lastFocus = document.activeElement;
      show(items.indexOf(el));
      lb.classList.add('is-on'); document.body.style.overflow = 'hidden';
      $('#lbClose').focus();
    };
    const close = () => {
      lb.classList.remove('is-on'); document.body.style.overflow = '';
      if (lastFocus) lastFocus.focus();
    };

    document.addEventListener('click', e => {
      const t = e.target.closest('.gitem');
      if (t) open(t);
    });
    $('#lbClose').addEventListener('click', close);
    $('#lbPrev').addEventListener('click', () => show(i - 1));
    $('#lbNext').addEventListener('click', () => show(i + 1));
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    addEventListener('keydown', e => {
      if (!lb.classList.contains('is-on')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(i - 1);
      if (e.key === 'ArrowRight') show(i + 1);
    });

    /* swipe */
    let x0 = null;
    lb.addEventListener('touchstart', e => x0 = e.touches[0].clientX, { passive: true });
    lb.addEventListener('touchend', e => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 55) show(dx > 0 ? i - 1 : i + 1);
      x0 = null;
    }, { passive: true });

    window.DOTFIT_LB = { refresh: collect };
    collect();
  }

  /* ── Enquiry form ── */
  const form = $('#leadForm');
  if (form) {
    const wrap = form.closest('.form');
    form.addEventListener('submit', async e => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      const d = Object.fromEntries(new FormData(form).entries());
      const btn = $('#leadSubmit');
      btn.textContent = 'Sending…'; btn.disabled = true;

      const summary = 'New enquiry — Dotfit Fitness\n\n' +
        'Name: ' + d.name + '\nPhone: ' + d.phone + '\nEmail: ' + d.email +
        '\nGoal: ' + d.goal + '\nPreferred training: ' + d.preference +
        (d.message ? '\nMessage: ' + d.message : '');

      try {
        if (DOTFIT.formEndpoint) {
          const r = await fetch(DOTFIT.formEndpoint, {
            method: 'POST', headers: { Accept: 'application/json' }, body: new FormData(form)
          });
          if (!r.ok) throw new Error('rejected');
        } else {
          window.open('https://wa.me/' + DOTFIT.whatsapp + '?text=' + encodeURIComponent(summary),
                      '_blank', 'noopener');
        }
        wrap.classList.add('is-sent');
        wrap.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'center' });
      } catch (err) {
        btn.textContent = 'Join Dotfit'; btn.disabled = false;
        alert('That did not send. Please message us on WhatsApp and we will take your details there.');
      }
    });
  }
})();
