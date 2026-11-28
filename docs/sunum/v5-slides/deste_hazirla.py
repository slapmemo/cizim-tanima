"""Sunum destesi için görselleri hazırlar: kırpma, kapak SVG'leri, 'aynı yarım çizim iki model' satırları."""
import json, sys
from pathlib import Path
import numpy as np
import torch
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

KOK = Path(r"C:/Users/slapm/OneDrive/Desktop/FinalCepKonsol/cizim-tanima")
sys.path.insert(0, str(KOK / "egitim"))
from modeller import MODELLER  # noqa
from onisleme import ciz, kismi, normallestir  # noqa
from siniflar import SINIFLAR  # noqa

S = Path(r"C:/Users/slapm/AppData/Local/Temp/claude/969f34f2dbdc9e64/20368ee8-404f-494b-a890-e73d31035f5d/scratchpad")
CIK = S / "deste_gorsel"
CIK.mkdir(exist_ok=True)
G = KOK / "docs" / "sunum" / "gorseller"
torch.set_grad_enabled(False)

# 1) Kırpmalar (grafiklerin kendi başlığı slaytta olacak)
def kirp(kaynak, hedef, kutu):
    im = Image.open(kaynak).convert("RGB")
    w, h = im.size
    x0, y0, x1, y1 = kutu
    im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))).save(CIK / hedef, optimize=True)

BASLIKSIZ = (0, 0.155, 1, 1)
for ad in ["kavram-evrisim", "kavram-havuzlama", "kavram-batchnorm-dropout", "kavram-artik",
           "mimari-m1", "mimari-m2", "mimari-m3", "m3-kismi-veri", "onisleme-4-piksel"]:
    kirp(G / f"{ad}.png", f"{ad}.png", BASLIKSIZ)
kirp(G / "onisleme-hepsi.png", "onisleme-hepsi.png", (0, 0.2, 1, 0.95))
kirp(G / "rdp.png", "rdp.png", (0, 0.2, 1, 0.98))
kirp(G / "ornek-json-cizim-28.png", "ornek-json-cizim-28.png", (0, 0, 1, 0.97))
kirp(KOK / "docs/sunum/4 - veri seti.png", "veri-seti.png", (0, 0, 1, 1))
kirp(KOK / "docs/sunum/5 - ornek json.png", "ornek-ndjson.png", (0.03, 0.085, 0.93, 0.62))
E = S / "ekran"
kirp(E / "site-giris.png", "site-giris.png", (0.15, 0, 0.85, 0.56))
kirp(E / "site-oyun-yarim.png", "site-oyun-tanindi.png", (0.28, 0.07, 0.72, 0.97))
kirp(E / "site-serbest.png", "site-serbest.png", (0.15, 0.07, 0.85, 0.74))

# 2) Kapak SVG'leri: gerçek test çizimleri, beyaz çizgi
def svg_yol(vuruslar, kutu=200, pay=10):
    nv = normallestir(vuruslar)
    o = (kutu - 2 * pay) / 255
    parca = []
    for v in nv:
        d = "M" + " L".join(f"{pay + x * o:.1f} {pay + y * o:.1f}" for x, y in v)
        parca.append(f'<path d="{d}"/>')
    return "".join(parca)

def test_ciz(en, i):
    satir = (KOK / "veri/islenmis/test_vuruslar" / f"{en}.ndjson").read_text(encoding="utf-8").splitlines()[i]
    return json.loads(satir)

kapak = {}
for en, i in [("bicycle", 4), ("cat", 5), ("airplane", 2), ("flower", 3), ("fish", 1), ("ice cream", 2)]:
    kapak[en] = svg_yol(test_ciz(en, i))
(CIK / "kapak_svg.json").write_text(json.dumps(kapak), encoding="utf-8")

# 3) Aynı yarım çizim, iki model
def yukle(ad):
    d = torch.load(KOK / "modeller" / f"{ad}.pt", map_location="cpu", weights_only=False)
    m = MODELLER[d["model"]](50); m.load_state_dict(d["durum"]); return m.eval()

m3, mk = yukle("m3"), yukle("m3_kismi")
TR = [tr for _, tr in SINIFLAR]
EN = [en for en, _ in SINIFLAR]
ORAN = [0.25, 0.5, 0.75, 1.0]

def tahmin(m, v):
    x = torch.from_numpy(ciz(v)).float().div(255).view(1, 1, 28, 28)
    p = torch.softmax(m(x), 1)[0]
    k = int(p.argmax()); return k, float(p[k])

def satir_ciz(vuruslar, dosya):
    fig, eks = plt.subplots(1, 4, figsize=(16, 3.6), dpi=120)
    fig.patch.set_alpha(0)
    nv = normallestir(vuruslar)
    toplam = sum(len(v) for v in nv)
    for ax, oran in zip(eks, ORAN):
        kalan = max(1, int(np.ceil(toplam * oran)))
        for v in nv:
            xs, ys = zip(*v)
            al = min(kalan, len(v))
            if al < len(v):
                ax.plot(xs[max(0, al - 1):], ys[max(0, al - 1):], color="#B9B2A3", lw=3, ls=(0, (1.5, 2.5)),
                        solid_capstyle="round")
            if al >= 1:
                ax.plot(xs[:al], ys[:al], color="#1D2142", lw=4.5, solid_capstyle="round", solid_joinstyle="round")
            kalan -= al
            if kalan <= 0:
                kalan = 0
        ax.set_xlim(-20, 275); ax.set_ylim(275, -20); ax.set_aspect("equal"); ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1, wspace=0.25)
    fig.savefig(CIK / dosya, transparent=True); plt.close(fig)

sonuc = {}
for en in ["cat", "bicycle"]:
    ki = EN.index(en)
    satirlar = (KOK / "veri/islenmis/test_vuruslar" / f"{en}.ndjson").read_text(encoding="utf-8").splitlines()
    for i, s in enumerate(satirlar[:400]):
        v = json.loads(s)
        a = [tahmin(m3, kismi(v, r)) for r in ORAN]
        b = [tahmin(mk, kismi(v, r)) for r in ORAN]
        # M3 yarıda yanlış, M3-kısmi yarıda doğru; ikisi de tamda doğru; çizim en az 4 vuruş
        if (a[1][0] != ki and b[1][0] == ki and a[3][0] == ki and b[3][0] == ki and a[0][0] != ki
                and len(v) >= 3 and a[2][0] == ki):
            sonuc[en] = {"indeks": i, "tr": TR[ki],
                         "m3": [[TR[k], round(p * 100)] for k, p in a],
                         "m3_kismi": [[TR[k], round(p * 100)] for k, p in b]}
            satir_ciz(v, f"iki-model-{en}.png")
            break
(CIK / "iki_model.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(sonuc, ensure_ascii=False))
print(sorted(p.name for p in CIK.iterdir()))
