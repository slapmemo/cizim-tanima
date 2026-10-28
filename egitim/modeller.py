"""Karşılaştırılan üç model. Giriş (N, 1, 28, 28), 0-1 arası; çıkış sınıf logitleri (varsayılan 50)."""
from torch import nn

SINIF = 50


def m1(sinif=SINIF):
    """Basit CNN: 2 evrişim + havuzlama + 1 gizli tam bağlı katman (temel çizgi)."""
    return nn.Sequential(
        nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),     # 14x14
        nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),    # 7x7
        nn.Flatten(),
        nn.Linear(64 * 7 * 7, 128), nn.ReLU(),
        nn.Linear(128, sinif),
    )


def _blok(giris, cikis):
    return nn.Sequential(
        nn.Conv2d(giris, cikis, 3, padding=1, bias=False), nn.BatchNorm2d(cikis), nn.ReLU(),
        nn.Conv2d(cikis, cikis, 3, padding=1, bias=False), nn.BatchNorm2d(cikis), nn.ReLU(),
        nn.MaxPool2d(2),
        nn.Dropout2d(0.1),
    )


def m2(sinif=SINIF):
    """Derin CNN: 3 blok (2 evrişim + BatchNorm), Dropout; veri artırmayla eğitilir."""
    return nn.Sequential(
        _blok(1, 32),     # 14x14
        _blok(32, 64),    # 7x7
        _blok(64, 128),   # 3x3
        nn.Flatten(),
        nn.Linear(128 * 3 * 3, 256, bias=False), nn.BatchNorm1d(256), nn.ReLU(),
        nn.Dropout(0.4),
        nn.Linear(256, sinif),
    )


class ArtikBlok(nn.Module):
    """ResNet temel bloğu: iki 3x3 evrişim + kısa yol."""

    def __init__(self, giris, cikis, adim=1):
        super().__init__()
        self.govde = nn.Sequential(
            nn.Conv2d(giris, cikis, 3, adim, 1, bias=False), nn.BatchNorm2d(cikis), nn.ReLU(),
            nn.Conv2d(cikis, cikis, 3, 1, 1, bias=False), nn.BatchNorm2d(cikis),
        )
        self.kisa = nn.Identity()
        if adim != 1 or giris != cikis:
            self.kisa = nn.Sequential(nn.Conv2d(giris, cikis, 1, adim, bias=False), nn.BatchNorm2d(cikis))
        self.relu = nn.ReLU()

    def forward(self, x):
        return self.relu(self.govde(x) + self.kisa(x))


def m3(sinif=SINIF):
    """Hafif ResNet: 3 aşama x 2 artık blok (32/64/128 kanal), küresel ortalama havuzlama."""
    return nn.Sequential(
        nn.Conv2d(1, 32, 3, padding=1, bias=False), nn.BatchNorm2d(32), nn.ReLU(),
        ArtikBlok(32, 32), ArtikBlok(32, 32),             # 28x28
        ArtikBlok(32, 64, 2), ArtikBlok(64, 64),          # 14x14
        ArtikBlok(64, 128, 2), ArtikBlok(128, 128),       # 7x7
        nn.AdaptiveAvgPool2d(1), nn.Flatten(),
        nn.Dropout(0.2),
        nn.Linear(128, sinif),
    )


MODELLER = {"m1": m1, "m2": m2, "m3": m3}
