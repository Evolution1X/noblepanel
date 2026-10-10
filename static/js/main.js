

let activeCategory = 'all';
let allPlans = [];
let appliedCoupon = null;
let currentSelectedPlanPricePKR = 3800;

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initDropdowns();
  initCardTiltAndGlow();
  initMagneticButtons();
  initNumberCounters();
  initParallax();
  initHeroCanvas();
  initNavbarScroll();
  initScrollReveal();
  initFramerMotionEffects();
  fetchPlans();
  fetchTestimonials();
  fetchFaqs();
  initSmoothAnchors();
  initPasswordToggles();
  initUnifiedAuth();
  initCookieNotice();
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
  const checkbox = document.getElementById('theme-checkbox');
  const nextTheme = checkbox && checkbox.checked ? 'light' : 'dark';
  setTheme(nextTheme, true);
}

function setTheme(theme, animate = true) {
  currentTheme = theme;
  localStorage.setItem('theme', theme);
  document.documentElement.setAttribute('data-theme', theme);

  const checkbox = document.getElementById('theme-checkbox');
  if (checkbox) {
    checkbox.checked = (theme === 'light');
  }

  if (animate) {
    document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
  }
}



function initFramerMotionEffects() {
  const cards = document.querySelectorAll('.mk-card, .deploy-card, .pricing-card, .step-card, .testimonial-card');
  cards.forEach(card => {
    card.addEventListener('mouseenter', () => {
      if (window.Motion && typeof window.Motion.animate === 'function') {
        window.Motion.animate(card, { scale: 1.015, y: -4 }, { duration: 0.2, easing: [0.16, 1, 0.3, 1] });
      } else {
        card.style.transform = 'translateY(-4px) scale(1.015)';
      }
    });
    card.addEventListener('mouseleave', () => {
      if (window.Motion && typeof window.Motion.animate === 'function') {
        window.Motion.animate(card, { scale: 1, y: 0 }, { duration: 0.2, easing: [0.16, 1, 0.3, 1] });
      } else {
        card.style.transform = 'translateY(0) scale(1)';
      }
    });
  });
}



function initDropdowns() {
  const dropdowns = document.querySelectorAll('.nav-dropdown');
  dropdowns.forEach(dropdown => {
    const trigger = dropdown.querySelector('.dropdown-trigger');
    if (!trigger) return;

    trigger.addEventListener('click', (event) => {
      event.preventDefault();
      const isOpen = dropdown.classList.contains('active');
      closeAllDropdowns();
      if (!isOpen) {
        dropdown.classList.add('active');
      }
    });

    trigger.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        trigger.click();
      }
      if (event.key === 'Escape') {
        closeAllDropdowns();
      }
    });
  });

  document.addEventListener('click', (event) => {
    if (!event.target.closest('.nav-dropdown')) {
      closeAllDropdowns();
    }
  });
}

function closeAllDropdowns() {
  document.querySelectorAll('.nav-dropdown').forEach(dropdown => dropdown.classList.remove('active'));
}

function initNavbarScroll() {
  const navbar = document.getElementById('navbar');
  if (!navbar) return;

  let ticking = false;
  const onScroll = () => {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        if (navbar.classList.contains('nn-nav')) {
          const mobile = window.innerWidth <= 700;
          const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
          const progress = reducedMotion
            ? (window.scrollY > 25 ? 1 : 0)
            : Math.min(window.scrollY / 140, 1);
          const compactWidth = Math.min(mobile ? window.innerWidth - 24 : 1000, window.innerWidth - (mobile ? 24 : 48));
          const width = window.innerWidth - (window.innerWidth - compactWidth) * progress;
          const startPadding = mobile ? 19 : window.innerWidth * 0.05;
          const compactPadding = mobile ? 14 : 22;

          navbar.classList.toggle('scrolled', progress > 0);
          navbar.style.top = `${progress * (mobile ? 9 : 14)}px`;
          navbar.style.left = `${(window.innerWidth - width) / 2}px`;
          navbar.style.right = 'auto';
          navbar.style.width = `${width}px`;
          navbar.style.height = `${(mobile ? 74 : 86) - progress * (mobile ? 16 : 22)}px`;
          navbar.style.padding = `0 ${startPadding + (compactPadding - startPadding) * progress}px`;
          navbar.style.borderRadius = `${7 * progress}px`;
          navbar.style.borderColor = `rgba(255, 255, 255, ${0.13 * progress})`;
          navbar.style.boxShadow = `0 ${16 * progress}px ${48 * progress}px rgba(10, 26, 20, ${0.2 * progress})`;
          navbar.style.backdropFilter = `blur(${16 * progress}px)`;
          navbar.style.transform = 'none';
          navbar.style.transition = 'none';
        } else {
          navbar.classList.toggle('scrolled', window.scrollY > 25);
        }
        ticking = false;
      });
      ticking = true;
    }
  };

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
  onScroll();
}

