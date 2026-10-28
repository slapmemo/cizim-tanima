# Çizim Tanıma Oyunu — Genel Plan

Tarih: 28 Ekim 2026
Durum: Kullanıcıyla konuşularak kararlaştırıldı. Bu belge yol haritasıdır; burada yazan bir işin yapıldığı anlamına gelmez.

Ders: Sinir Ağları. Proje konusu: CNN tabanlı çizim tanıma oyunu; kullanıcının çizdiği nesne gerçek zamanlı tahmin edilir. Veri seti: Google Quick, Draw!

## 1. Kararlar

| Konu | Karar |
| --- | --- |
| Yer | `FinalCepKonsol/cizim-tanima/`, CepKonsol deposundan bağımsız. Tek kişilik proje, yerel klasör (GitHub sonra). |
| Kütüphane | PyTorch (CUDA 12.8 / `cu128`; RTX 5070 Ti 16 GB). Eğitim bu bilgisayarda; Colab gerekmez. |
| Sınıf sayısı | 50 seçilmiş sınıf (çizmesi kolay, birbirine az benzeyen). |
| Tahmin yeri | Tarayıcıda: model ONNX'e aktarılır, ONNX Runtime Web ile çalışır. |
| Model karşılaştırması | 3 model (§4). Oyunda doğruluk/hız dengesi en iyi olan kullanılır. |
| Oyun akışı | "Yapay zekâya tanıt": herkese aynı kelime, herkes aynı anda çizer, model canlı tahmin eder, erken tanınan çok puan alır. |
| Çizim kaydı | Yalnız bağımsız demoda, isteğe bağlı, bilgisayara JSON. Raporda gerçek kullanıcı test seti olur. CepKonsol'da kayıt yok. |
| CepKonsol'da | Telefonda çizilir, vuruşlar Host'a gider, model Host tarayıcısında çalışır (oyun mantığı Host'ta, CepKonsol karar 001). Tahmin telefona da geri gider, oyuncu kendi ekranında görür. |
| Rapor | Türkçe. Teslim tarihi belli değil; tahmini çalışan demo + rapor. |

## 2. Veri

- Kaynak: Quick, Draw! `simplified` ndjson (vuruşlar, 256×256'ya ölçeklenmiş). Hazır 28×28 `numpy_bitmap` kullanılmaz: tarayıcıdaki çizim aynı yolla görüntüye çevrilemez, eğitim ile oyun arasında fark oluşur.
- Yalnız `recognized: true` çizimler alınır.
- Sınıf başına: 30 000 eğitim, 5 000 doğrulama, 5 000 test (sabit tohumla ayrılır). Toplam ~2 milyon çizim.
- **Tek ön işleme:** vuruşlar → sınır kutusu → ortala, oranı koruyarak ölçekle → sabit kalınlıkta çiz → 28×28 gri ton. Aynı algoritma Python'da (eğitim) ve TypeScript'te (tarayıcı) yazılır. Eşitlik testi: aynı vuruşlardan iki tarafın ürettiği pikseller karşılaştırılır.
- Giriş boyutu ilk sürümde 28×28. 64×64 ayrı bir deney olarak denenebilir (doğruluk/hız farkı rapora girer).

## 3. Sınıflar

50 sınıfın listesi 1. birimde önerilir, kullanıcı onaylar. Ölçütler: çizmesi 20 sn'de mümkün, birbirine çok benzeyen çiftler yok (ör. kupa / kahve fincanı), Türkçe adı açık. Her sınıfın Türkçe ve İngilizce adı tutulur.

## 4. Modeller

| No | Model | Amaç |
| --- | --- | --- |
| M1 | Basit CNN: 2 evrişim + havuzlama + 1 tam bağlı | Temel çizgi |
| M2 | Derin CNN: 3–4 evrişim bloğu, BatchNorm, Dropout, veri artırma (küçük döndürme, kaydırma, ölçek; kalınlık artırması gereksiz: ön işleme kalınlığı sabitliyor) | Düzenlileştirme ve artırmanın etkisi (artırmasız M2 de eğitilir) |
| M3 | Hafif ResNet tarzı (artık bağlantılar) | Derinliğin etkisi |
| M3-kısmi | M3 + eğitimde yarım çizimler (eklendi, 28 Ekim 2026) | M1'de erken tanıma zayıf çıktı (%25 mürekkepte %13); oyun için iyileştirme |

Eğitim: AdamW, kosinüs öğrenme oranı, erken durdurma (doğrulama doğruluğu), karışık hassasiyet (AMP). Her deneyin ayarları ve sonuçları dosyaya yazılır (tekrarlanabilir).

## 5. Ölçümler (rapor için)

- Test setinde top-1 ve top-3 doğruluk, sınıf bazında doğruluk, karışıklık matrisi, en çok karışan sınıf çiftleri.
- Model boyutu (parametre, ONNX dosyası) ve tarayıcıda tek tahmin süresi (masaüstü ve telefon).
- **Erken tanıma:** çizimin ilk %25 / %50 / %75 vuruşlarıyla doğruluk. Oyunun "gerçek zamanlı" iddiasını ölçer.
- **Gerçek kullanıcı seti:** demoda kaydedilen çizimlerle doğruluk; Quick, Draw! test setiyle farkı.
- Eğitim/doğrulama kayıp ve doğruluk eğrileri.

## 6. Oyun kuralları (ilk sürüm, sonra ayarlanır)

- Maç 5 tur, tur 20 sn. Her turda herkese aynı kelime; turlarda kelime tekrarlanmaz.
- Tahmin: her vuruş bitince ve çizim sürerken ~250 ms'de bir.
- **Tanınma:** hedef sınıf model tahmininde birinci ve olasılığı ≥ 0,5 (eşik ayarlanabilir). Tanınan oyuncunun çizimi kilitlenir.
- Puan: tanınma anındaki kalan süreyle orantılı (ör. 100 × kalan / 20). Tanınmayan 0.
- Ekranda: her oyuncunun o anki ilk tahmini ve olasılığı; tanınanlar süreleriyle.

## 7. Aşamalar

Her birim doğrulanınca durulur ve devam için onay alınır.

### Aşama 1 — Kurulum ve veri

| No | İş | Bitti sayılır |
| --- | --- | --- |
| 1a | Klasör yapısı, Python sanal ortamı, PyTorch `cu128`, GPU denemesi | GPU'da küçük bir tensör işlemi çalışır |
| 1b | 50 sınıf önerisi (TR/EN adlar) | Kullanıcı onayladı |
| 1c | İndirme ve ayırma betiği; ön işleme (Python) | Sınıf başına 30k/5k/5k, 28×28 dizi dosyaları; örnek görüntülerle bakıldı |

### Aşama 2 — Eğitim ve karşılaştırma

| No | İş | Bitti sayılır |
| --- | --- | --- |
| 2a | Eğitim betiği + M1 | Test doğruluğu ve eğriler kayıtlı |
| 2b | M2 ve M3 | Üç modelin tablosu |
| 2c | Değerlendirme: karışıklık matrisi, erken tanıma, karışan çiftler | Rapora girecek şekiller üretildi |

### Aşama 3 — Tarayıcı demosu

| No | İş | Bitti sayılır |
| --- | --- | --- |
| 3a | ONNX'e aktarma; PyTorch ile ONNX çıktılarının eşitliği | Aynı girişte fark ihmal edilebilir |
| 3b | TypeScript ön işleme + eşitlik testi (Python ile aynı pikseller) | Test geçer |
| 3c | Demo sayfası: tuval (fare/dokunma), canlı ilk 3 tahmin, tahmin süresi | Masaüstü ve telefon tarayıcısında çalışır |
| 3d | "Çizimi kaydet" (JSON) + kayıtlarla doğruluk ölçen betik | Gerçek kullanıcı seti ölçüldü |

### Aşama 4 — Tek kişilik oyun prototipi

Demo sayfasında §6 kurallarıyla oynanır sürüm: kelime, süre, tanınma, puan, maç sonu. Görünüm CepKonsol dilinde (Nunito, lacivert `#071943`, camgöbeği `#29eaf1`, beyaz yuvarlak kartlar).

### Aşama 5 — Rapor

Giriş, veri ve ön işleme, modeller, deneyler ve sonuçlar (§5), oyun, sınırlılıklar. Şekiller 2c ve 3d'den.

### Aşama 6 — CepKonsol entegrasyonu (ders tesliminden bağımsız, sonra)

- Yeni oyun `cepkonsol/games/cizim-duellosu/` (Renk Tahmini gibi ayrı origin, sandbox'lı iframe; model ve ONNX Runtime oyunla birlikte sunulur).
- Protokol: telefon için yeni kontrol (çizim tuvali); vuruşlar parça parça gönderilir (mesaj sınırı 16 KB). Host tahmini telefona geri yollar. TS + Dart + `docs/protocol.md` birlikte değişir.
- Web kumanda ve Flutter'da tuval; Flutter'da vuruşlar tarayıcıdakiyle aynı koordinat biçiminde.
- Ön işleme ve tahmin kodu 3b/3c'den aynen alınır.

## 7b. 345 sınıf (eklendi, 28 Ekim 2026)

Kullanıcı isteği: oyun çok kolay (2–3 sn'de tanıyor), nesne sayısı artsın. Kararlar:

- Model 345 sınıfın tamamını tanır; oyunda yalnız seçilmiş kelimeler sorulur (test doğruluğu ≥ %70, çizilemeyenler elle çıkarılır; `egitim/oyun_kelimeleri.py`).
- 50 sınıflık çalışma raporda kalır; 345 sınıf "ölçeklendirme" bölümü olarak eklenir.
- 345 sınıfta M1, M3, M3-kısmi eğitilir (sınıf başına 20k/2,5k/2,5k; M2 atlandı).
- Arkadaşlardan çizim toplama sayfası 50 sınıfla kalır; toplanan çizimler 345 sınıflı modellerle de ölçülür.
- Çalıştırma: `SINIF_SETI=345` ortam değişkeni (`egitim/siniflar.py`), zincir `egitim/calistir345.ps1`.

## 8. Klasör yapısı (öneri)

```
cizim-tanima/
  docs/          plan.md, durum.md, rapor/
  egitim/        Python: veri indirme, ön işleme, modeller, eğitim, değerlendirme
  veri/          indirilen ve işlenmiş veri (git dışı)
  deneyler/      her deneyin ayarları, kayıtları, şekilleri
  modeller/      .pt ve .onnx
  demo/          tarayıcı demosu ve oyun prototipi (Vite + TypeScript)
  kayitlar/      demoda kaydedilen çizimler (git dışı)
```

## 9. Riskler

- **Oyuncunun çizimi veri setine benzemeyebilir** (telefon parmağı, fare). Önlem: aynı ön işleme, veri artırma, 3d'deki gerçek kullanıcı ölçümü.
- **Anlamsız karalama da bir sınıfa atanır.** Önlem: olasılık eşiği; gerekirse sonra "karalama" sınıfı.
- RTX 50 serisi yalnız `cu128` PyTorch ile çalışır.
- Sandbox'lı iframe'de ONNX Runtime Web (WASM) yükleme ve `null` origin CORS; Aşama 6'da denenecek.

## 10. Açık konular

- ~~50 sınıfın listesi (1b)~~: `egitim/siniflar.py` (kullanıcı listeyi görmeden onay verdi; `anchor` veri setinde yok, yerine `snail`).
- Tanınma eşiği ve puan formülü ilk denemeden sonra ayarlanacak.
