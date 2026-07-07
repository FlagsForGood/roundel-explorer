/* ── Roundel Explorer ─────────────────────────────────────── */

// Three primary methods — the paper's taxonomy
const PRIMARY_METHODS = ['Radial', 'Punch', 'Non Sequitur'];

// Icons matching the paper's taxonomy symbols
const METHOD_ICONS = {
  // Radial: outer circle divided into quadrants by a cross, with a counterclockwise rotation arrow inside
  'Radial': `<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="50" cy="50" r="44" stroke="currentColor" stroke-width="3.5"/>
    <line x1="50" y1="6" x2="50" y2="94" stroke="currentColor" stroke-width="2.5"/>
    <line x1="6" y1="50" x2="94" y2="50" stroke="currentColor" stroke-width="2.5"/>
    <path d="M 71 38 A 24 24 0 1 0 38 71" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
    <path d="M 38 71 L 28 71 M 38 71 L 33 82" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
  </svg>`,
  // Punch: circle with a 5-pointed star whose tips reach toward the edge
  'Punch': `<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="50" cy="50" r="44" stroke="currentColor" stroke-width="3.5"/>
    <line x1="50" y1="6" x2="50" y2="94" stroke="currentColor" stroke-width="2"/>
    <polygon points="50,12 59.4,37.1 86.2,38.3 65.2,54.9 72.3,80.8 50,66 27.7,80.8 34.8,54.9 13.8,38.3 40.6,37.1" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
  </svg>`,
  // Non Sequitur: triangle (flag) + arc wedge (roundel) + diagonal slash — the translation link is severed
  'Non Sequitur': `<svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M 8 10 L 50 10 L 8 52 Z" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"/>
    <path d="M 54 92 A 36 36 0 0 0 90 56 L 90 92 Z" fill="none" stroke="currentColor" stroke-width="4" stroke-linejoin="round"/>
    <line x1="84" y1="10" x2="12" y2="90" stroke="currentColor" stroke-width="4.5" stroke-linecap="round"/>
  </svg>`,
};

const METHOD_DESCRIPTIONS = {
  'Radial': "A striped flag rotates around an axis determined by its stripe orientation: vertical tribands around the hoist edge (hoist color → center); horizontal tribands around the bottom edge (bottom color → center). Stripes become concentric rings. Color relationships are preserved. The method's failure mode is design collapse among nations with similar-colored flags.",
  'Punch':  "A flag's central charge is extracted and placed directly in the circle. The charge must be self-contained — carrying the flag's symbolic meaning without needing field color for context — and geometrically clean enough to read at speed.",
  'Non Sequitur': "The roundel does not follow from the flag. Three causes: political instability (the flag is contested), heraldic tradition (a military symbol pre-dates the flag), or flag complexity (no clean geometric translation is possible). This is not a design failure — it acknowledges that the translation problem sometimes has no clean solution.",
};

// ── Taxonomy component icons (Michael's SVG set) ──────────────
// Normalized SVGs live in icons/taxonomy/. Rendered as CSS masks so they
// inherit currentColor and adapt to light/dark mode.
const TAX_ICON_DIR = 'icons/taxonomy/';

function normVariant(v) {
  const s = (v || '').toLowerCase().replace('−', '-');
  if (s.includes('non-circular') || s.includes('flag charge')) return 'noncircular';
  if (s.includes('inverted') || s.includes('counterclock')) return 'inverted';
  if (s.includes('segment')) return 'segmented';
  if (s.includes('internal')) return 'hoist-internal';
  if (s.includes('+ hoist') || s === '+hoist') return '+hoist';
  if (s.includes('- hoist') || s === '-hoist') return '-hoist';
  if (s.includes('+ charge') || s === '+charge') return '+charge';
  if (s.includes('- charge') || s === '-charge') return '-charge';
  if (s.includes('some stripes') || s.includes('only some')) return 'some';
  if (s.includes('wing')) return 'winged';
  return s;
}

