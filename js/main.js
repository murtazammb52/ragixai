/* ============================================================
   RAGixAI - Enterprise Knowledge Base
   Shared JavaScript
   ============================================================ */

'use strict';

// ---- DOM Ready ----
document.addEventListener('DOMContentLoaded', () => {
  initNav();
  initScrollAnimations();
  initCounters();
  initTypewriter();
  initSmoothScroll();
  initTabs();
  initPipelineInteractions();
  initParticleCanvas();
});

// ---- Navigation ----
function initNav() {
  const nav = document.querySelector('.nav');
  const toggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');

  // Scroll-based nav styling
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      nav?.classList.add('scrolled');
    } else {
      nav?.classList.remove('scrolled');
    }
  });

  // Mobile toggle
  toggle?.addEventListener('click', () => {
    navLinks?.classList.toggle('open');
    const spans = toggle.querySelectorAll('span');
    const isOpen = navLinks?.classList.contains('open');
    if (spans[0]) spans[0].style.transform = isOpen ? 'rotate(45deg) translate(5px, 5px)' : '';
    if (spans[1]) spans[1].style.opacity = isOpen ? '0' : '1';
    if (spans[2]) spans[2].style.transform = isOpen ? 'rotate(-45deg) translate(5px, -5px)' : '';
  });

  // Active page highlighting
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });
}

// ---- Scroll-Triggered Animations ----
function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('show');
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  });

  document.querySelectorAll('.hidden, .hidden-left, .hidden-right, .hidden-scale').forEach(el => {
    observer.observe(el);
  });
}

// ---- Counter Animation ----
function animateCounter(el, target, duration = 2000, prefix = '', suffix = '') {
  let startTime = null;
  const startVal = 0;

  function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
  }

  function step(currentTime) {
    if (!startTime) startTime = currentTime;
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easedProgress = easeOutQuart(progress);
    const current = Math.floor(easedProgress * (target - startVal) + startVal);

    if (target >= 1000) {
      el.textContent = prefix + current.toLocaleString() + suffix;
    } else if (Number.isInteger(target)) {
      el.textContent = prefix + current + suffix;
    } else {
      el.textContent = prefix + (easedProgress * target).toFixed(1) + suffix;
    }

    if (progress < 1) {
      requestAnimationFrame(step);
    } else {
      el.textContent = prefix + (Number.isInteger(target) ? target.toLocaleString() : target) + suffix;
    }
  }

  requestAnimationFrame(step);
}

function initCounters() {
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.dataset.counted) {
        entry.target.dataset.counted = 'true';
        const el = entry.target;
        const target = parseFloat(el.dataset.target);
        const prefix = el.dataset.prefix || '';
        const suffix = el.dataset.suffix || '';
        animateCounter(el, target, 2200, prefix, suffix);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('.counter').forEach(el => {
    counterObserver.observe(el);
  });
}

// ---- Typewriter Effect ----
function initTypewriter() {
  const elements = document.querySelectorAll('[data-typewriter]');
  elements.forEach(el => {
    const text = el.dataset.typewriter;
    const speed = parseInt(el.dataset.speed) || 50;
    el.textContent = '';
    el.style.borderRight = '2px solid currentColor';
    el.style.animation = 'blink 0.8s step-end infinite';

    let i = 0;
    const type = () => {
      if (i < text.length) {
        el.textContent += text.charAt(i);
        i++;
        setTimeout(type, speed);
      } else {
        setTimeout(() => {
          el.style.borderRight = 'none';
          el.style.animation = 'none';
        }, 1500);
      }
    };

    // Start after a delay
    setTimeout(type, parseInt(el.dataset.delay) || 500);
  });
}

// ---- Smooth Scrolling ----
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        const navHeight = 72;
        const top = target.getBoundingClientRect().top + window.scrollY - navHeight;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });
}

// ---- Tabs ----
function initTabs() {
  document.querySelectorAll('.tabs').forEach(tabGroup => {
    const buttons = tabGroup.querySelectorAll('.tab-btn');
    const panelContainer = tabGroup.closest('.tab-section') || document.querySelector('.tab-panels');

    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.dataset.tab;

        // Update button states
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update panel states
        document.querySelectorAll('.tab-panel').forEach(panel => {
          panel.classList.remove('active');
          if (panel.dataset.panel === target) {
            panel.classList.add('active');
          }
        });
      });
    });
  });
}

