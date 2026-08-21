const $ = (s) => document.querySelector(s);
let datasets = {};
let entity = 'artists';
const fmt = (n) => Number(n).toLocaleString('ja-JP');
function render() {
  const payload = datasets[entity] || { rows: [], coverage: {} };
  const nameKey = entity === 'artists' ? 'artist' : 'character';
  const q = $('#search').value.trim().toLowerCase();
  const key = $('#sort').value;
  const rows = payload.rows.filter(x => x[nameKey].toLowerCase().includes(q)).sort((a,b) => b[key] - a[key] || a[nameKey].localeCompare(b[nameKey]));
  $('#name-heading').textContent = entity === 'artists' ? 'Artist' : 'Character';
  $('#table').innerHTML = rows.slice(0, 250).map((x, i) => `<tr><td class="rank">${i + 1}</td><td class="artist"><a href="${escapeAttr(x[entity === 'artists' ? 'artist_url' : 'character_url'])}" target="_blank" rel="noopener noreferrer">${escapeHtml(x[nameKey])}</a></td><td class="score">${fmt(x.favorites)}</td><td>${fmt(x.median_favorites)}</td><td>${fmt(x.top_favorites)}</td><td>${fmt(x.galleries)}</td><td class="tags">${(x.top_tags || []).map(tag => `<span>${escapeHtml(tag)}</span>`).join('')}</td></tr>`).join('');
  const limit = entity === 'artists' ? payload.coverage.artist_limit : payload.coverage.character_limit;
  const total = entity === 'artists' ? payload.coverage.artist_tags_total : payload.coverage.character_tags_total;
  $('#summary').innerHTML = `<div><strong>${fmt(limit || 0)}</strong><span>${entity} ranked</span></div><div><strong>${fmt(total || 0)}</strong><span>${entity} tags</span></div><div><strong>${fmt(payload.coverage.api_requests || 0)}</strong><span>API requests</span></div>`;
}
function escapeHtml(v) { return v.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function escapeAttr(v) { return escapeHtml(v || '#'); }
Promise.all([fetch('data/favorites-ranking.json').then(r => r.json()), fetch('data/characters-ranking.json').then(r => r.json())]).then(([artists, characters]) => { datasets = { artists, characters }; render(); }).catch(() => { $('#table').innerHTML = '<tr><td colspan="7">データを読み込めませんでした。Actionsの更新を確認してください。</td></tr>'; });
$('#search').addEventListener('input', render); $('#sort').addEventListener('change', render);
document.querySelectorAll('[data-entity]').forEach(button => button.addEventListener('click', () => { entity = button.dataset.entity; document.querySelectorAll('[data-entity]').forEach(x => x.classList.toggle('active', x === button)); $('#search').value = ''; render(); }));