// (method, orientation, variants) → taxonomy icon filename (no extension)
function taxonomyIconFile(d) {
  const V = new Set((d.variants || []).map(normVariant));
  const has = t => V.has(t);
  const m = d.method || d.primaryMethod || '';
  const orient = (d.radialOrientation || '').toLowerCase();
  const segmented = has('segmented') || orient === 'segmented';
  const charge = has('+charge') ? '+charge' : has('-charge') ? '-charge' : '';

  if (m === 'Punch') {
    if (has('winged')) return 'punch+wings';
    if (has('noncircular')) return 'charge-punch';
    return 'punch';
  }
  if (m === 'Non Sequitur') {
    return has('winged') ? 'nonsequitur+wings' : 'nonsequitur';
  }
  // Radial
  if (segmented) {
    if (charge === '+charge') return 'segmented-radial+charge';
    if (charge === '-charge') return 'segmented-radial-charge';
    return 'segmented-radial';
  }
  if (has('inverted')) {
    if (has('some')) return charge === '+charge'
      ? 'radial-inverted-some-internal+charge' : 'radial-inverted-some-internal';
    if (charge === '+charge') return 'inverted-radial+charge';
    if (charge === '-charge') return 'inverted-radial-charge';
    return 'inverted-radial';
  }
  if (has('hoist-internal')) return 'radial-hoist-internal';
  if (has('+hoist')) return 'radial+hoist';
  if (has('-hoist')) return 'radial-hoist';
  if (has('some')) return 'radial-some-internal';
  if (charge === '+charge') return orient === 'vertical' ? 'vertical-radial+charge' : 'radial+charge';
  if (charge === '-charge') return 'radial-charge';
  return orient === 'vertical' ? 'vertical-radial' : 'horizontal-radial';
}

// A tintable taxonomy glyph <span> (CSS mask). `wide` lets composed +charge
// glyphs keep their aspect ratio.
function taxGlyph(d, cls = '') {
  const file = taxonomyIconFile(d);
  // Absolute-from-document URL so it resolves against the page, not the
  // stylesheet (a url() inside a CSS custom property resolves relative to the
  // CSS file). Mask is set inline for the same reason.
  const url = new URL(`${TAX_ICON_DIR}${encodeURIComponent(file)}.svg`, document.baseURI).href;
  const mask = `url('${url}') center/contain no-repeat`;
  return `<span class="tax-glyph ${cls}" role="img" aria-label="${taxonomyLabel(d)}"
    style="-webkit-mask:${mask};mask:${mask}"></span>`;
}

// Human label from an additional-roundel filename, e.g.
// "Roundel_of_Germany_–_Type_1_–_Border.svg.png" → "Type 1 Border"
function labelFromFilename(path) {
  const base = (path.split('/').pop() || '')
    .replace(/\.(svg|png|webp|jpg|jpeg)/gi, '')
    .replace(/^Roundel_of_(the_)?/i, '');
  const m = base.match(/[–\-—]\s*(.+)$/);
  const tail = (m ? m[1] : base).replace(/[_–—]+/g, ' ').replace(/\s+/g, ' ').trim();
  return tail || 'Variant';
}

function taxonomyLabel(d) {
  const m = d.method || d.primaryMethod || '';
  const parts = [];
  if (d.radialOrientation) parts.push(d.radialOrientation);
  (d.variants || []).forEach(v => parts.push(v));
  return parts.length ? `${m} — ${parts.join(', ')}` : m;
}

// ── Vexillological glyphs (FIAV usage grid + IFIS reverse/status) ──
// FIAV national-usage code: 6 bits, row-major, cols Civil/State/War × rows Land/Sea.
function fiavGridSVG(code) {
  if (!code || !/^[01]{6}$/.test(code)) return '';
  const bits = code.split('').map(Number);
  let dots = '';
  const cx = [7, 19, 31], cy = [8, 22];
  for (let r = 0; r < 2; r++) for (let c = 0; c < 3; c++) {
    const on = bits[r * 3 + c];
    dots += `<circle cx="${cx[c]}" cy="${cy[r]}" r="4.4"
      fill="${on ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="1.3"/>`;
  }
  // grid frame
  const frame = `<line x1="13" y1="2" x2="13" y2="28" stroke="currentColor" stroke-width="1"/>
    <line x1="25" y1="2" x2="25" y2="28" stroke="currentColor" stroke-width="1"/>
    <line x1="1" y1="15" x2="37" y2="15" stroke="currentColor" stroke-width="1"/>`;
  return `<svg class="vex-glyph fiav" viewBox="0 0 38 30" aria-label="FIAV usage ${code}">${frame}${dots}</svg>`;
}

// IFIS reverse-side: boxed letter E (congruent) or A (mirror), with an arrow.
function reverseSVG(rev) {
  if (!rev) return '';
  const letter = rev.includes('A') || rev.toLowerCase().includes('mirror') ? 'A' : 'E';
  return `<svg class="vex-glyph reverse" viewBox="0 0 34 30" aria-label="Reverse ${letter}">
    <rect x="8" y="3" width="18" height="14" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.6"/>
    <text x="17" y="14.5" text-anchor="middle" font-size="11" font-weight="700"
      font-family="Georgia, serif" fill="currentColor">${letter}</text>
    <path d="M8 24 H24" stroke="currentColor" stroke-width="1.5"/>
    <path d="M22 21 L26 24 L22 27" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>
  </svg>`;
}

