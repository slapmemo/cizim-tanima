const path = require('path');
let PptxGenJS;
try { PptxGenJS = require('pptxgenjs'); } catch (e) { PptxGenJS = require('../node_modules/pptxgenjs'); }

const NAVY = '1F2A44', ACC = '0F6B73', TXT = '2B2B2B', GREY = 'E9ECEF', MID = '6B7280';
const FONT = 'Calibri';

const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5
pptx.title = 'CNN ile Gerçek Zamanlı Çizim Tanıma';

let n = 0;
function base(title, notes) {
  const s = pptx.addSlide();
  n++;
  s.background = { color: 'F7F8FA' };
  if (title) {
    s.addText(title, { x: 0.6, y: 0.35, w: 12.1, h: 0.8, fontFace: FONT, fontSize: 30, bold: true, color: NAVY, align: 'left', valign: 'middle', margin: 0 });
    s.addShape(pptx.ShapeType.rect, { x: 0.6, y: 1.18, w: 1.4, h: 0.06, fill: { color: ACC }, line: { color: ACC, width: 0 } });
  }
  s.addText(String(n), { x: 12.2, y: 7.0, w: 0.6, h: 0.3, fontFace: FONT, fontSize: 11, color: MID, align: 'right', margin: 0 });
  if (notes) s.addNotes(notes);
  return s;
}
function bullets(s, items, o = {}) {
  const arr = items.map(t => {
    if (typeof t === 'string') return { text: t, options: { bullet: { code: '2022' }, breakLine: true, paraSpaceAfter: 10 } };
    return { text: t.text, options: { bullet: { code: '2013' }, indentLevel: 1, breakLine: true, fontSize: (o.fontSize || 20) - 3, color: MID } };
  });
  s.addText(arr, Object.assign({ x: 0.6, y: 1.6, w: 12.1, h: 5.0, fontFace: FONT, fontSize: 20, color: TXT, valign: 'top', align: 'left', margin: 4 }, o));
}
function placeholder(s, text, x, y, w, h) {
  s.addShape(pptx.ShapeType.rect, { x, y, w, h, fill: { color: 'D9DDE1' }, line: { color: 'B8BEC5', width: 1 } });
  s.addText(text, { x, y, w, h, fontFace: FONT, fontSize: 16, color: MID, align: 'center', valign: 'middle' });
}
const H = (t, al) => ({ text: t, options: { bold: true, color: 'FFFFFF', fill: { color: NAVY }, align: al || 'left', fontFace: FONT } });
const C = (t, al, extra) => ({ text: t, options: Object.assign({ align: al || 'left', fontFace: FONT, color: TXT }, extra || {}) });
function table(s, rows, o) {
  s.addTable(rows, Object.assign({ fontFace: FONT, fontSize: 15, border: { type: 'solid', pt: 0.75, color: 'C9CED4' }, fill: { color: 'FFFFFF' }, valign: 'middle', rowH: 0.42 }, o));
}

// 1 Kapak
{
  const s = pptx.addSlide(); n++;
  s.background = { color: 'FFFFFF' };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.35, h: 7.5, fill: { color: NAVY }, line: { color: NAVY, width: 0 } });
  s.addText('CNN ile Gerçek Zamanlı Çizim Tanıma', { x: 1.0, y: 2.1, w: 11.3, h: 1.2, fontFace: FONT, fontSize: 44, bold: true, color: NAVY, align: 'left', margin: 0 });
  s.addShape(pptx.ShapeType.rect, { x: 1.0, y: 3.4, w: 1.8, h: 0.07, fill: { color: ACC }, line: { color: ACC, width: 0 } });
  s.addText('Sinir Ağları dersi projesi', { x: 1.0, y: 3.65, w: 11, h: 0.6, fontFace: FONT, fontSize: 24, color: ACC, align: 'left', margin: 0 });
  s.addText('[Ad Soyad] · [Öğrenci no] · Kasım 2026', { x: 1.0, y: 4.5, w: 11, h: 0.5, fontFace: FONT, fontSize: 18, color: MID, align: 'left', margin: 0 });
  s.addText(String(n), { x: 12.2, y: 7.0, w: 0.6, h: 0.3, fontFace: FONT, fontSize: 11, color: MID, align: 'right', margin: 0 });
  s.addNotes('Bu projede, oyuncunun ekrana çizdiği nesneyi çizim sürerken tanıyan, tarayıcıda sunucusuz çalışan, evrişimli sinir ağı (CNN) tabanlı bir çizim oyunu geliştirdik.');
}

