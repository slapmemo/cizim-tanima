// Vuruşlar -> 28x28 gri görüntü. egitim/onisleme.py ile birebir aynı algoritma ve
// aynı işlem sırası (kayan nokta sonuçları eşit çıksın diye). Biri değişirse öteki de
// değişir; eşitlik testi: `python egitim/esitlik_fikstur.py` sonra `npm test`.

export type Vurus = [number[], number[]]; // [xler, yler], Quick, Draw! biçimi
type Nokta = [number, number];

export const BOYUT = 28;
const PAY = 2;
const YARICAP = 1.0;
const RDP_EPS = 2.0;

function rdp(noktalar: Nokta[], eps: number): Nokta[] {
  const n = noktalar.length;
  if (n < 3) return noktalar.slice();
  const tut = new Array<boolean>(n).fill(false);
  tut[0] = tut[n - 1] = true;
  const yigin: [number, number][] = [[0, n - 1]];
  while (yigin.length) {
    const [a, b] = yigin.pop()!;
    const [ax, ay] = noktalar[a];
    const [bx, by] = noktalar[b];
    const dx = bx - ax, dy = by - ay;
    const uz = Math.sqrt(dx * dx + dy * dy);
    let enb = -1.0, enbi = -1;
    for (let i = a + 1; i < b; i++) {
      const [px, py] = noktalar[i];
      const d = uz === 0
        ? Math.sqrt((px - ax) * (px - ax) + (py - ay) * (py - ay))
        : Math.abs(dy * px - dx * py + bx * ay - by * ax) / uz;
      if (d > enb) { enb = d; enbi = i; }
    }
    if (enb > eps) {
      tut[enbi] = true;
      yigin.push([a, enbi]);
      yigin.push([enbi, b]);
    }
  }
  return noktalar.filter((_, i) => tut[i]);
}

export function normallestir(vuruslar: Vurus[]): Nokta[][] {
  let minx = Infinity, miny = Infinity, maxx = -Infinity, maxy = -Infinity;
  for (const [xs, ys] of vuruslar) {
    for (const x of xs) { if (x < minx) minx = x; if (x > maxx) maxx = x; }
    for (const y of ys) { if (y < miny) miny = y; if (y > maxy) maxy = y; }
  }
  if (minx === Infinity) return [];
  const uzun = Math.max(maxx - minx, maxy - miny);
  const olcek = uzun > 0 ? 255.0 / uzun : 1.0;
  const sonuc: Nokta[][] = [];
  for (const [xs, ys] of vuruslar) {
    const noktalar: Nokta[] = xs.map((x, i) => [(x - minx) * olcek, (ys[i] - miny) * olcek]);
    if (noktalar.length) sonuc.push(rdp(noktalar, RDP_EPS));
  }
  return sonuc;
}

/** Vuruşlar -> 784 baytlık görüntü (satır satır). Boş çizim siyah görüntü verir. */
export function ciz(vuruslar: Vurus[]): Uint8Array {
  const cikti = new Uint8Array(BOYUT * BOYUT);
  const nv = normallestir(vuruslar);
  if (!nv.length) return cikti;
  let genislik = -Infinity, yukseklik = -Infinity;
  for (const v of nv) for (const [x, y] of v) { if (x > genislik) genislik = x; if (y > yukseklik) yukseklik = y; }
  const alan = BOYUT - 2 * PAY;
  const olcek = alan / 255.0;
  const ox = (BOYUT - genislik * olcek) / 2.0;
  const oy = (BOYUT - yukseklik * olcek) / 2.0;
  const ax: number[] = [], ay: number[] = [], bx: number[] = [], by: number[] = [];
  for (let v of nv) {
    if (v.length === 1) v = [v[0], v[0]];
    for (let i = 0; i + 1 < v.length; i++) {
      ax.push(v[i][0] * olcek + ox); ay.push(v[i][1] * olcek + oy);
      bx.push(v[i + 1][0] * olcek + ox); by.push(v[i + 1][1] * olcek + oy);
    }
  }
  const s = ax.length;
  for (let j = 0; j < BOYUT; j++) {
    const py = j + 0.5;
    for (let i = 0; i < BOYUT; i++) {
      const px = i + 0.5;
      let enk = Infinity;
      for (let k = 0; k < s; k++) {
        const dx = bx[k] - ax[k], dy = by[k] - ay[k];
        const uz2 = dx * dx + dy * dy;
        let t = 0.0;
        if (uz2 > 0) {
          t = ((px - ax[k]) * dx + (py - ay[k]) * dy) / uz2;
          t = t < 0.0 ? 0.0 : t > 1.0 ? 1.0 : t;
        }
        const ex = px - (ax[k] + t * dx);
        const ey = py - (ay[k] + t * dy);
        const d = Math.sqrt(ex * ex + ey * ey);
        if (d < enk) enk = d;
      }
      let deger = YARICAP + 0.5 - enk;
      deger = deger < 0.0 ? 0.0 : deger > 1.0 ? 1.0 : deger;
      cikti[j * BOYUT + i] = Math.floor(deger * 255.0 + 0.5);
    }
  }
  return cikti;
}