// IFIS flag-status: rectangle (normal), rect+slash (historical), etc.
function statusSVG(status) {
  if (!status || status === 'Normal Version') return '';
  const box = `<rect x="4" y="7" width="26" height="16" rx="1" fill="none" stroke="currentColor" stroke-width="1.6"/>`;
  let extra = '';
  if (status.includes('Historical') || status.includes('Abandoned'))
    extra = `<line x1="4" y1="23" x2="30" y2="7" stroke="currentColor" stroke-width="1.6"/>`;
  else if (status.includes('Different'))
    extra = `<path d="M10 15 H24 M21 12 L25 15 L21 18" fill="none" stroke="currentColor" stroke-width="1.4"/>`;
  else if (status.includes('Variant'))
    extra = `<text x="17" y="19" text-anchor="middle" font-size="12" fill="currentColor">( )</text>`;
  return `<svg class="vex-glyph status" viewBox="0 0 34 30" aria-label="${status}">${box}${extra}</svg>`;
}

// Full vexillological icon row for a record.
// opts.noTax omits the taxonomy glyph (used in the detail modal, where the
// glyph is already shown large next to the method badge).
function vexRow(d, opts = {}) {
  const bits = [
    statusSVG(d.flagStatus),
    fiavGridSVG(d.flagFiavCode),
    reverseSVG(d.flagReverseSide),
    opts.noTax ? '' : taxGlyph(d),
  ].filter(Boolean);
  if (!bits.length) return '';
  return `<div class="vex-row ${opts.large ? 'vex-row-lg' : ''}">${bits.join('')}</div>`;
}

// Larger markers for vast countries where a single marker floats alone over huge territory
const LARGE_COUNTRY_SIZES = {
  'Russia': 74, 'Canada': 68, 'United States': 66, 'China': 64,
  'Australia': 64, 'Brazil': 62, 'India': 60, 'Argentina': 58,
  'Kazakhstan': 58, 'Algeria': 56, 'DR Congo': 56, 'Saudi Arabia': 56,
  'Mexico': 54, 'Indonesia': 54, 'Sudan': 54, 'Libya': 54,
  'Iran': 52, 'Mongolia': 52, 'Peru': 52, 'Chad': 52,
  'Niger': 52, 'Angola': 52, 'Mali': 52, 'South Africa': 50,
};

let allData = [];
let globeInstance = null;
let globeFailed = false;

// ── Scroll-reveal motion (Taste layer) ───────────────────────
const revealObserver = ('IntersectionObserver' in window)
  ? new IntersectionObserver((entries, obs) => {
      entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('in'); obs.unobserve(e.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 })
  : null;

// Add .reveal to each element and observe it, with a staggered transition delay.
function applyReveal(elements, { stagger = 60, max = 480 } = {}) {
  if (!revealObserver) return;
  elements.forEach((el, i) => {
    el.classList.add('reveal');
    el.style.transitionDelay = Math.min(i * stagger, max) + 'ms';
    revealObserver.observe(el);
  });
  // Safety net: never leave content invisible if the observer doesn't fire
  // (e.g. built inside a display:none view that later shows without an IO tick).
  setTimeout(() => elements.forEach(el => el.classList.add('in')), 1200);
}
let activeFilters = { taxonomy: new Set(), symbol: false, collapse: false, search: '' };

// ── Boot ─────────────────────────────────────────────────
fetch('data/roundels.json')
  .then(r => r.json())
  .then(data => {
    // Only nations that actually have a roundel image are shown. Placeholder
    // records (every other nation on earth, added so they're ready in Airtable)
    // stay hidden until they get a roundel — then they appear automatically.
    allData = data.filter(d => d.roundelImage || d.hasRoundel);
    initNav();
    buildGlobeLegend();
    buildGalleryFilters();
    buildGallery();
    buildLegend();
    buildSimilarView();
    initDetail();
    showView('globe');
  })
  .catch(err => {
    document.body.innerHTML = `<div style="padding:40px;font-family:sans-serif;color:#c41e3a">
      <h2>Data not found</h2>
      <p>Run <code>python3 build_data.py</code> from the <code>roundel-explorer/</code> directory to generate roundels.json.</p>
      <pre style="margin-top:12px;font-size:12px">${err}</pre></div>`;
  });

// ── Navigation ────────────────────────────────────────────
// Slide the capsule-nav indicator under the active button.
function moveNavIndicator() {
  const nav = document.querySelector('.main-nav');
  const ind = nav && nav.querySelector('.nav-indicator');
  const active = nav && nav.querySelector('.nav-btn.active');
  if (!ind || !active) return;
  ind.style.width = active.offsetWidth + 'px';
  ind.style.transform = `translateX(${active.offsetLeft}px)`;
}

function initNav() {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => showView(btn.dataset.view));
  });
  // Position the indicator once fonts/layout settle, and keep it in sync.
  requestAnimationFrame(moveNavIndicator);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(moveNavIndicator);
  window.addEventListener('resize', moveNavIndicator);
  // Inline links that jump to a view (e.g. "Legend" mention on About page)
  document.addEventListener('click', e => {
    const link = e.target.closest('.inline-link[data-view]');
    if (link) { e.preventDefault(); showView(link.dataset.view); window.scrollTo(0, 0); }
  });
}

