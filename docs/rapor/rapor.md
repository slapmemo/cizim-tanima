# CNN Tabanlı Gerçek Zamanlı Çizim Tanıma Oyunu

Taslak. Sayılar `deneyler/sonuclar.json`, `deneyler/sonuclar345.json` ve `deneyler/gercek.json` dosyalarından alınmıştır; şekiller `deneyler/` altındadır.

## 1. Giriş

Bu çalışmada, kullanıcının ekrana çizdiği nesneyi çizim sürerken tanıyan evrişimli sinir ağı (CNN) tabanlı bir oyun geliştirilmiştir. Oyunda oyuncuya bir nesne adı verilir; oyuncu 20 saniye içinde nesneyi çizer ve model çizimi tanıdığı anda, kalan süreyle orantılı puan kazanılır. Bu nedenle model yalnız tamamlanmış çizimleri değil, yarım çizimleri de olabildiğince erken tanımalıdır.

Hedefler:

1. Google Quick, Draw! veri setinin seçilmiş 50 sınıfında yüksek doğrulukla sınıflandırma yapan bir CNN eğitmek.
2. Farklı karmaşıklıktaki üç mimariyi doğruluk, model boyutu ve tahmin süresi açısından karşılaştırmak.
3. Modelin tarayıcıda, sunucuya ihtiyaç duymadan gerçek zamanlı çalışmasını sağlamak.
4. Erken tanıma başarımını (çizimin bir kısmıyla doğruluk) ölçmek ve iyileştirmek.
5. Yöntemi veri setinin 345 sınıfının tamamına ölçeklendirip sınıf sayısının doğruluğa ve oyuna etkisini ölçmek.

## 2. Veri seti ve ön işleme

### 2.1. Quick, Draw!

Quick, Draw! veri seti, 345 sınıfta 50 milyondan fazla çizim içerir. Her çizim, kullanıcının kalem vuruşlarının (stroke) nokta dizileri olarak saklanır. Bu çalışmada `simplified` sürüm kullanılmıştır. Bu sürümde çizimler 0–255 aralığına ölçeklenmiş ve Ramer–Douglas–Peucker (RDP) algoritmasıyla sadeleştirilmiştir. Her kayıtta, çizimin Google'ın kendi modeli tarafından tanınıp tanınmadığını gösteren `recognized` alanı bulunur.

### 2.2. Sınıf seçimi

345 sınıf içinden 50 sınıf seçilmiştir (`egitim/siniflar.py`). Seçimde üç ölçüt kullanılmıştır: nesne 20 saniyede çizilebilmeli, birbirine çok benzeyen sınıflar birlikte alınmamalı (ör. kupa / kahve fincanı) ve nesnenin Türkçe adı açık olmalıdır.

### 2.3. Bölümleme

Her sınıftan yalnız `recognized = true` olan çizimler alınmış, sabit tohumla karıştırılıp sınıf başına 30 000 eğitim, 5 000 doğrulama ve 5 000 test çizimi ayrılmıştır. Toplam 1,5 milyon eğitim, 250 bin doğrulama ve 250 bin test örneği vardır. Sınıflar dengelidir.

### 2.4. Vuruşlardan görüntüye

Veri setinin hazır 28×28 görüntü sürümü (`numpy_bitmap`) kullanılmamıştır. Bunun nedeni, oyunda kullanıcının çizimini aynı yöntemle görüntüye çevirme imkânının olmamasıdır. Eğitimdeki görüntüler ile oyundaki görüntüler arasındaki fark, modelin gerçek kullanımda başarımını düşürür. Bunun yerine vuruşlardan görüntü üreten tek bir algoritma yazılmış ve hem eğitimde (Python) hem tarayıcıda (TypeScript) birebir uygulanmıştır:

