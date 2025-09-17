import { state, icons } from './state.js';
import { addMessage } from './ui.js';

export function initMap(){
  if(state.map) return state.map;
  state.map = L.map('map').setView([30.7333, 76.7794], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(state.map);
  addLegend();
  createIcons();
  addMessage('Map initialized');
  return state.map;
}

function addLegend(){
  if (document.getElementById('legend')) return;
  const legend = L.control({ position:'bottomright'});
  legend.onAdd = function(){
    const div = L.DomUtil.create('div','info legend');
    div.id='legend';
    div.style.background='white';
    div.style.padding='6px 8px';
    div.style.boxShadow='0 0 4px rgba(0,0,0,0.3)';
    div.style.font='12px Arial';
    div.innerHTML='<strong>Safety Ranking</strong><br><span style="color:#2E7D32;">&#9608;</span> Safest<br><span style="color:#FB8C00;">&#9608;</span> Second<br><span style="color:#C62828;">&#9608;</span> Third';
    return div;
  };
  legend.addTo(state.map);
}

function createIcons(){
  icons.start = L.divIcon({className:'marker-icon marker-start', html:'S'});
  icons.end = L.divIcon({className:'marker-icon marker-end', html:'E'});
}
