// /topla sayfası ekran görüntüleri: giriş ve çizim ekranı (gönderim yapılmaz, yalnız ekran görüntüsü)
const path = require("path");
const fs = require("fs");
const puppeteer = require("C:/Users/slapm/OneDrive/Desktop/FinalCepKonsol/cizim-tanima/docs/sunum/node_modules/puppeteer-core");
const KOK = "C:/Users/slapm/OneDrive/Desktop/FinalCepKonsol/cizim-tanima";
const SINIF = JSON.parse(fs.readFileSync(KOK + "/demo/public/model/siniflar.json", "utf8"));
const bekle = (ms) => new Promise((r) => setTimeout(r, ms));
function cizimAl(en, sira) {
  return JSON.parse(fs.readFileSync(`${KOK}/veri/islenmis/test_vuruslar/${en}.ndjson`, "utf8").trim().split("\n")[sira]);
}
async function ciz(page, secici, vuruslar) {
  const kutu = await (await page.$(secici)).boundingBox();
  const o = Math.min(kutu.width, kutu.height) * 0.7 / 255;
  const ox = kutu.x + (kutu.width - 255 * o) / 2, oy = kutu.y + (kutu.height - 255 * o) / 2;
  for (const [xs, ys] of vuruslar) {
    await page.mouse.move(ox + xs[0] * o, oy + ys[0] * o); await page.mouse.down();
    for (let i = 1; i < xs.length; i++) await page.mouse.move(ox + xs[i] * o, oy + ys[i] * o, { steps: 4 });
    await page.mouse.up(); await bekle(60);
  }
}
(async () => {
  const t = await puppeteer.launch({ executablePath: "C:/Users/slapm/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe", args: ["--mute-audio"] });
  const p = await t.newPage();
  await p.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });
  await p.goto("https://cizim-tanima.vercel.app/topla", { waitUntil: "networkidle0" });
  await bekle(1000);
  await p.type("#takmaAd", "ornek");
  await p.click("#onay");
  await p.screenshot({ path: path.join(__dirname, "topla-giris.png") });
  await p.click("#basla");
  await bekle(1500);
  const kelime = (await p.$eval("#kelime", (e) => e.textContent)).trim().toLowerCase();
  const s = SINIF.find((x) => kelime.includes(x.tr.toLowerCase()));
  console.log("kelime", kelime, s && s.en);
  if (s) await ciz(p, "#tuval", cizimAl(s.en, 2));
  await bekle(800);
  await p.screenshot({ path: path.join(__dirname, "topla-cizim.png") });
  await t.close();
})().catch((h) => { console.error(h); process.exit(1); });
