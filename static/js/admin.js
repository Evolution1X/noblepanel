

let adminData = {
  coupons: [],
  plans: [],
  testimonials: [],
  faqs: [],
  orders: []
};

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  loadAdminData();
  refreshLucideIcons();
});

function refreshLucideIcons() {
  if (window.lucide && typeof window.lucide.createIcons === 'function') {
    window.lucide.createIcons();
  }
}

let currentTheme = localStorage.getItem('theme') || 'dark';

function initTheme() {
  setTheme(currentTheme, false);
}

function toggleTheme() {
  const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
  setTheme(nextTheme, true);
}

function setTheme(theme, animate = true) {
  currentTheme = theme;
  localStorage.setItem('theme', theme);
  document.documentElement.setAttribute('data-theme', theme);

  if (animate) {
    document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
  }
}


async function handleAdminLogout() {
  try {
    await fetch('/api/admin/logout', { method: 'POST' });
  } catch (err) {}
  window.location.href = document.body.dataset.adminUrl || '/';
}


async function loadAdminData() {
  try {
    const res = await fetch('/api/admin/all');
    if (res.status === 401) {
      window.location.href = document.body.dataset.adminUrl || '/';
      return;
    }
    const result = await res.json();
    if (result.success && result.data) {
      adminData = result.data;
      const counts = {
        'admin-stat-plans': adminData.plans?.length || 0,
        'admin-stat-coupons': adminData.coupons?.length || 0,
        'admin-stat-faqs': adminData.faqs?.length || 0,
        'admin-stat-orders': adminData.orders?.length || 0
      };
      Object.entries(counts).forEach(([id, count]) => {
        const element = document.getElementById(id);
        if (element) element.textContent = count.toLocaleString();
      });
      renderCouponsTable();
      renderPlansTable();
      renderTestimonialsTable();
      renderFaqsTable();
      renderOrdersTable();
      refreshLucideIcons();
    }
  } catch (err) {
    console.log('Error loading admin data:', err);
  }
}


function switchAdminTab(tabName) {
  document.querySelectorAll('.admin-tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.admin-tab-content').forEach(c => c.style.display = 'none');

  const activeBtn = document.getElementById(`tab-btn-${tabName}`);
  const activeTab = document.getElementById(`tab-${tabName}`);

  if (activeBtn) activeBtn.classList.add('active');
  if (activeTab) activeTab.style.display = 'block';

  refreshLucideIcons();
}


function renderCouponsTable() {
  const tbody = document.getElementById('coupons-table-body');
  if (!tbody) return;

  if (!adminData.coupons || adminData.coupons.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color: var(--text-dim);">No coupons available. Click "Create New Coupon" above.</td></tr>`;
    return;
  }

  tbody.innerHTML = adminData.coupons.map(coupon => `
    <tr>
      <td><strong style="color: #FFFFFF; font-family: var(--font-mono);">${coupon.code}</strong></td>
      <td>${coupon.discount_pct > 0 ? `${coupon.discount_pct}% OFF` : '—'}</td>
      <td>${coupon.flat_pkr > 0 ? `PKR ${coupon.flat_pkr.toLocaleString()} OFF` : '—'}</td>
      <td>${coupon.description || '—'}</td>
      <td>
        <span style="background: rgba(16,185,129,0.15); color: #10B981; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">
          ${coupon.active ? 'ACTIVE' : 'INACTIVE'}
        </span>
      </td>
      <td>
        <button class="btn btn-danger btn-sm" onclick="deleteCoupon('${coupon.code}')">
          <i data-lucide="trash-2"></i> Delete
        </button>
      </td>
    </tr>
  `).join('');
}


function renderPlansTable() {
  const tbody = document.getElementById('plans-table-body');
  if (!tbody) return;

  tbody.innerHTML = adminData.plans.map(plan => {
    const pkrPrice = plan.pkr_price === null || plan.pkr_price === undefined || plan.pkr_price === ''
      ? 'Not set'
      : `PKR ${Number(plan.pkr_price).toLocaleString()}`;
    const usdPrice = Number.isFinite(Number(plan.usd_price)) ? `$${Number(plan.usd_price).toFixed(2)}` : 'Not set';
    return `
    <tr>
      <td>
        <strong>${plan.name}</strong>
        ${plan.badge ? `<br><span style="font-size: 0.75rem; color: var(--text-dim);">${plan.badge}</span>` : ''}
      </td>
      <td>${plan.ram} / ${plan.cpu}</td>
      <td>${plan.storage}</td>
      <td><strong>${pkrPrice}</strong></td>
      <td><strong>${usdPrice}</strong></td>
      <td><span style="text-transform: uppercase; font-size: 0.8rem;">${plan.category || 'paper'}</span></td>
      <td>
        <button class="btn btn-danger btn-sm" onclick="deletePlan('${plan.id}')">
          <i data-lucide="trash-2"></i> Delete
        </button>
      </td>
    </tr>
  `;
  }).join('');
}


