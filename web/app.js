
async function loadJSON(path){
  try{ const res = await fetch(path); if(!res.ok) throw new Error(res.status); return await res.json(); }
  catch(e){ return null; }
}
(async()=>{
  const headlines = await loadJSON('/data/latest_headlines.json');
  const summary = await loadJSON('/data/latest_summary.json');
  document.getElementById('headlines').textContent = headlines ? JSON.stringify(headlines.slice(0,10), null, 2) : 'No data yet.';
  document.getElementById('summary').textContent = summary ? JSON.stringify(summary, null, 2) : 'No data yet.';
})();
