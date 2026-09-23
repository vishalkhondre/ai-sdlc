/* Beyond Faster Coding — progressive enhancement. No dependencies. */
(function () {
  'use strict';
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* ignore */ } }
  };

  /* ---------- theme ---------- */
  const themeBtn = $('#theme-toggle');
  if (themeBtn) themeBtn.addEventListener('click', () => {
    const root = document.documentElement;
    const dark = matchMedia('(prefers-color-scheme: dark)').matches;
    const cur = root.dataset.theme && root.dataset.theme !== 'auto' ? root.dataset.theme : (dark ? 'dark' : 'light');
    const next = cur === 'dark' ? 'light' : 'dark';
    root.dataset.theme = next; store.set('bfc-theme', next);
  });

  /* ---------- mobile menu ---------- */
  const menu = $('#menu-toggle'), topnav = $('.topnav');
  if (menu && topnav) menu.addEventListener('click', () => {
    const open = topnav.classList.toggle('open');
    menu.setAttribute('aria-expanded', String(open));
  });

  /* ---------- reading progress + active TOC ---------- */
  const bar = $('#progress span'), article = $('#article');
  const tocLinks = $$('.toc a');
  const headings = tocLinks.map(a => document.getElementById(a.getAttribute('href').slice(1))).filter(Boolean);
  function onScroll() {
    if (bar && article) {
      const r = article.getBoundingClientRect();
      const total = r.height - innerHeight;
      const p = total > 0 ? Math.min(1, Math.max(0, -r.top / total)) : 0;
      bar.style.width = (p * 100).toFixed(1) + '%';
    }
    if (headings.length) {
      let cur = headings[0];
      for (const h of headings) if (h.getBoundingClientRect().top < 120) cur = h;
      tocLinks.forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#' + cur.id));
    }
  }
  addEventListener('scroll', onScroll, { passive: true }); onScroll();

  /* ---------- glossary tooltips ---------- */
  let glossary = {};
  try { glossary = JSON.parse(($('#glossary-data') || {}).textContent || '{}'); } catch (e) { glossary = {}; }
  const tip = $('#tip');
  const ATTR = { adopted: 'Adopted from source', adapted: 'Adapted from source', coined: 'Coined in this series', common: 'Common usage' };
  function showTip(el, html) {
    if (!tip) return;
    tip.innerHTML = html; tip.hidden = false;
    const r = el.getBoundingClientRect(), tw = tip.offsetWidth, th = tip.offsetHeight;
    let x = Math.min(Math.max(8, r.left), innerWidth - tw - 8);
    let y = r.top - th - 10; if (y < 8) y = r.bottom + 10;
    tip.style.left = x + 'px'; tip.style.top = y + 'px';
  }
  function hideTip() { if (tip) tip.hidden = true; }
  $$('a.term').forEach(a => {
    const g = glossary[a.dataset.term]; if (!g) return;
    const html = `<b>${g.term}</b>${g.def.length > 260 ? g.def.slice(0, 257) + '…' : g.def}<div class="attr attr-${g.attr}">${ATTR[g.attr] || g.attr}</div>`;
    a.addEventListener('mouseenter', () => showTip(a, html));
    a.addEventListener('focus', () => showTip(a, html));
    a.addEventListener('mouseleave', hideTip); a.addEventListener('blur', hideTip);
  });
  /* footnote popovers */
  $$('sup a.footnote-ref, sup a[href^="#fn"]').forEach(a => {
    const target = document.getElementById(a.getAttribute('href').slice(1)); if (!target) return;
    const html = target.innerHTML.replace(/<a[^>]*footnote-backref[^>]*>.*?<\/a>/, '');
    a.addEventListener('mouseenter', () => showTip(a, html));
    a.addEventListener('mouseleave', hideTip);
  });
  addEventListener('scroll', hideTip, { passive: true });

  /* ---------- code copy buttons ---------- */
  $$('.prose pre').forEach(pre => {
    const b = document.createElement('button'); b.className = 'copybtn'; b.type = 'button'; b.textContent = 'Copy';
    b.addEventListener('click', async () => {
      const code = $('code', pre);
      if (!code || !navigator.clipboard) { toast('Copy unavailable'); return; }
      try {
        await navigator.clipboard.writeText(code.textContent);
        toast('Copied');
      } catch (e) { toast('Copy failed'); }
    });
    pre.appendChild(b);
  });
  $$('[data-copy]').forEach(b => b.addEventListener('click', () => {
    navigator.clipboard && navigator.clipboard.writeText(b.dataset.copy).then(() => toast('Link copied'));
  }));
  function toast(msg) {
    const t = document.createElement('div'); t.className = 'toast'; t.textContent = msg; document.body.appendChild(t);
    setTimeout(() => t.remove(), 1600);
  }

  /* ---------- lightbox for diagrams ---------- */
  const lb = $('#lightbox'), lbBody = lb && $('.lightbox-body', lb);
  function openLightbox(svg) {
    if (!lb) return;
    // A separate image document isolates IDs from the original inline diagram.
    const image = document.createElement('img');
    const figure = svg.closest('.diagram');
    image.src = base + 'diagrams/' + encodeURIComponent(figure.dataset.diagram) + '.svg';
    const caption = $('figcaption', figure);
    image.alt = caption ? caption.textContent.trim() : 'Diagram';
    lbBody.replaceChildren(image); lb.hidden = false; document.body.style.overflow = 'hidden';
  }
  function closeLightbox() { if (lb) { lb.hidden = true; document.body.style.overflow = ''; } }
  $$('.diagram .zoom').forEach(b => b.addEventListener('click', e => { e.preventDefault(); openLightbox($('svg', b.parentElement)); }));
  $$('.diagram-frame svg').forEach(svg => svg.addEventListener('dblclick', () => openLightbox(svg)));
  if (lb) { lb.addEventListener('click', e => { if (e.target === lb || e.target.classList.contains('lightbox-close')) closeLightbox(); }); }

  /* ---------- model explorer (home) ---------- */
  $$('#model-explorer .layer').forEach(l => {
    l.addEventListener('mouseenter', () => $$('#model-explorer .layer').forEach(x => x.classList.toggle('on', x === l)));
    l.addEventListener('mouseleave', () => l.classList.remove('on'));
  });

  /* ---------- reference sheet toggles ---------- */
  $$('.toggle').forEach(t => {
    $$('button', t).forEach(b => b.addEventListener('click', () => setVariant(t.closest('.ref-pair'), b.dataset.variant)));
  });
  function setVariant(section, v) {
    $$('.toggle button', section).forEach(b => b.classList.toggle('on', b.dataset.variant === v));
    $$('.variant', section).forEach(x => x.hidden = x.dataset.variant !== v);
  }
  const toggleAll = $('#toggle-all');
  if (toggleAll) {
    let generic = false;
    toggleAll.addEventListener('click', () => {
      generic = !generic; $$('.ref-pair').forEach(s => setVariant(s, generic ? 'generic' : 'export'));
      toggleAll.textContent = generic ? 'switch all to the worked example' : 'switch all to generic';
    });
  }

  /* ---------- glossary filter ---------- */
  const tf = $('#term-filter');
  if (tf) $$('button', tf).forEach(b => b.addEventListener('click', () => {
    $$('button', tf).forEach(x => x.classList.toggle('on', x === b));
    $$('.term-entry').forEach(e => e.hidden = b.dataset.attr !== 'all' && e.dataset.attr !== b.dataset.attr);
  }));

  /* ---------- workflow catalog ---------- */
  const wfData = $('#wf-data');
  if (wfData) initCatalog(JSON.parse(wfData.textContent));
  function initCatalog(D) {
    const phases = D.phases, byPhase = {}, byId = {};
    D.workflows.forEach(w => { (byPhase[w.phase] = byPhase[w.phase] || []).push(w); byId[w.id] = w; });
    const state = { q: '', m: 'all', a: 'all', view: 'map', sort: 'id', desc: false };
    const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const phaseName = k => (phases.find(p => p.key === k) || {}).name || k;
    function visible(w) {
      if (state.m !== 'all' && w.maturity !== state.m) return false;
      if (state.a !== 'all' && !(w.applies_to.includes('All') || w.applies_to.includes(state.a))) return false;
      if (state.q) {
        const hay = [w.id, w.name, w.decision, w.agent, w.checks, w.people, w.evidence, w.traditional.activity, w.traditional.owner].join(' ').toLowerCase();
        if (!hay.includes(state.q)) return false;
      }
      return true;
    }
    /* map */
    const map = $('#wf-map');
    map.innerHTML = phases.map(p => `<div class="wf-col" data-phase="${p.key}"><div class="wf-col-head"><b>${esc(p.name)}</b><br>${(byPhase[p.key] || []).length} workflows</div>${(byPhase[p.key] || []).map(w => `
      <button class="wf-card m-${w.maturity}" type="button" data-id="${w.id}" id="${w.id}"><span class="id">${w.id} · ${w.maturity}</span><span class="name">${esc(w.name)}</span><span class="was">${esc(w.traditional.activity.split(';')[0])}</span><span class="tags">${w.applies_to.map(a => `<span class="tag">${esc(a)}</span>`).join('')}</span></button>`).join('')}<div class="wf-empty" hidden>No match</div></div>`).join('');
    /* table */
    const tbl = $('#wf-table');
    const cols = [['id', 'ID'], ['phase', 'Phase'], ['name', 'Workflow'], ['decision', 'Decision it supports'], ['maturity', 'Maturity'], ['applies', 'Change type'], ['was', 'Traditional counterpart']];
    function renderTable() {
      const rows = D.workflows.slice().sort((x, y) => {
        const k = state.sort; const vx = k === 'applies' ? x.applies_to.join() : k === 'was' ? x.traditional.activity : x[k]; const vy = k === 'applies' ? y.applies_to.join() : k === 'was' ? y.traditional.activity : y[k];
        return (vx > vy ? 1 : vx < vy ? -1 : 0) * (state.desc ? -1 : 1);
      });
      tbl.innerHTML = `<div class="table-wrap"><table><thead><tr>${cols.map(c => `<th data-k="${c[0]}" class="${state.sort === c[0] ? 'sorted' + (state.desc ? ' desc' : '') : ''}">${c[1]}</th>`).join('')}</tr></thead><tbody>${rows.map(w => `
        <tr data-id="${w.id}"${visible(w) ? '' : ' hidden'}><td>${w.id}</td><td>${esc(phaseName(w.phase))}</td><td><b>${esc(w.name)}</b></td><td>${esc(w.decision)}</td><td><span class="pill m-${w.maturity}">${w.maturity}</span></td><td>${w.applies_to.join(', ')}</td><td>${esc(w.traditional.activity)}</td></tr>`).join('')}</tbody></table></div>`;
      $$('th', tbl).forEach(th => th.addEventListener('click', () => { if (state.sort === th.dataset.k) state.desc = !state.desc; else { state.sort = th.dataset.k; state.desc = false; } renderTable(); }));
      $$('tr[data-id]', tbl).forEach(tr => tr.addEventListener('click', () => openDetail(tr.dataset.id)));
    }
    /* traditional map */
    const trad = $('#wf-trad');
    trad.innerHTML = `<p class="muted">Every activity from the source models and where it lands. Rows landing in <b>harness</b> are mechanisms rather than workflows (rule registry, evidence schema, adapters); rows marked <b>excluded</b> are deliberately outside the catalog.</p><div class="table-wrap"><table><thead><tr><th>Source</th><th>Source phase</th><th>Role / initiator</th><th>Traditional activity</th><th>Artefact or tool</th><th>Lands in</th><th>How</th></tr></thead><tbody>${D.traditional_map.map(r => `<tr><td>${esc(D.sources[r.source] || r.source)}</td><td>${esc(r.phase)}</td><td>${esc(r.role)}</td><td>${esc(r.activity)}${r.note ? `<div class="muted">${esc(r.note)}</div>` : ''}</td><td>${esc(r.artefact)}</td><td class="lands">${byId[r.lands_in] ? `<a href="#${r.lands_in}" data-open="${r.lands_in}">${r.lands_in} ${esc(byId[r.lands_in].name)}</a>` : esc(r.lands_in)}</td><td>${esc(r.how)}</td></tr>`).join('')}</tbody></table></div>`;
    $$('a[data-open]', trad).forEach(a => a.addEventListener('click', e => { e.preventDefault(); openDetail(a.dataset.open); }));
    function apply() {
      $$('.wf-card', map).forEach(c => c.hidden = !visible(byId[c.dataset.id]));
      $$('.wf-col', map).forEach(col => { const any = $$('.wf-card:not([hidden])', col).length; $('.wf-empty', col).hidden = any > 0; });
      $$('tr[data-id]', tbl).forEach(tr => tr.hidden = !visible(byId[tr.dataset.id]));
    }
    $('#wf-search').addEventListener('input', e => { state.q = e.target.value.trim().toLowerCase(); apply(); });
    $$('#wf-maturity button').forEach(b => b.addEventListener('click', () => { $$('#wf-maturity button').forEach(x => x.classList.toggle('on', x === b)); state.m = b.dataset.m; apply(); }));
    $$('#wf-applies button').forEach(b => b.addEventListener('click', () => { $$('#wf-applies button').forEach(x => x.classList.toggle('on', x === b)); state.a = b.dataset.a; apply(); }));
    $$('.viewtabs button').forEach(b => b.addEventListener('click', () => {
      $$('.viewtabs button').forEach(x => x.classList.toggle('on', x === b)); state.view = b.dataset.view;
      $$('[data-view]', $('.section-inner')).forEach(v => { if (v.tagName !== 'BUTTON') v.hidden = v.dataset.view !== state.view; });
    }));
    $$('.wf-card', map).forEach(c => c.addEventListener('click', () => openDetail(c.dataset.id)));
    /* detail panel */
    const detail = $('#wf-detail'), body = $('.wf-detail-body', detail);
    function openDetail(id) {
      const w = byId[id]; if (!w) return;
      const ids = D.workflows.map(x => x.id), i = ids.indexOf(id);
      body.innerHTML = `
        <div class="k">${esc(phaseName(w.phase))} · ${w.id}</div>
        <h2>${esc(w.name)}</h2>
        <div><span class="pill m-${w.maturity}">${w.maturity}</span> <span class="muted" style="font-size:13px">${esc(D.maturity[w.maturity] || '')}</span></div>
        <div class="decision">${esc(w.decision)}</div>
        <div class="wf-grid">
          <div class="wf-cell agent"><span class="k">The agent</span>${esc(w.agent)}</div>
          <div class="wf-cell checks"><span class="k">The checks</span>${esc(w.checks)}</div>
          <div class="wf-cell people"><span class="k">The people</span>${esc(w.people)}</div>
        </div>
        <div class="wf-row"><span class="k">Trigger</span><span>${esc(w.trigger)}</span><span class="k">Evidence record</span><span>${esc(w.evidence)}</span><span class="k">Applies to</span><span>${w.applies_to.join(', ')}</span>${w.notes ? `<span class="k">Notes</span><span>${esc(w.notes)}</span>` : ''}</div>
        <div class="wf-trad-box"><span class="k">Traditional counterpart</span><br><b>${esc(w.traditional.activity)}</b><br><span class="muted">Owner: ${esc(w.traditional.owner)} · Artefact: ${esc(w.traditional.artefact)}</span></div>
        <div class="wf-nav">${i > 0 ? `<button class="btn small" type="button" data-go="${ids[i - 1]}">← ${ids[i - 1]}</button>` : '<span></span>'}<a class="btn small" href="workflows.html">How workflows are defined (Part 5)</a>${i < ids.length - 1 ? `<button class="btn small" type="button" data-go="${ids[i + 1]}">${ids[i + 1]} →</button>` : '<span></span>'}</div>`;
      $$('[data-go]', body).forEach(b => b.addEventListener('click', () => openDetail(b.dataset.go)));
      detail.hidden = false; document.body.style.overflow = 'hidden'; history.replaceState(null, '', '#' + id);
    }
    function closeDetail() { detail.hidden = true; document.body.style.overflow = ''; }
    detail.addEventListener('click', e => { if (e.target === detail || e.target.classList.contains('lightbox-close')) closeDetail(); });
    renderTable();
    if (location.hash && byId[location.hash.slice(1)]) openDetail(location.hash.slice(1));
    addEventListener('keydown', e => { if (e.key === 'Escape') closeDetail(); });
  }

  /* ---------- search ---------- */
  const sBox = $('#search'), sIn = $('#search-input'), sRes = $('#search-results');
  let index = null, sel = -1;
  const base = (document.querySelector('link[rel=stylesheet]').getAttribute('href') || '').replace(/assets\/style\.css.*$/, '');
  function openSearch() { if (!sBox) return; sBox.hidden = false; sIn.value = ''; sRes.innerHTML = ''; sIn.focus(); if (!index) fetch(base + 'search-index.json').then(r => r.json()).then(d => { index = d; }); }
  function closeSearch() { if (sBox) sBox.hidden = true; }
  const sBtn = $('#search-open'); if (sBtn) sBtn.addEventListener('click', openSearch);
  if (sBox) sBox.addEventListener('click', e => { if (e.target === sBox) closeSearch(); });
  addEventListener('keydown', e => {
    if (e.key === '/' && !/input|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); openSearch(); }
    if (e.key === 'Escape') { closeSearch(); closeLightbox(); hideTip(); }
    if (sBox && !sBox.hidden && (e.key === 'ArrowDown' || e.key === 'ArrowUp' || e.key === 'Enter')) {
      const items = $$('a', sRes); if (!items.length) return;
      if (e.key === 'Enter') { (items[sel] || items[0]).click(); return; }
      e.preventDefault(); sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
      items.forEach((a, i) => a.classList.toggle('on', i === sel)); items[sel].scrollIntoView({ block: 'nearest' });
    }
  });
  if (sIn) sIn.addEventListener('input', () => {
    const q = sIn.value.trim().toLowerCase(); sel = -1;
    if (!index || q.length < 2) { sRes.innerHTML = ''; return; }
    const terms = q.split(/\s+/);
    const scored = index.map(it => {
      const t = it.t.toLowerCase(), b = (it.b || '').toLowerCase();
      let s = 0; for (const w of terms) { if (t.includes(w)) s += 10; const n = b.split(w).length - 1; s += Math.min(n, 8); }
      return [s, it];
    }).filter(x => x[0] > 0).sort((a, b) => b[0] - a[0]).slice(0, 12);
    sRes.innerHTML = scored.map(([, it]) => {
      const b = (it.b || ''); const i = b.toLowerCase().indexOf(terms[0]);
      const snip = i >= 0 ? b.slice(Math.max(0, i - 60), i + 90) : it.s;
      const hl = snip.replace(new RegExp('(' + terms.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')', 'gi'), '<mark>$1</mark>');
      return `<a href="${base}${it.u}"><span class="rk">${it.k}</span>${it.t}<span class="rs">…${hl}…</span></a>`;
    }).join('') || '<div class="search-hint">Nothing found.</div>';
  });
})();
