# Tanınma kuralı karşılaştırması

Ölçüt açıklamaları `egitim/esik_karsilastir.py` başında. Test çizimleri %10'luk mürekkep adımlarıyla ilerletildi; "yanlış kabul": aynı çizime rastgele başka bir oyun kelimesi soruldu sayılır.

### s345_m3_kismi — 242 oyun kelimesi, 12100 test çizimi; gerçek: 228 çizim

| Kural | Tanınan | Ortalama an | İlk %20'de | Yanlış kabul | Gerçek çizim tanınan |
| --- | ---: | ---: | ---: | ---: | ---: |
| birinci + ≥%50 (şimdiki) | %83.2 | %65 | %1.2 | %0.1 | %72.4 |
| birinci + ≥%40 | %86.6 | %63 | %1.7 | %0.2 | %75.0 |
| birinci + ≥%35 | %88.1 | %62 | %2.0 | %0.3 | %76.3 |
| birinci + ≥%30 | %89.2 | %60 | %2.5 | %0.3 | %77.6 |
| birinci + ≥%25 | %90.1 | %59 | %2.9 | %0.4 | %78.5 |
| birinci + ikinciden ≥10 puan önde | %88.7 | %60 | %2.8 | %0.4 | %76.8 |
| birinci + ikinciden ≥20 puan önde | %85.8 | %62 | %1.9 | %0.2 | %75.0 |
| ilk 3'te + ≥%20 (Quick, Draw! benzeri) | %93.3 | %56 | %4.2 | %0.6 | %82.0 |
| ilk 3'te + ≥%15 (Quick, Draw! benzeri) | %94.8 | %53 | %5.8 | %0.9 | %84.2 |

### m3_kismi — 50 oyun kelimesi, 2500 test çizimi; gerçek: 228 çizim

| Kural | Tanınan | Ortalama an | İlk %20'de | Yanlış kabul | Gerçek çizim tanınan |
| --- | ---: | ---: | ---: | ---: | ---: |
| birinci + ≥%50 (şimdiki) | %98.3 | %43 | %17.2 | %1.2 | %92.5 |
| birinci + ≥%40 | %98.6 | %41 | %21.4 | %1.6 | %93.0 |
| birinci + ≥%35 | %98.8 | %40 | %24.2 | %1.9 | %93.0 |
| birinci + ≥%30 | %98.9 | %38 | %26.4 | %2.3 | %93.0 |
| birinci + ≥%25 | %99.0 | %37 | %28.7 | %2.6 | %93.9 |
| birinci + ikinciden ≥10 puan önde | %98.8 | %39 | %25.5 | %2.2 | %92.1 |
| birinci + ikinciden ≥20 puan önde | %98.4 | %42 | %20.7 | %1.4 | %91.2 |
| ilk 3'te + ≥%20 (Quick, Draw! benzeri) | %99.5 | %34 | %37.2 | %5.0 | %94.7 |
| ilk 3'te + ≥%15 (Quick, Draw! benzeri) | %99.6 | %31 | %44.6 | %7.0 | %95.6 |

