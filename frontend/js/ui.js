import { state } from './state.js';

const qs = (sel) => document.querySelector(sel);

export const ui = {
  start: () => qs('#start'),
  end: () => qs('#end'),
  tableBody: () => qs('#routeTable tbody'),
  messages: () => qs('#messages'),
  loading: () => qs('#loading'),
  btnRoute: () => qs('#btnRoute'),
  autoFetch: () => qs('#autoFetch')
};

export function setLoading(flag){
  const el = ui.loading();
  if(el) el.classList.toggle('hidden', !flag);
  const b = ui.btnRoute();
  if(b) b.disabled = flag;
}

export function addMessage(text, type='info'){
  const c = ui.messages(); if(!c) return;
  const d = document.createElement('div');
  d.className = `msg ${type}`;
  d.textContent = text;
  c.appendChild(d);
  c.scrollTop = c.scrollHeight;
}

export function clearMessages(){ const c = ui.messages(); if(c) c.innerHTML=''; }