1. Bütün noktaların sınır kutusu bulunur; çizim sol üst köşeye kaydırılır ve uzun kenarı 255 olacak biçimde en-boy oranı korunarak ölçeklenir.
2. Her vuruş RDP ile ε = 2,0 değerinde sadeleştirilir (veri setiyle aynı değer).
3. Çizim 28×28 tuvalde 2 piksel kenar payıyla ortalanır.
4. Her pikselin değeri, piksel merkezinin en yakın doğru parçasına uzaklığına (d) göre belirlenir: v = sınırla(1,5 − d, 0, 1). Bu, yaklaşık 2 piksel kalınlığında, kenarları yumuşatılmış çizgiler üretir.

İki uygulamanın eşitliği, 304 örnek (50 sınıftan tam ve yarım çizimler, uç durumlar) üzerinde test edilmiş ve bütün piksellerin bayt düzeyinde aynı olduğu görülmüştür (`demo/test/esitlik.ts`).

### 2.5. Yarım çizimler

Erken tanımayı ölçmek için her çizimin mürekkebinin (nokta sayısının) ilk %25, %50 ve %75'i alınarak görüntü üretilmiştir. Yarım çizim de aynı ön işlemeden geçer; yani oyundaki gibi, o ana kadar çizilmiş kısım kendi sınır kutusuna göre ölçeklenir. Ölçüm, test setinde sınıf başına 1000 çizimle (toplam 50 000) yapılmıştır.

## 3. Modeller

| Model | Yapı | Parametre |
| --- | --- | ---: |
| M1 — Basit CNN | 2 × (3×3 evrişim, ReLU, 2×2 maks. havuzlama), 128 nöronlu tam bağlı katman | 426 802 |
| M2 — Derin CNN | 3 blok × (2 × [3×3 evrişim, BatchNorm, ReLU], havuzlama, Dropout2d 0,1), 256 nöronlu tam bağlı katman, Dropout 0,4 | 595 154 |
| M3 — Hafif ResNet | Giriş evrişimi + 3 aşama × 2 artık blok (32/64/128 kanal), küresel ortalama havuzlama, Dropout 0,2 | 701 202 |
| M3-kısmi | M3 ile aynı mimari; eğitimde her yığındaki örneklerin yarısı yarım çizim sürümüyle değiştirilir (§4.5) | 701 202 |

M2 hem veri artırmasız hem veri artırmayla eğitilmiştir; böylece düzenlileştirme katmanlarının ve veri artırmanın etkisi ayrı ayrı görülebilmektedir.

