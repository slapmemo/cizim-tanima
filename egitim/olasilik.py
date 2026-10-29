"""Eğitilmiş modeli (modeller/<ad>.pt) GPU'ya yükler ve 28x28 uint8 görüntülerden olasılık üretir.

ONNX modelleri aynı ağırlıklardan softmax dahil aktarıldı (en büyük fark < 6e-7, degerlendir.py); ölçüm betikleri
hız için PyTorch'u kullanır.
"""
from pathlib import Path

import numpy as np
import torch

from modeller import MODELLER

KOK = Path(__file__).resolve().parent.parent


def model_yukle(ad, cihaz="cuda"):
    kayit = torch.load(KOK / "modeller" / f"{ad}.pt", map_location=cihaz)
    model = MODELLER[kayit["model"]](kayit.get("sinif", 50)).to(cihaz)
    model.load_state_dict(kayit["durum"])
    return model.eval()


@torch.no_grad()
def olasiliklar(model, X, yigin=8192):
    """X: (N, 28, 28) uint8 ya da (N, 1, 28, 28) 0-1 float. Çıkış (N, sınıf) float32."""
    cihaz = next(model.parameters()).device
    cikti = []
    for i in range(0, len(X), yigin):
        xb = torch.from_numpy(np.ascontiguousarray(X[i:i + yigin])).to(cihaz).float()
        if xb.ndim == 3:
            xb = xb.unsqueeze(1) / 255.0
        cikti.append(torch.softmax(model(xb), 1).cpu())
    return torch.cat(cikti).numpy()


def karisiklik(model, X, y, sinif):
    p = olasiliklar(model, X)
    km = np.zeros((sinif, sinif), np.int64)
    np.add.at(km, (y, p.argmax(1)), 1)
    return km
