import { initMap } from './map.js';
import { ui, addMessage } from './ui.js';
import { fetchRoutes } from './api.js';
import { displayRoute } from './routes.js';
import { clearRoutes } from './routes.js';
import { attachMapClick, clearMarkers, swapPoints } from './markers.js';
import { state } from './state.js';

// Orchestrated route fetch
export async function getAndDisplayRoutes(){
  const startInput = ui.start().value.trim();
  const endInput = ui.end().value.trim();
  if(!startInput || !endInput){ addMessage('Provide start and end coordinates','error'); return; }
  const s = startInput.split(','); const e = endInput.split(',');
  if(s.length!==2 || e.length!==2){ addMessage('Use lat,lon format','error'); return; }
  const [startLat,startLon] = s.map(v=>parseFloat(v));
  const [endLat,endLon] = e.map(v=>parseFloat(v));
  if([startLat,startLon,endLat,endLon].some(isNaN)){ addMessage('Invalid numeric coordinates','error'); return; }
  const data = await fetchRoutes(startLat,startLon,endLat,endLon);
  if(data) displayRoute(data);
}

function bindButtons(){
  const routeBtn = ui.btnRoute(); if(routeBtn) routeBtn.addEventListener('click', getAndDisplayRoutes);
  const swapBtn = document.querySelector('.buttons button:nth-child(2)');
  const clearMarkersBtn = document.querySelector('.buttons button:nth-child(3)');
  const clearRoutesBtn = document.querySelector('.buttons button:nth-child(4)');
  if(swapBtn) swapBtn.addEventListener('click', swapPoints);
  if(clearMarkersBtn) clearMarkersBtn.addEventListener('click', clearMarkers);
  if(clearRoutesBtn) clearRoutesBtn.addEventListener('click', clearRoutes);
}

function bootstrap(){
  initMap();
  attachMapClick();
  bindButtons();
  addMessage('Safety Route app initialized (modular)');
}

document.addEventListener('DOMContentLoaded', bootstrap);

// Expose for debugging if needed
window._safetyRoute = { state, getAndDisplayRoutes, clearMarkers, clearRoutes, swapPoints };
