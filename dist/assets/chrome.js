/* ═══════════════════════════════════════════════════════════
   GESTELL · Brand Operating System · WEB CHROME — BEHAVIOR
   Non-invasive overlay script. Reads window.__GBOS__ configured
   per-volume and builds nav + drawer + interactions.
   ═══════════════════════════════════════════════════════════ */
(function () {
  'use strict';

  var CFG = window.__GBOS__ || {};
  var VOLS = [
    { slug: 'vol-1', roman: 'I',   title: 'ADN Estratégico' },
    { slug: 'vol-2', roman: 'II',  title: 'Arquitectura de Marca' },
    { slug: 'vol-3', roman: 'III', title: 'Identidad Visual' },
    { slug: 'vol-4', roman: 'IV',  title: 'Identidad Verbal' },
    { slug: 'vol-5', roman: 'V',   title: 'Identidad Dinámica & Sensorial' },
    { slug: 'vol-6', roman: 'VI',  title: 'Infraestructura Digital' }
  ];

  // Apply per-volume accent color to chrome
  if (CFG.color) {
    document.documentElement.style.setProperty('--gbos-accent', CFG.color);
  }

  // ─────────────────────────────────────────────────────────
  // 1. RENDER THE NAV
  // ─────────────────────────────────────────────────────────
  function el(tag, attrs, children) {
    var n = document.createElement(tag);
    if (attrs) for (var k in attrs) {
      if (k === 'class') n.className = attrs[k];
      else if (k === 'html') n.innerHTML = attrs[k];
      else if (k === 'text') n.textContent = attrs[k];
      else if (k.indexOf('on') === 0) n.addEventListener(k.slice(2), attrs[k]);
      else n.setAttribute(k, attrs[k]);
    }
    if (children) children.forEach(function (c) {
      if (c) n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
    });
    return n;
  }

  function icon(path) {
    var s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    s.setAttribute('class', 'gbos-icon');
    s.setAttribute('viewBox', '0 0 24 24');
    s.innerHTML = path;
    return s;
  }

  var ICONS = {
    list:    '<line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/>',
    close:   '<line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/>',
    print:   '<path d="M6 9V3h12v6M6 18H4v-7h16v7h-2M8 14h8v7H8z"/>',
    home:    '<path d="M3 11l9-8 9 8v10a1 1 0 01-1 1h-5v-7h-6v7H4a1 1 0 01-1-1z"/>',
    arrow:   '<polyline points="9 6 15 12 9 18"/>',
    cmd:     '<path d="M6 9a3 3 0 110-6 3 3 0 013 3v12a3 3 0 11-3-3h12a3 3 0 113 3 3 3 0 01-3-3V6a3 3 0 113 3h-6M9 9h6v6H9z" fill="none"/>'
  };

  function buildNav() {
    var nav = el('nav', { class: 'gbos-nav', role: 'navigation', 'aria-label': 'GESTELL Brand Operating System' });

    // LEFT — brand
    var brand = el('a', { class: 'gbos-brand', href: 'index.html', 'aria-label': 'GESTELL — Home' }, [
      el('span', { class: 'gbos-brand__mark', text: 'G' }),
      el('span', { class: 'gbos-brand__text', text: 'GESTELL' }),
      el('span', { class: 'gbos-brand__sub', text: '· Brand OS' })
    ]);
    nav.appendChild(brand);

    // CENTER — volume switcher
    var vols = el('div', { class: 'gbos-vols', role: 'tablist' });
    VOLS.forEach(function (v) {
      var btn = el('a', {
        class: 'gbos-vols__btn',
        href: v.slug + '.html',
        role: 'tab',
        title: 'Vol. ' + v.roman + ' — ' + v.title
      });
      btn.textContent = 'Vol. ' + v.roman;
      if (v.slug === CFG.vol) btn.setAttribute('aria-current', 'page');
      vols.appendChild(btn);
    });
    nav.appendChild(vols);

    // RIGHT — actions
    var actions = el('div', { class: 'gbos-actions' });

    var indexBtn = el('button', {
      class: 'gbos-btn gbos-btn--primary',
      type: 'button',
      'aria-label': 'Abrir índice',
      onclick: openDrawer
    }, [
      icon(ICONS.list),
      el('span', { class: 'gbos-btn__label', text: 'Índice' }),
      el('span', { class: 'gbos-btn__kbd', text: 'I' })
    ]);
    actions.appendChild(indexBtn);

    var printBtn = el('button', {
      class: 'gbos-btn',
      type: 'button',
      'aria-label': 'Imprimir',
      onclick: function () { window.print(); }
    }, [
      icon(ICONS.print),
      el('span', { class: 'gbos-btn__label', text: 'Imprimir' })
    ]);
    actions.appendChild(printBtn);

    var homeBtn = el('a', {
      class: 'gbos-btn',
      href: 'index.html',
      'aria-label': 'Inicio'
    }, [
      icon(ICONS.home),
      el('span', { class: 'gbos-btn__label', text: 'Inicio' })
    ]);
    actions.appendChild(homeBtn);

    nav.appendChild(actions);

    // Progress
    var progress = el('div', { class: 'gbos-progress' }, [
      el('div', { class: 'gbos-progress__fill', id: 'gbos-progress-fill' })
    ]);
    nav.appendChild(progress);

    return nav;
  }

  // ─────────────────────────────────────────────────────────
  // 2. DRAWER (index)
  // ─────────────────────────────────────────────────────────
  function buildDrawer() {
    var scrim = el('div', { class: 'gbos-scrim', onclick: closeDrawer });

    var drawer = el('aside', {
      class: 'gbos-drawer',
      role: 'dialog',
      'aria-modal': 'true',
      'aria-label': 'Índice del volumen',
      tabindex: '-1'
    });

    var head = el('div', { class: 'gbos-drawer__head' }, [
      el('div', {}, [
        el('div', { class: 'gbos-drawer__eyebrow', text: 'Vol. ' + (CFG.roman || '') + ' · Índice' }),
        el('h2', { class: 'gbos-drawer__title', text: CFG.title || 'GESTELL' })
      ]),
      el('button', {
        class: 'gbos-drawer__close',
        type: 'button',
        'aria-label': 'Cerrar índice',
        onclick: closeDrawer
      }, [icon(ICONS.close)])
    ]);
    drawer.appendChild(head);

    var list = el('nav', { class: 'gbos-drawer__list', id: 'gbos-drawer-list' });
    // Cover link
    var coverLink = el('a', {
      class: 'gbos-drawer__item',
      href: '#cover',
      'data-anchor': 'cover',
      onclick: function (e) { navigateTo(e, 'cover'); }
    }, [
      el('span', { class: 'gbos-drawer__code', text: CFG.roman || '—' }),
      el('span', { class: 'gbos-drawer__label', text: 'Portada del Volumen' }),
      icon(ICONS.arrow)
    ]);
    coverLink.querySelector('.gbos-icon').classList.add('gbos-drawer__arrow');
    list.appendChild(coverLink);

    (CFG.sections || []).forEach(function (sec) {
      var a = el('a', {
        class: 'gbos-drawer__item',
        href: '#' + sec.id,
        'data-anchor': sec.id,
        onclick: function (e) { navigateTo(e, sec.id); }
      }, [
        el('span', { class: 'gbos-drawer__code', text: sec.code || '·' }),
        el('span', { class: 'gbos-drawer__label', text: sec.title || '' }),
        icon(ICONS.arrow)
      ]);
      a.querySelector('.gbos-icon').classList.add('gbos-drawer__arrow');
      list.appendChild(a);
    });
    drawer.appendChild(list);

    var foot = el('div', { class: 'gbos-drawer__foot' }, [
      el('span', { text: 'Confidencial · 2026' }),
      el('span', {}, [
        el('span', { class: 'gbos-drawer__foot-dot' })
      ])
    ]);
    // append dot + label
    foot.children[1].appendChild(document.createTextNode(' Live'));
    drawer.appendChild(foot);

    return { scrim: scrim, drawer: drawer };
  }

  var drawerOpen = false, scrimEl = null, drawerEl = null;

  function openDrawer() {
    if (drawerOpen) return;
    scrimEl.classList.add('is-open');
    drawerEl.classList.add('is-open');
    drawerOpen = true;
    document.body.style.overflow = 'hidden';
    // Focus first item for keyboard users
    setTimeout(function () {
      var first = drawerEl.querySelector('.gbos-drawer__item');
      if (first) first.focus();
    }, 300);
  }
  function closeDrawer() {
    if (!drawerOpen) return;
    scrimEl.classList.remove('is-open');
    drawerEl.classList.remove('is-open');
    drawerOpen = false;
    document.body.style.overflow = '';
  }

  function navigateTo(e, anchor) {
    if (e && e.preventDefault) e.preventDefault();
    var t = document.getElementById(anchor);
    if (t) {
      var top = t.getBoundingClientRect().top + window.scrollY - 60;
      window.scrollTo({ top: top, behavior: 'smooth' });
      history.replaceState(null, '', '#' + anchor);
    }
    closeDrawer();
  }

  // ─────────────────────────────────────────────────────────
  // 3. MOBILE FAB
  // ─────────────────────────────────────────────────────────
  function buildFab() {
    return el('button', {
      class: 'gbos-fab',
      type: 'button',
      'aria-label': 'Abrir índice',
      onclick: openDrawer
    }, [icon(ICONS.list)]);
  }

  // ─────────────────────────────────────────────────────────
  // 4. TOAST (shown briefly on first load)
  // ─────────────────────────────────────────────────────────
  function buildToast() {
    return el('div', { class: 'gbos-toast', id: 'gbos-toast' }, [
      el('span', { text: 'Atajos' }),
      el('span', { class: 'gbos-toast__kbd', text: 'I' }),
      el('span', { text: 'Índice' }),
      el('span', { class: 'gbos-toast__kbd', text: '← →' }),
      el('span', { text: 'Volumen' }),
      el('span', { class: 'gbos-toast__kbd', text: 'Esc' }),
      el('span', { text: 'Cerrar' })
    ]);
  }
  function showToastOnce() {
    try {
      if (sessionStorage.getItem('gbos-toast-seen')) return;
    } catch (_) {}
    var t = document.getElementById('gbos-toast');
    if (!t) return;
    setTimeout(function () { t.classList.add('is-in'); }, 900);
    setTimeout(function () { t.classList.remove('is-in'); }, 4800);
    try { sessionStorage.setItem('gbos-toast-seen', '1'); } catch (_) {}
  }

  // ─────────────────────────────────────────────────────────
  // 5. KEYBOARD SHORTCUTS
  // ─────────────────────────────────────────────────────────
  function bindKeys() {
    document.addEventListener('keydown', function (e) {
      // Ignore if user is typing
      var t = e.target;
      if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;

      var key = e.key;
      if (key === 'Escape') { closeDrawer(); return; }
      if (key === 'i' || key === 'I') {
        e.preventDefault();
        drawerOpen ? closeDrawer() : openDrawer();
        return;
      }
      // Arrow keys for volume nav only with no modifier and drawer closed
      if (!drawerOpen && !e.metaKey && !e.ctrlKey && !e.altKey) {
        var idx = VOLS.findIndex(function (v) { return v.slug === CFG.vol; });
        if (key === 'ArrowLeft'  && idx > 0) {
          window.location.href = VOLS[idx - 1].slug + '.html';
        } else if (key === 'ArrowRight' && idx >= 0 && idx < VOLS.length - 1) {
          window.location.href = VOLS[idx + 1].slug + '.html';
        }
      }
    });
  }

  // ─────────────────────────────────────────────────────────
  // 6. NAV AUTO-HIDE ON SCROLL DOWN
  // ─────────────────────────────────────────────────────────
  function bindNavHide(nav) {
    var lastY = window.scrollY;
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        var y = window.scrollY;
        if (y > lastY + 12 && y > 200) nav.classList.add('is-hidden');
        else if (y < lastY - 6 || y < 200) nav.classList.remove('is-hidden');
        lastY = y;
        ticking = false;
      });
    }, { passive: true });
  }

  // ─────────────────────────────────────────────────────────
  // 7. READING PROGRESS
  // ─────────────────────────────────────────────────────────
  function bindProgress() {
    var fill = document.getElementById('gbos-progress-fill');
    if (!fill) return;
    function update() {
      var h = document.documentElement;
      var max = h.scrollHeight - window.innerHeight;
      var p = max > 0 ? (window.scrollY / max) * 100 : 0;
      fill.style.width = Math.min(100, Math.max(0, p)) + '%';
    }
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  }

  // ─────────────────────────────────────────────────────────
  // 8. ACTIVE SECTION IN DRAWER
  // ─────────────────────────────────────────────────────────
  function bindActiveSection() {
    var anchors = ['cover'].concat((CFG.sections || []).map(function (s) { return s.id; }));
    var items = Array.prototype.slice.call(
      document.querySelectorAll('.gbos-drawer__item'));
    var targets = anchors
      .map(function (id) { return document.getElementById(id); })
      .filter(Boolean);

    if (!targets.length) return;

    function setActive(idx) {
      items.forEach(function (it, i) {
        it.classList.toggle('is-active', i === idx);
      });
    }

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        // Find the topmost visible section
        var visible = entries.filter(function (e) { return e.isIntersecting; });
        if (!visible.length) return;
        visible.sort(function (a, b) {
          return a.target.getBoundingClientRect().top - b.target.getBoundingClientRect().top;
        });
        var id = visible[0].target.id;
        var idx = anchors.indexOf(id);
        if (idx >= 0) setActive(idx);
      }, { rootMargin: '-40% 0px -55% 0px', threshold: 0 });
      targets.forEach(function (t) { observer.observe(t); });
    }
  }

  // ─────────────────────────────────────────────────────────
  // 9. WRAP PAGES IN FRAMES & SCALE ON MOBILE
  // ─────────────────────────────────────────────────────────
  var PAGE_SELECTOR = '.page, .chroma-page, .diagram-fullpage';
  // A4 width in CSS px at 96dpi: 210mm = 793.7007874 px
  var A4_W_PX = 793.70;
  var A4_H_PX = 1122.52; // 297mm
  var SCALE_BREAKPOINT = 840;

  function wrapPages() {
    var pages = Array.prototype.slice.call(document.querySelectorAll(PAGE_SELECTOR));
    pages.forEach(function (p) {
      if (p.parentElement && p.parentElement.classList.contains('gbos-page-frame')) return;
      var frame = document.createElement('div');
      frame.className = 'gbos-page-frame';
      p.parentNode.insertBefore(frame, p);
      frame.appendChild(p);
    });
  }

  function updateScale() {
    var vw = window.innerWidth;
    var frames = document.querySelectorAll('.gbos-page-frame');
    if (vw >= SCALE_BREAKPOINT) {
      frames.forEach(function (f) {
        f.style.height = '';
        f.style.setProperty('--gbos-scale', '1');
      });
    } else {
      // leave 0 side padding; fit full width
      var scale = vw / A4_W_PX;
      frames.forEach(function (f) {
        f.style.setProperty('--gbos-scale', scale);
        // Reserve correct layout height (the scaled page height)
        f.style.height = (A4_H_PX * scale) + 'px';
      });
    }
  }

  // ─────────────────────────────────────────────────────────
  // 10. INIT
  // ─────────────────────────────────────────────────────────
  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    // Mount nav + drawer + fab + toast
    var mount = document.getElementById('gbos-mount') || document.body;
    var nav = buildNav();
    var pieces = buildDrawer();
    scrimEl = pieces.scrim;
    drawerEl = pieces.drawer;
    var fab = buildFab();
    var toast = buildToast();

    document.body.insertBefore(nav, document.body.firstChild);
    document.body.appendChild(scrimEl);
    document.body.appendChild(drawerEl);
    document.body.appendChild(fab);
    document.body.appendChild(toast);

    bindKeys();
    bindNavHide(nav);
    bindProgress();
    wrapPages();
    updateScale();
    bindActiveSection();

    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(updateScale, 120);
    });

    showToastOnce();

    // Smooth-scroll if a hash is present on load
    if (location.hash) {
      setTimeout(function () {
        var t = document.getElementById(location.hash.slice(1));
        if (t) {
          var top = t.getBoundingClientRect().top + window.scrollY - 60;
          window.scrollTo({ top: top, behavior: 'auto' });
        }
      }, 100);
    }
  });
})();
