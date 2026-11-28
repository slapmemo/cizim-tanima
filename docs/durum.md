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
- **Yapılmayan:** Vercel deploy doğrulanmadı; telefonda deneme. (Commit'ler sonradan atıldı: `bcdd731` ve sonrası.)

## Tanınma eşiği (28 Ekim 2026)

- **Sorun:** 345 sınıfta doğru tahmin %50'ye ulaşmıyordu (ör. "daire" birinci %41, kabul edilmedi). Quick, Draw! kaynak kodu incelendi (`oyun-incelemeleri/quick-draw/`): hedefin birinci olmasını istemiyor, eş anlamlıları kabul ediyor.
- **Ölçüm:** `egitim/esik_karsilastir.py` → `deneyler/esik_karsilastir.md`. 242 sekmesinde %50 → %30: tanınan %83,2 → %89,2, gerçek çizim %72,4 → %77,6, yanlış kabul %0,1 → %0,3, ilk %20'de tanınan %1,2 → %2,5. 50 sekmesinde gevşetme yalnız şans eseri erken tanımayı artırıyor.
- **Karar (kullanıcı):** 242 sekmesi birinci + ≥%30 (`TANIMA_ESIGI_345`), 50 sekmesi %50. "İlk 3'te" kuralı benzer kelimeleri kabul ettiği için seçilmedi.
- **Ek düzeltme:** model yüklenirken sekme değişirse eski maç başlamıyor (`macBasla` modu yakalar).
- **Doğrulama:** tsc, `npm test` (304 örnek, 0 fark), build temiz. Playwright 6 koşu: 242 sekmesinde %44 ile tanınan çizim (dürbün) görüldü; konsol hatası yok. İlk koşulardaki takılma test betiğinden çıktı (tanındıktan sonra çizmeye devam edip sonraki tura taşıyordu); betik düzeltildi, sonra 5 koşu sorunsuz. Uygulamada hedef/model sınıf indisi uyuşmazlığı geçici kayıtla arandı, bulunmadı.

## Seri modu (28 Ekim 2026)

- **Karar (kullanıcı):** ayrı sekme değil; iki oyun sekmesinin başlangıç ekranında "5 tur" / "60 sn seri" seçimi. 3 ücretsiz pas; sonraki her pas 1 puan düşürür (ikinci karar, önce düğme kapanıyordu).
- **Ne:** `oyun.ts` `SERI_SURESI_MS` 60 sn, `SERI_PAS_HAKKI` 3, `SERI_PAS_CEZASI` 1. Seride süre maç boyunca akar (tanınma bildirimi 0,7 sn, pas 0,3 sn sonra yeni kelime), kelimeler listeden karışık sırayla, puan = tanınan − cezalı pas (eksiye inebilir), üstte "N pas" sonra "pas −1", sonda "N puan" + "M nesne tanıttın" ve liste (✓ süre / pas / pas -1 / süre bitti). Kayıt `mod: "seri"`; `gercek_degerlendir.py` bunları oyun kayıtları gibi doğruluğa katmaz. Telefonda mod etiketi taşması düzeltildi.
- **Doğrulama:** tsc, `npm test`, build temiz. Playwright (`scratchpad/pw/seri.mjs`): iki sekmede 3 pas → "0 pas", düğme kapalı; süre 60,0 sn'de bitti; 50 sekmesinde 8–32 tanınan (test çizimine göre); 242 sekmesinde test çizimi tanınmayınca seri o kelimede kaldı (posta kutusu → şifonyer %21 gibi gerçek model hatası; test yeniden çizmiyor). 5 tur biçimi bozulmadı (`dene.mjs`), 390×844 taşma yok, konsol hatası yok. Görüntülere bakıldı. Test betiğinde 0,7 sn'lik bildirimi kaçırma sorunu bulundu ve düzeltildi.
- **Pas cezası doğrulaması:** `seri2.mjs` iki sekmede 5 pas → "pas −1", puan -2, düğme açık; süre 60,0 sn; sonda "9 puan / 11 nesne" (242) ve "29 puan / 31 nesne" (50); taşma ve konsol hatası yok; görüntüye bakıldı.

## Ölçüm gözden geçirmesi (29 Ekim 2026)

- **Neden:** bir arkadaşın incelemesi (7 madde): test seti seçimde kullanılmış, "yanlış kabul %0,3" kandırılamazlığı göstermiyor, ölçüm betikleri güncel kuralı (%30, çizim boyunca kabul) ölçmüyor, zorluğun bir kısmı ad belirsizliği, M3-kısmi seçimi yalnız tanınanların erkenliğiyle yapılmış, iki oyun hatası. Hepsi koda bakılarak doğrulandı. Öncesi yedek: etiket `yedek-olcum-oncesi` (push'lu) + `FinalCepKonsol/cizim-tanima-yedek-2026-10-29/` (bundle + `test-verileri/` + `kayitlar/`).
- **Oyun hataları (`91b194c`):** Temizle/Geri al süren tahmini geçersiz kılar (`Tuval.silme`), kilit süren çizimi durdurur. Playwright (`scratchpad/hata67.mjs`, olaylar sayfa içinden eş zamanlı): eski kodda 9/10 boş tuvale +100 puan, 5/5 kilitten sonra çizim; yeni kodda 0/10, 0/5.
- **Ölçüm (`6b3f759`):** seçimler doğrulamayla, test yalnız son ölçüm. Doğrulama vuruşları ham veriden aynı tohumla (`dogrulama_vuruslar.py`, 1 185 çizim piksel eşit). Kural tek yerde: `oyun_kurali.py` = `oyun.ts`, eşitlik `npm test` (`kural_fikstur.py`, 600 örnek). `olcum.py`: %5 adım, süre gerçek çizim süresi dağılımından (≤ 20 sn), tur puanı, seri benzetimi, eşleştirilmiş bootstrap, zor çiftler, anlamsız çizimler (karalama, çizgi, üretilmiş), bilinmeyen nesne (kolay sekme). Sonuç `deneyler/olcum.md`. `oyun_simulasyonu.py`, `esik_karsilastir.py` kaldırıldı.
- **Eşdeğer gruplar (kullanıcı: A grubu, "grup tek sınıf"):** `demo/public/model/esdeger.json` 12 grup (pasta, otobüs, hortum, bardak/kupa/fincan, kamyon, radyo, kova, telefon, bilgisayar, araba, yüz, sakal); birinci tahmin grupta + grup toplamı ≥ eşik. Adaylar `deneyler/esdeger_adaylari.md`. Tarayıcıda: bardak sorulunca 40 kupa çiziminden 37 kabul (grupsuz 4).
- **Kelimeler:** doğrulama + grup + oyun modeli (M3-kısmi) ≥ %70 → 258 (önce 242). Testten doğrulamaya geçiş yalnız 16 sınır kelimeyi değiştirdi; ölçülen yanlılık ihmal edilebilir (eski liste test %82,58 / doğrulama %82,57). Sekme adı kelime sayısından (`Oyun · 258`). 50 listesinde `ladder` = "el merdiveni".
- **Sonuçlar (test):** zor sekme M3-kısmi tanınan %90,3, tur puanı 59,8, seri 6,72; M3 %91,0 / 55,8 / 5,98 (tur puanı farkı 4,0 [3,8; 4,1]) → oyun modeli değişmedi, gerekçe artık oyun puanı. Kolay sekme M3-kısmi 74,7 puan, M3 67,4. Eşik %30 doğrulamada da makul (%50'ye göre +5,5 tanınan). Kandırılabilirlik: rastgele hedef %0,36 (şans tabanı 1/257 = %0,39), başka kelimeyle kabul %62, zor çiftler ortalama %33 (M3 %27), karalama belirli hedefle %0,4 (kolay sekmede %4,5, kaçış sınıfı yok). Gerçek çizim (zor, 216): M3-kısmi %80,6, 58,4 puan.
- **Doğrulama:** `npm run build`, `npm test` (eşitlik + kural) geçti; Playwright `dene.mjs` iki sekmede 5'er tur, serbest çizim, kayıt, taşma yok, konsol hatası yok.
- **Rapor:** §2.3 (seçim doğrulamayla), §4.6 yeniden (oyun kuralıyla ölçüm, yöntem), §4.7 (el merdiveni, oyun kuralıyla gerçek), §4.8 (eşdeğer gruplar, kelime seçimi ve yanlılık, yeni tablo), §5 (Temizle/kilit), §6 (eşik tablosu doğrulamadan, kandırılabilirlik), §7. `docs/tanima-esigi.md` başına not.
- **Yapılmayan:** süre modeli gerçek oyun kayıtlarıyla doğrulanmadı; kişi raporları (`kisi_raporu.py`, git dışı) yeniden üretilmedi; kısa/şaka çizim eleme kararı hâlâ açık.

## Rapor tamamlama (29 Ekim 2026)

- `docs/rapor/rapor.md`: Özet, §1.1 İlgili çalışmalar, §7'ye eğitim varyansı, §8 Sonuç, §9 Kaynaklar (21 kaynak, metinde [n] atıfları; hepsi kullanılıyor). "Taslak" ibaresi kaldırıldı. ~6 000 kelime.
- Künyelerin 21'i web'den doğrulandı (yayıncı/konferans/arXiv sayfaları); hata yok, DOI ve sayfa ayrıntıları eklendi.
- **Yapılmayan:** hocanın şablonu/biçimi bilinmiyor (Word/PDF, kapak, sayfa sınırı).



0. **Kullanıcı kararı (29 Ekim 2026): sonra başlatılacak.** Tohum tekrarı (eğitim varyansı): 50 sınıfta M2 artırmasız, M2, M3, M3-kısmi 2'şer ek tohumla (8 eğitim, ~1,5–2 sa GPU). Amaç doğruluk artışı değil, M3 > M2 (0,3–0,5 puan) ve "artırma işe yaramadı" (0,2 puan) farklarının eğitim rastgeleliğinden büyük olup olmadığı. Rapor §4.1 tablosuna ortalama ± sapma, §4.3 ve §7 yorumu. `egit.py --tohum` var (varsayılan 42; yeni eğitimler farklı adla, ör. `m3_t2`); mevcut modeller ve oyun değişmez.
1. Vercel'de iki sekmenin (Oyun · 258 / Oyun · 50), seri modunun ve eşdeğer grupların çalıştığını doğrula.
2. Telefonda deneme ve hız testi; Web Share.
3. Açık karar: 1 sn'den kısa ve şaka çizimlerin elenmesi.
4. Kolay sekmede karalama %4,5 kabul ediliyor: "hiçbiri" sınıfı (karalama + bilinmeyen nesne) ile 50 sınıflı model denemesi rapora girebilir.
5. 242/258 kelimeyle ayrı model eğitimi: ölçüm altyapısı hazır (`olcum.py` aday listesine eklenir); kararı yeni sonuçlara göre ver (zor çiftler M3-kısmi'de zaten %33).
6. Aşama 6: CepKonsol entegrasyonu ("Çizim Düellosu"); seçilen modlar Seri ve Sahtekâr (`plan.md` Aşama 6). Oyun kuralı `oyun.ts` + `esdeger.json` aynen taşınır.

## Sunum (21 Kasım 2026)

- Hoca sunum istedi. Konuşma notları kullanıcıyla birlikte yazıldı: `docs/sunum/konusma-notlari.md` + `.pdf` (13 slayt; söylenecek, hoca sorarsa, kavramlar).
- Üç taslak: `v1-pptx` (pptxgenjs, öneri), `v2-html` (reveal.js), `v3-marp` (Marp PDF). Kullanıcı henüz seçmedi; seçilen düzeltilecek (v1: veri seti slaytı boş; v2: içerik üstte, erken tanıma vurgusu ters; v3: yazılar küçük).
- **Açık:** versiyon seçimi; demo adresi (Vercel); oyun ekranı görüntüsü; kapakta ad/no; 345 sınıflı modelle gerçek kullanıcı yeniden testi (sunuma eski %68,6 konmadı).

## Sunum v5 (27–28 Kasım 2026)

- Slides destesi (37 slayt): https://claude.ai/artifact/LRkddHw8yFkUsyiS8wdwGm · yerel kopya `docs/sunum/v5-slides/` (slayt HTML, görseller, üretim betikleri). Kullanıcı geri bildirimiyle bir kez revize edildi; anlatım metinleri konuşmacı notlarında. Kaynak metin `docs/sunum/sunum-detayli - Kopya.md`.
- Görseller `docs/sunum/gorseller/` (ön işleme adımları, RDP, kavramlar, mimari) ve siteden ekran görüntüleri (puppeteer, `v5-slides/cek.cjs`, `topla.cjs`).
- Ölçülen not: 50 sınıfta `recognized:false` %6; çıkarınca sınıf başına en az 103 bin çizim kaldı.
- `.venv`'e `pymupdf` ve `segno` kuruldu (PDF okuma, QR).

## Sıradaki iş (kullanıcı onayladı, sonra yapılacak)

- Sunum v6 demo slaytına (36) Pratik maddesi eklemek (yöntem kullanıcıya sorulacak).
- Sunumda bekleyen küçük öneriler: 7. slayt "recognized" kartı ("etiketi güvenilmez, %6"), 11. slayt 2 piksel pay gerekçesi, 12. slayt "neden piksele çevirdik" kartı; isteğe bağlı birkaç `recognized:false` örnek çizimi.
- **345 sınıflı modelle arkadaş çizimleri → sunuma ekle:** yeniden ölçüm gerekmiyor; gruplu ve %30 eşikli ölçüm 29 Ekim’de yapıldı (`deneyler/olcum.md`, zor sekme, 216/229 çizim): ilk-1 (grup) M1 %63,0 · M3 %69,4 · M3-kısmi %69,4; oyunda tanınan M1 %75,5 · M3 %80,6 · M3-kısmi %80,6; tur puanı 49,0 / 53,4 / 58,4. 50 nesneden yalnız “araba” bir eşdeğer grupta, gruplar sonucu neredeyse değiştirmiyor (grupsuz %68,6). İş: bu tabloyu sunumun gerçek kullanıcı slaytına eklemek.

## Pratik sekmesi (28 Kasım 2026)

- **Ne:** sitede `Pratik` sekmesi (`demo/index.html`, `demo/src/main.ts`): rastgele kelime ("ARABA ÇİZ"), çizerken ilk 5 tahmin canlı, hedef ve eşdeğer grubu vurgulu, oyun kuralıyla "Tanındı!" (otomatik geçmez; eşik 345 sınıflı modelde %30, 50 sınıflıda %50, oyunla aynı), süre/puan yok; Geri al, Temizle, Örnek çiz, Sonraki kelime; 28×28 model girdisi (168 px); model seçimi (8 model; 50 sınıflıda havuz 50 sınıf, 345'likte oyun listesi 258).
- **Örnek çiz:** `demo/public/model/ornekler.json` (419 KB), her kelimeye test setinden 5 çizim; oyun modeli s345_m3_kismi ile grup birinci ve grup olasılığı ≥ %70 olanlar (daire/kare gibi olasılığı dağılanlarda ≥ %50). Başka model seçiliyken tanınmayabilir.
- **Daire/kare:** önce yanlışlıkla %50 eşiğe göre oyundan çıkarıldı, geri alındı. Test setinde (s345_m3_kismi, tam çizim) %30 eşikle tanınma: daire %48, kare %57 (kedi %68); %50 eşikle %9 / %22.
- **Doğrulama:** `npm run build`, `npm test` temiz; Puppeteer ile yerelde 40 örnek çizimin 40'ı, daire ve karenin 5/5 örneği tanındı; Geri al vuruş vuruş siliyor, örnek canlandırmasını durduruyor; model değiştirme; 390 px'te taşma yok, konsol hatası yok. Gerçek telefonda denenmedi.
- **Sunum v6:** kullanıcının yeni sunumu `docs/sunum/v6 - memo/` (pptx, html, pdf; 36 slayt). 7/11/12 açıklama kartları orada var. Kalan: demo slaytına (36) Pratik maddesi; nasıl düzenleneceği kullanıcıya sorulacak.
