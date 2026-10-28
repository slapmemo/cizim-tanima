import { ciz } from "./onisleme.ts";
import { KOLAY_OYUN_MODELI, MODELLER, OYUN_MODELI, hizOlc, oturum, oyunKelimeleri, siniflar, tahminEt, type Sinif } from "./model.ts";
import { TAHMIN_ARALIGI_MS, TUR_SAYISI, TUR_SURESI_MS, kelimeSec, puan, tanindiMi } from "./oyun.ts";
import { Tuval } from "./tuval.ts";

const $ = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
const yuzde = (p: number) => `%${Math.round(p * 100)}`;
const buyukHarf = (s: string) => s.toLocaleUpperCase("tr");

/** Soru eki, son ünlüye göre (büyük ünlü uyumu): elma mı, kedi mi, kuş mu, göz mü. */
function mi(sozcuk: string): string {
  const unlu = [...sozcuk.toLocaleLowerCase("tr")].reverse().find((h) => "aıoueiöü".includes(h));
  const ek = unlu === "a" || unlu === "ı" ? "mı" : unlu === "o" || unlu === "u" ? "mu" : unlu === "ö" || unlu === "ü" ? "mü" : "mi";
  return `${sozcuk} ${ek}`;
}

// OYUN_MODELI'nin sınıfları (345; serbest çizimde "ne çizdin" listesi); serbest çizim seçili modelin listesini kullanır
let SINIFLAR: Sinif[] = [];

// İki oyun sekmesi aynı ekranı kullanır; mod yalnız modeli ve sorulan kelimeleri belirler
type Mod = "zor" | "kolay";
const MODLAR: Record<Mod, { model: string; aciklama: string }> = {
  zor: { model: OYUN_MODELI, aciklama: "242 kelime · yapay zekâ 345 nesne biliyor" },
  kolay: { model: KOLAY_OYUN_MODELI, aciklama: "50 kelime · yapay zekâ 50 nesne biliyor (kolay)" },
};
let mod: Mod = "zor";
let oyunSiniflari: Sinif[] = [];
let oyunKelimeListesi: number[] = [];

/** Modun model ve kelime listesi (zor: oyun_kelimeleri.json, kolay: 50 sınıfın hepsi). */
async function modYukle(m: Mod) {
  const s = await siniflar(MODLAR[m].model);
  return { s, k: m === "zor" ? await oyunKelimeleri() : s.map((_, i) => i) };
}

// ---- sekmeler
for (const b of document.querySelectorAll<HTMLButtonElement>(".sekmeler button")) {
  b.addEventListener("click", () => {
    for (const d of document.querySelectorAll<HTMLButtonElement>(".sekmeler button")) d.classList.toggle("secili", d === b);
    for (const s of document.querySelectorAll<HTMLElement>(".sekme")) s.hidden = s.id !== b.dataset.sekme;
    if (b.dataset.mod && b.dataset.mod !== mod) modDegistir(b.dataset.mod as Mod);
  });
}

// ---- kayıt (yalnız Vite geliştirme/önizleme sunucusunda çalışır)
async function kaydet(kayit: Record<string, unknown>): Promise<boolean> {
  try {
    const y = await fetch("/api/kaydet", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ ...kayit, tarayici: navigator.userAgent, zaman: new Date().toISOString() }),
    });
    return y.ok;
  } catch {
    return false;
  }
}

/** Aynı anda tek tahmin çalışsın; çalışırken gelen istek bitince bir kez daha çalışır. */
function tahminSirasi(calistir: () => Promise<void>) {
  let mesgul = false, bekleyen = false, son = 0;
  const dene = async () => {
    if (mesgul) { bekleyen = true; return; }
    mesgul = true;
    son = performance.now();
    try { await calistir(); } finally {
      mesgul = false;
      if (bekleyen) { bekleyen = false; void dene(); }
    }
  };
  return (bitti: boolean) => {
    if (bitti || performance.now() - son >= TAHMIN_ARALIGI_MS) void dene();
  };
}

// ---- serbest çizim
let seciliModel = OYUN_MODELI;
const onizleme = $<HTMLCanvasElement>("onizleme").getContext("2d")!;

const tuval1 = new Tuval($<HTMLCanvasElement>("tuval1"), (bitti) => serbestTahmin(bitti));
const serbestTahmin = tahminSirasi(async () => {
  const resim = onizleme.createImageData(28, 28);
  const p = ciz(tuval1.vuruslar);
  p.forEach((v, i) => { resim.data.set([v, v, v, 255], i * 4); });
  onizleme.putImageData(resim, 0, 0);
  if (!tuval1.vuruslar.length) { $("tahminler").innerHTML = ""; return; }
  const model = seciliModel;
  const [t, liste] = await Promise.all([tahminEt(model, tuval1.vuruslar), siniflar(model)]);
  $("tahminler").innerHTML = t.sira.slice(0, 5).map((i) =>
    `<li><span>${liste[i].tr}</span><span>${yuzde(t.olasilik[i])}</span>` +
    `<span class="cubuk"><i style="width:${(t.olasilik[i] * 100).toFixed(1)}%"></i></span></li>`).join("");
  $("sure1").textContent = `Ön işleme + tahmin: ${t.ms.toFixed(1)} ms`;
});
const serbestTemizle = () => {
  tuval1.temizle();
  serbestTahmin(true);
  $<HTMLSelectElement>("etiket").value = "";
  $("kayitDurum").textContent = "";
};
$("temizle1").addEventListener("click", serbestTemizle);
$("geri1").addEventListener("click", () => { tuval1.geriAl(); serbestTahmin(true); });

