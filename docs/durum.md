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
- **Yapılmayan:** "Gönder" (Web Share) gerçek telefonda denenmedi (headless'ta yok, düğme gizleniyor). Vercel'e yüklenmedi; git deposu yok.

## Sıradaki

1. Kullanıcı ve arkadaşları demoda çizim kaydeder (fare + telefon), `gercek_degerlendir.py` → rapor §4.7.
2. Telefonda deneme (`npm run dev:lan`) ve hız testi.
3. Aşama 6: CepKonsol entegrasyonu ("Çizim Düellosu").
