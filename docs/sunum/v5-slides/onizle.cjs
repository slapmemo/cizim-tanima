// Desteyi yerelde işler: her slaytı 1920×1080'de çizer, taşmaları raporlar, küçük görüntüler alır.
const fs = require("fs");
const path = require("path");
const puppeteer = require("C:/Users/slapm/OneDrive/Desktop/FinalCepKonsol/cizim-tanima/docs/sunum/node_modules/puppeteer-core");
const S = "C:/Users/slapm/AppData/Local/Temp/claude/969f34f2dbdc9e64/20368ee8-404f-494b-a890-e73d31035f5d/scratchpad";
const D = S + "/deste/project";
const G = S + "/deste_gorsel";
const BLOB = {
  "2710aa6e83455590a64c515577f78b47": "veri-seti.png", "cfc58a7d746d5b16b887a71a60d2a9e6": "ornek-ndjson.png",
  "7372b4c2b67a67eaf62bbc58ca5c9287": "ornek-json-cizim-28.png", "02cad060bb181b25798f2ff07ebb9522": "onisleme-hepsi.png",
  "b8e34d137ec652b52164becda80efabf": "rdp.png", "992c2272bb099ad31d6be9cdd43d26d5": "onisleme-4-piksel.png",
  "65f0e70a7b1eb1bb809acbc018a7d3ec": "kavram-evrisim.png", "b7b3ef8af36f465346425ece33759bf0": "kavram-havuzlama.png",
  "38d4f63d53b69a4717b1234b9fe81faa": "kavram-batchnorm-dropout.png", "b82f7481aeca722199fce3aaa3b201df": "kavram-artik.png",
  "cddb04f831fc93eda20eda769e225f12": "mimari-m1.png", "ddf146dc4d959bae294c774b6f9d5daa": "mimari-m2.png",
  "447df5d319c583ca7614ead8c3fa81ef": "mimari-m3.png", "970e1b9247fc8c57e867fda33441cdf8": "m3-kismi-veri.png",
  "d59b717cd4d82b392f3011c4285318ec": "iki-model-cat-k.png", "24126097d67a6f883328223320d949de": "iki-model-bicycle-k.png",
  "cf4b84ab942432c3694d4022faadc686": "site-giris.png", "a996f6ccb35608540e2ff77ceecf3e4e": "site-oyun-tanindi.png",
  "cb07fdc03d615bf79d38655045baede4": "site-serbest.png", "d0aec1ac3c4f0f3a8249901b31a58406": "kullanici-dogru.png", "eb916b4ecb20e12059a664feb5a74e95": "kullanici-yanlis.png", "9f3c04b37d4abf5a56caa5e4694553d4": "batchnorm-buyuk.png", "f0f61615cc51a33b965aada0aaf17987": "qr-site.png", "ca63becb247c66fcac924966eef2d5e0": "topla-giris.png", "0d4a80b872bb822fe94c4435225bfc2c": "topla-cizim.png", "e3c14c01bb37c9155d7cfcc1f3b3e3c0": "onisleme-1-kutu.png", "fcecb6c1ff6c67535c9d4e9bb010c4d3": "onisleme-3-ortala.png", "b765a44ee877396aabdf50c562b885e0": "dropout.svg",
};
const deck = JSON.parse(fs.readFileSync(D + "/deck.json", "utf8"));
let css = fs.readFileSync(D + "/deck.css", "utf8");
let govde = "";
for (const id of deck.order) {
  let h = fs.readFileSync(`${D}/slides/${id}.html`, "utf8");
  h = h.replace(/\/_blob\/([0-9a-f]{32})/g, (_, b) => "file:///" + G + "/" + BLOB[b]);
  h = h.replace(/<aside>[\s\S]*?<\/aside>/, "");
  govde += h;
}
const sayfa = `<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="${Object.values(deck.faces)[0].href}">
<style>*{margin:0;box-sizing:content-box} ${css}
section{width:1920px;height:1080px;box-sizing:border-box;overflow:hidden;position:relative}
x-shape{display:block} x-shape[kind="arrow-right"]{clip-path:polygon(0 30%,60% 30%,60% 0,100% 50%,60% 100%,60% 70%,0 70%)}
.giris{animation:none!important}</style></head><body>${govde}</body></html>`;
fs.writeFileSync(__dirname + "/deste.html", sayfa);
(async () => {
  const t = await puppeteer.launch({ executablePath: "C:/Users/slapm/AppData/Local/ms-playwright/chromium-1248/chrome-win64/chrome.exe", args: ["--allow-file-access-from-files"] });
  const p = await t.newPage();
  await p.setViewport({ width: 1920, height: 1080 });
  await p.goto("file:///" + __dirname.replace(/\\/g, "/") + "/deste.html", { waitUntil: "networkidle0" });
  await p.evaluate(() => document.fonts.ready);
  const rapor = await p.evaluate(() => [...document.querySelectorAll("section")].map((s) => {
    const r = s.getBoundingClientRect();
    let enAlt = 0, enSag = 0, tasan = [];
    s.querySelectorAll("*").forEach((e) => {
      if (e.tagName === "ASIDE") return;
      const b = e.getBoundingClientRect();
      if (!b.width) return;
      enAlt = Math.max(enAlt, b.bottom - r.top); enSag = Math.max(enSag, b.right - r.left);
      if (e.scrollWidth > e.clientWidth + 2 && ["P", "H2", "H3", "TD", "TH", "LI"].includes(e.tagName)) tasan.push(e.textContent.slice(0, 30));
    });
    return { id: s.id, enAlt: Math.round(enAlt), enSag: Math.round(enSag), tasan };
  }));
  for (const r of rapor) console.log(r.id.padEnd(12), "alt", r.enAlt, "sağ", r.enSag, r.enAlt > 976 || r.enSag > 1800 ? "  <<< SINIR" : "", r.tasan.length ? " taşan: " + r.tasan.join(" | ") : "");
  const bolumler = await p.$$("section");
  for (let i = 0; i < bolumler.length; i++) {
    await bolumler[i].screenshot({ path: path.join(__dirname, `s${String(i + 1).padStart(2, "0")}.png`) });
  }
  await t.close();
})();
