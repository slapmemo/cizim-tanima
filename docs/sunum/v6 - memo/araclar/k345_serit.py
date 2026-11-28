import glob, json, sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
KOK = Path(r"C:/Users/slapm/OneDrive/Desktop/FinalCepKonsol/cizim-tanima")
sys.path.insert(0, str(KOK / "egitim"))
from onisleme import normallestir
S = Path(sys.argv[1]); sat = json.load(open(S / "k345_aday.json", encoding="utf-8"))
kel = set(json.loads((KOK / "demo/public/model/oyun_kelimeleri.json").read_text()))
kay = []
for i, f in enumerate(sorted(glob.glob(str(KOK / "test-verileri/*/cizimler-*.json")))):
    for r in json.load(open(f, encoding="utf-8"))["kayitlar"]:
        if r.get("vuruslar") and r.get("etiket") in kel: kay.append(r)
LAC = "#1C2142"
def serit(js, dosya):
    fig, eks = plt.subplots(1, 4, figsize=(16, 3.6), dpi=120); fig.patch.set_alpha(0)
    for ax, j in zip(eks, js):
        for s in normallestir(kay[j]["vuruslar"]):
            xs, ys = zip(*s); ax.plot(xs, ys, color=LAC, lw=4, solid_capstyle="round", solid_joinstyle="round")
        ax.set_xlim(-15, 270); ax.set_ylim(270, -15); ax.set_aspect("equal"); ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1, wspace=0.25); fig.savefig(S / dosya, transparent=True); plt.close(fig)
DOGRU, YANLIS = [35, 57, 124, 182], [36, 58, 209, 175]
serit(DOGRU, "k345-dogru.png"); serit(YANLIS, "k345-yanlis.png")
for j in DOGRU + YANLIS: s = sat[j]; print(s["kisi"], s["tr"], s["ttr"], s["p"], s["dogru"])
