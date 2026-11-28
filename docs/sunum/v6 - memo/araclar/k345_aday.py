import glob, json, sys
from pathlib import Path
import numpy as np, onnxruntime as ort
KOK = Path(r"C:/Users/slapm/OneDrive/Desktop/FinalCepKonsol/cizim-tanima")
sys.path.insert(0, str(KOK / "egitim"))
from onisleme import ciz
M = KOK / "demo/public/model"
s345 = json.loads((M / "siniflar345.json").read_text(encoding="utf-8")); AD = [s["en"] for s in s345]; TR = {s["en"]: s["tr"] for s in s345}
s50 = json.loads((M / "siniflar.json").read_text(encoding="utf-8")); AD50 = [s["en"] for s in s50]
kel = set(json.loads((M / "oyun_kelimeleri.json").read_text()))
grp = {a: {a} for a in AD}
for g in json.loads((M / "esdeger.json").read_text()):
    for a in g: grp[a] = set(g)
o345 = ort.InferenceSession(str(M / "s345_m3_kismi.onnx"), providers=["CPUExecutionProvider"])
o50 = ort.InferenceSession(str(M / "m3_kismi.onnx"), providers=["CPUExecutionProvider"])
kay = []
for i, f in enumerate(sorted(glob.glob(str(KOK / "test-verileri/*/cizimler-*.json")))):
    for r in json.load(open(f, encoding="utf-8"))["kayitlar"]:
        if r.get("vuruslar") and r.get("etiket") in kel: kay.append((chr(65 + i), r))
X = np.stack([ciz(r["vuruslar"]) for _, r in kay]).astype(np.float32)[:, None] / 255
p = o345.run(None, {o345.get_inputs()[0].name: X})[0]; q = o50.run(None, {o50.get_inputs()[0].name: X})[0]
sat = []
for j, (h, r) in enumerate(kay):
    e = r["etiket"]; t = AD[p[j].argmax()]; ok = t in grp[e]
    t50 = AD50[q[j].argmax()]
    sat.append(dict(j=j, kisi=h, etiket=e, tr=TR[e], tahmin=t, ttr=TR[t], p=round(float(p[j].max()) * 100), dogru=ok, d50=(t50 == e), p50=round(float(q[j].max()) * 100)))
print("toplam", len(sat), "doğru", sum(s["dogru"] for s in sat))
print("YANLIŞ (345), 50'de doğru olanlar:")
for s in sat:
    if not s["dogru"] and s["d50"]: print(f'  {s["j"]:3} {s["kisi"]} {s["tr"]} -> {s["ttr"]} %{s["p"]}  (50: %{s["p50"]})')
print("DOĞRU yüksek:")
for s in sorted([s for s in sat if s["dogru"]], key=lambda s: -s["p"])[:40]: print(f'  {s["j"]:3} {s["kisi"]} {s["tr"]} %{s["p"]}')
json.dump(sat, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False)