// 2 Amaç
{
  const s = base('Amaç', 'Söylenecek: Bu projede, oyuncunun ekrana çizdiği nesneyi çizim sürerken tanıyan, tarayıcıda sunucusuz çalışan, CNN tabanlı bir çizim oyunu geliştirdik. Erken tanıma = puan; model yarım çizimi de tanımalı, bu yüzden eğitime yarım çizim ekledik (ayrıntı 5. bölümde).\nHoca sorarsa: Tarayıcıda nasıl? Model ONNX\'e çevrildi, tek tahmin ~5 ms. CNN nedir? Görüntüde küçük filtrelerle çizgi, köşe, kavis gibi desenleri yakalayan sinir ağı; çizimi 28×28 görüntüye çevirip veriyoruz.');
  bullets(s, [
    'Çizim sürerken nesneyi tanıyan, tarayıcıda sunucusuz çalışan CNN tabanlı oyun',
    'Kural: kelime gelir, 20 sn içinde çiz, model tanıyınca tur biter',
    'Puan = 100 × kalan süre / 20 sn',
    'Neden anlık: erken tanıma = puan; model yarım çizimi de tanımalı',
  ], { w: 6.8 });
  placeholder(s, '[oyun ekranı görüntüsü]', 7.8, 1.7, 4.9, 4.2);
}

// 3 Veri seti
{
  const s = base('Veri seti', 'Quick, Draw! Google\'ın çevrimiçi oyunu; oyuncu çizimleri açık veri seti: 345 sınıf, 50 milyondan fazla çizim. Çizimler resim değil, kalem hareketi (vuruş) olarak saklanıyor. Yalnız Google\'ın modelinin tanıdığı (recognized) çizimleri kullandık; sınırlılık: kötü çizimler veride yok. Önce 50 sınıf: yöntemi küçükte denemek için. Bölme sınıf başına 30 000 / 5 000 / 5 000. Test en sonda bir kez kullanıldı.\nHazır 28×28 görüntüler kullanılmadı: oyunda aynı dönüşüm yapılamazdı. Tek algoritma, Python ve TypeScript birebir aynı; 304 örnekte 0 farklı piksel.\nHoca sorarsa: Test neden en sonda? Seçimi testle yaparsak sonuç iyimser olur. Sınıflar dengeli mi? Evet, eşit sayı.');
  bullets(s, [
    'Quick, Draw!: 345 sınıf, 50 milyondan fazla çizim (kalem vuruşları)',
    'Önce 50 sınıf; ölçütler: 20 sn\'de çizilebilir, birbirine benzemeyen, Türkçe adı açık',
    'Sınıf başına bölme: 30 000 eğitim / 5 000 doğrulama / 5 000 test',
    'Vuruştan görüntüye tek algoritma: Python = TypeScript, 304 örnekte 0 farklı piksel',
  ]);
}

