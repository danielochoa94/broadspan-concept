(function ()
{
  const B = window.BSC;
  const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
    'November', 'December'];
  const SHORT = { ma: 'M&A', restructuring: 'Restructuring', placements: 'Capital Raising', valuations: 'Valuation' };

  const $ = (sel, root = document) => root.querySelector(sel);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const initials = (name) => name.split(' ').filter((w) => /^[A-ZÁÉÍÓÚ]/.test(w)).map((w) => w[0]).slice(0, 2).join('');

  // Nav
  const header = $('.site-header');
  $('.nav-toggle')?.addEventListener('click', () =>
  {
    const open = header.classList.toggle('nav-open');
    $('.nav-toggle').setAttribute('aria-expanded', open);
  });
  document.querySelectorAll('.nav a').forEach((a) => a.addEventListener('click', () => header.classList.remove('nav-open')));

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

  // Stats
  document.querySelectorAll('[data-stat]').forEach((el) =>
  {
    const v = { deals: B.stats.deals, restructured: `US$${Math.floor(B.stats.restructuredUsdBn)}B+` }[el.dataset.stat];
    if (v !== undefined)
    {
      el.textContent = v;
    }
  });

  function dealCard(d)
  {
    const date = d.year ? `<time>${d.month ? MONTHS[d.month - 1].slice(0, 3) + ' ' : ''}${d.year}</time>` : '';
    const desc = d.desc || (d.practice === 'valuations' ? `Valuation and fairness opinion advisory${d.client && d.client !== d.name ? ' for ' + d.client : ''}.` : '');
    return `<article class="deal reveal">
      <div class="deal-top"><span>${SHORT[d.practice]}</span>${date}</div>
      <h3 class="deal-name">${esc(d.name)}</h3>
      ${desc ? `<p class="deal-desc">${esc(desc)}</p>` : ''}
      <div class="deal-meta"><span>${esc(d.country || '')}</span>${d.value ? `<span class="deal-value">${esc(d.value)}</span>` : ''}</div>
    </article>`;
  }

  function addMoreToggles(root)
  {
    root.querySelectorAll('.deal-desc').forEach((p) =>
    {
      if (p.scrollHeight > p.clientHeight + 2 && !p.nextElementSibling?.classList.contains('deal-more'))
      {
        p.insertAdjacentHTML('afterend', '<button class="deal-more" type="button">Read more</button>');
      }
    });
  }

  document.addEventListener('click', (e) =>
  {
    const btn = e.target.closest('.deal-more');
    if (btn)
    {
      const open = btn.closest('.deal').classList.toggle('open');
      btn.textContent = open ? 'Show less' : 'Read more';
    }
  });

  function avatar(p)
  {
    return `<span class="avatar">${p.img ? `<img src="${p.img}" alt="" width="190" height="190">` : `<span class="initials">${initials(p.name)}</span>`}</span>`;
  }

  function personCard(p)
  {
    const badge = p.exec ? '<span class="badge">Executive Committee</span>' : '';
    return `<button class="person reveal" type="button" data-person="${esc(p.name)}">
      ${avatar(p)}
      <span class="person-name">${esc(p.name)}</span>
      <span class="person-title">${esc(p.title)}</span>${badge}
    </button>`;
  }

  function newsItem(n)
  {
    const date = `${n.month ? MONTHS[n.month - 1].slice(0, 3) + ' ' : ''}${n.year}`;
    return `<a class="news-item reveal" href="${n.pdf}" target="_blank" rel="noopener">
      <time>${date}</time><h3>${esc(n.title)}</h3><span class="tag">PDF ↗</span><p>${esc(n.summary)}</p>
    </a>`;
  }

  // Bio dialog
  const dialog = $('dialog.bio');
  if (dialog)
  {
    document.addEventListener('click', (e) =>
    {
      const btn = e.target.closest('[data-person]');
      if (!btn)
      {
        return;
      }
      const p = B.team.find((x) => x.name === btn.dataset.person);
      $('.bio-content', dialog).innerHTML = `
        <div class="bio-head">${avatar(p)}<div><h2 class="h3" id="bio-title">${esc(p.name)}</h2>
          <p class="person-title">${esc(p.title)}${p.exec ? ' · Executive Committee' : ''}</p></div></div>
        <div class="bio-body">${p.bio.map((b) => `<p>${esc(b)}</p>`).join('')}</div>
        ${p.languages ? `<p class="bio-langs">Languages: ${esc(p.languages)}</p>` : ''}`;
      dialog.showModal();
      dialog.scrollTop = 0;
    });
    dialog.addEventListener('click', (e) =>
    {
      if (e.target === dialog || e.target.closest('.bio-close'))
      {
        dialog.close();
      }
    });
  }

  const page = document.body.dataset.page;

  if (page === 'home')
  {
    const featured = ['Republic of Ecuador', 'Province of Buenos Aires', 'Puerto Rico Employees Retirement System',
      'Latin American Agribusiness Development Corp.', 'Instacredit', 'Bancolombia'];
    $('#featured-deals').innerHTML = featured.map((n) => dealCard(B.deals.find((d) => d.name === n))).join('');
    addMoreToggles($('#featured-deals'));
    $('#leadership').innerHTML = B.team.filter((p) => p.group === 'board').map(personCard).join('');
    $('#latest-news').innerHTML = B.news.slice(0, 4).map(newsItem).join('');
    document.querySelectorAll('[data-count]').forEach((el) =>
    {
      const [practice, scope] = el.dataset.count.split(':');
      const sovereign = (d) => d.sector === 'Sovereign & Public';
      el.textContent = B.deals.filter((d) => d.practice === practice && (!scope || (scope === 'sovereign') === sovereign(d))).length;
    });
  }

  if (page === 'firm')
  {
    const groups = [
      ['board', 'Board of Managers', 'Leadership and governance'],
      ['team', 'Investment Banking & Restructuring', 'Miami · Mexico City · Medellín · Rio de Janeiro · São Paulo'],
      ['advisors', 'Senior Advisors', 'Former CEOs, bankers and public officials'],
    ];
    $('#team-groups').innerHTML = groups.map(([key, title, sub]) => `
      <div class="team-group">
        <div class="team-group-head"><h3 class="h3">${title}</h3><span>${sub}</span></div>
        <div class="people">${B.team.filter((p) => p.group === key).map(personCard).join('')}</div>
      </div>`).join('');
  }

  if (page === 'news')
  {
    const years = [...new Set(B.news.map((n) => n.year))];
    $('#news').innerHTML = years.map((y) => `
      <div class="year-group"><div class="year-label">${y}</div>
        <div class="news-list">${B.news.filter((n) => n.year === y).map(newsItem).join('')}</div></div>`).join('');
    $('#research').innerHTML = B.research.map((r) => `
      <div class="research-card reveal"><h3>${esc(r.sector)}</h3>
        ${r.items.map((i) => `<a href="${i.pdf}" target="_blank" rel="noopener">${esc(i.title)}<span>${i.date || 'PDF'} ↗</span></a>`).join('')}
      </div>`).join('');
  }

  if (page === 'transactions')
  {
    const PAGE = 24;
    const params = new URLSearchParams(location.search);
    const state = { practice: params.get('practice') || 'all', region: '', sector: '', q: '', shown: PAGE };
    const practiceKeys = ['all', ...Object.keys(B.practices)];

    const seg = $('#practice-filter');
    seg.innerHTML = practiceKeys.map((k) =>
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

    function render()
    {
      seg.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', b.dataset.practice === state.practice));
      const active = seg.querySelector('[aria-pressed="true"]');
      seg.scrollTo({ left: Math.max(0, active.offsetLeft - 20), behavior: 'smooth' });
      const list = B.deals.filter(matches);
      const grid = $('#deals');
      grid.innerHTML = list.slice(0, state.shown).map(dealCard).join('');
      $('#empty').hidden = list.length > 0;
      $('#result-count').textContent = `${list.length} transaction${list.length === 1 ? '' : 's'}`;
      $('#reset').hidden = state.practice === 'all' && !state.region && !state.sector && !state.q;
      $('#more').hidden = list.length <= state.shown;
      addMoreToggles(grid);
      observe(grid);
    }

    const update = (patch) =>
    {
      Object.assign(state, patch, { shown: PAGE });
      const url = new URL(location.href);
      state.practice === 'all' ? url.searchParams.delete('practice') : url.searchParams.set('practice', state.practice);
      history.replaceState(null, '', url);
      render();
    };

    seg.addEventListener('click', (e) =>
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
