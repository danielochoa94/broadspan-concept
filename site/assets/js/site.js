(function ()
{
  const $ = (sel, root = document) => root.querySelector(sel);

  // Nav
  const header = $('.site-header');
  $('.nav-toggle').addEventListener('click', () =>
  {
    const open = header.classList.toggle('nav-open');
    $('.nav-toggle').setAttribute('aria-expanded', open);
  });

  // Reveal on scroll
  const io = 'IntersectionObserver' in window && new IntersectionObserver((entries) =>
  {
    entries.forEach((e) =>
    {
      if (e.isIntersecting)
      {
        e.target.classList.add('in');
        io.unobserve(e.target);
      }
    });
  }, { rootMargin: '0px 0px -8% 0px' });
  const observe = (root = document) => root.querySelectorAll('.reveal:not(.in)').forEach((el) => io ? io.observe(el) : el.classList.add('in'));

  // Modal
  const modal = $('dialog.modal');
  const openModal = (html) =>
  {
    $('.modal-body', modal).innerHTML = html;
    modal.showModal();
    modal.scrollTop = 0;
  };
  modal.addEventListener('click', (e) =>
  {
    if (e.target === modal || e.target.closest('.modal-close'))
    {
      modal.close();
    }
  });

  document.addEventListener('click', (e) =>
  {
    const b = e.target.closest('[data-deal], [data-person]');
    if (b)
    {
      openModal($(b.dataset.deal ? `#deal-${b.dataset.deal}` : `#bio-${b.dataset.person}`).innerHTML);
    }
  });

  const page = document.body.dataset.page;

  if (page === 'home')
  {
    // Hero: city labels follow the montage segments in hero.mp4
    const CITIES = [['Miami', 0], ['Mexico City', 3.8], ['Medellín', 7.6], ['Rio de Janeiro', 11.4], ['São Paulo', 15.2]];
    const END = 19.8;
    const video = $('#hero-video');
    const wrap = $('#cities');
    wrap.innerHTML = CITIES.map(([n]) => `<button class="city" type="button"><span class="bar"><i></i></span><span class="name">${n}</span></button>`).join('');
    const btns = [...wrap.children];
    btns.forEach((b, i) => b.addEventListener('click', () =>
    {
      video.currentTime = CITIES[i][1] + 0.45;
      video.play();
    }));
    const tick = () =>
    {
      const t = video.currentTime;
      btns.forEach((b, i) =>
      {
        const start = CITIES[i][1] + (i ? 0.4 : 0);
        const end = i < CITIES.length - 1 ? CITIES[i + 1][1] + 0.4 : END;
        const active = t >= start && t < end;
        b.classList.toggle('active', active);
        b.classList.toggle('done', t >= end);
        $('i', b).style.transform = active ? `scaleX(${(t - start) / (end - start)})` : '';
      });
      requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);

    const slides = $('#slides');
    const dots = $('#dots');
    const count = slides.children.length;
    let current = 0;
    let timer;
    const show = (i) =>
    {
      current = (i + count) % count;
      [...slides.children].forEach((s, k) =>
      {
        s.classList.toggle('active', k === current);
        s.setAttribute('aria-hidden', k !== current);
      });
      [...dots.children].forEach((d, k) => d.setAttribute('aria-current', k === current));
    };
    const start = () =>
    {
      clearInterval(timer);
      timer = setInterval(() => show(current + 1), 6000);
    };
    dots.addEventListener('click', (e) =>
    {
      const i = [...dots.children].indexOf(e.target);
      if (i >= 0)
      {
        show(i);
        start();
      }
    });
    let x0 = null;
    slides.addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; }, { passive: true });
    slides.addEventListener('touchend', (e) =>
    {
      const dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 40)
      {
        show(current + (dx < 0 ? 1 : -1));
        start();
      }
    });
    slides.parentElement.addEventListener('mouseenter', () => clearInterval(timer));
    slides.parentElement.addEventListener('mouseleave', start);
    start();
  }

  if (page === 'firm')
  {
    const tabs = $('#team-tabs');
    tabs.addEventListener('click', (e) =>
    {
      const b = e.target.closest('button');
      if (!b)
      {
        return;
      }
      tabs.querySelectorAll('button').forEach((t) => t.setAttribute('aria-pressed', t === b));
      document.querySelectorAll('#team-grid .person').forEach((p) =>
      {
        p.hidden = b.dataset.group !== 'all' && p.dataset.group !== b.dataset.group;
      });
    });
  }

  if (page === 'alliance')
  {
    const world = $('.world');
    const highlight = (slug) =>
    {
      world.classList.toggle('focus', !!slug);
      world.querySelectorAll('.pin').forEach((p) => p.classList.toggle('on', p.dataset.firm === slug));
    };
    ['mouseover', 'focusin'].forEach((ev) => document.addEventListener(ev, (e) =>
    {
      const el = e.target.closest('[data-firm]');
      highlight(el && el.dataset.firm);
    }));
  }

  if (page === 'contact')
  {
    const form = $('#contact-form');
    const interest = $('#interest');
    const requested = new URLSearchParams(location.search).get('interest');
    if ([...interest.options].some((o) => o.value === requested))
    {
      interest.value = requested;
    }
    // Preview only: no form backend is wired up yet, so submissions just show the confirmation.
    form.addEventListener('submit', (e) =>
    {
      e.preventDefault();
      form.hidden = true;
      const message = $('#form-message');
      message.textContent = 'Thank you. A member of our team will be in touch shortly.';
      message.hidden = false;
    });
  }

  if (page === 'client-login')
  {
    // Preview only: the client portal isn't connected, so sign-in attempts explain that instead of failing silently.
    const form = $('#login-form');
    form.addEventListener('submit', (e) =>
    {
      e.preventDefault();
      const message = $('#form-message');
      message.textContent = 'Client login is not connected in this preview.';
      message.hidden = false;
    });
  }

  if (page === 'transactions')
  {
    const PAGE = 24;
    const params = new URLSearchParams(location.search);
    const state = { practice: params.get('practice') || 'all', region: '', sector: '', q: '', shown: PAGE };
    const tabs = $('#practice-filter');
    const cards = [...$('#deals').children].map((el) =>
    {
      const detail = $(`#deal-${el.dataset.deal}`);
      const text = [$('.ts-name', el), $('.flagged', el), $('.copy', detail), $('.modal-meta', detail)]
        .map((n) => n ? n.textContent : '').join(' ').toLowerCase();
      return { el, text };
    });

    const matches = ({ el, text }) =>
      (state.practice === 'all' || el.dataset.practice === state.practice) &&
      (!state.region || el.dataset.region === state.region) &&
      (!state.sector || el.dataset.sector === state.sector) &&
      (!state.q || text.includes(state.q));

    function render()
    {
      tabs.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', b.dataset.practice === state.practice));
      const active = tabs.querySelector('[aria-pressed="true"]');
      tabs.scrollTo({ left: Math.max(0, active.offsetLeft - 24), behavior: 'smooth' });
      let total = 0;
      cards.forEach((c) =>
      {
        c.el.hidden = !matches(c) || ++total > state.shown;
      });
      $('#empty').hidden = total > 0;
      $('#result-count').textContent = `${total} transaction${total === 1 ? '' : 's'}`;
      $('#reset').hidden = state.practice === 'all' && !state.region && !state.sector && !state.q;
      $('#more').hidden = total <= state.shown;
    }

    const update = (patch) =>
    {
      Object.assign(state, patch, { shown: PAGE });
      const url = new URL(location.href);
      state.practice === 'all' ? url.searchParams.delete('practice') : url.searchParams.set('practice', state.practice);
      history.replaceState(null, '', url);
      render();
    };

    tabs.addEventListener('click', (e) =>
    {
      const b = e.target.closest('button');
      if (b)
      {
        update({ practice: b.dataset.practice });
      }
    });
    $('#region-filter').addEventListener('change', (e) => update({ region: e.target.value }));
    $('#sector-filter').addEventListener('change', (e) => update({ sector: e.target.value }));
    $('#search').addEventListener('input', (e) => update({ q: e.target.value.trim().toLowerCase() }));
    $('#reset').addEventListener('click', () =>
    {
      $('#region-filter').value = '';
      $('#sector-filter').value = '';
      $('#search').value = '';
      update({ practice: 'all', region: '', sector: '', q: '' });
    });
    $('#more button').addEventListener('click', () =>
    {
      state.shown += PAGE;
      render();
    });
    render();
  }

  observe();
})();
