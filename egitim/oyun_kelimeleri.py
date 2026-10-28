"""Oyunda sorulacak kelimeleri seçer (model 345 sınıfın hepsini tanır, oyunda yalnız bunlar sorulur).

Ölçüt: oyun modelinin (s345_m3_kismi) test setinde sınıf doğruluğu >= ESIK ve elle çıkarılanlarda değil.
Girdi: deneyler/sonuclar345.json (SINIF_SETI=345 ile degerlendir.py)
Çıktı: demo/public/model/oyun_kelimeleri.json, deneyler/oyun_kelimeleri.md
Kullanım: .venv\\Scripts\\python.exe egitim\\oyun_kelimeleri.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from siniflar345 import SINIFLAR  # noqa: E402

KOK = Path(__file__).resolve().parent.parent
MODEL = "s345_m3_kismi"
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


def main():
    sonuc = json.loads((KOK / "deneyler" / "sonuclar345.json").read_text(encoding="utf-8"))[MODEL]
    dogruluk = sonuc["sinif_dogruluk"]
    tr = dict(SINIFLAR)
    secilen, dusuk, elle = [], [], []
    for en, _ in SINIFLAR:
        d = dogruluk[en]
        if en in CIKARILAN:
            elle.append((en, d))
        elif d < ESIK:
            dusuk.append((en, d))
        else:
            secilen.append(en)
    (KOK / "demo" / "public" / "model" / "oyun_kelimeleri.json").write_text(json.dumps(secilen), encoding="utf-8")
    md = [f"# Oyun kelimeleri ({MODEL})", "",
          f"Model 345 sınıfın hepsini tanır; oyunda {len(secilen)} kelime sorulur. Ölçüt: test doğruluğu ≥ %{ESIK * 100:.0f}, "
          f"elle çıkarılanlar hariç.", "",
          f"## Doğruluğu düşük olduğu için çıkarılan ({len(dusuk)})", ""]
    md += [f"- {tr[en]} ({en}): %{d * 100:.0f}" for en, d in sorted(dusuk, key=lambda x: x[1])]
    md += ["", f"## Elle çıkarılan ({len(elle)})", ""]
    md += [f"- {tr[en]} ({en}): {CIKARILAN[en]}, doğruluk %{d * 100:.0f}" for en, d in elle]
    md += ["", f"## Sorulanlar ({len(secilen)})", "", ", ".join(sorted((tr[en] for en in secilen), key=lambda s: s.lower()))]
    (KOK / "deneyler" / "oyun_kelimeleri.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"sorulan {len(secilen)}, düşük doğruluk {len(dusuk)}, elle {len(elle)}")


if __name__ == "__main__":
    main()
