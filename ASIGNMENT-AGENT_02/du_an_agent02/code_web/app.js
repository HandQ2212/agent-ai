'use strict';
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const labels = {overview:'Tổng quan', shopping:'Trợ lý mua sắm', experiments:'Thí nghiệm RL', classifier:'Phân loại ý định'};
const statusLabels = {success:'THÀNH CÔNG', ok:'THÀNH CÔNG', no_results:'KHÔNG CÓ KẾT QUẢ', invalid_input:'ĐẦU VÀO KHÔNG HỢP LỆ', timeout:'QUÁ THỜI GIAN', availability_unverified:'CHƯA XÁC MINH TỒN KHO', contract_error:'LỖI THÔNG ĐIỆP'};
const agentLabels = {catalog:'Catalog agent', recommender:'Recommendation agent', policy:'Policy agent', inventory:'Inventory agent'};
const configLabels = {baseline:'Baseline', alpha_001:'Alpha 0.01', alpha_050:'Alpha 0.50', epsilon_005:'Epsilon 0.05', epsilon_030:'Epsilon 0.30'};
const intentLabels = {ecommerce:'Mua sắm', tourism:'Du lịch', healthcare_admin:'Hành chính y tế', clarify:'Cần làm rõ'};
const escapeHTML = (value) => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const format = (value, digits=2) => Number(value).toFixed(digits);
async function api(url, payload) {
  const options = payload === undefined ? {} : {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)};
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Không thể xử lý yêu cầu.');
  return data;
}
function switchView(name) {
  if (!Object.hasOwn(labels, name)) name = 'overview';
  $$('.view').forEach(el => el.classList.toggle('active', el.id === `view-${name}`));
  $$('.nav-item').forEach(el => el.classList.toggle('active', el.dataset.view === name));
  $('#breadcrumb').textContent = labels[name];
  if (location.hash !== `#${name}`) history.replaceState(null, '', `#${name}`);
  window.scrollTo({top:0, behavior:'smooth'});
}
$$('[data-view]').forEach(el => el.addEventListener('click', event => {event.preventDefault(); switchView(el.dataset.view);}));
$$('[data-go]').forEach(el => el.addEventListener('click', () => switchView(el.dataset.go)));
window.addEventListener('hashchange', () => switchView(location.hash.slice(1)));
switchView(location.hash.slice(1) || 'overview');
function showGlobalError(message) {
  const box = $('#global-error'); box.textContent = message; box.classList.remove('hidden');
}
function renderOverview(data) {
  const baseline = data.assignment.find(row => row.configuration === 'baseline');
  $('#metric-products').textContent = data.catalog_count;
  $('#metric-accuracy').textContent = `${format(data.intent.accuracy * 100, 0)}%`;
  $('#metric-test-count').textContent = data.intent.splits.test;
  $('#metric-reward').textContent = baseline ? format(baseline.mean) : '—';
  $('#metric-episodes').textContent = Number(data.episodes).toLocaleString('en-US');
  $('#seed-list').textContent = data.seeds.join(' · ');
  $('#reward-chart').innerHTML = data.assignment.map(row => `<div class="bar-column"><span class="bar-value">${format(row.mean)}</span><div class="bar" style="height:${Math.max(2, Math.min(100, Number(row.mean)/40*100))}%"></div><span class="bar-label">${escapeHTML(configLabels[row.configuration] || row.configuration)}</span></div>`).join('');
  $('#experiment-table').innerHTML = data.assignment.map(row => `<tr><td>${escapeHTML(configLabels[row.configuration] || row.configuration)}</td><td>${format(row.mean,4)}</td><td>${format(row.sd,4)}</td><td>${format(row.discount_rate*100,2)}%</td></tr>`).join('');
}
api('/api/overview').then(renderOverview).catch(() => showGlobalError('Không thể kết nối máy chủ hoặc đọc kết quả. Hãy chạy: python3 code_web/server.py'));

