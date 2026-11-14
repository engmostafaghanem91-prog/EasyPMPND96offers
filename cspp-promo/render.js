// Usage:
//   node render.js frames            -> renders every frame to build/frames/*.jpg (parallel workers)
//   node render.js stills 3.2 10 ... -> renders single frames to build/stills/ for preview
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const PAGE = 'file://' + path.join(ROOT, 'build', 'index.html');
const TL = JSON.parse(fs.readFileSync(path.join(ROOT, 'build', 'timeline.json'), 'utf8'));
const WORKERS = +(process.env.WORKERS || 4);

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto(PAGE);
  await page.evaluate(() => window.ready);
  return page;
}

async function shot(page, t, file) {
  await page.evaluate(tt => window.setTime(tt), t);
  await page.screenshot({ path: file, type: 'jpeg', quality: 93 });
}

(async () => {
  const mode = process.argv[2] || 'frames';
  const browser = await chromium.launch({ args: ['--disable-gpu-vsync', '--force-color-profile=srgb'] });
  if (mode === 'stills') {
    const dir = path.join(ROOT, 'build', 'stills');
    fs.mkdirSync(dir, { recursive: true });
    const page = await openPage(browser);
    for (const ts of process.argv.slice(3)) {
      await shot(page, +ts, path.join(dir, `t_${(+ts).toFixed(2)}.jpg`));
      console.log('still', ts);
    }
  } else {
    const dir = path.join(ROOT, 'build', 'frames');
    fs.mkdirSync(dir, { recursive: true });
    const N = Math.ceil(TL.total * TL.fps);
    const per = Math.ceil(N / WORKERS);
    const t0 = Date.now();
    let done = 0;
    await Promise.all(Array.from({ length: WORKERS }, async (_, w) => {
      const page = await openPage(browser);
      for (let i = w * per; i < Math.min(N, (w + 1) * per); i++) {
        await shot(page, i / TL.fps, path.join(dir, `f_${String(i).padStart(5, '0')}.jpg`));
        if (++done % 150 === 0) console.log(`${done}/${N} frames  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
      }
    }));
    console.log(`rendered ${N} frames in ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  await browser.close();
})();
