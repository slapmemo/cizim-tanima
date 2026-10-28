# Tanınma eşiği sorunu ve çözüm yolları

Tarih: 28 Ekim 2026. **Karar (kullanıcı): "Oyun · 242" sekmesinde birinci + ≥%30; "Oyun · 50" %50 kaldı.** Uygulandı: `demo/src/oyun.ts` `TANIMA_ESIGI_345`.

## Sorun

Oyunda bir çizim, şu iki koşul birlikte sağlanırsa tanınmış sayılır (`demo/src/oyun.ts`, `TANIMA_ESIGI = 0.5`):

1. Hedef kelime modelin birinci tahmini olmalı.
2. Hedefin olasılığı en az %50 olmalı.

Kullanıcı denemesinde "daire" birinci tahmin olarak %41 aldı. Ekranda "daire mi?" yazdı, ama çizim kabul edilmedi ve süre doldu. Oyuncu açısından bu haksız görünüyor: model doğru bildiği halde puan verilmiyor.

## Neden 345 sınıfta daha sık

- 345 sınıflı modelde benzer sınıflar çok olduğu için olasılık bu sınıflara bölünür. Örneğin bir daire çizimi için daire, saat, pizza, güneş, kurabiye. Doğru sınıf birinci olsa bile %50'ye ulaşması zorlaşır.
- 50 sınıflı modelde rakip az olduğundan aynı çizim çoğunlukla %80'in üstünde çıkar.
- Simülasyon bunu gösteriyor (rapor §4.6 ve §4.8). M3-kısmi tam çizimlerin %98,2'sini tanıyor, 345 sınıflı M3-kısmi ise %74,2'sini. Test setinde 345 sınıflı modelin ilk-1 doğruluğu %75,1, ama eşikle "oyunda tanınır" oranı daha düşük: s345_m3'te tam çizimde ilk-1 %77,3, oyunda tanınır %70,6.

## Eşik neden var

Çizimin başında, örneğin tek bir çizgi çekilmişken, model rastgele bir sınıfı %10–20 ile birinci gösterebilir. Eşik olmasa hedef kelime şans eseri birinci olduğunda oyuncu bir çizgiyle puan alır. Eşik, "model gerçekten emin mi?" sorusunu cevaplar.

## Quick, Draw! (Google) nasıl yapıyor

https://quickdraw.withgoogle.com/ incelendi. Sayfadan ve haberlerden öğrenilenler:

- Oyuncuya 6 kelime verilir, her biri 20 saniye.
- Model çizim sürerken sesli tahmin eder ("I see … or …"). Hedefi bulduğunda "Oh, I know, it's …!" der ve çizim orada kesilir.
- Bitişte her çizim için modelin ilk 3 tahmini gösterilir ("Correct match", "2nd closest match", "3rd closest match").
- Model yalnız son görüntüye bakmaz. Vuruş sırası ve yönü de girdidir. Google'ın el yazısı tanıma teknolojisine dayanır.

### Canlı istemci kodundan (REA incelemesi, `oyun-incelemeleri/quick-draw/`)

Oyunun `app.bundle.js` dosyasında (28 Ekim 2026 yakalaması) kural açıkça yazıyor:

```js
handwriting_threshold: 4,             // tahmin ekranda gösterilir: score < 4
handwriting_recognition_threshold: 2, // tur kazanılır: score < 2
round_length: 20, num_rounds: 6, max_api_rate: 1
...
n = find(adaylar, t => (t.word === tur.word || synonyms.includes(t.word)) && t.score < 2)
if (n) roundRecognized(n)
```

Bundan çıkanlar (kodda doğrudan görülen):

