// simple, professional UI behaviour
const elems = {
  voltage: document.getElementById('voltage'),
  temperature: document.getElementById('temperature'),
  power_factor: document.getElementById('power_factor'),
  load_kw: document.getElementById('load_kw'),
  frequency_hz: document.getElementById('frequency_hz'),
  v_pill: document.getElementById('v-pill'),
  t_pill: document.getElementById('t-pill'),
  pf_pill: document.getElementById('pf-pill'),
  load_pill: document.getElementById('load-pill'),
  f_pill: document.getElementById('f-pill'),
  predictBtn: document.getElementById('predictBtn'),
  resetBtn: document.getElementById('resetBtn'),
  status: document.getElementById('status'),
  predicted_main: document.getElementById('predicted-main'),
  card_voltage: document.getElementById('card-voltage'),
  card_load: document.getElementById('card-load'),
  card_pf: document.getElementById('card-pf'),
  card_temp: document.getElementById('card-temp'),
  card_f: document.getElementById('card-f'),
  card_last: document.getElementById('card-last'),
  history: document.getElementById('history'),
  lineChartEl: document.getElementById('lineChart')
};

function updatePills(){
  elems.v_pill.textContent = elems.voltage.value + ' V';
  elems.t_pill.textContent = elems.temperature.value + ' °C';
  elems.pf_pill.textContent = Number(elems.power_factor.value).toFixed(2);
  elems.load_pill.textContent = elems.load_kw.value + ' kW';
  elems.f_pill.textContent = elems.frequency_hz.value + ' Hz';

  elems.card_voltage.textContent = elems.voltage.value + ' V';
  elems.card_load.textContent = elems.load_kw.value + ' kW';
  elems.card_pf.textContent = Number(elems.power_factor.value).toFixed(2);
  elems.card_temp.textContent = elems.temperature.value + ' °C';
  elems.card_f.textContent = elems.frequency_hz.value + ' Hz';
}

['voltage','temperature','power_factor','load_kw','frequency_hz'].forEach(id=>{
  const el = document.getElementById(id);
  if(el) el.addEventListener('input', updatePills);
});
updatePills();

// Chart.js setup
const ctx = elems.lineChartEl.getContext('2d');
const chartData = { labels: [], datasets: [{ label:'kWh', data: [], borderWidth:2, fill:true, backgroundColor:'rgba(37,99,235,0.08)', borderColor:'#2563eb' }] };
const chart = new Chart(ctx, { type:'line', data: chartData, options:{ responsive:true, plugins:{legend:{display:false}}, scales:{ x:{display:true}, y:{display:true} } } });

const runs = [];

function appendRun(time, predicted){
  runs.unshift({ time, predicted });
  if(runs.length>6) runs.pop();
  elems.history.innerHTML = runs.map(r=>`<div style="padding:6px 0;border-bottom:1px solid #f1f5f9"><strong>${r.predicted} kWh</strong><div style="color:#6b7280;font-size:12px">${r.time}</div></div>`).join('');
  elems.card_last.textContent = runs[0]?.time ?? '—';
}

async function callPredict(){
  elems.predictBtn.disabled = true;
  elems.status.textContent = 'Predicting...';
  elems.predicted_main.textContent = '— — kWh';

  const payload = {
    voltage: Number(elems.voltage.value),
    temperature: Number(elems.temperature.value),
    power_factor: Number(elems.power_factor.value),
    load_kw: Number(elems.load_kw.value),
    frequency_hz: Number(elems.frequency_hz.value)
  };

  try {
    const resp = await fetch('/predict', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });

    if(!resp.ok){
      elems.status.textContent = 'Error';
      elems.predictBtn.disabled = false;
      return;
    }

    const data = await resp.json();
    const predicted = (data.predicted_units ?? data.prediction ?? data.value ?? null);
    const val = (predicted !== null) ? Number(predicted).toFixed(3) : 'n/a';
    elems.predicted_main.textContent = (val==='n/a') ? 'n/a' : `${val} kWh`;
    elems.status.textContent = 'Done';

    const time = new Date().toLocaleTimeString();
    chart.data.labels.push(time);
    chart.data.datasets[0].data.push(Number(predicted) || 0);
    if(chart.data.labels.length > 12){
      chart.data.labels.shift(); chart.data.datasets[0].data.shift();
    }
    chart.update();

    appendRun(time, val);

  } catch (err){
    console.error(err);
    elems.status.textContent = 'Network error';
  } finally {
    elems.predictBtn.disabled = false;
  }
}

elems.predictBtn.addEventListener('click', callPredict);
elems.resetBtn.addEventListener('click', ()=>{
  elems.voltage.value = 220; elems.temperature.value = 25; elems.power_factor.value = 0.95;
  elems.load_kw.value = 50; elems.frequency_hz.value = 50; updatePills();
});
document.addEventListener('keydown', e=>{ if(e.key==='Enter') callPredict(); });
