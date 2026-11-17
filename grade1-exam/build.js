// Renders exam.html and answer-key.html to A4 PDFs: node build.js
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const [src, out] of [['exam.html', 'Grade1_ELA_First_Term_Exam.pdf'], ['answer-key.html', 'Grade1_ELA_First_Term_Answer_Key.pdf']]) {
    await page.goto('file://' + path.join(__dirname, src));
    await page.evaluate(() => document.fonts.ready);
    await page.pdf({ path: path.join(__dirname, out), format: 'A4', printBackground: true, preferCSSPageSize: true });
    console.log('wrote', out);
  }
  await browser.close();
})();