// 4 Modeller
{
  const s = base('Modeller', 'Amaç: yapının (mimarinin) ne kadar fark yarattığını görmek. Evrişim: gezen 3×3 filtre. Havuzlama: görüntüyü küçültür. BatchNorm: eğitimi hızlı ve kararlı yapar. Dropout: ezberi azaltır. Artık bağlantı: giriş çıktıya eklenir (ResNet). Parametreler 400–700 bin, tarayıcıda hızlı.\nHoca sorarsa: Neden büyük hazır model yok? Tarayıcıda her 250 ms\'de çalışacak, küçük ve hızlı olmalı; giriş 28×28. Eğitim: AdamW, 20 epoch (M1 10), yığın 512, RTX 5070 Ti.');
  table(s, [
    [H('Model'), H('Yapı'), H('Parametre', 'right')],
    [C('M1 Basit CNN', 'left', { bold: true }), C('2 evrişim + havuzlama, tam bağlı katman (taban model)'), C('427 bin', 'right')],
    [C('M2 Derin CNN', 'left', { bold: true }), C('Daha çok evrişim, BatchNorm, Dropout; artırmalı ve artırmasız'), C('595 bin', 'right')],
    [C('M3 Hafif ResNet', 'left', { bold: true }), C('Artık bağlantılı küçük ResNet'), C('701 bin', 'right')],
    [C('M3-kısmi', 'left', { bold: true }), C('M3 ile aynı mimari; eğitimde yarım çizimler de var'), C('701 bin', 'right')],
  ], { x: 0.6, y: 1.8, w: 12.1, colW: [2.8, 7.3, 2.0], fontSize: 17, rowH: 0.7 });
}

// 5 50 sınıf sonuçları
{
  const s = base('50 sınıf sonuçları', 'Test seti 250 000 çizim. M1→M2: hata %4,8\'den %2,9\'a, neredeyse yarıya. M2→M3: yalnız 0,3 puan kazanç, M3 2,5 kat yavaş. Veri artırma test setinde işe yaramadı (−0,19 puan); yararı gerçek kullanıcıda beklenir. Dürüstlük: her model bir kez eğitildi, 0,3 puanlık farklar kesin değil. M3-kısmi tam çizimde 0,9 puan geride; neden seçildiği 5. bölümde.\nHoca sorarsa: En çok karışan: ay↔muz, örümcek↔güneş, mantar↔şemsiye (şekil benzerliği). Aşırı öğrenme: M1\'de biraz (eğitim %97, doğrulama %95); M2 ve M3\'te eğriler yakın.');
  s.addText('Hata oranı (%), test seti, 250 000 çizim', { x: 0.6, y: 1.4, w: 7.4, h: 0.4, fontFace: FONT, fontSize: 14, color: MID, margin: 0 });
  s.addChart(pptx.charts.BAR, [{
    name: 'Hata oranı (%)',
    labels: ['M3-kısmi', 'M3', 'M2 artırmalı', 'M2 artırmasız', 'M1'],
    values: [3.50, 2.57, 3.06, 2.87, 4.78],
  }], {
    x: 0.5, y: 1.8, w: 7.6, h: 4.9, barDir: 'bar', chartColors: [ACC],
    showValue: true, dataLabelFormatCode: '0.00', dataLabelFontFace: FONT, dataLabelFontSize: 14, dataLabelColor: TXT,
    catAxisLabelFontFace: FONT, catAxisLabelFontSize: 14, catAxisLabelColor: TXT,
    valAxisLabelFontFace: FONT, valAxisLabelFontSize: 12, valAxisMinVal: 0, valAxisMaxVal: 6,
    valGridLine: { color: 'DDDDDD', size: 0.5 }, showLegend: false, barGapWidthPct: 50,
  });
  bullets(s, [
    'M1 → M2: hata neredeyse yarıya (%4,8 → %2,9)',
    'M2 → M3: yalnız 0,3 puan kazanç; karmaşıklık her zaman çok daha iyi değil',
    'Veri artırma test setinde yaramadı (−0,19 puan)',
  ], { x: 8.4, y: 1.8, w: 4.4, h: 4.5, fontSize: 18 });
}

