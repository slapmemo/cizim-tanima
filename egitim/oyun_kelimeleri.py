"""Oyunda sorulacak kelimeleri seçer (model 345 sınıfın hepsini tanır, oyunda yalnız bunlar sorulur).

Ölçüt: DOĞRULAMA setinde, eşdeğer grup sayılarak (birinci tahmin hedefin grubundaysa doğru) oyun modelinin
sınıf doğruluğu >= ESIK; elle çıkarılanlar hariç. Oyun modeli (s345_m3_kismi) olcum.py'nin doğrulama
karşılaştırmasıyla seçildi; o karşılaştırma iki M3 adayının ortalamasıyla seçilmiş tarafsız listeyle yapıldı
(--modeller s345_m3 s345_m3_kismi). Test seti seçimde kullanılmaz. Önceki sürüm test setiyle ve grupsuz seçiyordu.

Girdi: deneyler/dogrulama/karisiklik_<model>.npy (esdeger_aday.py üretir), demo/public/model/esdeger.json
Çıktı: demo/public/model/oyun_kelimeleri.json, deneyler/oyun_kelimeleri.md
Kullanım: .venv\\Scripts\\python.exe egitim\\oyun_kelimeleri.py [--modeller s345_m3_kismi]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from esdeger_aday import karisiklik_matrisi  # noqa: E402
from oyun_kurali import MODEL_KLASORU, gruplar, sinif_listesi  # noqa: E402

KOK = Path(__file__).resolve().parent.parent
MODELLER = ["s345_m3_kismi"]
ESIK = 0.70
# 20 sn'de çizilemeyen, soyut ya da oyunda anlamsız olanlar
CIKARILAN = {
    "animal migration": "soyut",
    "camouflage": "çizilemez",
    "The Great Wall of China": "çizilemez",
    "line": "anlamsız (tek çizgi)",
    "squiggle": "anlamsız (karalama)",
    "yoga": "soyut",
}


def grup_dogrulugu(km, g):
    """Satır sınıfının çizimlerinde birinci tahminin aynı grupta olma oranı."""
    ayni = g[:, None] == g[None, :]
    return (km * ayni).sum(1) / km.sum(1)


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--modeller", nargs="+", default=MODELLER)
    modeller = a.parse_args().modeller
    adlar, tr = sinif_listesi("345")
    g = gruplar(adlar)
    dogruluk = np.mean([grup_dogrulugu(karisiklik_matrisi(m), g) for m in modeller], 0)
    tek = np.mean([np.diag(km) / km.sum(1) for km in map(karisiklik_matrisi, modeller)], 0)
    yol = MODEL_KLASORU / "oyun_kelimeleri.json"
    eski = set(json.loads(yol.read_text(encoding="utf-8")))
    secilen, dusuk, elle = [], [], []
    for i, en in enumerate(adlar):
        if en in CIKARILAN:
            elle.append(i)
        elif dogruluk[i] < ESIK:
            dusuk.append(i)
        else:
            secilen.append(en)
    yol.write_text(json.dumps(secilen), encoding="utf-8")
    yeni = set(secilen)
    satir = lambda i: f"- {tr[adlar[i]]} ({adlar[i]}): %{dogruluk[i] * 100:.0f}" + (
        f" (grupsuz %{tek[i] * 100:.0f})" if g[i] != i or (g == g[i]).sum() > 1 else "")
    md = [f"# Oyun kelimeleri ({' / '.join(modeller)})", "",
          f"Model 345 sınıfın hepsini tanır; oyunda {len(secilen)} kelime sorulur. Ölçüt: doğrulama setinde eşdeğer grup "
          f"sayılarak doğruluk (birden çok modelde ortalama) ≥ %{ESIK * 100:.0f}; elle çıkarılanlar hariç.", "",
          f"Önceki listeye (test setiyle seçilmiş, {len(eski)} kelime) göre eklenen: "
          + (", ".join(sorted(tr[a] for a in yeni - eski)) or "yok") + "; çıkan: "
          + (", ".join(sorted(tr[a] for a in eski - yeni)) or "yok") + ".", "",
          f"## Doğruluğu düşük olduğu için çıkarılan ({len(dusuk)})", ""]
    md += [satir(i) for i in sorted(dusuk, key=lambda i: dogruluk[i])]
    md += ["", f"## Elle çıkarılan ({len(elle)})", ""]
    md += [f"- {tr[adlar[i]]} ({adlar[i]}): {CIKARILAN[adlar[i]]}, doğruluk %{dogruluk[i] * 100:.0f}" for i in elle]
    md += ["", f"## Sorulanlar ({len(secilen)})", "", ", ".join(sorted((tr[en] for en in secilen), key=lambda s: s.lower()))]
    (KOK / "deneyler" / "oyun_kelimeleri.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"sorulan {len(secilen)}, düşük doğruluk {len(dusuk)}, elle {len(elle)}; "
          f"eklenen {sorted(yeni - eski)}, çıkan {sorted(eski - yeni)}")


if __name__ == "__main__":
    main()
