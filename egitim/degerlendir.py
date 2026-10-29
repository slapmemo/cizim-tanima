"""Eğitilmiş modelleri test setinde ölçer, ONNX'e aktarır ve rapor şekillerini üretir.

Kullanım: .venv\\Scripts\\python.exe egitim\\degerlendir.py [m1 m2_artirmasiz m2 m3 m3_kismi]
Çıktılar:
  modeller/<ad>.onnx                 softmax dahil; giriş "giris" (N,1,28,28) 0-1, çıkış "olasilik" (N,50)
  deneyler/<ad>/karisiklik.png       karışıklık matrisi
  deneyler/egriler.png, kismi.png    bütün modeller birlikte
  deneyler/sonuclar.json, sonuclar.md
"""
import json
import sys
import time
from pathlib import Path

import matplotlib
import numpy as np
import onnxruntime as ort
import torch
from torch import nn

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from modeller import MODELLER  # noqa: E402
from onisleme import ciz, kismi  # noqa: E402
from siniflar import ADLAR, ISLENMIS_AD, ON_EK, SINIF_SETI, SINIFLAR  # noqa: E402

KOK = Path(__file__).resolve().parent.parent
VERI = KOK / "veri" / ISLENMIS_AD
DENEY = KOK / "deneyler"
ORANLAR = [0.25, 0.5, 0.75, 1.0]
KISMI_SINIF_BASI = 200 if SINIF_SETI == "345" else 1000
SON_EK = "345" if SINIF_SETI == "345" else ""  # ortak çıktı dosyaları: sonuclar345.json vb.
N = len(ADLAR)
TR = [tr for _, tr in SINIFLAR]


def kismi_veri():
    """Her sınıfın ilk 1000 test çiziminin %25/50/75/100 mürekkeple görüntüleri (önbellekli)."""
    yol = VERI / "kismi.npz"
    if yol.exists():
        d = np.load(yol)
        return d["X"], d["y"]
    X = np.zeros((len(ORANLAR), len(ADLAR) * KISMI_SINIF_BASI, 28, 28), np.uint8)
    y = np.zeros(len(ADLAR) * KISMI_SINIF_BASI, np.uint16)
    i = 0
    for no, ad in enumerate(ADLAR):
        with open(VERI / "test_vuruslar" / f"{ad}.ndjson", encoding="utf-8") as f:
            for k, satir in enumerate(f):
                if k >= KISMI_SINIF_BASI:
                    break
                v = json.loads(satir)
                for j, oran in enumerate(ORANLAR):
                    X[j, i] = ciz(kismi(v, oran))
                y[i] = no
                i += 1
    np.savez(yol, X=X, y=y)
    return X, y


@torch.no_grad()
def olasiliklar(model, X, cihaz, yigin=4096):
    cikti = []
    for i in range(0, len(X), yigin):
        xb = torch.from_numpy(X[i:i + yigin]).to(cihaz).unsqueeze(1).float() / 255.0
        cikti.append(torch.softmax(model(xb), 1).cpu())
    return torch.cat(cikti).numpy()


class SoftmaxIle(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, x):
        return torch.softmax(self.model(x), 1)


def onnx_aktar(model, ad):
    yol = KOK / "modeller" / f"{ad}.onnx"
    sarili = SoftmaxIle(model).cpu().eval()
    ornek = torch.rand(1, 1, 28, 28)
    torch.onnx.export(sarili, (ornek,), str(yol), input_names=["giris"], output_names=["olasilik"],
                      dynamic_axes={"giris": {0: "n"}, "olasilik": {0: "n"}}, opset_version=17, dynamo=False)
    secenek = ort.SessionOptions()
    secenek.intra_op_num_threads = 1
    oturum = ort.InferenceSession(str(yol), secenek, providers=["CPUExecutionProvider"])
    deneme = torch.rand(64, 1, 28, 28)
    with torch.no_grad():
        beklenen = sarili(deneme).numpy()
    fark = float(np.abs(oturum.run(None, {"giris": deneme.numpy()})[0] - beklenen).max())
    tek = np.random.rand(1, 1, 28, 28).astype(np.float32)
    for _ in range(50):
        oturum.run(None, {"giris": tek})
    t0 = time.perf_counter()
    for _ in range(500):
        oturum.run(None, {"giris": tek})
    ms = (time.perf_counter() - t0) / 500 * 1000
    return yol.stat().st_size, fark, ms


