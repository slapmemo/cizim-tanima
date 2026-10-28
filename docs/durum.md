# Çizim Tanıma — çalışma durumu

Plan: [plan.md](plan.md). Rapor taslağı: [rapor/rapor.md](rapor/rapor.md).

## 1a: kurulum ve GPU denemesi (28 Ekim 2026)

- **Ne:** klasörler, Python 3.13.9 sanal ortamı `.venv`, PyTorch 2.11.0+cu128 ve torchvision (`requirements.txt`), `.gitignore`. Git deposu henüz yok.
- **Doğrulama:** `egitim\gpu_dene.py` → CUDA 12.8, RTX 5070 Ti; küçük CNN rastgele veriyle ~248 bin görüntü/sn.
- **Not:** `.venv` 4,3 GB. Yol `OneDrive` içeriyor ama kullanıcıya göre klasör senkronize edilmiyor (eski etiket).

## 1b–1c: sınıflar ve veri (28 Ekim 2026)

- **Sınıflar:** `egitim/siniflar.py`, 50 sınıf, TR/EN ad. Kullanıcı listeyi görmeden onayladı. `anchor` veri setinde yok (404), yerine `snail`.
- **Veri:** `egitim/veri_hazirla.py` → `simplified` ndjson (3,0 GB, `veri/ham/`), yalnız `recognized`, sınıf başına 30k/5k/5k (tohum 1234) → `veri/islenmis/{egitim,dogrulama,test}.npz` (1,5M / 250k / 250k), test vuruşları `test_vuruslar/`. İşleme 91 sn (14 süreç).
- **Ön işleme:** `egitim/onisleme.py` (sınır kutusu → 255 → RDP ε=2 → 28×28, 2 px pay, uzaklık alanıyla çizgi). Örnek görüntülerle bakıldı.

## 2a–2c: eğitim ve karşılaştırma (28 Ekim 2026)

- **Modeller:** `egitim/modeller.py` M1/M2/M3; `egitim/egit.py` (GPU'da veri, AdamW + one-cycle, bf16, artırma GPU'da, `--kismi`). Süre/epoch: M1 5 sn, M2 21–24 sn, M3 53 sn.
- **Test (250k):** M1 %95,22 · M2 artırmasız %97,13 · M2 %96,94 · M3 %97,43 · M3-kısmi %96,50 (ilk-3 %98,8–99,5). Ayrıntı `deneyler/sonuclar.md`, `sonuclar.json`, şekiller `deneyler/`.
- **Erken tanıma** zayıf çıktı (M3: %25 mürekkepte %14,7); plana eklenen M3-kısmi (eğitimde yarım çizim, `egitim/kismi_hazirla.py`) → %40,2 / %76,3 / %91,9 (%25/50/75). Oyun simülasyonu (`egitim/oyun_simulasyonu.py`, 10k çizim): ortalama tanınma anı M3 %56 → M3-kısmi %43 mürekkep.
- **Yapılmayan:** tohum farkıyla tekrar (varyans) ölçülmedi; her model bir kez eğitildi.

## 3a–3d ve 4: ONNX, tarayıcı demosu, oyun prototipi (28 Ekim 2026)