// 6 Erken tanıma
{
  const s = base('Erken tanıma: yarım çizimde doğruluk', 'İlk üç model yarım çizimde çöküyor: tam %97, ilk çeyrekte %15; eğitimde hiç yarım çizim görmediler. Mimari çözmüyor: M1–M3 hepsi %13–15. Çözüm veride: her çizimin rastgele %20–100\'ü alınarak yarım sürüm; eğitimde her yığının yarısı bununla değiştirildi, etiket aynı. Sonuç: ilk çeyrekte %15 → %40 (2,7 kat); bedeli tam çizimde −0,9 puan. (%25 = çizginin/mürekkebin ilk çeyreği.)\nHoca sorarsa: Dezavantaj? Ayrıntı çizilmeden karar verdiği için benzer nesneleri (ceket/kazak) daha kolay karıştırır. Neden %20–100? Çok küçük parça bilgi taşımaz; oran ayrıca denenmedi (sınırlılık).');
  s.addText('Doğruluk (%), çizimin ilk %25 / %50 / %75 / %100\'ü görünürken', { x: 0.6, y: 1.4, w: 8, h: 0.4, fontFace: FONT, fontSize: 14, color: MID, margin: 0 });
  s.addChart(pptx.charts.BAR, [
    { name: 'M3', labels: ['%25', '%50', '%75', '%100'], values: [14.7, 50.5, 87.1, 97.4] },
    { name: 'M3-kısmi', labels: ['%25', '%50', '%75', '%100'], values: [40.2, 76.3, 91.9, 96.5] },
  ], {
    x: 0.5, y: 1.8, w: 8.0, h: 4.9, barDir: 'col', barGrouping: 'clustered', chartColors: ['8A94A6', ACC],
    showValue: true, dataLabelFormatCode: '0.0', dataLabelFontFace: FONT, dataLabelFontSize: 12, dataLabelColor: TXT,
    catAxisLabelFontFace: FONT, catAxisLabelFontSize: 14, valAxisLabelFontFace: FONT, valAxisLabelFontSize: 12,
    valAxisMinVal: 0, valAxisMaxVal: 100, valGridLine: { color: 'DDDDDD', size: 0.5 },
    showLegend: true, legendPos: 'b', legendFontFace: FONT, legendFontSize: 14, barGapWidthPct: 60,
  });
  bullets(s, [
    'M1–M3 yarım çizimde çöktü: ilk çeyrekte %13–15',
    'Çözüm veride: eğitimde yarım çizimler',
    'İlk çeyrekte 2,7 kat; bedeli tam çizimde −0,9 puan',
  ], { x: 8.8, y: 1.8, w: 4.0, h: 4.5, fontSize: 18 });
}

// 7 Oyunda fark
{
  const s = base('Oyunda fark: M3 ve M3-kısmi', 'Oyun kuralıyla, 50 sınıf, test seti. M3 biraz daha çok tanıyor ama geç; M3-kısmi 7 puan önde. Model doğruluğa göre değil oyun puanına göre seçildi.\nHoca sorarsa: Dezavantaj? Ayrıntı çizilmeden karar verdiği için benzer nesneleri (ceket/kazak) daha kolay karıştırır.');
  table(s, [
    [H(''), H('M3', 'right'), H('M3-kısmi', 'right')],
    [C('Tanınan çizim'), C('%98,9', 'right'), C('%98,4', 'right')],
    [C('Tur puanı', 'left', { bold: true }), C('67,4', 'right'), C('74,7', 'right', { bold: true, color: ACC })],
    [C('60 sn\'de tanınan nesne', 'left', { bold: true }), C('8,1', 'right'), C('10,3', 'right', { bold: true, color: ACC })],
  ], { x: 0.6, y: 1.8, w: 8.0, colW: [4.0, 2.0, 2.0], fontSize: 20, rowH: 0.7 });
  s.addText('Model, doğruluğa göre değil oyun puanına göre seçildi.', { x: 0.6, y: 5.2, w: 12, h: 0.7, fontFace: FONT, fontSize: 22, bold: true, color: ACC, margin: 0 });
}

