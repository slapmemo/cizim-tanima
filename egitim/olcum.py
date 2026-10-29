"""Oyun ölçümü: oyunun kendi kuralıyla (oyun_kurali.py) tanınma, puan, seri skoru ve kandırılabilirlik.

Önceki oyun_simulasyonu.py ve esik_karsilastir.py'nin yerini alır; gercek_degerlendir.py'deki "oyunda tanınır"
sütunu da buraya taşındı (oyun çizimin herhangi bir anında kabul eder, yalnız bitmiş çizime bakmak yetmez).

Seçim ve son ölçüm ayrıdır:
  - doğrulama: eşik, model ve kelime listesi seçimi bu sonuçlarla yapılır,
  - test: yalnız son ölçüm; hiçbir seçimde kullanılmaz.
Çizimler mürekkebin %5'lik adımlarıyla ilerletilir (oyun_kurali.ADIMLAR).

Süre: Quick, Draw! çizimlerinde zaman yok. Bir çizimin süresi T, arkadaşlardan toplanan 228 çizimin süre dağılımından
(topla.html, süre sınırı yok) örneklenir ve tur süresiyle (20 sn) sınırlanır; mürekkep oranı f'de tanınan çizim
f·T anında tanınmış sayılır. Aynı çizime bütün modellerde aynı T verilir (eşleştirilmiş karşılaştırma).

Seri: kelimeler karışık sırayla; her kelimeye o sınıftan rastgele bir çizim. Tanınırsa f·T + 0,7 sn, tanınmazsa
oyuncu çizimi bitirip pas geçer (T + 0,3 sn); 60 sn dolunca biter. Puan = tanınan − 3'ü aşan pas.

Kandırılabilirlik (yanlış kabul):
  - rastgele hedef: çizime rastgele başka bir oyun kelimesi sorulur (önceki ölçüt). Bir yanlış tahminin rastgele
    hedefe denk gelme olasılığı 1/(K−1) olduğu için bu oran düşük çıkar; tek başına kandırılamazlığı göstermez,
  - başka kelimeyle kabul: çizimin herhangi bir anında, kendi grubundan başka bir oyun kelimesi kabul ediliyor mu
    (hedef o kelime olsaydı oyuncu yanlış çizimle puan alırdı); rastgele hedefin üst sınırı,
  - zor çiftler: doğrulamada en çok karışan oyun kelimesi çiftleri (A çizilir, B sorulur),
  - anlamsız çizimler: veri setinin "karalama" ve "çizgi" sınıfları ve rastgele üretilmiş karalamalar.

Kullanım: .venv\\Scripts\\python.exe egitim\\olcum.py [--bolum dogrulama test] [--sekme zor kolay]
Çıktı: deneyler/olcum.md, deneyler/olcum.json, deneyler/olcum_<sekme>.png
"""
import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from onisleme import ciz, kismi  # noqa: E402
import oyun_kurali as ok  # noqa: E402

# torch, onnxruntime ve matplotlib yalnız ana süreçte (fonksiyon içinde) yüklenir: Windows'ta çizim alt süreçleri
# bu dosyayı yeniden içe aktarır.

KOK = Path(__file__).resolve().parent.parent
ONBELLEK = KOK / "veri" / "olcum"
SINIF_BASI = {"345": 200, "50": 500}  # bölüm başına sınıf başı çizim
YABANCI_SINIF_BASI = 20  # kolay sekme: modelin bilmediği 295 sınıftan çizim
ANLAMSIZ_SAYI = 500
ESIKLER = [0.20, 0.25, 0.30, 0.35, 0.40, 0.50]
SERI_OYUN = 2000
ZOR_CIFT = 15
TOHUM = 1234


# ---------------------------------------------------------------- çizimler ve adım görüntüleri

def adim_resimleri(vuruslar):
    return np.stack([ciz(kismi(vuruslar, o)) for o in ok.ADIMLAR])


