import { ciz, type Vurus } from "./onisleme.ts";
import { KOLAY_OYUN_MODELI, MODELLER, OYUN_MODELI, esdegerGruplar, hizOlc, oturum, oyunKelimeleri, siniflar, tahminEt, type Sinif, type Tahmin } from "./model.ts";
import { SERI_PAS_CEZASI, SERI_PAS_HAKKI, SERI_SURESI_MS, TAHMIN_ARALIGI_MS, TANIMA_ESIGI, TANIMA_ESIGI_345, TUR_SAYISI, TUR_SURESI_MS, grupOlasiligi, kelimeSec, puan, tanindiMi } from "./oyun.ts";
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
const MODLAR: Record<Mod, { model: string; esik: number; aciklama: (kelime: number) => string }> = {
  zor: { model: OYUN_MODELI, esik: TANIMA_ESIGI_345, aciklama: (n) => `${n} kelime · yapay zekâ 345 nesne biliyor` },
  kolay: { model: KOLAY_OYUN_MODELI, esik: TANIMA_ESIGI, aciklama: (n) => `${n} kelime · yapay zekâ ${n} nesne biliyor (kolay)` },
};
let mod: Mod = "zor";
let oyunSiniflari: Sinif[] = [];
let oyunKelimeListesi: number[] = [];
let oyunGruplari: number[] = [];

/** Modun model, kelime listesi (zor: oyun_kelimeleri.json, kolay: 50 sınıfın hepsi) ve eşdeğer grupları. */
async function modYukle(m: Mod) {
  const s = await siniflar(MODLAR[m].model);
  const k = m === "zor" ? await oyunKelimeleri() : s.map((_, i) => i);
  return { s, k, g: await esdegerGruplar(MODLAR[m].model) };
}

