# Çizim Tanıma — Detaylı Sunum Metni

Her slayt için: **Slaytta** (ekrana yazılacak), **Anlatım** (söylenecek), gerekiyorsa **Hoca sorarsa**.
Sayılar `deneyler/`, `docs/durum.md` ve koddan alınmıştır.

Akış: Kapak → Amaç → Genel akış → Veri seti → Veri hazırlama → Ön işleme → Modeller → Eğitim → 50 sınıf sonuçları → Erken tanıma (2 slayt) → Gerçek kullanıcı → 345 sınıf → Tarayıcıda çalışma → Oyun → Sınırlılıklar → Sonuç → Demo

---

## 1. Kapak

**Slaytta:**
- CNN ile Gerçek Zamanlı Çizim Tanıma Oyunu
- Sinir Ağları dersi · Ad Soyad · Öğrenci No · Tarih

---

## 2. Amaç

**Slaytta:**
- Oyuncunun çizdiği nesneyi **çizim sürerken** tanıyan oyun
- Konvolüsyonel sinir ağı (CNN) ile
- **Tarayıcıda, sunucusuz** çalışır
- Erken tanıma = daha çok puan

**Anlatım:**
"Bu projede oyuncunun ekrana çizdiği nesneyi çizim bitmeden tanıyan, CNN tabanlı bir oyun geliştirdik. Oyunda bir kelime geliyor, oyuncunun 20 saniyesi var; model çizimi tanıdığı anda tur bitiyor. Puan kalan süreyle orantılı: 100 × kalan süre / 20 sn. Yani model ne kadar erken tanırsa oyuncu o kadar çok puan alıyor. Bu yüzden modelin yalnız bitmiş çizimi değil, **yarım çizimi** de tanıması gerekiyordu. Projenin asıl araştırma sorusu bu oldu."

**Hedefler:**
1. Küçük ve hızlı CNN modelleriyle yüksek doğruluk
2. Farklı mimarileri karşılaştırmak (M1, M2, M3)
3. Yarım çizimde erken tanıma
4. Modeli tarayıcıda çalıştırmak (sunucu yok)
5. Gerçek kullanıcılarla test

---

## 3. Genel akış (Nasıl yaptık?)

**Slaytta (diyagram):**
```
Quick, Draw! NDJSON (vuruşlar)
   → ayıklama + bölme (eğitim / doğrulama / test)
   → 28×28 görüntü (.npz)
   → PyTorch ile eğitim (GPU)
   → ONNX'e çevirme
   → Tarayıcıda onnxruntime-web ile oyun
```

**Anlatım:**
"İşin tamamı iki parçadan oluşuyor: Python tarafında veri hazırlama ve eğitim, tarayıcı tarafında oyun. İki tarafı bağlayan şey ONNX model dosyası ve iki dilde birebir aynı yazılmış ön işleme kodu."

---

## 4. Veri seti: Quick, Draw!

**Slaytta:**
- Google'ın çevrimiçi çizim oyunu, açık veri seti
- 345 sınıf, 50 milyondan fazla çizim
- Çizimler **resim değil, vuruş** (kalem hareketi) olarak saklanır
- Biz önce **50 sınıf** seçtik, sonra 345'e geçtik

**Anlatım:**
"Quick, Draw! Google'ın oyunu: 20 saniyede bir şey çiziyorsunuz, model tahmin ediyor. Oyuncuların çizimleri açık veri seti olarak yayınlanmış. Önemli nokta: çizimler resim olarak değil, kalemin hareketi olarak saklanıyor. Bu bizim için iyi oldu, çünkü yarım çizim üretebildik.

İlk aşamada 50 sınıf seçtik; yöntemi küçükte denemek için. Seçim ölçütlerimiz: 20 saniyede çizilebilir olması, birbirine çok benzememesi ve Türkçe adının açık olması."

---

## 5. Veri hazırlama: JSON'dan veri setine

