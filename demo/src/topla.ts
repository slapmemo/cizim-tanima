// Gerçek kullanıcı çizimlerini toplar: 50 nesne rastgele sırada, tahmin gizli, ilerleme
// tarayıcıda saklanır, sonda tek JSON dosyası (paylaş ya da indir). Ölçüm:
// egitim/gercek_degerlendir.py (dosyalar kayitlar/ altına konur).
import type { Vurus } from "./onisleme.ts";
import { OYUN_MODELI, siniflar, tahminEt, type Sinif } from "./model.ts";
import { kelimeSec } from "./oyun.ts";
import { Tuval } from "./tuval.ts";

const $ = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
const ANAHTAR = "cizim-topla-v1";

type Kayit = { etiket: string; vuruslar: Vurus[]; aygit: string; sure_ms: number; zaman: string };
type Durum = {
  surum: 1;
  oturum: string;
  takma_ad: string;
  sira: number[];
  indeks: number;
  atlanan: string[];
  kayitlar: Kayit[];
  baslangic: string;
};

let SINIFLAR: Sinif[] = [];
let durum: Durum | null = null;
let cizimBasi = 0;

function oku(): Durum | null {
  try {
    const d = JSON.parse(localStorage.getItem(ANAHTAR) ?? "null");
    return d && d.surum === 1 ? d : null;
  } catch {
    return null;
  }
}
function yaz() {
  try { localStorage.setItem(ANAHTAR, JSON.stringify(durum)); } catch { /* gizli pencere: bellekte sürer */ }
}

const tuval = new Tuval($<HTMLCanvasElement>("tuval"), () => {
  if (!cizimBasi) cizimBasi = performance.now();
});

function ekran(ad: "giris" | "cizim" | "son") {
  for (const id of ["giris", "cizim", "son"]) $(id).hidden = id !== ad;
  $("ilerlemeHap").hidden = ad !== "cizim";
}

function goster() {
  const d = durum!;
  if (d.indeks >= d.sira.length) return bitir();
  const toplam = d.sira.length;
  $("sayac").textContent = `${d.indeks + 1}/${toplam}`;
  $("kelime").textContent = SINIFLAR[d.sira[d.indeks]].tr.toLocaleUpperCase("tr");
  $("ilerleme").style.transform = `scaleX(${d.indeks / toplam})`;
  $("ilerlemeHap").textContent = `${d.kayitlar.length} çizim`;
  tuval.temizle();
  tuval.kilitli = false;
  cizimBasi = 0;
  ekran("cizim");
}

function ilerle() {
  durum!.indeks++;
  yaz();
  goster();
}

$("kaydet").addEventListener("click", () => {
  if (!tuval.vuruslar.length) return;
  const d = durum!;
  d.kayitlar.push({
    etiket: SINIFLAR[d.sira[d.indeks]].en,
    vuruslar: tuval.vuruslar,
    aygit: tuval.aygit,
    sure_ms: cizimBasi ? Math.round(performance.now() - cizimBasi) : 0,
    zaman: new Date().toISOString(),
  });
  ilerle();
});
$("atla").addEventListener("click", () => {
  durum!.atlanan.push(SINIFLAR[durum!.sira[durum!.indeks]].en);
  ilerle();
});
$("temizle").addEventListener("click", () => { tuval.temizle(); cizimBasi = 0; });
$("geri").addEventListener("click", () => tuval.geriAl());
$("bitir").addEventListener("click", () => bitir());
$("devam").addEventListener("click", () => goster());

const takmaAd = $<HTMLInputElement>("takmaAd");
const onay = $<HTMLInputElement>("onay");
const baslaKontrol = () => { $<HTMLButtonElement>("basla").disabled = !(takmaAd.value.trim() && onay.checked); };
takmaAd.addEventListener("input", baslaKontrol);
onay.addEventListener("change", baslaKontrol);
$("basla").addEventListener("click", () => {
  durum = {
    surum: 1,
    oturum: crypto.randomUUID?.() ?? String(Math.random()).slice(2),
    takma_ad: takmaAd.value.trim().slice(0, 24),
    sira: kelimeSec(SINIFLAR.length, SINIFLAR.length),
    indeks: 0,
    atlanan: [],
    kayitlar: [],
    baslangic: new Date().toISOString(),
  };
  yaz();
  goster();
});

function dosya(): File {
  const d = durum!;
  const icerik = { ...d, bitis: new Date().toISOString(), tarayici: navigator.userAgent, ekran: [screen.width, screen.height] };
  const ad = `cizimler-${d.takma_ad.replace(/[^\p{L}\p{N}_-]+/gu, "_")}-${d.kayitlar.length}.json`;
  return new File([JSON.stringify(icerik)], ad, { type: "application/json" });
}

async function bitir() {
  const d = durum!;
  ekran("son");
  $("devam").hidden = d.indeks >= d.sira.length;
  const f = dosya();
  $("gonder").hidden = !(navigator.canShare?.({ files: [f] }));
  if (!d.kayitlar.length) {
    $("ozet").textContent = "";
    $("ozetMetin").textContent = "Henüz kaydedilmiş çizim yok.";
    return;
  }
  $("ozet").textContent = "…";
  $("ozetMetin").textContent = "Yapay zekâ çizimlerine bakıyor…";
  const yanlis: string[] = [];
  let dogru = 0;
  for (const k of d.kayitlar) {
    const hedef = SINIFLAR.findIndex((s) => s.en === k.etiket);
    const t = await tahminEt(OYUN_MODELI, k.vuruslar);
    if (t.sira[0] === hedef) dogru++;
    else yanlis.push(`${SINIFLAR[hedef].tr} → “${SINIFLAR[t.sira[0]].tr}” sandı`);
  }
  $("ozet").textContent = `${dogru}/${d.kayitlar.length}`;
  $("ozetMetin").textContent = `Yapay zekâ ${d.kayitlar.length} çiziminden ${dogru} tanesini bildi.`;
  $("yanlisListe").innerHTML = yanlis.map((y) => `<li>${y}</li>`).join("") || "<li>Hepsini bildi!</li>";
}

$("gonder").addEventListener("click", async () => {
  const f = dosya();
  try {
    await navigator.share({ files: [f], title: "Çizimlerim" });
  } catch { /* kullanıcı vazgeçti */ }
});
$("indir").addEventListener("click", () => {
  const f = dosya();
  const a = document.createElement("a");
  a.href = URL.createObjectURL(f);
  a.download = f.name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 5000);
});

siniflar().then((s) => {
  SINIFLAR = s;
  durum = oku();
  if (durum && durum.indeks > 0) goster();
  else ekran("giris");
});
