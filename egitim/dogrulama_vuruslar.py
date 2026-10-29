"""Doğrulama çizimlerinin vuruşlarını ham veriden yeniden çıkarır (veri_hazirla.py yalnız test vuruşlarını kaydetmişti).

Oyun kuralına ilişkin seçimler (kelime listesi, eşik, eşdeğer gruplar, oyun modeli) doğrulama çizimleriyle yapılır,
test çizimleri yalnız son ölçüm içindir (olcum.py). Ayırma veri_hazirla.py ile aynıdır (aynı tohum ve sıra);
her sınıfın ilk çizimleri yeniden çizilip dogrulama.npz ile piksel piksel karşılaştırılır.

Çıktı: veri/<islenmis>/dogrulama_vuruslar/<sinif>.ndjson
Kullanım: .venv\\Scripts\\python.exe egitim\\dogrulama_vuruslar.py  (345 sınıf için önce: set SINIF_SETI=345)
"""
import json
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from onisleme import ciz  # noqa: E402
from siniflar import ADLAR, ISLENMIS_AD  # noqa: E402
from veri_hazirla import HAM, ISLENMIS, SAYI, TOHUM  # noqa: E402

KARSILASTIR = 3  # sınıf başına yeniden çizilip karşılaştırılan çizim


def isle(sinif_no):
    ad = ADLAR[sinif_no]
    kayitlar = []
    with open(HAM / f"{ad}.ndjson", encoding="utf-8") as f:
        for satir in f:
            k = json.loads(satir)
            if k["recognized"]:
                kayitlar.append(k["drawing"])
    random.Random(TOHUM + sinif_no).shuffle(kayitlar)
    bas = SAYI["egitim"]
    parca = kayitlar[bas:bas + SAYI["dogrulama"]]
    with open(ISLENMIS / "dogrulama_vuruslar" / f"{ad}.ndjson", "w", encoding="utf-8") as f:
        for v in parca:
            f.write(json.dumps(v, separators=(",", ":")) + "\n")
    return sinif_no, np.stack([ciz(v) for v in parca[:KARSILASTIR]])


def main():
    (ISLENMIS / "dogrulama_vuruslar").mkdir(exist_ok=True)
    X = np.load(ISLENMIS / "dogrulama.npz")["X"]
    t0 = time.time()
    farkli = 0
    with ProcessPoolExecutor(14) as havuz:
        for no, ornek in havuz.map(isle, range(len(ADLAR))):
            beklenen = X[no * SAYI["dogrulama"]: no * SAYI["dogrulama"] + KARSILASTIR]
            if not np.array_equal(ornek, beklenen):
                farkli += 1
                print(f"FARKLI: {ADLAR[no]}", flush=True)
    print(f"{ISLENMIS_AD}: {len(ADLAR)} sınıf, {time.time() - t0:.0f} sn, karşılaştırılan {len(ADLAR) * KARSILASTIR} çizim, "
          f"farklı sınıf {farkli}")
    if farkli:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
