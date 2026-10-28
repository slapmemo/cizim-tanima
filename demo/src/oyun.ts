// Oyun kuralları (arayüzden bağımsız; CepKonsol'a taşınırken aynen alınır). Plan §6.

export const TUR_SAYISI = 5;
export const TUR_SURESI_MS = 20_000;
export const TANIMA_ESIGI = 0.5;
export const TAHMIN_ARALIGI_MS = 250;

/** Hedef sınıf birinci tahminse ve olasılığı eşiği geçiyorsa çizim tanınmıştır. */
export function tanindiMi(sira: number[], olasilik: ArrayLike<number>, hedef: number): boolean {
  return sira[0] === hedef && olasilik[hedef] >= TANIMA_ESIGI;
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
