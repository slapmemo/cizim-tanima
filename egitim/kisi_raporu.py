"""Arkadaşlardan gelen toplama dosyaları için kişi başına klasör ve rapor üretir.

test-verileri/ altındaki her cizimler-*.json (topla.html çıktısı) için:
  test-verileri/<takma_ad>/
    <dosya>.json        dosya buraya taşınır
    cizimler.png        bütün çizimler tek tabloda (yeşil: bildi, kırmızı: bilemedi)
    resimler/NN-<nesne>.png  her çizim ayrı
    rapor.md            özet, nesne nesne tahminler, bilemedikleri
Tahminler oyun modeliyle (M3-kısmi); özet tabloda bütün modellerin doğruluğu da var.
Dosyalar alt klasöre taşındıktan sonra da yeniden çalıştırılabilir (raporlar yenilenir).

Kullanım: .venv\\Scripts\\python.exe egitim\\kisi_raporu.py
"""
import json
import re
import shutil
import sys
from pathlib import Path

import matplotlib
import numpy as np
import onnxruntime as ort

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from onisleme import ciz  # noqa: E402
from siniflar import ADLAR, SINIFLAR  # noqa: E402
from siniflar345 import ADLAR as ADLAR345  # noqa: E402

KOK = Path(__file__).resolve().parent.parent
KLASOR = KOK / "test-verileri"
OYUN_MODELI = "m3_kismi"
# s345_: 345 sınıfın tamamıyla eğitilenler (dosyası varsa); aynı çizim 345 seçenek arasında ölçülür
MODELLER = ["m1", "m2_artirmasiz", "m2", "m3", "m3_kismi", "s345_m1", "s345_m3", "s345_m3_kismi"]
TR = dict(SINIFLAR)
AYGIT = {"mouse": "fare", "touch": "dokunma", "pen": "kalem"}
YESIL, KIRMIZI, LACIVERT = "#16a34a", "#dc2626", "#071943"


def klasor_adi(ad):
    return re.sub(r"[^\w-]+", "_", ad.strip()).strip("_") or "adsiz"


def vurus_ciz(a, vuruslar, renk):
    for xs, ys in vuruslar:
        if len(xs) == 1:
            a.plot(xs, ys, "o", color=renk, ms=2)
        a.plot(xs, ys, color=renk, lw=2, solid_capstyle="round", solid_joinstyle="round")
    a.invert_yaxis()
    a.set_aspect("equal")
    a.set_xticks([]); a.set_yticks([])
    for k in a.spines.values():
        k.set_color("#dbe3f5")


