# Çizim Tanıma

CNN tabanlı gerçek zamanlı çizim tanıma oyunu (Sinir Ağları dersi). Veri: Google Quick, Draw! (50 sınıf). Plan [docs/plan.md](docs/plan.md), durum [docs/durum.md](docs/durum.md), rapor taslağı [docs/rapor/rapor.md](docs/rapor/rapor.md).

## Demo / oyun

```sh
cd demo
npm install
npm run dev        # http://localhost:5173 — telefondan denemek için: npm run dev:lan
```

"Çizimi kaydet" yalnız `npm run dev` / `npm run preview` ile çalışır; çizimler `kayitlar/` altına JSON olarak yazılır.

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
.venv\Scripts\python.exe egitim\oyun_simulasyonu.py
.venv\Scripts\python.exe egitim\gercek_degerlendir.py  # kayitlar/ ile gerçek kullanıcı ölçümü
```

ONNX dosyaları `modeller/` altından `demo/public/model/` altına kopyalanır.

## Ön işleme eşitliği

`egitim/onisleme.py` ve `demo/src/onisleme.ts` aynı algoritmadır. Biri değişirse:

```sh
.venv\Scripts\python.exe egitim\esitlik_fikstur.py
cd demo && npm test
```
