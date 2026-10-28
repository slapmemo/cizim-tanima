"""GPU denemesi: küçük bir CNN'i rastgele 28x28 verilerle birkaç adım eğitir, hızı ölçer."""
import time

import torch
from torch import nn

assert torch.cuda.is_available(), "CUDA yok"
cihaz = torch.device("cuda")
print("PyTorch", torch.__version__, "| CUDA", torch.version.cuda, "|", torch.cuda.get_device_name(0))

model = nn.Sequential(
    nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
    nn.Flatten(), nn.Linear(64 * 7 * 7, 128), nn.ReLU(), nn.Linear(128, 50),
).to(cihaz)
eniyilestirici = torch.optim.AdamW(model.parameters(), lr=1e-3)
x = torch.rand(1024, 1, 28, 28, device=cihaz)
y = torch.randint(0, 50, (1024,), device=cihaz)

for _ in range(5):  # ısınma
    kayip = nn.functional.cross_entropy(model(x), y)
    eniyilestirici.zero_grad(); kayip.backward(); eniyilestirici.step()
torch.cuda.synchronize()

adim = 200
bas = time.perf_counter()
for _ in range(adim):
    with torch.autocast("cuda", dtype=torch.bfloat16):
        kayip = nn.functional.cross_entropy(model(x), y)
    eniyilestirici.zero_grad(); kayip.backward(); eniyilestirici.step()
torch.cuda.synchronize()
sure = time.perf_counter() - bas
print(f"{adim} adım, {sure:.2f} sn, {adim * 1024 / sure:,.0f} görüntü/sn, son kayıp {kayip.item():.3f}")
