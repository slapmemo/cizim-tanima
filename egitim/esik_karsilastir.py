"""Oyunda tanınma kuralı karşılaştırması (docs/tanima-esigi.md).

Her kural için test çizimleri %10'luk adımlarla ilerletilir:
  - tanınan: hedef sorulduğunda çizim bitene kadar tanınan oran,
  - ortalama an: tanınanlarda mürekkep oranı,
  - erken: mürekkebin ilk %20'sinde tanınan (şans eseri tanınma göstergesi),
  - yanlış kabul: çizime rastgele BAŞKA bir oyun kelimesi sorulmuş gibi bakılır; kuralın bunu kabul ettiği oran
    (oyuncu "kupa" sorulunca bardak çizse de geçer mi?).
Yalnız oyunda sorulan sınıflar kullanılır. Gerçek kullanıcı çizimleri (test-verileri/) ayrıca ölçülür.

Kullanım: .venv\\Scripts\\python.exe egitim\\esik_karsilastir.py
Çıktı: deneyler/esik_karsilastir.md ve ekrana tablolar.
"""
import json
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort

sys.path.insert(0, str(Path(__file__).parent))
from onisleme import ciz, kismi  # noqa: E402
from siniflar import ADLAR as ADLAR50  # noqa: E402
from siniflar345 import ADLAR as ADLAR345  # noqa: E402

KOK = Path(__file__).resolve().parent.parent
ADIMLAR = [i / 10 for i in range(1, 11)]
SINIF_BASI = 50
ATLA = 200  # degerlendir.py'nin erken tanıma çizimlerinden sonrakiler (345 veri setinde)


def birinci_esik(t):
    return lambda p, y: (p.argmax(1) == y) & (p[np.arange(len(y)), y] >= t)


def fark(f):
    def kural(p, y):
        s = np.sort(p, 1)
        return (p.argmax(1) == y) & (s[:, -1] - s[:, -2] >= f)
    return kural


def ilk_n(n, t):
    def kural(p, y):
        sira = np.argsort(-p, 1)[:, :n]
        return (sira == y[:, None]).any(1) & (p[np.arange(len(y)), y] >= t)
    return kural


KURALLAR = {
    "birinci + ≥%50 (şimdiki)": birinci_esik(0.5),
    "birinci + ≥%40": birinci_esik(0.4),
    "birinci + ≥%35": birinci_esik(0.35),
    "birinci + ≥%30": birinci_esik(0.3),
    "birinci + ≥%25": birinci_esik(0.25),
    "birinci + ikinciden ≥10 puan önde": fark(0.10),
    "birinci + ikinciden ≥20 puan önde": fark(0.20),
    "ilk 3'te + ≥%20 (Quick, Draw! benzeri)": ilk_n(3, 0.20),
    "ilk 3'te + ≥%15 (Quick, Draw! benzeri)": ilk_n(3, 0.15),
}


def adim_goruntuleri(vuruslar_listesi):
    X = np.zeros((len(ADIMLAR), len(vuruslar_listesi), 1, 28, 28), np.float32)
    for i, v in enumerate(vuruslar_listesi):
        for j, oran in enumerate(ADIMLAR):
            X[j, i, 0] = ciz(kismi(v, oran)) / 255.0
    return X


def olc(oturum, X, y, y_yanlis):
    P = [oturum.run(None, {"giris": X[j]})[0] for j in range(len(ADIMLAR))]
    satirlar = {}
    for ad, kural in KURALLAR.items():
        ilk = np.full(len(y), np.inf)
        yanlis = np.zeros(len(y), bool)
        for j, oran in enumerate(ADIMLAR):
            ilk = np.where(np.isinf(ilk) & kural(P[j], y), oran, ilk)
            yanlis |= kural(P[j], y_yanlis)
        t = np.isfinite(ilk)
        satirlar[ad] = (t.mean(), ilk[t].mean() if t.any() else float("nan"), (ilk <= 0.2).mean(), yanlis.mean())
    return satirlar


def tablo(baslik, satirlar, gercek=None):
    md = [f"### {baslik}", "", "| Kural | Tanınan | Ortalama an | İlk %20'de | Yanlış kabul |" + (" Gerçek çizim tanınan |" if gercek else ""),
          "| --- | ---: | ---: | ---: | ---: |" + (" ---: |" if gercek else "")]
    for ad, (t, an, erken, yanlis) in satirlar.items():
        md.append(f"| {ad} | %{t * 100:.1f} | %{an * 100:.0f} | %{erken * 100:.1f} | %{yanlis * 100:.1f} |"
                  + (f" %{gercek[ad][0] * 100:.1f} |" if gercek else ""))
    return md


def gercek_cizimler():
    cizimler = []
    for yol in sorted((KOK / "test-verileri").glob("**/*.json")):
        k = json.loads(yol.read_text(encoding="utf-8"))
        cizimler += [c for c in k.get("kayitlar", []) if c.get("etiket") in ADLAR50 and c.get("vuruslar")]
    return cizimler


def main():
    rng = np.random.default_rng(1234)
    md = ["# Tanınma kuralı karşılaştırması", "",
          "Ölçüt açıklamaları `egitim/esik_karsilastir.py` başında. Test çizimleri %10'luk mürekkep adımlarıyla ilerletildi; "
          "\"yanlış kabul\": aynı çizime rastgele başka bir oyun kelimesi soruldu sayılır.", ""]
    gercek = gercek_cizimler()
    Xg = adim_goruntuleri([c["vuruslar"] for c in gercek])

    for model, liste, kelimeler, veri in [
        ("s345_m3_kismi", ADLAR345, json.loads((KOK / "demo/public/model/oyun_kelimeleri.json").read_text(encoding="utf-8")), "islenmis345"),
        ("m3_kismi", ADLAR50, ADLAR50, "islenmis"),
    ]:
        oturum = ort.InferenceSession(str(KOK / "modeller" / f"{model}.onnx"), providers=["CPUExecutionProvider"])
        vuruslar, y = [], []
        for en in kelimeler:
            with open(KOK / "veri" / veri / "test_vuruslar" / f"{en}.ndjson", encoding="utf-8") as f:
                for s in f.read().splitlines()[ATLA:ATLA + SINIF_BASI]:
                    vuruslar.append(json.loads(s))
                    y.append(liste.index(en))
        y = np.array(y)
        k_indis = np.array([liste.index(en) for en in kelimeler])
        y_yanlis = np.array([rng.choice(k_indis[k_indis != h]) for h in y])
        sat = olc(oturum, adim_goruntuleri(vuruslar), y, y_yanlis)

        yg = np.array([liste.index(c["etiket"]) for c in gercek])
        yg_yanlis = np.array([rng.choice(k_indis[k_indis != h]) for h in yg])
        sat_g = olc(oturum, Xg, yg, yg_yanlis)
        md += tablo(f"{model} — {len(kelimeler)} oyun kelimesi, {len(y)} test çizimi; gerçek: {len(gercek)} çizim", sat, sat_g) + [""]
        print("\n".join(tablo(model, sat, sat_g)), "\n")
    (KOK / "deneyler" / "esik_karsilastir.md").write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
