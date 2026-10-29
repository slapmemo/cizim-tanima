"""Oyun kuralının Python karşılığı (demo/src/oyun.ts ve main.ts ile aynı sayılar); ölçüm betiklerinin hepsi buradan okur.

Tanınma: modelin birinci tahmini hedefin eşdeğer grubundaysa ve grubun olasılıkları toplamı eşiği geçiyorsa
(grup tek sınıf sayılır; gruplar demo/public/model/esdeger.json, yalnız modelin bildiği sınıflar). Grubu olmayan
sınıfın grubu kendisidir; o zaman kural "birinci tahmin hedef ve olasılığı ≥ eşik" olur.

Gruplar ayrık olduğundan bir adımda tek bilgi yeter: birinci tahminin grubu (g) ve o grubun toplam olasılığı (q).
Hedef h, g == grup(h) ve q ≥ eşik ise kabul edilir.
"""
import json
from pathlib import Path

import numpy as np

KOK = Path(__file__).resolve().parent.parent
MODEL_KLASORU = KOK / "demo" / "public" / "model"

TUR_SAYISI = 5
TUR_SURESI_MS = 20_000
SERI_SURESI_MS = 60_000
SERI_PAS_HAKKI = 3
SERI_PAS_CEZASI = 1
TANINDI_BEKLEME_MS = 700  # seride tanınınca yeni kelimeye kadar (main.ts seriTurBitir)
PAS_BEKLEME_MS = 300

# Çizim boyunca tahmin anları: mürekkebin (nokta sayısının) %5'lik adımları. Oyun 250 ms'de bir ve her vuruş
# bitince tahmin eder; 5-10 sn'lik bir çizimde bu 20-40 tahmindir.
ADIMLAR = [i / 20 for i in range(1, 21)]

# İki oyun sekmesi (main.ts MODLAR): "zor" = Oyun · <kelime sayısı>, 345 sınıflı model; "kolay" = Oyun · 50. "model": oyunda kullanılan; ölçümde aday modeller ayrıca verilir.
SEKMELER = {
    "zor": {"sinif_seti": "345", "model": "s345_m3_kismi", "esik": 0.30, "adaylar": ["s345_m1", "s345_m3", "s345_m3_kismi"]},
    "kolay": {"sinif_seti": "50", "model": "m3_kismi", "esik": 0.50, "adaylar": ["m1", "m2", "m3", "m3_kismi"]},
}


def sinif_listesi(sinif_seti):
    if sinif_seti == "345":
        from siniflar345 import SINIFLAR
    else:
        from siniflar import SINIFLAR_50 as SINIFLAR  # SINIF_SETI ortam değişkeninden bağımsız
    return [en for en, _ in SINIFLAR], dict(SINIFLAR)


def gruplar(adlar):
    """Her sınıfın grup numarası (C,). Grubu olmayan sınıf tek başına bir gruptur."""
    g = np.arange(len(adlar))
    for grup in json.loads((MODEL_KLASORU / "esdeger.json").read_text(encoding="utf-8")):
        uyeler = [adlar.index(a) for a in grup if a in adlar]
        if len(uyeler) > 1:
            g[uyeler] = min(uyeler)
    return g


def oyun_kelimeleri(sekme, adlar):
    """Sekmede sorulan kelimelerin sınıf numaraları."""
    if sekme == "kolay":
        return np.arange(len(adlar))
    kelimeler = json.loads((MODEL_KLASORU / "oyun_kelimeleri.json").read_text(encoding="utf-8"))
    return np.array([adlar.index(a) for a in kelimeler])


def adim_ozeti(p, g):
    """Bir tahmin adımının olasılıkları (N, C) → birinci tahminin grubu (N,) ve grubun toplam olasılığı (N,)."""
    birinci = g[p.argmax(1)]
    birlestir = np.zeros((len(g), g.max() + 1), np.float32)
    birlestir[np.arange(len(g)), g] = 1
    toplam = p @ birlestir
    return birinci.astype(np.int16), toplam[np.arange(len(p)), birinci].astype(np.float32)


def kabul(birinci, q, hedef_grup, esik):
    """birinci, q: (S, N) adım özetleri; hedef_grup: (N,). Her adımda hedef kabul ediliyor mu (S, N)."""
    return (birinci == hedef_grup[None]) & (q >= esik)


def ilk_kabul(birinci, q, hedef_grup, esik):
    """İlk kabul edilen adımın mürekkep oranı (N,); hiç kabul edilmezse inf."""
    k = kabul(birinci, q, hedef_grup, esik)
    ilk = np.full(k.shape[1], np.inf)
    for j in range(len(ADIMLAR) - 1, -1, -1):
        ilk = np.where(k[j], ADIMLAR[j], ilk)
    return ilk


def tur_puani(ms):
    """oyun.ts puan(): tanınma anında kalan süreyle orantılı (0-100)."""
    return np.round(100 * np.maximum(0, TUR_SURESI_MS - ms) / TUR_SURESI_MS)