function initPasswordToggles() {
  document.querySelectorAll('[data-toggle-password]').forEach(button => {
    button.addEventListener('click', () => {
      const target = document.getElementById(button.getAttribute('data-toggle-password'));
      if (!target) return;
      const isPassword = target.type === 'password';
      target.type = isPassword ? 'text' : 'password';
      button.textContent = isPassword ? 'Hide' : 'Show';
      button.setAttribute('aria-label', `${isPassword ? 'Hide' : 'Show'} password`);
    });
  });
}

function initUnifiedAuth() {
  const page = document.querySelector('[data-auth-mode]');
  if (!page) return;
  const switchButton = document.getElementById('auth-switch-button');
  const switchLabel = document.getElementById('auth-switch-label');
  const storyTitle = document.getElementById('auth-story-title');
  const storyCopy = document.getElementById('auth-story-copy');
  const formTitle = document.getElementById('auth-form-title');
  const formSubtitle = document.getElementById('auth-form-subtitle');

  const setMode = (mode, animate = false) => {
    const isSignup = mode === 'signup';
    const isSignin = mode === 'signin';
    const isReset = mode === 'reset';
    const frame = document.querySelector('.nn-auth-frame');
    page.dataset.authMode = mode;
    document.querySelectorAll('[data-auth-panel]').forEach(panel => {
      panel.hidden = panel.dataset.authPanel !== mode;
    });
    if (switchButton) {
      switchButton.dataset.authModeTarget = isSignup ? 'signin' : 'signup';
      switchButton.innerHTML = isReset ? 'Back to sign in <span aria-hidden="true">↗</span>' : isSignup ? 'Sign in <span aria-hidden="true">↗</span>' : 'Create account <span aria-hidden="true">↗</span>';
      if (isReset) switchButton.dataset.authModeTarget = 'signin';
    }
    if (switchLabel) switchLabel.textContent = isReset ? 'Remembered your password?' : isSignup ? 'Already have an account?' : 'New to Noble Node?';
    if (storyTitle) storyTitle.textContent = isReset ? 'Back in your world.' : isSignup ? 'Welcome back.' : 'A new world starts here.';
    if (storyCopy) storyCopy.textContent = isReset ? 'We’ll send a private, one-use link to the email on your account.' : isSignup ? 'Sign in to pick up where your server story left off.' : 'Create an account and find the plan that fits your next server.';
    if (formTitle) formTitle.textContent = isReset ? 'Reset password' : isSignup ? 'Create account' : 'Sign in';
    if (formSubtitle) formSubtitle.textContent = isReset ? 'We’ll email a time-limited recovery link.' : isSignup ? 'One account for your Noble Node hosting.' : 'Good to have you back.';
    document.getElementById('auth-sso')?.toggleAttribute('hidden', isReset || !document.querySelector('.nn-sso-button'));
    document.getElementById('auth-divider')?.toggleAttribute('hidden', isReset);
    const url = new URL(window.location.href);
    url.searchParams.set('mode', mode);
    window.history.replaceState({}, '', `${url.pathname}${url.search}${url.hash}`);
    if (animate && frame) {
      frame.classList.remove('nn-auth-switching');
      void frame.offsetWidth;
      frame.classList.add('nn-auth-switching');
      window.setTimeout(() => frame.classList.remove('nn-auth-switching'), 420);
      document.querySelector(`[data-auth-panel="${mode}"] input`)?.focus();
    }
  };

  document.querySelectorAll('[data-auth-mode-target]').forEach(button => {
    button.addEventListener('click', () => setMode(button.dataset.authModeTarget, true));
  });
  setMode(page.dataset.authMode, false);
}

