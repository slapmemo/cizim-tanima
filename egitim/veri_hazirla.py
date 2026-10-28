"""Quick, Draw! `simplified` ndjson dosyalarını indirir, ayırır ve 28x28'e çizer.

Çıktılar (veri/islenmis/):
  egitim.npz, dogrulama.npz, test.npz  -> X (N, 28, 28) uint8, y (N,) uint16 (50 sınıfın eski dosyalarında uint8)
  test_vuruslar/<sinif>.ndjson          -> test çizimlerinin vuruşları (erken tanıma ölçümü)
Ayırma: yalnız recognized=true, sabit tohumla karıştırılır; sınıf başına 30k/5k/5k.

Kullanım: .venv\\Scripts\\python.exe egitim\\veri_hazirla.py
345 sınıf için önce: set SINIF_SETI=345 (çıktı veri/islenmis345/, sınıf başına 20k/2,5k/2,5k)
"""
import json
import random
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from onisleme import ciz  # noqa: E402
from siniflar import ADLAR, ISLENMIS_AD, SINIF_SETI  # noqa: E402

KOK = Path(__file__).resolve().parent.parent
HAM = KOK / "veri" / "ham"
ISLENMIS = KOK / "veri" / ISLENMIS_AD
ADRES = "https://storage.googleapis.com/quickdraw_dataset/full/simplified/{}.ndjson"
# 345 sınıfta bellek (GPU 16 GB) için sınıf başına daha az örnek
SAYI = ({"egitim": 20_000, "dogrulama": 2_500, "test": 2_500} if SINIF_SETI == "345"
        else {"egitim": 30_000, "dogrulama": 5_000, "test": 5_000})
TOHUM = 1234


def indir(ad):
    hedef = HAM / f"{ad}.ndjson"
    if hedef.exists() and hedef.stat().st_size > 0:
        return ad, "var"
    gecici = hedef.with_suffix(".part")
    urllib.request.urlretrieve(ADRES.format(urllib.parse.quote(ad)), gecici)
    gecici.replace(hedef)
    return ad, f"{hedef.stat().st_size / 1e6:.0f} MB"


def isle(sinif_no):
    ad = ADLAR[sinif_no]
    kayitlar = []
    with open(HAM / f"{ad}.ndjson", encoding="utf-8") as f:
        for satir in f:
            k = json.loads(satir)
            if k["recognized"]:
                kayitlar.append(k["drawing"])
    toplam = sum(SAYI.values())
    if len(kayitlar) < toplam:
        raise RuntimeError(f"{ad}: yalnız {len(kayitlar)} tanınmış çizim var")
    random.Random(TOHUM + sinif_no).shuffle(kayitlar)
    sonuc, bas = {}, 0
    for bolum, n in SAYI.items():
        parca = kayitlar[bas:bas + n]
        bas += n
        sonuc[bolum] = np.stack([ciz(v) for v in parca])
        if bolum == "test":
            with open(ISLENMIS / "test_vuruslar" / f"{ad}.ndjson", "w", encoding="utf-8") as f:
                for v in parca:
                    f.write(json.dumps(v, separators=(",", ":")) + "\n")
    return sinif_no, sonuc, len(kayitlar)


def main():
    HAM.mkdir(parents=True, exist_ok=True)
    (ISLENMIS / "test_vuruslar").mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    with ThreadPoolExecutor(8) as havuz:
        for ad, durum in havuz.map(indir, ADLAR):
            print(f"indirildi {ad}: {durum}", flush=True)
    print(f"indirme bitti: {time.time() - t0:.0f} sn", flush=True)

    t0 = time.time()
    parcalar = {b: [None] * len(ADLAR) for b in SAYI}
    with ProcessPoolExecutor(14) as havuz:
        for no, sonuc, tanınan in havuz.map(isle, range(len(ADLAR))):
            for b, X in sonuc.items():
                parcalar[b][no] = X
            print(f"işlendi {ADLAR[no]} ({tanınan} tanınmış)", flush=True)
    for b, liste in parcalar.items():
        X = np.concatenate(liste)
        y = np.concatenate([np.full(len(x), i, np.uint16) for i, x in enumerate(liste)])  # 345 > 255
        np.savez(ISLENMIS / f"{b}.npz", X=X, y=y)
        print(f"{b}: {X.shape}", flush=True)
    print(f"işleme bitti: {time.time() - t0:.0f} sn")


if __name__ == "__main__":
    main()
