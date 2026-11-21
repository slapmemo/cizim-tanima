# Sunum konuşma notları (birlikte hazırlanıyor)

Sıra: 1 Amaç · 2 Veri seti · 3 Modeller · 4 50 sınıf sonuçları · 5 Erken tanıma ve M3-kısmi · 6 345 sınıf · 7 Gerçek kullanıcı, tarayıcı, sonuç, demo

## 1. Amaç

**Söylenecek:** "Bu projede, oyuncunun ekrana çizdiği nesneyi çizim sürerken tanıyan, tarayıcıda sunucusuz çalışan, evrişimli sinir ağı (CNN) tabanlı bir çizim oyunu geliştirdik."

- Oyun: kelime gelir, oyuncu 20 sn içinde çizer, model tanıyınca tur biter. Puan = 100 × kalan süre / 20 sn.
- Neden anlık: erken tanıma = puan. Model yarım çizimi de tanımalı. Bunun için eğitime yarım çizim ekledik (ayrıntısı 5. bölümde).

**Görsel:** oyun ekranı görüntüsü (yarım çizim + "kedi mi? %62").

**Hoca sorarsa:**
- Neden anlık? → Oyunda erken tanıma puan demek; yarım çizimle eğittik.
- Tarayıcıda nasıl? → Model ONNX'e çevrildi, tarayıcıda tek tahmin ~5 ms.
- CNN nedir? → Görüntüde küçük filtrelerle çizgi, köşe, kavis gibi desenleri yakalayan sinir ağı. Çizimi 28×28 görüntüye çevirip veriyoruz.

## 2. Veri seti

- Quick, Draw!: Google'ın çevrimiçi oyunu; 20 sn'de çiz, model tahmin etsin. Oyuncuların çizimleri açık veri seti: 345 sınıf, 50 milyondan fazla çizim.
- Çizimler resim değil, kalem hareketi (vuruş, stroke) olarak saklanıyor.
- `recognized`: Google'ın modeli tanıyabilmiş mi. Yalnız tanınanları kullandık (sınırlılık: kötü çizimler veride yok).
- Önce 50 sınıf: yöntemi küçükte denemek için. Ölçütler: 20 sn'de çizilebilir, birbirine benzemeyen, Türkçe adı açık.
- Bölme (sınıf başına): 30 000 eğitim / 5 000 doğrulama / 5 000 test.
  - Eğitim: model öğrenir. Doğrulama: ayar ve model seçimi. Test: en sonda bir kez, gerçek başarı.
- Hazır 28×28 görüntüler kullanılmadı: oyunda aynı dönüşüm yapılamazdı. Vuruştan görüntüye tek algoritma yazıldı, Python (eğitim) ve TypeScript (oyun) birebir aynı; 304 örnekte 0 farklı piksel.

**Hoca sorarsa:**
- Test setini neden en sonda kullandınız? → Seçimi testle yaparsak test tarafsız olmaz, sonuç iyimser görünür.
- Sınıflar dengeli mi? → Evet, her sınıfta eşit sayı.

## 3. Modeller

Amaç: yapının (mimarinin) ne kadar fark yarattığını görmek. Üç model, her biri bir öncekinden gelişmiş.