function initCookieNotice() {
  const banner = document.getElementById('nn-cookie-banner');
  if (!banner) return;
  try {
    if (localStorage.getItem('noble-node-cookie-choice') === 'essential') return;
  } catch (error) {}
  banner.hidden = false;
  document.getElementById('nn-cookie-accept')?.addEventListener('click', () => {
    try {
      localStorage.setItem('noble-node-cookie-choice', 'essential');
    } catch (error) {}
    banner.hidden = true;
  });
}


function initScrollReveal() {
  const revealElements = document.querySelectorAll('.reveal');
  if (!revealElements.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.08,
    rootMargin: '0px 0px -40px 0px'
  });

  revealElements.forEach(el => observer.observe(el));
}



function initSmoothAnchors() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        e.preventDefault();
        const navbarHeight = document.getElementById('navbar')?.offsetHeight || 70;
        const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - navbarHeight - 20;
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
}



function openMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  if (menu) {
    menu.classList.add('active');
    document.body.style.overflow = 'hidden';
    document.getElementById('hamburger-btn')?.setAttribute('aria-expanded', 'true');
    refreshLucideIcons();
    menu.querySelector('a, button')?.focus();
  }
}

function closeMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  if (menu) {
    menu.classList.remove('active');
    document.body.style.overflow = '';
    document.getElementById('hamburger-btn')?.setAttribute('aria-expanded', 'false');
  }
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeMobileMenu();
    closeOrderModal();
  }
});



async function fetchPlans() {
  try {
    const res = await fetch('/api/plans');
    const data = await res.json();
    if (!res.ok || !data.success || !Array.isArray(data.plans)) throw new Error('Plan data unavailable');
    allPlans = data.plans;
  } catch (err) {
    allPlans = [];
  }
  renderPlans();
}



async function fetchTestimonials() {
  const container = document.getElementById('testimonials-grid');
  if (!container) return;

  try {
    const res = await fetch('/api/testimonials');
    const data = await res.json();
    if (data.success && data.testimonials && data.testimonials.length) {
      container.innerHTML = data.testimonials.map((t) => `
        <div class="nn-testimonial-card">
          <div class="nn-t-stars">${'★'.repeat(t.stars || 5)}</div>
          <p class="nn-t-quote">"${t.text}"</p>
          <div class="nn-t-author">
            <div class="nn-t-avatar">${t.avatar || 'MC'}</div>
            <div>
              <strong>${t.name}</strong>
              <small>${t.role}</small>
            </div>
          </div>
        </div>
      `).join('');
    }
  } catch (err) {}
}



async function fetchFaqs() {
  const container = document.getElementById('faq-container');
  if (!container) return;

  try {
    const res = await fetch('/api/faqs');
    const data = await res.json();
    if (data.success && data.faqs) {
      container.innerHTML = data.faqs.map((faq, idx) => `
        <div class="faq-item ${idx === 0 ? 'active' : ''} reveal${idx > 0 ? ` reveal-delay-${Math.min(idx, 4)}` : ''}">
          <div class="faq-question" onclick="toggleFaq(this)">
            <span>${faq.question}</span>
            <i data-lucide="chevron-down"></i>
          </div>
          <div class="faq-answer">
            ${faq.answer}
          </div>
        </div>
      `).join('');
      
      initScrollReveal();
      refreshLucideIcons();
    }
  } catch (err) {
    
  }
}

function toggleFaq(el) {
  const item = el.parentElement;
  const isActive = item.classList.contains('active');
  document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('active'));
  if (!isActive) item.classList.add('active');
}


function initCardTiltAndGlow() {
  const cards = document.querySelectorAll('.pricing-card, .deploy-card, .feature-card-glow, .testimonial-card, .coupons-banner-card');
  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      card.style.setProperty('--mouse-x', `${x}px`);
      card.style.setProperty('--mouse-y', `${y}px`);
    });
  });
}