// ---- Pipeline Interactions ----
function initPipelineInteractions() {
  const nodes = document.querySelectorAll('.pipeline-node');
  nodes.forEach((node, i) => {
    node.addEventListener('click', () => {
      nodes.forEach(n => n.classList.remove('active'));
      node.classList.add('active');

      // Show detail panel if exists
      const detailId = node.dataset.detail;
      if (detailId) {
        document.querySelectorAll('.pipeline-detail').forEach(d => {
          d.style.display = 'none';
        });
        const detail = document.getElementById(detailId);
        if (detail) {
          detail.style.display = 'block';
          detail.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      }
    });
  });
}

// ---- Particle Canvas ----
function initParticleCanvas() {
  const canvas = document.getElementById('hero-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width, height, particles, animationId;

  function resize() {
    width = canvas.width = canvas.offsetWidth;
    height = canvas.height = canvas.offsetHeight;
  }

  class Particle {
    constructor() {
      this.reset();
    }

    reset() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.vx = (Math.random() - 0.5) * 0.5;
      this.vy = (Math.random() - 0.5) * 0.5;
      this.radius = Math.random() * 2 + 1;
      this.opacity = Math.random() * 0.5 + 0.2;
      this.color = Math.random() > 0.5
        ? `rgba(124, 58, 237, ${this.opacity})`
        : Math.random() > 0.5
          ? `rgba(59, 130, 246, ${this.opacity})`
          : `rgba(6, 182, 212, ${this.opacity})`;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;
      if (this.x < 0 || this.x > width) this.vx *= -1;
      if (this.y < 0 || this.y > height) this.vy *= -1;
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = this.color;
      ctx.fill();
    }
  }

  function drawConnections() {
    const maxDist = 130;
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < maxDist) {
          const opacity = (1 - dist / maxDist) * 0.3;
          const gradient = ctx.createLinearGradient(
            particles[i].x, particles[i].y,
            particles[j].x, particles[j].y
          );
          gradient.addColorStop(0, `rgba(124, 58, 237, ${opacity})`);
          gradient.addColorStop(1, `rgba(6, 182, 212, ${opacity})`);
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = gradient;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }
    }
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);
    drawConnections();
    particles.forEach(p => { p.update(); p.draw(); });
    animationId = requestAnimationFrame(animate);
  }

  resize();
  const count = Math.min(80, Math.floor(width * height / 12000));
  particles = Array.from({ length: count }, () => new Particle());

  window.addEventListener('resize', () => {
    resize();
  });

  animate();
}

// ---- Score Bar Animation ----
function initScoreBars() {
  const barObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const fill = entry.target.querySelector('.score-bar-fill');
        if (fill) {
          const targetWidth = fill.dataset.width;
          fill.style.width = targetWidth;
        }
        barObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  document.querySelectorAll('.score-bar-item').forEach(item => {
    const fill = item.querySelector('.score-bar-fill');
    if (fill) {
      fill.style.width = '0%';
      barObserver.observe(item);
    }
  });
}

// Call score bars after DOM ready
document.addEventListener('DOMContentLoaded', initScoreBars);

// ---- Pipeline SVG Animation ----
function initPipelineSVG() {
  const paths = document.querySelectorAll('.pipeline-path');
  paths.forEach((path, i) => {
    const length = path.getTotalLength ? path.getTotalLength() : 300;
    path.style.strokeDasharray = length;
    path.style.strokeDashoffset = length;
    path.style.transition = `stroke-dashoffset 1s ease ${i * 0.3}s`;
  });

  const svgObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const paths = entry.target.querySelectorAll('.pipeline-path');
        paths.forEach(path => {
          path.style.strokeDashoffset = '0';
        });
      }
    });
  }, { threshold: 0.2 });

  document.querySelectorAll('.pipeline-svg-container').forEach(el => {
    svgObserver.observe(el);
  });
}

document.addEventListener('DOMContentLoaded', initPipelineSVG);

// ---- Data Flow Pulse Animation ----
function animateDataFlow() {
  const pulses = document.querySelectorAll('.data-pulse');
  pulses.forEach((pulse, i) => {
    pulse.style.animationDelay = `${i * 0.4}s`;
  });
}

document.addEventListener('DOMContentLoaded', animateDataFlow);
