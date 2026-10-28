"""Oyun kuralıyla tanınma anı: test çizimleri %10'luk adımlarla ilerletilir, hedef sınıf
birinci ve olasılığı >= 0.5 olduğu ilk adım kaydedilir.

Kullanım: .venv\\Scripts\\python.exe egitim\\oyun_simulasyonu.py [m3 m3_kismi]
Çıktı: deneyler/oyun_simulasyonu.json, deneyler/oyun_simulasyonu.png
"""
import json
import sys
from pathlib import Path

import matplotlib
import numpy as np
import onnxruntime as ort

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from onisleme import ciz, kismi  # noqa: E402
from siniflar import ADLAR, ISLENMIS_AD, ON_EK, SINIF_SETI  # noqa: E402

KOK = Path(__file__).resolve().parent.parent
SINIF_BASI = 50 if SINIF_SETI == "345" else 200
# degerlendir.py'nin erken tanıma ölçümünde kullandığı ilk çizimlerden sonrakiler
ATLA = 200 if SINIF_SETI == "345" else 1000
SON_EK = "345" if SINIF_SETI == "345" else ""
ADIMLAR = [i / 10 for i in range(1, 11)]
ESIK = 0.5


def main():
    adlar = sys.argv[1:] or [ON_EK + "m3", ON_EK + "m3_kismi"]
    X = np.zeros((len(ADIMLAR), len(ADLAR) * SINIF_BASI, 1, 28, 28), np.float32)
    y = np.repeat(np.arange(len(ADLAR)), SINIF_BASI)
    i = 0
    for ad in ADLAR:
        with open(KOK / "veri" / ISLENMIS_AD / "test_vuruslar" / f"{ad}.ndjson", encoding="utf-8") as f:
            satirlar = f.read().splitlines()[ATLA:ATLA + SINIF_BASI]
        for s in satirlar:
            v = json.loads(s)
            for j, oran in enumerate(ADIMLAR):
                X[j, i, 0] = ciz(kismi(v, oran)) / 255.0
            i += 1
    sonuc = {}
    fig, ax = plt.subplots(figsize=(6, 4))
    for ad in adlar:
        oturum = ort.InferenceSession(str(KOK / "modeller" / f"{ad}.onnx"), providers=["CPUExecutionProvider"])
        ilk = np.full(len(y), np.inf)
        for j, oran in enumerate(ADIMLAR):
            p = oturum.run(None, {"giris": X[j]})[0]
            tamam = (p.argmax(1) == y) & (p[np.arange(len(y)), y] >= ESIK)
            ilk = np.where(np.isinf(ilk) & tamam, oran, ilk)
        taninan = np.isfinite(ilk)
        birikimli = [float((ilk <= o).mean()) for o in ADIMLAR]
        sonuc[ad] = {
            "taninan_oran": float(taninan.mean()),
            "ortalama_tanima_ani": float(ilk[taninan].mean()),
            "medyan_tanima_ani": float(np.median(ilk[taninan])),
            "birikimli": dict(zip([str(o) for o in ADIMLAR], birikimli)),
        }
        ax.plot([o * 100 for o in ADIMLAR], birikimli, "o-", label=ad)
        print(f"{ad}: tanınan {taninan.mean():.1%}, ortalama an %{ilk[taninan].mean() * 100:.0f}, "
              f"medyan %{np.median(ilk[taninan]) * 100:.0f}")
    ax.set_xlabel("Çizimin tamamlanan kısmı (%)"); ax.set_ylabel("O ana kadar tanınmış çizim oranı")
    ax.set_title("Oyun kuralıyla tanınma (ilk tahmin ve olasılık ≥ 0,5)"); ax.grid(alpha=.3); ax.legend()
    fig.tight_layout(); fig.savefig(KOK / "deneyler" / f"oyun_simulasyonu{SON_EK}.png", dpi=110)
    (KOK / "deneyler" / f"oyun_simulasyonu{SON_EK}.json").write_text(json.dumps(sonuc, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
