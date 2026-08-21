const $ = (s) => document.querySelector(s);
let payload = { rows: [], coverage: {} };
const fmt = (n) => Number(n).toLocaleString('ja-JP');
function render() {
  const q = $('#search').value.trim().toLowerCase();
  const key = $('#sort').value;
  const rows = payload.rows.filter(x => x.artist.toLowerCase().includes(q)).sort((a,b) => b[key] - a[key] || a.artist.localeCompare(b.artist));
  $('#table').innerHTML = rows.slice(0, 250).map((x, i) => `<tr><td class="rank">${i + 1}</td><td class="artist">${escapeHtml(x.artist)}</td><td>${fmt(x.galleries)}</td><td>${fmt(x.pages)}</td><td>${fmt(x.recent)}</td><td class="score">${x.score}</td></tr>`).join('');
  $('#summary').innerHTML = `<div><strong>${fmt(payload.coverage.artists || 0)}</strong><span>artists</span></div><div><strong>${fmt(payload.coverage.source_rows || 0)}</strong><span>galleries</span></div><div><strong>${payload.coverage.months || 0}</strong><span>months covered</span></div>`;
}
function escapeHtml(v) { return v.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
fetch('data/ranking.json').then(r => r.ok ? r.json() : Promise.reject()).then(x => { payload = x; render(); }).catch(() => { $('#table').innerHTML = '<tr><td colspan="6">データを読み込めませんでした。Actionsの更新を確認してください。</td></tr>'; });
$('#search').addEventListener('input', render); $('#sort').addEventListener('change', render);

