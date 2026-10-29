# Çizim Tanıma

CNN tabanlı gerçek zamanlı çizim tanıma oyunu (Sinir Ağları dersi). Veri: Google Quick, Draw! (50 sınıf). Plan [docs/plan.md](docs/plan.md), durum [docs/durum.md](docs/durum.md), rapor taslağı [docs/rapor/rapor.md](docs/rapor/rapor.md).

## Demo / oyun

```sh
cd demo
npm install
npm run dev        # http://localhost:5173 — telefondan denemek için: npm run dev:lan
```

"Çizimi kaydet" yalnız `npm run dev` / `npm run preview` ile çalışır; çizimler `kayitlar/` altına JSON olarak yazılır.

Arkadaşlardan çizim toplama: yayımlanan sitede `/topla` (Vercel, kök klasör `demo`). Gelen `cizimler-*.json` dosyaları `test-verileri/` altına konur.

## Eğitim (Windows, NVIDIA GPU)

```sh
python -m venv .venv
.venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
.venv\Scripts\python.exe -m pip install numpy matplotlib onnx onnxruntime onnxscript

.venv\Scripts\python.exe egitim\veri_hazirla.py      # indir (~3 GB) + 30k/5k/5k ayır + 28x28
.venv\Scripts\python.exe egitim\kismi_hazirla.py     # yarım çizimler (M3-kısmi için)
.venv\Scripts\python.exe egitim\egit.py --ad m1 --model m1 --epoch 10
.venv\Scripts\python.exe egitim\egit.py --ad m2_artirmasiz --model m2 --epoch 20
.venv\Scripts\python.exe egitim\egit.py --ad m2 --model m2 --epoch 20 --artirma
.venv\Scripts\python.exe egitim\egit.py --ad m3 --model m3 --epoch 20 --artirma
.venv\Scripts\python.exe egitim\egit.py --ad m3_kismi --model m3 --epoch 20 --artirma --kismi 0.5
.venv\Scripts\python.exe egitim\degerlendir.py       # test, ONNX, şekiller -> deneyler/
.venv\Scripts\python.exe egitim\dogrulama_vuruslar.py  # doğrulama vuruşları (seçimler doğrulamayla yapılır; 345 için de SINIF_SETI=345 ile)
.venv\Scripts\python.exe egitim\esdeger_aday.py       # eşdeğer grup adayları -> elle demo/public/model/esdeger.json
.venv\Scripts\python.exe egitim\oyun_kelimeleri.py    # oyunda sorulan kelimeler (doğrulama, gruplu)
.venv\Scripts\python.exe egitim\olcum.py              # oyun kuralıyla ölçüm -> deneyler/olcum.md
.venv\Scripts\python.exe egitim\kisi_raporu.py         # test-verileri/*.json -> kişi başına klasör + rapor.md
.venv\Scripts\python.exe egitim\gercek_degerlendir.py  # kayitlar/ + test-verileri/ ile gerçek kullanıcı ölçümü
```

ONNX dosyaları `modeller/` altından `demo/public/model/` altına kopyalanır.

## Ön işleme eşitliği

`egitim/onisleme.py` ve `demo/src/onisleme.ts` aynı algoritmadır. Biri değişirse:

```sh
.venv\Scripts\python.exe egitim\esitlik_fikstur.py
.venv\Scripts\python.exe egitim\kural_fikstur.py      # oyun kuralı (eşik + eşdeğer gruplar), oyun.ts ile oyun_kurali.py
cd demo && npm test
```