def _sinif_isle(arg):
    yol, bas, n = arg
    with open(yol, encoding="utf-8") as f:
        satirlar = f.read().splitlines()[bas:bas + n]
    return np.stack([adim_resimleri(json.loads(s)) for s in satirlar], 1)


def _cok_isle(vuruslar_listesi):
    return np.stack([adim_resimleri(v) for v in vuruslar_listesi], 1)


def veri_klasoru(sinif_seti):
    return KOK / "veri" / ("islenmis345" if sinif_seti == "345" else "islenmis")


def adim_verisi(bolum, sinif_seti):
    """(S, N, 28, 28) uint8 adım görüntüleri ve y (N,): her sınıftan ilk SINIF_BASI çizim (önbellekli)."""
    yol = ONBELLEK / f"adim_{sinif_seti}_{bolum}.npz"
    if not yol.exists():
        adlar, _ = ok.sinif_listesi(sinif_seti)
        n = SINIF_BASI[sinif_seti]
        klasor = veri_klasoru(sinif_seti) / f"{bolum}_vuruslar"
        with ProcessPoolExecutor(14) as havuz:
            parcalar = list(havuz.map(_sinif_isle, [(klasor / f"{a}.ndjson", 0, n) for a in adlar], chunksize=4))
        ONBELLEK.mkdir(parents=True, exist_ok=True)
        np.savez(yol, X=np.concatenate(parcalar, 1), y=np.repeat(np.arange(len(adlar)), n).astype(np.int16))
    d = np.load(yol)
    return d["X"], d["y"]


def rastgele_karalamalar(n, rng):
    """1-3 vuruşlu rastgele yürüyüşler (0-255 kutusunda); hiçbir nesneye benzemesi beklenmez."""
    cizimler = []
    for _ in range(n):
        v = []
        for _ in range(rng.integers(1, 4)):
            m = rng.integers(8, 40)
            adim = rng.normal(0, 25, (m, 2)).cumsum(0) + rng.uniform(40, 215, 2)
            adim = np.clip(adim, 0, 255).round().astype(int)
            v.append([adim[:, 0].tolist(), adim[:, 1].tolist()])
        cizimler.append(v)
    return cizimler


def anlamsiz_verisi(bolum):
    """Anlamsız çizimler: karalama ve çizgi sınıfları (345 verisinden) + rastgele karalama. {tür: (S, N, 28, 28)}"""
    yol = ONBELLEK / f"anlamsiz_{bolum}.npz"
    if not yol.exists():
        klasor = veri_klasoru("345") / f"{bolum}_vuruslar"
        rng = np.random.default_rng(TOHUM + (bolum == "test"))
        with ProcessPoolExecutor(14) as havuz:
            karalama, cizgi = havuz.map(_sinif_isle, [(klasor / "squiggle.ndjson", 0, ANLAMSIZ_SAYI),
                                                       (klasor / "line.ndjson", 0, ANLAMSIZ_SAYI)])
            parca = np.array_split(np.arange(ANLAMSIZ_SAYI), 14)
            rastgele = rastgele_karalamalar(ANLAMSIZ_SAYI, rng)
            rastgele = np.concatenate(list(havuz.map(_cok_isle, [[rastgele[i] for i in p] for p in parca])), 1)
        ONBELLEK.mkdir(parents=True, exist_ok=True)
        np.savez(yol, karalama=karalama, cizgi=cizgi, rastgele=rastgele)
    return dict(np.load(yol))


# ---------------------------------------------------------------- model çıktısı

def ozet(model, X, g):
    """Her adımda birinci tahminin grubu ve grubun toplam olasılığı: (S, N) int16, (S, N) float32."""
    from olasilik import olasiliklar
    birinci, q = zip(*(ok.adim_ozeti(olasiliklar(model, X[j]), g) for j in range(len(X))))
    return np.stack(birinci), np.stack(q)


def ozet_onbellekli(ad, anahtar, X, g):
    yol = ONBELLEK / f"ozet_{ad}_{anahtar}.npz"
    if not yol.exists():
        from olasilik import model_yukle
        b, q = ozet(model_yukle(ad), X, g)
        np.savez(yol, b=b, q=q)
    d = np.load(yol)
    return d["b"], d["q"]