function showView(name) {
  document.querySelectorAll('.nav-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.view === name));
  document.querySelectorAll('.view').forEach(v =>
    v.classList.toggle('active', v.id === `view-${name}`));
  if (name === 'globe' && !globeInstance && !globeFailed) initGlobe();
  moveNavIndicator();
  // A view that was display:none doesn't fire IntersectionObserver on show,
  // so deterministically reveal anything now in view (below-fold items still
  // animate in on scroll via the observer).
  requestAnimationFrame(() => flushReveals(document.getElementById(`view-${name}`)));
}

function flushReveals(view) {
  if (!view) return;
  const vh = window.innerHeight;
  view.querySelectorAll('.reveal:not(.in)').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.top < vh + 120 && r.bottom > -120) el.classList.add('in');
  });
}

// ── Globe ────────────────────────────────────────────────
function initGlobe() {
  const container = document.getElementById('globe-container');
  try {
    buildGlobe(container);
  } catch (err) {
    // WebGL unavailable (headless GPU, blocked context, etc.). Degrade
    // gracefully instead of taking the whole app down — the other views work.
    globeFailed = true;
    globeInstance = null;
    console.warn('Globe init failed, falling back:', err);
    container.innerHTML = `<div class="globe-fallback">
      <p>The interactive globe needs WebGL, which isn't available in this browser.</p>
      <button class="inline-link" data-view="gallery">Browse the gallery instead →</button>
    </div>`;
  }
}