**Veri artırma** (GPU'da, her yığında rastgele): ±15° döndürme, 0,85–1,15 ölçekleme, ±2 piksel kaydırma. Ön işleme çizgi kalınlığını sabitlediği için kalınlık artırması kullanılmamıştır.

**Eğitim ayarları:** AdamW (ağırlık azalması 0,05), tek döngülü (one-cycle) öğrenme oranı, en yüksek oran 0,003, yığın boyutu 512, bfloat16 karışık hassasiyet, M1 için 10, diğerleri için 20 epoch. Her epoch sonunda doğrulama doğruluğu ölçülmüş ve en iyi epoch'un ağırlıkları saklanmıştır. Test seti yalnız son değerlendirmede kullanılmıştır. Donanım: NVIDIA RTX 5070 Ti (16 GB), PyTorch 2.11 (CUDA 12.8).

## 4. Sonuçlar

### 4.1. Test doğruluğu

Test seti: 250 000 çizim (sınıf başına 5 000), eğitimde ve model seçiminde hiç kullanılmadı.

| Model | Parametre | İlk-1 doğruluk | İlk-3 doğruluk | ONNX boyutu | CPU tahmin süresi* |
| --- | ---: | ---: | ---: | ---: | ---: |
| M1 Basit CNN | 426 802 | %95,22 | %98,81 | 1,7 MB | 0,06 ms |
| M2 Derin CNN (artırmasız) | 595 154 | %97,13 | %99,35 | 2,3 MB | 0,24 ms |
| M2 Derin CNN (artırmalı) | 595 154 | %96,94 | %99,33 | 2,3 MB | 0,24 ms |
| M3 Hafif ResNet | 701 202 | **%97,43** | **%99,46** | 2,7 MB | 0,60 ms |
| M3-kısmi | 701 202 | %96,50 | %99,22 | 2,7 MB | 0,60 ms |

\* ONNX Runtime (Python), tek iş parçacığı, tek görüntü, 500 tekrar ortalaması.

M1'den M2'ye geçiş (BatchNorm, daha fazla evrişim katmanı, Dropout) hatayı %4,78'den %2,87'ye indirmiştir. Artık bağlantılı M3 en yüksek doğruluğa ulaşmış, ancak kazanç M2'ye göre küçük kalmıştır (0,3 puan). Buna karşılık M3'ün tahmin süresi M2'nin 2,5 katıdır.

### 4.2. Öğrenme eğrileri

![Kayıp ve doğruluk eğrileri](../../deneyler/egriler.png)

M1'de eğitim doğruluğu (%97,0) ile doğrulama doğruluğu (%95,2) arasındaki fark son epoch'larda açılmaktadır; basit model aşırı öğrenmeye başlamıştır. M2 ve M3'te iki eğri birbirine yakındır. Veri artırmalı M2'nin eğitim doğruluğu doğrulama doğruluğunun altındadır, çünkü artırılmış örnekler orijinallerden daha zordur ve Dropout eğitim sırasında etkindir.

### 4.3. Veri artırmanın etkisi

Veri artırma, M2'nin test doğruluğunu %97,13'ten %96,94'e düşürmüştür (−0,19 puan). Sınıf başına 30 000 çizim, döndürme ve ölçek çeşitliliğini zaten içerdiği için, aynı dağılımdan gelen test setinde artırmanın katkısı görülmemiştir. Artırmanın asıl beklenen yararı, veri setinden farklı koşullarda (fare, telefon, farklı çizim alışkanlıkları) çizilen gerçek kullanıcı çizimlerindedir (§4.7).

### 4.4. Karışan sınıflar

![M3 karışıklık matrisi](../../deneyler/m3/karisiklik.png)

M3'te en çok karışan çiftler (5 000 test çiziminde):

| Gerçek | Tahmin | Sayı |
| --- | --- | ---: |
| ay | muz | 367 |
| muz | ay | 204 |
| örümcek | güneş | 141 |
| mantar | şemsiye | 124 |
| güneş | örümcek | 108 |
| ay | pizza | 94 |
| dondurma | elmas | 69 |
| ağaç | mantar | 67 |

Karışıklıklar şekil benzerliğinden kaynaklanmaktadır: hilal biçimli ay ile muz, ortasından çizgiler çıkan daire biçimindeki güneş ile örümcek, kubbe ve sap yapısındaki mantar ile şemsiye. "Ay → pizza" karışıklığı, dilim biçiminde çizilen aylardan gelmektedir. En zor sınıflar ay (%88,4), mantar (%93,0) ve kuş (%93,1); en kolaylar merdiven, tişört, ev ve zarftır (%99,2).

### 4.5. Erken tanıma

Çizimin yalnız ilk %25, %50 ve %75'i (mürekkep oranı) verildiğinde ilk-1 doğruluk (sınıf başına 1 000, toplam 50 000 test çizimi):

| Model | %25 | %50 | %75 | %100 |
| --- | ---: | ---: | ---: | ---: |
| M1 | %12,8 | %43,1 | %82,3 | %95,2 |
| M2 (artırmasız) | %15,3 | %49,7 | %86,2 | %97,1 |
| M2 (artırmalı) | %13,7 | %49,5 | %86,7 | %96,9 |
| M3 | %14,7 | %50,5 | %87,1 | %97,4 |
| M3-kısmi | **%40,2** | **%76,3** | **%91,9** | %96,5 |

![Erken tanıma](../../deneyler/kismi.png)

İlk dört model yalnız tamamlanmış çizimlerle eğitildiği için yarım çizimlerde başarısızdır; mimari farkı bu sorunu çözmemektedir. Bu nedenle M3, eğitim verisine yarım çizimler eklenerek yeniden eğitilmiştir (M3-kısmi): her eğitim çizimi için mürekkebin rastgele %20–100'ü alınarak bir yarım sürüm üretilmiş (`egitim/kismi_hazirla.py`), her yığında örneklerin yarısı bu sürümle değiştirilmiştir. Etiketler aynı kalmıştır. Sonuçta yarım çizimdeki doğruluk %25 mürekkepte 2,7 katına, %50'de 1,5 katına çıkmış, tam çizimdeki doğruluk ise yalnız 0,9 puan düşmüştür.

### 4.6. Oyun simülasyonu

Oyun kuralıyla (hedef birinci tahmin ve olasılığı ≥ 0,5) her test çizimi %10'luk adımlarla ilerletilmiş ve ilk tanındığı adım kaydedilmiştir (sınıf başına 200, toplam 10 000 çizim; §4.5'te kullanılmayan çizimler).

