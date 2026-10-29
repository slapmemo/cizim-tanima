"""Eşdeğer grup adayları: doğrulama setinde en çok karışan sınıf çiftleri (345 sınıflı oyun modeli adayları).

Gruplar elle onaylanır ve demo/public/model/esdeger.json'a yazılır (oyun ve ölçüm betikleri oradan okur).
Karışıklık matrisleri deneyler/dogrulama/karisiklik_<model>.npy olarak saklanır (oyun_kelimeleri.py de kullanır).

Kullanım: .venv\\Scripts\\python.exe egitim\\esdeger_aday.py
Çıktı: deneyler/esdeger_adaylari.md
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from olasilik import karisiklik, model_yukle  # noqa: E402
from siniflar345 import ADLAR, SINIFLAR  # noqa: E402

KOK = Path(__file__).resolve().parent.parent
MODELLER = ["s345_m3", "s345_m3_kismi"]
ADAY = 40


def karisiklik_matrisi(ad):
    """Modelin doğrulama setindeki karışıklık matrisi (önbellekli); "s345_" önekliler 345, diğerleri 50 sınıf."""
    yol = KOK / "deneyler" / "dogrulama" / f"karisiklik_{ad}.npy"
    if not yol.exists():
        s345 = ad.startswith("s345_")
        d = np.load(KOK / "veri" / ("islenmis345" if s345 else "islenmis") / "dogrulama.npz")
        yol.parent.mkdir(exist_ok=True)
        np.save(yol, karisiklik(model_yukle(ad), d["X"], d["y"].astype(np.int64), len(ADLAR) if s345 else 50))
    return np.load(yol)


def main():
    tr = dict(SINIFLAR)
    oran = np.mean([km / km.sum(1, keepdims=True) for km in map(karisiklik_matrisi, MODELLER)], 0)
    np.fill_diagonal(oran, 0)
    iki_yon = oran + oran.T
    a, b = np.triu_indices(len(ADLAR), 1)
    sira = np.argsort(-iki_yon[a, b])[:ADAY]
    kelimeler = set(json.loads((KOK / "demo/public/model/oyun_kelimeleri.json").read_text(encoding="utf-8")))
    md = ["# Eşdeğer grup adayları", "",
          f"Doğrulama seti (sınıf başına 2.500 çizim), {' ve '.join(MODELLER)} ortalaması. "
          "A→B: A çizimlerinin B tahmin edilme oranı. ✓: şimdiki 242 oyun kelimesinde.", "",
          "| # | A | B | A→B | B→A | Toplam |", "| ---: | --- | --- | ---: | ---: | ---: |"]
    for n, k in enumerate(sira, 1):
        i, j = a[k], b[k]
        isaret = lambda x: f"{tr[ADLAR[x]]}{' ✓' if ADLAR[x] in kelimeler else ''}"
        md.append(f"| {n} | {isaret(i)} | {isaret(j)} | %{oran[i, j] * 100:.1f} | %{oran[j, i] * 100:.1f} | %{iki_yon[i, j] * 100:.1f} |")
    (KOK / "deneyler" / "esdeger_adaylari.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
