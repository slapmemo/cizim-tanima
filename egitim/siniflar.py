"""Oyunda kullanılan 50 sınıf: (Quick, Draw! adı, Türkçe ad).

Ölçüt: 20 sn'de çizilebilir, birbirine çok benzeyen çift yok (kupa/kahve fincanı,
kamyon/araba, kalem/boya kalemi gibi çiftlerden yalnız biri ya da hiçbiri alındı).
Sıra modelin çıkış sırasıdır; değiştirilirse modeller yeniden eğitilmeli.
"""
import os

SINIFLAR = [
    ("airplane", "uçak"),
    ("snail", "salyangoz"),
    ("apple", "elma"),
    ("banana", "muz"),
    ("bicycle", "bisiklet"),
    ("bird", "kuş"),
    ("book", "kitap"),
    ("bowtie", "papyon"),
    ("butterfly", "kelebek"),
    ("cactus", "kaktüs"),
    ("camera", "fotoğraf makinesi"),
    ("car", "araba"),
    ("cat", "kedi"),
    ("chair", "sandalye"),
    ("clock", "saat"),
    ("cloud", "bulut"),
    ("crown", "taç"),
    ("diamond", "elmas"),
    ("door", "kapı"),
    ("envelope", "zarf"),
    ("eye", "göz"),
    ("eyeglasses", "gözlük"),
    ("fish", "balık"),
    ("flower", "çiçek"),
    ("guitar", "gitar"),
    ("hammer", "çekiç"),
    ("hand", "el"),
    ("hat", "şapka"),
    ("house", "ev"),
    ("ice cream", "dondurma"),
    ("key", "anahtar"),
    ("ladder", "el merdiveni"),  # 345 listesiyle aynı (stairs = merdiven); toplama sayfasında "merdiven" basamaklı çizildi
    ("light bulb", "ampul"),
    ("lightning", "şimşek"),
    ("moon", "ay"),
    ("mountain", "dağ"),
    ("mushroom", "mantar"),
    ("pants", "pantolon"),
    ("pizza", "pizza"),
    ("rainbow", "gökkuşağı"),
    ("scissors", "makas"),
    ("snowman", "kardan adam"),
    ("spider", "örümcek"),
    ("star", "yıldız"),
    ("sun", "güneş"),
    ("sword", "kılıç"),
    ("t-shirt", "tişört"),
    ("table", "masa"),
    ("tree", "ağaç"),
    ("umbrella", "şemsiye"),
]

ADLAR = [en for en, _ in SINIFLAR]
assert len(SINIFLAR) == 50 and len(set(ADLAR)) == 50

# Ortam değişkeni SINIF_SETI=345 verilirse bütün betikler 345 sınıfla çalışır (siniflar345.py):
# işlenmiş veri veri/islenmis345/, model ve deney adları "s345_" önekli.
SINIFLAR_50 = SINIFLAR
SINIF_SETI = os.environ.get("SINIF_SETI", "50")
if SINIF_SETI == "345":
    from siniflar345 import SINIFLAR  # noqa: E402
    ADLAR = [en for en, _ in SINIFLAR]
elif SINIF_SETI != "50":
    raise ValueError(f"SINIF_SETI 50 ya da 345 olmalı: {SINIF_SETI}")
ON_EK = "s345_" if SINIF_SETI == "345" else ""
ISLENMIS_AD = "islenmis345" if SINIF_SETI == "345" else "islenmis"