| Model | Tanınan çizim | Ortalama tanınma anı | Medyan tanınma anı |
| --- | ---: | ---: | ---: |
| M3 | %98,7 | mürekkebin %56'sı | %60 |
| M3-kısmi | %98,2 | mürekkebin %43'ü | %40 |

![Oyun simülasyonu](../../deneyler/oyun_simulasyonu.png)

M3-kısmi çizimleri ortalama 13 puan, medyanda 20 puan daha erken tanımaktadır. Puan kalan süreyle orantılı olduğundan, oyunda M3-kısmi kullanılmıştır.

### 4.7. Gerçek kullanıcı çizimleri

Gerçek kullanıcı çizimleri, demonun çizim toplama sayfasıyla (`demo/topla.html`) toplanmıştır. Katılımcıya 50 nesne kişiye özel rastgele sırada gösterilmiş, model tahmini çizim sırasında gizlenmiş (katılımcı çizimini modele göre düzeltmesin diye), çizimler katılımcının cihazında dosyaya yazılıp elle iletilmiştir. Sonuç (28 Ekim 2026; 5 katılımcı + 1 yerel çizim, toplam 229 çizim; 179 fare, 50 dokunmatik ekran; hiçbir çizim elenmedi):

| Model | Gerçek ilk-1 | Gerçek ilk-3 | Quick, Draw! test ilk-1 |
| --- | ---: | ---: | ---: |
| M1 | %82,5 | %90,8 | %95,22 |
| M2 (artırmasız) | %86,0 | %93,9 | %97,13 |
| M2 (artırmalı) | %85,6 | %93,9 | %96,94 |
| M3 | **%88,2** | **%94,3** | %97,43 |
| M3-kısmi | %86,9 | %94,3 | %96,50 |

| Katılımcı | Aygıt | Çizim | M3 | M3-kısmi |
| --- | --- | ---: | ---: | ---: |
| A | dokunmatik | 50 | %80 | %78 |
| B | fare | 50 | %92 | %96 |
| C | fare | 28 | %82 | %75 |
| D | fare | 50 | %90 | %88 |
| E | fare | 50 | %94 | %92 |

Gerçek çizimlerde doğruluk, test setine göre 9–13 puan düşüktür. Model sıralaması büyük ölçüde korunmuştur: M1 en zayıf, M3 ve M3-kısmi en iyidir. Hataların incelenmesi (`test-verileri/<kişi>/cizimler.png`) üç kaynak göstermektedir:

1. **Alışılmadık bakış açısı ya da biçim.** Önden çizilmiş araba, yumruk biçiminde el, sarkaçlı duvar saati, körüklü fotoğraf makinesi örnek verilebilir. Rakamlı çizilen saat iki katılımcıda (C, D) pizza sanılmıştır. Veri setindeki çizimlerin çoğu nesneyi en tipik açıdan ve basitçe gösterir.
2. **Etiketin Türkçe karşılığının belirsizliği.** "Merdiven" (veri setinde *ladder*, el merdiveni) üç katılımcı (A, D, E) tarafından basamaklı merdiven olarak çizilmiştir.
3. **Test setinde de karışan sınıflar.** Örümcek → güneş ve papyon → kelebek karışıklıkları gerçek çizimlerde de görülmüştür.

