"""Sunum v2 görselleri: kullanıcı çizim örnekleri, BatchNorm görseli, QR kodu, /topla kırpmaları."""
import glob, json, sys
from pathlib import Path
import numpy as np
import torch
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import segno

KOK = Path(r"C:/Users/slapm/OneDrive/Desktop/FinalCepKonsol/cizim-tanima")
sys.path.insert(0, str(KOK / "egitim"))
from modeller import MODELLER  # noqa
from onisleme import ciz, normallestir  # noqa
from siniflar import SINIFLAR  # noqa

S = Path(r"C:/Users/slapm/AppData/Local/Temp/claude/969f34f2dbdc9e64/20368ee8-404f-494b-a890-e73d31035f5d/scratchpad")
CIK = S / "deste_gorsel"
torch.set_grad_enabled(False)
EN = [e for e, _ in SINIFLAR]; TR = {e: t for e, t in SINIFLAR}
LAC, KREM = "#1C2142", "#F6F2EA"

def yukle(ad):
    d = torch.load(KOK / "modeller" / f"{ad}.pt", map_location="cpu", weights_only=False)
    m = MODELLER[d["model"]](50); m.load_state_dict(d["durum"]); return m.eval()

mk = yukle("m3_kismi")

# 1) Kullanıcı çizimleri (kişiler A–E diye gizli)
kisiler = {}
for i, f in enumerate(sorted(glob.glob(str(KOK / "test-verileri/*/cizimler-*.json")))):
    kisiler[Path(f).parent.name] = (chr(65 + i), json.load(open(f, encoding="utf-8"))["kayitlar"])

def tahmin(v):
    x = torch.from_numpy(ciz(v)).float().div(255).view(1, 1, 28, 28)
    p = torch.softmax(mk(x), 1)[0]; k = int(p.argmax()); return EN[k], round(float(p[k]) * 100)

def bul(etiket, tahmin_en=None, dogru=True):
    for ad, (harf, kay) in kisiler.items():
        for r in kay:
            if r.get("etiket") != etiket or not r.get("vuruslar"):
                continue
            t, p = tahmin(r["vuruslar"])
            if dogru and t == etiket and p >= 80:
                return harf, r["vuruslar"], t, p
            if not dogru and t == tahmin_en:
                return harf, r["vuruslar"], t, p
    return None

def serit(ornekler, dosya):
    fig, eks = plt.subplots(1, len(ornekler), figsize=(4 * len(ornekler), 3.6), dpi=120)
    fig.patch.set_alpha(0)
    for ax, (_, v, _, _) in zip(eks, ornekler):
        for s in normallestir(v):
            xs, ys = zip(*s); ax.plot(xs, ys, color=LAC, lw=4, solid_capstyle="round", solid_joinstyle="round")
        ax.set_xlim(-15, 270); ax.set_ylim(270, -15); ax.set_aspect("equal"); ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1, wspace=0.25)
    fig.savefig(CIK / dosya, transparent=True); plt.close(fig)

dogru = [bul(e) for e in ["bicycle", "airplane", "cat", "umbrella"]]
yanlis = [bul("clock", "pizza", False), bul("car", "pizza", False), bul("spider", "sun", False), bul("ladder", "lightning", False)]
bilgi = {}
for ad, grup in (("dogru", dogru), ("yanlis", yanlis)):
    grup = [g for g in grup if g]
    serit(grup, f"kullanici-{ad}.png")
    bilgi[ad] = [{"kisi": h, "cizilen": TR[e2] if (e2 := None) else None, "tahmin": TR[t], "olasilik": p} for h, v, t, p in grup]
# çizilen etiketleri ayrıca yaz
bilgi["dogru_etiket"] = ["bicycle", "airplane", "cat", "umbrella"]
bilgi["yanlis_etiket"] = ["clock", "car", "spider", "ladder"]
(CIK / "kullanici.json").write_text(json.dumps(bilgi, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(bilgi, ensure_ascii=False))

# 2) BatchNorm: 8 kanalın değer aralığı, önce/sonra, aynı eksende
m2 = yukle("m2")
test = np.load(KOK / "veri/islenmis/test.npz")
idx = np.random.default_rng(0).choice(len(test["y"]), 512, replace=False)
xb = torch.from_numpy(test["X"][idx]).float().div(255).unsqueeze(1)
once = m2[0][0](xb); bn = m2[0][1]
sonra = (once - bn.running_mean.view(1, -1, 1, 1)) / torch.sqrt(bn.running_var.view(1, -1, 1, 1) + bn.eps)
kanal = [0, 3, 7, 11, 15, 20, 26, 30]
fig, eks = plt.subplots(1, 2, figsize=(16, 6.2), dpi=130, sharex=True)
fig.patch.set_alpha(0)
for ax, veri, renk, bas in ((eks[0], once, "#E8964A", "BatchNorm’dan önce"), (eks[1], sonra, "#2D57C9", "BatchNorm’dan sonra")):
    for j, c in enumerate(kanal):
        v = veri[:, c].flatten().numpy()
        o, sd = v.mean(), v.std()
        ax.plot([o - sd, o + sd], [j, j], color=renk, lw=14, solid_capstyle="round")
        ax.plot([o], [j], "o", color=LAC, ms=9)
    ax.axvline(0, color="#B9B2A3", lw=1.5, zorder=0)
    ax.set_yticks(range(len(kanal)), [f"kanal {c + 1}" for c in kanal], fontsize=17, color=LAC)
    ax.set_xlim(-1.6, 1.6); ax.tick_params(axis="x", labelsize=16, colors="#565C74")
    ax.set_title(bas, fontsize=24, color=LAC, pad=14, fontweight="bold")
    ax.set_xlabel("kanalın değerleri (ortalama ± sapma)", fontsize=17, color="#565C74")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.invert_yaxis(); ax.set_facecolor("none")
fig.tight_layout(w_pad=4)
fig.savefig(CIK / "batchnorm-buyuk.png", transparent=True); plt.close(fig)

# 3) QR kodu
segno.make("https://cizim-tanima.vercel.app", error="m").save(str(CIK / "qr-site.png"), scale=20, border=2, dark=LAC, light=KREM)

# 4) /topla kırpmaları
E = S / "ekran"
def kirp(k, h, kutu):
    im = Image.open(E / k); w, hh = im.size
    im.crop((int(kutu[0] * w), int(kutu[1] * hh), int(kutu[2] * w), int(kutu[3] * hh))).save(CIK / h, optimize=True)
kirp("topla-giris.png", "topla-giris.png", (0.31, 0.1, 0.69, 0.75))
kirp("topla-cizim.png", "topla-cizim.png", (0.16, 0.05, 0.84, 0.85))
print("bitti")