function buildGlobe(container) {
  globeInstance = Globe()
    .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
    .backgroundImageUrl('https://unpkg.com/three-globe/example/img/night-sky.png')
    .atmosphereColor('#3a7bd5')
    .atmosphereAltitude(0.12)
    .htmlElementsData(allData)
    .htmlLat(d => d.lat)
    .htmlLng(d => d.lng)
    .htmlAltitude(0.01)
    .htmlTransitionDuration(0)
    .htmlElement(d => makeGlobeMarker(d))
    (container);

  // Country border outlines
  fetch('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
    .then(r => r.json())
    .then(world => {
      const features = topojson.feature(world, world.objects.countries).features;
      globeInstance
        .polygonsData(features)
        .polygonCapColor(() => 'rgba(255,255,255,0.03)')
        .polygonSideColor(() => 'transparent')
        .polygonStrokeColor(() => 'rgba(255,255,255,0.22)')
        .polygonAltitude(0.002);
    });

  globeInstance.controls().autoRotate = true;
  globeInstance.controls().autoRotateSpeed = 0.35;
  globeInstance.controls().enableZoom = true;

  container.addEventListener('pointerdown', () => {
    globeInstance.controls().autoRotate = false;
  });
}

function makeGlobeMarker(d) {
  const el = document.createElement('div');
  el.className = 'globe-marker';

  const sz = LARGE_COUNTRY_SIZES[d.nation] || 38;
  el.style.setProperty('--marker-sz', sz + 'px');

  const img = document.createElement('img');
  img.src = d.roundelImage;
  img.alt = d.nation;
  img.onerror = () => { img.style.display = 'none'; };

  const label = document.createElement('div');
  label.className = 'marker-label';
  label.textContent = d.nation;

  el.appendChild(img);
  el.appendChild(label);

  // setPointerCapture is critical: without it, pointerup won't fire on this
  // element if the pointer moves even 1px between down and up.
  el.style.pointerEvents = 'all';
  let downAt = null;
  el.addEventListener('pointerdown', e => {
    downAt = { x: e.clientX, y: e.clientY };
    el.setPointerCapture(e.pointerId);
    e.stopPropagation();
  });
  el.addEventListener('pointerup', e => {
    if (downAt) {
      const dx = e.clientX - downAt.x;
      const dy = e.clientY - downAt.y;
      if (dx * dx + dy * dy < 100) { // < 10px = click, not drag
        openDetail(d);
      }
    }
    downAt = null;
    e.stopPropagation();
  });

  return el;
}

function buildGlobeLegend() {
  const container = document.querySelector('.legend-items');
  PRIMARY_METHODS.forEach(method => {
    const item = document.createElement('div');
    item.className = 'legend-item';
    item.innerHTML = `
      <span class="legend-method-icon">${METHOD_ICONS[method] || ''}</span>
      <span>${method}</span>
    `;
    container.appendChild(item);
  });
}

// ── Gallery ───────────────────────────────────────────────
function buildGalleryFilters() {
  const group = document.getElementById('filter-taxonomy');

  PRIMARY_METHODS.forEach(method => {
    const label = document.createElement('label');
    label.className = 'filter-item';
    label.innerHTML = `
      <input type="checkbox" value="${method}">
      <span class="filter-method-icon">${METHOD_ICONS[method] || ''}</span>
      <span class="filter-tax-name">${method}</span>
    `;
    label.querySelector('input').addEventListener('change', e => {
      if (e.target.checked) activeFilters.taxonomy.add(method);
      else activeFilters.taxonomy.delete(method);
      buildGallery();
    });
    group.appendChild(label);
  });

  document.getElementById('filter-symbol').addEventListener('change', e => {
    activeFilters.symbol = e.target.checked;
    buildGallery();
  });
  document.getElementById('filter-collapse').addEventListener('change', e => {
    activeFilters.collapse = e.target.checked;
    buildGallery();
  });
  document.getElementById('search-input').addEventListener('input', e => {
    activeFilters.search = e.target.value.toLowerCase().trim();
    buildGallery();
  });
}

function getFilteredData() {
  return allData.filter(d => {
    if (activeFilters.taxonomy.size > 0 && !activeFilters.taxonomy.has(d.primaryMethod)) return false;
    if (activeFilters.symbol && !d.hasCenterSymbol) return false;
    if (activeFilters.collapse && !d.designCollapse) return false;
    if (activeFilters.search && !d.nation.toLowerCase().includes(activeFilters.search)) return false;
    return true;
  });
}

function methodLabel(d) {
  return d.method || d.primaryMethod || '';
}

function buildGallery() {
  const grid = document.getElementById('gallery-grid');
  const filtered = getFilteredData();
  document.getElementById('result-count').textContent = filtered.length;

  grid.innerHTML = '';
  filtered.forEach(d => {
    const card = document.createElement('div');
    card.className = 'gallery-card';
    card.innerHTML = `
      <div class="card-images">
        <img class="card-flag" src="${d.flagUrl}" alt="${d.nation} flag" onerror="this.style.display='none'">
        <span class="card-arrow">→</span>
        <img class="card-roundel" src="${d.roundelImage}" alt="${d.nation} roundel" onerror="this.style.opacity='.2'">
      </div>
      <div class="card-body">
        <div class="card-nation">${d.nation}</div>
        <div class="card-tax-row">
          <span class="method-badge" data-method="${methodLabel(d)}">${methodLabel(d)}</span>
        </div>
        ${vexRow(d)}
        ${d.designCollapse ? '<div class="card-collapse">Design collapse risk</div>' : ''}
      </div>
    `;
    card.addEventListener('click', () => openDetail(d));
    grid.appendChild(card);
  });
  applyReveal([...grid.children], { stagger: 35, max: 400 });
}

// ── Legend view ───────────────────────────────────────────
function buildLegend() {
  buildLegendIFIS();
  buildLegendMethods();
  applyReveal([...document.querySelectorAll('#view-legend .legend-entry')], { stagger: 25, max: 300 });
}

function legendItem(glyphHTML, title, desc) {
  return `<div class="legend-entry">
    <div class="legend-glyph">${glyphHTML}</div>
    <div class="legend-text"><strong>${title}</strong><span>${desc}</span></div>
  </div>`;
}

function buildLegendIFIS() {
  const el = document.getElementById('legend-ifis');
  if (!el) return;
  el.innerHTML = `
    <h3>Flag Grammar — FIAV &amp; IFIS</h3>
    <p class="legend-block-sub">Standard vexillological notation, describing the national flag each roundel derives from.</p>
    <div class="legend-grid">
      ${legendItem(fiavGridSVG('111111'),
        'Usage grid', 'A 2×3 matrix — columns Civil / State / War, rows Land / Sea. A filled dot marks each context in which the flag is flown.')}
      ${legendItem(statusSVG('Historical (Abandoned)'),
        'Historical design', 'The flag or marking shown is a historical design, now abandoned.')}
      ${legendItem(statusSVG('Different'),
        'Different obverse', 'The obverse (front) carries a different design from the reverse.')}
      ${legendItem(reverseSVG('Congruent (E)'),
        'Reverse congruent (E)', 'The reverse side is congruent — identical to the obverse read through the cloth.')}
      ${legendItem(reverseSVG('Mirror Image (A)'),
        'Reverse mirrored (A)', 'The reverse side is a mirror image of the obverse.')}
    </div>`;
}

// Sample "records" that drive the taxonomy glyph for each legend row.
const LEGEND_METHODS = [
  {
    method: 'Punch', blurb: METHOD_DESCRIPTIONS['Punch'],
    rows: [
      [{ method: 'Punch' }, 'Punch', 'A charge lifted straight from the flag into the disc.'],
      [{ method: 'Punch', variants: ['Non-Circular or Flag Charge'] }, 'Non-circular / flag charge', 'The punched element keeps a non-circular or literal flag-charge form.'],
      [{ method: 'Punch', variants: ['+ Winged Roundel'] }, '+ Winged roundel', 'Wings or bars flank the roundel.'],
    ],
  },
  {
    method: 'Radial', blurb: METHOD_DESCRIPTIONS['Radial'],
    rows: [
      [{ method: 'Radial', radialOrientation: 'Horizontal' }, 'Horizontal radial', 'Horizontal stripes wrapped into rings around the bottom edge.'],
      [{ method: 'Radial', radialOrientation: 'Vertical' }, 'Vertical radial', 'Vertical stripes wrapped around the hoist.'],
      [{ method: 'Radial', variants: ['Inverted / Counterclockwise'] }, 'Inverted / counterclockwise', 'Ring order reversed from the standard reading.'],
      [{ method: 'Radial', variants: ['Segmented'] }, 'Segmented', 'Pie segments instead of concentric rings.'],
      [{ method: 'Radial', variants: ['+ Hoist Element'] }, '± Hoist element', 'The flag\'s hoist element is kept (+) or dropped (−).'],
      [{ method: 'Radial', variants: ['Hoist Element Internalized'] }, 'Hoist internalized', 'The hoist element is moved to the roundel\'s center.'],
      [{ method: 'Radial', variants: ['Only Some Stripes Used'] }, 'Only some stripes', 'Only a subset of the flag\'s stripes become rings.'],
      [{ method: 'Radial', variants: ['+ Charge'] }, '± Charge', 'A charge is added (+) or omitted (−) over the rings.'],
    ],
  },
  {
    method: 'Non Sequitur', blurb: METHOD_DESCRIPTIONS['Non Sequitur'],
    rows: [
      [{ method: 'Non Sequitur' }, 'Non sequitur', 'The roundel does not derive from the current flag.'],
      [{ method: 'Non Sequitur', variants: ['+ Winged Roundel'] }, '+ Winged roundel', 'Wings or bars flank an unrelated device.'],
    ],
  },
];

function buildLegendMethods() {
  const el = document.getElementById('legend-methods');
  if (!el) return;
  el.innerHTML = '<h3>Translation Methods</h3>';
  LEGEND_METHODS.forEach(group => {
    const section = document.createElement('div');
    section.className = 'legend-method-section';
    const rows = group.rows.map(([rec, title, desc]) =>
      legendItem(taxGlyph(rec, 'tax-glyph-lg'), title, desc)).join('');
    section.innerHTML = `
      <div class="legend-method-head" data-method="${group.method}">
        <span class="method-badge" data-method="${group.method}">${group.method}</span>
      </div>
      <p class="legend-method-blurb">${group.blurb || ''}</p>
      <div class="legend-grid">${rows}</div>`;
    el.appendChild(section);
  });
}

// ── Similar view ──────────────────────────────────────────
function buildSimilarView() {
  buildCollapseSection();
  buildTaxonomyClusters();
}

function buildCollapseSection() {
  const grid = document.getElementById('collapse-grid');
  const seen = new Set();

  allData.filter(d => d.designCollapse).forEach(d => {
    const key = [d.nation, ...(d.designCollapseWith || [])].sort().join('|');
    if (seen.has(key)) return;
    seen.add(key);

    const pair = document.createElement('div');
    pair.className = 'collapse-pair';
    pair.innerHTML = `
      <img class="collapse-roundel" src="${d.roundelImage}" alt="${d.nation}" onerror="this.style.opacity='.2'">
      <div class="collapse-info">
        <strong>${d.nation}</strong>
        <span>${d.designCollapseWith && d.designCollapseWith.length
          ? '≈ ' + d.designCollapseWith.join(', ')
          : 'visually ambiguous'}</span>
      </div>
    `;
    pair.addEventListener('click', () => openDetail(d));
    grid.appendChild(pair);
  });

  if (!allData.some(d => d.designCollapse)) {
    document.getElementById('collapse-alert').classList.add('hidden');
  }
}

function buildTaxonomyClusters() {
  const container = document.getElementById('similar-clusters');

  PRIMARY_METHODS.forEach(method => {
    const members = allData.filter(d => d.primaryMethod === method);
    if (!members.length) return;

    // Group by subMethod within each primary
    const subGroups = {};
    members.forEach(d => {
      const key = d.subMethod || 'General';
      if (!subGroups[key]) subGroups[key] = [];
      subGroups[key].push(d);
    });

    const section = document.createElement('div');
    section.className = 'cluster-section';
    section.innerHTML = `
      <div class="cluster-heading">
        <span class="cluster-icon">${METHOD_ICONS[method] || ''}</span>
        <h3>${method} Method</h3>
        <span class="cluster-count">${members.length} nations</span>
      </div>
      <p class="cluster-description">${METHOD_DESCRIPTIONS[method] || ''}</p>
      <div class="cluster-subclusters"></div>
    `;

    const subContainer = section.querySelector('.cluster-subclusters');
    Object.entries(subGroups)
      .sort((a, b) => b[1].length - a[1].length)
      .forEach(([sub, subMembers]) => {
        const subEl = document.createElement('div');
        subEl.className = 'subcluster';
        subEl.innerHTML = `
          <div class="subcluster-label">${sub} <span class="cluster-count">${subMembers.length}</span></div>
          <div class="cluster-grid"></div>
        `;
        const grid = subEl.querySelector('.cluster-grid');
        subMembers.sort((a, b) => a.nation.localeCompare(b.nation)).forEach(d => {
          const card = document.createElement('div');
          card.className = 'cluster-card';
          card.innerHTML = `
            <img class="cluster-roundel" src="${d.roundelImage}" alt="${d.nation}" onerror="this.style.opacity='.2'">
            <span class="cluster-name">${d.nation}</span>
          `;
          card.addEventListener('click', () => openDetail(d));
          grid.appendChild(card);
        });
        subContainer.appendChild(subEl);
      });

    container.appendChild(section);
  });
}

// ── Detail panel ──────────────────────────────────────────
function initDetail() {
  document.getElementById('detail-close').addEventListener('click', closeDetail);
  document.getElementById('detail-overlay').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeDetail();
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeDetail();
  });
}

