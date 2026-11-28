// cizim-tanima.vercel.app ekran görüntüleri (sunum için)
const path = require("path");
const fs = require("fs");
const puppeteer = require("C:/Users/slapm/OneDrive/Desktop/FinalCepKonsol/cizim-tanima/docs/sunum/node_modules/puppeteer-core");

const KOK = "C:/Users/slapm/OneDrive/Desktop/FinalCepKonsol/cizim-tanima";
const CIKTI = __dirname;
const CHROME = "C:/Users/slapm/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe";
const SINIF = JSON.parse(fs.readFileSync(KOK + "/demo/public/model/siniflar.json", "utf8"));
const bekle = (ms) => new Promise((r) => setTimeout(r, ms));

function cizimAl(en, sira = 3) {
  const satirlar = fs.readFileSync(`${KOK}/veri/islenmis/test_vuruslar/${en}.ndjson`, "utf8").trim().split("\n");
  return JSON.parse(satirlar[sira]);
}

async function ciz(page, secici, vuruslar, oran = 1, bekleMs = 6) {
  const kutu = await (await page.$(secici)).boundingBox();
  const olcek = Math.min(kutu.width, kutu.height) * 0.7 / 255;
  const ox = kutu.x + (kutu.width - 255 * olcek) / 2, oy = kutu.y + (kutu.height - 255 * olcek) / 2;
  const toplam = vuruslar.reduce((t, v) => t + v[0].length, 0);
  let kalan = Math.max(1, Math.ceil(toplam * oran));
  for (const [xs, ys] of vuruslar) {
    if (kalan <= 0) break;
    const n = Math.min(kalan, xs.length);
    await page.mouse.move(ox + xs[0] * olcek, oy + ys[0] * olcek);
    await page.mouse.down();
    for (let i = 1; i < n; i++) {
      // ara noktalar: gerçek fare hareketi gibi
      const x0 = xs[i - 1], y0 = ys[i - 1], x1 = xs[i], y1 = ys[i];
      const adim = Math.max(1, Math.round(Math.hypot(x1 - x0, y1 - y0) / 6));
      for (let k = 1; k <= adim; k++) {
        await page.mouse.move(ox + (x0 + (x1 - x0) * k / adim) * olcek, oy + (y0 + (y1 - y0) * k / adim) * olcek);
        await bekle(bekleMs);
      }
    }
    await page.mouse.up();
    kalan -= n;
    await bekle(80);
  }
}

(async () => {
  const tarayici = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ["--mute-audio"] });
  const page = await tarayici.newPage();
  await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });
  await page.goto("https://cizim-tanima.vercel.app", { waitUntil: "networkidle0" });
  await bekle(1500);
  await page.screenshot({ path: path.join(CIKTI, "site-giris.png") });

  // Serbest çizim: kedi
  await page.click('button[data-sekme="serbest"]');
  await bekle(1500);
  await ciz(page, "#tuval1", cizimAl("cat", 5));
  await bekle(1500);
  await page.screenshot({ path: path.join(CIKTI, "site-serbest.png") });

  // Oyun · 50: tur başlat, kelimeyi oku, o sınıftan bir test çizimini yarım çiz
  await page.click('button[data-sekme="oyun"][data-mod="kolay"]');
  await bekle(1500);
  await page.click("#basla");
  await page.waitForSelector("#oyunTur:not([hidden])", { timeout: 20000 });
  await bekle(1200);
  const kelime = (await page.$eval("#kelime", (e) => e.textContent)).trim();
  const sinif = SINIF.find((s) => kelime.toLowerCase().includes(s.tr.toLowerCase()));
  console.log("kelime:", kelime, "->", sinif && sinif.en);
  const vurus = cizimAl(sinif.en, 7);
  await ciz(page, "#tuval2", vurus, 0.35, 10);
  await bekle(700);
  await page.screenshot({ path: path.join(CIKTI, "site-oyun-yarim.png") });
  await ciz(page, "#tuval2", vurus.slice(0), 1, 4);
  await bekle(300);
  await page.screenshot({ path: path.join(CIKTI, "site-oyun-tanindi.png") });

  // Telefon görünümü
  const tel = await tarayici.newPage();
  await tel.setViewport({ width: 390, height: 844, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  await tel.goto("https://cizim-tanima.vercel.app", { waitUntil: "networkidle0" });
  await bekle(1500);
  await tel.screenshot({ path: path.join(CIKTI, "site-telefon.png") });
  await tarayici.close();
})().catch((h) => { console.error(h); process.exit(1); });
