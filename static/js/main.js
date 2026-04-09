/* ============================================================
   Dristhi Earth — Main JavaScript
   ============================================================ */

(function () {
  'use strict';

  // ── CSRF token helper ─────────────────────────────────────
  function getCsrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  // ── Nav scroll effect ──────────────────────────────────────
  const nav = document.querySelector('.nav');
  if (nav) {
    const onScroll = () => {
      nav.classList.toggle('scrolled', window.scrollY > 50);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ── Active nav link ────────────────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav__link, .nav__mobile-link').forEach(function (link) {
    const href = link.getAttribute('href');
    if (!href) return;
    const isHome = (currentPath === '/' || currentPath === '') && (href === '/' || href === '');
    const isMatch = href !== '/' && currentPath.startsWith(href);
    if (isHome || isMatch) {
      link.classList.add('active');
    }
  });

  // ── Mobile hamburger ───────────────────────────────────────
  const hamburger = document.querySelector('.nav__hamburger');
  const mobileNav = document.querySelector('.nav__mobile');
  if (hamburger && mobileNav) {
    hamburger.addEventListener('click', function () {
      const isOpen = hamburger.classList.toggle('open');
      mobileNav.classList.toggle('open', isOpen);
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });

    mobileNav.querySelectorAll('.nav__mobile-link').forEach(function (link) {
      link.addEventListener('click', function () {
        hamburger.classList.remove('open');
        mobileNav.classList.remove('open');
        document.body.style.overflow = '';
      });
    });
  }

  // ── IntersectionObserver fade-in ───────────────────────────
  const fadeEls = document.querySelectorAll('.fade-in');
  if (fadeEls.length && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );
    fadeEls.forEach(function (el) { observer.observe(el); });
  } else {
    // Fallback: make all visible immediately
    fadeEls.forEach(function (el) { el.classList.add('visible'); });
  }

  // ── Contact form AJAX ──────────────────────────────────────
  const contactForm = document.getElementById('contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();
      clearFormErrors(contactForm);

      const submitBtn = contactForm.querySelector('[type="submit"]');
      const originalText = submitBtn.textContent;
      submitBtn.textContent = 'Sending…';
      submitBtn.disabled = true;

      const data = {
        name: getValue(contactForm, 'name'),
        organisation: getValue(contactForm, 'organisation'),
        country: getValue(contactForm, 'country'),
        email: getValue(contactForm, 'email'),
        service_interest: getValue(contactForm, 'service_interest'),
        message: getValue(contactForm, 'message'),
      };

      fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify(data),
      })
        .then(function (res) { return res.json().then(function (body) { return { status: res.status, body: body }; }); })
        .then(function (result) {
          if (result.body.success) {
            contactForm.style.display = 'none';
            const success = document.getElementById('contact-success');
            if (success) success.style.display = 'block';
          } else {
            if (result.body.errors) {
              showFormErrors(contactForm, result.body.errors);
            }
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
          }
        })
        .catch(function () {
          showFieldError(contactForm, 'general', 'A network error occurred. Please try again.');
          submitBtn.textContent = originalText;
          submitBtn.disabled = false;
        });
    });
  }

  // ── Newsletter form AJAX ───────────────────────────────────
  document.querySelectorAll('.newsletter-form').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      clearFormErrors(form);

      const submitBtn = form.querySelector('[type="submit"]');
      const originalText = submitBtn.textContent;
      submitBtn.textContent = 'Subscribing…';
      submitBtn.disabled = true;

      const emailInput = form.querySelector('input[name="email"]');
      const sourcePage = form.dataset.source || window.location.pathname;

      fetch('/api/newsletter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ email: emailInput ? emailInput.value : '', source_page: sourcePage }),
      })
        .then(function (res) { return res.json().then(function (body) { return { status: res.status, body: body }; }); })
        .then(function (result) {
          if (result.body.success) {
            const msg = form.querySelector('.newsletter-success');
            if (msg) {
              msg.textContent = result.body.message;
              msg.style.display = 'block';
            }
            form.querySelector('.input-row').style.display = 'none';
          } else {
            if (result.body.errors && result.body.errors.email) {
              showFieldError(form, 'email', result.body.errors.email);
            }
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
          }
        })
        .catch(function () {
          submitBtn.textContent = originalText;
          submitBtn.disabled = false;
        });
    });
  });

  // ── Helpers ───────────────────────────────────────────────
  function getValue(form, name) {
    const el = form.querySelector('[name="' + name + '"]');
    return el ? el.value.trim() : '';
  }

  function clearFormErrors(form) {
    form.querySelectorAll('.form-error').forEach(function (el) {
      el.textContent = '';
    });
    form.querySelectorAll('.form-input, .form-select, .form-textarea').forEach(function (el) {
      el.style.borderColor = '';
    });
    const general = document.getElementById('form-error-general');
    if (general) general.textContent = '';
  }

  function showFormErrors(form, errors) {
    Object.keys(errors).forEach(function (field) {
      showFieldError(form, field, errors[field]);
    });
  }

  function showFieldError(form, field, message) {
    if (field === 'general') {
      const el = document.getElementById('form-error-general') || form.querySelector('.form-error--general');
      if (el) { el.textContent = message; return; }
    }
    const errorEl = form.querySelector('[data-error="' + field + '"]');
    if (errorEl) errorEl.textContent = message;
    const input = form.querySelector('[name="' + field + '"]');
    if (input) input.style.borderColor = '#e07070';
  }

})();
