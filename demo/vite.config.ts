import { mkdirSync, writeFileSync } from "node:fs";
import type { IncomingMessage, ServerResponse } from "node:http";
import { fileURLToPath } from "node:url";
import { defineConfig, type Connect } from "vite";

// "Çizimi kaydet": POST /api/kaydet gövdesi ../kayitlar/<zaman>-<rastgele>.json olarak yazılır.
// Yalnız yerel geliştirme/önizleme sunucusunda vardır; derlenmiş sayfada kayıt yoktur.
const KAYITLAR = new URL("../kayitlar/", import.meta.url);
const SINIR = 512 * 1024;

const kaydet: Connect.NextHandleFunction = (req: IncomingMessage, res: ServerResponse, next) => {
  if (req.url !== "/api/kaydet" || req.method !== "POST") return next();
  let govde = "";
  let asti = false;
  req.on("data", (p: Buffer) => {
    govde += p;
    if (govde.length > SINIR) { asti = true; req.destroy(); }
  });
  req.on("end", () => {
    if (asti) return;
    try {
      const k = JSON.parse(govde);
      if (typeof k.etiket !== "string" || !Array.isArray(k.vuruslar)) throw new Error("biçim");
      mkdirSync(KAYITLAR, { recursive: true });
      const ad = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}.json`;
      writeFileSync(new URL(ad, KAYITLAR), JSON.stringify(k));
      res.setHeader("content-type", "application/json");
      res.end(JSON.stringify({ ok: true, ad }));
    } catch {
      res.statusCode = 400;
      res.end(JSON.stringify({ ok: false }));
    }
  });
};

export default defineConfig({
  plugins: [{
    name: "cizim-kaydet",
    configureServer(s) { s.middlewares.use(kaydet); },
    configurePreviewServer(s) { s.middlewares.use(kaydet); },
  }],
  optimizeDeps: { exclude: ["onnxruntime-web"] },
  build: {
    rollupOptions: {
      input: {
        index: fileURLToPath(new URL("./index.html", import.meta.url)),
        topla: fileURLToPath(new URL("./topla.html", import.meta.url)),
      },
    },
  },
});