// 8 Gerçek kullanıcı
{
  const s = base('Gerçek kullanıcı testi', 'Neden: test seti de Quick, Draw!\'dan; gerçek kişi fareyle/telefonda farklı çizer. Nasıl: ayrı çizim toplama sayfası; kişi başı 50 nesne, rastgele sıra; model tahmini gizli (görse çizimini düzeltir, sonuç iyimser olur); adlar yerine A–E. Sonuç: 5 kişi, 229 çizim (179 fare, 50 dokunmatik); gerçekte 9–13 puan düşük, sıralama korunuyor. Dürüstlük: 5 kişi küçük; aygıt etkisi kişi etkisinden ayrılamıyor.\nHoca sorarsa: Veri artırma işe yaradı mı? Hayır: artırmalı M2 %85,6, artırmasız %86,0. Neden sonuç gösterilmedi? Görse düzeltirdi, ölçüm iyimser olurdu.');
  s.addText('%97,4 → %88,2', { x: 0.6, y: 1.6, w: 6.0, h: 1.2, fontFace: FONT, fontSize: 48, bold: true, color: ACC, margin: 0 });
  s.addText('test seti → gerçek kullanıcı (M3, 50 sınıf)', { x: 0.6, y: 2.8, w: 6.0, h: 0.5, fontFace: FONT, fontSize: 18, color: NAVY, margin: 0 });
  s.addText('5 kişi · 229 çizim · model tahmini gizli', { x: 0.6, y: 3.4, w: 6.0, h: 0.5, fontFace: FONT, fontSize: 16, color: MID, margin: 0 });
  s.addText('Düşüşün üç sebebi', { x: 7.2, y: 1.6, w: 5.5, h: 0.5, fontFace: FONT, fontSize: 20, bold: true, color: NAVY, margin: 0 });
  bullets(s, [
    'Alışılmadık biçim: önden araba, rakamlı saat → pizza',
    'Türkçe ad belirsizliği: "merdiven" → veri sınıfı el merdiveni',
    'Zaten karışan sınıflar: örümcek → güneş',
  ], { x: 7.2, y: 2.2, w: 5.6, h: 3.8, fontSize: 18 });
}

// 9 345 sınıf
{
  const s = base('345 sınıfa geçiş', 'Neden geçtik: 50 sınıflı oyun çok kolay geldi, çizimler 2–4 sn\'de tanınıyordu. Ne değişti: sınıf başına 20 000 eğitim (toplam 6,9 milyon, bellek sınırı); mimari aynı, yalnız son katman 345 çıkış; M2 atlandı. Neden düştü: yeni sınıflar zor olduğu için değil; aynı 50 sınıfın çizimleri 345 sınıflı modelde %84,4. Sebep benzer sınıfların bir arada olması.\nÜç çözüm: eşdeğer gruplar (12), eşik %50→%30, sorulan kelimeler 258. İki sekme: Oyun · 50 (kolay), Oyun · 258 (zor).\nHoca sorarsa: Eşik neden %30? %50/40/30/25/20 denendi; düştükçe daha çok tanınır ama yanlış kabul artar; %30 denge, doğrulama setiyle seçildi. Daha iyi nasıl? 64×64 giriş ince ayrıntıyı koruyabilir.');
  s.addText('%97 → %77', { x: 0.6, y: 1.5, w: 6.0, h: 0.8, fontFace: FONT, fontSize: 36, bold: true, color: ACC, margin: 0 });
  s.addText('M3: 50 sınıf %97,4 → 345 sınıf %77,3. Sebep: benzer sınıflar bir arada', { x: 0.6, y: 2.3, w: 6.0, h: 0.6, fontFace: FONT, fontSize: 14, color: MID, margin: 0 });
  table(s, [
    [H('Gerçek'), H('Tahmin'), H('/2 500', 'right')],
    [C('doğum günü pastası'), C('pasta'), C('936', 'right')],
    [C('kasırga'), C('hortum'), C('871', 'right')],
    [C('keman'), C('gitar'), C('710', 'right')],
    [C('okul otobüsü'), C('otobüs'), C('663', 'right')],
    [C('bardak'), C('kupa'), C('645', 'right')],
  ], { x: 0.6, y: 3.1, w: 6.0, colW: [2.6, 2.0, 1.4], fontSize: 15, rowH: 0.5 });
  s.addText('Oyunda üç çözüm', { x: 7.2, y: 1.5, w: 5.5, h: 0.5, fontFace: FONT, fontSize: 22, bold: true, color: NAVY, margin: 0 });
  bullets(s, [
    'Eşdeğer gruplar (12): bardak = kupa = kahve fincanı',
    'Eşik %50 → %30',
    'Sorulan kelimeler: iyi tanınan 258',
    { text: 'Sekmeler: "Oyun · 50" (kolay), "Oyun · 258" (zor)' },
  ], { x: 7.2, y: 2.1, w: 5.6, h: 4.0, fontSize: 19 });
}

