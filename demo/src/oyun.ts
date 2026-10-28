// Oyun kuralları (arayüzden bağımsız; CepKonsol'a taşınırken aynen alınır). Plan §6.

export const TUR_SAYISI = 5;
export const TUR_SURESI_MS = 20_000;
export const TANIMA_ESIGI = 0.5;
// 345 sınıfta olasılık benzer sınıflara bölünür; doğru tahmin %50'ye zor ulaşır (docs/tanima-esigi.md).
// %30'da tanınan %83 → %89, şans eseri erken tanınma %2,5, yanlış kabul %0,3.
export const TANIMA_ESIGI_345 = 0.3;
export const TAHMIN_ARALIGI_MS = 250;
// Seri: toplam süre içinde art arda kaç kelime tanıtılır; süre pas sırasında da akar.
// İlk SERI_PAS_HAKKI pas ücretsiz, sonrakilerin her biri SERI_PAS_CEZASI puan düşürür.
export const SERI_SURESI_MS = 60_000;
export const SERI_PAS_HAKKI = 3;
export const SERI_PAS_CEZASI = 1;

/** Hedef sınıf birinci tahminse ve olasılığı eşiği geçiyorsa çizim tanınmıştır. */
export function tanindiMi(sira: number[], olasilik: ArrayLike<number>, hedef: number, esik = TANIMA_ESIGI): boolean {
  return sira[0] === hedef && olasilik[hedef] >= esik;
}

/** Tanınma anında kalan süreyle orantılı puan (0-100). */
export function puan(gecenMs: number): number {
  const kalan = Math.max(0, TUR_SURESI_MS - gecenMs);
  return Math.round((100 * kalan) / TUR_SURESI_MS);
}

/** Tekrarsız rastgele n sınıf. */
export function kelimeSec(sinifSayisi: number, n: number, rastgele = Math.random): number[] {
  const dizi = Array.from({ length: sinifSayisi }, (_, i) => i);
  for (let i = dizi.length - 1; i > 0; i--) {
    const j = Math.floor(rastgele() * (i + 1));
    [dizi[i], dizi[j]] = [dizi[j], dizi[i]];
  }
  return dizi.slice(0, n);
}
