"""Vuruşlar -> 28x28 gri görüntü.

Aynı algoritma demo/src/onisleme.ts içinde birebir yazılıdır; biri değişirse öteki de
değişir ve `egitim/esitlik_fikstur.py` + `demo` eşitlik testi yeniden çalıştırılır.

Adımlar:
1. Bütün noktaların sınır kutusu bulunur; çizim sol üste kaydırılır ve uzun kenarı
   255 olacak biçimde oranı korunarak ölçeklenir (Quick, Draw! `simplified` biçimi).
2. Her vuruş Ramer-Douglas-Peucker ile epsilon 2.0'da sadeleştirilir (Google'ın
   `simplified` veri setinde kullandığı değer).
3. 28x28 tuvalde 2 piksel kenar payıyla (24 piksellik alan) ortalanır.
4. Her piksel merkezinin en yakın doğru parçasına uzaklığı d ile
   değer = sınırla(YARICAP + 0.5 - d, 0, 1); bayt = taban(değer * 255 + 0.5).

Vuruş biçimi: [[x0, x1, ...], [y0, y1, ...]] listeleri (Quick, Draw! ndjson ile aynı).
"""
import math

import numpy as np

BOYUT = 28
PAY = 2
YARICAP = 1.0
RDP_EPS = 2.0

_ix, _iy = np.meshgrid(np.arange(BOYUT, dtype=np.float64) + 0.5,
                       np.arange(BOYUT, dtype=np.float64) + 0.5)
_PX = _ix.reshape(-1, 1)  # (784, 1); satır sırası: y dıştaki döngü, x içteki
_PY = _iy.reshape(-1, 1)


def _rdp(noktalar, eps):
    """Ramer-Douglas-Peucker; yinelemeli değil, yığınla (TS ile aynı sıra)."""
    n = len(noktalar)
    if n < 3:
        return list(noktalar)
    tut = [False] * n
    tut[0] = tut[n - 1] = True
    yigin = [(0, n - 1)]
    while yigin:
        a, b = yigin.pop()
        ax, ay = noktalar[a]
        bx, by = noktalar[b]
        dx, dy = bx - ax, by - ay
        uz = math.sqrt(dx * dx + dy * dy)
        enb, enbi = -1.0, -1
        for i in range(a + 1, b):
            px, py = noktalar[i]
            if uz == 0.0:
                d = math.sqrt((px - ax) ** 2 + (py - ay) ** 2)
            else:
                d = abs(dy * px - dx * py + bx * ay - by * ax) / uz
            if d > enb:
                enb, enbi = d, i
        if enb > eps:
            tut[enbi] = True
            yigin.append((a, enbi))
            yigin.append((enbi, b))
    return [p for p, t in zip(noktalar, tut) if t]


def normallestir(vuruslar):
    """Sınır kutusu -> sol üst, uzun kenar 255, sonra RDP. Boş çizimde [] döner."""
    xs = [x for v in vuruslar for x in v[0]]
    ys = [y for v in vuruslar for y in v[1]]
    if not xs:
        return []
    minx, miny = min(xs), min(ys)
    genislik, yukseklik = max(xs) - minx, max(ys) - miny
    uzun = max(genislik, yukseklik)
    olcek = 255.0 / uzun if uzun > 0 else 1.0
    sonuc = []
    for v in vuruslar:
        noktalar = [((x - minx) * olcek, (y - miny) * olcek) for x, y in zip(v[0], v[1])]
        if noktalar:
            sonuc.append(_rdp(noktalar, RDP_EPS))
    return sonuc


def ciz(vuruslar):
    """Vuruşlar -> (28, 28) uint8. Boş çizim siyah görüntü verir."""
    nv = normallestir(vuruslar)
    if not nv:
        return np.zeros((BOYUT, BOYUT), np.uint8)
    tum = [p for v in nv for p in v]
    genislik = max(p[0] for p in tum)
    yukseklik = max(p[1] for p in tum)
    alan = BOYUT - 2 * PAY
    olcek = alan / 255.0
    ox = (BOYUT - genislik * olcek) / 2.0
    oy = (BOYUT - yukseklik * olcek) / 2.0
    ax, ay, bx, by = [], [], [], []
    for v in nv:
        if len(v) == 1:
            v = [v[0], v[0]]
        for (x0, y0), (x1, y1) in zip(v[:-1], v[1:]):
            ax.append(x0 * olcek + ox); ay.append(y0 * olcek + oy)
            bx.append(x1 * olcek + ox); by.append(y1 * olcek + oy)
    ax, ay = np.array(ax)[None, :], np.array(ay)[None, :]
    bx, by = np.array(bx)[None, :], np.array(by)[None, :]
    dx, dy = bx - ax, by - ay
    uz2 = dx * dx + dy * dy
    with np.errstate(invalid="ignore", divide="ignore"):
        t = ((_PX - ax) * dx + (_PY - ay) * dy) / uz2
    t = np.where(uz2 > 0, np.clip(t, 0.0, 1.0), 0.0)
    ex = _PX - (ax + t * dx)
    ey = _PY - (ay + t * dy)
    d = np.sqrt(ex * ex + ey * ey).min(axis=1)
    deger = np.clip(YARICAP + 0.5 - d, 0.0, 1.0)
    return np.floor(deger * 255.0 + 0.5).astype(np.uint8).reshape(BOYUT, BOYUT)


def kismi(vuruslar, oran):
    """Mürekkebin (nokta sayısının) ilk `oran` kadarı; erken tanıma ölçümü için."""
    toplam = sum(len(v[0]) for v in vuruslar)
    kalan = max(1, math.ceil(toplam * oran))
    sonuc = []
    for v in vuruslar:
        if kalan <= 0:
            break
        al = min(kalan, len(v[0]))
        sonuc.append([v[0][:al], v[1][:al]])
        kalan -= al
    return sonuc