// ---- sekmeler
for (const b of document.querySelectorAll<HTMLButtonElement>(".sekmeler button")) {
  b.addEventListener("click", () => {
    for (const d of document.querySelectorAll<HTMLButtonElement>(".sekmeler button")) d.classList.toggle("secili", d === b);
    for (const s of document.querySelectorAll<HTMLElement>(".sekme")) s.hidden = s.id !== b.dataset.sekme;
    if (b.dataset.sekme === "pratik") void pratikBaslat();
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

function tahminleriGoster(id: string, t: Tahmin, liste: Sinif[], hedef?: number, gruplar?: number[]) {
  $(id).innerHTML = t.sira.slice(0, 5).map ( (i) =>
    `<li${hedef !== undefined && gruplar && gruplar[i] === gruplar[hedef] ? ' class="hedef"' : ""}><span>${liste[i].tr}</span><span>${yuzde(t.olasilik[i])}</span>` +
    `<span class="cubuk"><i style="width:${(t.olasilik[i] * 100).toFixed(1)}%"></i></span></li>`).join("");
}

// ---- serbest çizim
let seciliModel = OYUN_MODELI;
const onizleme = $<HTMLCanvasElement>("onizleme").getContext("2d")!;

const tuval1 = new Tuval($<HTMLCanvasElement>("tuval1"), (bitti) => serbestTahmin(bitti));
function onizlemeCiz(ctx: CanvasRenderingContext2D, vuruslar: Vurus[]) {
  const resim = ctx.createImageData(28, 28);
  const p = ciz(vuruslar);
  p.forEach((v, i) => { resim.data.set([v, v, v, 255], i * 4); });
  ctx.putImageData(resim, 0, 0);
}
const serbestTahmin = tahminSirasi(async () => {
  onizlemeCiz(onizleme, tuval1.vuruslar);
  if (!tuval1.vuruslar.length) { $("tahminler").innerHTML = ""; return; }
  const model = seciliModel;
  const [t, liste] = await Promise.all([tahminEt(model, tuval1.vuruslar), siniflar(model)]);
  tahminleriGoster("tahminler", t, liste);
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

// ---- pratik: zor modun verileri oyun modundan bağımsız tutulur.
let pratikModel = OYUN_MODELI;
let pratikVeri: (Awaited<ReturnType<typeof modYukle>> & { model: string }) | undefined;
let pratikYuklemeKimligi = 0;
const pratikModelSec = $<HTMLSelectElement>("pratikModel");
pratikModelSec.innerHTML = MODELLER.map((m) => `<option ${m === pratikModel ? "selected" : ""}>${m}</option>`).join("");
let pratikHazir: Promise<void> | undefined;
let pratikHedef = -1;
const pratikOnizleme = $<HTMLCanvasElement>("pratikOnizleme").getContext("2d")!;
const ornekDugme = $<HTMLButtonElement>("ornekCiz");
let ornekler: Record<string, Vurus[][]> | undefined;
let ornekYukleme: Promise<Record<string, Vurus[][]>> | undefined;
let animasyonKimligi = 0;
const sonOrnekler = new Map<string, number>();
function ornekDugmesiniGuncelle() {
  const ad = pratikVeri?.s[pratikHedef]?.en;
  ornekDugme.disabled = !ad || (!!ornekler && !ornekler[ad]?.length);
}
function animasyonuDurdur() { animasyonKimligi++; }

const tuval3 = new Tuval($<HTMLCanvasElement>("tuval3"), (bitti) => pratikTahmin(bitti));
const pratikTahmin = tahminSirasi(async () => {
  onizlemeCiz(pratikOnizleme, tuval3.vuruslar);
  if (!tuval3.vuruslar.length) {
    $("pratikTahminler").innerHTML = "";
    $("pratikBildirim").hidden = true;
    return;
  }
  if (!pratikVeri || pratikVeri.model !== pratikModel || pratikHedef < 0) return;
  const silme = tuval3.silme, hedef = pratikHedef, veri = pratikVeri, model = pratikModel, kimlik = pratikYuklemeKimligi;
  try {
    const t = await tahminEt(model, tuval3.vuruslar);
    if (silme !== tuval3.silme || hedef !== pratikHedef || model !== pratikModel || kimlik !== pratikYuklemeKimligi) return;
    tahminleriGoster("pratikTahminler", t, veri.s, hedef, veri.g);
    const esik = model.startsWith("s345_") ? TANIMA_ESIGI_345 : TANIMA_ESIGI;
    $("pratikBildirim").hidden = !tanindiMi(t.sira, t.olasilik, hedef, esik, veri.g);
  } catch {
    if (model === pratikModel && kimlik === pratikYuklemeKimligi) $("pratikKelime").textContent = "Model yüklenemedi.";
  }
});
function pratikTemizle() {
  animasyonuDurdur();
  tuval3.temizle();
  onizlemeCiz(pratikOnizleme, []);
  $("pratikTahminler").innerHTML = "";
  $("pratikBildirim").hidden = true;
}
function pratikSonraki() {
  if (!pratikVeri) return;
  pratikTemizle();
  const adaylar = pratikVeri.k.filter((i) => i !== pratikHedef);
  const havuz = adaylar.length ? adaylar : pratikVeri.k;
  pratikHedef = havuz[kelimeSec(havuz.length, 1)[0]];
  $("pratikKelime").textContent = `${buyukHarf(pratikVeri.s[pratikHedef].tr)} ÇİZ`;
  ornekDugmesiniGuncelle();
}
function pratikBaslat(): Promise<void> {
  if (!pratikHazir) pratikHazir = pratikModelYukle();
  return pratikHazir;
}
async function pratikModelYukle(): Promise<void> {
  const model = pratikModel, kimlik = ++pratikYuklemeKimligi;
  const eskiAd = pratikVeri?.s[pratikHedef]?.en;
  $("pratikTahminler").innerHTML = "";
  $("pratikBildirim").hidden = true;
  try {
    const [s, g] = await Promise.all([siniflar(model), esdegerGruplar(model)]);
    const k = model.startsWith("s345_") ? await oyunKelimeleri() : s.map((_, i) => i);
    if (kimlik !== pratikYuklemeKimligi) return;
    pratikVeri = { s, k, g, model };
    const hedef = k.find((i) => s[i].en === eskiAd);
    if (hedef === undefined) {
      pratikHedef = -1;
      pratikSonraki();
    } else {
      pratikHedef = hedef;
      $("pratikKelime").textContent = `${buyukHarf(s[hedef].tr)} ÇİZ`;
      ornekDugmesiniGuncelle();
      pratikTahmin(true);
    }
    void oturum(model).catch(() => {});
  } catch {
    if (kimlik === pratikYuklemeKimligi) {
      $("pratikKelime").textContent = "Kelimeler yüklenemedi.";
      pratikHazir = undefined;
    }
  }
}
pratikModelSec.addEventListener("change", () => {
  pratikModel = pratikModelSec.value;
  pratikHazir = pratikModelYukle();
});
$<HTMLCanvasElement>("tuval3").addEventListener("pointerdown", animasyonuDurdur);
ornekDugme.addEventListener("click", async () => {
  pratikTemizle();
  const kimlik = animasyonKimligi, hedef = pratikHedef;
  const ad = pratikVeri?.s[hedef]?.en;
  if (!ad) return;
  try {
    ornekYukleme ??= fetch(`${import.meta.env.BASE_URL}model/ornekler.json`).then((r) => {
      if (!r.ok) throw new Error("Örnekler yüklenemedi");
      return r.json() as Promise<Record<string, Vurus[][]>>;
    });
    ornekler = await ornekYukleme;
    ornekDugmesiniGuncelle();
    if (kimlik !== animasyonKimligi || hedef !== pratikHedef) return;
    const liste = ornekler[ad];
    if (!liste?.length) return;
    const onceki = sonOrnekler.get(ad);
    const adaylar = liste.map((_, i) => i).filter((i) => liste.length === 1 || i !== onceki);
    const secim = adaylar[Math.floor(Math.random() * adaylar.length)];
    sonOrnekler.set(ad, secim);
    const kaynak = liste[secim].filter(([xs, ys]) => xs.length && xs.length === ys.length);
    const xs = kaynak.flatMap((v) => v[0]), ys = kaynak.flatMap((v) => v[1]);
    if (!xs.length) return;
    const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
    const r = $<HTMLCanvasElement>("tuval3").getBoundingClientRect();
    const olcek = Math.min(r.width * .8 / (maxX - minX || 1), r.height * .8 / (maxY - minY || 1));
    const ox = (r.width - (maxX - minX) * olcek) / 2, oy = (r.height - (maxY - minY) * olcek) / 2;
    const noktalar = kaynak.flatMap(([vx, vy], v) => vx.map((x, i) => ({ v, x: ox + (x - minX) * olcek, y: oy + (vy[i] - minY) * olcek })));
    let eklenen = 0;
    const baslangic = performance.now();
    const kare = (simdi: number) => {
      if (kimlik !== animasyonKimligi) return;
      const sayi = Math.min(noktalar.length, Math.max  (1, Math.ceil(noktalar.length * (simdi - baslangic) / 1250)));
      while (eklenen < sayi) {
        const n = noktalar[eklenen++];
        if (!tuval3.vuruslar[n.v]) tuval3.vuruslar.push([[], []]);
        const v = tuval3.vuruslar[n.v];
        v[0].push(n.x); v[1].push(n.y);
      }
      tuval3.yeniden();
      pratikTahmin(sayi === noktalar.length);
      if (sayi < noktalar.length) requestAnimationFrame(kare);
    };
    requestAnimationFrame(kare);
  } catch {
    ornekYukleme = undefined;
    if (kimlik === animasyonKimligi) ornekDugme.title = "Örnekler yüklenemedi; yeniden deneyin.";
  }
});
$("temizle3").addEventListener("click", pratikTemizle);
$("geri3").addEventListener("click", () => { animasyonuDurdur(); tuval3.geriAl(); pratikTahmin(true); });
$("sonraki").addEventListener("click", pratikSonraki);

// ---- oyun
// "tur": 5 tur × 20 sn, erken tanınan çok puan; "seri": 60 sn'de art arda kaç kelime, 3 ücretsiz pas, sonrası puan düşürür
type Bicim = "tur" | "seri";
const BICIM_ACIKLAMA: Record<Bicim, string> = {
  tur: "5 tur, her turda 20 saniye. Ekrandaki nesneyi çiz; yapay zekâ çizimini tanıdığı anda puanı alırsın. Ne kadar erken tanınırsan o kadar çok puan.",
  seri: `${SERI_SURESI_MS / 1000} saniyede art arda kaç nesne tanıtabilirsin? Tanınan her nesne 1 puan, tanınınca hemen yeni nesne gelir. ${SERI_PAS_HAKKI} pas ücretsiz, sonraki her pas ${SERI_PAS_CEZASI} puan düşürür; süre pas geçerken de akar.`,
};
let bicim: Bicim = "tur";
type TurSonucu = { hedef: number; taninan: boolean; ms: number; puan: number; pas?: boolean; yarim?: boolean };
const tuval2 = new Tuval($<HTMLCanvasElement>("tuval2"), (bitti) => oyunTahmin(bitti));
let kelimeler: number[] = [];
let tur = 0, toplam = 0, turBasi = 0, turAcik = false, turKimligi = 0;
let sonuclar: TurSonucu[] = [];
let sonTahmin = -1;
let seriBasi = 0, seriAcik = false, pasKalan = 0;

const oyunTahmin = tahminSirasi(async () => {
  if (!turAcik || !tuval2.vuruslar.length) return;
  const kimlik = turKimligi, silme = tuval2.silme;
  const t = await tahminEt(MODLAR[mod].model, tuval2.vuruslar);
  // tahmin sürerken tur değiştiyse ya da çizim silindiyse sonuç eskidir
  if (!turAcik || kimlik !== turKimligi || silme !== tuval2.silme) return;
  const hedef = kelimeler[tur];
  sonTahmin = t.sira[0];
  if (tanindiMi(t.sira, t.olasilik, hedef, MODLAR[mod].esik, oyunGruplari)) {
    $("canliTahmin").innerHTML = `Yapay zekâ: Bu bir ${oyunSiniflari[hedef].tr}! <small>${yuzde(grupOlasiligi(t.olasilik, hedef, oyunGruplari))}</small>`;
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
  $("turNo").textContent = bicim === "seri" ? (pasKalan ? `${pasKalan} pas` : `pas −${SERI_PAS_CEZASI}`) : `Tur ${tur + 1}/${TUR_SAYISI}`;
  $("kelime").textContent = buyukHarf(oyunSiniflari[kelimeler[tur]].tr);
  $("canliTahmin").textContent = "Çizmeye başla…";
  turBasi = performance.now();
  turAcik = true;
  if (bicim === "tur") requestAnimationFrame(sayac);
}

function sayac() {
  if (bicim === "seri") return seriSayac();
  if (!turAcik) return;
  const gecen = performance.now() - turBasi;
  const kalan = Math.max(0, 1 - gecen / TUR_SURESI_MS);
  $("sureDolgu").style.transform = `scaleX(${kalan})`;
  $("sureDolgu").parentElement!.classList.toggle("az", kalan < 0.25);
  if (gecen >= TUR_SURESI_MS) return turBitir(false);
  requestAnimationFrame(sayac);
}

/** Seride süre maç boyunca akar (tanınma bildirimi ve pas sırasında da). */
function seriSayac() {
  if (!seriAcik) return;
  const gecen = performance.now() - seriBasi;
  const kalan = Math.max(0, 1 - gecen / SERI_SURESI_MS);
  $("sureDolgu").style.transform = `scaleX(${kalan})`;
  $("sureDolgu").parentElement!.classList.toggle("az", kalan < 0.25);
  if (gecen >= SERI_SURESI_MS) return seriBitir();
  requestAnimationFrame(seriSayac);
}

function seriBitir() {
  seriAcik = false;
  if (turAcik) {
    turAcik = false;
    tuval2.kilitli = true;
    sonuclar.push({ hedef: kelimeler[tur], taninan: false, ms: performance.now() - turBasi, puan: 0, yarim: true });
  }
  turKimligi++; // bekleyen bildirim zamanlayıcısı yeni kelime açmasın
  macBitir();
}

/** Seride tanınan ya da pas: kısa bildirimden sonra hemen yeni kelime, süre durmaz. */
function seriTurBitir(taninan: boolean) {
  if (!turAcik) return;
  const ceza = !taninan && pasKalan === 0;
  if (!taninan && !ceza) pasKalan--;
  turAcik = false;
  tuval2.kilitli = true;
  const ms = performance.now() - turBasi;
  const p = taninan ? 1 : ceza ? -SERI_PAS_CEZASI : 0;
  sonuclar.push({ hedef: kelimeler[tur], taninan, ms, puan: p, pas: !taninan });
  toplam += p;
  $("puan").textContent = `${toplam} puan`;
  const b = $("bildirim");
  b.classList.toggle("olmadi", !taninan);
  b.innerHTML = taninan ? `Tanındı! <small>${(ms / 1000).toFixed(1)} sn · +1</small>`
    : ceza ? `Pas <small>−${SERI_PAS_CEZASI} puan</small>` : `Pas <small>${pasKalan} ücretsiz hak kaldı</small>`;
  b.hidden = false;
  if ($<HTMLInputElement>("oyunKaydet").checked && tuval2.vuruslar.length) {
    void kaydet({ etiket: oyunSiniflari[kelimeler[tur]].en, mod: "seri", taninan, sure_ms: Math.round(ms), vuruslar: tuval2.vuruslar, aygit: tuval2.aygit });
  }
  const kimlik = turKimligi;
  setTimeout(() => {
    if (kimlik !== turKimligi || !seriAcik) return;
    tur = (tur + 1) % kelimeler.length;
    turBasla();
  }, taninan ? 700 : 300);
}

function turBitir(taninan: boolean) {
  if (bicim === "seri") return seriTurBitir(taninan);
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
  if (bicim === "seri") {
    const taninanSayi = sonuclar.filter((s) => s.taninan).length;
    $("sonBaslik").textContent = toplam >= 10 ? "Harika seri!" : taninanSayi ? "Süre bitti" : "Bir dahakine!";
    $("sonPuan").innerHTML = `${toplam} puan <small>${taninanSayi} nesne tanıttın</small>`;
    $("sonListe").innerHTML = sonuclar.map((s) =>
      `<li class="${s.taninan ? "tamam" : ""}"><span>${oyunSiniflari[s.hedef].tr}</span>` +
      `<span>${s.taninan ? `✓ ${(s.ms / 1000).toFixed(1)} sn` : s.pas ? (s.puan < 0 ? `pas ${s.puan}` : "pas") : "süre bitti"}</span></li>`).join("");
    return;
  }
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
  const m = mod;
  try {
    await modHazir;
    await oturum(MODLAR[m].model);
  } catch (e) {
    $("yukleniyor").textContent = `Model yüklenemedi: ${e}`;
    b.disabled = false;
    return;
  }
  $("yukleniyor").textContent = "";
  b.disabled = false;
  if (m !== mod) return; // yüklenirken sekme değişti
  const seri = bicim === "seri";
  kelimeler = kelimeSec(oyunKelimeListesi.length, seri ? oyunKelimeListesi.length : TUR_SAYISI).map((i) => oyunKelimeListesi[i]);
  tur = 0; toplam = 0; sonuclar = [];
  pasKalan = SERI_PAS_HAKKI;
  $("puan").textContent = "0 puan";
  ekran("oyunTur");
  turBasla();
  if (seri) {
    seriBasi = performance.now();
    seriAcik = true;
    requestAnimationFrame(seriSayac);
  }
}

$("basla").addEventListener("click", macBasla);
for (const b of document.querySelectorAll<HTMLButtonElement>(".bicimler button")) {
  b.addEventListener("click", () => {
    bicim = b.dataset.bicim as Bicim;
    for (const d of document.querySelectorAll<HTMLButtonElement>(".bicimler button")) d.classList.toggle("secili", d === b);
    $("bicimAciklama").textContent = BICIM_ACIKLAMA[bicim];
  });
}
$("bicimAciklama").textContent = BICIM_ACIKLAMA[bicim];
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
  seriAcik = false;
  turKimligi++;
  tuval2.kilitli = true;
  mod = m;
  ekran("oyunGiris");
  $("modAciklama").textContent = "";
  modHazir = modYukle(m).then(({ s, k, g }) => {
    if (mod !== m) return;
    oyunSiniflari = s;
    oyunKelimeListesi = k;
    oyunGruplari = g;
    $("modAciklama").textContent = MODLAR[m].aciklama(k.length);
    void oturum(MODLAR[m].model).catch(() => {});
  });
}

// ---- açılış
modDegistir(mod);
// sekme adında kelime sayısı (liste egitim/oyun_kelimeleri.py ile değişebilir)
void oyunKelimeleri().then((k) => { document.querySelector<HTMLButtonElement>("button[data-mod=zor]")!.textContent = `Oyun · ${k.length}`; });
siniflar(OYUN_MODELI).then((s) => {
  SINIFLAR = s;
  const sirali = s.map((c, i) => [c.tr, i] as const).sort((a, b) => a[0].localeCompare(b[0], "tr"));
  $<HTMLSelectElement>("etiket").innerHTML = `<option value="">seç…</option>` +
    sirali.map(([tr, i]) => `<option value="${i}">${tr}</option>`).join("");
});