Örnek küçüktür (5 kişi). Dokunmatik ekranla çizen tek katılımcı (A) en düşük sonucu almıştır, ancak fareyle çizenler arasındaki fark da (%75–96) benzer büyüklükte olduğundan aygıt etkisi bu veriyle kişi etkisinden ayrıştırılamamaktadır.

**Ön deneme (oyun, tek kullanıcı, fare):** 9 turda 7 çizim tanınmıştır (%77,8); tanınan çizimlerde ortalama tanınma süresi 4,1 sn'dir (en kısa 2,6 sn, zarf; en uzun 5,7 sn, bisiklet). Tanınmayan iki çizimin incelemesi:

- *Gökkuşağı*, kavisler yerine çapraz düz çizgilerle çizilmiş ve model %72 olasılıkla "şimşek" demiştir; oyuncu 8,6 sn'de turu geçmiştir.
- *Şapka* çizimi şapkadan çok bir çubuk insana benzemektedir; modelin ilk tahmini "ampul" (%38) olmuş ve süre dolmuştur.

Her iki hata da, çizimin veri setindeki tipik çizim biçiminden uzak olmasından kaynaklanmaktadır.

Oyun kayıtları tanındığı anda kesildiği için yukarıdaki doğruluk ölçümüne katılmamıştır.

### 4.8. 345 sınıfa ölçeklendirme

50 sınıflık oyun ön denemelerde çok kolay bulunmuştur: çizimler çoğunlukla 2–4 saniyede tanınmaktadır. Bu nedenle modeller veri setinin 345 sınıfının tamamıyla yeniden eğitilmiştir (`SINIF_SETI=345`, `egitim/siniflar345.py`). Veri miktarını bellekte tutulabilir düzeyde tutmak için sınıf başına 20 000 eğitim, 2 500 doğrulama ve 2 500 test çizimi alınmıştır. Toplamda 6,9 milyon eğitim, 862 500 doğrulama ve 862 500 test çizimi vardır. Ön işleme ve yarım çizim üretimi aynıdır. M2, 50 sınıfta M3'e yakın sonuç verdiği için atlanmıştır. M1 10 epoch, M3 ve M3-kısmi veri artırmalı olarak 15 epoch eğitilmiştir. Mimari yalnız son katmanın çıkış sayısında değişir.

| Model | Parametre | İlk-1 | İlk-3 | %25 | %50 | %75 | Aynı 50 sınıfta ilk-1* |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| M1 | 464 857 | %70,12 | %87,39 | %2,0 | %16,0 | %49,0 | %79,7 |
| M3 | 739 257 | **%77,30** | **%92,39** | %2,6 | %21,0 | %58,2 | %84,4 |
| M3-kısmi | 739 257 | %75,12 | %90,68 | **%10,1** | **%37,3** | **%64,0** | %82,7 |

\* 345 sınıflı modelin, §2.2'deki 50 sınıfın test çizimlerindeki ortalama sınıf doğruluğu (345 seçenek arasından).

Test seti 862 500 çizimdir. Erken tanıma ölçümünde sınıf başına 200 çizim kullanılmıştır (toplam 69 000).

![345 sınıf öğrenme eğrileri](../../deneyler/egriler345.png)

**Sınıf sayısının etkisi.** Sınıf sayısı 6,9 katına çıktığında M3'ün hatası %2,6'dan %22,7'ye yükselmiştir. Aynı 50 sınıfın çizimleri bile, 345 seçenek arasından tanınırken %97,4 yerine %84,4 doğrulukla tanınmaktadır. Düşüşün nedeni yeni sınıfların zor olması değildir. Neden, 50 sınıflık seçimde bilerek dışarıda bırakılan birbirine benzer sınıfların artık birlikte bulunmasıdır. M3'te en çok karışan çiftler bunu göstermektedir:

