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

# --- 31'in kopyası: 345 sınıflı modellerle aynı çizimler
import base64, os
GORSEL = os.environ["GORSEL"]
def uri(ad):
    return "data:image/png;base64," + base64.b64encode(open(os.path.join(GORSEL, ad), "rb").read()).decode()
yeni = bol[30]
yeni = tek(yeni, ">06 · GERÇEK KULLANICI TESTİ • SONUÇLAR<", ">06 · GERÇEK KULLANICI TESTİ • 345 SINIF<")
yeni = tek(yeni, ">Gerçek Kullanıcı Çizimlerinde Model Performansı<", ">345 Sınıflı Modellerde Kullanıcı Performansı<")
yeni = re.sub(r'data-label="[^"]*"', 'data-label="345 Sınıflı Modellerde Kullanıcı Performansı"', yeni, count=1)
notlar = ("Aynı arkadaş çizimlerini 345 sınıflı modellerle de ölçtük. 229 çizimin 216'sı oyunun 258 nesneli listesinde; "
          "kalan 13'ünün nesnesi oyunda sorulmuyor. Kullanıcı doğruluğu eşdeğer gruplarla sayıldı; grupsuz M3-kısmi %68,6, fark çok küçük. "
          "Dikkat: veri seti sütunu 345 sınıfın hepsinde ve grupsuz, kullanıcı sütunu yalnız 258 nesnede ve gruplu; birebir karşılaştırılamaz. "
          "Oyun kuralıyla (birinci tahmin hedef grubunda, olasılık en az %30) M3 ve M3-kısmi çizimlerin %80,6'sını tanıdı. "
          "Sağ altta: 50 sınıflı modelin doğru bildiği bu dört çizim 345 sınıfta yakın bir sınıfa kaydı: kedi kaplana, balık köpek balığına, "
          "bisiklet motosiklete, örümcek yengece. 50 sınıfta kaplan, köpek balığı, motosiklet, yengeç yoktu.")
yeni = re.sub(r'data-speaker-notes="[^"]*"', 'data-speaker-notes="%s"' % H.escape(notlar, quote=True), yeni, count=1)
for a, b in (("%97,4", "%77,3"), ("%88,2", "%69,4"), ("%96,5", "%75,1"), ("%86,9", "%69,4"), ("%95,2", "%70,1"), ("%82,5", "%63,0")):
    yeni = yeni.replace(">" + a + "<", ">" + b + "<", 1)
yeni = tek(yeni, ">5 katılımcıdan toplam 229 çizim toplandı. Çizimlerin 179'u fare, 50'si dokunmatik ekran ile oluşturuldu. Doğruluk oranları 9–13 yüzde puan düşmesine rağmen modellerin başarı sıralaması değişmedi.<",
           ">Aynı 229 çizimden, nesnesi 258 nesneli oyunda yer alan 216'sı değerlendirildi; eşdeğer sınıflar doğru kabul edildi. Oyun kuralıyla (%30 eşik) M3 ve M3-kısmi çizimlerin %80,6'sını tanıdı. Sıralama yine değişmedi.<")
yeni = tek(yeni, ">Eğitim verisinden farklı çizim biçimleri (rakamlı saat, önden çizilen araba) ve Türkçe nesne adlarının farklı yorumlanması (merdiven) doğruluk kaybına neden olmuş olabilir.<",
           ">345 sınıfta birbirine çok benzeyen nesneler var. 50 sınıflı modelin doğru tanıdığı çizimlerin bir kısmı kaplan, köpek balığı, motosiklet gibi yakın sınıflara kaydı.<")
srcs = re.findall(r'src="(data:image/[^"]+)"', yeni)
assert len(srcs) == 2
yeni = yeni.replace(srcs[0], uri("k345-dogru.png"), 1).replace(srcs[1], uri("k345-yanlis.png"), 1)
yeni = re.sub(r'alt="Arkadaşların doğru tanınan[^"]*"', 'alt="345 sınıflı modelin doğru tanıdığı arkadaş çizimleri: elma, salyangoz, kelebek, ağaç"', yeni)
yeni = re.sub(r'alt="Arkadaşların yanlış tanınan[^"]*"', 'alt="345 sınıflı modelin yakın sınıfa kaydırdığı çizimler: kedi, balık, bisiklet, örümcek"', yeni)
for a, b in (("<b>bisiklet</b> %100 · A", "<b>elma</b> %100 · A"), ("<b>uçak</b> %100 · C", "<b>salyangoz</b> %100 · B"),
             ("<b>kedi</b> %86 · A", "<b>kelebek</b> %100 · C"), ("<b>şemsiye</b> %100 · A", "<b>ağaç</b> %100 · E"),
             ("saat → <b>pizza</b> · B", "kedi → <b>kaplan</b> · A"), ("araba → <b>pizza</b> · D", "balık → <b>köpek balığı</b> · B"),
             ("örümcek → <b>güneş</b> · C", "bisiklet → <b>motosiklet</b> · E"), ("merdiven → <b>şimşek</b> · B", "örümcek → <b>yengeç</b> · E")):
    yeni = tek(yeni, ">" + a + "<", ">" + b + "<")

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