- **ONNX:** `degerlendir.py` softmax dahil aktarır (`modeller/*.onnx`, 1,7–2,7 MB), PyTorch ile en büyük fark < 6e-7.
- **TS ön işleme** `demo/src/onisleme.ts`; eşitlik testi (`npm test`, fikstür `egitim/esitlik_fikstur.py`): 304 örnek, 0 farklı piksel.
- **Demo** `demo/` (Vite 8 + TS, onnxruntime-web 1.31 WASM): Oyun sekmesi (5 tur × 20 sn, model M3-kısmi, tanınma: hedef birinci ve ≥0,5, puan kalan süreyle; kurallar `src/oyun.ts`) ve Serbest çizim (ilk 5 tahmin, 28×28 önizleme, model seçimi, hız testi, "Çizimi kaydet" → Vite ara katmanı `kayitlar/*.json`). CepKonsol görünümü.
- **Doğrulama:** `npm run build` (tsc + vite) temiz. Playwright Chromium (`--mute-audio`, betik scratchpad'de): 5 turluk oyun test setinden çizimlerle oynandı, 5/5 tanındı; serbest çizim, kayıt (deneme kaydı sonra silindi), hız testi (M1 0,29 ms, M2 1,66 ms, M3/M3-kısmi 4,3 ms), 390×844'te yatay taşma yok, konsol hatası yok. Görüntülerle bakıldı; düzeltilen: tanınınca şeritte eski tahmin, soru eki ünlü uyumu (mi/mı/mu/mü), oyun alanında metin seçimi.
- **Yapılmayan:** gerçek telefonda deneme ve telefonda tahmin süresi; gerçek kullanıcı çizimleriyle ölçüm (`kayitlar/` boş; `egitim/gercek_degerlendir.py` hazır); metin seçimi düzeltmesinden sonra tarayıcı denemesi yeniden yapılmadı (yalnız derleme).

## 5: rapor taslağı (28 Ekim 2026)

- `docs/rapor/rapor.md`: giriş, veri ve ön işleme, modeller, sonuçlar (tablolar + `deneyler/` şekilleri), tarayıcı, oyun, sınırlılıklar. §4.7 gerçek kullanıcı ölçümü boş.

## Gerçek kullanıcı ön denemesi (28 Ekim 2026)

- **Ne:** kullanıcı bilgisayarda (fare) oyun oynadı, "Çizimlerimi kaydet" açık: 9 tur, 7 tanındı (%77,8), ortalama 4,1 sn. Tanınmayanlar: gökkuşağı (çapraz düz çizgiler → şimşek %72, pas), şapka (çubuk insana benziyor → ampul %38, süre doldu). Rapor §4.7'ye ön sonuç olarak yazıldı.
- `gercek_degerlendir.py` artık oyun kayıtlarını doğruluğa katmıyor (tanınınca kesildikleri için yanlı), ayrıca özetliyor.
- **Yapılmayan:** Serbest çizim kaydı yok; gerçek kullanıcı doğruluğu ölçülmedi. Telefon denenmedi.

## Arkadaşlardan çizim toplama sayfası (28 Ekim 2026)

- **Karar (kullanıcı):** site Vercel'de (GitHub deposundan), çizimler arkadaşın cihazında dosya olarak oluşur, arkadaş dosyayı kullanıcıya gönderir. Veritabanı yok.
- **Ne:** `demo/topla.html` + `src/topla.ts`: takma ad + onay → 50 nesne kişi başı rastgele sırada, tahmin gizli, "Atla", ilerleme `localStorage`'da (yenilemede sürer), "Bitir ve gönder" her an; sonda modelin bildiği sayı + bilemedikleri, "Gönder" (Web Share, telefonda) ve "Dosyayı indir" (`cizimler-<ad>-<n>.json`). Vite çok sayfalı derleme, `vercel.json` `cleanUrls` (link `/topla`). Yayımlanan ana sayfada yerel kayıt arayüzü gizli (`import.meta.env.DEV`). `gercek_degerlendir.py` toplu dosyaları okuyor (aynı oturumdan en çok çizimli dosya), kişiye ve aygıta göre ayırıyor.
- **Doğrulama:** `npm run build` temiz. Playwright (390×844, derlenmiş site `vite preview`): onaysız Başla kapalı; 2 çizim + atla → 4/50; yenileme sonrası 4/50 ve 2 çizim; çizerken tahmin yok; bitir → "3 çiziminden 3", indirilen dosyada 3 kayıt, 1 atlanan, etiketler doğru, aygıt ve süre var; ana sayfada kayıt arayüzü gizli; konsol hatası yok. Görüntülerle bakıldı.
- **Yapılmayan:** "Gönder" (Web Share) gerçek telefonda denenmedi (headless'ta yok, düğme gizleniyor). Vercel'e yüklenmedi.
- **Git:** depo `cizim-tanima/`, uzak `origin` = https://github.com/slapmemo/cizim-tanima.git, ilk commit `f0e3d8b` (71 dosya, 24,5 MB; veri, `.venv`, `kayitlar/`, `.pt` dışarıda). Commit mesajına imza/Co-Authored-By yok.

## Arkadaş çizimleri ve kişi raporları (28 Ekim 2026)

- **Ne:** `egitim/kisi_raporu.py`: `test-verileri/*.json` (topla.html çıktısı) → `test-verileri/<takma_ad>/` (JSON taşınır, `cizimler.png` tablo, `resimler/NN-<nesne>.png`, `rapor.md`: özet, model bazında doğruluk, bilemedikleri ve ilk 3 tahmin). `gercek_degerlendir.py` `test-verileri/` altını da okuyor. `test-verileri/` git dışı (kişisel veri). Kullanıcı isteğiyle `kastamonufedaisi` dosyası ve takma adı `faruk` yapıldı.
- **Veri (3 kişi):** büş 50 (dokunma) M3-kısmi %78; NECO 50 (fare) %96; faruk 28 (fare) %75. Toplam 129 çizim (1 yerel serbest dahil): M3 %85,3, M3-kısmi %84,5, M1 %77,5 (test setinde %95–97). Rapor §4.7 ara sonuçla güncellendi (katılımcılar A/B/C).
- **Bulgular:** alışılmadık açı/biçim (önden araba, yumruk, sarkaçlı saat, körüklü fotoğraf makinesi), Türkçe etiket belirsizliği ("merdiven" → basamaklı merdiven çizildi; veri setinde el merdiveni), test setindeki karışıklıklar (örümcek→güneş, papyon→kelebek). büş'te 0,3 sn'lik tek çizgi "elmas" (yanlışlıkla kayıt).
- **Açık kararlar (kullanıcıya soruldu):** "merdiven" → "el merdiveni" (siteye gönderim gerekir); 1 sn'den kısa çizimleri ve şaka çizimleri eleme kuralı. Şimdilik hiçbir çizim elenmedi.
- **Sonra gelen (5 kişi):** alper 50 (fare) M3-kısmi 44/50; ömer 50 (fare) 46/50 (`alper` asıl adı yerine, kullanıcı isteğiyle). Toplam 229 çizim (179 fare, 50 dokunma): M3 %88,2, M3-kısmi %86,9, M1 %82,5. "Merdiven" 3 kişide basamaklı çizildi, rakamlı saat 2 kişide pizza. Rapor §4.7 5 kişiyle (A–E) güncellendi.

## 345 sınıf (28 Ekim 2026, plan §7b)

- **Neden:** kullanıcı oyunu çok kolay buldu. Model 345 sınıfın hepsini tanır, oyunda seçilmiş kelimeler sorulur.
- **Ne:** `SINIF_SETI=345` (`siniflar.py` → `siniflar345.py`, TR adlar), veri sınıf başına 20k/2,5k/2,5k → `veri/islenmis345/` (6,9M / 862,5k / 862,5k; etiket `uint16`). Zincir `egitim/calistir345.ps1` (17:23–19:34): yarım çizimler, s345_m1 (10 epoch), s345_m3 ve s345_m3_kismi (15 epoch, artırmalı), değerlendirme, oyun simülasyonu. M3 epoch başına 225 sn.
- **Test (862,5k):** M1 %70,12 · M3 %77,30 · M3-kısmi %75,12 (ilk-3 %87–92). %50 mürekkep: M3 %21,0, M3-kısmi %37,3. Simülasyon: tanınan M3 %79,9 / M3-kısmi %74,2; ortalama tanınma anı %71 / %66. En çok karışan: doğum günü pastası→pasta, kasırga→hortum, keman→gitar, otobüs↔okul otobüsü, bardak→kupa. Ayrıntı `deneyler/sonuclar345.md/json`, şekiller `*345.png`.
- **Oyun kelimeleri:** `egitim/oyun_kelimeleri.py` → `demo/public/model/oyun_kelimeleri.json`, 242 kelime (M3-kısmi doğruluğu ≥ %70; 97 düşük, 6 elle çıkarıldı; liste `deneyler/oyun_kelimeleri.md`).
- **Gerçek kullanıcı (229 çizim, 345 seçenek):** M1 %62,0 · M3 %68,6 · M3-kısmi %68,6 (aynı 50 sınıf test setinde %80–84). Kişi raporları yenilendi (345 sütunları).
- **Demo:** oyun 345 sınıflı `s345_m3_kismi` ile, kelimeler listeden; `s345_*.onnx` `demo/public/model/` altına kopyalandı. Toplama sayfası 50 sınıfla kaldı (`m3_kismi`).
- **Doğrulama:** `npm run build` temiz. Playwright (vite dev, `--mute-audio`): 5 tur, 4 tanındı (zikzak: birinci tahmin doğru ama eşik altı, süre doldu), serbest çizim bisiklet %92, kayıt (deneme kaydı silindi), hız 345: M1 0,25 ms, M3-kısmi 4,37 ms; 390×844 taşma yok, konsol hatası yok. Görüntülere bakılmadı.
- **Rapor:** §1 hedef 5, §4.7 (5 kişi), yeni §4.8 ölçeklendirme, §5 süre tablosu, §6, §7.
- **İki oyun sekmesi (kullanıcı isteği):** "Oyun · 242" (`s345_m3_kismi`, oyun_kelimeleri.json) ve "Oyun · 50" (`m3_kismi`, 50 sınıfın hepsi; `KOLAY_OYUN_MODELI`). Aynı oyun ekranı; sekme değişince süren maç bırakılır, giriş ekranına dönülür (bekleyen tur zamanlayıcısı `turKimligi` ile iptal). Dar ekranda sekme yazıları tek satır. Doğrulama: tsc + build temiz; Playwright iki sekmede 5'er tur (zor 5/5, kolay 5/5 son koşuda), maç ortasında sekme değişimi, 390×844 taşma yok, konsol hatası yok; görüntülere bakıldı.
- **Yapılmayan:** commit/push (`f0e3d8b`, `084c809` sonrası hepsi commit'siz); Vercel deploy doğrulanmadı; telefonda deneme.

## Tanınma eşiği (28 Ekim 2026)

- **Sorun:** 345 sınıfta doğru tahmin %50'ye ulaşmıyordu (ör. "daire" birinci %41, kabul edilmedi). Quick, Draw! kaynak kodu incelendi (`oyun-incelemeleri/quick-draw/`): hedefin birinci olmasını istemiyor, eş anlamlıları kabul ediyor.
- **Ölçüm:** `egitim/esik_karsilastir.py` → `deneyler/esik_karsilastir.md`. 242 sekmesinde %50 → %30: tanınan %83,2 → %89,2, gerçek çizim %72,4 → %77,6, yanlış kabul %0,1 → %0,3, ilk %20'de tanınan %1,2 → %2,5. 50 sekmesinde gevşetme yalnız şans eseri erken tanımayı artırıyor.
- **Karar (kullanıcı):** 242 sekmesi birinci + ≥%30 (`TANIMA_ESIGI_345`), 50 sekmesi %50. "İlk 3'te" kuralı benzer kelimeleri kabul ettiği için seçilmedi.
- **Ek düzeltme:** model yüklenirken sekme değişirse eski maç başlamıyor (`macBasla` modu yakalar).
- **Doğrulama:** tsc, `npm test` (304 örnek, 0 fark), build temiz. Playwright 6 koşu: 242 sekmesinde %44 ile tanınan çizim (dürbün) görüldü; konsol hatası yok. İlk koşulardaki takılma test betiğinden çıktı (tanındıktan sonra çizmeye devam edip sonraki tura taşıyordu); betik düzeltildi, sonra 5 koşu sorunsuz. Uygulamada hedef/model sınıf indisi uyuşmazlığı geçici kayıtla arandı, bulunmadı.
- **Yapılmayan:** commit/push.

## Sıradaki

1. Commit ve push (kullanıcıya sorulacak); Vercel'de oyunun 345 sınıfla çalıştığını doğrula.
2. Açık kararlar: "el merdiveni", eleme kuralı.
3. Telefonda deneme ve hız testi; Web Share.
4. Aşama 6: CepKonsol entegrasyonu ("Çizim Düellosu").
5. ~~Tanınma eşiği~~: karar verildi ve uygulandı (242 sekmesi birinci + ≥%30), [tanima-esigi.md](tanima-esigi.md).
6. **Bakılabilir (sonra karar):** yalnız 242 oyun kelimesiyle model eğitmek (~1 saat). 345'li modelle karşılaştırma rapora "rakip sınıfların etkisi" olarak girer. Beklenen: 242'lik model oyunda daha çok tanır (bardak/kupa gibi rakipler yok), ama kaba çizimleri de en yakın kelimeye bağlar (daha kolay kandırılır). 345'li model "zor" sekmede kalır; 242'lik olursa ayrı sekme ya da kolay mod olabilir.