function initMagneticButtons() {
  const btns = document.querySelectorAll('.btn-primary, .btn-pill-white');
  btns.forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'translate(0px, 0px)';
    });
  });
}


function initNumberCounters() {
  const counters = document.querySelectorAll('[data-counter-target]');
  if (!counters.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = parseFloat(el.getAttribute('data-counter-target') || '0');
        const suffix = el.getAttribute('data-counter-suffix') || '';
        const prefix = el.getAttribute('data-counter-prefix') || '';
        let current = 0;
        const duration = 1000;
        const stepTime = 20;
        const steps = duration / stepTime;
        const increment = target / steps;

        const timer = setInterval(() => {
          current += increment;
          if (current >= target) {
            current = target;
            clearInterval(timer);
          }
          const formatted = target % 1 === 0 ? Math.floor(current).toLocaleString() : current.toFixed(1);
          el.innerText = `${prefix}${formatted}${suffix}`;
        }, stepTime);

        observer.unobserve(el);
      }
    });
  }, { threshold: 0.2 });

  counters.forEach(c => observer.observe(c));
}


function initParallax() {
  const parallaxEls = document.querySelectorAll('[data-parallax-speed]');
  if (!parallaxEls.length) return;

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;
    parallaxEls.forEach(el => {
      const speed = parseFloat(el.getAttribute('data-parallax-speed') || '0.15');
      el.style.transform = `translateY(${scrollY * speed}px)`;
    });
  }, { passive: true });
}