// 10 Tarayıcı
{
  const s = base('Tarayıcıda çalışma', 'Çoğu uygulama çizimi sunucuya yollar; bizde model kullanıcının tarayıcısında çalışır: hızlı, ücretsiz (sunucu yok), gizli (çizim cihazdan çıkmaz). Akış: PyTorch ile eğitim; ONNX\'e çevirme (modeller için ortak dosya formatı, "modelin PDF\'i"); tarayıcıda ONNX Runtime Web (WebAssembly). PyTorch ve ONNX çıktıları arası en büyük fark < 0,0000006. Tahmin 250 ms\'de bir + her çizgi bitince; %2: gerçek zaman için fazlasıyla yeterli.\nHoca sorarsa: Telefonda? Ölçülmedi (sınırlılık). 345 sınıfta yavaşladı mı? Hayır, 4,4 ms. Ön işleme neden iki dilde? Eğitim Python, oyun TypeScript; aynı görüntü şart, 304 örnekle test.');
  const big = [['4,3 ms', 'tek tahmin (M3-kısmi)'], ['2,7 MB', 'model dosyası'], ['%2', 'tahmin aralığının (250 ms) payı']];
  big.forEach((b, i) => {
    const x = 0.6 + i * 4.1;
    s.addShape(pptx.ShapeType.rect, { x, y: 1.7, w: 3.9, h: 2.4, fill: { color: 'FFFFFF' }, line: { color: 'C9CED4', width: 1 } });
    s.addText(b[0], { x, y: 1.95, w: 3.9, h: 1.2, fontFace: FONT, fontSize: 48, bold: true, color: ACC, align: 'center', valign: 'middle' });
    s.addText(b[1], { x, y: 3.2, w: 3.9, h: 0.6, fontFace: FONT, fontSize: 16, color: TXT, align: 'center', valign: 'middle' });
  });
  const flow = ['PyTorch', 'ONNX', 'Tarayıcı'];
  flow.forEach((f, i) => {
    const x = 1.6 + i * 3.7;
    s.addShape(pptx.ShapeType.roundRect, { x, y: 5.0, w: 2.6, h: 0.9, fill: { color: NAVY }, line: { color: NAVY, width: 0 }, rectRadius: 0.1 });
    s.addText(f, { x, y: 5.0, w: 2.6, h: 0.9, fontFace: FONT, fontSize: 20, bold: true, color: 'FFFFFF', align: 'center', valign: 'middle' });
    if (i < 2) s.addText('→', { x: x + 2.6, y: 5.0, w: 1.1, h: 0.9, fontFace: FONT, fontSize: 32, color: ACC, align: 'center', valign: 'middle' });
  });
}

