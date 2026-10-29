// Oyun kuralları (arayüzden bağımsız; CepKonsol'a taşınırken aynen alınır). Plan §6.

export const TUR_SAYISI = 5;
export const TUR_SURESI_MS = 20_000;
export const TANIMA_ESIGI = 0.5;
// 345 sınıfta olasılık benzer sınıflara bölünür; doğru tahmin %50'ye zor ulaşır (docs/tanima-esigi.md).
// Doğrulamada %50 → %30: tanınan %84,7 → %90,2, tur puanı 53,8 → 59,7; bedeli benzer nesneyle kabulün artması
// (deneyler/olcum.md, "başka kelimeyle kabul" %37 → %62).
export const TANIMA_ESIGI_345 = 0.3;
export const TAHMIN_ARALIGI_MS = 250;
// Seri: toplam süre içinde art arda kaç kelime tanıtılır; süre pas sırasında da akar.
// İlk SERI_PAS_HAKKI pas ücretsiz, sonrakilerin her biri SERI_PAS_CEZASI puan düşürür.
export const SERI_SURESI_MS = 60_000;
export const SERI_PAS_HAKKI = 3;
export const SERI_PAS_CEZASI = 1;

/**
 * Birinci tahmin hedefin eşdeğer grubundaysa ve grubun olasılıkları toplamı eşiği geçiyorsa çizim tanınmıştır
 * (grup tek sınıf sayılır; bardak/kupa/kahve fincanı gibi, public/model/esdeger.json). grup[c]: c sınıfının grup
 * numarası; verilmezse her sınıf kendi grubudur ve kural "hedef birinci ve olasılığı ≥ eşik" olur.
 * Python karşılığı egitim/oyun_kurali.py; ölçümler (deneyler/olcum.md) bu kuralla yapılır.
 */
export function tanindiMi(sira: number[], olasilik: ArrayLike<number>, hedef: number, esik = TANIMA_ESIGI, grup?: ArrayLike<number>): boolean {
  return grupOlasiligi(olasilik, hedef, grup) >= esik && (grup ? grup[sira[0]] === grup[hedef] : sira[0] === hedef);
}

/** Hedefin grubundaki sınıfların olasılıkları toplamı. */
export function grupOlasiligi(olasilik: ArrayLike<number>, hedef: number, grup?: ArrayLike<number>): number {
  if (!grup) return olasilik[hedef];
  let toplam = 0;
  for (let c = 0; c < olasilik.length; c++) if (grup[c] === grup[hedef]) toplam += olasilik[c];
  return toplam;
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