# ---------------------------------------------------------------- ölçütler

def kabul_edilen_kelime(b, q, g, kelimeler, esik, kendi_grup=None):
    """Çizimin herhangi bir anında, kendi grubundan başka bir oyun kelimesi kabul ediliyor mu (N,)."""
    kelime_grubu = np.zeros(g.max() + 1, bool)
    kelime_grubu[g[kelimeler]] = True
    olur = kelime_grubu[b] & (q >= esik)
    if kendi_grup is not None:
        olur &= b != kendi_grup[None]
    return olur.any(0)


def kabul_edilen_hedef_orani(b, q, g, kelimeler, esik):
    """Her çizim için, sorulsaydı kabul edilecek oyun kelimelerinin oranı (N,) (rastgele hedefle kabul olasılığı)."""
    grup_kelime_sayisi = np.bincount(g[kelimeler], minlength=g.max() + 1)
    sayi = np.zeros(b.shape[1])
    gorulen = np.zeros((b.shape[1], g.max() + 1), bool)
    for j in range(len(b)):
        tamam = q[j] >= esik
        gorulen[np.arange(b.shape[1])[tamam], b[j][tamam]] = True
    sayi = (gorulen * grup_kelime_sayisi[None]).sum(1)
    return sayi / len(kelimeler)


def seri_benzetimi(ilk, sure, y, kelimeler, rng):
    """ilk: çizimlerin ilk kabul anı (mürekkep oranı, inf = tanınmadı); sure: çizim süresi (ms). Ortalama tanınan ve puan."""
    havuz = {k: np.flatnonzero(y == k) for k in kelimeler}
    taninan, puan = np.zeros(SERI_OYUN), np.zeros(SERI_OYUN)
    for o in range(SERI_OYUN):
        sira = rng.permutation(kelimeler)
        t, pas, n, i = 0.0, 0, 0, 0
        while True:
            c = rng.choice(havuz[sira[i % len(sira)]])
            i += 1
            if np.isfinite(ilk[c]):
                t += ilk[c] * sure[c]
                if t > ok.SERI_SURESI_MS:
                    break
                n += 1
                t += ok.TANINDI_BEKLEME_MS
            else:
                t += sure[c]
                if t > ok.SERI_SURESI_MS:
                    break
                pas += 1
                t += ok.PAS_BEKLEME_MS
        taninan[o], puan[o] = n, n - ok.SERI_PAS_CEZASI * max(0, pas - ok.SERI_PAS_HAKKI)
    return float(taninan.mean()), float(puan.mean())


def tanima_olcutleri(b, q, y, g, kelimeler, esik, sure, rng, seri=True):
    hedef = np.isin(y, kelimeler)
    b, q, y, sure = b[:, hedef], q[:, hedef], y[hedef], sure[hedef]
    ilk = ok.ilk_kabul(b, q, g[y], esik)
    ms = ilk * sure
    ilk = np.where(ms <= ok.TUR_SURESI_MS, ilk, np.inf)  # turun 20 sn'sinde tanınamayan
    t = np.isfinite(ilk)
    puan = np.where(t, ok.tur_puani(np.where(t, ilk * sure, 0)), 0)
    rastgele = np.array([rng.choice(kelimeler[g[kelimeler] != g[k]]) for k in y])
    sonuc = {
        "cizim": int(len(y)),
        "ilk1": float((b[-1] == g[y]).mean()),
        "taninan": float(t.mean()),
        "ortalama_an": float(ilk[t].mean()) if t.any() else None,
        "erken": float((ilk <= 0.2).mean()),
        "tur_puani": float(puan.mean()),
        "rastgele_hedefle_kabul": float(ok.kabul(b, q, g[rastgele], esik).any(0).mean()),
        "baska_kelimeyle_kabul": float(kabul_edilen_kelime(b, q, g, kelimeler, esik, g[y]).mean()),
        "birikimli": [float((ilk <= o).mean()) for o in ok.ADIMLAR],
        "_puan": puan, "_taninan": t,
    }
    if seri:
        sonuc["seri_taninan"], sonuc["seri_puan"] = seri_benzetimi(ilk, sure, y, kelimeler, rng)
    return sonuc


