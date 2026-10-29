"""Oyun kuralının Python (oyun_kurali.py) ve TypeScript (demo/src/oyun.ts) eşitlik testi için fikstür.

345 sınıflı listede rastgele olasılık vektörleri (eşdeğer grupların üyelerine ağırlık verilerek, eşiğe yakın
toplamlarla) ve hedefler üretilir; Python'un kabul kararı demo/test/kural_fikstur.json dosyasına yazılır.
`npm test` (demo/) aynı girdileri tanindiMi ile karşılaştırır.
Kullanım: .venv\\Scripts\\python.exe egitim\\kural_fikstur.py
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import oyun_kurali as ok  # noqa: E402

KOK = Path(__file__).resolve().parent.parent
ORNEK = 600


def main():
    adlar, _ = ok.sinif_listesi("345")
    g = ok.gruplar(adlar)
    rng = np.random.default_rng(7)
    gruplu = np.flatnonzero(np.bincount(g, minlength=len(g))[g] > 1)
    ornekler = []
    for i in range(ORNEK):
        p = rng.dirichlet(np.full(len(adlar), 0.05))
        uyeler = np.flatnonzero(g == g[rng.choice(gruplu)])
        if i % 2:  # bir grubun üyelerine ağırlık: toplam eşiğin çevresinde, tek üye çoğu zaman altında
            p *= rng.uniform(0.3, 0.9)
            p[uyeler] += rng.dirichlet(np.ones(len(uyeler))) * (1 - p.sum())
        hedef = int(rng.choice(uyeler)) if i % 4 in (1, 2) else int(rng.integers(len(adlar)))
        if i % 7 == 0:
            hedef = int(p.argmax())
        p = p.astype(np.float32)
        b, q = ok.adim_ozeti(p[None], g)
        kabul = bool(ok.kabul(b[None], q[None], np.array([g[hedef]]), ok.SEKMELER["zor"]["esik"])[0, 0])
        ornekler.append({"olasilik": [float(x) for x in p], "hedef": hedef, "kabul": kabul})
    cikti = {"esik": ok.SEKMELER["zor"]["esik"], "grup": g.tolist(), "ornekler": ornekler}
    (KOK / "demo" / "test" / "kural_fikstur.json").write_text(json.dumps(cikti), encoding="utf-8")
    print(f"{ORNEK} örnek, kabul {sum(o['kabul'] for o in ornekler)}")


if __name__ == "__main__":
    main()
