"""Gerçek kullanıcı çizimleriyle (kayitlar/*.json) modelleri ölçer.

İki tür dosya okunur:
  - topla.html'den gelen toplu dosya: {"takma_ad", "kayitlar": [{etiket, vuruslar, aygit, ...}], ...}
  - yerel demodan tek kayıt: {"etiket", "vuruslar", "mod": "serbest" | "oyun", ...}
Oyun kayıtları tanındığı anda kesildiği için (model lehine yanlı) doğruluğa katılmaz, ayrıca özetlenir.
Burada yalnız bitmiş çizimin sınıflandırma doğruluğu ölçülür; oyun kuralıyla (eşik, eşdeğer gruplar, çizim boyunca
kabul, sekmede sorulan kelimeler) ölçüm olcum.py'nin "gerçek" bölümündedir.
Aynı oturum iki kez gönderildiyse (aynı "oturum" kimliği) en çok çizim içeren dosya alınır.

Kullanım: .venv\\Scripts\\python.exe egitim\\gercek_degerlendir.py [model adları; varsayılan: bulunan 50 ve 345 sınıflı modellerin hepsi]
Çıktı: deneyler/gercek.json ve ekrana tablolar.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import onnxruntime as ort

sys.path.insert(0, str(Path(__file__).parent))
from onisleme import ciz  # noqa: E402
from siniflar import ADLAR, SINIFLAR  # noqa: E402
from siniflar345 import ADLAR as ADLAR345, SINIFLAR as SINIFLAR345  # noqa: E402

KOK = Path(__file__).resolve().parent.parent
TR = dict(SINIFLAR)
TR345 = dict(SINIFLAR345)
AYGIT = {"mouse": "fare", "touch": "dokunma", "pen": "kalem"}


def yukle():
    oturumlar, tekil, oyun = {}, [], []
    yollar = sorted((KOK / "kayitlar").glob("*.json")) + sorted((KOK / "test-verileri").glob("**/*.json"))
    for yol in yollar:
        k = json.loads(yol.read_text(encoding="utf-8"))
        if isinstance(k.get("kayitlar"), list):
            onceki = oturumlar.get(k.get("oturum") or yol.name)
            if not onceki or len(k["kayitlar"]) > len(onceki["kayitlar"]):
                oturumlar[k.get("oturum") or yol.name] = k
        elif k.get("mod") in ("oyun", "seri"):
            oyun.append(k)
        else:
            tekil.append({**k, "kisi": "yerel"})
    cizimler = list(tekil)
    for o in oturumlar.values():
        cizimler += [{**c, "kisi": o.get("takma_ad") or "?"} for c in o["kayitlar"]]
    cizimler = [c for c in cizimler if c.get("etiket") in ADLAR and c.get("vuruslar")]
    return cizimler, oyun


def main():
    adlar = sys.argv[1:] or ["m1", "m2_artirmasiz", "m2", "m3", "m3_kismi", "s345_m1", "s345_m3", "s345_m3_kismi"]
    adlar = [a for a in adlar if (KOK / "modeller" / f"{a}.onnx").exists()]
    cizimler, oyun = yukle()
    if oyun:
        taninan = [k for k in oyun if k.get("taninan")]
        sure = np.mean([k["sure_ms"] for k in taninan]) / 1000 if taninan else float("nan")
        print(f"oyun: {len(oyun)} tur, tanınan {len(taninan) / len(oyun):.1%}, ortalama tanınma {sure:.1f} sn\n")
    if not cizimler:
        print("Ölçülecek çizim yok: topla.html dosyalarını ya da Serbest çizim kayıtlarını kayitlar/ altına koy.")
        return

    X = np.stack([ciz(c["vuruslar"]) for c in cizimler]).astype(np.float32)[:, None] / 255.0
    y50 = np.array([ADLAR.index(c["etiket"]) for c in cizimler])
    y345 = np.array([ADLAR345.index(c["etiket"]) for c in cizimler])
    kisi = np.array([c["kisi"] for c in cizimler])
    aygit = np.array([AYGIT.get(c.get("aygit"), c.get("aygit") or "?") for c in cizimler])
    print(f"{len(cizimler)} çizim, {len(set(kisi))} kişi, {len(set(y50))} sınıf, aygıt: {dict(Counter(aygit.tolist()))}\n")

    test = {}
    sonuc_yolu = KOK / "deneyler" / "sonuclar.json"
    if sonuc_yolu.exists():
        test = json.loads(sonuc_yolu.read_text(encoding="utf-8"))
    sonuc = {"cizim": len(cizimler), "kisi": len(set(kisi)), "aygit": dict(Counter(aygit.tolist())), "modeller": {},
             "oyun": {"tur": len(oyun), "taninan": sum(1 for k in oyun if k.get("taninan"))}}

    print("| Model | Gerçek ilk-1 | Gerçek ilk-3 | Quick, Draw! test ilk-1 |")
    print("| --- | ---: | ---: | ---: |")
    tahminler = {}
    for ad in adlar:
        oturum = ort.InferenceSession(str(KOK / "modeller" / f"{ad}.onnx"), providers=["CPUExecutionProvider"])
        p = oturum.run(None, {"giris": X})[0]
        # 345 sınıflı modellerde etiketler 345 listesindeki sıraya çevrilir
        y = y345 if ad.startswith("s345_") else y50
        tahminler[ad] = (p, y)
        dogru = p.argmax(1) == y
        r = {
            "ilk1": float(dogru.mean()),
            "ilk3": float((np.argsort(-p, 1)[:, :3] == y[:, None]).any(1).mean()),
            "aygit": {a: float(dogru[aygit == a].mean()) for a in sorted(set(aygit))},
            "kisi": {k: float(dogru[kisi == k].mean()) for k in sorted(set(kisi))},
        }
        sonuc["modeller"][ad] = r
        qd = test.get(ad, {}).get("test_ilk1")
        print(f"| {ad} | {r['ilk1']:.1%} | {r['ilk3']:.1%} | "
              + (f"{qd:.2%} |" if qd else "- |"))

    print("\nAygıta göre ilk-1:")
    for ad in adlar:
        print(f"  {ad}: " + ", ".join(f"{a} {v:.1%} (n={int((aygit == a).sum())})"
                                      for a, v in sonuc["modeller"][ad]["aygit"].items()))
    print("\nKişiye göre ilk-1:")
    for ad in adlar:
        print(f"  {ad}: " + ", ".join(f"{k} {v:.1%} (n={int((kisi == k).sum())})"
                                      for k, v in sonuc["modeller"][ad]["kisi"].items()))

    son = adlar[-1]
    p, y = tahminler[son]
    liste, tr = (ADLAR345, TR345) if son.startswith("s345_") else (ADLAR, TR)
    hatalar = Counter((tr[liste[a]], tr[liste[b]]) for a, b in zip(y, p.argmax(1)) if a != b)
    sonuc["en_cok_karisan"] = [{"gercek": a, "tahmin": b, "sayi": n} for (a, b), n in hatalar.most_common(10)]
    print(f"\n{son} en çok karışan: " + ", ".join(f"{a}→{b} ({n})" for (a, b), n in hatalar.most_common(10)))
    (KOK / "deneyler" / "gercek.json").write_text(json.dumps(sonuc, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