def eslestirilmis_fark(a, b, rng, n=2000):
    """İki modelin aynı çizimlerdeki değer farkının ortalaması ve %95 bootstrap aralığı."""
    d = a - b
    ort = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n)])
    return float(d.mean()), float(np.percentile(ort, 2.5)), float(np.percentile(ort, 97.5))


def zor_ciftler(sekme, adlar, g, kelimeler):
    """Doğrulamada en çok karışan (A çizimi → B tahmini) çiftler; B oyun kelimesi, A ile aynı grupta değil.
    Karışma, sekmenin iki M3 adayının (M3, M3-kısmi) ortalaması."""
    from esdeger_aday import karisiklik_matrisi
    km = np.mean([k / k.sum(1, keepdims=True) for k in map(karisiklik_matrisi, ok.SEKMELER[sekme]["adaylar"][-2:])], 0)
    ayni = g[:, None] == g[None, :]
    km[ayni] = 0
    km[:, ~np.isin(np.arange(len(adlar)), kelimeler)] = 0
    sira = np.argsort(-km, None)[:ZOR_CIFT]
    return [(int(i), int(j), float(km[i, j])) for i, j in zip(*np.unravel_index(sira, km.shape))]


# ---------------------------------------------------------------- ana akış

def gercek_yukle():
    from gercek_degerlendir import yukle
    return yukle()


def sure_ornekle(n, rng):
    sureler = np.array([c["sure_ms"] for c in gercek_yukle()[0] if c.get("sure_ms")], float)
    return np.minimum(rng.choice(sureler, n), ok.TUR_SURESI_MS), sureler