function initHeroCanvas() {
  const canvas = document.getElementById('hero-particles-canvas');
  if (!canvas || !canvas.parentElement) return;

  const ctx = canvas.getContext('2d');
  let width = canvas.width = canvas.parentElement.offsetWidth;
  let height = canvas.height = canvas.parentElement.offsetHeight;

  window.addEventListener('resize', () => {
    if (!canvas.parentElement) return;
    width = canvas.width = canvas.parentElement.offsetWidth;
    height = canvas.height = canvas.parentElement.offsetHeight;
  });

  const particles = Array.from({ length: 28 }, () => ({
    x: Math.random() * width,
    y: Math.random() * height,
    vx: (Math.random() - 0.5) * 0.35,
    vy: (Math.random() - 0.5) * 0.35,
    radius: Math.random() * 2 + 1,
    alpha: Math.random() * 0.35 + 0.15
  }));

  function animate() {
    ctx.clearRect(0, 0, width, height);
    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(16, 185, 129, ${p.alpha})`;
      ctx.fill();
    });
    requestAnimationFrame(animate);
  }
  animate();
}


function copyCouponCode(code, el) {
  navigator.clipboard.writeText(code).then(() => {
    showToast(`✓ Coupon Code "${code}" copied to clipboard!`);
    if (el && el.querySelector('.copy-hint')) {
      const hint = el.querySelector('.copy-hint');
      const originalText = hint.innerHTML;
      hint.innerHTML = '<i data-lucide="check"></i> Copied!';
      refreshLucideIcons();
      setTimeout(() => {
        hint.innerHTML = originalText;
        refreshLucideIcons();
      }, 2000);
    }
  }).catch(() => {
    showToast(`Code: ${code}`);
  });
}

function showToast(message) {
  let toast = document.getElementById('global-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'global-toast';
    toast.className = 'toast-notification';
    document.body.appendChild(toast);
  }
  toast.innerHTML = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}



let currentBilling = 'monthly';

function switchBilling(mode) {
  currentBilling = mode;
  document.getElementById('billing-monthly')?.classList.toggle('active', mode === 'monthly');
  document.getElementById('billing-yearly')?.classList.toggle('active', mode === 'yearly');
  renderPlans();
}



function renderPlans() {
  const container = document.getElementById('pricing-grid') || document.getElementById('home-pricing-grid');
  if (!container) return;

  if (!allPlans.length) {
    return;
  }

  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[character]);

  container.innerHTML = allPlans.map((plan, index) => {
    const badge = plan.badge ? `<div class="nn-plan-label">${escapeHtml(plan.badge)}</div>` : '';
    const pkrPrice = plan.pkr_price ? Number(plan.pkr_price).toLocaleString() : '2,200';
    const priceUsd = Number(plan.usd_price).toFixed(2);
    const selectUrl = `/checkout?plan=${encodeURIComponent(plan.id)}`;
    const specs = [
      ['cpu', plan.cpu],
      ['hard-drive', plan.storage],
      ['archive', plan.backups],
      ['users', plan.slots]
    ].filter(([, value]) => value);

    return `<article class="nn-plan nn-plan-${index + 1} ${plan.recommended ? 'nn-plan-featured' : ''}">
      ${badge}
      <h3>${escapeHtml(plan.ram || plan.name)}</h3>
      <ul class="nn-plan-specs">${specs.map(([icon, value]) => `<li><i data-lucide="${icon}" aria-hidden="true"></i><span>${escapeHtml(value)}</span></li>`).join('')}</ul>
      <div class="nn-plan-protection"><i data-lucide="shield-check" aria-hidden="true"></i><span>${escapeHtml(plan.ddos_protection || 'Free 12+ Tbps Corero & Path.net DDoS Protection')}</span></div>
      <div class="nn-plan-price-row">
        <p class="nn-plan-price" data-pkr="${plan.pkr_price || 2200}" data-usd="${plan.usd_price || 7.95}">
          <span class="nn-curr-sym">PKR</span> <span class="nn-price-val">${pkrPrice}</span>
        </p>
        <p class="nn-plan-period">/ month (~$${priceUsd})</p>
      </div>
      <a class="nn-plan-action" href="${selectUrl}">Configure & Deploy 🚀</a>
    </article>`;
  }).join('');
  refreshLucideIcons();

  const proofStrip = document.getElementById('home-proof-strip');
  if (proofStrip) {
    const ramValues = allPlans.map(plan => Number.parseFloat(plan.ram || '')).filter(Number.isFinite);
    const cpuModel = allPlans.map(plan => (plan.cpu || '').match(/\(([^)]+)\)/)?.[1]).find(Boolean) || 'Ryzen 9 9950X';
    const storage = allPlans.map(plan => plan.storage || '').find(value => /NVMe/i.test(value));
    const storageLabel = storage?.match(/NVMe\s*Gen\s*\d+/i)?.[0] || 'Gen4 NVMe';
    const ramRange = ramValues.length ? `${Math.min(...ramValues)}–${Math.max(...ramValues)} GB` : `${allPlans.length} plans`;
    proofStrip.innerHTML = [
      [ramRange, 'DDR5 6000MHz Tiers'],
      [cpuModel, 'Listed CPU platform'],
      [storageLabel, 'Listed plan storage'],
      ['12+ Tbps', 'Path.net DDoS Shield']
    ].map(([value, label]) => `<div><strong>${escapeHtml(value)}</strong><span>${escapeHtml(label)}</span></div>`).join('');
  }
}



function openOrderModal(planId, planName, pkrPrice) {
  const modal = document.getElementById('order-modal');
  if (!modal) return;

  currentSelectedPlanPricePKR = pkrPrice || 3800;
  appliedCoupon = null;

  document.getElementById('modal-plan-id').value = planId || 'pro-diamond';
  document.getElementById('modal-plan-title').innerText = `Deploy Server: ${planName || 'Minecraft Server'}`;
  document.getElementById('modal-coupon-code').value = '';
  document.getElementById('coupon-message').innerText = '';

  updateModalTotalPrice();
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
  refreshLucideIcons();
}

function closeOrderModal() {
  const modal = document.getElementById('order-modal');
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

async function applyCouponCode() {
  const codeInput = document.getElementById('modal-coupon-code');
  const msgEl = document.getElementById('coupon-message');
  const code = codeInput.value.trim().toUpperCase();

  if (!code) {
    msgEl.innerText = 'Please enter a coupon code.';
    msgEl.style.color = '#F87171';
    return;
  }

  try {
    const res = await fetch('/api/coupons/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: code })
    });
    const data = await res.json();

    if (data.success && data.coupon) {
      appliedCoupon = data.coupon;
      msgEl.innerText = `✓ Coupon Applied: ${data.coupon.description}`;
      msgEl.style.color = '#FAFAFA';
      updateModalTotalPrice();
    } else {
      appliedCoupon = null;
      msgEl.innerText = '✕ ' + (data.message || 'Invalid Coupon');
      msgEl.style.color = '#F87171';
      updateModalTotalPrice();
    }
  } catch (err) {
    msgEl.innerText = 'Error checking coupon code.';
    msgEl.style.color = '#F87171';
  }
}

function updateModalTotalPrice() {
  let finalPKR = currentSelectedPlanPricePKR;

  if (appliedCoupon) {
    if (appliedCoupon.discount_pct > 0) {
      finalPKR = Math.floor(finalPKR * (1 - appliedCoupon.discount_pct / 100));
    } else if (appliedCoupon.flat_pkr > 0) {
      finalPKR = Math.max(0, finalPKR - appliedCoupon.flat_pkr);
    }
  }

  const priceText = `PKR ${finalPKR.toLocaleString()}`;
  const el = document.getElementById('modal-total-price');
  if (el) el.innerText = priceText;
}



async function handleOrderSubmit(e) {
  e.preventDefault();

  const planId = document.getElementById('modal-plan-id').value;
  const location = document.getElementById('modal-location').value;
  const software = document.getElementById('modal-software').value;
  const subdomain = document.getElementById('modal-subdomain').value;
  const payment = document.getElementById('modal-payment').value;
  const couponCode = document.getElementById('modal-coupon-code').value.trim().toUpperCase();

  const btn = e.target.querySelector('button[type="submit"]');
  const originalText = btn.innerHTML;
  btn.innerHTML = 'Provisioning Server...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/order', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        plan_id: planId,
        location: location,
        software: software,
        subdomain: subdomain,
        payment_method: payment,
        coupon_code: couponCode
      })
    });

    const data = await res.json();
    btn.innerHTML = originalText;
    btn.disabled = false;
    if (!res.ok || !data.success) throw new Error(data.message || 'Checkout is not configured yet. No order was placed.');
    closeOrderModal();
    showSuccessNotification(data);
  } catch (err) {
    btn.innerHTML = originalText;
    btn.disabled = false;
    showToast(err.message || 'Checkout is not configured yet. No order was placed.');
  }
}

function showSuccessNotification(data) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay active';
  overlay.id = 'success-notification';
  overlay.innerHTML = `
    <div class="modal-content" style="max-width: 500px; text-align: center;">
      <div style="margin-bottom: 1.5rem;">
        <div class="logo-badge" style="margin: 0 auto 1rem auto; width: 56px; height: 56px; background-color: #FFFFFF;">
          <i data-lucide="check-circle" style="width: 2rem; height: 2rem; color: #09090B;"></i>
        </div>
        <h2 style="font-size: 1.6rem; font-family: var(--font-heading); margin-bottom: 0.5rem; color: #FFFFFF;">Server Provisioned!</h2>
        <p style="color: var(--text-muted); font-size: 0.9rem;">Your Minecraft server is being deployed now.</p>
      </div>

      <div style="background: var(--bg-card); border: 1px solid var(--border-bright); border-radius: var(--radius-sm); padding: 1.25rem; text-align: left; margin-bottom: 1.5rem;">
        <div style="display: grid; gap: 0.75rem;">
          <div style="display: flex; justify-content: space-between;">
            <span style="color: var(--text-dim);">Order ID</span>
            <strong style="font-family: var(--font-mono); color: #FFFFFF;">${data.order_id || 'CC-00000'}</strong>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span style="color: var(--text-dim);">Server IP</span>
            <strong style="font-family: var(--font-mono); color: #10B981;">${data.server_ip || 'server.noblenode.host'}</strong>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span style="color: var(--text-dim);">Location</span>
            <strong style="color: #FFFFFF;">${data.location || 'Lahore'}</strong>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span style="color: var(--text-dim);">Software</span>
            <strong style="color: #FFFFFF;">${data.software || 'Paper 1.20.4'}</strong>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span style="color: var(--text-dim);">Total PKR</span>
            <strong style="color: #FFFFFF;">PKR ${data.total_pkr.toLocaleString()}</strong>
          </div>
        </div>
      </div>

      <div style="display: flex; gap: 0.75rem;">
        <a href="${data.control_panel_url || '#'}" target="_blank" class="btn btn-pill-white" style="flex: 1; text-decoration: none;">
          <i data-lucide="external-link"></i> Access Control Panel
        </a>
        <button class="btn btn-outline" onclick="document.getElementById('success-notification').remove()">
          Close
        </button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);
  refreshLucideIcons();
}

