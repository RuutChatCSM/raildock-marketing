
(() => {
  const nav = document.querySelector('.nav');
  const menu = document.querySelector('.menu');
  menu?.addEventListener('click', () => {
    const open = nav?.classList.toggle('mobile-open') ?? false;
    menu.setAttribute('aria-expanded', String(open));
  });
  nav?.querySelectorAll('.nav-links a').forEach(a => a.addEventListener('click', () => {
    nav.classList.remove('mobile-open'); menu?.setAttribute('aria-expanded','false');
  }));

  const rail = document.querySelector('.scroll-rail');
  const updateRail = () => {
    if (!rail) return;
    const max = document.documentElement.scrollHeight - innerHeight;
    rail.style.width = `${max > 0 ? Math.min(100, scrollY / max * 100) : 0}%`;
  };
  addEventListener('scroll', updateRail, {passive:true}); updateRail();

  document.querySelectorAll('[data-copy]').forEach(btn => btn.addEventListener('click', async () => {
    const value = btn.getAttribute('data-copy') || btn.closest('.command')?.querySelector('code')?.textContent || '';
    try { await navigator.clipboard.writeText(value); const old = btn.textContent; btn.textContent='Copied'; btn.classList.add('copied'); setTimeout(()=>{btn.textContent=old;btn.classList.remove('copied')},1300); } catch (_) {}
  }));

  const contextViewer = document.querySelector('[data-context-viewer]');
  if (contextViewer) {
    const imageWrap = contextViewer.querySelector('[data-context-image]');
    const image = imageWrap?.querySelector('img');
    const tag = imageWrap?.querySelector('[data-context-tag]');
    const number = contextViewer.querySelector('[data-context-number]');
    const title = contextViewer.querySelector('[data-context-title]');
    const body = contextViewer.querySelector('[data-context-body]');
    const fact1 = contextViewer.querySelector('[data-fact-1]');
    const fact2 = contextViewer.querySelector('[data-fact-2]');
    const tabs = [...contextViewer.querySelectorAll('[data-context-tab]')];
    let active = 0, timer;
    const render = (i, restart=false) => {
      const tab = tabs[i];
      if (!tab || !image) return;
      active = i;
      tabs.forEach((t,j)=>t.setAttribute('aria-selected',String(i===j)));
      imageWrap?.classList.add('is-switching');
      setTimeout(()=>{
        image.src = tab.dataset.src;
        image.alt = tab.dataset.alt || '';
        if (tag) tag.textContent = tab.dataset.tag || '';
        if (number) number.textContent = tab.dataset.number || `0${i+1}`;
        if (title) title.textContent = tab.dataset.title || '';
        if (body) body.textContent = tab.dataset.body || '';
        if (fact1) { fact1.querySelector('b').textContent=tab.dataset.fact1 || ''; fact1.querySelector('span').textContent=tab.dataset.fact1Meta || ''; }
        if (fact2) { fact2.querySelector('b').textContent=tab.dataset.fact2 || ''; fact2.querySelector('span').textContent=tab.dataset.fact2Meta || ''; }
        imageWrap?.classList.remove('is-switching');
      },180);
      if (restart) start();
    };
    const start=()=>{clearInterval(timer);if(!matchMedia('(prefers-reduced-motion: reduce)').matches)timer=setInterval(()=>render((active+1)%tabs.length),7000)};
    tabs.forEach((tab,i)=>tab.addEventListener('click',()=>render(i,true)));
    contextViewer.addEventListener('mouseenter',()=>clearInterval(timer));
    contextViewer.addEventListener('mouseleave',start);
    start();
  }

})();