function renderTestimonialsTable() {
  const tbody = document.getElementById('testimonials-table-body');
  if (!tbody) return;

  if (!adminData.testimonials || adminData.testimonials.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--text-dim);">No testimonials available. Click "Add New Review" above.</td></tr>`;
    return;
  }

  tbody.innerHTML = adminData.testimonials.map(t => `
    <tr>
      <td>
        <div style="display: flex; align-items: center; gap: 0.6rem;">
          <div class="testimonial-avatar" style="width: 32px; height: 32px; font-size: 0.75rem;">${t.avatar || 'CC'}</div>
          <strong>${t.name}</strong>
        </div>
      </td>
      <td style="color: var(--text-muted);">${t.role || 'Player'}</td>
      <td style="color: #F59E0B;">${'★'.repeat(t.stars || 5)}</td>
      <td style="font-size: 0.88rem; color: var(--text-muted); font-style: italic;">"${t.text}"</td>
      <td>
        <button class="btn btn-danger btn-sm" onclick="deleteTestimonial(${t.id})">
          <i data-lucide="trash-2"></i> Delete
        </button>
      </td>
    </tr>
  `).join('');
}


function renderFaqsTable() {
  const tbody = document.getElementById('faqs-table-body');
  if (!tbody) return;

  tbody.innerHTML = adminData.faqs.map(faq => `
    <tr>
      <td><strong>${faq.question}</strong></td>
      <td style="color: var(--text-muted); font-size: 0.9rem;">${faq.answer}</td>
      <td>
        <button class="btn btn-danger btn-sm" onclick="deleteFaq(${faq.id})">
          <i data-lucide="trash-2"></i> Delete
        </button>
      </td>
    </tr>
  `).join('');
}


function renderOrdersTable() {
  const tbody = document.getElementById('orders-table-body');
  if (!tbody) return;

  if (!adminData.orders || adminData.orders.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color: var(--text-dim);">No customer orders recorded yet.</td></tr>`;
    return;
  }

  tbody.innerHTML = adminData.orders.map(order => `
    <tr>
      <td><strong style="font-family: var(--font-mono); color: #FFFFFF;">${order.order_id}</strong></td>
      <td>${order.plan_name}</td>
      <td style="font-family: var(--font-mono); font-size: 0.85rem; color: #10B981;">${order.subdomain}</td>
      <td>${order.location}</td>
      <td><span style="font-weight: 700;">${order.payment_method}</span></td>
      <td><strong>PKR ${order.total_pkr.toLocaleString()}</strong></td>
      <td><span style="background: rgba(16,185,129,0.15); color: #10B981; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem;">${order.status || 'Active'}</span></td>
    </tr>
  `).join('');
}


function closeAdminModals() {
  document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));
}

function openAddCouponModal() {
  document.getElementById('coupon-code-input').value = '';
  document.getElementById('coupon-pct-input').value = '0';
  document.getElementById('coupon-flat-input').value = '0';
  document.getElementById('coupon-desc-input').value = '';
  document.getElementById('coupon-modal').classList.add('active');
  refreshLucideIcons();
}

function openAddPlanModal() {
  document.getElementById('plan-id-input').value = '';
  document.getElementById('plan-name-input').value = '';
  document.getElementById('plan-ram-input').value = '';
  document.getElementById('plan-cpu-input').value = '';
  document.getElementById('plan-storage-input').value = '';
  document.getElementById('plan-pkr-input').value = '';
  document.getElementById('plan-usd-input').value = '';
  document.getElementById('plan-badge-input').value = '';
  document.getElementById('plan-modal').classList.add('active');
  refreshLucideIcons();
}

function openAddTestimonialModal() {
  document.getElementById('testimonial-id-input').value = '';
  document.getElementById('testimonial-name-input').value = '';
  document.getElementById('testimonial-role-input').value = '';
  document.getElementById('testimonial-stars-input').value = '5';
  document.getElementById('testimonial-avatar-input').value = '';
  document.getElementById('testimonial-text-input').value = '';
  document.getElementById('testimonial-modal').classList.add('active');
  refreshLucideIcons();
}

