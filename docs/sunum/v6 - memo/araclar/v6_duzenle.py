import re, sys, html as H
src, dst = sys.argv[1], sys.argv[2]
t = open(src, encoding="utf-8").read()
secs = [m.start() for m in re.finditer(r'<section class="deck-slide"', t)]
end = t.index("</section>", secs[-1]) + len("</section>")
bol = [t[a:b] for a, b in zip(secs, secs[1:] + [end])]
bas, son = t[:secs[0]], t[end:]
assert len(bol) == 36


def tek(s, a, b):
    assert s.count(a) == 1, (a[:60], s.count(a))
    return s.replace(a, b)


# --- 30: son cümle
bol[29] = tek(bol[29], "Performans değerlendirmesi, 50 sınıflı modeller kullanılarak gerçekleştirildi.",
              "Performans önce 50 sınıflı, sonra 345 sınıflı modellerle değerlendirildi.")

# --- 31'den yeni slayt
s31 = bol[30]


def stil(yol):
    m = re.search(r'data-node-path="%s" (?:role="[^"]*" aria-level="\d" )?style="([^"]*)"' % re.escape(yol), s31)
    return m.group(1)


def hucre_stili(k):
    return re.search(r'data-cell="%s" style="([^"]*)"' % re.escape(k), s31).group(1)


st_par, st_h3, st_govde, st_etiket = stil("1.0.1"), stil("1.0.2.0"), stil("1.0.2.1"), stil("1.1.0")
kart_st = ("display: flex; flex-direction: column; align-items: stretch; gap: 8px; min-width: 0px; min-height: 0px; "
           "background-color: rgb(251, 249, 244); padding: 24px 32px; border-width: 2px; border-style: solid; "
           "border-color: rgb(214, 205, 184); border-radius: 20px; box-sizing: border-box; flex-shrink: 0;")
kart_etiket = ("font-family: Rubik, Arial, ui-sans-serif, system-ui, sans-serif; font-size: 24px; font-weight: 800; "
               "line-height: 1.4; color: rgb(168, 72, 26); margin: 0px; white-space: pre-wrap; overflow-wrap: break-word; "
               "min-width: 0px; flex-shrink: 0; letter-spacing: 1px;")
kart_sayi = ("font-family: Rubik, Arial, ui-sans-serif, system-ui, sans-serif; font-size: 52px; font-weight: 700; "
             "line-height: 1.1; color: rgb(28, 33, 66); margin: 0px; white-space: pre-wrap; min-width: 0px; flex-shrink: 0;")

tablo_st = stil("1.0.0")
tablo_st = re.sub(r"grid-template-columns: [^;]+;", "grid-template-columns: 31fr 23fr 23fr 23fr;", tablo_st)
tablo_st = tablo_st.replace("min-width: 640px", "min-width: 1000px").replace("max-width: 640px", "max-width: 1000px")
satirlar = [("Model", "Veri seti doğruluğu", "Kullanıcı doğruluğu", "Oyunda tanınan"),
            ("M3", "%77,3", "%69,4", "%80,6"), ("M3-kısmi", "%75,1", "%69,4", "%80,6"), ("M1", "%70,1", "%63,0", "%75,5")]
hucreler = []
for r, sat in enumerate(satirlar):
    for c, v in enumerate(sat):
        if r == 0:
            s = hucre_stili("0.1") if c else hucre_stili("0.0")
        else:
            s = hucre_stili("1.0") if c == 0 else (hucre_stili("1.2") if c == 2 else hucre_stili("1.1"))
        hucreler.append(f'<div data-cell="{r}.{c}" style="{s}">{v}</div>')
tablo = f'<div data-node-path="1.0.0" style="{tablo_st}">' + "".join(hucreler) + "</div>"


def d(yol, st, ic, rol=""):
    return f'<div data-text-path="{yol}" data-node-path="{yol}"{rol} style="{st}">{ic}</div>'


sol = ('<div data-node-path="1.0" style="display: flex; flex-direction: column; align-items: stretch; gap: 24px; '
       'min-width: 1000px; min-height: 0px; max-width: 1000px;">'
       + tablo
       + d("1.0.1", st_par, "Aynı 5 katılımcının 229 çiziminden 216'sı değerlendirildi; 13 çizimin nesnesi 258 nesneli oyun "
                            "listesinde yer almıyor. Kullanıcı doğruluğunda eşdeğer sınıflar doğru kabul edildi "
                            "(örneğin araba yerine polis arabası). Oyunda tanınan: birinci tahmin hedefle eşleşir ve olasılık en az %30.")
       + '<div data-node-path="1.0.2" style="display: flex; flex-direction: column; align-items: stretch; gap: 12px; '
         'min-width: 0px; min-height: 0px; flex-shrink: 0;">'
       + d("1.0.2.0", st_h3, "Sıralama değişmedi", ' role="heading" aria-level="3"')
       + d("1.0.2.1", st_govde, "345 sınıfta da M3 ve M3-kısmi önde, M1 geride. Doğruluk düşse de oyunda tanınma oranı "
                                "%75'in üzerinde kaldı.")
       + "</div></div>")


