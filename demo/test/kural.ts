// Oyun kuralının Python ile eşitliği (eşdeğer gruplar dahil). Fikstür: python egitim/kural_fikstur.py
import { readFileSync } from "node:fs";
import { tanindiMi } from "../src/oyun.ts";

type Fikstur = { esik: number; grup: number[]; ornekler: { olasilik: number[]; hedef: number; kabul: boolean }[] };
const f: Fikstur = JSON.parse(readFileSync(new URL("./kural_fikstur.json", import.meta.url), "utf8"));
const oku = (d: string) => JSON.parse(readFileSync(new URL(`../public/model/${d}`, import.meta.url), "utf8"));

// grup numaraları model.ts esdegerGruplar ile aynı yoldan (fetch yerine dosya)
const liste: { en: string }[] = oku("siniflar345.json");
const grup = liste.map((_, i) => i);
for (const adlar of oku("esdeger.json") as string[][]) {
  const uyeler = adlar.map((en) => liste.findIndex((s) => s.en === en)).filter((i) => i >= 0);
  for (const i of uyeler) grup[i] = Math.min(...uyeler);
}
const grupFarki = grup.filter((g, i) => g !== f.grup[i]).length;

let farkli = 0;
for (const o of f.ornekler) {
  const p = Float32Array.from(o.olasilik);
  const sira = Array.from(p.keys()).sort((a, b) => p[b] - p[a]);
  if (tanindiMi(sira, p, o.hedef, f.esik, grup) !== o.kabul) farkli++;
}
const kabul = f.ornekler.filter((o) => o.kabul).length;
console.log(`kural: ${f.ornekler.length} örnek (${kabul} kabul), farklı karar ${farkli}, farklı grup ${grupFarki}`);
if (farkli || grupFarki) process.exit(1);
console.log("kural testi geçti");
