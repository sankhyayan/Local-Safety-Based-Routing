import { state, icons } from './state.js';
import { ui, addMessage } from './ui.js';
import { clearRoutes } from './routes.js';
import { getAndDisplayRoutes } from './main.js';

export function attachMapClick(){
  state.map.on('click', e => {
    const lat = e.latlng.lat.toFixed(6); const lon = e.latlng.lng.toFixed(6);
    if(!ui.start().value){
      if(state.startMarker) state.map.removeLayer(state.startMarker);
      ui.start().value=`${lat},${lon}`;
      state.startMarker=createMarker(lat,lon,true);
    } else if(!ui.end().value){
      if(state.endMarker) state.map.removeLayer(state.endMarker);
      ui.end().value=`${lat},${lon}`;
      clearRoutes();
      state.endMarker=createMarker(lat,lon,false);
    } else {
      if(state.endMarker) state.map.removeLayer(state.endMarker);
      ui.end().value=`${lat},${lon}`;
      clearRoutes();
      state.endMarker=createMarker(lat,lon,false);
    }
    if(ui.autoFetch()?.checked && ui.start().value && ui.end().value) getAndDisplayRoutes();
  });
}

function createMarker(lat,lon,isStart){
  const icon = isStart?icons.start:icons.end;
  const m = L.marker([parseFloat(lat),parseFloat(lon)],{draggable:true,icon}).addTo(state.map)
    .bindPopup(isStart?'Start':'End')
    .bindTooltip(isStart?'Start Point':'End Point',{permanent:false,direction:'top',offset:[0,-18]});
  m.on('dragend',()=> markerDragged(m,isStart));
  return m;
}

function markerDragged(marker,isStart){
  const {lat,lng} = marker.getLatLng();
  const val = `${lat.toFixed(6)},${lng.toFixed(6)}`;
  if(isStart) ui.start().value=val; else ui.end().value=val;
  if(ui.autoFetch()?.checked && ui.start().value && ui.end().value) getAndDisplayRoutes();
}

export function clearMarkers(){
  if(state.startMarker){ state.map.removeLayer(state.startMarker); state.startMarker=null; }
  if(state.endMarker){ state.map.removeLayer(state.endMarker); state.endMarker=null; }
  ui.start().value=''; ui.end().value='';
  clearRoutes();
  addMessage('Markers cleared');
}

export function swapPoints(){
  const s = ui.start().value; ui.start().value = ui.end().value; ui.end().value = s;
  if(state.startMarker){ state.map.removeLayer(state.startMarker); state.startMarker=null; }
  if(state.endMarker){ state.map.removeLayer(state.endMarker); state.endMarker=null; }
  clearRoutes();
  recreateMarker(ui.start().value,true);
  recreateMarker(ui.end().value,false);
  if(ui.autoFetch()?.checked && ui.start().value && ui.end().value) getAndDisplayRoutes();
}

function recreateMarker(val,isStart){
  if(!val) return; const parts=val.split(','); if(parts.length!==2) return;
  const lat=parseFloat(parts[0]); const lon=parseFloat(parts[1]); if(isNaN(lat)||isNaN(lon)) return;
  const icon = isStart?icons.start:icons.end;
  const m=L.marker([lat,lon],{draggable:true,icon}).addTo(state.map)
    .bindPopup(isStart?'Start':'End')
    .bindTooltip(isStart?'Start Point':'End Point',{permanent:false,direction:'top',offset:[0,-18]});
  m.on('dragend',()=>markerDragged(m,isStart));
  if(isStart) state.startMarker=m; else state.endMarker=m;
}