// 11 Sınırlılıklar
{
  const s = base('Sınırlılıklar ve sonraki adımlar', '1) Küçük örnek: 5 kişi, dokunmatikte 1 kişi; genellenemez. 2) Her model bir kez eğitildi: 0,3 puanlık M2–M3 farkı kesin değil; M1\'in 2 puan geriliği ve M3-kısmi\'nin erken tanıma farkı bundan etkilenmeyecek kadar büyük. 4) Erken kararın bedeli: ceket → kazak kabul %65 (zor çiftlerde ortalama %33). 5) 50 sınıflı modelde "hiçbiri" yok: karalamaların %4,5\'i (20\'de 1) kabul; 345 sınıflı modelde "karalama" sınıfı var, %0,4.\nSorulursa: veri yanlılığı (yalnız Google\'ın tanıdığı çizimler, test iyimser olabilir); telefonda hız ölçülmedi.');
  bullets(s, [
    'Küçük örnek: 5 kişi, dokunmatikte 1 kişi; genellenemez',
    'Her model bir kez eğitildi; 0,3 puanlık farklar kesin değil',
    'Erken kararın bedeli: benzer nesnelerde kolay kandırılır (ceket → kazak %65)',
    '50 sınıflı modelde "hiçbiri" yok: karalamaların %4,5\'i kabul',
  ], { h: 3.4 });
  s.addText('Sonraki adımlar', { x: 0.6, y: 5.0, w: 12, h: 0.4, fontFace: FONT, fontSize: 18, bold: true, color: ACC, margin: 0 });
  s.addText('"Hiçbiri" sınıfı · RNN/Transformer ile karşılaştırma · farklı tohumlarla tekrar eğitim · telefonda ölçüm ve 8 bit nicemleme', { x: 0.6, y: 5.45, w: 12.1, h: 0.9, fontFace: FONT, fontSize: 16, color: TXT, valign: 'top', margin: 0 });
}

// 12 Sonuç
{
  const s = base('Sonuç', 'Ana cümle: Erken tanımada belirleyici olan mimari değil, eğitim verisiydi. 1) Küçük CNN\'ler yeterli: 50 sınıfta %97,4, tarayıcıda ~5 ms. 2) Yarım çizimle eğitim: ilk çeyrekte doğruluk 2,7 kat; mimari değişikliği bunu yapmadı. 3) Model oyun puanına göre seçildi; model kullanılacağı kuralla ölçülmeli.');
  s.addText('Erken tanımada belirleyici olan mimari değil, eğitim verisiydi.', { x: 0.6, y: 1.6, w: 12.1, h: 1.3, fontFace: FONT, fontSize: 30, bold: true, color: ACC, valign: 'middle', margin: 0 });
  bullets(s, [
    'Küçük CNN\'ler yeterli: 50 sınıfta %97,4, tarayıcıda ~5 ms',
    'Yarım çizimle eğitim: ilk çeyrekte doğruluk 2,7 kat',
    'Model, oyun puanına göre seçildi; model kullanılacağı kuralla ölçülmeli',
  ], { y: 3.3, h: 3.3, fontSize: 22 });
}

// 13 Demo
{
  const s = base('Canlı demo', 'Canlı demo ~2 dk: 1) Oyun · 50: 1–2 tur, tahminin çizerken değişmesi. 2) Oyun · 258: bardak/pasta çıkarsa eşdeğer grup (kupa da kabul). 3) Serbest çizim: modelin gördüğü 28×28 görüntü, ilk 5 tahmin. B planı: demo/ içinde npx vite; sunumdan önce dene.');
  s.addText('[demo adresi]', { x: 0.6, y: 1.5, w: 12.1, h: 0.7, fontFace: FONT, fontSize: 28, bold: true, color: ACC, margin: 0 });
  bullets(s, [
    'Oyun · 50: tahmin çizerken değişiyor',
    'Oyun · 258: eşdeğer grup (bardak = kupa)',
    'Serbest çizim: modelin gördüğü 28×28 görüntü, ilk 5 tahmin',
  ], { y: 2.5, h: 2.6, fontSize: 22 });
  s.addText('Teşekkürler · Sorular?', { x: 0.6, y: 5.5, w: 12.1, h: 0.9, fontFace: FONT, fontSize: 36, bold: true, color: NAVY, margin: 0 });
}

pptx.writeFile({ fileName: path.join(__dirname, 'sunum.pptx') }).then(f => console.log('Yazıldı:', f, '| slayt:', n));
