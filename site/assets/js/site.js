(function ()
{
  const B = window.BSC;
  const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
    'November', 'December'];
  const SHORT = { ma: 'M&A', restructuring: 'Restructuring', placements: 'Capital Raising', valuations: 'Valuation' };

  const $ = (sel, root = document) => root.querySelector(sel);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const initials = (name) => name.split(' ').filter((w) => /^[A-ZÁÉÍÓÚ]/.test(w)).map((w) => w[0]).slice(0, 2).join('');
  const monthYear = (o, short) => o.year ? `${o.month ? MONTHS[o.month - 1].slice(0, short ? 3 : 99) + ' ' : ''}${o.year}` : '';
  const flags = (codes, country) => `<span class="flagged">${codes.map((c) => `<img class="flag" src="assets/img/flags/${c}.svg" alt="" width="22" height="17">`).join('')}<span>${esc(country || '')}</span></span>`;

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

  function avatar(p)
  {
    return `<span class="avatar">${p.img ? `<img src="${p.img}" alt="" width="190" height="190">` : `<span class="initials">${initials(p.name)}</span>`}</span>`;
  }

  document.addEventListener('click', (e) =>
  {
    const btn = e.target.closest('[data-person]');
    if (!btn)
    {
      return;
    }
    const p = B.team.find((x) => x.name === btn.dataset.person);
    openModal(`
      <div class="bio-head">${avatar(p)}<div><h2>${esc(p.name)}</h2><p>${esc(p.title)}${p.exec ? ' · Executive Committee' : ''}</p></div></div>
      <div class="copy">${p.bio.map((b) => `<p>${esc(b)}</p>`).join('')}</div>
      ${p.languages ? `<p class="modal-meta">Languages: ${esc(p.languages)}</p>` : ''}`);
  });

  function dealDesc(d)
  {
    if (d.desc)
    {
      return d.desc;
    }
    return d.practice === 'valuations' ? `Valuation and fairness opinion advisory${d.client && d.client !== d.name ? ' for ' + d.client : ''}.` : '';
  }

  function logoBlock(d)
  {
    return d.logo ? `<img src="${d.logo}" alt="${esc(d.name)}" loading="lazy">` : `<span class="wordlogo">${esc(d.name)}</span>`;
  }

  // Stats and counts
  document.querySelectorAll('[data-stat]').forEach((el) =>
  {
    el.textContent = B.stats[el.dataset.stat];
  });
  document.querySelectorAll('[data-count-sovereign]').forEach((el) =>
  {
    el.textContent = B.deals.filter((d) => d.practice === 'restructuring' && d.sector === 'Sovereign & Public').length;
  });
  document.querySelectorAll('[data-count]').forEach((el) =>
  {
    el.textContent = `${B.deals.filter((d) => d.practice === el.dataset.count).length} transactions`;
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

    $('#latest-news').innerHTML = B.news.slice(0, 3).map((n) => `
      <a class="news-item" href="${n.pdf}" target="_blank" rel="noopener"><h3>${esc(n.title)}</h3><time>${monthYear(n)}</time></a>`).join('');

    // Featured carousel
    const slides = $('#slides');
    const dots = $('#dots');
    slides.innerHTML = B.featured.map((f, i) => `
      <div class="slide${i ? '' : ' active'}" role="tabpanel" aria-hidden="${i ? 'true' : 'false'}">
        <div class="logo"><img src="${f.logo}" alt="${esc(f.name)}"></div>
        <p class="line1">${esc(f.line1)}</p>
        <p class="line2">${esc(f.line2)}</p>
        <p class="role"><span>${esc(f.role)}</span><span class="sep"></span><span>${esc(f.value || f.year)}</span></p>
        <p class="where">${flags(f.flags, f.country)}</p>
      </div>`).join('');
    dots.innerHTML = B.featured.map((f, i) => `<button type="button" role="tab" aria-label="${esc(f.name)}" aria-current="${!i}"></button>`).join('');
    let current = 0;
    let timer;
    const show = (i) =>
    {
      current = (i + B.featured.length) % B.featured.length;
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

    const people = [...B.team.filter((p) => p.group === 'board'), B.team.find((p) => p.name === 'Luis Camarena')];
    $('#leadership').innerHTML = people.map((p) => `
      <button class="mini" type="button" data-person="${esc(p.name)}">${avatar(p)}<span class="n">${esc(p.name)}</span><span class="t">${esc(p.title)}</span></button>`).join('');
  }

  if (page === 'firm')
  {
    const GROUPS = [['all', 'All'], ['board', 'Board of Managers'], ['team', 'Investment Banking & Restructuring'], ['advisors', 'Senior Advisors']];
    const tabs = $('#team-tabs');
    let group = 'all';
    tabs.innerHTML = GROUPS.map(([k, label]) => `<button type="button" data-group="${k}">${label}<span>${k === 'all' ? B.team.length : B.team.filter((p) => p.group === k).length}</span></button>`).join('');
    const render = () =>
    {
      tabs.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', b.dataset.group === group));
      $('#team-grid').innerHTML = B.team.filter((p) => group === 'all' || p.group === group).map((p) => `
        <button class="person" type="button" data-person="${esc(p.name)}">
          ${avatar(p)}<span class="n">${esc(p.name)}</span><span class="t">${esc(p.title)}</span>
          ${p.exec ? '<span class="ec">Executive Committee</span>' : ''}
          <span class="more">View Bio <span class="chev"></span></span>
        </button>`).join('');
    };
    tabs.addEventListener('click', (e) =>
    {
      const b = e.target.closest('button');
      if (b)
      {
        group = b.dataset.group;
        render();
      }
    });
    render();
  }

  if (page === 'news')
  {
    const years = [...new Set(B.news.map((n) => n.year))];
    $('#news').innerHTML = years.map((y) => `<h2 class="year">${y}</h2>` + B.news.filter((n) => n.year === y).map((n) => `
      <a class="news-row" href="${n.pdf}" target="_blank" rel="noopener">
        <time>${monthYear(n, true)}</time><h3>${esc(n.title)}</h3><span class="chev"></span><p>${esc(n.summary)}</p>
      </a>`).join('')).join('');
    $('#research').innerHTML = B.research.map((r) => `
      <div class="research-card"><h3>${esc(r.sector)}</h3>
        ${r.items.map((i) => `<a href="${i.pdf}" target="_blank" rel="noopener">${esc(i.title)}<span>${i.date || 'PDF'}</span></a>`).join('')}
      </div>`).join('');
  }

  if (page === 'alliance')
  {
    const A = window.ALLIANCE;
    document.querySelectorAll('[data-alliance]').forEach((el) =>
    {
      el.textContent = A.stats[el.dataset.alliance];
    });

    // Partner pins first so BroadSpan's sit on top where offices overlap (Miami and Fort Lauderdale)
    const ordered = [...A.firms.slice(1), A.firms[0]];
    $('#pins').innerHTML = ordered.map((f) => f.offices.map((o) => `
      <button class="pin${f.slug === 'broadspan' ? ' own' : ''}" type="button" data-firm="${f.slug}" style="left:${o.x}%;top:${o.y}%" aria-label="${esc(f.name)}, ${esc(o.city)}">
        <span class="tip"><b>${esc(o.city)}</b>${esc(f.name)}</span>
      </button>`).join('')).join('');

    $('#members').innerHTML = A.firms.map((f) =>
    {
      const codes = [...new Set(f.offices.map((o) => o.flag))];
      const body = `
        <span class="member-logo"><img src="${f.logo}" alt="${esc(f.name)}" loading="lazy"></span>
        <span class="member-name">${esc(f.name)}</span>
        <span class="member-flags">${codes.map((c) => `<img class="flag" src="assets/img/flags/${c}.svg" alt="" width="22" height="17">`).join('')}</span>
        <span class="member-cities">${f.offices.map((o) => esc(o.city)).join(' · ')}</span>
        <span class="member-est">Est. ${f.est}</span>`;
      const cls = `member${f.slug === 'broadspan' ? ' own' : ''}`;
      return f.url ? `<a class="${cls}" data-firm="${f.slug}" href="${f.url}" target="_blank" rel="noopener">${body}</a>` : `<div class="${cls}" data-firm="${f.slug}">${body}</div>`;
    }).join('');

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

  if (page === 'transactions')
  {
    const PAGE = 24;
    const params = new URLSearchParams(location.search);
    const state = { practice: params.get('practice') || 'all', region: '', sector: '', q: '', shown: PAGE };
    const tabs = $('#practice-filter');
    tabs.innerHTML = ['all', ...Object.keys(B.practices)].map((k) =>
    {
      const n = k === 'all' ? B.deals.length : B.deals.filter((d) => d.practice === k).length;
      return `<button type="button" data-practice="${k}">${k === 'all' ? 'All' : B.practices[k]}<span>${n}</span></button>`;
    }).join('');
    $('#region-filter').insertAdjacentHTML('beforeend', B.regions.filter((r) => B.deals.some((d) => d.region === r)).map((r) => `<option>${r}</option>`).join(''));
    $('#sector-filter').insertAdjacentHTML('beforeend', B.sectors.filter((s) => B.deals.some((d) => d.sector === s)).map((s) => `<option>${s}</option>`).join(''));

    const matches = (d) =>
      (state.practice === 'all' || d.practice === state.practice) &&
      (!state.region || d.region === state.region) &&
      (!state.sector || d.sector === state.sector) &&
      (!state.q || `${d.name} ${d.client} ${d.country} ${d.desc}`.toLowerCase().includes(state.q));

    let list = [];
    const card = (d, i) => `
      <button class="ts" type="button" data-deal="${i}">
        <div class="ts-logo">${logoBlock(d)}</div>
        <div class="ts-body">
          <div class="ts-top">${flags(d.flags, d.country)}<time>${monthYear(d, true)}</time></div>
          <h3 class="ts-name">${esc(d.name)}</h3>
          <div class="ts-practice">${SHORT[d.practice]}</div>
          <div class="ts-value${d.value ? '' : ' undisclosed'}">${d.value ? esc(d.value) : 'Undisclosed'}</div>
        </div>
      </button>`;

    function render()
    {
      tabs.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', b.dataset.practice === state.practice));
      const active = tabs.querySelector('[aria-pressed="true"]');
      tabs.scrollTo({ left: Math.max(0, active.offsetLeft - 24), behavior: 'smooth' });
      list = B.deals.filter(matches);
      $('#deals').innerHTML = list.slice(0, state.shown).map(card).join('');
      $('#empty').hidden = list.length > 0;
      $('#result-count').textContent = `${list.length} transaction${list.length === 1 ? '' : 's'}`;
      $('#reset').hidden = state.practice === 'all' && !state.region && !state.sector && !state.q;
      $('#more').hidden = list.length <= state.shown;
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
    $('#deals').addEventListener('click', (e) =>
    {
      const b = e.target.closest('[data-deal]');
      if (!b)
      {
        return;
      }
      const d = list[+b.dataset.deal];
      openModal(`
        <div class="deal-modal">
          <div class="deal-modal-logo">${logoBlock(d)}</div>
          <h2>${esc(d.name)}</h2>
          <dl class="facts">
            <div><dt>Practice</dt><dd>${esc(B.practices[d.practice])}</dd></div>
            <div><dt>Country</dt><dd>${d.flags.length ? flags(d.flags, d.country) : esc(d.country || '—')}</dd></div>
            <div><dt>Completed</dt><dd>${monthYear(d) || '—'}</dd></div>
            <div><dt>Value</dt><dd>${esc(d.value || 'Undisclosed')}</dd></div>
          </dl>
          <div class="copy"><p>${esc(dealDesc(d))}</p></div>
          ${d.client && d.client !== d.name ? `<p class="modal-meta">Client: ${esc(d.client)}</p>` : ''}
        </div>`);
    });
    render();
  }

  observe();
})();
