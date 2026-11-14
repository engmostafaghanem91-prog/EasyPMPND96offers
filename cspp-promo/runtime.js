(() => {
  const TL = window.TIMELINE;
  const scenes = [...document.querySelectorAll('.scene')].map(el => ({ el, s: +el.dataset.s, e: +el.dataset.e }));
  const counters = [...document.querySelectorAll('.count')];
  const bar = document.querySelector('.progress i');
  const cv = document.getElementById('fx');
  const ctx = cv.getContext('2d');

  // deterministic particles
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const P = Array.from({ length: 64 }, () => ({
    x: rnd() * 1080, y: rnd() * 2020, v: 18 + rnd() * 55, a: 20 + rnd() * 60, f: 0.2 + rnd() * 0.6,
    ph: rnd() * 6.28, r: 2 + rnd() * 5, leaf: rnd() < 0.28, rot: rnd() * 6.28, rs: (rnd() - 0.5) * 1.2,
    c: rnd() < 0.5 ? '163,230,53' : (rnd() < 0.5 ? '52,211,153' : '45,212,191'), o: 0.25 + rnd() * 0.5,
  }));

  function particles(t) {
    ctx.clearRect(0, 0, 1080, 1920);
    for (const p of P) {
      const y = ((p.y - p.v * t) % 2020 + 2020) % 2020 - 50;
      const x = p.x + Math.sin(t * p.f + p.ph) * p.a;
      const tw = 0.6 + 0.4 * Math.sin(t * 2 * p.f + p.ph * 3);
      ctx.save();
      ctx.translate(x, y);
      ctx.globalAlpha = p.o * tw;
      ctx.shadowColor = `rgba(${p.c},0.9)`;
      ctx.shadowBlur = 16;
      ctx.fillStyle = `rgba(${p.c},1)`;
      if (p.leaf) {
        ctx.rotate(p.rot + t * p.rs);
        ctx.beginPath();
        ctx.ellipse(0, 0, p.r * 2.6, p.r * 1.1, 0, 0, Math.PI * 2);
        ctx.fill();
      } else {
        ctx.beginPath();
        ctx.arc(0, 0, p.r * 0.8, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }
  }

  const easeOut = p => 1 - Math.pow(1 - p, 3);

  const BR = (TL.broll || []).map(b => ({ ...b, el: document.getElementById('bv_' + b.clip) }));
  const pingpong = (i, n) => { const m = 2 * (n - 1); i = i % m; return i < n ? i : m - i; };
  async function broll(t) {
    const waits = [];
    for (const b of BR) {
      if (t < b.s - 0.05 || t > b.e + 0.05) { b.el.style.opacity = 0; continue; }
      const fin = Math.min(1, (t - b.s) / 0.9), fout = Math.min(1, (b.e - t) / 0.9);
      b.el.style.opacity = (Math.max(0, Math.min(fin, fout)) * b.op).toFixed(3);
      const idx = pingpong(Math.floor((t - b.s) * 30 * b.speed), b.n) + 1;
      const src = `broll/${b.clip}/f_${String(idx).padStart(4, '0')}.jpg`;
      if (b.el.getAttribute('src') !== src) { b.el.setAttribute('src', src); waits.push(b.el.decode().catch(() => {})); }
    }
    await Promise.all(waits);
  }

  window.setTime = async (t) => {
    await broll(t);
    for (const sc of scenes) sc.el.style.visibility = (t >= sc.s - 0.05 && t <= sc.e + 0.05) ? 'visible' : 'hidden';
    for (const a of document.getAnimations()) { a.pause(); a.currentTime = t * 1000; }
    for (const c of counters) {
      const t0 = +c.dataset.t0, d = +c.dataset.dur, from = +c.dataset.from, to = +c.dataset.to;
      const p = Math.max(0, Math.min(1, (t - t0) / d));
      c.textContent = Math.round(from + (to - from) * easeOut(p));
    }
    bar.style.width = (Math.min(1, t / TL.total) * 100) + '%';
    particles(t);
  };

  window.ready = document.fonts.ready.then(() => window.setTime(0)).then(() => true);
})();