def main():
    varsayilan = ["m1", "m3", "m3_kismi"] if SINIF_SETI == "345" else ["m1", "m2_artirmasiz", "m2", "m3", "m3_kismi"]
    adlar = sys.argv[1:] or [ON_EK + a for a in varsayilan]
    cihaz = torch.device("cuda")
    d = np.load(VERI / "test.npz")
    Xt, yt = d["X"], d["y"].astype(np.int64)
    Xk, yk = kismi_veri()
    sonuclar = {}
    for ad in adlar:
        kayit = torch.load(KOK / "modeller" / f"{ad}.pt", map_location=cihaz)
        model = MODELLER[kayit["model"]](kayit.get("sinif", 50)).to(cihaz)
        model.load_state_dict(kayit["durum"])
        model.eval()
        p = olasiliklar(model, Xt, cihaz)
        tahmin = p.argmax(1)
        ilk3 = np.argpartition(-p, 3, axis=1)[:, :3]
        km = np.zeros((N, N), np.int64)
        np.add.at(km, (yt, tahmin), 1)
        sinif_dogruluk = km.diagonal() / km.sum(1)
        karisan = []
        for a in range(N):
            for b in range(N):
                if a != b and km[a, b]:
                    karisan.append((int(km[a, b]), ADLAR[a], ADLAR[b]))
        karisan.sort(reverse=True)
        kismi_dogruluk = {}
        for j, oran in enumerate(ORANLAR):
            pk = olasiliklar(model, Xk[j], cihaz)
            # oyun kuralıyla ölçüm (eşik, eşdeğer gruplar, çizim boyunca kabul) olcum.py'de
            kismi_dogruluk[str(oran)] = {"ilk1": float((pk.argmax(1) == yk).mean())}
        boyut, fark, ms = onnx_aktar(model, ad)
        sonuclar[ad] = {
            "model": kayit["model"],
            "en_iyi_epoch": kayit["epoch"],
            "parametre": sum(q.numel() for q in model.parameters()),
            "test_ilk1": float((tahmin == yt).mean()),
            "test_ilk3": float((ilk3 == yt[:, None]).any(1).mean()),
            "sinif_dogruluk": {ADLAR[i]: float(v) for i, v in enumerate(sinif_dogruluk)},
            "en_cok_karisan": [{"sayi": s, "gercek": a, "tahmin": b} for s, a, b in karisan[:30]],
            "kismi": kismi_dogruluk,
            "onnx_bayt": boyut,
            "onnx_en_buyuk_fark": fark,
            "onnx_cpu_ms": ms,
        }
        print(f"{ad}: ilk1 {sonuclar[ad]['test_ilk1']:.4f} ilk3 {sonuclar[ad]['test_ilk3']:.4f} "
              f"onnx {boyut / 1024:.0f} KB fark {fark:.1e} {ms:.3f} ms", flush=True)

        sira = np.argsort(sinif_dogruluk)
        kmn = km / km.sum(1, keepdims=True)
        fig, ax = plt.subplots(figsize=(13, 12))
        ax.imshow(kmn[sira][:, sira], cmap="Blues", vmin=0, vmax=1)
        if N <= 60:
            ax.set_xticks(range(N), [TR[i] for i in sira], rotation=90, fontsize=7)
            ax.set_yticks(range(N), [TR[i] for i in sira], fontsize=7)
        else:
            ax.set_xticks([]); ax.set_yticks([])
        ax.set_xlabel("Tahmin"); ax.set_ylabel("Gerçek")
        ax.set_title(f"{ad} karışıklık matrisi (satır normalleştirilmiş, zordan kolaya)")
        fig.tight_layout(); fig.savefig(DENEY / ad / "karisiklik.png", dpi=110); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for ad in adlar:
        g = json.loads((DENEY / ad / "gecmis.json").read_text(encoding="utf-8"))
        ep = [s["epoch"] for s in g]
        ax[0].plot(ep, [s["egitim_kayip"] for s in g], "--", label=f"{ad} eğitim")
        ax[0].plot(ep, [s["dogrulama_kayip"] for s in g], label=f"{ad} doğrulama")
        ax[1].plot(ep, [s["egitim_dogruluk"] for s in g], "--", label=f"{ad} eğitim")
        ax[1].plot(ep, [s["dogrulama_dogruluk"] for s in g], label=f"{ad} doğrulama")
    ax[0].set_title("Kayıp"); ax[1].set_title("Doğruluk")
    for a in ax:
        a.set_xlabel("epoch"); a.grid(alpha=.3); a.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(DENEY / f"egriler{SON_EK}.png", dpi=110); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    for ad in adlar:
        ax.plot([o * 100 for o in ORANLAR], [sonuclar[ad]["kismi"][str(o)]["ilk1"] for o in ORANLAR], "o-", label=ad)
    ax.set_xlabel("Çizimin tamamlanan kısmı (%)"); ax.set_ylabel("İlk-1 doğruluk")
    ax.set_title("Erken tanıma"); ax.grid(alpha=.3); ax.legend()
    fig.tight_layout(); fig.savefig(DENEY / f"kismi{SON_EK}.png", dpi=110); plt.close(fig)

    (DENEY / f"sonuclar{SON_EK}.json").write_text(json.dumps(sonuclar, indent=2, ensure_ascii=False), encoding="utf-8")
    satirlar = ["| Model | Parametre | Test ilk-1 | Test ilk-3 | %25 | %50 | %75 | ONNX | CPU ms |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for ad, s in sonuclar.items():
        k = s["kismi"]
        satirlar.append(
            f"| {ad} | {s['parametre']:,} | {s['test_ilk1']:.2%} | {s['test_ilk3']:.2%} | "
            f"{k['0.25']['ilk1']:.1%} | {k['0.5']['ilk1']:.1%} | {k['0.75']['ilk1']:.1%} | "
            f"{s['onnx_bayt'] / 1024:.0f} KB | {s['onnx_cpu_ms']:.3f} |")
    (DENEY / f"sonuclar{SON_EK}.md").write_text("\n".join(satirlar) + "\n", encoding="utf-8")
    print("\n".join(satirlar))


if __name__ == "__main__":
    main()
