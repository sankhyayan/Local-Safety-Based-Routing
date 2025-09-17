import { state, COLORS } from './state.js';
import { ui, addMessage } from './ui.js';

export function displayRoute(data){
  clearRoutes();
  if(!data?.ranked_routes?.length){ addMessage('No ranked routes','error'); return; }
  state.rankedData = data.ranked_routes;
  state.activeRouteIndex = 0;
  rebuildLayers();
  renderScoreboard();
  const top3 = state.rankedData.slice(0,3).map((r,i)=>`#${i+1} score=${r.score.toFixed(2)} dist ${(r.distance/1000).toFixed(2)}km`);
  addMessage(top3.join(' | '));
}

export function rebuildLayers(){
  state.currentRouteLayers.forEach(l=> state.map.removeLayer(l));
  state.currentRouteLayers = [];
  state.rankedData.slice(0,3).forEach((rr,i)=>{
    if(!rr.route?.points?.coordinates) return;
    const coords = rr.route.points.coordinates.map(pt=>[pt[1],pt[0]]);
    const active = (i===state.activeRouteIndex);
    const layer = L.polyline(coords,{
      color: COLORS.ranks[i]||'#666',
      weight: active?8:(i===0?6:4),
      opacity: active?1:(i===0?0.95:0.65),
      dashArray: i===0?null:'6,8'
    }).addTo(state.map);
    layer.bindPopup(`Rank #${i+1}<br>Score ${rr.score.toFixed(2)}<br>Dist ${(rr.distance/1000).toFixed(2)} km`);
    if(active){ state.map.fitBounds(coords); layer.bringToFront(); }
    state.currentRouteLayers.push(layer);
  });
}

export function renderScoreboard(){
  const tb = ui.tableBody(); if(!tb) return; tb.innerHTML='';
  state.rankedData.forEach((r,i)=>{
    const tr=document.createElement('tr'); tr.dataset.idx=i; if(i===state.activeRouteIndex) tr.classList.add('active');
    tr.innerHTML = `<td>${i+1}</td><td>${r.score.toFixed(2)}</td><td>${(r.distance/1000).toFixed(2)}</td><td>${Math.round((r.time||0)/60000)}</td>`;
    tr.addEventListener('click',()=>{ state.activeRouteIndex=i; rebuildLayers(); renderScoreboard(); });
    tb.appendChild(tr);
  });
}

export function clearRoutes(){
  state.currentRouteLayers.forEach(l=> state.map.removeLayer(l));
  state.currentRouteLayers=[];
  state.rankedData=[];
  state.activeRouteIndex=null;
  const tb = ui.tableBody(); if(tb) tb.innerHTML='';
}