function openAddFaqModal() {
  document.getElementById('faq-id-input').value = '';
  document.getElementById('faq-question-input').value = '';
  document.getElementById('faq-answer-input').value = '';
  document.getElementById('faq-modal').classList.add('active');
  refreshLucideIcons();
}


async function handleSaveCoupon(e) {
  e.preventDefault();
  const code = document.getElementById('coupon-code-input').value.trim().toUpperCase();
  const pct = parseInt(document.getElementById('coupon-pct-input').value) || 0;
  const flat = parseInt(document.getElementById('coupon-flat-input').value) || 0;
  const desc = document.getElementById('coupon-desc-input').value.trim();

  try {
    const res = await fetch('/api/admin/coupons', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: code, discount_pct: pct, flat_pkr: flat, description: desc, active: true })
    });
    const result = await res.json();
    closeAdminModals();
    if (result.success) loadAdminData();
  } catch (err) {
    alert('Error saving coupon');
  }
}

async function deleteCoupon(code) {
  if (!confirm(`Are you sure you want to delete coupon ${code}?`)) return;
  try {
    const res = await fetch('/api/admin/coupons', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: code })
    });
    const result = await res.json();
    if (result.success) loadAdminData();
  } catch (err) {
    alert('Error deleting coupon');
  }
}

async function handleSavePlan(e) {
  e.preventDefault();
  const name = document.getElementById('plan-name-input').value.trim();
  const ram = document.getElementById('plan-ram-input').value.trim();
  const cpu = document.getElementById('plan-cpu-input').value.trim();
  const storage = document.getElementById('plan-storage-input').value.trim();
  const pkr = parseInt(document.getElementById('plan-pkr-input').value);
  const usd = parseFloat(document.getElementById('plan-usd-input').value);
  const badge = document.getElementById('plan-badge-input').value.trim();
  const category = document.getElementById('plan-category-input').value;

  try {
    const res = await fetch('/api/admin/plans', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: `plan-${Date.now()}`,
        name: name,
        ram: ram,
        cpu: cpu,
        storage: storage,
        pkr_price: pkr,
        usd_price: usd,
        badge: badge,
        category: category,
        icon: 'box'
      })
    });
    const result = await res.json();
    closeAdminModals();
    if (result.success) loadAdminData();
  } catch (err) {
    alert('Error saving package');
  }
}

async function deletePlan(id) {
  if (!confirm(`Delete package ${id}?`)) return;
  try {
    const res = await fetch('/api/admin/plans', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: id })
    });
    const result = await res.json();
    if (result.success) loadAdminData();
  } catch (err) {
    alert('Error deleting package');
  }
}

async function handleSaveTestimonial(e) {
  e.preventDefault();
  const t_id = document.getElementById('testimonial-id-input').value;
  const name = document.getElementById('testimonial-name-input').value.trim();
  const role = document.getElementById('testimonial-role-input').value.trim();
  const stars = parseInt(document.getElementById('testimonial-stars-input').value) || 5;
  const avatar = document.getElementById('testimonial-avatar-input').value.trim();
  const text = document.getElementById('testimonial-text-input').value.trim();

  try {
    const res = await fetch('/api/admin/testimonials', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: t_id || undefined,
        name: name,
        role: role,
        stars: stars,
        avatar: avatar,
        text: text
      })
    });
    const result = await res.json();
    closeAdminModals();
    if (result.success) loadAdminData();
  } catch (err) {
    alert('Error saving review');
  }
}

async function deleteTestimonial(id) {
  if (!confirm('Delete this review?')) return;
  try {
    const res = await fetch('/api/admin/testimonials', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: id })
    });
    const result = await res.json();
    if (result.success) loadAdminData();
  } catch (err) {
    alert('Error deleting review');
  }
}

async function handleSaveFaq(e) {
  e.preventDefault();
  const question = document.getElementById('faq-question-input').value.trim();
  const answer = document.getElementById('faq-answer-input').value.trim();

  try {
    const res = await fetch('/api/admin/faqs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: question, answer: answer })
    });
    const result = await res.json();
    closeAdminModals();
    if (result.success) loadAdminData();
  } catch (err) {
    alert('Error saving FAQ');
  }
}

async function deleteFaq(id) {
  if (!confirm('Delete this FAQ entry?')) return;
  try {
    const res = await fetch('/api/admin/faqs', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: id })
    });
    const result = await res.json();
    if (result.success) loadAdminData();
  } catch (err) {
    alert('Error deleting FAQ');
  }
}
