"""Python ve TypeScript ön işlemesinin eşitlik testi için fikstür üretir.

Test çizimlerinden (her sınıftan 6, tam ve kısmi) vuruşlar + Python'un ürettiği
pikseller demo/test/fikstur.json dosyasına yazılır; `npm test` (demo/) aynı
vuruşları TS ile çizip karşılaştırır. Ayrıca uç durumlar: tek nokta, yatay çizgi, boş.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from onisleme import ciz, kismi  # noqa: E402
from siniflar import ADLAR  # noqa: E402

KOK = Path(__file__).resolve().parent.parent

ornekler = [
    [[[10], [20]]],
    [[[0, 100, 200], [50, 50, 50]]],
    [[[5, 5], [0, 300]], [[0.5, 99.25, 13.125], [7.75, 3.5, 88.0]]],
    [],
]
for ad in ADLAR:
    with open(KOK / "veri" / "islenmis" / "test_vuruslar" / f"{ad}.ndjson", encoding="utf-8") as f:
        satirlar = [json.loads(next(f)) for _ in range(6)]
    for i, v in enumerate(satirlar):
        ornekler.append(kismi(v, [0.3, 0.6, 1.0][i % 3]))

cikti = [{"vuruslar": v, "pikseller": ciz(v).ravel().tolist()} for v in ornekler]
hedef = KOK / "demo" / "test" / "fikstur.json"
hedef.parent.mkdir(parents=True, exist_ok=True)
hedef.write_text(json.dumps(cikti, separators=(",", ":")), encoding="utf-8")
print(f"{len(cikti)} örnek -> {hedef}")
