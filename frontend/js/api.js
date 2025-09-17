import { setLoading, addMessage } from './ui.js';

export async function fetchRoutes(startLat,startLon,endLat,endLon){
  setLoading(true);
  addMessage(`Requesting routes ${startLat},${startLon} -> ${endLat},${endLon}`);
  try {
    const url = `http://localhost:8000/safest-route?start_lat=${startLat}&start_lon=${startLon}&end_lat=${endLat}&end_lon=${endLon}`;
    const resp = await fetch(url);
    if(!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    if(data.error){ addMessage(data.error,'error'); return null; }
    addMessage('Routes computed');
    return data;
  } catch(err){ addMessage(`Failed: ${err.message}`,'error'); return null; }
  finally { setLoading(false); }
}
