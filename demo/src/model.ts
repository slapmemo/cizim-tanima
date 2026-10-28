// ONNX modelini yükler ve vuruşlardan tahmin üretir (tarayıcıda, WASM).
import * as ort from "onnxruntime-web/wasm";
import { BOYUT, ciz, type Vurus } from "./onisleme.ts";

ort.env.wasm.numThreads = 1; // çok iş parçacığı cross-origin isolation ister; model küçük

export type Sinif = { en: string; tr: string };
export type Tahmin = { sira: number[]; olasilik: Float32Array; ms: number };

// "s345_" önekliler Quick, Draw!'ın 345 sınıfının tamamıyla eğitildi, diğerleri 50 sınıfla.
export const MODELLER = ["m1", "m2_artirmasiz", "m2", "m3", "m3_kismi", "s345_m1", "s345_m3", "s345_m3_kismi"] as const;
// Yarım çizimlerle de eğitilen M3, erken tanımada en iyisi (docs/rapor/rapor.md §4). Oyunda 345 sınıflısı:
// model bütün sınıfları tanır, oyunda yalnız oyun_kelimeleri.json'dakiler sorulur.
export const OYUN_MODELI = "s345_m3_kismi";
// "Oyun · 50" sekmesi: ilk sürüm, 50 sınıflı model ve 50 sınıfın hepsi sorulur
export const KOLAY_OYUN_MODELI = "m3_kismi";
// Çizim toplama sayfası 50 sınıfla (arkadaşlardan gelen veriler karşılaştırılabilir kalsın)
export const TOPLA_MODELI = "m3_kismi";

const oturumlar = new Map<string, Promise<ort.InferenceSession>>();

export function oturum(ad: string): Promise<ort.InferenceSession> {
  let o = oturumlar.get(ad);
  if (!o) {
    o = ort.InferenceSession.create(`${import.meta.env.BASE_URL}model/${ad}.onnx`, { executionProviders: ["wasm"] });
    oturumlar.set(ad, o);
  }
  return o;
}

const listeler = new Map<string, Promise<Sinif[]>>();

/** Modelin çıkış sırasındaki sınıflar; model adı verilmezse 50 sınıflık liste. */
export function siniflar(model = "m3_kismi"): Promise<Sinif[]> {
  const dosya = model.startsWith("s345_") ? "siniflar345.json" : "siniflar.json";
  let l = listeler.get(dosya);
  if (!l) {
    l = fetch(`${import.meta.env.BASE_URL}model/${dosya}`).then((y) => y.json());
    listeler.set(dosya, l);
  }
  return l;
}

/** Oyunda sorulan kelimeler (OYUN_MODELI'nin sınıf sırasında indisler). Dosya yoksa bütün sınıflar. */
export async function oyunKelimeleri(): Promise<number[]> {
  const liste = await siniflar(OYUN_MODELI);
  try {
    const y = await fetch(`${import.meta.env.BASE_URL}model/oyun_kelimeleri.json`);
    const adlar: string[] = await y.json();
    const indis = adlar.map((en) => liste.findIndex((s) => s.en === en)).filter((i) => i >= 0);
    if (indis.length) return indis;
  } catch { /* dosya yok */ }
  return liste.map((_, i) => i);
}

export async function tahminEt(ad: string, vuruslar: Vurus[]): Promise<Tahmin> {
  const o = await oturum(ad);
  const bas = performance.now();
  const piksel = ciz(vuruslar);
  const giris = new Float32Array(BOYUT * BOYUT);
  for (let i = 0; i < giris.length; i++) giris[i] = piksel[i] / 255;
  const sonuc = await o.run({ giris: new ort.Tensor("float32", giris, [1, 1, BOYUT, BOYUT]) });
  const olasilik = sonuc.olasilik.data as Float32Array;
  const ms = performance.now() - bas;
  const sira = Array.from(olasilik.keys()).sort((a, b) => olasilik[b] - olasilik[a]);
  return { sira, olasilik, ms };
}

/** Yalnız modelin çalışma süresi (ön işleme hariç), n tekrarın ortalaması (ms). */
export async function hizOlc(ad: string, n = 200): Promise<number> {
  const o = await oturum(ad);
  const giris = new ort.Tensor("float32", new Float32Array(BOYUT * BOYUT).map(() => Math.random()), [1, 1, BOYUT, BOYUT]);
  for (let i = 0; i < 20; i++) await o.run({ giris });
  const bas = performance.now();
  for (let i = 0; i < n; i++) await o.run({ giris });
  return (performance.now() - bas) / n;
}