| Gerçek | Tahmin | Sayı (2 500 çizimde) |
| --- | --- | ---: |
| doğum günü pastası | pasta | 936 |
| kasırga | hortum | 871 |
| keman | gitar | 710 |
| okul otobüsü | otobüs | 663 |
| otobüs | okul otobüsü | 661 |
| bardak | kupa | 645 |
| kahve fincanı | kupa | 590 |
| tırmık | süpürge | 527 |
| radyo | müzik seti | 516 |

Bu çiftlerin çoğu 28×28 çözünürlükte, hatta insan gözüyle de ayırt edilmesi zor nesnelerdir. Bazıları anlam olarak da iç içedir (pasta / doğum günü pastası). En zor sınıflar keçeli kalem (%26), bahçe hortumu (%27), ayı (%28), havuz (%36) ve uçak gemisi (%37); en kolaylar zarf (%97), yıldız (%96), el merdiveni (%95) ve kulaklıktır (%95). İlk-3 doğruluğu (%92,4) ilk-1'den 15 puan yüksektir. Hataların çoğunda doğru sınıf ilk üç tahmin arasındadır.

**Erken tanıma.** 345 sınıfta yarım çizimler çok daha zordur: M3 %50 mürekkepte yalnız %21 doğruluğa ulaşmaktadır. Yarım çizimle eğitim (M3-kısmi) bu değeri %37,3'e çıkarmış, tam çizimde ise 2,2 puan kaybettirmiştir. Bu kayıp 50 sınıftakinin (0,9 puan) iki katından fazladır.

![345 sınıf erken tanıma](../../deneyler/kismi345.png)

**Oyun simülasyonu** (§4.6 ile aynı kural; sınıf başına 50, toplam 17 250 çizim):

| Model | Tanınan çizim | Mürekkebin %50'sinde tanınan | %70'inde | Ortalama tanınma anı* |
| --- | ---: | ---: | ---: | ---: |
| M3 | %79,9 | %15,6 | %45,4 | %71 |
| M3-kısmi | %74,2 | %22,4 | %48,3 | %66 |

\* Yalnız tanınan çizimler üzerinden.

![345 sınıf oyun simülasyonu](../../deneyler/oyun_simulasyonu345.png)

M3-kısmi, mürekkebin %70'ine kadar daha çok çizimi tanımaktadır. Ancak çizim tamamlandığında daha az çizimi tanımaktadır, çünkü eşiği (olasılık ≥ 0,5) daha seyrek aşar. Puan kalan süreyle orantılı olduğundan erken tanıma daha değerlidir. Bu nedenle oyunda M3-kısmi kullanılmıştır. Fark 50 sınıftakinden küçük olduğundan bu seçim ileride gerçek oyun verisiyle yeniden değerlendirilmelidir.

**Oyunda sorulan kelimeler.** Model 345 sınıfın hepsini tanır, yani oyuncunun çizimi bütün sınıflarla yarışır. Ancak oyunda yalnız M3-kısmi'nin test doğruluğu en az %70 olan sınıflar sorulur (`egitim/oyun_kelimeleri.py`). Bu ölçüt 97 sınıfı çıkarmıştır. Ayrıca 20 saniyede çizilemeyen ya da anlamsız 6 sınıf elle çıkarılmıştır: hayvan göçü, kamuflaj, Çin Seddi, çizgi, karalama, yoga. Kalan 242 kelimenin ortalama test doğruluğu %82,6'dır. İlk 50 sınıfın 45'i bu listededir.

