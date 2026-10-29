// Fare ve dokunmayla çizim; vuruşları Quick, Draw! biçiminde ([xler, yler]) toplar.
import type { Vurus } from "./onisleme.ts";

export class Tuval {
  vuruslar: Vurus[] = [];
  kilitli = false;
  /** Temizle ve Geri al'da artar: bu sırada başlamış bir tahmin artık çizimin kendisine ait değildir. */
  silme = 0;
  aygit = "";
  private ctx: CanvasRenderingContext2D;
  private ciziyor = false;

  /** degisti: çizim sürerken ve her vuruş bitince çağrılır (bitti = vuruş tamamlandı). */
  constructor(private kanvas: HTMLCanvasElement, private degisti: (bitti: boolean) => void) {
    this.ctx = kanvas.getContext("2d")!;
    kanvas.addEventListener("pointerdown", (e) => this.basla(e));
    kanvas.addEventListener("pointermove", (e) => this.devam(e));
    kanvas.addEventListener("pointerup", () => this.bitir());
    kanvas.addEventListener("pointercancel", () => this.bitir());
    new ResizeObserver(() => this.boyutla()).observe(kanvas);
  }

  private nokta(e: PointerEvent): [number, number] {
    const r = this.kanvas.getBoundingClientRect();
    return [Math.round((e.clientX - r.left) * 10) / 10, Math.round((e.clientY - r.top) * 10) / 10];
  }

  private basla(e: PointerEvent) {
    if (this.kilitli || (e.pointerType === "mouse" && e.button !== 0)) return;
    this.kanvas.setPointerCapture(e.pointerId);
    this.ciziyor = true;
    this.aygit = e.pointerType;
    const [x, y] = this.nokta(e);
    this.vuruslar.push([[x], [y]]);
    this.yeniden();
    this.degisti(false);
  }

  private devam(e: PointerEvent) {
    // kilit, çizim sürerken de gelebilir (tanınma anında parmak hâlâ ekranda)
    if (!this.ciziyor || this.kilitli) return;
    const v = this.vuruslar[this.vuruslar.length - 1];
    for (const o of e.getCoalescedEvents?.() ?? [e]) {
      const [x, y] = this.nokta(o);
      const n = v[0].length - 1;
      if (x === v[0][n] && y === v[1][n]) continue;
      v[0].push(x); v[1].push(y);
    }
    this.yeniden();
    this.degisti(false);
  }

  private bitir() {
    if (!this.ciziyor) return;
    this.ciziyor = false;
    this.degisti(true);
  }

  temizle() {
    this.vuruslar = [];
    this.ciziyor = false;
    this.silme++;
    this.yeniden();
  }

  geriAl() {
    this.vuruslar.pop();
    this.silme++;
    this.yeniden();
  }

  private boyutla() {
    const r = this.kanvas.getBoundingClientRect();
    const o = devicePixelRatio || 1;
    this.kanvas.width = Math.round(r.width * o);
    this.kanvas.height = Math.round(r.height * o);
    this.ctx.setTransform(o, 0, 0, o, 0, 0);
    this.yeniden();
  }

  yeniden() {
    const c = this.ctx;
    c.save();
    c.setTransform(1, 0, 0, 1, 0, 0);
    c.clearRect(0, 0, this.kanvas.width, this.kanvas.height);
    c.restore();
    c.lineCap = "round";
    c.lineJoin = "round";
    c.lineWidth = 5;
    c.strokeStyle = getComputedStyle(this.kanvas).color;
    for (const [xs, ys] of this.vuruslar) {
      c.beginPath();
      c.moveTo(xs[0], ys[0]);
      if (xs.length === 1) c.lineTo(xs[0] + 0.01, ys[0]);
      for (let i = 1; i < xs.length; i++) c.lineTo(xs[i], ys[i]);
      c.stroke();
    }
  }
}