$('#shopping-form').addEventListener('submit', async event => {
  event.preventDefault();
  const button=$('#search-button'), result=$('#product-results'), status=$('#result-status'), trace=$('#agent-trace');
  const query=$('#query').value.trim(), budget=Number($('#budget').value), scenario=$('#scenario').value;
  button.disabled=true; button.innerHTML='Đang xử lý <span>…</span>'; status.textContent='ĐANG CHẠY';
  result.className='empty-state'; result.innerHTML='<div class="empty-icon">✳</div><b>Đang hỏi các agent…</b><p>Vui lòng chờ trong giây lát.</p>';
  try {
    const data=await api('/api/recommend',{query,budget,scenario});
    status.textContent=statusLabels[data.status] || data.status.toUpperCase();
    if (data.items.length) {
      result.className='product-grid';
      result.innerHTML=data.items.map(item=>`<article class="product"><div class="product-icon">${item.category === 'travel' ? '▧' : '◇'}</div><h4>${escapeHTML(item.name)}</h4><small>${escapeHTML(item.category)} · ${escapeHTML(item.id)}</small><div class="product-bottom"><b>${escapeHTML(item.price)} <small>đơn vị</small></b><span class="stock">✓ Còn hàng</span></div></article>`).join('');
    } else {
      const messages={no_results:'Không tìm thấy sản phẩm phù hợp hoặc còn hàng.',invalid_input:'Kiểm tra lại từ khóa và ngân sách.',timeout:'Agent tồn kho không phản hồi trong thời gian cho phép.',availability_unverified:'Dữ liệu tồn kho đã cũ; hệ thống chưa thể xác minh.',contract_error:'Một agent đã trả dữ liệu không hợp lệ.'};
      result.className='empty-state'; result.innerHTML=`<div class="empty-icon">◇</div><b>${escapeHTML(statusLabels[data.status] || data.status)}</b><p>${escapeHTML(messages[data.status] || 'Không có sản phẩm để hiển thị.')}</p>`;
    }
    trace.className=data.trace.length?'trace-list':'trace-empty';
    trace.innerHTML=data.trace.length?data.trace.map(row=>`<div class="trace-row"><span class="trace-dot ${row.status==='ok'?'':'error'}">${row.status==='ok'?'✓':'!'}</span><b>${escapeHTML(agentLabels[row.agent] || row.agent)}</b><small>${escapeHTML(row.kind)} · ${format(row.milliseconds)} ms</small></div>`).join(''):'Không có lời gọi agent.';
  } catch(error) {
    status.textContent='LỖI KẾT NỐI'; result.className='empty-state'; result.innerHTML=`<div class="empty-icon">!</div><b>Không thể xử lý</b><p>${escapeHTML(error.message)}</p>`;trace.className='trace-empty';trace.textContent='Không có trace.';
  } finally {button.disabled=false; button.innerHTML='Bắt đầu tìm kiếm <span>↗</span>';}
});
$('#intent-form').addEventListener('submit', async event => {
  event.preventDefault();const button=$('#intent-button'), result=$('#intent-result');
  button.disabled=true;button.innerHTML='Đang phân loại <span>…</span>';result.className='empty-state';result.innerHTML='<div class="empty-icon">◎</div><b>Đang chạy mô hình…</b><p>Lần đầu có thể mất vài giây.</p>';
  try {
    const data=await api('/api/intent',{text:$('#intent-text').value.trim()});const confidence=Math.max(0,Math.min(100,Number(data.confidence)*100));
    result.className='prediction';result.innerHTML=`<div class="empty-icon" style="margin:0 auto">◎</div><div class="prediction-label">${escapeHTML(intentLabels[data.intent] || data.intent)}</div><small>${data.intent==='clarify'?'Mô hình yêu cầu làm rõ':'Ý định được dự đoán'}</small><div class="confidence-track"><div class="confidence-fill" style="width:${confidence}%"></div></div><small>Confidence ${format(confidence,1)}%</small>`;
  }catch(error){result.className='empty-state';result.innerHTML=`<div class="empty-icon">!</div><b>Không thể phân loại</b><p>${escapeHTML(error.message)}</p>`;}
  finally{button.disabled=false;button.innerHTML='Phân loại ý định <span>↗</span>';}
});
