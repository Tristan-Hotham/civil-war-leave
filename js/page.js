/* Roundhead or Cavalier, Leave or Remain? Map of 2010 constituencies (England and Wales) with the Danelaw line,
   historic counties coloured by the share of their 1640 members who joined the King, and the 1640 boroughs. */
(function () {
  const STYLE = 'https://tiles.openfreemap.org/styles/positron';
  const LEAVE = [25, '#1f4e79', 37.5, '#7ea6c9', 50, '#eeeae2', 62.5, '#e3a26b', 75, '#9c4a12'];
  const ROY = [0, '#4E7A63', 25, '#A9C0B1', 50, '#EFE7D6', 75, '#D9958F', 100, '#9B2D30'];
  const SCAND = [0, '#f3efe6', 5, '#cfdccf', 15, '#7fa58e', 30, '#2f5d48'];
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const f1 = v => v == null ? 'n/a' : (Math.round(v * 10) / 10).toFixed(1);
  let mode = 'leave';

  const tb = document.getElementById('theme');
  try { const t = localStorage.getItem('cwl-theme'); if (t) document.documentElement.dataset.theme = t; } catch (e) {}
  tb.addEventListener('click', () => {
    const cur = document.documentElement.dataset.theme || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    const nx = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = nx;
    try { localStorage.setItem('cwl-theme', nx); } catch (e) {}
  });
  const card = document.getElementById('cartouche');
  document.getElementById('ctFold').onclick = () => card.classList.add('folded');
  document.getElementById('ctToggle').onclick = () => card.classList.toggle('folded');
  if (window.innerWidth < 600) card.classList.add('folded');
  const lp = document.getElementById('lp'), lpb = document.getElementById('lyrBtn');
  lpb.addEventListener('click', () => { lp.classList.toggle('open'); lpb.setAttribute('aria-expanded', lp.classList.contains('open')); });

  const map = new maplibregl.Map({ container: 'map', style: STYLE, bounds: [[-5.8, 49.9], [1.8, 55.85]], fitBoundsOptions: { padding: 24 },
    attributionControl: { compact: true }, maxZoom: 14, minZoom: 4 });
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
  window.__map = map;

  const grad = st => { const s = []; for (let i = 0; i < st.length; i += 2) s.push(`${st[i + 1]} ${(st[i] - st[0]) / (st[st.length - 2] - st[0]) * 100}%`); return `linear-gradient(90deg,${s.join(',')})`; };
  function legend() {
    const K = document.getElementById('keys');
    const line = '<div class="row"><span style="display:inline-block;width:22px;border-top:3px solid #22201C"></span>Danelaw line: treaty text, then Watling Street to Chester</div>';
    if (mode === 'leave') K.innerHTML = `<b>Estimated Leave share, 2016</b><div class="bar" style="background:${grad(LEAVE)}"></div><div class="ends"><span>25%</span><span>50%</span><span>75%</span></div>${line}<div class="row kx" style="color:#6E604E">2010 constituencies, England and Wales. Scotland not studied.</div>`;
    else if (mode === 'dl') K.innerHTML = `<b>Side of the Danelaw line</b><div class="row"><span class="sw" style="background:#D8B98C"></span>Danelaw side (half the seat or more)</div><div class="row"><span class="sw" style="background:#C9D3D6"></span>Other side, and Wales</div>${line}<div class="row kx" style="color:#6E604E">Darker edges: seats split by the line.</div>`;
    else if (mode === 'king') K.innerHTML = `<b>Members of 1640 who joined the King</b><div class="bar" style="background:${grad(ROY)}"></div><div class="ends"><span>none</span><span>half</span><span>all</span></div><div class="row kx" style="color:#6E604E">Share of each historic county's members (county and boroughs) later disabled for siding with the King, mostly 1642 to 1644. Members, not territory. Grey: Durham, no members.</div><div class="row"><span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#EFE7D6;border:1px solid #2B2119;margin-right:6px"></span>Dots: 1640 boroughs, same colours for the borough's own members; bigger dot, more members</div>${line}`;
    else K.innerHTML = `<b>Viking village names</b><div class="bar" style="background:${grad(SCAND)}"></div><div class="ends"><span>0%</span><span>15%</span><span>30%</span></div>${line}<div class="row kx" style="color:#6E604E">Share of each seat's Wikidata settlements ending -by, -thorpe, -thwaite or -toft. Grey: fewer than 5 settlements.</div>`;
  }
  function setMode(m) {
    mode = m;
    document.querySelectorAll('.chip[data-m]').forEach(c => c.setAttribute('aria-pressed', c.dataset.m === m));
    if (map.getLayer('seat-fill')) {
      const seatVis = m === 'king' ? 'none' : 'visible';
      map.setLayoutProperty('seat-fill', 'visibility', seatVis);
      map.setLayoutProperty('cty-fill', 'visibility', m === 'king' ? 'visible' : 'none');
      let col;
      if (m === 'leave') col = ['interpolate', ['linear'], ['get', 'lv'], ...LEAVE];
      else if (m === 'dl') col = ['case', ['==', ['get', 'dl'], 1], '#D8B98C', '#C9D3D6'];
      else col = ['case', ['==', ['get', 'sc'], null], '#d9d6d0', ['interpolate', ['linear'], ['get', 'sc'], ...SCAND]];
      if (m !== 'king') map.setPaintProperty('seat-fill', 'fill-color', col);
      map.setPaintProperty('seat-split', 'line-opacity', m === 'dl' ? 0.9 : 0);
      if (m === 'king' && !document.getElementById('lyBor').checked) { document.getElementById('lyBor').checked = true; map.setLayoutProperty('bor', 'visibility', 'visible'); }
    }
    legend();
  }
  document.querySelectorAll('.chip[data-m]').forEach(c => c.addEventListener('click', () => setMode(c.dataset.m)));

  const R = (a, b) => ['interpolate', ['linear'], ['zoom'], 5, a, 11, b];
  map.on('load', async () => {
    document.getElementById('nojs').style.display = 'none';
    document.querySelectorAll('.maplibregl-ctrl-attrib').forEach(a => a.classList.remove('maplibregl-compact-show'));
    const st = map.getStyle();
    const labelLayers = st.layers.filter(l => l.type === 'symbol').map(l => l.id);
    const first = labelLayers[0];
    map.addSource('seats', { type: 'geojson', data: 'data/web/seats.geojson', attribution: 'Leave: Hanretty (2017); boundaries ONS/OS (OGL)' });
    map.addSource('cty', { type: 'geojson', data: 'data/web/counties.geojson', attribution: 'Long Parliament list: Wikipedia (CC BY-SA); counties from Wikidata (CC0)' });
    map.addSource('bor', { type: 'geojson', data: 'data/web/boroughs.geojson' });
    map.addSource('line', { type: 'geojson', data: 'data/web/line.geojson' });
    map.addLayer({ id: 'seat-fill', type: 'fill', source: 'seats', paint: { 'fill-opacity': 0.78, 'fill-color': '#ccc' } }, first);
    map.addLayer({ id: 'cty-fill', type: 'fill', source: 'cty', layout: { visibility: 'none' }, paint: { 'fill-opacity': 0.8,
      'fill-color': ['case', ['==', ['get', 'p'], null], '#d9d6d0', ['interpolate', ['linear'], ['get', 'p'], ...ROY]] } }, first);
    map.addLayer({ id: 'seat-line', type: 'line', source: 'seats', paint: { 'line-color': '#ffffff', 'line-width': R(0.25, 1.4), 'line-opacity': 0.9 } }, first);
    map.addLayer({ id: 'seat-split', type: 'line', source: 'seats', filter: ['all', ['>', ['get', 'da'], 5], ['<', ['get', 'da'], 95]], paint: { 'line-color': '#6E604E', 'line-width': R(0.8, 2.2), 'line-opacity': 0 } }, first);
    map.addLayer({ id: 'cty-line', type: 'line', source: 'cty', layout: { visibility: 'none' }, paint: { 'line-color': '#2B2119', 'line-width': R(0.6, 2), 'line-opacity': 0.7 } });
    map.addLayer({ id: 'pl-line', type: 'line', source: 'line', filter: ['in', ['get', 'k'], ['literal', ['placebo_ne', 'placebo_sw']]], layout: { visibility: 'none' },
      paint: { 'line-color': '#6E604E', 'line-width': R(1.2, 2.5), 'line-dasharray': [2, 2] } });
    map.addLayer({ id: 'dl-halo', type: 'line', source: 'line', filter: ['==', ['get', 'k'], 'line'], paint: { 'line-color': '#ffffff', 'line-width': R(5, 9), 'line-opacity': 0.8 } });
    map.addLayer({ id: 'dl-line', type: 'line', source: 'line', filter: ['==', ['get', 'k'], 'line'], paint: { 'line-color': '#22201C', 'line-width': R(2.4, 4.5) } });
    map.addLayer({ id: 'seat-hi', type: 'line', source: 'seats', filter: ['==', ['get', 'c'], ''], paint: { 'line-color': '#22201C', 'line-width': 2.4 } });
    map.addLayer({ id: 'bor', type: 'circle', source: 'bor', layout: { visibility: 'none' }, paint: {
      'circle-radius': ['interpolate', ['linear'], ['zoom'], 5, ['+', 3, ['get', 's']], 11, ['+', 7, ['*', 2, ['get', 's']]]],
      'circle-color': ['interpolate', ['linear'], ['/', ['*', 100, ['get', 'r']], ['get', 's']], ...ROY],
      'circle-stroke-color': '#2B2119', 'circle-stroke-width': R(0.8, 1.5) } });
    setMode('leave');
    const vis = { lyLine: ['dl-line', 'dl-halo'], lyBor: ['bor'], lyCty: ['cty-line'], lyPl: ['pl-line'], lySeat: ['seat-line'], lyB: labelLayers };
    Object.keys(vis).forEach(id => document.getElementById(id).addEventListener('change', e => vis[id].forEach(l => map.getLayer(l) && map.setLayoutProperty(l, 'visibility', e.target.checked ? 'visible' : 'none'))));

    const pop = new maplibregl.Popup({ maxWidth: '330px' });
    const seatHTML = p => `<b class="t">${esc(p.n)}</b><table>
      <tr><td>Leave 2016</td><td>${f1(p.lv)}%${p.lk === true || p.lk === 'true' ? ' (counted wards)' : ' (estimate)'}</td></tr>
      <tr><td>Danelaw line</td><td>${p.dl == 1 ? 'Danelaw side' : 'English side'} (${p.da}% of area on the Danelaw side; ${Math.abs(p.sd)} km from the line)</td></tr>
      <tr><td>Medieval shire lists</td><td>${p.ds == 1 ? 'one of the 15 Danelaw shires' : 'not a Danelaw shire'}</td></tr>
      <tr><td>Historic county</td><td>${esc(p.hc)}</td></tr>
      <tr><td>Members of 1640 for the King</td><td>${p.rs == null ? 'no members (Durham)' : `${p.cr} of ${p.cs} (${p.rs}%) in ${esc(p.hc)}`}</td></tr>
      <tr><td>Viking village names</td><td>${p.sc == null ? `too few settlements (${p.ns})` : `${p.nk} of ${p.ns} (${f1(p.sc)}%)`}</td></tr>
      <tr><td>UKIP 2015</td><td>${f1(p.uk)}%</td></tr><tr><td>Reform UK 2024</td><td>${f1(p.rf)}% (approx.)</td></tr></table>
      ${p.bn ? `<div class="nt">Borough of 1640 inside: ${esc(p.bn)}</div>` : ''}<div class="nt">${esc(p.rg)}. Leave: Hanretty (2017).</div>`;
    const ctyHTML = p => `<b class="t">${esc(p.n)}</b>${p.s == null ? 'Returned no members to the Long Parliament in 1640.' : `<table><tr><td>Seats in 1640</td><td>${p.s} in ${p.k} constituencies</td></tr><tr><td>Joined the King</td><td>${p.r} (${p.p}%)</td></tr></table>`}<div class="nt">Members who were later disabled for siding with the King, mostly 1642 to 1644 (Wikipedia list of members elected in 1640). Historic county rebuilt from Wikidata places, approximate.</div>`;
    const borHTML = p => `<b class="t">${esc(p.n)}</b>${esc(p.c)}, ${p.s} seat${p.s > 1 ? 's' : ''} in 1640<table><tr><td>Members</td><td>${esc(p.m)}</td></tr><tr><td>For the King</td><td>${p.r} of ${p.s}</td></tr></table>${p.t ? `<div class="nt">List notes: ${esc(p.t)}</div>` : ''}<div class="nt">Source: Wikipedia, List of MPs elected to the English Parliament in 1640 (November), CC BY-SA 4.0.</div>`;
    map.on('click', e => {
      const lays = ['bor', 'cty-fill', 'seat-fill'].filter(l => map.getLayoutProperty(l, 'visibility') !== 'none');
      const f = map.queryRenderedFeatures(e.point, { layers: lays });
      const b = f.find(x => x.layer.id === 'bor'), c = f.find(x => x.layer.id === 'cty-fill'), s = f.find(x => x.layer.id === 'seat-fill');
      let html;
      if (b) html = borHTML(b.properties);
      else if (c) html = ctyHTML(c.properties);
      else if (s) { html = seatHTML(s.properties); map.setFilter('seat-hi', ['==', ['get', 'c'], s.properties.c]); }
      else return;
      pop.setLngLat(e.lngLat).setHTML(html).addTo(map);
    });
    ['bor', 'cty-fill', 'seat-fill'].forEach(l => { map.on('mouseenter', l, () => map.getCanvas().style.cursor = 'pointer'); map.on('mouseleave', l, () => map.getCanvas().style.cursor = ''); });

    const [sj, cj, bj] = await Promise.all(['seats', 'counties', 'boroughs'].map(n => fetch(`data/web/${n}.geojson`).then(r => r.json())));
    const bbox = g => { let a = [180, 90, -180, -90]; const walk = c => typeof c[0] === 'number' ? (a = [Math.min(a[0], c[0]), Math.min(a[1], c[1]), Math.max(a[2], c[0]), Math.max(a[3], c[1])]) : c.forEach(walk); walk(g.coordinates); return a; };
    const items = [];
    sj.features.forEach(f => items.push({ n: f.properties.n, t: 'constituency', b: bbox(f.geometry), p: f.properties, k: 's' }));
    cj.features.forEach(f => items.push({ n: f.properties.n, t: 'historic county', b: bbox(f.geometry), p: f.properties, k: 'c' }));
    bj.features.forEach(f => items.push({ n: f.properties.n, t: `borough of 1640, ${f.properties.c}`, c: f.geometry.coordinates, p: f.properties, k: 'b' }));
    const q = document.getElementById('q'), sug = document.getElementById('sug');
    let cur = [], sel = -1;
    const norm = s => s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
    function go(it) {
      sug.style.display = 'none'; q.value = it.n;
      if (it.k === 's') { map.fitBounds([[it.b[0], it.b[1]], [it.b[2], it.b[3]]], { padding: 60, maxZoom: 11 }); map.setFilter('seat-hi', ['==', ['get', 'c'], it.p.c]); pop.setLngLat([(it.b[0] + it.b[2]) / 2, (it.b[1] + it.b[3]) / 2]).setHTML(seatHTML(it.p)).addTo(map); }
      else if (it.k === 'c') { setMode('king'); pop.remove(); map.fitBounds([[it.b[0], it.b[1]], [it.b[2], it.b[3]]], { padding: 40, maxZoom: 9 }); map.once('moveend', () => pop.setLngLat(map.getCenter()).setHTML(ctyHTML(it.p)).addTo(map)); }
      else { document.getElementById('lyBor').checked = true; map.setLayoutProperty('bor', 'visibility', 'visible'); map.flyTo({ center: it.c, zoom: 10 }); pop.setLngLat(it.c).setHTML(borHTML(it.p)).addTo(map); }
    }
    function render() {
      sug.innerHTML = cur.map((it, i) => `<li role="option" aria-selected="${i === sel}" data-i="${i}">${esc(it.n)} <span>${esc(it.t)}</span></li>`).join('');
      sug.style.display = cur.length ? 'block' : 'none';
    }
    q.addEventListener('input', () => {
      const v = norm(q.value.trim()); sel = -1;
      if (v.length < 2) { cur = []; render(); return; }
      const a = items.filter(it => norm(it.n).startsWith(v)), b2 = items.filter(it => !norm(it.n).startsWith(v) && norm(it.n).includes(v));
      cur = a.concat(b2).slice(0, 12); render();
    });
    q.addEventListener('keydown', e => {
      if (e.key === 'ArrowDown') { sel = Math.min(sel + 1, cur.length - 1); render(); e.preventDefault(); }
      else if (e.key === 'ArrowUp') { sel = Math.max(sel - 1, 0); render(); e.preventDefault(); }
      else if (e.key === 'Enter' && cur.length) go(cur[Math.max(sel, 0)]);
      else if (e.key === 'Escape') sug.style.display = 'none';
    });
    sug.addEventListener('mousedown', e => { const li = e.target.closest('li'); if (li) { e.preventDefault(); go(cur[+li.dataset.i]); } });
    const qs = new URLSearchParams(location.search);
    if (qs.get('mode')) setMode(qs.get('mode'));
  });
})();
