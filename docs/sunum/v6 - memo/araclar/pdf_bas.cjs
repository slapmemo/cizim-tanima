const puppeteer = require("C:/Users/slapm/OneDrive/Desktop/FinalCepKonsol/cizim-tanima/docs/sunum/node_modules/puppeteer-core");
const CHROME = "C:/Users/slapm/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe";
(async () => {
  const [, , html, pdf] = process.argv;
  const b = await puppeteer.launch({ executablePath: CHROME, headless: true });
  const p = await b.newPage(); await p.setViewport({ width: 1920, height: 1080 });
  await p.goto(require("url").pathToFileURL(html).href, { waitUntil: "networkidle0", timeout: 120000 });
  await p.evaluateHandle("document.fonts.ready"); await new Promise((r) => setTimeout(r, 1500));
  await p.pdf({ path: pdf, preferCSSPageSize: true, printBackground: true });
  await b.close();
})();
