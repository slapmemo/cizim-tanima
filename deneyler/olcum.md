# Oyun ölçümü

`egitim/olcum.py` çıktısı; ölçütler betiğin başında. Doğrulama: seçim (eşik, model, kelime listesi); test: son ölçüm. Mürekkep %5 adımlarla; süre arkadaş çizimlerinin süre dağılımından (≤ 20 sn).

## Sekme zor (oyun modeli s345_m3_kismi, eşik %30)

### Doğrulama (51600 çizim, 258 kelime)

| Model | İlk-1 (grup) | Tanınan | Ort. an | İlk %20'de | Tur puanı | Seri tanınan | Seri puan | Rastgele hedefle kabul | Başka kelimeyle kabul |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| s345_m1 | %77.1 | %85.3 | %69 | %0.5 | 50.6 | 5.25 | 5.24 | %0.76 | %80.2 |
| s345_m3 | %84.1 | %91.1 | %66 | %0.7 | 55.7 | 5.97 | 5.96 | %0.71 | %79.9 |
| s345_m3_kismi (oyun) | %82.8 | %90.2 | %57 | %2.8 | 59.7 | 6.60 | 6.60 | %0.43 | %61.8 |

Eşleştirilmiş fark (s345_m3_kismi'e göre, %95 bootstrap aralığı): s345_m1 tur puanı -9.1 [-9.3, -8.9], tanınan -4.9 puan [-5.2, -4.6]; s345_m3 tur puanı -4.0 [-4.2, -3.8], tanınan +0.9 puan [+0.7, +1.1]

Eşik karşılaştırması (doğrulama):

| Model | Eşik | Tanınan | Ort. an | İlk %20'de | Tur puanı | Başka kelimeyle kabul |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| s345_m1 | %20 | %87.0 | %67 | %0.7 | 52.3 | %86.2 |
| s345_m1 | %25 | %86.3 | %68 | %0.6 | 51.5 | %83.5 |
| s345_m1 | %30 ← | %85.3 | %69 | %0.5 | 50.6 | %80.2 |
| s345_m1 | %35 | %84.0 | %69 | %0.4 | 49.5 | %76.3 |
| s345_m1 | %40 | %82.4 | %70 | %0.4 | 48.2 | %72.0 |
| s345_m1 | %50 | %78.6 | %72 | %0.3 | 45.2 | %62.2 |
| s345_m3 | %20 | %91.8 | %65 | %0.8 | 56.7 | %84.4 |
| s345_m3 | %25 | %91.5 | %65 | %0.7 | 56.3 | %82.5 |
| s345_m3 | %30 ← | %91.1 | %66 | %0.7 | 55.7 | %79.9 |
| s345_m3 | %35 | %90.5 | %66 | %0.6 | 55.1 | %76.8 |
| s345_m3 | %40 | %89.7 | %67 | %0.6 | 54.3 | %73.2 |
| s345_m3 | %50 | %87.5 | %68 | %0.4 | 52.2 | %65.1 |
| s345_m3_kismi | %20 | %91.8 | %55 | %3.9 | 62.1 | %75.5 |
| s345_m3_kismi | %25 | %91.1 | %56 | %3.3 | 60.9 | %68.5 |
| s345_m3_kismi | %30 ← | %90.2 | %57 | %2.8 | 59.7 | %61.8 |
| s345_m3_kismi | %35 | %89.1 | %58 | %2.4 | 58.4 | %55.4 |
| s345_m3_kismi | %40 | %88.0 | %59 | %2.0 | 57.0 | %49.2 |
| s345_m3_kismi | %50 | %84.7 | %62 | %1.4 | 53.8 | %37.0 |

Anlamsız çizimler ve sorulmayan nesneler (doğrulama, eşik %30): "en az bir kelime" = çizimin herhangi bir anında bir oyun kelimesi kabul ediliyor; "rastgele hedef" = rastgele sorulan kelimenin kabul olasılığı.

| Model | Karalama: en az bir / rastgele | Çizgi | Rastgele karalama (üretilmiş) | Sorulmayan nesne: en az bir | Bilinmeyen nesne (kolay sekme) |
| --- | ---: | ---: | ---: | ---: | ---: |
| s345_m1 | %83.8 / %0.66 | %2.4 / %0.01 | %90.4 / %0.98 | %70.4 | - |
| s345_m3 | %80.0 / %0.60 | %2.6 / %0.01 | %92.0 / %0.87 | %70.8 | - |
| s345_m3_kismi | %66.4 / %0.43 | %4.0 / %0.02 | %86.4 / %0.69 | %62.5 | - |

Zor çiftler (doğrulama): A çizilir, B sorulur; kabul oranı. Çiftler doğrulama karışıklığından.

| A → B | Doğrulama karışması | s345_m1 | s345_m3 | s345_m3_kismi |
| --- | ---: | ---: | ---: | ---: |
| altıgen → sekizgen | %27.9 | %30.5 | %29.0 | %49.5 |
| keman → çello | %23.3 | %21.5 | %31.0 | %37.0 |
| tırmık → süpürge | %23.1 | %33.5 | %47.5 | %43.0 |
| motosiklet → bisiklet | %22.6 | %53.5 | %44.5 | %54.0 |
| pastel boya → kurşun kalem | %17.5 | %21.0 | %23.5 | %30.0 |
| gitar → çello | %17.0 | %21.0 | %25.0 | %28.0 |
| kuş → ördek | %16.0 | %22.0 | %27.0 | %32.0 |
| takvim → hesap tablosu | %15.2 | %20.0 | %27.0 | %27.5 |
| ceket → kazak | %15.1 | %53.5 | %56.5 | %63.0 |
| saat → pusula | %14.6 | %15.5 | %24.0 | %31.5 |
| ayı → panda | %14.6 | %12.5 | %15.5 | %23.0 |
| dirsek → kol | %13.9 | %13.0 | %18.0 | %22.5 |
| patates → kurabiye | %13.7 | %6.0 | %13.5 | %16.0 |
| kaplan → zebra | %13.4 | %15.5 | %15.5 | %20.0 |
| pantolon → şort | %12.7 | %15.0 | %16.0 | %22.5 |

### Test (51600 çizim, 258 kelime)

| Model | İlk-1 (grup) | Tanınan | Ort. an | İlk %20'de | Tur puanı | Seri tanınan | Seri puan | Rastgele hedefle kabul | Başka kelimeyle kabul |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| s345_m1 | %77.0 | %85.3 | %69 | %0.5 | 50.7 | 5.31 | 5.31 | %0.70 | %80.3 |
| s345_m3 | %84.1 | %91.0 | %65 | %0.7 | 55.8 | 5.98 | 5.98 | %0.65 | %79.8 |
| s345_m3_kismi (oyun) | %82.8 | %90.3 | %57 | %2.7 | 59.8 | 6.72 | 6.72 | %0.36 | %62.0 |

Eşleştirilmiş fark (s345_m3_kismi'e göre, %95 bootstrap aralığı): s345_m1 tur puanı -9.1 [-9.3, -8.9], tanınan -5.0 puan [-5.3, -4.7]; s345_m3 tur puanı -4.0 [-4.1, -3.8], tanınan +0.7 puan [+0.5, +0.9]

Eşik karşılaştırması (test):

| Model | Eşik | Tanınan | Ort. an | İlk %20'de | Tur puanı | Başka kelimeyle kabul |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| s345_m1 | %20 | %87.1 | %67 | %0.6 | 52.3 | %86.2 |
| s345_m1 | %25 | %86.3 | %68 | %0.6 | 51.6 | %83.6 |
| s345_m1 | %30 ← | %85.3 | %69 | %0.5 | 50.7 | %80.3 |
| s345_m1 | %35 | %84.0 | %69 | %0.4 | 49.6 | %76.3 |
| s345_m1 | %40 | %82.6 | %70 | %0.3 | 48.4 | %71.9 |
| s345_m1 | %50 | %78.7 | %72 | %0.2 | 45.3 | %61.9 |
| s345_m3 | %20 | %91.8 | %64 | %0.8 | 56.7 | %84.3 |
| s345_m3 | %25 | %91.5 | %65 | %0.8 | 56.3 | %82.4 |
| s345_m3 | %30 ← | %91.0 | %65 | %0.7 | 55.8 | %79.8 |
| s345_m3 | %35 | %90.3 | %66 | %0.6 | 55.1 | %76.8 |
| s345_m3 | %40 | %89.5 | %66 | %0.5 | 54.3 | %73.2 |
| s345_m3 | %50 | %87.3 | %68 | %0.4 | 52.2 | %64.9 |
| s345_m3_kismi | %20 | %91.8 | %55 | %3.9 | 62.1 | %75.5 |
| s345_m3_kismi | %25 | %91.1 | %56 | %3.3 | 61.0 | %68.4 |
| s345_m3_kismi | %30 ← | %90.3 | %57 | %2.7 | 59.8 | %62.0 |
| s345_m3_kismi | %35 | %89.3 | %58 | %2.4 | 58.5 | %55.6 |
| s345_m3_kismi | %40 | %88.0 | %59 | %2.0 | 57.0 | %49.3 |
| s345_m3_kismi | %50 | %84.8 | %62 | %1.4 | 53.8 | %37.2 |

Anlamsız çizimler ve sorulmayan nesneler (test, eşik %30): "en az bir kelime" = çizimin herhangi bir anında bir oyun kelimesi kabul ediliyor; "rastgele hedef" = rastgele sorulan kelimenin kabul olasılığı.

| Model | Karalama: en az bir / rastgele | Çizgi | Rastgele karalama (üretilmiş) | Sorulmayan nesne: en az bir | Bilinmeyen nesne (kolay sekme) |
| --- | ---: | ---: | ---: | ---: | ---: |
| s345_m1 | %85.8 / %0.68 | %2.8 / %0.02 | %88.2 / %0.93 | %70.7 | - |
| s345_m3 | %82.8 / %0.61 | %2.6 / %0.02 | %92.0 / %0.86 | %71.4 | - |
| s345_m3_kismi | %64.8 / %0.40 | %3.4 / %0.02 | %85.2 / %0.71 | %61.8 | - |

Zor çiftler (test): A çizilir, B sorulur; kabul oranı. Çiftler doğrulama karışıklığından.

| A → B | Doğrulama karışması | s345_m1 | s345_m3 | s345_m3_kismi |
| --- | ---: | ---: | ---: | ---: |
| altıgen → sekizgen | %27.9 | %23.0 | %23.0 | %37.0 |
| keman → çello | %23.3 | %17.0 | %19.0 | %25.5 |
| tırmık → süpürge | %23.1 | %43.5 | %55.5 | %53.5 |
| motosiklet → bisiklet | %22.6 | %44.0 | %39.0 | %47.5 |
| pastel boya → kurşun kalem | %17.5 | %16.0 | %19.0 | %23.0 |
| gitar → çello | %17.0 | %27.0 | %27.0 | %35.0 |
| kuş → ördek | %16.0 | %24.5 | %27.0 | %38.5 |
| takvim → hesap tablosu | %15.2 | %22.0 | %26.5 | %29.5 |
| ceket → kazak | %15.1 | %54.0 | %56.0 | %64.5 |
| saat → pusula | %14.6 | %15.0 | %23.0 | %32.5 |
| ayı → panda | %14.6 | %13.5 | %27.0 | %28.0 |
| dirsek → kol | %13.9 | %13.0 | %19.5 | %23.0 |
| patates → kurabiye | %13.7 | %10.5 | %14.5 | %17.0 |
| kaplan → zebra | %13.4 | %22.0 | %14.5 | %25.0 |
| pantolon → şort | %12.7 | %12.5 | %15.0 | %19.0 |

### Gerçek kullanıcı çizimleri (216 çizim; toplam 229, 13 çizimin kelimesi bu sekmede sorulmuyor)

| Model | İlk-1 (grup) | Tanınan | Ort. an | İlk %20'de | Tur puanı | Rastgele hedefle kabul | Başka kelimeyle kabul |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| s345_m1 | %63.0 | %75.5 | %61 | %4.2 | 49.0 | %0.46 | %79.2 |
| s345_m3 | %69.4 | %80.6 | %59 | %4.2 | 53.4 | %0.46 | %80.1 |
| s345_m3_kismi (oyun) | %69.4 | %80.6 | %49 | %7.9 | 58.4 | %0.46 | %66.7 |

## Sekme kolay (oyun modeli m3_kismi, eşik %50)

### Doğrulama (25000 çizim, 50 kelime)

| Model | İlk-1 (grup) | Tanınan | Ort. an | İlk %20'de | Tur puanı | Seri tanınan | Seri puan | Rastgele hedefle kabul | Başka kelimeyle kabul |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| m1 | %95.2 | %98.1 | %56 | %4.1 | 65.8 | 7.67 | 7.67 | %3.76 | %82.7 |
| m2 | %97.0 | %98.9 | %54 | %4.0 | 67.3 | 8.00 | 8.00 | %3.32 | %80.8 |
| m3 | %97.4 | %99.0 | %54 | %3.7 | 67.4 | 8.06 | 8.06 | %3.01 | %77.6 |
| m3_kismi (oyun) | %96.6 | %98.6 | %40 | %17.2 | 74.9 | 10.41 | 10.41 | %1.93 | %60.0 |

Eşleştirilmiş fark (m3_kismi'e göre, %95 bootstrap aralığı): m1 tur puanı -9.2 [-9.4, -9.0], tanınan -0.4 puan [-0.6, -0.2]; m2 tur puanı -7.6 [-7.8, -7.4], tanınan +0.3 puan [+0.2, +0.5]; m3 tur puanı -7.5 [-7.7, -7.4], tanınan +0.5 puan [+0.3, +0.6]

Eşik karşılaştırması (doğrulama):

| Model | Eşik | Tanınan | Ort. an | İlk %20'de | Tur puanı | Başka kelimeyle kabul |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m1 | %20 | %98.7 | %51 | %9.9 | 68.9 | %95.1 |
| m1 | %25 | %98.6 | %52 | %8.5 | 68.4 | %93.2 |
| m1 | %30 | %98.6 | %52 | %7.2 | 67.9 | %91.2 |
| m1 | %35 | %98.5 | %53 | %6.2 | 67.4 | %89.2 |
| m1 | %40 | %98.4 | %54 | %5.2 | 66.9 | %87.1 |
| m1 | %50 ← | %98.1 | %56 | %4.1 | 65.8 | %82.7 |
| m2 | %20 | %99.1 | %50 | %7.9 | 69.5 | %95.7 |
| m2 | %25 | %99.1 | %51 | %7.2 | 69.3 | %94.8 |
| m2 | %30 | %99.1 | %51 | %6.5 | 68.9 | %93.7 |
| m2 | %35 | %99.0 | %52 | %5.8 | 68.6 | %92.6 |
| m2 | %40 | %99.0 | %52 | %4.9 | 68.2 | %84.9 |
| m2 | %50 ← | %98.9 | %54 | %4.0 | 67.3 | %80.8 |
| m3 | %20 | %99.2 | %50 | %7.3 | 69.5 | %88.3 |
| m3 | %25 | %99.2 | %51 | %6.5 | 69.2 | %86.3 |
| m3 | %30 | %99.2 | %51 | %5.8 | 68.9 | %84.7 |
| m3 | %35 | %99.2 | %52 | %5.2 | 68.6 | %83.1 |
| m3 | %40 | %99.1 | %53 | %4.7 | 68.2 | %81.4 |
| m3 | %50 ← | %99.0 | %54 | %3.7 | 67.4 | %77.6 |
| m3_kismi | %20 | %99.2 | %33 | %30.7 | 79.5 | %97.6 |
| m3_kismi | %25 | %99.1 | %34 | %28.7 | 79.0 | %96.0 |
| m3_kismi | %30 | %99.0 | %35 | %26.5 | 78.2 | %91.7 |
| m3_kismi | %35 | %98.9 | %36 | %23.9 | 77.5 | %84.2 |
| m3_kismi | %40 | %98.9 | %38 | %21.0 | 76.6 | %73.4 |
| m3_kismi | %50 ← | %98.6 | %40 | %17.2 | 74.9 | %60.0 |

Anlamsız çizimler ve sorulmayan nesneler (doğrulama, eşik %50): "en az bir kelime" = çizimin herhangi bir anında bir oyun kelimesi kabul ediliyor; "rastgele hedef" = rastgele sorulan kelimenin kabul olasılığı.

| Model | Karalama: en az bir / rastgele | Çizgi | Rastgele karalama (üretilmiş) | Sorulmayan nesne: en az bir | Bilinmeyen nesne (kolay sekme) |
| --- | ---: | ---: | ---: | ---: | ---: |
| m1 | %99.4 / %5.37 | %7.6 / %0.18 | %98.4 / %6.70 | - | %98.0 / %6.07 |
| m2 | %99.6 / %4.69 | %10.2 / %0.23 | %98.4 / %5.60 | - | %97.9 / %5.65 |
| m3 | %99.0 / %4.48 | %5.2 / %0.14 | %98.4 / %5.26 | - | %97.6 / %5.38 |
| m3_kismi | %98.0 / %4.58 | %14.2 / %0.37 | %97.6 / %5.05 | - | %97.6 / %4.94 |

Zor çiftler (doğrulama): A çizilir, B sorulur; kabul oranı. Çiftler doğrulama karışıklığından.

| A → B | Doğrulama karışması | m1 | m2 | m3 | m3_kismi |
| --- | ---: | ---: | ---: | ---: | ---: |
| ay → muz | %9.2 | %17.0 | %19.0 | %19.4 | %21.8 |
| muz → ay | %3.2 | %25.6 | %21.6 | %20.8 | %16.4 |
| ay → pizza | %2.8 | %3.6 | %3.8 | %5.2 | %5.8 |
| örümcek → güneş | %2.7 | %18.8 | %16.2 | %15.8 | %10.0 |
| güneş → örümcek | %2.6 | %8.0 | %6.6 | %7.4 | %13.8 |
| elmas → dondurma | %2.3 | %3.6 | %2.2 | %1.8 | %10.2 |
| mantar → şemsiye | %1.8 | %21.8 | %21.8 | %19.8 | %16.4 |
| kuş → uçak | %1.7 | %4.4 | %3.0 | %2.8 | %7.4 |
| şemsiye → mantar | %1.6 | %11.8 | %8.8 | %10.2 | %9.0 |
| çiçek → ağaç | %1.4 | %14.6 | %12.6 | %11.8 | %8.2 |
| mantar → ağaç | %1.4 | %3.8 | %3.8 | %2.0 | %9.2 |
| dağ → taç | %1.4 | %1.4 | %1.0 | %0.8 | %6.6 |
| anahtar → gitar | %1.3 | %4.8 | %1.6 | %2.4 | %8.6 |
| ağaç → çiçek | %1.3 | %5.2 | %4.4 | %4.2 | %8.0 |
| kapı → kitap | %1.3 | %5.6 | %2.6 | %2.2 | %4.2 |

### Test (25000 çizim, 50 kelime)

| Model | İlk-1 (grup) | Tanınan | Ort. an | İlk %20'de | Tur puanı | Seri tanınan | Seri puan | Rastgele hedefle kabul | Başka kelimeyle kabul |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| m1 | %95.2 | %98.1 | %56 | %4.0 | 65.7 | 7.66 | 7.66 | %3.56 | %83.0 |
| m2 | %96.9 | %98.8 | %54 | %4.1 | 67.3 | 8.09 | 8.09 | %3.23 | %81.0 |
| m3 | %97.5 | %98.9 | %54 | %3.8 | 67.4 | 8.12 | 8.12 | %2.94 | %77.8 |
| m3_kismi (oyun) | %96.4 | %98.4 | %40 | %17.1 | 74.7 | 10.28 | 10.28 | %1.81 | %60.5 |

Eşleştirilmiş fark (m3_kismi'e göre, %95 bootstrap aralığı): m1 tur puanı -9.0 [-9.2, -8.8], tanınan -0.3 puan [-0.5, -0.1]; m2 tur puanı -7.4 [-7.6, -7.2], tanınan +0.5 puan [+0.3, +0.6]; m3 tur puanı -7.3 [-7.5, -7.2], tanınan +0.6 puan [+0.4, +0.7]

Eşik karşılaştırması (test):

| Model | Eşik | Tanınan | Ort. an | İlk %20'de | Tur puanı | Başka kelimeyle kabul |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| m1 | %20 | %98.6 | %51 | %10.1 | 68.8 | %95.0 |
| m1 | %25 | %98.5 | %52 | %8.5 | 68.3 | %93.2 |
| m1 | %30 | %98.5 | %52 | %7.2 | 67.8 | %91.3 |
| m1 | %35 | %98.4 | %53 | %6.1 | 67.3 | %89.4 |
| m1 | %40 | %98.3 | %54 | %5.2 | 66.8 | %87.3 |
| m1 | %50 ← | %98.1 | %56 | %4.0 | 65.7 | %83.0 |
| m2 | %20 | %99.1 | %50 | %7.8 | 69.4 | %95.4 |
| m2 | %25 | %99.0 | %51 | %7.1 | 69.2 | %94.4 |
| m2 | %30 | %99.0 | %51 | %6.4 | 68.9 | %93.4 |
| m2 | %35 | %99.0 | %52 | %5.8 | 68.5 | %92.4 |
| m2 | %40 | %98.9 | %52 | %4.9 | 68.1 | %84.9 |
| m2 | %50 ← | %98.8 | %54 | %4.1 | 67.3 | %81.0 |
| m3 | %20 | %99.1 | %50 | %7.5 | 69.5 | %88.2 |
| m3 | %25 | %99.1 | %51 | %6.6 | 69.2 | %86.3 |
| m3 | %30 | %99.1 | %51 | %5.9 | 68.8 | %84.5 |
| m3 | %35 | %99.1 | %52 | %5.3 | 68.5 | %83.0 |
| m3 | %40 | %99.0 | %53 | %4.8 | 68.2 | %81.4 |
| m3 | %50 ← | %98.9 | %54 | %3.8 | 67.4 | %77.8 |
| m3_kismi | %20 | %99.1 | %33 | %30.7 | 79.4 | %97.7 |
| m3_kismi | %25 | %99.0 | %34 | %28.6 | 78.8 | %96.1 |
| m3_kismi | %30 | %98.9 | %36 | %26.3 | 78.1 | %91.9 |
| m3_kismi | %35 | %98.8 | %37 | %23.8 | 77.3 | %84.5 |
| m3_kismi | %40 | %98.7 | %38 | %20.9 | 76.3 | %73.6 |
| m3_kismi | %50 ← | %98.4 | %40 | %17.1 | 74.7 | %60.5 |

Anlamsız çizimler ve sorulmayan nesneler (test, eşik %50): "en az bir kelime" = çizimin herhangi bir anında bir oyun kelimesi kabul ediliyor; "rastgele hedef" = rastgele sorulan kelimenin kabul olasılığı.

| Model | Karalama: en az bir / rastgele | Çizgi | Rastgele karalama (üretilmiş) | Sorulmayan nesne: en az bir | Bilinmeyen nesne (kolay sekme) |
| --- | ---: | ---: | ---: | ---: | ---: |
| m1 | %99.4 / %5.42 | %5.8 / %0.18 | %99.4 / %7.08 | - | %98.4 / %6.09 |
| m2 | %99.8 / %4.69 | %7.2 / %0.18 | %99.2 / %5.92 | - | %98.2 / %5.67 |
| m3 | %99.8 / %4.63 | %4.8 / %0.15 | %99.0 / %5.35 | - | %97.8 / %5.44 |
| m3_kismi | %98.0 / %4.48 | %10.2 / %0.28 | %99.0 / %5.26 | - | %98.0 / %4.94 |

Zor çiftler (test): A çizilir, B sorulur; kabul oranı. Çiftler doğrulama karışıklığından.

| A → B | Doğrulama karışması | m1 | m2 | m3 | m3_kismi |
| --- | ---: | ---: | ---: | ---: | ---: |
| ay → muz | %9.2 | %13.2 | %15.8 | %14.4 | %20.0 |
| muz → ay | %3.2 | %27.8 | %25.0 | %21.6 | %20.0 |
| ay → pizza | %2.8 | %2.8 | %2.6 | %2.8 | %4.2 |
| örümcek → güneş | %2.7 | %20.4 | %17.0 | %15.6 | %11.0 |
| güneş → örümcek | %2.6 | %8.6 | %6.8 | %4.8 | %15.4 |
| elmas → dondurma | %2.3 | %3.2 | %1.8 | %1.0 | %6.8 |
| mantar → şemsiye | %1.8 | %25.8 | %27.0 | %24.4 | %17.8 |
| kuş → uçak | %1.7 | %5.0 | %3.8 | %2.4 | %6.4 |
| şemsiye → mantar | %1.6 | %11.6 | %8.0 | %10.4 | %7.0 |
| çiçek → ağaç | %1.4 | %14.4 | %13.0 | %11.8 | %8.4 |
| mantar → ağaç | %1.4 | %6.0 | %5.4 | %5.0 | %9.4 |
| dağ → taç | %1.4 | %0.8 | %0.8 | %0.8 | %6.8 |
| anahtar → gitar | %1.3 | %4.2 | %1.4 | %2.0 | %6.6 |
| ağaç → çiçek | %1.3 | %6.6 | %6.8 | %5.4 | %9.6 |
| kapı → kitap | %1.3 | %6.2 | %3.2 | %1.8 | %4.8 |

### Gerçek kullanıcı çizimleri (229 çizim; toplam 229, 0 çizimin kelimesi bu sekmede sorulmuyor)

| Model | İlk-1 (grup) | Tanınan | Ort. an | İlk %20'de | Tur puanı | Rastgele hedefle kabul | Başka kelimeyle kabul |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| m1 | %82.5 | %88.2 | %50 | %9.2 | 63.7 | %4.37 | %87.8 |
| m2 | %85.6 | %90.0 | %49 | %8.7 | 65.2 | %3.93 | %89.1 |
| m3 | %88.2 | %92.6 | %50 | %8.7 | 65.7 | %3.49 | %86.0 |
| m3_kismi (oyun) | %86.9 | %93.0 | %38 | %27.1 | 73.3 | %2.62 | %74.7 |