**Slaytta:**
- Kaynak: Google Cloud Storage, `simplified/<sınıf>.ndjson`
- **NDJSON**: her satır bir JSON = bir çizim
- Yalnız `recognized: true` çizimler
- Sınıf başına **30 000 eğitim / 5 000 doğrulama / 5 000 test**
- Toplam 1,5 milyon / 250 bin / 250 bin

Örnek satır (slayta küçük konabilir):
```json
{"word":"cat","countrycode":"TR","recognized":true,
 "drawing":[[[x0,x1,...],[y0,y1,...]], [[...],[...]]]}
```

**Anlatım:**
"Veriyi Google'ın deposundan NDJSON biçiminde indirdik; her sınıf ayrı bir dosya, her satır bir JSON nesnesi, yani bir çizim. `drawing` alanı vuruşların listesi: her vuruş kalem kaldırılmadan çizilen bir çizgi ve x, y koordinatlarından oluşuyor. `simplified` sürümünü kullandık; Google koordinatları 0–255 aralığına ölçekleyip sadeleştirmiş.

50 sınıf yaklaşık 3 GB tuttu. `recognized` alanı, Google'ın kendi modelinin o çizimi tanıyıp tanımadığını gösteriyor; biz yalnız tanınanları aldık. Sonra her sınıfı sabit bir rastgelelik tohumuyla karıştırıp 30 bin eğitim, 5 bin doğrulama, 5 bin test olarak ayırdık. Her sınıfta eşit sayı var, veri dengeli."

**Üç bölümün rolü:**
- **Eğitim:** model bununla öğrenir
- **Doğrulama:** ayar ve model seçimi bununla yapılır
- **Test:** en sonda bir kez, gerçek başarıyı ölçmek için

**Hoca sorarsa:**
- *Test setini neden en sonda kullandınız?* → Seçimleri testle yaparsak test tarafsız olmaz, sonuç iyimser görünür.
- *recognized filtresinin yan etkisi?* → Kötü çizimler veride yok; test sonucu biraz iyimser olabilir. Gerçek kullanıcıdaki düşüşün bir sebebi bu olabilir.

---

## 6. Ön işleme: vuruştan 28×28 görüntüye

**Slaytta:**
1. Sınır kutusu → uzun kenar 255'e ölçeklenir (oran korunur)
2. Ramer-Douglas-Peucker ile çizgi sadeleştirme (ε = 2)
3. 28×28 tuvale ortalama (2 piksel kenar payı)
4. Piksel değeri = en yakın çizgiye uzaklık (yumuşak kenar)
- Aynı algoritma **Python** (eğitim) ve **TypeScript** (oyun) ile yazıldı
- 304 örnekte **0 farklı piksel**

**Anlatım:**
"Veri setinin hazır 28×28 numpy sürümü de var ama onu kullanmadık. Çünkü oyunda oyuncunun çizgilerini de tam aynı şekilde görüntüye çevirmemiz gerekiyordu; hazır dosyanın nasıl üretildiğini birebir kopyalayamazdık. Dönüşümü kendimiz yazdık: çizimi bir kutuya sığdırıp ölçekliyoruz, çizgileri sadeleştiriyoruz, 28×28 tuvale ortalıyoruz ve her pikselin değerini çizgiye uzaklığına göre veriyoruz.

Eğitim Python'da, oyun tarayıcıda TypeScript'te. İki kod farklı görüntü üretirse model oyunda eğitimde görmediği bir şey görür ve başarı düşer. Bu yüzden iki tarafı bir eşitlik testiyle karşılaştırdık: 304 örnekte tek bir piksel bile farklı çıkmadı."

**Çıktı:** `.npz` dosyaları (numpy): `X` (N, 28, 28) piksel, `y` sınıf numarası.

---

## 7. Modeller

**Slaytta:**