const modelSec = $<HTMLSelectElement>("modelSec");
modelSec.innerHTML = MODELLER.map((m) => `<option ${m === seciliModel ? "selected" : ""}>${m}</option>`).join("");
modelSec.addEventListener("change", () => { seciliModel = modelSec.value; serbestTahmin(true); });

$("hizTesti").addEventListener("click", async () => {
  const b = $<HTMLButtonElement>("hizTesti");
  b.disabled = true;
  const sonuc: string[] = [];
  for (const m of MODELLER) {
    $("hizSonuc").textContent = `${m} ölçülüyor…`;
    sonuc.push(`${m}: ${(await hizOlc(m)).toFixed(2)} ms`);
  }
  $("hizSonuc").textContent = `Tek tahmin (200 tekrar ortalaması): ${sonuc.join(" · ")}`;
  console.log("[hiz]", sonuc.join(" | "));
  b.disabled = false;
});

let kayitSayisi = 0;
$("kaydet").addEventListener("click", async () => {
  const etiket = $<HTMLSelectElement>("etiket").value;
  if (!tuval1.vuruslar.length) { $("kayitDurum").textContent = "Önce bir şey çiz."; return; }
  if (!etiket) { $("kayitDurum").textContent = "Ne çizdiğini seç."; return; }
  const ok = await kaydet({ etiket: SINIFLAR[+etiket].en, mod: "serbest", taninan: null, vuruslar: tuval1.vuruslar, aygit: tuval1.aygit });
  if (ok) {
    kayitSayisi++;
    serbestTemizle();
    $("kayitDurum").textContent = `Kaydedildi ✓ (bu oturumda ${kayitSayisi})`;
  } else {
    $("kayitDurum").textContent = "Kaydedilemedi: sayfa `npm run dev` ile açılmalı.";
  }
});

// ---- oyun
type TurSonucu = { hedef: number; taninan: boolean; ms: number; puan: number };
const tuval2 = new Tuval($<HTMLCanvasElement>("tuval2"), (bitti) => oyunTahmin(bitti));
let kelimeler: number[] = [];
let tur = 0, toplam = 0, turBasi = 0, turAcik = false, turKimligi = 0;
let sonuclar: TurSonucu[] = [];
let sonTahmin = -1;

const oyunTahmin = tahminSirasi(async () => {
  if (!turAcik || !tuval2.vuruslar.length) return;
  const kimlik = turKimligi;
  const t = await tahminEt(MODLAR[mod].model, tuval2.vuruslar);
  if (!turAcik || kimlik !== turKimligi) return;
  const hedef = kelimeler[tur];
  sonTahmin = t.sira[0];
  if (tanindiMi(t.sira, t.olasilik, hedef)) {
    $("canliTahmin").innerHTML = `Yapay zekâ: Bu bir ${oyunSiniflari[hedef].tr}! <small>${yuzde(t.olasilik[hedef])}</small>`;
    return turBitir(true);
  }
  const ilk = oyunSiniflari[t.sira[0]].tr, ikinci = oyunSiniflari[t.sira[1]].tr;
  $("canliTahmin").innerHTML = `Yapay zekâ: ${mi(ilk)}? <small>${yuzde(t.olasilik[t.sira[0]])} · yoksa ${mi(ikinci)}?</small>`;
});

function ekran(ad: "oyunGiris" | "oyunTur" | "oyunSon") {
  for (const id of ["oyunGiris", "oyunTur", "oyunSon"]) $(id).hidden = id !== ad;
}

function turBasla() {
  turKimligi++;
  tuval2.temizle();
  tuval2.kilitli = false;
  sonTahmin = -1;
  $("bildirim").hidden = true;
  $("turNo").textContent = `Tur ${tur + 1}/${TUR_SAYISI}`;
  $("kelime").textContent = buyukHarf(oyunSiniflari[kelimeler[tur]].tr);
  $("canliTahmin").textContent = "Çizmeye başla…";
  turBasi = performance.now();
  turAcik = true;
  requestAnimationFrame(sayac);
}

function sayac() {
  if (!turAcik) return;
  const gecen = performance.now() - turBasi;
  const kalan = Math.max(0, 1 - gecen / TUR_SURESI_MS);
  $("sureDolgu").style.transform = `scaleX(${kalan})`;
  $("sureDolgu").parentElement!.classList.toggle("az", kalan < 0.25);
  if (gecen >= TUR_SURESI_MS) return turBitir(false);
  requestAnimationFrame(sayac);
}