def bolum_olc(sekme, bolum, sonuc):
    ayar = ok.SEKMELER[sekme]
    adlar, tr = ok.sinif_listesi(ayar["sinif_seti"])
    g = ok.gruplar(adlar)
    kelimeler = ok.oyun_kelimeleri(sekme, adlar)
    X, y = adim_verisi(bolum, ayar["sinif_seti"])
    rng = np.random.default_rng(TOHUM)
    sure, _ = sure_ornekle(len(y), rng)
    anlamsiz = anlamsiz_verisi(bolum)
    cikti = sonuc.setdefault(sekme, {}).setdefault(bolum, {"modeller": {}, "kelime": int(len(kelimeler))})
    ciftler = zor_ciftler(sekme, adlar, g, kelimeler)
    cikti["zor_ciftler"] = [{"A": tr[adlar[i]], "B": tr[adlar[j]], "dogrulama_karisma": o} for i, j, o in ciftler]
    if sekme == "kolay":  # modelin bilmediği nesneler: 345 verisinden, 50 listesinde olmayan sınıflar
        X345, y345 = adim_verisi(bolum, "345")
        adlar345, _ = ok.sinif_listesi("345")
        sec = np.flatnonzero(~np.isin(np.array(adlar345)[y345], adlar) & (np.arange(len(y345)) % SINIF_BASI["345"] < YABANCI_SINIF_BASI))
        yabanci = X345[:, sec]
        del X345
    for ad in ayar["adaylar"]:
        b, q = ozet_onbellekli(ad, f"{sekme}_{bolum}", X, g)
        m = cikti["modeller"].setdefault(ad, {})
        m["esikler"] = {}
        for esik in ESIKLER:
            r = tanima_olcutleri(b, q, y, g, kelimeler, esik, sure, np.random.default_rng(TOHUM), seri=esik == ayar["esik"])
            if esik == ayar["esik"]:
                m.update(r)
            m["esikler"][str(esik)] = {k: v for k, v in r.items() if k in ("taninan", "ortalama_an", "erken", "tur_puani", "baska_kelimeyle_kabul")}
        # kelime olmayan sınıfların çizimleri (oyunda sorulmayan nesne çizildiğinde bir kelime kabul ediliyor mu)
        disari = ~np.isin(y, kelimeler)
        if disari.any():
            m["sorulmayan_nesneyle_kabul"] = float(kabul_edilen_kelime(b[:, disari], q[:, disari], g, kelimeler, ayar["esik"]).mean())
        if sekme == "kolay":
            bb, qq = ozet_onbellekli(ad, f"yabanci_{bolum}", yabanci, g)
            m["bilinmeyen_nesneyle_kabul"] = float(kabul_edilen_kelime(bb, qq, g, kelimeler, ayar["esik"]).mean())
            m["bilinmeyen_nesne_hedef_orani"] = float(kabul_edilen_hedef_orani(bb, qq, g, kelimeler, ayar["esik"]).mean())
        m["anlamsiz"] = {}
        for tur, Xa in anlamsiz.items():
            bb, qq = ozet_onbellekli(ad, f"anlamsiz_{tur}_{bolum}", Xa, g)
            m["anlamsiz"][tur] = {
                "en_az_bir_kelime": float(kabul_edilen_kelime(bb, qq, g, kelimeler, ayar["esik"]).mean()),
                "rastgele_hedef": float(kabul_edilen_hedef_orani(bb, qq, g, kelimeler, ayar["esik"]).mean()),
            }
        m["zor_ciftler"] = []
        for i, j, _ in ciftler:
            s = y == i
            m["zor_ciftler"].append(float(ok.kabul(b[:, s], q[:, s], np.full(s.sum(), g[j]), ayar["esik"]).any(0).mean()))
        print(f"{sekme} {bolum} {ad}: tanınan {m['taninan']:.1%}, tur puanı {m['tur_puani']:.1f}, "
              f"seri {m['seri_puan']:.2f}, başka kelimeyle kabul {m['baska_kelimeyle_kabul']:.1%}", flush=True)
    # eşleştirilmiş karşılaştırma: oyun modeli ile diğer adaylar
    rng = np.random.default_rng(TOHUM)
    esas = cikti["modeller"][ayar["model"]]
    for ad, m in cikti["modeller"].items():
        if ad != ayar["model"]:
            m["fark_tur_puani"] = eslestirilmis_fark(m["_puan"], esas["_puan"], rng)
            m["fark_taninan"] = eslestirilmis_fark(m["_taninan"].astype(float), esas["_taninan"].astype(float), rng)


def gercek_olc(sekme, sonuc):
    """Arkadaşlardan toplanan çizimler: yalnız sekmede sorulan kelimeler; süre çizimin kendi süresi."""
    ayar = ok.SEKMELER[sekme]
    adlar, _ = ok.sinif_listesi(ayar["sinif_seti"])
    g = ok.gruplar(adlar)
    kelimeler = ok.oyun_kelimeleri(sekme, adlar)
    cizimler, _ = gercek_yukle()
    y_tum = np.array([adlar.index(c["etiket"]) for c in cizimler])
    sec = np.isin(y_tum, kelimeler)
    secilen = [c for c, s in zip(cizimler, sec) if s]
    X = _cok_isle([c["vuruslar"] for c in secilen])
    y = y_tum[sec]
    # topla.html'de süre sınırı yok; oyundaki gibi 20 sn ile sınırlanır
    sure = np.minimum([c.get("sure_ms") or ok.TUR_SURESI_MS for c in secilen], ok.TUR_SURESI_MS).astype(float)
    cikti = sonuc.setdefault(sekme, {}).setdefault("gercek", {"modeller": {}, "toplam_cizim": len(cizimler), "cizim": int(sec.sum())})
    from olasilik import model_yukle
    for ad in ayar["adaylar"]:
        b, q = ozet(model_yukle(ad), X, g)
        r = tanima_olcutleri(b, q, y, g, kelimeler, ayar["esik"], sure, np.random.default_rng(TOHUM), seri=False)
        cikti["modeller"][ad] = r