| Model | Yapı | Parametre |
|---|---|---:|
| M1 Basit CNN | 2 konvolüsyon + havuzlama + tam bağlı | 427 bin |
| M2 Derin CNN | 3 blok (2'şer konvolüsyon), BatchNorm, Dropout | 595 bin |
| M3 Hafif ResNet | Artık (residual) bağlantılı bloklar | 701 bin |
| M3-kısmi | M3 + eğitimde yarım çizim | 701 bin |

**Anlatım:**
"Mimarinin ne kadar fark yarattığını görmek için her biri bir öncekinden gelişmiş üç model kurduk. M1 taban model: iki konvolüsyon ve havuzlama katmanı, sonra tam bağlı katman. M2 daha derin; BatchNorm ve Dropout ekledik. M2'yi veri artırmalı ve artırmasız olarak iki kez eğittik. M3 küçük bir ResNet; artık bağlantılar sayesinde bilgi derin ağda kaybolmadan akıyor. M3-kısmi mimari olarak M3'ün aynısı, farkı yalnız eğitim verisinde.

Modeller bilinçli olarak küçük: 400–700 bin parametre. Çünkü tarayıcıda saniyede birkaç kez çalışacaklar."

**Kavramlar (sorulursa):**
- **Konvolüsyon:** görüntüde gezen 3×3 filtre; her filtre bir desen (çizgi, köşe, kavis) öğrenir.
- **Havuzlama:** görüntüyü küçültür (2×2'den en büyük), genel şekle bakılır.
- **BatchNorm:** katman çıktısını normalleştirir; eğitim hızlı ve kararlı olur.
- **Dropout:** eğitimde nöronların bir kısmını rastgele kapatır; ezberlemeyi azaltır.
- **Artık bağlantı:** bloğun girişi çıktısına eklenir (ResNet).

**Hoca sorarsa:**
- *Neden hazır büyük model yok?* → Tarayıcıda her 250 ms'de çalışacak; küçük ve hızlı olmalı. Giriş zaten 28×28.

---

## 8. Eğitim

**Slaytta:**
- PyTorch, RTX 5070 Ti ekran kartı
- AdamW + OneCycle öğrenme oranı (en yüksek 0,003)
- Yığın 512, 10–20 epoch, bf16 karışık hassasiyet
- Veri artırma: ±15° döndürme, 0,85–1,15 ölçek, ±2 piksel kaydırma
- En iyi **doğrulama** doğruluğundaki ağırlıklar saklandı
- Epoch süresi: M1 5 sn · M2 ~22 sn · M3 53 sn

**Anlatım:**
"Eğitimi PyTorch ile ekran kartında yaptık. Verinin tamamını ekran kartı belleğine yükledik; veri artırmayı da orada yaptık. Böylece bir epoch, yani verinin modelden bir kez tam geçmesi, M1 için 5 saniye, M3 için 53 saniye sürdü. Eniyileyici olarak AdamW, öğrenme oranı için OneCycle zamanlaması kullandık. Her epoch sonunda doğrulama setinde ölçtük ve en iyi sonucu veren ağırlıkları sakladık."

---

## 9. 50 sınıf sonuçları

**Slaytta (çubuk grafik önerilir):**

| Model | Doğruluk | Hata |
|---|---:|---:|
| M1 | %95,22 | %4,78 |
| M2 artırmasız | %97,13 | %2,87 |
| M2 artırmalı | %96,94 | %3,06 |
| M3 | **%97,43** | %2,57 |
| M3-kısmi | %96,50 | %3,50 |

Test seti: 250 000 çizim. İlk 3 tahminde doğruluk %98,8–99,5.

**Anlatım:**
1. "M1'den M2'ye hata %4,8'den %2,9'a indi, neredeyse yarıya. Derinlik, BatchNorm ve Dropout işe yarıyor."
2. "M2'den M3'e kazanç yalnız 0,3 puan, ama M3 2,5 kat yavaş. Daha karmaşık model her zaman çok daha iyi değil."
3. "Veri artırma test setinde işe yaramadı, hatta 0,2 puan düşürdü. 30 bin çizim zaten yeterince çeşitli."
4. "Dürüst olmak gerekirse her model bir kez eğitildi; 0,3 puanlık farklar kesin değil."
5. "M3-kısmi tam çizimde 0,9 puan geride. Neden onu seçtiğimizi şimdi anlatacağım."

**Hoca sorarsa:**
- *En çok karışanlar?* → ay ↔ muz (hilal), örümcek ↔ güneş, mantar ↔ şemsiye. Şekil benzerliği.
- *Aşırı öğrenme?* → M1'de biraz (eğitim %97, doğrulama %95). M2 ve M3'te eğriler yakın. (Görsel: `deneyler/egriler.png`)

---

## 10. Erken tanıma: sorun ve çözüm (en önemli bölüm)

**Slaytta (sütun grafik, `deneyler/kismi.png`):**

| Model | %25 çizim | %50 | %75 | %100 |
|---|---:|---:|---:|---:|
| M1 | %12,8 | %43,1 | %82,3 | %95,2 |
| M2 | %15,3 | %49,7 | %86,2 | %97,1 |
| M3 | %14,7 | %50,5 | %87,1 | %97,4 |
| **M3-kısmi** | **%40,2** | **%76,3** | **%91,9** | %96,5 |

**Anlatım:**
"Oyunda asıl önemli olan yarım çizim. Burada çizimin ilk %25'ini, %50'sini, %75'ini modele verdik. İlk üç model tam çizimde %97 iken ilk çeyrekte %15'e düşüyor. Sebep basit: eğitimde hiç yarım çizim görmediler. Mimari de çözmüyor; M1, M2, M3 hepsi %13–15 civarında.

Çözümü veride bulduk. Vuruş verisi elimizde olduğu için her eğitim çiziminin rastgele %20 ile %100 arasını alıp yarım bir sürüm ürettik; etiketi aynı bıraktık. Eğitimde her yığındaki örneklerin yarısını bu yarım sürümlerle değiştirdik. Sonuç: ilk çeyrekte doğruluk %15'ten %40'a, yani 2,7 katına çıktı. Bedeli tam çizimde yalnız 0,9 puan."

**Ana cümle:** "Erken tanımada belirleyici olan mimari değil, eğitim verisiydi."

**Hoca sorarsa:**
- *Neden %20–100?* → Çok küçük parça bilgi taşımaz. Başka oranlar denenmedi (sınırlılık).
- *Dezavantajı?* → Ayrıntı çizilmeden karar verdiği için benzer nesneleri (ceket/kazak) daha kolay karıştırır.

---

## 11. Erken tanıma oyunda ne kazandırdı?

**Slaytta:**

| Oyun kuralıyla (50 sınıf, test) | M3 | M3-kısmi |
|---|---:|---:|
| Tanınan çizim | %98,9 | %98,4 |
| Ortalama tur puanı | 67,4 | **74,7** |
| 60 sn'de tanınan nesne | 8,1 | **10,3** |

**Anlatım:**
"Modeli oyunun kendi kuralıyla da ölçtük; Python'da oyunun birebir kopyası bir kural yazıp test çizimlerini sanki biri çiziyormuş gibi adım adım verdik. M3 biraz daha çok çizim tanıyor ama geç tanıyor. M3-kısmi tur başına 7 puan önde, 60 saniyede 2 nesne daha fazla tanıyor. Bu yüzden oyun modelini sınıflandırma doğruluğuna göre değil, **oyun puanına** göre seçtik."

---

## 12. Gerçek kullanıcı testi

**Slaytta:**
- Ayrı çizim toplama sayfası (`/topla`), arkadaşlara link
- 5 kişi, 229 çizim (179 fare, 50 dokunmatik)
- Model tahmini kullanıcıya **gizli**

| | Test seti | Gerçek kullanıcı |
|---|---:|---:|
| M3 | %97,4 | %88,2 |
| M3-kısmi | %96,5 | %86,9 |
| M1 | %95,2 | %82,5 |

**Anlatım:**
"Test seti de Quick, Draw!'dan geliyor; gerçek bir kişi fareyle ya da telefonda farklı çiziyor. Bunu ölçmek için ayrı bir toplama sayfası yaptık. Her kişiye 50 nesne kendi rastgele sırasıyla soruldu. Model tahminini göstermedik, çünkü görse çizimini modele göre düzeltir ve sonuç iyimser çıkardı.

Veritabanı kullanmadık: çizimler kişinin cihazında Quick, Draw! ile aynı vuruş biçiminde bir JSON dosyasına yazıldı, kişi bu dosyayı bize gönderdi. Kişisel veri olduğu için adlar yerine A–E kullandık.

Sonuç: gerçek kullanıcıda doğruluk 9–13 puan düşük, ama modellerin sıralaması korunuyor."

**Hata sebepleri:**
1. Alışılmadık biçim: önden araba, rakamlı saat → pizza
2. Türkçe ad belirsizliği: "merdiven" → 3 kişi basamaklı merdiven çizdi, veri setindeki ise el merdiveni. Ad sonra "el merdiveni" yapıldı.
3. Zaten karışan sınıflar: örümcek → güneş

**Dürüstlük:** 5 kişi az. Dokunmatikte tek kişi var (%78); fareyle çizenler arasında da %75–96 fark var, yani aygıt etkisi kişi etkisinden ayrılamıyor.

**Hoca sorarsa:**
- *Veri artırma gerçek kullanıcıda işe yaradı mı?* → Hayır: artırmalı M2 %85,6, artırmasız %86,0.

---

## 13. 345 sınıfa geçiş

**Slaytta:**
- Neden: 50 sınıflı oyun çok kolaydı (2–4 sn'de tanınıyordu)
- Sınıf başına 20 000 eğitim (toplam 6,9 milyon; bellek sınırı)
- Aynı mimari, son katman 345 çıkış

| | 50 sınıf | 345 sınıf |
|---|---:|---:|
| M3 | %97,4 | %77,3 |
| M3-kısmi | %96,5 | %75,1 |
| M1 | %95,2 | %70,1 |

**En çok karışanlar (2 500 çizimde):**
doğum günü pastası → pasta 936 · kasırga → hortum 871 · keman → gitar 710 · okul otobüsü → otobüs 663 · bardak → kupa 645

**Anlatım:**
"Doğruluk %97'den %77'ye düştü. Ama sebep yeni sınıfların zor olması değil: aynı 50 sınıfın çizimleri 345 sınıflı modelde %84. Asıl sebep birbirine çok benzeyen, hatta aynı nesneyi farklı adla tutan sınıflar: pasta ile doğum günü pastası, bardak ile kupa gibi."

**Oyunda üç çözüm:**
1. **Eşdeğer gruplar (12 grup):** aynı nesnenin farklı adları birlikte kabul (bardak = kupa = kahve fincanı). Keman/gitar gibi gerçekten farklı nesneler birleştirilmedi.
2. **Eşik %50 → %30:** olasılık benzer sınıflara bölündüğü için doğru cevap birinci olsa da %41 gibi kalıyordu. Eşik doğrulama setiyle seçildi.
3. **Sorulan kelimeler:** model 345 sınıfın hepsini tanır, ama oyunda iyi tanınan 258 kelime sorulur.

Sonuç: iki oyun sekmesi, "Oyun · 50" (kolay) ve "Oyun · 258" (zor).

**Hoca sorarsa:**
- *Eşik neden %30?* → %50/40/30/25/20 denendi. Düştükçe daha çok tanınır ama yanlış kabul artar. %30 denge.
- *Model kandırılabiliyor mu?* → Rastgele hedefle kabul %0,36 (şans düzeyi %0,39). Karalamaların %0,4'ü kabul ediliyor (345 sınıfta "karalama" sınıfı var).

---

## 14. Tarayıcıda çalışma

**Slaytta (üç büyük sayı):**
- **4,3 ms** tek tahmin · **2,7 MB** model · 250 ms'nin **%2'si**
- PyTorch → ONNX → onnxruntime-web (WebAssembly)

**Anlatım:**
"Çoğu uygulama çizimi bir sunucuya gönderir. Bizde model kullanıcının tarayıcısında çalışıyor. Bunun üç faydası var: hızlı, çünkü ağ gecikmesi yok; ücretsiz, çünkü sunucu yok; gizli, çünkü çizim cihazdan çıkmıyor.

Eğitilmiş PyTorch modelini ONNX'e çevirdik. ONNX modeller için ortak bir dosya biçimi; 'modelin PDF'i' gibi düşünülebilir. Tarayıcıda onu ONNX Runtime Web ile, WebAssembly üzerinden çalıştırıyoruz. Çevirmeden sonra PyTorch ve ONNX çıktılarını karşılaştırdık; en büyük fark 0,0000006'dan küçük.

Tek tahmin 4,3 ms, ön işlemeyle birlikte yaklaşık 5 ms. Oyunda her 250 ms'de bir ve her çizgi bitince tahmin yapıyoruz; bu sürenin yalnız %2'si."

**Hoca sorarsa:**
- *Telefonda?* → Ölçülmedi (sınırlılık).
- *345 sınıfta yavaşladı mı?* → Hayır, 4,4 ms; yalnız son katman büyüdü.

---

## 15. Oyun

**Slaytta (oyun ekranı görüntüsü):**
- Vite + TypeScript, sunucusuz; Vercel'de yayında
- **5 tur modu:** tur başına 20 sn, puan = 100 × kalan süre / 20
- **60 sn seri modu:** art arda çizim, 3 ücretsiz pas, sonrası −1 puan
- **Tanınma kuralı:** birinci tahmin hedefin grubunda ve olasılık ≥ eşik (50: %50, 258: %30)
- Serbest çizim: modelin gördüğü 28×28 görüntü + ilk 5 tahmin

**Anlatım:**
"Oyun tarayıcıda çalışan bir web sayfası. Oyuncu çizerken vuruşlar toplanıyor, her 250 ms'de ön işleme ve tahmin yapılıyor. Tanınma kuralı tek bir yerde yazıldı; ölçümlerde de Python'daki birebir kopyası kullanıldı, ikisinin aynı sonucu verdiği 600 örnekle test edildi. Kelime listesi, eşdeğer gruplar ve sınıf adları JSON dosyalarında tutuluyor."

---

## 16. Sınırlılıklar ve sonraki adımlar

**Slaytta:**
1. Küçük örnek: 5 kişi, dokunmatikte 1 kişi
2. Her model bir kez eğitildi: 0,3 puanlık farklar kesin değil
3. Erken kararın bedeli: benzer nesnelerde kolay kandırılır (zor çiftlerde ortalama %33)
4. 50 sınıflı modelde "hiçbiri" sınıfı yok: karalamaların %4,5'i kabul

**Sonraki adımlar:** "hiçbiri" sınıfı · çizim sırasını kullanan RNN/Transformer ile karşılaştırma · farklı tohumlarla tekrar eğitim · telefonda hız ölçümü

**Notta (sorulursa):** veri yanlılığı (yalnız tanınmış çizimler); telefonda hız ölçülmedi.

---

## 17. Sonuç

**Slaytta:**
> Erken tanımada belirleyici olan mimari değil, eğitim verisiydi.

1. Küçük CNN'ler yeterli: 50 sınıfta %97,4, tarayıcıda ~5 ms
2. Yarım çizimle eğitim: ilk çeyrekte doğruluk 2,7 kat
3. Model, kullanılacağı kuralla ölçülmeli: oyun modeli oyun puanına göre seçildi

---

## 18. Canlı demo (~2 dk)

1. **Oyun · 50:** 1–2 tur; tahminin çizerken değiştiğini göster
2. **Oyun · 258:** bardak ya da pasta gelirse eşdeğer grup (kupa da kabul)
3. **Serbest çizim:** modelin gördüğü 28×28 görüntü, ilk 5 tahmin

**B planı:** internet yoksa `demo/` içinde `npm run dev` (http://localhost:5173). Sunumdan önce dene.

---

## Eksikler (sunumdan önce doldur)
- Kapak: ad / öğrenci no
- Vercel demo adresi
- Oyun ekranı görüntüsü
- (İsteğe bağlı) 345 sınıflı modelle gerçek kullanıcı sonucu