function turBitir(taninan: boolean) {
  if (!turAcik) return;
  turAcik = false;
  tuval2.kilitli = true;
  const ms = performance.now() - turBasi;
  const p = taninan ? puan(ms) : 0;
  const hedef = kelimeler[tur];
  toplam += p;
  sonuclar.push({ hedef, taninan, ms, puan: p });
  $("puan").textContent = `${toplam} puan`;
  const b = $("bildirim");
  b.classList.toggle("olmadi", !taninan);
  b.innerHTML = taninan
    ? `Tanındı! <small>${(ms / 1000).toFixed(1)} sn · +${p} puan</small>`
    : `Süre doldu <small>${sonTahmin >= 0 ? `Yapay zekâ en son “${oyunSiniflari[sonTahmin].tr}” dedi` : "Çizim yoktu"}</small>`;
  b.hidden = false;
  if ($<HTMLInputElement>("oyunKaydet").checked && tuval2.vuruslar.length) {
    void kaydet({ etiket: oyunSiniflari[hedef].en, mod: "oyun", taninan, sure_ms: Math.round(ms), vuruslar: tuval2.vuruslar, aygit: tuval2.aygit });
  }
  const kimlik = turKimligi;
  setTimeout(() => {
    if (kimlik !== turKimligi) return; // bu arada mod değişti
    tur++;
    if (tur < TUR_SAYISI) turBasla(); else macBitir();
  }, taninan ? 1600 : 2000);
}

function macBitir() {
  ekran("oyunSon");
  const taninanSayi = sonuclar.filter((s) => s.taninan).length;
  $("sonBaslik").textContent = taninanSayi === TUR_SAYISI ? "Kusursuz!" : taninanSayi ? "Maç bitti" : "Bir dahakine!";
  $("sonPuan").textContent = `${toplam} puan`;
  $("sonListe").innerHTML = sonuclar.map((s) =>
    `<li class="${s.taninan ? "tamam" : ""}"><span>${oyunSiniflari[s.hedef].tr}</span>` +
    `<span>${s.taninan ? `✓ ${(s.ms / 1000).toFixed(1)} sn · ${s.puan}` : "✗ tanınmadı"}</span></li>`).join("");
}

async function macBasla() {
  const b = $<HTMLButtonElement>("basla");
  b.disabled = true;
  $("yukleniyor").textContent = "Model yükleniyor…";
  try {
    await modHazir;
    await oturum(MODLAR[mod].model);
  } catch (e) {
    $("yukleniyor").textContent = `Model yüklenemedi: ${e}`;
    b.disabled = false;
    return;
  }
  $("yukleniyor").textContent = "";
  b.disabled = false;
  kelimeler = kelimeSec(oyunKelimeListesi.length, TUR_SAYISI).map((i) => oyunKelimeListesi[i]);
  tur = 0; toplam = 0; sonuclar = [];
  $("puan").textContent = "0 puan";
  ekran("oyunTur");
  turBasla();
}

$("basla").addEventListener("click", macBasla);
$("tekrar").addEventListener("click", macBasla);
$("temizle2").addEventListener("click", () => { if (turAcik) { tuval2.temizle(); $("canliTahmin").textContent = "Çizmeye başla…"; } });
$("geri2").addEventListener("click", () => { if (turAcik) { tuval2.geriAl(); oyunTahmin(true); } });
$("pas").addEventListener("click", () => turBitir(false));

// Kayıt ara katmanı yalnız yerel Vite sunucusunda var; yayımlanan sitede kayıt arayüzü gizlenir
// (orada çizim toplama topla.html ile yapılır).
if (!import.meta.env.DEV) {
  for (const id of ["kaydet", "etiket", "kayitDurum"]) $(id).closest(".satir, div")!.setAttribute("hidden", "");
  $("oyunKaydet").closest("label")!.setAttribute("hidden", "");
  document.querySelector("#serbest h3")?.setAttribute("hidden", "");
}

let modHazir: Promise<void> = Promise.resolve();

/** Sekme değişince süren maç bırakılır, seçilen modun listeleri ve modeli yüklenir. */
function modDegistir(m: Mod) {
  turAcik = false;
  turKimligi++;
  tuval2.kilitli = true;
  mod = m;
  ekran("oyunGiris");
  $("modAciklama").textContent = MODLAR[m].aciklama;
  modHazir = modYukle(m).then(({ s, k }) => {
    if (mod !== m) return;
    oyunSiniflari = s;
    oyunKelimeListesi = k;
    void oturum(MODLAR[m].model).catch(() => {});
  });
}

// ---- açılış
modDegistir(mod);
siniflar(OYUN_MODELI).then((s) => {
  SINIFLAR = s;
  const sirali = s.map((c, i) => [c.tr, i] as const).sort((a, b) => a[0].localeCompare(b[0], "tr"));
  $<HTMLSelectElement>("etiket").innerHTML = `<option value="">seç…</option>` +
    sirali.map(([tr, i]) => `<option value="${i}">${tr}</option>`).join("");
});