function handleClientSignIn(e) {
  e.preventDefault();
  const form = e.target;
  const email = form.querySelector('input[type="email"]').value.trim();
  const password = form.querySelector('input[type="password"]').value;
  const button = form.querySelector('button[type="submit"]');

  if (!email || !password) {
    showToast('Please enter both email and password.');
    return;
  }

  button.disabled = true;
  button.querySelector('span:first-child').textContent = 'Signing in…';
  fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, plan_id: document.body.dataset.selectedPlan || '' })
  }).then(async response => {
    const result = await response.json();
    if (!response.ok || !result.success) {
      throw new Error(result.message || 'Sign in failed.');
    }
    showToast('✓ Signed in successfully. Redirecting to the dashboard...');
    setTimeout(() => window.location.href = '/dashboard', 1000);
  }).catch(error => {
    showToast(error.message || 'Unable to sign you in right now.');
  }).finally(() => {
    button.disabled = false;
    button.querySelector('span:first-child').textContent = 'Sign in';
  });
}

function handleClientSignUp(e) {
  e.preventDefault();
  const form = e.target;
  const name = form.querySelector('input[name="name"]').value.trim();
  const email = form.querySelector('input[type="email"]').value.trim();
  const password = form.querySelector('input[type="password"]').value;
  const button = form.querySelector('button[type="submit"]');

  if (!name || !email || !password || password.length < 8) {
    showToast('Please provide a full name, valid email, and at least 8 characters in the password.');
    return;
  }

  button.disabled = true;
  button.querySelector('span:first-child').textContent = 'Creating account…';
  fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password, plan_id: document.body.dataset.selectedPlan || '' })
  }).then(async response => {
    const result = await response.json();
    if (!response.ok || !result.success) {
      throw new Error(result.message || 'Account creation failed.');
    }
    showToast('✓ Account created successfully. Redirecting to your dashboard...');
    setTimeout(() => window.location.href = '/dashboard', 1000);
  }).catch(error => {
    showToast(error.message || 'Unable to create your account right now.');
  }).finally(() => {
    button.disabled = false;
    button.querySelector('span:first-child').textContent = 'Create account';
  });
}