**Gerçek kullanıcı çizimleri** (§4.7'deki 229 çizim, 345 seçenek arasından):

| Model | Gerçek ilk-1 | Gerçek ilk-3 | Aynı 50 sınıfta Quick, Draw! test ilk-1 |
| --- | ---: | ---: | ---: |
| M1 | %62,0 | %77,7 | %79,7 |
| M3 | %68,6 | %81,7 | %84,4 |
| M3-kısmi | %68,6 | %80,8 | %82,7 |

Gerçek çizimlerle test seti arasındaki fark 345 sınıfta 14–18 puandır. Bu fark 50 sınıftakinden (9–13 puan) büyüktür: veri setinin tipik çiziminden uzaklaşan bir çizim, 345 sınıfta yakınında başka bir sınıf bulma olasılığı daha yüksek olduğundan daha kolay yanlış sınıfa düşer. Katılımcılara göre M3-kısmi doğruluğu A %60, B %74, C %61, D %70, E %76'dır. Yeni karışıklıklar beklenen benzer sınıflardır: dağ → hız treni, balık → köpek balığı, kapı → şifonyer, ağaç → brokoli.

Tarayıcıda tek tahmin süresi 345 sınıfta da değişmemiştir (M1 0,25 ms, M3-kısmi 4,4 ms), çünkü yalnız son katman büyümüştür. Oyunun uçtan uca otomatik denemesinde (test setinden çizimlerle, 5 tur) 4 tur tanınmıştır. Tanınmayan turda (zikzak) model doğru sınıfı birinci tahmin olarak vermiş, ancak olasılığı eşiğin altında kalmıştır.

## 5. Tarayıcıda gerçek zamanlı tahmin

Eğitilen modeller ONNX biçimine aktarılmış (softmax dahil) ve tarayıcıda ONNX Runtime Web (WebAssembly, tek iş parçacığı) ile çalıştırılmıştır. Aktarımın doğruluğu, PyTorch ve ONNX Runtime çıktılarının aynı girişlerdeki en büyük mutlak farkıyla kontrol edilmiştir.

Oyunda tahmin, kullanıcı çizerken en fazla 250 ms'de bir ve her vuruşun sonunda yapılır. Bir tahmin sürerken gelen istekler birleştirilir ve tahmin bitince bir kez daha çalıştırılır. Çizim, hedef sınıf modelin birinci tahmini olduğunda ve olasılığı en az 0,5 olduğunda tanınmış sayılır. Puan, kalan süreyle orantılıdır: puan = 100 × kalan süre / 20 sn.

ONNX aktarımında PyTorch ile ONNX Runtime çıktıları arasındaki en büyük mutlak fark bütün modellerde 6 × 10⁻⁷'nin altındadır.

Tarayıcıda tek tahmin süresi (masaüstü Chromium, WebAssembly, tek iş parçacığı, 200 tekrar ortalaması, ön işleme hariç):

| Model | Süre |
| --- | ---: |
| M1 | 0,29 ms |
| M2 | 1,66 ms |
| M3 / M3-kısmi | 4,3 ms |
| M1, 345 sınıf | 0,25 ms |
| M3 / M3-kısmi, 345 sınıf | 4,3 / 4,4 ms |

Ön işleme dahil bir tahmin M3-kısmi ile yaklaşık 5 ms sürmektedir. Bu, 250 ms'lik tahmin aralığının %2'si kadardır; model tarayıcıda gerçek zamanlı çalışmak için yeterince hızlıdır. Telefon tarayıcısındaki süre bu taslakta ölçülmemiştir.

## 6. Oyun

Demo iki bölümden oluşur:

- **Oyun:** 5 tur, her turda rastgele ve tekrarsız bir nesne, 20 saniye. İki sekme vardır: "Oyun · 242" (345 sınıflı M3-kısmi, 242 kelimelik listeden; §4.8) ve "Oyun · 50" (50 sınıflı M3-kısmi, 50 sınıfın hepsi; daha kolay). 242 sekmesinde tanınma eşiği %30'dur (aşağıda).

**Tanınma eşiğinin seçimi.** 345 sınıfta olasılık benzer sınıflara bölündüğü için doğru sınıf birinci olsa bile çoğu zaman %50'ye ulaşmamaktadır. Farklı kurallar, oyun kelimelerinin test çizimlerinde (kelime başına 50) ve gerçek çizimlerde ölçülmüştür (`egitim/esik_karsilastir.py`). "Yanlış kabul", aynı çizime rastgele başka bir oyun kelimesi sorulduğunda kuralın bunu kabul etme oranıdır:

| Kural (242 sekmesi) | Tanınan | Gerçek çizim | İlk %20 mürekkepte | Yanlış kabul |
| --- | ---: | ---: | ---: | ---: |
| birinci + ≥%50 | %83,2 | %72,4 | %1,2 | %0,1 |
| birinci + ≥%30 (seçilen) | %89,2 | %77,6 | %2,5 | %0,3 |
| ilk 3'te + ≥%20 | %93,3 | %82,0 | %4,2 | %0,6 |

Eşik %30'a indirildiğinde tanınan oran 6 puan artmakta, şans eseri erken tanınma ve yanlış kabul düşük kalmaktadır. Quick, Draw!'ın istemci kodu, hedefin birinci olmasını şart koşmadığını ve eş anlamlıları kabul ettiğini göstermektedir; buna benzeyen "ilk 3'te" kuralı daha yüksek tanıma verse de benzer nesneleri (ör. kupa sorulunca bardak) kabul ettiği için seçilmemiştir. 50 sınıflı modelde eşiği düşürmek yalnız şans eseri erken tanınmayı artırdığından (%17 → %26) bu sekmede %50 korunmuştur. Oyuncu çizerken modelin tahmini ("Yapay zekâ: kedi mi? %62 · yoksa kuş mu?") ekranda canlı görünür. Tanınınca çizim kilitlenir ve puan gösterilir; maç sonunda turların listesi ve toplam puan çıkar.
- **Serbest çizim:** İlk beş tahmin ve olasılıkları, modelin gördüğü 28×28 görüntü, model seçimi, tarayıcıda hız testi ve rapor için çizim kaydetme.

Demo, CepKonsol çok oyunculu platformuna "Çizim Düellosu" oyunu olarak eklenecek biçimde tasarlanmıştır: ön işleme, model ve oyun kuralları arayüzden bağımsız modüllerdedir.

## 7. Sınırlılıklar ve gelecek çalışmalar

- **Gerçek kullanıcı ölçümü küçük örneklidir** (§4.7, 5 kişi, yalnız biri dokunmatik ekranla). Gerçek çizimlerde doğruluk test setine göre belirgin biçimde düşmektedir. Düşüş 345 sınıfta daha büyüktür.
- **Veri yanlılığı:** yalnız Google'ın kendi modelinin tanıdığı çizimler (`recognized = true`) kullanıldı. Bu, kötü ya da yarım bırakılmış çizimleri veri setinden çıkarır ve test doğruluğunu iyimser gösterebilir.
- **Anlamsız karalama** da sınıflardan birine atanır. Oyunda yalnız hedef sınıf için olasılık eşiği kullanıldığından bu oyunu bozmaz, ama serbest çizimde yanıltıcı tahminler görülebilir. Veri setindeki "squiggle" (karalama) sınıfı bunu kısmen karşılar.
- **345 sınıfta benzer sınıflar** (pasta / doğum günü pastası, otobüs / okul otobüsü, bardak / kupa) doğruluğun büyük kısmını düşürmektedir (§4.8). Bu çiftleri birleştirmek ya da oyunda bunları kabul edilebilir karışıklık saymak doğruluğu artırır. Daha yüksek giriş çözünürlüğü (ör. 64×64) ince ayrıntıyı koruyabilir.
- **Telefon tarayıcısında tahmin süresi** ölçülmedi.
- **Gelecek çalışmalar:** vuruş sırasını doğrudan kullanan modellerle (RNN/Transformer) karşılaştırma; yarım çizim oranının ve eğitimdeki karışım oranının ayarlanması; modelin 8 bit tamsayıya nicemlenmesi (boyut ve hız); CepKonsol'da çok oyunculu "Çizim Düellosu" (telefonlarda çizim, ortak ekranda canlı tahmin).