function setOrHide(id, value) {
  const el = document.getElementById(id);
  if (!el) return;
  const wrap = el.closest ? el.closest('[id$="-wrap"]') : null;
  if (value) {
    if (wrap) wrap.classList.remove('hidden');
    el.textContent = value;
  } else {
    if (wrap) wrap.classList.add('hidden');
  }
}

function openDetail(d) {
  // Images
  document.getElementById('detail-flag').src = d.flagUrl;
  document.getElementById('detail-roundel').src = d.roundelImage;
  document.getElementById('detail-nation').textContent = d.nation;

  // Method glyph + badge + variant chips
  const method = methodLabel(d);
  document.getElementById('detail-tax-icon').innerHTML = taxGlyph(d, 'tax-glyph-lg');
  const badge = document.getElementById('detail-taxonomy-badge');
  badge.innerHTML = '';
  const b = document.createElement('span');
  b.className = 'method-badge';
  b.setAttribute('data-method', method);
  b.textContent = method;
  badge.appendChild(b);
  if (d.radialOrientation) {
    const o = document.createElement('span');
    o.className = 'sub-badge';
    o.textContent = d.radialOrientation;
    badge.appendChild(o);
  }
  (d.variants || []).forEach(v => {
    const chip = document.createElement('span');
    chip.className = 'variant-chip';
    chip.textContent = v;
    badge.appendChild(chip);
  });
  document.getElementById('detail-tax-description').textContent =
    METHOD_DESCRIPTIONS[d.method || d.primaryMethod] || '';

  // Vexillological icon row (status / FIAV usage / reverse) — no taxonomy
  // glyph here; it's already shown large next to the method badge.
  const vexWrap = document.getElementById('detail-vex-row');
  if (vexWrap) vexWrap.innerHTML = vexRow(d, { large: true, noTax: true });

  // Core fields
  document.getElementById('detail-flag-desc').textContent = d.flagDescription || '—';
  document.getElementById('detail-roundel-desc').textContent = d.roundelDescription || '—';
  document.getElementById('detail-tax-raw').textContent = taxonomyLabel(d) || d.taxonomyRaw || '';
  setOrHide('detail-year', d.yearAdopted);
  setOrHide('detail-status', d.stillInUse);
  setOrHide('detail-fiav', d.flagFiavCode);
  setOrHide('detail-reverse', d.flagReverseSide);

  // Additional roundels: low-vis + historic/variant images
  const addWrap = document.getElementById('detail-additional-wrap');
  const addGrid = document.getElementById('detail-additional-grid');
  if (addWrap && addGrid) {
    const extras = [];
    if (d.lowVisImage) extras.push({ src: d.lowVisImage, label: 'Low-visibility' });
    (d.additionalImages || []).forEach(a => {
      // Support both {src,label} objects (current) and bare path strings (legacy)
      if (typeof a === 'string') extras.push({ src: a, label: labelFromFilename(a) });
      else if (a && a.src) extras.push({ src: a.src, label: a.label || labelFromFilename(a.src) });
    });
    addGrid.innerHTML = '';
    if (extras.length) {
      addWrap.classList.remove('hidden');
      extras.forEach(x => {
        const fig = document.createElement('figure');
        fig.className = 'additional-item';
        fig.innerHTML = `<img src="${x.src}" alt="${x.label}" loading="lazy"
          onerror="this.closest('.additional-item').style.display='none'">
          <figcaption>${x.label}</figcaption>`;
        addGrid.appendChild(fig);
      });
    } else {
      addWrap.classList.add('hidden');
    }
  }

  // Fin flash
  document.getElementById('detail-fin').textContent = d.finFlash || '—';
  const ffImg = document.getElementById('detail-finflash-img');
  if (d.finFlashImage) {
    ffImg.src = d.finFlashImage;
    ffImg.classList.remove('hidden');
  } else {
    ffImg.src = '';
    ffImg.classList.add('hidden');
  }

  // Historical notes
  const histWrap = document.getElementById('detail-history-wrap');
  if (d.historicalNotes) {
    histWrap.classList.remove('hidden');
    document.getElementById('detail-history').textContent = d.historicalNotes;
  } else {
    histWrap.classList.add('hidden');
  }

  // Analysis
  document.getElementById('detail-notes').textContent = d.notes || '—';

  // Design collapse warning
  const collapseWarn = document.getElementById('detail-collapse-warn');
  if (d.designCollapse) {
    collapseWarn.classList.remove('hidden');
    document.getElementById('detail-collapse-with').textContent =
      d.designCollapseWith && d.designCollapseWith.length
        ? 'Visually identical to: ' + d.designCollapseWith.join(', ')
        : 'Visually ambiguous or non-distinctive.';
  } else {
    collapseWarn.classList.add('hidden');
  }

  // Wikimedia / Commons links
  const commonsLink = document.getElementById('detail-commons-link');
  const wikimediaLink = document.getElementById('detail-wikimedia-img-link');
  if (d.commonsPage) {
    commonsLink.href = d.commonsPage;
    commonsLink.classList.remove('hidden');
  } else {
    commonsLink.classList.add('hidden');
  }
  if (d.wikimediaUrl) {
    wikimediaLink.href = d.wikimediaUrl;
    wikimediaLink.classList.remove('hidden');
  } else {
    wikimediaLink.classList.add('hidden');
  }

  // Further reading
  const frWrap = document.getElementById('detail-further-reading');
  const frLinks = document.getElementById('detail-further-links');
  frLinks.innerHTML = '';
  if (d.furtherReading) {
    frWrap.classList.remove('hidden');
    d.furtherReading.split(',').map(s => s.trim()).filter(Boolean).forEach(url => {
      const a = document.createElement('a');
      a.href = url;
      a.target = '_blank';
      a.className = 'detail-link';
      a.textContent = url.replace(/^https?:\/\/(www\.)?/, '').split('/')[0];
      frLinks.appendChild(a);
    });
  } else {
    frWrap.classList.add('hidden');
  }

  // Similar roundels — same primary method, prefer same sub-method first
  const similar = allData
    .filter(r => r.nation !== d.nation && r.primaryMethod === d.primaryMethod)
    .sort((a, b) => (b.subMethod === d.subMethod ? 1 : 0) - (a.subMethod === d.subMethod ? 1 : 0))
    .slice(0, 8);
  const row = document.getElementById('detail-similar-row');
  row.innerHTML = '';
  similar.forEach(r => {
    const chip = document.createElement('div');
    chip.className = 'similar-chip';
    chip.innerHTML = `
      <img src="${r.roundelImage}" alt="${r.nation}" onerror="this.style.opacity='.2'">
      <span>${r.nation}</span>
    `;
    chip.addEventListener('click', () => openDetail(r));
    row.appendChild(chip);
  });

  document.getElementById('detail-overlay').classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}

function closeDetail() {
  document.getElementById('detail-overlay').classList.add('hidden');
  document.body.style.overflow = '';
}