def kart(i, etiket, sayi):
    return (f'<div data-node-path="1.1.{i}" style="{kart_st}">' + d(f"1.1.{i}.0", kart_etiket, etiket)
            + d(f"1.1.{i}.1", kart_sayi, sayi) + "</div>")


sag = ('<div data-node-path="1.1" style="display: flex; flex-direction: column; align-items: stretch; gap: 20px; '
       'min-width: 0px; min-height: 0px; flex-grow: 1; flex-basis: 0%;">'
       + d("1.1.0", re.sub(r"color: [^;]+;", "color: rgb(28, 33, 66);", st_etiket), "M3-kısmi · 50 sınıftan 345 sınıfa")
       + kart(1, "KULLANICI DOĞRULUĞU", "%86,9 → %69,4")
       + kart(2, "OYUNDA TANINAN", "%93,0 → %80,6")
       + kart(3, "ORTALAMA TUR PUANI", "73,3 → 58,4")
       + "</div>")

i0 = s31.index('<div data-node-path="1" ')
govde_ac = re.match(r'<div data-node-path="1" style="[^"]*">', s31[i0:]).group(0)
kapanis = "</div></div></div></div></div></div></section>"
ara = s31[len(s31.rstrip()):]
assert s31.rstrip().endswith(kapanis), s31[-120:]
ust = s31[:i0]
ust = tek(ust, ">06 · GERÇEK KULLANICI TESTİ • SONUÇLAR<", ">06 · GERÇEK KULLANICI TESTİ • 345 SINIF<")
ust = tek(ust, ">Gerçek Kullanıcı Çizimlerinde Model Performansı<", ">Aynı Çizimler, 345 Sınıflı Modellerle<")
ust = re.sub(r'data-label="[^"]*"', 'data-label="Aynı Çizimler, 345 Sınıflı Modellerle"', ust, count=1)
notlar = ("Aynı arkadaş çizimlerini 345 sınıflı modellerle de ölçtük. 229 çizimin 216'sı oyunun 258 nesneli listesinde. "
          "Kullanıcı doğruluğu eşdeğer gruplarla sayıldı; grupsuz M3-kısmi %68,6, fark çok küçük. "
          "Dikkat: veri seti sütunu 345 sınıfın hepsinde ve grupsuz, kullanıcı sütunu yalnız 258 nesnede ve gruplu; "
          "birebir karşılaştırılamaz. Oyunda tanınan: oyun kuralıyla, birinci tahmin hedef grubunda ve olasılık en az %30. "
          "50 sınıftan 345'e geçince M3-kısmi kullanıcı doğruluğu %86,9'dan %69,4'e, oyunda tanınma %93,0'dan %80,6'ya "
          "düştü; sıralama aynı kaldı.")
ust = re.sub(r'data-speaker-notes="[^"]*"', 'data-speaker-notes="%s"' % H.escape(notlar, quote=True), ust, count=1)
yeni = ust + govde_ac + sol + sag + kapanis + ara

# --- 36: dördüncü madde
s36 = bol[35]
m = re.search(r'<div data-node-path="1\.0\.2" style="[^"]*">.*?Serbest Çizim</div><div [^>]*>[^<]*</div></div></div>', s36, re.S)
blok = m.group(0)
yeni_blok = blok.replace('"1.0.2', '"1.0.3').replace(">3<", ">4<").replace(">Serbest Çizim<", ">Pratik<")
yeni_blok = re.sub(r">Modelin işlediği 28×28[^<]*<",
                   ">Süre ve puan olmadan rastgele bir nesne çizin, model çizerken tahmin etsin. “Örnek çiz” ile veri "
                   "setinden gerçek bir çizimi izleyin, modeller arasında geçiş yaparak sonuçları karşılaştırın.<", yeni_blok)
assert yeni_blok.count(">4<") == 1 and "Pratik" in yeni_blok
s36 = s36.replace(blok, blok + yeni_blok, 1)
s36 = s36.replace("padding: 32px 36px; border-width: 2px; border-style: solid; border-color: rgb(58, 65, 117)",
                  "padding: 24px 32px; border-width: 2px; border-style: solid; border-color: rgb(58, 65, 117)")
s36 = tek(s36, "align-items: stretch; gap: 22px; min-width: min-content", "align-items: stretch; gap: 16px; min-width: min-content")
bol[35] = s36

bol = bol[:31] + [yeni] + bol[31:]
for i, s in enumerate(bol):
    s = re.sub(r'id="\d+"', f'id="{i + 1}"', s, count=1)
    s = re.sub(r'aria-label="Slide \d+ of \d+"', f'aria-label="Slide {i + 1} of {len(bol)}"', s, count=1)
    bol[i] = s
open(dst, "w", encoding="utf-8", newline="").write(bas + "".join(bol) + son)
print("slayt:", len(bol))