async function handlePasswordResetRequest(e) {
  e.preventDefault();
  const form = e.target;
  const button = form.querySelector('button[type="submit"]');
  const status = document.getElementById('password-reset-request-status');
  button.disabled = true;
  button.querySelector('span:first-child').textContent = 'Sending…';
  status.textContent = '';
  status.classList.remove('is-error');

  try {
    const response = await fetch('/api/auth/password-reset/request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: form.elements.email.value.trim() })
    });
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.message || 'Could not request a reset link.');
    status.textContent = result.message;
  } catch (error) {
    status.textContent = error.message || 'Could not request a reset link.';
    status.classList.add('is-error');
  } finally {
    button.disabled = false;
    button.querySelector('span:first-child').textContent = 'Send reset link';
  }
}

async function handlePasswordResetComplete(e) {
  e.preventDefault();
  const form = e.target;
  const button = form.querySelector('button[type="submit"]');
  const status = document.getElementById('password-reset-status');
  button.disabled = true;
  button.querySelector('span:first-child').textContent = 'Updating…';
  status.textContent = '';
  status.classList.remove('is-error');

  try {
    const response = await fetch('/api/auth/password-reset/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: form.elements.token.value, password: form.elements.password.value })
    });
    const result = await response.json();
    if (!response.ok || !result.success) throw new Error(result.message || 'Could not update your password.');
    status.textContent = result.message;
    window.setTimeout(() => window.location.href = '/auth?mode=signin', 1200);
  } catch (error) {
    status.textContent = error.message || 'Could not update your password.';
    status.classList.add('is-error');
  } finally {
    button.disabled = false;
    button.querySelector('span:first-child').textContent = 'Update password';
  }
}
