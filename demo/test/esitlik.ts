// Python ve TS ön işlemesinin eşitliği. Fikstür: python egitim/esitlik_fikstur.py
import { readFileSync } from "node:fs";
import { ciz, type Vurus } from "../src/onisleme.ts";

type Ornek = { vuruslar: Vurus[]; pikseller: number[] };
const ornekler: Ornek[] = JSON.parse(readFileSync(new URL("./fikstur.json", import.meta.url), "utf8"));

let farkliOrnek = 0, farkliPiksel = 0, enBuyuk = 0;
for (const o of ornekler) {
  const p = ciz(o.vuruslar);
  let farkli = 0;
  for (let i = 0; i < p.length; i++) {
    const f = Math.abs(p[i] - o.pikseller[i]);
    if (f) { farkli++; if (f > enBuyuk) enBuyuk = f; }
  }
  if (farkli) { farkliOrnek++; farkliPiksel += farkli; }
}
console.log(`${ornekler.length} örnek, farklı örnek ${farkliOrnek}, farklı piksel ${farkliPiksel}, en büyük fark ${enBuyuk}`);
if (farkliOrnek) process.exit(1);
console.log("eşitlik testi geçti");
