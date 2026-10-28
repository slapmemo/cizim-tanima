"""Bir modeli eğitir; en iyi doğrulama doğruluğundaki ağırlıkları saklar.

Kullanım:
  .venv\\Scripts\\python.exe egitim\\egit.py --ad m1 --model m1 --epoch 10
  .venv\\Scripts\\python.exe egitim\\egit.py --ad m2 --model m2 --epoch 20 --artirma
345 sınıf: SINIF_SETI=345 ortam değişkeniyle (veri veri/islenmis345/, ad örn. s345_m3)
Çıktılar: modeller/<ad>.pt, deneyler/<ad>/ayarlar.json, deneyler/<ad>/gecmis.json
"""
import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

sys.path.insert(0, str(Path(__file__).parent))
from modeller import MODELLER  # noqa: E402
from siniflar import ADLAR, ISLENMIS_AD  # noqa: E402

KOK = Path(__file__).resolve().parent.parent
VERI = KOK / "veri" / ISLENMIS_AD


def yukle(bolum, cihaz):
    d = np.load(VERI / f"{bolum}.npz")
    return torch.from_numpy(d["X"]).to(cihaz), torch.from_numpy(d["y"]).long().to(cihaz)


def hazirla(xb):
    return xb.unsqueeze(1).float().div_(255.0)


def artir(x, uretec):
    """Rastgele afin dönüşüm (GPU'da): döndürme ±15°, ölçek 0.85-1.15, kaydırma ±2 piksel."""
    n = x.shape[0]
    aci = (torch.rand(n, device=x.device, generator=uretec) * 2 - 1) * math.radians(15)
    olcek = 0.85 + torch.rand(n, device=x.device, generator=uretec) * 0.30
    kay = (torch.rand(n, 2, device=x.device, generator=uretec) * 2 - 1) * (2 / 14)
    cos, sin = torch.cos(aci) / olcek, torch.sin(aci) / olcek
    teta = torch.stack([torch.stack([cos, -sin, kay[:, 0]], 1),
                        torch.stack([sin, cos, kay[:, 1]], 1)], 1)
    izgara = F.affine_grid(teta, x.shape, align_corners=False)
    return F.grid_sample(x, izgara, mode="bilinear", padding_mode="zeros", align_corners=False)


@torch.no_grad()
def degerlendir(model, X, y, yigin=4096):
    model.eval()
    kayip, dogru = 0.0, 0
    for i in range(0, len(X), yigin):
        with torch.autocast("cuda", dtype=torch.bfloat16):
            cikti = model(hazirla(X[i:i + yigin]))
        kayip += F.cross_entropy(cikti.float(), y[i:i + yigin], reduction="sum").item()
        dogru += (cikti.argmax(1) == y[i:i + yigin]).sum().item()
    return kayip / len(X), dogru / len(X)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ad", required=True)
    p.add_argument("--model", choices=MODELLER, required=True)
    p.add_argument("--epoch", type=int, default=15)
    p.add_argument("--yigin", type=int, default=512)
    p.add_argument("--oo", type=float, default=3e-3, help="en yüksek öğrenme oranı")
    p.add_argument("--agirlik-azalmasi", type=float, default=0.05)
    p.add_argument("--artirma", action="store_true")
    p.add_argument("--kismi", type=float, default=0.0,
                   help="her yığında örneklerin bu oranı yarım çizim sürümüyle değiştirilir (kismi_hazirla.py)")
    p.add_argument("--tohum", type=int, default=42)
    a = p.parse_args()

    torch.manual_seed(a.tohum)
    cihaz = torch.device("cuda")
    Xe, ye = yukle("egitim", cihaz)
    Xd, yd = yukle("dogrulama", cihaz)
    if a.kismi:
        Xek = torch.from_numpy(np.load(VERI / "egitim_kismi.npz")["X"])
        try:
            Xek = Xek.to(cihaz)
        except torch.OutOfMemoryError:
            # 345 sınıfta GPU'ya sığmazsa sabitlenmiş bellekte kalır, yığın başına taşınır
            print("yarım çizimler GPU'ya sığmadı, sabitlenmiş bellekte", flush=True)
            Xek = Xek.pin_memory()
    model = MODELLER[a.model](len(ADLAR)).to(cihaz)
    parametre = sum(p.numel() for p in model.parameters())
    print(f"{a.ad}: {a.model}, {parametre:,} parametre, eğitim {len(Xe):,}, doğrulama {len(Xd):,}", flush=True)

    adim_sayisi = math.ceil(len(Xe) / a.yigin)
    eniyilestirici = torch.optim.AdamW(model.parameters(), lr=a.oo, weight_decay=a.agirlik_azalmasi)
    zamanlayici = torch.optim.lr_scheduler.OneCycleLR(
        eniyilestirici, max_lr=a.oo, epochs=a.epoch, steps_per_epoch=adim_sayisi, pct_start=0.15)
    uretec = torch.Generator(device=cihaz).manual_seed(a.tohum)

    klasor = KOK / "deneyler" / a.ad
    klasor.mkdir(parents=True, exist_ok=True)
    (KOK / "modeller").mkdir(exist_ok=True)
    (klasor / "ayarlar.json").write_text(json.dumps({**vars(a), "parametre": parametre}, indent=2), encoding="utf-8")

    gecmis, eniyi = [], -1.0
    for ep in range(1, a.epoch + 1):
        model.train()
        t0 = time.time()
        sira = torch.randperm(len(Xe), device=cihaz, generator=uretec)
        top_kayip, top_dogru = torch.zeros((), device=cihaz), torch.zeros((), device=cihaz)
        for i in range(adim_sayisi):
            idx = sira[i * a.yigin:(i + 1) * a.yigin]
            xb, yb = Xe[idx], ye[idx]
            if a.kismi:
                sec = torch.rand(len(idx), device=cihaz, generator=uretec) < a.kismi
                yarim = Xek[idx] if Xek.is_cuda else Xek[idx.cpu()].to(cihaz, non_blocking=True)
                xb = torch.where(sec[:, None, None], yarim, xb)
            xb = hazirla(xb)
            if a.artirma:
                xb = artir(xb, uretec)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                cikti = model(xb)
                kayip = F.cross_entropy(cikti, yb)
            eniyilestirici.zero_grad(set_to_none=True)
            kayip.backward()
            eniyilestirici.step()
            zamanlayici.step()
            top_kayip += kayip.detach() * len(yb)
            top_dogru += (cikti.argmax(1) == yb).sum()
        torch.cuda.synchronize()
        sure = time.time() - t0
        dk, dd = degerlendir(model, Xd, yd)
        satir = {"epoch": ep, "egitim_kayip": top_kayip.item() / len(Xe),
                 "egitim_dogruluk": top_dogru.item() / len(Xe),
                 "dogrulama_kayip": dk, "dogrulama_dogruluk": dd, "sure_sn": sure}
        gecmis.append(satir)
        if dd > eniyi:
            eniyi = dd
            torch.save({"model": a.model, "sinif": len(ADLAR), "durum": model.state_dict(), "epoch": ep},
                       KOK / "modeller" / f"{a.ad}.pt")
        (klasor / "gecmis.json").write_text(json.dumps(gecmis, indent=2), encoding="utf-8")
        print(f"epoch {ep:2d}  kayıp {satir['egitim_kayip']:.4f}  eğitim {satir['egitim_dogruluk']:.4f}  "
              f"doğrulama {dd:.4f}  ({sure:.0f} sn)", flush=True)
    print(f"en iyi doğrulama doğruluğu: {eniyi:.4f}")


if __name__ == "__main__":
    main()