def isle(yol, oturumlar):
    veri = json.loads(yol.read_text(encoding="utf-8"))
    kayitlar = [k for k in veri.get("kayitlar", []) if k.get("etiket") in ADLAR and k.get("vuruslar")]
    if not kayitlar:
        print(f"{yol.name}: çizim yok, atlandı")
        return
    hedef_klasor = KLASOR / klasor_adi(veri.get("takma_ad") or yol.stem)
    hedef_klasor.mkdir(exist_ok=True)
    if yol.parent != hedef_klasor:
        yol = Path(shutil.move(str(yol), hedef_klasor / yol.name))

    X = np.stack([ciz(k["vuruslar"]) for k in kayitlar]).astype(np.float32)[:, None] / 255.0
    y = np.array([ADLAR.index(k["etiket"]) for k in kayitlar])
    y345 = np.array([ADLAR345.index(k["etiket"]) for k in kayitlar])
    p = {m: o.run(None, {"giris": X})[0] for m, o in oturumlar.items()}
    po = p[OYUN_MODELI]
    sira = np.argsort(-po, 1)
    bildi = sira[:, 0] == y
    ilk3 = (sira[:, :3] == y[:, None]).any(1)

    # tek tek resimler
    resimler = hedef_klasor / "resimler"
    if resimler.exists():
        shutil.rmtree(resimler)
    resimler.mkdir()
    for i, k in enumerate(kayitlar):
        fig, a = plt.subplots(figsize=(3, 3))
        vurus_ciz(a, k["vuruslar"], LACIVERT)
        a.set_title(TR[k["etiket"]], fontsize=12)
        fig.tight_layout()
        fig.savefig(resimler / f"{i + 1:02d}-{klasor_adi(TR[k['etiket']])}.png", dpi=80)
        plt.close(fig)

    # tablo
    sutun = 8
    satir = -(-len(kayitlar) // sutun)
    fig, eksen = plt.subplots(satir, sutun, figsize=(sutun * 2, satir * 2.3))
    for a in np.atleast_1d(eksen).flat:
        a.axis("off")
    for i, (a, k) in enumerate(zip(np.atleast_1d(eksen).flat, kayitlar)):
        a.axis("on")
        vurus_ciz(a, k["vuruslar"], LACIVERT)
        renk = YESIL if bildi[i] else KIRMIZI
        tahmin = TR[ADLAR[sira[i, 0]]]
        alt = "✓" if bildi[i] else f"✗ {tahmin}"
        a.set_title(f"{TR[k['etiket']]}\n{alt}", fontsize=9, color=renk)
        for s in a.spines.values():
            s.set_color(renk); s.set_linewidth(2)
    fig.suptitle(f"{veri.get('takma_ad', '?')}: {bildi.sum()}/{len(kayitlar)} bildi (yeşil bildi, kırmızı bilemedi; altında modelin tahmini)",
                 fontsize=12)
    fig.tight_layout()
    fig.savefig(hedef_klasor / "cizimler.png", dpi=90)
    plt.close(fig)

    # rapor
    aygitlar = sorted({AYGIT.get(k.get("aygit"), k.get("aygit") or "?") for k in kayitlar})
    sureler = [k.get("sure_ms", 0) / 1000 for k in kayitlar if k.get("sure_ms")]
    md = [
        f"# {veri.get('takma_ad', '?')} — çizim raporu",
        "",
        f"- Dosya: `{yol.name}`",
        f"- Çizim: {len(kayitlar)} · atlanan: {len(veri.get('atlanan', []))}"
        + (f" ({', '.join(TR.get(a, a) for a in veri['atlanan'])})" if veri.get("atlanan") else ""),
        f"- Aygıt: {', '.join(aygitlar)} · tarih: {(veri.get('baslangic') or '')[:10]}",
        f"- Çizim başına süre: ortalama {np.mean(sureler):.1f} sn, en kısa {min(sureler):.1f} sn, en uzun {max(sureler):.1f} sn" if sureler else "- Süre bilgisi yok",
        "",
        f"## Özet (oyun modeli {OYUN_MODELI})",
        "",
        f"- **Bildi (ilk tahmin doğru): {bildi.sum()}/{len(kayitlar)} (%{bildi.mean() * 100:.0f})**",
        f"- İlk 3 tahminde doğru: {ilk3.sum()}/{len(kayitlar)} (%{ilk3.mean() * 100:.0f})",
        f"- Oyunda tanınırdı (ilk tahmin + olasılık ≥ %50): {(bildi & (po.max(1) >= 0.5)).sum()}/{len(kayitlar)}",
        "",
        "| Model | Bildi |",
        "| --- | ---: |",
    ]
    for m in p:
        d = (p[m].argmax(1) == (y345 if m.startswith("s345_") else y))
        md.append(f"| {m} | {d.sum()}/{len(kayitlar)} (%{d.mean() * 100:.0f}) |")
    md += ["", "![Bütün çizimler](cizimler.png)", ""]

    yanlis = [i for i in range(len(kayitlar)) if not bildi[i]]
    md += ["## Bilemedikleri", ""]
    if yanlis:
        md += ["| # | Çizilen | Model ne sandı | Doğru nesnenin olasılığı / sırası |", "| ---: | --- | --- | --- |"]
        for i in yanlis:
            tahminler = ", ".join(f"{TR[ADLAR[j]]} %{po[i, j] * 100:.0f}" for j in sira[i, :3])
            dogru_sira = int(np.where(sira[i] == y[i])[0][0]) + 1
            md.append(f"| {i + 1} | {TR[kayitlar[i]['etiket']]} | {tahminler} | %{po[i, y[i]] * 100:.1f} · {dogru_sira}. sırada |")
    else:
        md.append("Hepsini bildi.")

    md += ["", "## Bütün çizimler", "", "| # | Çizilen | Sonuç | İlk 3 tahmin | Süre |", "| ---: | --- | --- | --- | ---: |"]
    for i, k in enumerate(kayitlar):
        tahminler = ", ".join(f"{TR[ADLAR[j]]} %{po[i, j] * 100:.0f}" for j in sira[i, :3])
        sure = f"{k['sure_ms'] / 1000:.1f} sn" if k.get("sure_ms") else "-"
        md.append(f"| {i + 1} | [{TR[k['etiket']]}](resimler/{i + 1:02d}-{klasor_adi(TR[k['etiket']])}.png) | "
                  f"{'✓' if bildi[i] else '✗'} | {tahminler} | {sure} |")
    (hedef_klasor / "rapor.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"{veri.get('takma_ad')}: {bildi.sum()}/{len(kayitlar)} bildi -> {hedef_klasor.relative_to(KOK)}")


def main():
    oturumlar = {m: ort.InferenceSession(str(KOK / "modeller" / f"{m}.onnx"), providers=["CPUExecutionProvider"])
                 for m in MODELLER if (KOK / "modeller" / f"{m}.onnx").exists()}
    dosyalar = sorted(KLASOR.glob("*.json")) + sorted(KLASOR.glob("*/*.json"))
    if not dosyalar:
        print("test-verileri/ altında dosya yok")
    for yol in dosyalar:
        isle(yol, oturumlar)


if __name__ == "__main__":
    main()