1. **Birinci tahmin olma şartı yok.** Sunucunun döndürdüğü aday listesinin *herhangi bir yerinde* hedef kelime varsa ve skoru eşiği geçiyorsa tur kazanılır. Bizim oyunumuz ise hedefin birinci olmasını şart koşuyor.
2. **Eş anlamlılar kabul ediliyor** (`synonyms`). Her turun kelimesiyle birlikte sunucudan kabul edilen başka kelimeler de gelir. Bu, çözüm 4'e (benzer sınıf grupları) karşılık gelir.
3. **İki eşik var:** göstermek için gevşek (`< 4`), kabul için sıkı (`< 2`).
4. Skor olasılık yüzdesi değil, **küçük olan daha iyi**. Tek gözlenen yanıtta ilk üç aday 1,08 / 2,03 / 2,32 idi. Skor −ln(olasılık) türünde bir değerse (doğrulanmadı), `< 2` yaklaşık **olasılık > %13,5** demektir. Bu, bizim %50'mizden çok daha gevşek bir sınır olur. Bu yorum tahmindir: sunucu tarafındaki modelin skor tanımı yayımlanmamış.
5. Tanıma, çizimde 10'dan fazla nokta olduktan sonra başlar ve saniyede en fazla 1 kez yapılır. Bizde her vuruş sonunda ve en fazla 250 ms'de bir yapılıyor.
6. Model sunucuda çalışır (`inputtools.google.com`, `app=quickdraw`). Bizde tarayıcıda çalışıyor.

Sonuç: Quick, Draw! bizden belirgin şekilde daha gevşek. Hedefin birinci olmasını istemiyor, eş anlamlıları kabul ediyor ve eşiği muhtemelen düşük.

