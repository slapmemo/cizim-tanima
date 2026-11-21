---
marp: true
size: 16:9
paginate: true
title: CNN ile Gerçek Zamanlı Çizim Tanıma
style: |
  section {
    background: #fbf8f1;
    color: #222;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 25px;
    padding: 50px 70px 56px 70px;
    line-height: 1.4;
  }
  h1, h2, h3 { font-family: Georgia, "Source Serif 4", "Times New Roman", serif; color: #1f2a44; font-weight: 700; }
  h1 { font-size: 52px; margin: 0 0 10px 0; }
  h2 { font-size: 38px; margin: 0 0 22px 0; padding-bottom: 10px; border-bottom: 1px solid #b9b2a0; }
  h3 { font-size: 26px; margin: 0 0 8px 0; }
  section::after { font-family: Georgia, serif; font-size: 18px; color: #7a7466; }
  ul { margin: 6px 0; padding-left: 26px; }
  li { margin: 5px 0; }
  table { border-collapse: collapse; font-size: 23px; margin: 8px 0; }
  th, td { border: none; border-bottom: 1px solid #cfc8b6; padding: 6px 16px; background: transparent; }
  th { border-top: 2px solid #1f2a44; border-bottom: 1px solid #1f2a44; font-weight: 600; color: #1f2a44; }
  tr:last-child td { border-bottom: 2px solid #1f2a44; }
  td:not(:first-child), th:not(:first-child) { text-align: right; }
  .cols { display: flex; gap: 44px; }
  .cols > div { flex: 1; }
  .ph { background: #e3e1dc; border: 1px dashed #9b978c; color: #5f5c54; display: flex; align-items: center; justify-content: center; text-align: center; min-height: 300px; font-style: italic; }
  .muted { color: #6b665a; font-size: 21px; }
  .key { border-left: 3px solid #8a2c2c; padding: 4px 0 4px 16px; font-family: Georgia, serif; font-size: 27px; margin-top: 18px; }
  .hb { display: flex; align-items: center; margin: 9px 0; }
  .hb .l { width: 210px; font-size: 22px; }
  .hb .t { flex: 1; }
  .hb .b { height: 30px; background: #9aa3b8; }
  .hb .b.w { background: #1f2a44; }
  .hb .v { width: 80px; padding-left: 10px; font-weight: 600; font-size: 22px; }
  .vc { display: flex; gap: 40px; align-items: flex-end; height: 300px; border-bottom: 1px solid #222; padding: 0 10px; }
  .grp { display: flex; flex-direction: column; align-items: center; justify-content: flex-end; }
  .pair { display: flex; gap: 8px; align-items: flex-end; }
  .col { width: 62px; background: #9aa3b8; position: relative; }
  .col.w { background: #8a2c2c; }
  .col span { position: absolute; top: -26px; left: -8px; right: -8px; text-align: center; font-size: 18px; font-weight: 600; }
  .xl { display: flex; gap: 40px; padding: 4px 10px; }
  .xl div { text-align: center; font-family: Georgia, serif; font-size: 22px; }
  .leg { font-size: 20px; margin-top: 8px; }
  .leg i { display: inline-block; width: 14px; height: 14px; background: #9aa3b8; margin: 0 6px 0 14px; }
  .leg i.w { background: #8a2c2c; }
  .big { display: flex; gap: 30px; margin: 20px 0; }
  .big div { flex: 1; text-align: center; border-top: 2px solid #1f2a44; border-bottom: 1px solid #b9b2a0; padding: 16px 0; }
  .big b { display: block; font-family: Georgia, serif; font-size: 58px; color: #1f2a44; }
  .flow { display: flex; align-items: center; justify-content: center; gap: 18px; font-family: Georgia, serif; font-size: 28px; margin-top: 24px; }
  .flow span { border: 1px solid #1f2a44; padding: 8px 22px; }
  .cover { display: flex; flex-direction: column; justify-content: center; }
  .cover hr { width: 160px; margin: 20px 0; border: 0; border-top: 2px solid #8a2c2c; }
---

<!-- _class: cover -->
<!-- _paginate: false -->

# CNN ile Gerçek Zamanlı Çizim Tanıma

<hr>

### Sinir Ağları dersi projesi

<p class="muted">[Ad Soyad] · [Öğrenci no] · Kasım 2026</p>

<!--
Bu projede, oyuncunun ekrana çizdiği nesneyi çizim sürerken tanıyan, tarayıcıda sunucusuz çalışan, evrişimli sinir ağı (CNN) tabanlı bir çizim oyunu geliştirdik.
-->

---

## 1 · Amaç

<div class="cols">
<div>

- Çizim sürerken nesneyi tanıyan **CNN tabanlı oyun**
- Tarayıcıda, sunucusuz çalışır
- Kural: kelime gelir, **20 sn** içinde çiz
- **Puan = 100 × kalan süre / 20 sn**
- Neden anlık? Erken tanıma = puan; model yarım çizimi de tanımalı

</div>
<div class="ph">[oyun ekranı görüntüsü]</div>
</div>

<!--
Model tanıyınca tur biter. Eğitime yarım çizim ekledik (5. bölüm).
Hoca sorarsa: Tarayıcıda nasıl? Model ONNX'e çevrildi, tek tahmin ~5 ms. CNN nedir? Küçük filtrelerle çizgi, köşe, kavis gibi desenleri yakalayan sinir ağı; çizimi 28×28 görüntüye çevirip veriyoruz.
-->

---

## 2 · Veri seti

<div class="cols">
<div>

- **Quick, Draw!** (Google): **345 sınıf**, **50 milyon+** çizim
- Çizimler kalem hareketi (vuruş) olarak saklı
- Önce **50 sınıf**: çizilebilir · benzemeyen · Türkçe adı açık
- Sınıf başına bölme:

| Eğitim | Doğrulama | Test |
|---:|---:|---:|
| 30 000 | 5 000 | 5 000 |

</div>
<div>

### Vuruştan görüntüye

- Tek algoritma, iki dil
- Python (eğitim) = TypeScript (oyun)
- **304 örnekte 0 farklı piksel**

</div>
</div>

<!--
recognized: Google'ın modeli tanıyabilmiş mi; yalnız tanınanlar kullanıldı (kötü çizimler veride yok). Eğitim: öğrenir; doğrulama: ayar ve seçim; test: en sonda bir kez. Hazır 28×28 görüntüler kullanılmadı: oyunda aynı dönüşüm yapılamazdı.
Hoca sorarsa: Test neden en sonda? Seçimi testle yaparsak sonuç iyimser olur. Sınıflar dengeli mi? Evet, eşit sayı.
-->

---

## 3 · Modeller

| Model | Yapı | Parametre |
|---|---|---:|
| **M1** Basit CNN | 2 evrişim + havuzlama, tam bağlı katman (taban) | 427 bin |
| **M2** Derin CNN | Daha çok evrişim, BatchNorm, Dropout; artırmalı / artırmasız | 595 bin |
| **M3** Hafif ResNet | Artık (residual) bağlantılı küçük ResNet | 701 bin |
| **M3-kısmi** | M3 ile aynı mimari, eğitimde yarım çizim de var | 701 bin |

<p class="muted">Amaç: mimarinin ne kadar fark yarattığını görmek.</p>

<!--
Evrişim: gezen 3×3 filtre. Havuzlama: küçültür. Parametre: öğrenilen sayılar, 400–700 bin, tarayıcıda hızlı. BatchNorm: eğitim hızlı ve kararlı. Dropout: ezberi azaltır. Artık bağlantı: bilgi kaybolmadan akar.
Hoca sorarsa: Neden büyük hazır model yok? Her 250 ms'de çalışacak, küçük ve hızlı olmalı; giriş 28×28. Eğitim: AdamW, 20 epoch (M1 10), yığın 512, RTX 5070 Ti.
-->

---

## 4 · 50 sınıf sonuçları — hata oranı (%)

<div class="hb"><div class="l">M1</div><div class="t"><div class="b" style="width:95.6%"></div></div><div class="v">4,78</div></div>
<div class="hb"><div class="l">M2 artırmasız</div><div class="t"><div class="b" style="width:57.4%"></div></div><div class="v">2,87</div></div>
<div class="hb"><div class="l">M2 artırmalı</div><div class="t"><div class="b" style="width:61.2%"></div></div><div class="v">3,06</div></div>
<div class="hb"><div class="l">M3</div><div class="t"><div class="b w" style="width:51.4%"></div></div><div class="v">2,57</div></div>
<div class="hb"><div class="l">M3-kısmi</div><div class="t"><div class="b" style="width:70%"></div></div><div class="v">3,50</div></div>

- M1 → M2: hata neredeyse yarıya (4,8 → 2,9)
- M2 → M3: yalnız 0,3 puan kazanç, M3 2,5 kat yavaş
- Her model bir kez eğitildi; küçük farklar kesin değil

<p class="muted">Test seti: 250 000 çizim.</p>

<!--
Veri artırma test setinde işe yaramadı (−0,19 puan): 30 000 çizim zaten çeşitli; asıl yararı gerçek kullanıcıda beklenir. M3-kısmi tam çizimde 0,9 puan geride; neden seçildiği 5. bölümde.
Hoca sorarsa: En çok karışan? ay ↔ muz, örümcek ↔ güneş, mantar ↔ şemsiye. Aşırı öğrenme? M1'de biraz (eğitim %97, doğrulama %95); M2 ve M3'te eğriler yakın.
-->

---

## 5a · Erken tanıma — doğruluk (%)

<div class="vc">
<div class="grp"><div class="pair"><div class="col" style="height:38.2px"><span>14,7</span></div><div class="col w" style="height:104.5px"><span>40,2</span></div></div></div>
<div class="grp"><div class="pair"><div class="col" style="height:131.3px"><span>50,5</span></div><div class="col w" style="height:198.4px"><span>76,3</span></div></div></div>
<div class="grp"><div class="pair"><div class="col" style="height:226.5px"><span>87,1</span></div><div class="col w" style="height:239px"><span>91,9</span></div></div></div>
<div class="grp"><div class="pair"><div class="col" style="height:253.2px"><span>97,4</span></div><div class="col w" style="height:250.9px"><span>96,5</span></div></div></div>
</div>
<div class="xl"><div style="width:140px">%25</div><div style="width:140px">%50</div><div style="width:140px">%75</div><div style="width:140px">%100</div></div>
<div class="leg"><i></i>M3<i class="w"></i>M3-kısmi · x ekseni: çizginin tamamlanma oranı</div>

<div class="key">İlk çeyrekte <b>2,7 kat</b> · bedeli tam çizimde <b>−0,9 puan</b></div>

<!--
İlk üç model yarım çizimde çöküyor (M1–M3 ilk çeyrekte %13–15): eğitimde hiç yarım çizim görmediler. Mimari çözmüyor. Çözüm veride: her çizimin rastgele %20–100'ü; her yığının yarısı bununla değiştirildi, etiket aynı. Ana cümle: Erken tanımada belirleyici olan mimari değil, eğitim verisiydi.
Hoca sorarsa: Dezavantaj? Ayrıntı çizilmeden karar verdiği için benzer nesneleri (ceket/kazak) daha kolay karıştırır. Neden %20–100? Çok küçük parça bilgi taşımaz; oran ayrıca denenmedi.
-->

---

## 5b · Oyunda fark (50 sınıf, test)

| | M3 | M3-kısmi |
|---|---:|---:|
| Tanınan çizim | %98,9 | %98,4 |
| Tur puanı | 67,4 | **74,7** |
| 60 sn'de tanınan nesne | 8,1 | **10,3** |

- M3 biraz daha çok tanıyor ama geç
- M3-kısmi 7 puan önde

<div class="key">Model doğruluğa göre değil, <b>oyun puanına göre</b> seçildi.</div>

<!--
Oyun kuralıyla ölçüldü: 50 sınıf, test seti.
-->

---

## 6 · Gerçek kullanıcı testi

<div class="cols">
<div>

<div class="big">
<div><b>%97,4</b>test seti</div>
<div><b>%88,2</b>gerçek</div>
</div>

<p class="muted">M3 · 50 sınıf · 5 kişi · 229 çizim · tahmin gizli</p>

</div>
<div>

### Hata sebepleri

1. Alışılmadık biçim (önden araba)
2. Türkçe ad belirsizliği (merdiven)
3. Zaten karışan sınıflar (örümcek → güneş)

</div>
</div>

<!--
Test seti de Quick, Draw!'dan; gerçek kişi fareyle/telefonda farklı çizer. Ayrı çizim toplama sayfası, kişi başı 50 nesne, rastgele sıra; tahmin gizli çünkü görse çizimini düzeltirdi. 229 çizim: 179 fare, 50 dokunmatik. Adlar yerine A–E. Gerçekte 9–13 puan düşük; sıralama korunuyor. Rakamlı saat → pizza. "merdiven": 3 kişi basamaklı çizdi, veri sınıfı el merdiveni; ad sonra düzeltildi.
Dürüstlük: 5 kişi küçük; aygıt etkisi kişi etkisinden ayrılamıyor.
Hoca sorarsa: Veri artırma işe yaradı mı? Hayır: artırmalı M2 %85,6, artırmasız %86,0. Neden sonuç gösterilmedi? Ölçüm iyimser olurdu.
-->

---

## 7 · 345 sınıfa geçiş

<div class="cols">
<div>

### %97 → %77 · neden düştü?

| Gerçek | Tahmin | /2 500 |
|---|---|---:|
| doğum günü pastası | pasta | 936 |
| kasırga | hortum | 871 |
| keman | gitar | 710 |
| okul otobüsü | otobüs | 663 |
| bardak | kupa | 645 |

</div>
<div>

### Oyunda 3 çözüm

1. **Eşdeğer gruplar** (12): bardak = kupa = kahve fincanı
2. **Eşik %50 → %30**
3. **Sorulan kelimeler**: oyunda iyi tanınan 258 kelime

<p class="muted">Sekmeler: Oyun · 50 (kolay), Oyun · 258 (zor)</p>

</div>
</div>

<!--
50 sınıflı oyun çok kolay geldi (2–4 sn). Sınıf başına 20 000 eğitim (6,9 milyon); mimari aynı, son katman 345 çıkış; M2 atlandı. M3 %77,3, M3-kısmi %75,1, M1 %70,1. Düşüş yeni sınıflar zor olduğu için değil: aynı 50 sınıf 345'li modelde %84,4. Sebep benzer sınıfların bir arada olması. Keman/gitar gibi farklı nesneler birleştirilmedi. Eşik: olasılık benzer sınıflara bölünüyor, doğru cevap %41 gibi kalıyordu.
Hoca sorarsa: Eşik neden %30? %50/40/30/25/20 denendi; düştükçe daha çok tanınır, yanlış kabul artar; doğrulama setiyle seçildi. Daha iyi nasıl? 64×64 giriş.
-->

---

## 8 · Tarayıcıda çalışma

<div class="big">
<div><b>4,3 ms</b>tek tahmin</div>
<div><b>2,7 MB</b>model dosyası</div>
<div><b>%2</b>250 ms'nin</div>
</div>

<div class="flow"><span>PyTorch</span> → <span>ONNX</span> → <span>tarayıcı</span></div>

<p class="muted" style="text-align:center;margin-top:22px">Hızlı · ücretsiz (sunucu yok) · gizli (çizim cihazdan çıkmaz)</p>

<!--
ONNX: modeller için ortak dosya formatı ("modelin PDF'i"); tarayıcıda ONNX Runtime Web (WebAssembly). PyTorch–ONNX çıktı farkı < 0,0000006. Ön işleme dahil ~5 ms; tahmin 250 ms'de bir + her çizgi bitince.
Hoca sorarsa: Telefonda? Ölçülmedi. 345 sınıfta yavaşladı mı? Hayır, 4,4 ms. Ön işleme neden iki dilde? Eğitim Python, oyun TypeScript; aynı görüntü şart, 304 örnekle test.
-->

---

## 9 · Sınırlılıklar

1. **Küçük örnek:** 5 kişi, dokunmatikte 1 kişi
2. **Tek eğitim:** her model bir kez eğitildi; 0,3 puanlık fark kesin değil
3. **Erken kararın bedeli:** benzer nesnelerde kolay kandırılır (ceket → kazak %65)
4. **"Hiçbiri" yok (50 sınıf):** karalamaların %4,5'i kabul

### Sonraki adımlar

<p class="muted">"hiçbiri" sınıfı · RNN/Transformer ile karşılaştırma · farklı tohumlarla tekrar eğitim · telefonda ölçüm, 8 bit nicemleme</p>

<!--
Zor çiftlerde ortalama kabul %33. 345 sınıflı modelde "karalama" sınıfı var, %0,4.
Sorulursa: Veri yanlılığı: yalnız Google'ın tanıdığı çizimler, test iyimser olabilir, gerçek kullanıcı düşüşünün bir sebebi olabilir. Telefonda hız ölçülmedi. M1'in 2 puan geriliği ve M3-kısmi'nin erken tanıma farkı tek eğitimden etkilenmeyecek kadar büyük.
-->

---

## 10 · Sonuç

<div class="key">Erken tanımada belirleyici olan mimari değil, <b>eğitim verisiydi</b>.</div>

1. **Küçük CNN'ler yeterli:** 50 sınıfta %97,4, tarayıcıda ~5 ms
2. **Yarım çizimle eğitim:** ilk çeyrekte doğruluk 2,7 kat
3. **Model kullanılacağı kuralla ölçülmeli:** oyun puanına göre seçildi

<!--
Mimari değişikliği erken tanımayı sağlamadı; yarım çizimle eğitim sağladı. Model sınıflandırma doğruluğuna göre değil oyun puanına göre seçildi.
-->

---

<!-- _class: cover -->

## Canlı demo

### [demo adresi]

- Oyun · 50: tahminin çizerken değişmesi
- Oyun · 258: eşdeğer grup (kupa da kabul)
- Serbest çizim: 28×28 görüntü, ilk 5 tahmin

<hr>

### Teşekkürler · Sorular?

<!--
~2 dk. B planı: demo/ içinde `npx vite`; sunumdan önce dene.
-->