def yuzde(x, n=1):
    return "-" if x is None else f"%{x * 100:.{n}f}"


def rapor(sonuc):
    md = ["# Oyun ölçümü", "", "`egitim/olcum.py` çıktısı; ölçütler betiğin başında. Doğrulama: seçim (eşik, model, kelime listesi); "
          "test: son ölçüm. Mürekkep %5 adımlarla; süre arkadaş çizimlerinin süre dağılımından (≤ 20 sn).", ""]
    for sekme, bolumler in sonuc.items():
        if not isinstance(bolumler, dict) or sekme.startswith("_"):
            continue
        ayar = ok.SEKMELER[sekme]
        md += [f"## Sekme {sekme} (oyun modeli {ayar['model']}, eşik %{ayar['esik'] * 100:.0f})", ""]
        for bolum in ("dogrulama", "test", "gercek"):
            if bolum not in bolumler:
                continue
            b = bolumler[bolum]
            ilk = next(iter(b["modeller"].values()))
            baslik = {"dogrulama": "Doğrulama", "test": "Test", "gercek": "Gerçek kullanıcı çizimleri"}[bolum]
            md += [f"### {baslik} ({ilk['cizim']} çizim" + (f", {b['kelime']} kelime" if "kelime" in b else
                   f"; toplam {b['toplam_cizim']}, {b['toplam_cizim'] - b['cizim']} çizimin kelimesi bu sekmede sorulmuyor") + ")", ""]
            seri = bolum != "gercek"
            md += ["| Model | İlk-1 (grup) | Tanınan | Ort. an | İlk %20'de | Tur puanı | " + ("Seri tanınan | Seri puan | " if seri else "")
                   + "Rastgele hedefle kabul | Başka kelimeyle kabul |",
                   "| --- | ---: | ---: | ---: | ---: | ---: | " + ("---: | ---: | " if seri else "") + "---: | ---: |"]
            for ad, m in b["modeller"].items():
                md.append(f"| {ad}{' (oyun)' if ad == ayar['model'] else ''} | {yuzde(m['ilk1'])} | {yuzde(m['taninan'])} | "
                          f"{yuzde(m['ortalama_an'], 0)} | {yuzde(m['erken'])} | {m['tur_puani']:.1f} | "
                          + (f"{m['seri_taninan']:.2f} | {m['seri_puan']:.2f} | " if seri else "")
                          + f"{yuzde(m['rastgele_hedefle_kabul'], 2)} | {yuzde(m['baska_kelimeyle_kabul'])} |")
            farklar = [(ad, m) for ad, m in b["modeller"].items() if "fark_tur_puani" in m]
            if farklar:
                md += ["", f"Eşleştirilmiş fark ({ayar['model']}'e göre, %95 bootstrap aralığı): "
                       + "; ".join(f"{ad} tur puanı {m['fark_tur_puani'][0]:+.1f} [{m['fark_tur_puani'][1]:+.1f}, {m['fark_tur_puani'][2]:+.1f}], "
                                   f"tanınan {m['fark_taninan'][0] * 100:+.1f} puan [{m['fark_taninan'][1] * 100:+.1f}, {m['fark_taninan'][2] * 100:+.1f}]"
                                   for ad, m in farklar)]
            md.append("")
            if bolum == "gercek":
                continue
            md += [f"Eşik karşılaştırması ({baslik.lower()}):", "",
                   "| Model | Eşik | Tanınan | Ort. an | İlk %20'de | Tur puanı | Başka kelimeyle kabul |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
            for ad, m in b["modeller"].items():
                for e, r in m["esikler"].items():
                    md.append(f"| {ad} | %{float(e) * 100:.0f}{' ←' if float(e) == ayar['esik'] else ''} | {yuzde(r['taninan'])} | "
                              f"{yuzde(r['ortalama_an'], 0)} | {yuzde(r['erken'])} | {r['tur_puani']:.1f} | {yuzde(r['baska_kelimeyle_kabul'])} |")
            md += ["", f"Anlamsız çizimler ve sorulmayan nesneler ({baslik.lower()}, eşik %{ayar['esik'] * 100:.0f}): "
                   "\"en az bir kelime\" = çizimin herhangi bir anında bir oyun kelimesi kabul ediliyor; \"rastgele hedef\" = rastgele sorulan kelimenin kabul olasılığı.", "",
                   "| Model | Karalama: en az bir / rastgele | Çizgi | Rastgele karalama (üretilmiş) | Sorulmayan nesne: en az bir | Bilinmeyen nesne (kolay sekme) |",
                   "| --- | ---: | ---: | ---: | ---: | ---: |"]
            for ad, m in b["modeller"].items():
                a = m["anlamsiz"]
                hucre = lambda t: f"{yuzde(a[t]['en_az_bir_kelime'])} / {yuzde(a[t]['rastgele_hedef'], 2)}"
                md.append(f"| {ad} | {hucre('karalama')} | {hucre('cizgi')} | {hucre('rastgele')} | "
                          f"{yuzde(m.get('sorulmayan_nesneyle_kabul'))} | "
                          + (f"{yuzde(m['bilinmeyen_nesneyle_kabul'])} / {yuzde(m['bilinmeyen_nesne_hedef_orani'], 2)}" if "bilinmeyen_nesneyle_kabul" in m else "-") + " |")
            md += ["", f"Zor çiftler ({baslik.lower()}): A çizilir, B sorulur; kabul oranı. Çiftler doğrulama karışıklığından.", "",
                   "| A → B | Doğrulama karışması | " + " | ".join(b["modeller"]) + " |", "| --- | ---: |" + " ---: |" * len(b["modeller"])]
            for k, c in enumerate(b["zor_ciftler"]):
                md.append(f"| {c['A']} → {c['B']} | {yuzde(c['dogrulama_karisma'])} | " + " | ".join(yuzde(m["zor_ciftler"][k]) for m in b["modeller"].values()) + " |")
            md.append("")
    (KOK / "deneyler" / "olcum.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def sekil(sonuc):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for sekme, bolumler in sonuc.items():
        fig, ax = plt.subplots(figsize=(6, 4))
        for bolum, cizgi in (("test", "-"), ("dogrulama", ":")):
            for n, (ad, m) in enumerate(bolumler.get(bolum, {}).get("modeller", {}).items()):
                ax.plot([o * 100 for o in ok.ADIMLAR], m["birikimli"], cizgi, color=f"C{n}",
                        label=f"{ad} ({'test' if bolum == 'test' else 'doğrulama'})")
        ayar = ok.SEKMELER[sekme]
        ax.set_xlabel("Çizimin tamamlanan kısmı (%)"); ax.set_ylabel("O ana kadar tanınmış çizim oranı")
        ax.set_title(f"{sekme} sekme ({bolumler['test']['kelime']} kelime, eşik %{ayar['esik'] * 100:.0f}): oyun kuralıyla tanınma")
        ax.grid(alpha=.3); ax.legend(fontsize=7)
        fig.tight_layout(); fig.savefig(KOK / "deneyler" / f"olcum_{sekme}.png", dpi=110); plt.close(fig)


def temizle(x):
    if isinstance(x, dict):
        return {k: temizle(v) for k, v in x.items() if not k.startswith("_")}
    return x


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--bolum", nargs="+", default=["dogrulama", "test"])
    a.add_argument("--sekme", nargs="+", default=["zor", "kolay"])
    a.add_argument("--gercek", action=argparse.BooleanOptionalAction, default=True)
    args = a.parse_args()
    sonuc = {}
    for sekme in args.sekme:
        for bolum in args.bolum:
            bolum_olc(sekme, bolum, sonuc)
        if args.gercek:
            gercek_olc(sekme, sonuc)
    rapor(sonuc)
    sekil(sonuc)
    (KOK / "deneyler" / "olcum.json").write_text(json.dumps(temizle(sonuc), indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