Kaynaklar: `oyun-incelemeleri/quick-draw/OYUN_OZETI.md` ve `2026-10-28/inceleme.md` (REA kanıtlı), [quickdraw.withgoogle.com](https://quickdraw.withgoogle.com/), [Mental Floss](https://www.mentalfloss.com/article/88882/googles-addictive-new-app-makes-ai-guess-what-youre-doodling), [Bustle](https://www.bustle.com/articles/196717-how-does-google-quick-draw-work-this-game-makes-learning-about-artificial-intelligence-fun), [Daily Dot](https://dailydot.com/google-quick-draw-neural-network).

## Çözüm yolları

| No | Yöntem | Artı | Eksi |
| --- | --- | --- | --- |
| 1 | **Eşiği düşürmek** (yalnız 242 sekmesinde, ör. %30–35; 50 sekmesi %50 kalır) | En basit, tek sabit değişir | Erken çizimde şans eseri tanınma artar; değer elle seçilir |
| 2 | **Fark kuralı**: hedef birinci ve ikinci tahminden en az *f* puan önde (ör. %41 / %15 kabul, %41 / %38 değil) | "Model iki şey arasında kararsız" durumunu ayırır; mutlak olasılığa bağlı değil | Bir parametre daha; açıklaması biraz daha zor |
| 3 | **Süreklilik kuralı**: hedef, art arda *k* tahminde (ör. 2–3 tahmin, ~0,5–0,75 sn) birinci kalırsa kabul (eşik düşük, ör. %25) | Tek anlık şans eşleşmesini eler, Quick, Draw!'ın "emin olunca söyle" davranışına yakın | Tanınma biraz gecikir; puan hesabı etkilenir |
| 4 | **Benzer sınıf grupları**: hedefin "akrabaları"nın olasılığı hedefe eklenir (daire + saat + kurabiye …) | Olasılık bölünmesini doğrudan çözer | Gruplar elle yazılmalı; kullanıcı daha önce benzer kelimeleri kabul etmeyi istemedi |
| 5 | **Kalibrasyon (sıcaklık ölçekleme)**: olasılıklar doğrulama setine göre yeniden ölçeklenir | Olasılıklar "gerçek" güveni gösterir, eşik anlamlı olur | Sıralama değişmez; tek başına sorunu çözmez, 1–3 ile birlikte kullanılır |
| 6 | **Quick, Draw! kuralı**: hedef ilk *n* tahmin içinde (birinci olması gerekmez) ve olasılığı ≥ düşük eşik (ör. %15–20); isteğe bağlı eş anlamlılar | Gerçek oyunun yaptığı, oyuncuya cömert | En gevşek kural; erken şans eşleşmesi ölçülmeli. 345 sınıfta "kupa" sorulup "bardak" birinci olsa da kabul edilebilir |
| 7 | **Sınıf sayısını 242'ye indirmek** (durum.md "Sıradaki" 5) | Rakip az, olasılıklar yüksek | Yeni eğitim (~1 saat); model kaba çizimlerden daha kolay kandırılır |

## Önerilen ilerleyiş

1. `egitim/oyun_simulasyonu.py` ile 345 sınıflı M3-kısmi'de farklı kuralları ölçmek:
   - eşik %25 / %30 / %35 / %40 / %50,
   - fark kuralı *f* = 10 / 20 puan,
   - süreklilik *k* = 2 / 3,
   - Quick, Draw! kuralı: hedef ilk 3'te ve olasılık ≥ %15 / %20.
   Her biri için tanınan oran, ortalama tanınma anı ve **şans eseri erken tanıma** ölçülür (mürekkebin %10–20'sinde tanınma oranı). Ayrıca 229 gerçek çizimde aynı ölçüm yapılır. Birkaç dakika sürer.
2. Sayılara bakıp kullanıcıyla kural seçilir. Ön tahmin: 1 ve 3'ün birleşimi (eşik ~%30 + 2 tahmin üst üste) iyi bir denge verebilir; bu ölçülmeden önerilmez.
3. Seçilen kural `demo/src/oyun.ts` içinde, sekmeye göre ayrı parametreyle uygulanır. Rapor §4.6 ve §4.8'e "eşik seçimi" eklenir.

## Ölçüm sonuçları (28 Ekim 2026, `egitim/esik_karsilastir.py`)

Yalnız oyunda sorulan kelimeler, kelime başına 50 test çizimi. Çizimler %10'luk mürekkep adımlarıyla ilerletildi. Süreklilik kuralı (3) bu adımlarla taklit edilemediği için ölçülmedi. Tam tablolar `deneyler/esik_karsilastir.md` dosyasında.

- **Yanlış kabul:** Aynı çizime rastgele başka bir oyun kelimesi soruldu sayıldı; kuralın bunu kabul ettiği oran.
- **İlk %20'de:** Mürekkebin ilk %20'sinde tanınan oran. Şans eseri tanınma göstergesi.
- **Gerçek:** 229 arkadaş çizimi.

**Oyun · 242 (s345_m3_kismi, 12 100 çizim)**

| Kural | Tanınan | Ortalama an | İlk %20'de | Yanlış kabul | Gerçek |
| --- | ---: | ---: | ---: | ---: | ---: |
| birinci + ≥%50 (şimdiki) | %83,2 | %65 | %1,2 | %0,1 | %72,4 |
| birinci + ≥%35 | %88,1 | %62 | %2,0 | %0,3 | %76,3 |
| birinci + ≥%30 | %89,2 | %60 | %2,5 | %0,3 | %77,6 |
| birinci + ikinciden ≥10 puan önde | %88,7 | %60 | %2,8 | %0,4 | %76,8 |
| ilk 3'te + ≥%20 (Quick, Draw! benzeri) | %93,3 | %56 | %4,2 | %0,6 | %82,0 |
| ilk 3'te + ≥%15 | %94,8 | %53 | %5,8 | %0,9 | %84,2 |

**Oyun · 50 (m3_kismi, 2 500 çizim)**

| Kural | Tanınan | Ortalama an | İlk %20'de | Yanlış kabul | Gerçek |
| --- | ---: | ---: | ---: | ---: | ---: |
| birinci + ≥%50 (şimdiki) | %98,3 | %43 | %17,2 | %1,2 | %92,5 |
| birinci + ≥%30 | %98,9 | %38 | %26,4 | %2,3 | %93,0 |
| ilk 3'te + ≥%20 | %99,5 | %34 | %37,2 | %5,0 | %94,7 |

Yorum:

- 242 sekmesinde eşik gevşetildikçe tanınan oran belirgin artıyor. Şans eseri tanınma ve yanlış kabul ise %1'in altında kalıyor. Model bu sekmede zaten temkinli: çizimin ilk %20'sinde neredeyse hiçbir şeyi tanımıyor.
- 50 sekmesinde gevşetmenin yararı yok. Tanınan oran zaten %98, gevşetince yalnız erken şans tanıması artıyor (%17'den %37'ye). Bu sekme %50'de kalmalı.
- "İlk 3'te" kuralı, hedefin birinci olmasını istemiyor. Yani "kupa" sorulduğunda model "bardak" dese bile kupa ilk 3'teyse kabul ediliyor. Bu, kullanıcının daha önce istemediği "benzer kelimeleri kabul et" davranışına yakın. Karar kullanıcıda.
