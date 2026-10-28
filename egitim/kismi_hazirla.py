"""Eğitim ve doğrulama çizimlerinin yarım bırakılmış (kısmi) sürümlerini üretir.

veri_hazirla.py ile aynı ayırmayı (aynı tohum) yeniden kurar; her çizim için mürekkebin
rastgele %20-100'ü alınıp çizilir. Görüntü i, egitim.npz'deki görüntü i'nin kısmi sürümüdür.
Çıktı: veri/islenmis/egitim_kismi.npz, dogrulama_kismi.npz (yalnız X).
Kullanım: .venv\\Scripts\\python.exe egitim\\kismi_hazirla.py
"""
import json
import random
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from onisleme import ciz, kismi  # noqa: E402
from siniflar import ADLAR  # noqa: E402
from veri_hazirla import HAM, ISLENMIS, SAYI, TOHUM  # noqa: E402

EN_AZ = 0.2


def isle(sinif_no):
    kayitlar = []
    with open(HAM / f"{ADLAR[sinif_no]}.ndjson", encoding="utf-8") as f:
        for satir in f:
            k = json.loads(satir)
            if k["recognized"]:
                kayitlar.append(k["drawing"])
    random.Random(TOHUM + sinif_no).shuffle(kayitlar)
    r = random.Random(TOHUM * 7 + sinif_no)
    n_e, n_d = SAYI["egitim"], SAYI["dogrulama"]
    sonuc = {}
    for bolum, parca in (("egitim", kayitlar[:n_e]), ("dogrulama", kayitlar[n_e:n_e + n_d])):
        sonuc[bolum] = np.stack([ciz(kismi(v, r.uniform(EN_AZ, 1.0))) for v in parca])
    return sinif_no, sonuc


def main():
    parcalar = {"egitim": [None] * len(ADLAR), "dogrulama": [None] * len(ADLAR)}
    with ProcessPoolExecutor(12) as havuz:
        for no, sonuc in havuz.map(isle, range(len(ADLAR))):
            for b, X in sonuc.items():
                parcalar[b][no] = X
            print(f"işlendi {ADLAR[no]}", flush=True)
    for b, liste in parcalar.items():
        X = np.concatenate(liste)
        np.savez(ISLENMIS / f"{b}_kismi.npz", X=X)
        print(f"{b}_kismi: {X.shape}")


if __name__ == "__main__":
    main()
