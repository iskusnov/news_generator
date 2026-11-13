// node render_pdf.js data.json out.pdf — шпаргалка к уроку (cheatsheet.html, A4) в PDF через Chromium.
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const [dp, out] = process.argv.slice(2);
  const data = fs.readFileSync(dp, 'utf8');
  const b = await chromium.launch(); const p = await b.newPage();
  await p.addInitScript(`window.DATA=${data}`);
  await p.goto('file://' + path.join(__dirname, process.env.TPL || 'cheatsheet.html'));
  await p.evaluate(() => document.fonts.ready.then(() => 1));
  await p.pdf({ path: out, format: 'A4', printBackground: true, margin: { top: '0', bottom: '0', left: '0', right: '0' } });
  await b.close(); console.log('ok', out);
})();