**Kavramlar:**
- Evrişim (convolution): görüntüde gezen küçük filtre (3×3); her filtre bir desen (çizgi, köşe, kavis) öğrenir.
- Havuzlama (pooling): görüntüyü küçültür (2×2'den en büyük), genel şekle bakılır.
- Parametre: modelin öğrendiği sayılar. Bizimkiler 400–700 bin, çok küçük; tarayıcıda hızlı.
- BatchNorm: katman çıktısını normalleştirir; eğitim hızlı ve kararlı.
- Dropout: eğitimde nöronların bir kısmını rastgele kapatır; ezberi (aşırı öğrenme, overfitting) azaltır.
- Veri artırma: eğitim görüntülerini rastgele döndürme (±15°), ölçekleme, kaydırma.
- Artık bağlantı (residual): bloğun girişi çıktısına eklenir; derin ağda bilgi kaybolmadan akar (ResNet).
- Epoch: eğitim verisinin modelden bir kez tam geçmesi.

**Modeller:**
- M1 Basit CNN (427 bin): 2 evrişim + havuzlama, tam bağlı katman. Taban model.
- M2 Derin CNN (595 bin): daha çok evrişim, BatchNorm, Dropout. Artırmalı ve artırmasız iki kez eğitildi.
- M3 Hafif ResNet (701 bin): artık bağlantılı küçük ResNet.
- M3-kısmi (701 bin): M3 ile aynı mimari, eğitimde yarım çizimler de var (5. bölüm).

**Hoca sorarsa:**
- Neden büyük hazır model yok? → Tarayıcıda her 250 ms'de çalışacak, küçük ve hızlı olmalı; giriş 28×28.
- Eğitim? → AdamW, 20 epoch (M1 10), yığın 512, RTX 5070 Ti ekran kartı.

## 4. 50 sınıf sonuçları

**Görsel (karar):** yatay çubuk grafik, hata oranı. Test seti 250 000 çizim.

| Model | Doğruluk | Hata |
|---|---:|---:|
| M1 | %95,22 | %4,78 |
| M2 artırmasız | %97,13 | %2,87 |
| M2 artırmalı | %96,94 | %3,06 |
| M3 | %97,43 | %2,57 |
| M3-kısmi | %96,50 | %3,50 |

**Söylenecek:**
1. M1 → M2: hata %4,8'den %2,9'a, neredeyse yarıya. BatchNorm, Dropout, derinlik işe yarıyor.
2. M2 → M3: yalnız 0,3 puan kazanç, ama M3 2,5 kat yavaş. Karmaşık model her zaman çok daha iyi değil.
3. Veri artırma test setinde işe yaramadı (−0,19 puan): 30 000 çizim zaten çeşitli. Asıl yararı gerçek kullanıcıda beklenir.
4. Dürüstlük: her model bir kez eğitildi; 0,3 puanlık farklar kesin değil.
5. M3-kısmi tam çizimde 0,9 puan geride; neden seçildiği 5. bölümde.

**Hoca sorarsa:**
- En çok karışan? → ay ↔ muz (hilal), örümcek ↔ güneş (çizgili daire), mantar ↔ şemsiye. Şekil benzerliği.
- Aşırı öğrenme? → M1'de biraz (eğitim %97, doğrulama %95). M2 ve M3'te eğriler yakın.

## 5. Erken tanıma ve M3-kısmi (en önemli bölüm)

**Görsel (varsayılan, kullanıcı cevaplamadı):** iki slayt. (a) %25/50/75/100 sütun grafiği M3 vs M3-kısmi; (b) oyunda fark tablosu. Ana cümle sonuç slaytında, burada da bir kez söylenebilir.

| Model | %25 | %50 | %75 | %100 |
|---|---:|---:|---:|---:|
| M1 | %12,8 | %43,1 | %82,3 | %95,2 |
| M2 | %15,3 | %49,7 | %86,2 | %97,1 |
| M3 | %14,7 | %50,5 | %87,1 | %97,4 |
| M3-kısmi | %40,2 | %76,3 | %91,9 | %96,5 |

(%25 = çizginin/mürekkebin ilk çeyreği)

**Söylenecek:**
1. İlk üç model yarım çizimde çöküyor: tam %97, ilk çeyrekte %15. Eğitimde hiç yarım çizim görmediler.
2. Mimari çözmüyor: M1–M3 hepsi %13–15.
3. Çözüm veride: her çizimin rastgele %20–100'ü alınarak yarım sürüm; eğitimde her yığının yarısı bununla değiştirildi, etiket aynı.
4. Sonuç: ilk çeyrekte %15 → %40 (2,7 kat); bedeli tam çizimde −0,9 puan.
5. Ana cümle: "Erken tanımada belirleyici olan mimari değil, eğitim verisiydi."

**Oyunda fark** (oyun kuralıyla, 50 sınıf, test):

| | M3 | M3-kısmi |
|---|---:|---:|
| Tanınan çizim | %98,9 | %98,4 |
| Tur puanı | 67,4 | 74,7 |
| 60 sn'de tanınan nesne | 8,1 | 10,3 |

M3 biraz daha çok tanıyor ama geç; M3-kısmi 7 puan önde. Model doğruluğa göre değil oyun puanına göre seçildi.

**Hoca sorarsa:**
- Dezavantaj? → Ayrıntı çizilmeden karar verdiği için benzer nesneleri (ceket/kazak) daha kolay karıştırır.
- Neden %20–100? → Çok küçük parça bilgi taşımaz; oran ayrıca denenmedi (sınırlılık).

## 6. Gerçek kullanıcı testi (50 sınıflı model)

**Görsel (karar):** yalnız "test %97 → gerçek %88" karşılaştırması + üç hata sebebi. Kişi tablosu slaytta yok, aşağıda notta.

**Neden:** test seti de Quick, Draw!'dan; gerçek kişi fareyle/telefonda farklı çizer. Laboratuvar dışı başarı ölçüldü.

**Nasıl:**
- Ayrı çizim toplama sayfası, arkadaşlara link.
- Kişi başı 50 nesne, kişiye özel rastgele sıra.
- Model tahmini gizli: görse çizimini modele göre düzeltir, sonuç iyimser çıkar.
- Çizimler katılımcının cihazında dosyaya, elle gönderildi; veritabanı yok.
- Adlar yerine A–E (kişisel veri).

**Sonuç:** 5 kişi, 229 çizim (179 fare, 50 dokunmatik).

| | Test seti | Gerçek |
|---|---:|---:|
| M3 | %97,4 | %88,2 |
| M3-kısmi | %96,5 | %86,9 |
| M1 | %95,2 | %82,5 |

Gerçekte 9–13 puan düşük; sıralama korunuyor.

**Hata sebepleri:**
1. Alışılmadık biçim: önden araba, rakamlı saat → pizza.
2. Türkçe ad belirsizliği: "merdiven" → 3 kişi basamaklı çizdi; veri sınıfı ladder (el merdiveni). Ad sonra "el merdiveni" yapıldı.
3. Zaten karışan sınıflar: örümcek → güneş.

**Dürüstlük:** 5 kişi küçük. Tek dokunmatik kişi en düşük (%78), ama fareyle çizenler arasında da %75–96 fark; aygıt etkisi kişi etkisinden ayrılamıyor.

Kişi tablosu (yalnız not): A dokunmatik 50 çizim M3 %80 / M3-kısmi %78; B fare 50 %92/%96; C fare 28 %82/%75; D fare 50 %90/%88; E fare 50 %94/%92.

**Hoca sorarsa:**
- Veri artırma işe yaradı mı? → Hayır: artırmalı M2 %85,6, artırmasız %86,0.
- Neden sonuç gösterilmedi? → Görse düzeltirdi, ölçüm iyimser olurdu.

**AÇIK:** gerçek çizimlerin 345 sınıflı modeldeki sonucu sunuma konmayacak; kullanıcı yeniden test edecek, yeni sayı sonra yazılacak. [345 gerçek kullanıcı sonucu: ___]

## 7. 345 sınıfa geçiş

**Görsel (karar):** tek slayt; sol "neden düştü" (karışan çiftler), sağ "oyunda üç çözüm".

**Neden geçtik:** 50 sınıflı oyun çok kolay geldi, çizimler 2–4 sn'de tanınıyordu.

**Ne değişti:** sınıf başına 20 000 eğitim (toplam 6,9 milyon, bellek sınırı); mimari aynı, yalnız son katman 345 çıkış; M2 atlandı (M3'e çok yakındı).

| | 50 sınıf | 345 sınıf |
|---|---:|---:|
| M3 | %97,4 | %77,3 |
| M3-kısmi | %96,5 | %75,1 |
| M1 | %95,2 | %70,1 |

**Neden düştü:** yeni sınıflar zor olduğu için değil. Aynı 50 sınıfın çizimleri 345 sınıflı modelde %84,4 (önce %97,4). Sebep benzer sınıfların bir arada olması:

| Gerçek | Tahmin | /2 500 |
|---|---|---:|
| doğum günü pastası | pasta | 936 |
| kasırga | hortum | 871 |
| keman | gitar | 710 |
| okul otobüsü | otobüs | 663 |
| bardak | kupa | 645 |

**Oyunda üç çözüm:**
1. Eşdeğer gruplar (12): aynı nesnenin adları birlikte kabul (bardak = kupa = kahve fincanı). Keman/gitar gibi farklı nesneler birleştirilmedi.
2. Eşik %50 → %30: olasılık benzer sınıflara bölünüyor, doğru cevap birinci ama %41 gibi kalıyordu.
3. Sorulan kelimeler: model 345'i tanır, oyunda iyi tanınan 258 kelime sorulur.
İki sekme: "Oyun · 50" (kolay), "Oyun · 258" (zor).

**Hoca sorarsa:**
- Eşik neden %30? → %50/40/30/25/20 denendi; düştükçe daha çok tanınır ama yanlış kabul artar. %30 denge; doğrulama setiyle seçildi.
- Daha iyi nasıl? → 64×64 giriş ince ayrıntıyı (yay, yazı) koruyabilir.

## 8. Tarayıcıda çalışma

**Görsel (karar):** üç büyük sayı (4,3 ms · 2,7 MB · %2) + altında akış PyTorch → ONNX → tarayıcı.

**Söylenecek:** çoğu uygulama çizimi sunucuya yollar; bizde model kullanıcının tarayıcısında çalışır. Faydası: hızlı (gecikme yok), ücretsiz (sunucu yok), gizli (çizim cihazdan çıkmaz).

**Nasıl:**
1. PyTorch (Python sinir ağı kütüphanesi) ile eğitim.
2. ONNX'e çevirme: modeller için ortak dosya formatı ("modelin PDF'i").
3. Tarayıcıda ONNX Runtime Web (WebAssembly: tarayıcıda hızlı kod).
Doğrulama: PyTorch ve ONNX çıktıları arası en büyük fark < 0,0000006.

| | |
|---|---:|
| Tek tahmin (M3-kısmi) | 4,3 ms |
| Ön işleme dahil | ~5 ms |
| Model dosyası | 2,7 MB |
| Tahmin sıklığı | 250 ms'de bir + her çizgi bitince |

250 ms'nin %2'si: gerçek zaman için fazlasıyla yeterli.

**Hoca sorarsa:**
- Telefonda? → Ölçülmedi (sınırlılık).
- 345 sınıfta yavaşladı mı? → Hayır, 4,4 ms; yalnız son katman büyüdü.
- Ön işleme neden iki dilde? → Eğitim Python, oyun TypeScript; aynı görüntü şart, 304 örnekle test.

## 9. Sınırlılıklar ve sonraki adımlar

**Görsel (karar):** slaytta 4 madde (1, 2, 4, 5 aşağıda); 3 ve 6 yalnız notta.

**Slayttakiler:**
1. Küçük örnek: 5 kişi, dokunmatikte 1 kişi; genellenemez.
2. Her model bir kez eğitildi: 0,3 puanlık M2–M3 farkı kesin değil. M1'in 2 puan geriliği ve M3-kısmi'nin erken tanıma farkı bundan etkilenmeyecek kadar büyük.
4. Erken kararın bedeli: benzer nesnelerde kolay kandırılır; ceket → kazak kabul %65 (zor çiftlerde ortalama %33). Erken tanıma ile ayırt etme arasında denge.
5. 50 sınıflı modelde "hiçbiri" yok: karalamaların %4,5'i (20'de 1) kabul. 345 sınıflı modelde "karalama" sınıfı var, %0,4.

**Notta (sorulursa):**
3. Veri yanlılığı: yalnız Google'ın tanıdığı çizimler; kötü çizimler veride yok, test iyimser olabilir; gerçek kullanıcı düşüşünün bir sebebi olabilir.
6. Telefonda hız ölçülmedi.

**Sonraki adımlar:** "hiçbiri" sınıfı; çizim sırasını kullanan RNN/Transformer ile karşılaştırma; farklı tohumlarla tekrar eğitim; telefonda ölçüm ve 8 bit nicemleme.

## 10. Sonuç

**Ana cümle:** "Erken tanımada belirleyici olan mimari değil, eğitim verisiydi."
1. Küçük CNN'ler yeterli: 50 sınıfta %97,4, tarayıcıda ~5 ms.
2. Yarım çizimle eğitim: ilk çeyrekte doğruluk 2,7 kat; mimari değişikliği bunu yapmadı.
3. Model oyun puanına göre seçildi, sınıflandırma doğruluğuna göre değil; model kullanılacağı kuralla ölçülmeli.
(Karar: CepKonsol cümlesi yok.)

## 11. Canlı demo (~2 dk)

1. Oyun · 50: 1–2 tur, tahminin çizerken değişmesi.
2. Oyun · 258: bardak/pasta çıkarsa eşdeğer grup (kupa da kabul).
3. Serbest çizim: modelin gördüğü 28×28 görüntü, ilk 5 tahmin.
B planı: `demo/` içinde `npx vite`; sunumdan önce dene.

## Açık kararlar
- Kapak: ad / öğrenci no boş bırakılacak (kullanıcı yazacak).
- Demo adresi: Vercel'de var, adres henüz verilmedi.
- Görünüm/şablon: karar bekliyor.
- Slayt sayısı: 13 (kapak, amaç, veri, modeller, 50 sonuç, erken a, erken b, gerçek kullanıcı, 345, tarayıcı, sınırlılık, sonuç, demo).
