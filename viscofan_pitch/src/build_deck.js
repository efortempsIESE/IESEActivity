const pptxgen = require("pptxgenjs");
const M = require("./model.json");

const OUT = process.argv[2] || "/home/user/IESEActivity/viscofan_pitch/HFQuantA_HedgeFund.pptx";

// ---------- palette & type
const NAVY = "14213D", NAVY2 = "22345C", ORANGE = "E8702A", SLATE = "5B7083",
  LIGHT = "F3F5F8", LINE = "D5DBE3", INK = "1E2530", MUTED = "6B7684",
  GREEN = "2E7D4F", RED = "B83B2E", WHITE = "FFFFFF";
const HF = "Cambria", BF = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.title = "Viscofan – Long – HF & Quant A";

const W = 13.333, MX = 0.5;
const eur = (v, d = 1) => "€" + v.toFixed(d);
const pct = (v, d = 1) => (v >= 0 ? "+" : "−") + Math.abs(v * 100).toFixed(d) + "%";
const fx = (v, d = 1) => v.toFixed(d) + "x";

function badge(slide, label, dark) {
  slide.addShape(pres.shapes.OVAL, { x: MX, y: 0.38, w: 0.42, h: 0.42, fill: { color: ORANGE }, line: { color: ORANGE } });
  slide.addText(label, { x: MX, y: 0.38, w: 0.42, h: 0.42, align: "center", valign: "middle", fontFace: BF, fontSize: label.length > 1 ? 11 : 14, bold: true, color: WHITE, margin: 0, isTextBox: true });
}
function kicker(slide, text, dark) {
  slide.addText(text.toUpperCase(), { x: MX + 0.55, y: 0.38, w: 8, h: 0.42, fontFace: BF, fontSize: 11, bold: true, charSpacing: 2, color: dark ? "AEB9CC" : SLATE, valign: "middle", margin: 0, isTextBox: true });
}
function title(slide, text, dark, y = 0.85) {
  slide.addText(text, { x: MX, y, w: W - 2 * MX, h: 0.75, fontFace: HF, fontSize: 24, bold: true, color: dark ? WHITE : NAVY, valign: "top", margin: 0, isTextBox: true });
}
function source(slide, text, dark) {
  slide.addText(text, { x: MX, y: 7.08, w: W - 2 * MX - 1.2, h: 0.3, fontFace: BF, fontSize: 8.5, color: dark ? "8E9AB0" : MUTED, valign: "bottom", margin: 0, isTextBox: true });
  slide.addText("HF & Quant A · Viscofan (BME:VIS)", { x: W - MX - 3, y: 7.08, w: 3, h: 0.3, fontFace: BF, fontSize: 8.5, color: dark ? "8E9AB0" : MUTED, align: "right", valign: "bottom", margin: 0, isTextBox: true });
}
function card(slide, x, y, w, h, fill) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill || LIGHT }, line: { color: fill || LIGHT } });
}
function txt(slide, text, o) {
  slide.addText(text, Object.assign({ fontFace: BF, fontSize: 12, color: INK, margin: 0, valign: "top", isTextBox: true }, o));
}
function bullets(slide, items, o) {
  const arr = items.map((t, i) => {
    const runs = Array.isArray(t) ? t : [{ text: t }];
    return runs.map((r, j) => ({ text: r.text, options: Object.assign({ bullet: j === 0 ? { indent: 12 } : undefined, breakLine: j === runs.length - 1 && i < items.length - 1, paraSpaceAfter: 4 }, r.options || {}) }));
  }).flat();
  slide.addText(arr, Object.assign({ fontFace: BF, fontSize: 12, color: INK, margin: 0, valign: "top", isTextBox: true }, o));
}
function table(slide, rows, o) {
  slide.addTable(rows, Object.assign({ fontFace: BF, fontSize: 11, color: INK, border: { type: "solid", pt: 0.5, color: LINE }, margin: [3, 5, 3, 5], valign: "middle" }, o));
}
const th = (t, o = {}) => ({ text: t, options: Object.assign({ bold: true, color: WHITE, fill: { color: NAVY }, align: "center" }, o) });
const td = (t, o = {}) => ({ text: t, options: Object.assign({ align: "center" }, o) });

const sc = M.sc, S = M.sum, I = M.inp, D = M.dcf, DV = M.dcfv;

// =====================================================================
// SLIDE 1 – Recommendation & thesis (dark)
{
  const s = pres.addSlide(); s.background = { color: NAVY };
  badge(s, "1"); kicker(s, "Recommendation & thesis", true);
  title(s, `LONG Viscofan: volumes are intact and the margin trough is temporary. Target ${eur(S.tp)} (${pct(S.up, 0)}) in 18–24 months`, true);

  // stat column
  const stats = [
    [`${eur(I.price, 2)} → ${eur(S.tp)}`, "Share price → probability-weighted target (15% bear / 50% base / 35% bull)"],
    [pct(S.up), "Price upside; base case assumes no re-rating"],
    [pct(S.tsr, 0), `Expected total return incl. ${eur(S.div, 2)} consensus dividends (~${(S.tsr_pa * 100).toFixed(0)}% p.a.)`],
    [fx(S.ud), `Upside / downside: bull ${pct(sc.up[2], 0)} vs bear ${pct(sc.up[0], 0)}`],
  ];
  stats.forEach((st, i) => {
    const y = 1.95 + i * 1.12;
    txt(s, st[0], { x: MX, y, w: 4.3, h: 0.55, fontFace: HF, fontSize: 30, bold: true, color: i === 0 ? ORANGE : WHITE });
    txt(s, st[1], { x: MX, y: y + 0.55, w: 4.3, h: 0.45, fontSize: 11, color: "C3CCDA" });
  });

  // thesis cards
  const cards = [
    ["Volumes held, prices pass through", `Like-for-like revenue +4.8% in 1H26 with volume growth in all four regions. Q2 revenue +4.3% in the middle of the Middle East conflict; H2-26 price increases already implemented.`],
    ["The margin dip is cyclical, not structural", `Like-for-like EBITDA margin 23.1% vs 21.4% reported: FX alone cost €14.6M of EBITDA. A +10% gas move costs only ~€1.7M of operating profit.`],
    ["Cheap on recovery, balance sheet intact", `${fx(I.ev / sc.ebitda[1])} EV / our FY27E EBITDA vs ${fx(S.tp_mult)} implied by the Street's €78.7 target. Net bank debt ${fx(I.nbd_x)} EBITDA funds €100M Beat'30 capex and ~€3.3/share dividends.`],
  ];
  cards.forEach((c, i) => {
    const x = 5.15, y = 1.95 + i * 1.5, w = 7.68, h = 1.35;
    card(s, x, y, w, h, NAVY2);
    txt(s, String(i + 1), { x: x + 0.2, y: y + 0.18, w: 0.45, h: 0.6, fontFace: HF, fontSize: 30, bold: true, color: ORANGE });
    txt(s, c[0], { x: x + 0.8, y: y + 0.15, w: w - 1.0, h: 0.35, fontFace: HF, fontSize: 15, bold: true, color: WHITE });
    txt(s, c[1], { x: x + 0.8, y: y + 0.52, w: w - 1.0, h: 0.75, fontSize: 11.5, color: "D6DDE8" });
  });

  card(s, MX, 6.48, W - 2 * MX, 0.55, "0E182E");
  txt(s, [
    { text: "Variant view: ", options: { bold: true, color: ORANGE } },
    { text: `the market prices Viscofan on FX-distorted trough numbers. We underwrite FY27E EBITDA of €${sc.ebitda[1]}M (4% below consensus) at today's 10x.   `, options: { color: WHITE } },
    { text: "Trade: ", options: { bold: true, color: ORANGE } },
    { text: `long, 30% USD overlay, stop-loss ${eur(I.stop)}`, options: { color: WHITE } },
  ], { x: MX + 0.2, y: 6.48, w: W - 2 * MX - 0.4, h: 0.55, fontSize: 11.5, valign: "middle" });
  source(s, "Sources: Viscofan 1H26 results presentation; S&P Capital IQ consensus (EUR); team model. Price €53.70 at 1 Oct 2026.", true);
  s.addNotes(`(~60s) We are long Viscofan, with an 18–24 month target of €${S.tp.toFixed(1)}, about 20% above today's €53.70, or roughly 32% including dividends. Three reasons. One: casing volumes are still growing everywhere, even through the Middle East conflict, and prices are going up in H2. Two: the margin drop is mostly FX and a one-off energy spike; like-for-like margin is 23%, not 21%. Three: at under 9x our FY27 EBITDA, with a 1x-levered balance sheet, the stock is cheap if margins simply normalise. We need no re-rating in our base case. The bull case is the Street's base case. Risk/reward is about 2 to 1, and we cap the downside with a stop at €45.6.`);
}

// =====================================================================
// SLIDE 2 – Company & market snapshot
{
  const s = pres.addSlide(); s.background = { color: WHITE };
  badge(s, "2"); kicker(s, "Company & market snapshot");
  title(s, "A global casing leader with defensive volumes, structural tailwinds and new growth options");

  const kpis = [
    [`€${I.ltm_rev.toLocaleString("en-US", { maximumFractionDigits: 0 })}M`, "LTM revenue (Jun-26)"],
    [`€${I.ltm_ebitda.toFixed(0)}M`, `LTM EBITDA · ${(I.ltm_margin * 100).toFixed(1)}% margin`],
    ["#1 globally", "Only player across all 4 casing technologies"],
    [fx(I.nbd_x), "Net bank debt / LTM EBITDA"],
  ];
  kpis.forEach((k, i) => {
    const w = 2.95, x = MX + i * (w + 0.18), y = 1.75;
    card(s, x, y, w, 1.0);
    txt(s, k[0], { x: x + 0.2, y: y + 0.1, w: w - 0.4, h: 0.5, fontFace: HF, fontSize: 24, bold: true, color: NAVY });
    txt(s, k[1], { x: x + 0.2, y: y + 0.6, w: w - 0.4, h: 0.32, fontSize: 11, color: MUTED });
  });

  // left: market & moat
  txt(s, "Why the franchise is defensive", { x: MX, y: 3.0, w: 4.4, h: 0.35, fontFace: HF, fontSize: 15, bold: true, color: NAVY });
  bullets(s, [
    [{ text: "Non-cyclical demand: ", options: { bold: true } }, { text: "€5.1B casing market, 2–4% volume growth a year (≈4% in 2025)" }],
    [{ text: "Gut → collagen replacement: ", options: { bold: true } }, { text: "multi-decade shift to manufactured casings" }],
    [{ text: "Cellulose consolidation: ", options: { bold: true } }, { text: "rivals cutting capacity while Viscofan expands (Zacapu, Mexico)" }],
    [{ text: "Beat'30 (2026–30): ", options: { bold: true } }, { text: "grow faster than the market, enrich mix (Health, Pet), net debt well below 2x" }],
  ], { x: MX, y: 3.42, w: 4.4, h: 3.3, fontSize: 12 });

  // middle: region doughnut
  txt(s, "1H26 revenue by region", { x: 5.15, y: 3.0, w: 4.4, h: 0.35, fontFace: HF, fontSize: 15, bold: true, color: NAVY });
  s.addChart(pres.charts.DOUGHNUT, [{ name: "Region", labels: ["EMEA", "N. America", "S. America", "Asia-Pac."], values: [254.8, 194.3, 99.2, 81.4] }], {
    x: 5.05, y: 3.35, w: 2.3, h: 2.3, holeSize: 58, chartColors: [NAVY, SLATE, ORANGE, "A9B6C6"], showLegend: false, showValue: false, showPercent: false, showTitle: false, dataLabelColor: WHITE,
  });
  const reg = [["EMEA", "40%", "−0.2%", NAVY], ["N. America", "31%", "+5.8%", SLATE], ["S. America", "16%", "+14.7%", ORANGE], ["Asia-Pacific", "13%", "+7.3%", "A9B6C6"]];
  reg.forEach((r, i) => {
    const y = 3.55 + i * 0.47;
    s.addShape(pres.shapes.OVAL, { x: 7.45, y: y + 0.08, w: 0.16, h: 0.16, fill: { color: r[3] }, line: { color: r[3] } });
    txt(s, [{ text: r[0] + " ", options: { bold: true } }, { text: `${r[1]} · LFL ${r[2]}`, options: { color: MUTED } }], { x: 7.7, y, w: 2.0, h: 0.4, fontSize: 10 });
  });
  txt(s, "Volumes grew in every region; EMEA held back by lower energy (cogeneration) sales (+1.9% ex energy).", { x: 5.15, y: 5.75, w: 4.4, h: 0.6, fontSize: 10, color: MUTED, italic: true });

  // right: margin history
  txt(s, "EBITDA margin (%)", { x: 9.75, y: 3.0, w: 3.1, h: 0.35, fontFace: HF, fontSize: 15, bold: true, color: NAVY });
  s.addChart(pres.charts.BAR, [{ name: "EBITDA margin", labels: ["FY21", "FY22", "FY23", "FY24", "FY25", "LTM"], values: [25.0, 21.8, 21.5, 23.2, 22.6, 21.5] }], {
    x: 9.6, y: 3.35, w: 3.3, h: 2.35, barDir: "col", chartColors: [NAVY], showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 9, dataLabelColor: INK, dataLabelFormatCode: "0.0",
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" }, catAxisLabelFontSize: 9, catAxisLabelColor: MUTED, valAxisMinVal: 15, valAxisMaxVal: 27, showLegend: false, barGapWidthPct: 45,
  });
  txt(s, "Margin dips have recovered before (2022 energy shock → 23.2% by FY24). 1H26 like-for-like margin: 23.1%.", { x: 9.75, y: 5.75, w: 3.1, h: 0.6, fontSize: 10, color: MUTED, italic: true });

  card(s, MX, 6.42, W - 2 * MX, 0.55);
  txt(s, [{ text: "Growth options: ", options: { bold: true, color: ORANGE } }, { text: "Health (€3.8M, +57%) and Pet treats (€8.3M, +88%) are only 1.9% of revenue. We value them in the bull case only. Energy (cogeneration, €26.0M, −15.4%) is a by-product of the plants, not a strategic division." }],
    { x: MX + 0.2, y: 6.42, w: W - 2 * MX - 0.4, h: 0.55, fontSize: 11, valign: "middle" });
  source(s, "Sources: Viscofan 1H26 results presentation pp.3–6; S&P Capital IQ (margin history, computed in USD); Viscofan annual report 2025 (market size).");
  s.addNotes("(~60s) Viscofan makes the casings that sausages are made in. It is number one globally and the only company making all four casing technologies. Demand follows processed-meat consumption, so it is not cyclical, and two long-term shifts help: replacement of animal gut with collagen, and consolidation in cellulose where competitors are cutting capacity while Viscofan adds it. Margins have dipped before, with the 2022 energy shock, and came back above 23% within two years. Health and Pet are exciting, but under 2% of sales, so we keep them as bull-case upside rather than build the thesis on them.");
}

// =====================================================================
// SLIDE 3 – Valuation
{
  const s = pres.addSlide(); s.background = { color: WHITE };
  badge(s, "3"); kicker(s, "Valuation");
  title(s, `Valuation: ${eur(S.tp)} probability-weighted target. The base case needs only margin recovery, not a re-rating`);

  // football field (manual)
  const fx0 = 40, fx1 = 85, X0 = 2.95, X1 = 7.65;
  const xv = v => X0 + (v - fx0) / (fx1 - fx0) * (X1 - X0);
  txt(s, "Value per share (€)", { x: MX, y: 1.8, w: 4, h: 0.35, fontFace: HF, fontSize: 15, bold: true, color: NAVY });
  const r1 = M.sens1.rows; // rows: [wacc, g1.0, g1.5, g2.0, g2.5, g3.0]
  const dcfLo = r1[4][2], dcfHi = r1[1][4]; // WACC 8.5% g1.5% ; WACC 7.0% g2.5%
  const r2 = M.sens2.rows; // consensus EBITDA row idx 4; cols 9x (2) to 11x (4)
  const mLo = r2[4][2], mHi = r2[4][4];
  const bars = [
    ["Scenarios (bear–bull)", "Exit EV/EBITDA 8.0–11.5x on FY27E", sc.px[0], sc.px[2], NAVY],
    ["DCF", "WACC 7.0–8.5%, g 1.5–2.5%", dcfLo, dcfHi, SLATE],
    ["Trading multiple", "9–11x consensus FY27E EBITDA", mLo, mHi, "8796AB"],
    ["Street target", "10 analysts; 7 Buy/Outperform", I.tp_cons - 0.35, I.tp_cons + 0.35, ORANGE],
  ];
  const Y0 = 2.35, BH = 0.42, GAP = 0.78;
  // axis ticks
  for (let v = 40; v <= 85; v += 10) {
    s.addShape(pres.shapes.LINE, { x: xv(v), y: Y0 - 0.1, w: 0, h: GAP * bars.length, line: { color: "E6EAF0", width: 0.75 } });
    txt(s, "€" + v, { x: xv(v) - 0.3, y: Y0 + GAP * bars.length - 0.05, w: 0.6, h: 0.25, fontSize: 9, color: MUTED, align: "center" });
  }
  bars.forEach((b, i) => {
    const y = Y0 + i * GAP;
    txt(s, b[0], { x: MX, y: y - 0.02, w: 2.4, h: 0.25, fontSize: 11.5, bold: true, color: INK });
    txt(s, b[1], { x: MX, y: y + 0.22, w: 2.4, h: 0.25, fontSize: 9, color: MUTED });
    s.addShape(pres.shapes.RECTANGLE, { x: xv(b[2]), y, w: xv(b[3]) - xv(b[2]), h: BH, fill: { color: b[4] }, line: { color: b[4] } });
    if (i < 3) {
      const inside = xv(I.price) > xv(b[2]) - 0.65 && xv(I.price) < xv(b[2]);
      if (inside) txt(s, eur(b[2]), { x: xv(b[2]) + 0.05, y, w: 0.6, h: BH, fontSize: 9.5, bold: true, valign: "middle", color: WHITE });
      else txt(s, eur(b[2]), { x: xv(b[2]) - 0.62, y, w: 0.58, h: BH, fontSize: 9.5, align: "right", valign: "middle", color: INK });
      txt(s, eur(b[3]), { x: xv(b[3]) + 0.05, y, w: 0.6, h: BH, fontSize: 9.5, valign: "middle", color: INK });
    } else {
      txt(s, eur(I.tp_cons, 2), { x: xv(b[3]) + 0.05, y, w: 0.7, h: BH, fontSize: 9.5, valign: "middle", color: INK });
    }
  });
  const yTop = Y0 - 0.25, hLine = GAP * bars.length + 0.05;
  s.addShape(pres.shapes.LINE, { x: xv(I.price), y: yTop, w: 0, h: hLine, line: { color: RED, width: 1.5, dashType: "dash" } });
  s.addShape(pres.shapes.LINE, { x: xv(S.tp), y: yTop, w: 0, h: hLine, line: { color: GREEN, width: 1.5, dashType: "dash" } });
  txt(s, `Price ${eur(I.price, 2)}`, { x: xv(I.price) - 1.2, y: yTop - 0.22, w: 1.15, h: 0.22, fontSize: 9.5, bold: true, color: RED, align: "right" });
  txt(s, `Target ${eur(S.tp)}`, { x: xv(S.tp) + 0.06, y: yTop - 0.22, w: 1.3, h: 0.22, fontSize: 9.5, bold: true, color: GREEN });

  // method box
  card(s, MX, 5.75, 7.2, 1.2);
  txt(s, "Methodology", { x: MX + 0.2, y: 5.83, w: 3, h: 0.3, fontSize: 12, bold: true, color: NAVY });
  txt(s, `Anchor: exit EV/EBITDA on FY27E EBITDA (the earnings the market will price at our exit), one share, no control premium. Cross-check: DCF ${eur(DV.px)} (WACC ${(DV.wacc * 100).toFixed(2)}%, g ${(DV.g * 100).toFixed(1)}%, terminal value ${(DV.tvpct * 100).toFixed(0)}% of EV, implied exit ${fx(DV.exitx)}). EV bridge: net debt €${I.nd.toFixed(0)}M incl. leases; ${I.shares.toFixed(1)}M diluted shares.`,
    { x: MX + 0.2, y: 6.12, w: 6.8, h: 0.8, fontSize: 10.5 });

  // scenario table
  txt(s, "Bear / base / bull (FY27E, € per share)", { x: 8.15, y: 1.8, w: 4.7, h: 0.35, fontFace: HF, fontSize: 15, bold: true, color: NAVY });
  const rows = [
    [th(""), th("Bear"), th("Base"), th("Bull")],
    [td("Probability", { align: "left" }), ...sc.prob.map(v => td((v * 100).toFixed(0) + "%"))],
    [td("FY27E EBITDA (€M)", { align: "left" }), ...sc.ebitda.map(v => td(v.toFixed(0)))],
    [td("vs consensus €328M", { align: "left", color: MUTED }), ...sc.vscons.map(v => td(pct(v, 0), { color: MUTED }))],
    [td("EV / EBITDA", { align: "left" }), ...sc.mult.map(v => td(fx(v)))],
    [td("Value per share", { align: "left", bold: true }), ...sc.px.map(v => td(eur(v), { bold: true }))],
    [td("Up / (down)side", { align: "left" }), ...sc.up.map(v => td(pct(v, 0), { bold: true, color: v >= 0 ? GREEN : RED }))],
  ];
  table(s, rows, { x: 8.15, y: 2.25, w: 4.68, colW: [1.86, 0.94, 0.94, 0.94], rowH: 0.36, fontSize: 11 });
  card(s, 8.15, 4.95, 4.68, 0.62, NAVY);
  txt(s, [{ text: `Weighted target ${eur(S.tp)}  ·  ${pct(S.up)}`, options: { bold: true, color: WHITE } }], { x: 8.3, y: 4.95, w: 4.4, h: 0.62, fontSize: 14, valign: "middle", align: "center" });
  bullets(s, [
    `Base: margin back to ~23% (1H26 LFL 23.1%) on H2 price increases; 10.0x = today's multiple`,
    `Bear: energy shock persists and USD weakens; de-rates toward food peers (~8x)`,
    `Bull: Hormuz normalises, USD tailwind, Health/Pet valued. 11.5x is still below the Street's implied ${fx(S.tp_mult)}`,
  ], { x: 8.15, y: 5.72, w: 4.68, h: 1.3, fontSize: 10 });
  source(s, "Sources: team model (Viscofan_HF_Model.xlsx); S&P Capital IQ consensus (EUR) and estimates; Viscofan 1H26 results presentation.");
  s.addNotes(`(~75s) Our anchor is an exit multiple on FY27 EBITDA, because that is what the market will be pricing when we exit. Base case: EBITDA recovers to €315M, which is 4% below consensus, at today's 10x. That gives €61, so the upside comes from earnings, not from multiple expansion. Bear: the energy shock persists, the dollar weakens and the stock de-rates to food-peer levels at 8x: €42. Bull: energy normalises and the dollar helps, at 11.5x: €78, which is roughly the Street's own target. Weighting 15/50/35 gives €${S.tp.toFixed(1)}. The DCF cross-checks at €${DV.px.toFixed(0)}, and every method except the bear case sits above today's price.`);
}

// =====================================================================
// SLIDE 4 – Variant view & catalysts
{
  const s = pres.addSlide(); s.background = { color: WHITE };
  badge(s, "4"); kicker(s, "Variant view & catalysts");
  title(s, "Variant view: the market is anchored on trough, FX-distorted 1H26 numbers. Catalysts arrive within our horizon");

  const rows = [
    [th("The market sees", { align: "left" }), th("We see", { align: "left" }), th("Evidence", { align: "left" })],
    [td("EBITDA −7.4%: a business in decline", { align: "left" }), td("Like-for-like EBITDA +3.1%; the decline is translation", { align: "left", bold: true }), td("FX −€14.6M of EBITDA (−10.1pp); LFL margin 23.1%", { align: "left", color: MUTED })],
    [td("Q2 cost shock (+16.8% consumption costs) is permanent", { align: "left" }), td("A one-off spike, already being priced through", { align: "left", bold: true }), td("H2-26 price increases + cost control; +10% gas ≈ €1.7M; Q2 revenue +4.3%", { align: "left", color: MUTED })],
    [td("FX is a structural drag", { align: "left" }), td("FX is turning: USD strength now helps", { align: "left", bold: true }), td("Finance-line FX swung to +€3.7M (1H25: −€14.0M)", { align: "left", color: MUTED })],
    [td("10x LTM EBITDA = full price", { align: "left" }), td(`${fx(I.ev / sc.ebitda[1])} our FY27E; ${fx(I.ev / M.cons.ebitda[1])} consensus FY27E`, { align: "left", bold: true }), td(`Street target implies ${fx(S.tp_mult)}; consensus EBITDA +18% FY26→28`, { align: "left", color: MUTED })],
  ];
  table(s, rows, { x: MX, y: 1.8, w: 7.6, colW: [2.35, 2.45, 2.8], rowH: [0.38, 0.72, 0.72, 0.72, 0.72], fontSize: 10.5 });

  // timeline
  txt(s, "Catalyst timeline", { x: 8.6, y: 1.75, w: 4.2, h: 0.35, fontFace: HF, fontSize: 15, bold: true, color: NAVY });
  const cats = [
    ["Late Oct 2026", "Q3 results", "First quarter with H2 price increases"],
    ["Feb 2027", "FY26 results + 2027 guidance", "Guidance reset from a trough base"],
    ["2027", "Zacapu cellulose ramp-up", "New capacity in a consolidating market"],
    ["2028", "Czech plant start-up", "České Budějovice: Beat'30 capacity"],
    ["Ongoing", "Short covering", "PDT 0.50% + Marble Bar 0.57% short (quant funds)"],
  ];
  const TX = 8.75, TY = 2.25, STEP = 0.62;
  s.addShape(pres.shapes.LINE, { x: TX + 0.09, y: TY + 0.1, w: 0, h: STEP * (cats.length - 1), line: { color: LINE, width: 2 } });
  cats.forEach((c, i) => {
    const y = TY + i * STEP;
    s.addShape(pres.shapes.OVAL, { x: TX, y: y + 0.01, w: 0.18, h: 0.18, fill: { color: i < 2 ? ORANGE : NAVY }, line: { color: WHITE, width: 1.5 } });
    txt(s, [{ text: c[0] + "  ", options: { bold: true, color: i < 2 ? ORANGE : NAVY } }, { text: c[1], options: { bold: true } }], { x: TX + 0.35, y: y - 0.04, w: 3.75, h: 0.28, fontSize: 11 });
    txt(s, c[2], { x: TX + 0.35, y: y + 0.24, w: 3.75, h: 0.28, fontSize: 9.5, color: MUTED });
  });

  // trade construction
  txt(s, "Trade construction", { x: MX, y: 5.45, w: 6, h: 0.35, fontFace: HF, fontSize: 15, bold: true, color: NAVY });
  const tc = [["Position", "Long VIS (EUR)"], ["Entry", eur(I.price, 2)], ["Target (18–24m)", eur(S.tp)], ["Stop-loss", `${eur(I.stop)} (−15%)`], ["FX overlay", "Sell USD fwd on 30% of position"], ["Sizing", "Upside/downside 2.1x"]];
  tc.forEach((t, i) => {
    const w = 1.95, x = MX + i * (w + 0.12), y = 5.85;
    card(s, x, y, w, 1.1, i === 2 ? NAVY : LIGHT);
    txt(s, t[0], { x: x + 0.15, y: y + 0.12, w: w - 0.3, h: 0.28, fontSize: 10, color: i === 2 ? "AEB9CC" : MUTED });
    txt(s, t[1], { x: x + 0.15, y: y + 0.42, w: w - 0.3, h: 0.6, fontSize: 13, bold: true, color: i === 2 ? WHITE : NAVY });
  });
  source(s, "Sources: Viscofan 1H26 results presentation pp.4–10, 13; S&P Capital IQ (consensus, short-interest disclosures Jul-26); team model.");
  s.addNotes(`(~60s) Our variant view: the headline numbers look bad, with EBITDA down 7%, but almost all of that is currency translation and a Q2 energy spike. Like-for-like, EBITDA grew 3%, and the company is already pushing prices through. FX is also turning: the stronger dollar already shows as gains in the finance line. So the stock trades at under 9x the earnings we expect in FY27, while the Street's own target implies 12x. Catalysts within our window: Q3 results this month as the first proof of price increases, then FY26 results and 2027 guidance in February. The disclosed shorts come from quant funds, so a better print could force covering. Trade: long at €53.70, target €${S.tp.toFixed(0)}, stop at €45.6, with a USD forward overlay.`);
}

// =====================================================================
// SLIDE 5 – Risks & mitigants
{
  const s = pres.addSlide(); s.background = { color: WHITE };
  badge(s, "5"); kicker(s, "Risks & mitigants");
  title(s, "Risks: FX and energy are the swing factors. Both are quantified, partly hedged and tracked quarterly");

  // manual EBITDA waterfall
  txt(s, "1H26 EBITDA bridge (€M)", { x: MX, y: 1.8, w: 4.6, h: 0.35, fontFace: HF, fontSize: 14, bold: true, color: NAVY });
  const steps = [["1H25", 145.2, "t"], ["Like-for-like", 4.5, "p"], ["FX", -14.6, "n"], ["Scope", -0.6, "n"], ["1H26", 134.5, "t"]];
  const base = 120, top = 152, GX = MX + 0.1, GY = 2.55, GH = 2.85, BW = 0.62, BG = 0.28;
  const yv = v => GY + GH - (v - base) / (top - base) * GH;
  let run = 0;
  steps.forEach((st, i) => {
    const x = GX + i * (BW + BG);
    let y0, y1, color;
    if (st[2] === "t") { y0 = base; y1 = st[1]; run = st[1]; color = NAVY; }
    else { const nr = run + st[1]; y0 = Math.min(run, nr); y1 = Math.max(run, nr); run = nr; color = st[2] === "p" ? GREEN : RED; }
    s.addShape(pres.shapes.RECTANGLE, { x, y: yv(y1), w: BW, h: Math.max(yv(y0) - yv(y1), 0.02), fill: { color }, line: { color } });
    const lab = st[2] === "t" ? st[1].toFixed(1) : (st[1] > 0 ? "+" : "−") + Math.abs(st[1]).toFixed(1);
    txt(s, lab, { x: x - 0.15, y: yv(y1) - 0.27, w: BW + 0.3, h: 0.25, fontSize: 10, bold: true, align: "center", color: st[2] === "t" ? INK : color });
    txt(s, st[0], { x: x - 0.2, y: GY + GH + 0.05, w: BW + 0.4, h: 0.25, fontSize: 9.5, align: "center", color: MUTED });
  });
  s.addShape(pres.shapes.LINE, { x: GX - 0.05, y: GY + GH, w: 5 * (BW + BG), h: 0, line: { color: LINE, width: 1 } });
  txt(s, "Axis starts at €120M. Like-for-like includes energy sales. Source: 1H26 presentation p.9.", { x: MX, y: 5.72, w: 4.6, h: 0.3, fontSize: 9, color: MUTED, italic: true });

  // risk table
  const rows = [
    [th("Risk", { align: "left" }), th("Impact (quantified)", { align: "left" }), th("Mitigants", { align: "left" }), th("We exit / review if", { align: "left" })],
    [td("FX: USD weakness vs EUR; MXN/BRL strength on costs", { align: "left", bold: true }),
      td("1H26: −€20.5M revenue (−3.3pp), −€14.6M EBITDA (−10.1pp). FX hits EBITDA ~3x harder than revenue", { align: "left" }),
      td("Plants located in USD/MXN/BRL zones (natural hedge); USD now strengthening; fund overlay sells USD forward on 30% of the position", { align: "left" }),
      td("EUR/USD back to 1H26 averages and Q3 FX drag widens", { align: "left", color: MUTED })],
    [td("Energy & raw materials (Middle East conflict)", { align: "left", bold: true }),
      td("Q2 consumption costs +16.8% (Q1 −2.2%); Q2 LFL EBITDA −2.4%; FY26 EBITDA guided to low end of range", { align: "left" }),
      td("H2-26 price increases + cost control; annual fixed-price fuel contracts; +10% gas ≈ only €1.7M operating profit; Cáseda efficiency capex", { align: "left" }),
      td("Q3 EBITDA margin below 1H26's 21.4%", { align: "left", color: MUTED })],
  ];
  table(s, rows, { x: 5.45, y: 1.8, w: 7.38, colW: [1.55, 2.0, 2.33, 1.5], rowH: [0.36, 1.45, 1.45], fontSize: 10 });

  card(s, 5.45, 5.25, 7.38, 0.95, "FBEDEA");
  txt(s, [{ text: `Downside scenario: ${eur(sc.px[0])} (${pct(sc.up[0], 0)}). `, options: { bold: true, color: RED } },
    { text: `Energy shock persists into 2027, USD weakens again, FY27E EBITDA €${sc.ebitda[0]}M at 8.0x (food-peer level). Our stop-loss at ${eur(I.stop)} caps the loss at −15%, above the bear value.` }],
    { x: 5.65, y: 5.25, w: 7.0, h: 0.95, fontSize: 11, valign: "middle" });
  txt(s, "Also monitored (appendix): de-rating vs food peers, Beat'30 execution (€100M capex, H2-weighted; Czech plant 2028), US tariffs on Brazilian exports (Pet Mania, <2% of revenue).",
    { x: MX, y: 6.35, w: W - 2 * MX, h: 0.5, fontSize: 10.5, color: INK });
  source(s, "Sources: Viscofan 1H26 results presentation pp.4, 8–10, 13; 1H26 Half-Year Financial Report (sensitivities); team model.");
  s.addNotes(`(~45s) What would make us wrong? First, FX. FX hits EBITDA three times harder than sales because Viscofan sells in dollars but produces partly in pesos and reais. Our answer is to sell dollars forward on about 30% of the position, and the dollar is currently moving in our favour. Second, energy: Q2 costs jumped 17%, but the gas sensitivity is small and prices are already going up. We review the position if the Q3 margin comes in below 21.4%. If both go wrong, the bear case is €42; our stop at €45.6 limits the loss to 15%.`);
}

// =====================================================================
// APPENDIX
function appx(label, kick, ttl) {
  const s = pres.addSlide(); s.background = { color: WHITE };
  badge(s, label); kicker(s, "Appendix · " + kick); title(s, ttl);
  return s;
}
// A1 results detail
{
  const s = appx("A1", "1H26 results", "1H26: like-for-like growth intact, reported numbers hit by FX and Q2 costs");
  const r = (l, a, b, c, d, bold) => [td(l, { align: "left", bold }), td(a, { bold }), td(b), td(c, { color: c.startsWith("−") ? RED : GREEN }), td(d, { color: d.startsWith("−") ? RED : d === "–" ? MUTED : GREEN })];
  const rows = [
    [th("€M", { align: "left" }), th("1H26"), th("1H25"), th("Reported"), th("Like-for-like")],
    r("Revenue", "629.8", "618.8", "+1.8%", "+4.8%", true),
    r("EBITDA", "134.5", "145.2", "−7.4%", "+3.1%", true),
    r("EBITDA margin", "21.4%", "23.5%", "−2.1pp", "−0.4pp"),
    r("Operating profit", "91.8", "101.8", "−9.9%", "–"),
    r("Net finance result", "−1.3", "−18.1", "+92.9%", "–"),
    r("Taxes", "−19.5", "−14.0", "−39.7%", "–"),
    r("Net profit", "71.3", "69.8", "+2.2%", "–", true),
  ];
  table(s, rows, { x: MX, y: 1.8, w: 6.2, colW: [2.0, 1.0, 1.0, 1.1, 1.1], rowH: 0.42, fontSize: 11 });
  const q = [
    [th("Q2 (€M)", { align: "left" }), th("2Q26"), th("2Q25"), th("Reported"), th("LFL")],
    r("Revenue", "325.0", "311.5", "+4.3%", "+4.9%", true),
    r("EBITDA", "71.1", "76.3", "−6.9%", "−2.4%", true),
    r("Net profit", "37.7", "38.4", "−2.0%", "–"),
  ];
  table(s, q, { x: 7.1, y: 1.8, w: 5.73, colW: [1.6, 1.0, 1.0, 1.05, 1.08], rowH: 0.42, fontSize: 11 });
  bullets(s, [
    "Net profit growth (+2.2%) came from the finance line: FX differences +€3.7M vs −€14.0M. Operating profit fell 9.9%, so we lead with like-for-like EBITDA.",
    "Effective tax rate 21.5% vs 16.7% (1H25 included a €5M US tax-loss credit).",
    "Divisions: Food, Packaging & Ingredients €591.7M (+1.8%); Health €3.8M (+57.3%); Pet €8.3M (+87.8%, incl. Pet Mania scope); Energy €26.0M (−15.4%).",
  ], { x: 7.1, y: 3.75, w: 5.73, h: 2.6, fontSize: 11 });
  source(s, "Source: Viscofan Results Presentation January–June 2026, pp.3–10, 14–15.");
}
// A2 DCF
{
  const s = appx("A2", "DCF", `DCF cross-check: ${eur(DV.px)} per share at a ${(DV.wacc * 100).toFixed(2)}% WACC and 2.0% terminal growth`);
  const yrs = ["FY26E", "FY27E", "FY28E", "FY29E", "FY30E", "FY31E"];
  const f1 = v => v.toFixed(1), fp = v => (v * 100).toFixed(1) + "%";
  const row = (l, arr, f, o = {}) => [td(l, Object.assign({ align: "left" }, o)), ...arr.map(v => td(v == null ? "–" : f(v), o))];
  const rows = [
    [th("€M", { align: "left" }), ...yrs.map(y => th(y))],
    row("Revenue", D.rev, f1, { bold: true }),
    row("growth", D.growth, fp, { color: MUTED }),
    row("EBITDA", D.ebitda, f1, { bold: true }),
    row("margin", D.margin, fp, { color: MUTED }),
    row("− Taxes on EBIT (22%)", D.tax, f1),
    row("− Capex", D.capex, f1),
    row("− Increase in NWC", D.nwc, f1),
    row("Unlevered FCF", D.fcf, f1, { bold: true }),
    row("PV of FCF", D.pv.map((v, i) => i === 0 ? null : v), f1),
  ];
  table(s, rows, { x: MX, y: 1.8, w: 8.0, colW: [2.3, 0.95, 0.95, 0.95, 0.95, 0.95, 0.95], rowH: 0.37, fontSize: 10.5 });
  txt(s, "FY26E shown for reference, not discounted (conservative). End-year discounting from 1 Oct 2026.", { x: MX, y: 5.6, w: 8, h: 0.3, fontSize: 9.5, color: MUTED, italic: true });
  const v = [
    [th("WACC & value", { align: "left" }), th("")],
    [td("Cost of equity (Rf 3.58% + 0.85 × 5.5%)", { align: "left" }), td(fp(DV.ke))],
    [td("After-tax cost of debt", { align: "left" }), td("3.0%")],
    [td("Weights E / D (market)", { align: "left" }), td("89% / 11%")],
    [td("WACC · terminal growth", { align: "left", bold: true }), td(`${(DV.wacc * 100).toFixed(2)}% · ${fp(DV.g)}`, { bold: true })],
    [td("PV FCF FY27–31", { align: "left" }), td("€" + DV.sumpv.toFixed(0) + "M")],
    [td("PV terminal value", { align: "left" }), td("€" + DV.pvtv.toFixed(0) + "M")],
    [td("Enterprise value", { align: "left" }), td("€" + DV.ev.toFixed(0) + "M")],
    [td("− Net debt (incl. leases)", { align: "left" }), td("€" + I.nd.toFixed(0) + "M")],
    [td("Value per share", { align: "left", bold: true }), td(eur(DV.px, 2), { bold: true })],
  ];
  table(s, v, { x: 8.85, y: 1.8, w: 3.98, colW: [2.68, 1.3], rowH: 0.37, fontSize: 10.5 });
  bullets(s, [
    `Terminal value ${(DV.tvpct * 100).toFixed(0)}% of EV; implied exit ${fx(DV.exitx)} FY31 EBITDA, below today's 10x`,
    "Margins capped at 24%, inside the 21.5–25% FY21–LTM range",
  ], { x: 8.85, y: 5.65, w: 3.98, h: 1.0, fontSize: 10 });
  source(s, "Sources: team model; Viscofan 1H26 presentation (capex €100M FY26, D&A, tax rate); S&P Capital IQ (Spain 10Y). Beta and ERP are team assumptions.");
}
// A3 sensitivities
{
  const s = appx("A3", "Sensitivities", "Sensitivities: the upside holds across most reasonable WACC, growth and multiple assumptions");
  const colr = v => v >= I.price ? "E3F1E7" : "F8E1DE";
  const g = M.sens1;
  const rows = [[th("WACC \\ g"), ...g.g.map(x => th((x * 100).toFixed(1) + "%"))],
    ...g.rows.map(r => [td((r[0] * 100).toFixed(1) + "%", { bold: true }), ...r.slice(1).map(v => td(eur(v), { fill: { color: colr(v) } }))])];
  txt(s, "DCF value per share (€): WACC × terminal growth", { x: MX, y: 1.8, w: 6, h: 0.35, fontFace: HF, fontSize: 14, bold: true, color: NAVY });
  table(s, rows, { x: MX, y: 2.25, w: 5.9, colW: [1.15, 0.95, 0.95, 0.95, 0.95, 0.95], rowH: 0.42, fontSize: 11 });
  const m = M.sens2;
  const rows2 = [[th("EBITDA \\ x"), ...m.m.map(x => th(fx(x)))],
    ...m.rows.map(r => [td("€" + r[0].toFixed(0) + "M" + (Math.abs(r[0] - 328.06) < 0.1 ? " (cons.)" : r[0] === 315 ? " (base)" : ""), { bold: true }), ...r.slice(1).map(v => td(eur(v), { fill: { color: colr(v) } }))])];
  txt(s, "Exit value per share (€): FY27E EBITDA × EV/EBITDA", { x: 6.9, y: 1.8, w: 6, h: 0.35, fontFace: HF, fontSize: 14, bold: true, color: NAVY });
  table(s, rows2, { x: 6.9, y: 2.25, w: 5.93, colW: [1.68, 0.85, 0.85, 0.85, 0.85, 0.85], rowH: 0.42, fontSize: 11 });
  txt(s, `Green = above today's €53.70; red = below. Each 1.0x of multiple ≈ €${(sc.ebitda[1] / I.shares).toFixed(1)}/share; each €10M of EBITDA at 10x ≈ €${(100 / I.shares).toFixed(1)}/share.`, { x: MX, y: 5.9, w: 12.3, h: 0.4, fontSize: 11, color: INK });
  source(s, "Source: team model (Viscofan_HF_Model.xlsx, Sensitivity tab).");
}
// A4 cash & balance sheet
{
  const s = appx("A4", "Cash generation & Beat'30", "A strong balance sheet funds Beat'30 capex and continued shareholder returns");
  const nb = [["Net bank debt Dec-25", 206.1], ["EBITDA", -134.5], ["Tax paid", 21.9], ["Working capital", 41.3], ["Capex", 34.5], ["FX & others", 7.0], ["Shareholder remuneration", 107.0], ["Net bank debt Jun-26", 283.3]];
  const rows = [[th("Net bank debt bridge (€M)", { align: "left" }), th("")], ...nb.map((r, i) => [td(r[0], { align: "left", bold: i === 0 || i === 7 }), td((r[1] > 0 && i > 0 && i < 7 ? "+" : r[1] < 0 ? "−" : "") + Math.abs(r[1]).toFixed(1), { bold: i === 0 || i === 7 })])];
  table(s, rows, { x: MX, y: 1.8, w: 5.2, colW: [3.6, 1.6], rowH: 0.4, fontSize: 11 });
  bullets(s, [
    `Net bank debt / LTM EBITDA ${fx(I.nbd_x)} (Dec-25: 0.71x). The increase is the €107M payout (incl. €1.00 extraordinary dividend and the buyback completed Feb-26), not operations`,
    "+1% interest rates ≈ −€1.1M operating profit: immaterial",
    "Consensus DPS €3.29 / €3.39 / €3.54 (FY26–28E)",
  ], { x: MX, y: 5.55, w: 5.2, h: 1.4, fontSize: 10.5 });
  txt(s, "Beat'30 capex 2026E: €100M (+19% vs 2025)", { x: 6.4, y: 1.8, w: 6.4, h: 0.35, fontFace: HF, fontSize: 14, bold: true, color: NAVY });
  s.addChart(pres.charts.DOUGHNUT, [{ name: "Capex mix", labels: ["Capacity", "Process improvements", "Environment & safety", "Other recurring"], values: [56, 20, 13, 11] }], {
    x: 6.3, y: 2.2, w: 2.6, h: 2.6, holeSize: 55, chartColors: [NAVY, SLATE, ORANGE, "A9B6C6"], showLegend: false, showPercent: true, showValue: false, dataLabelColor: WHITE, dataLabelFontSize: 10,
  });
  [["Capacity", "56%", NAVY], ["Process improvements", "20%", SLATE], ["Environment & safety", "13%", ORANGE], ["Other recurring", "11%", "A9B6C6"]].forEach((r, i) => {
    const y = 2.6 + i * 0.45;
    s.addShape(pres.shapes.OVAL, { x: 9.1, y: y + 0.07, w: 0.16, h: 0.16, fill: { color: r[2] }, line: { color: r[2] } });
    txt(s, [{ text: r[1] + "  ", options: { bold: true } }, { text: r[0] }], { x: 9.35, y, w: 3.4, h: 0.32, fontSize: 11 });
  });
  bullets(s, [
    [{ text: "US (New Jersey): ", options: { bold: true } }, { text: "collagen capacity with new technology (completed)" }],
    [{ text: "Mexico (Zacapu): ", options: { bold: true } }, { text: "cellulose extrusion capacity" }],
    [{ text: "Czech Republic: ", options: { bold: true } }, { text: "plant relocation, České Budějovice (start 2028)" }],
    [{ text: "Spain (Cáseda) & cross-plant: ", options: { bold: true } }, { text: "energy efficiency, water, safety" }],
  ], { x: 6.4, y: 5.0, w: 6.4, h: 1.9, fontSize: 10.5 });
  source(s, "Sources: Viscofan 1H26 presentation pp.11–12; 1H26 Half-Year Financial Report; S&P Capital IQ consensus.");
}
// A5 comps & data integrity
{
  const s = appx("A5", "Comparables & data integrity", "Comparables and data integrity: why we rebuilt the source analysis in EUR");
  const rows = [
    [th("Company", { align: "left" }), th("TEV/EBITDA"), th("P/E"), th("EBITDA margin")],
    [td("Viscofan (BME:VIS)", { align: "left", bold: true }), td("9.9x", { bold: true }), td("15.0x", { bold: true }), td("21.5%", { bold: true })],
    [td("Ebro Foods (BME:EBRO)", { align: "left" }), td("7.5x"), td("12.5x"), td("13.3%")],
  ];
  table(s, rows, { x: MX, y: 1.8, w: 6.0, colW: [2.4, 1.2, 1.2, 1.2], rowH: 0.42, fontSize: 11 });
  bullets(s, [
    "Direct casing peers are few and mostly private: Devro was taken private by SARIA (2022); Shenguan (HK:0829) is a small Chinese collagen player; Viskase is controlled by Icahn. Hence multiples are a secondary check",
    "The 30% premium to Ebro reflects ~8pp higher margins and niche leadership. Our base case keeps it; our bear case removes it",
    "The broad agri/food peer set in the source reports (salmon, olive oil, agri-commodities) was dropped as not comparable",
  ], { x: MX, y: 3.25, w: 6.0, h: 3.5, fontSize: 11 });
  txt(s, "Corrections to the source reports", { x: 7.0, y: 1.8, w: 5.8, h: 0.35, fontFace: HF, fontSize: 14, bold: true, color: NAVY });
  bullets(s, [
    "Source DCF and comps mixed USD figures with a EUR share price; we rebuilt everything in EUR",
    "USD consensus implied +8.6% FY26 revenue growth (FX translation); we use EUR consensus (EBITDA €300.5M / €328.1M / €355.9M)",
    "Leverage: the source's 29% debt weight was book-based; market weights give 11%",
    "€21.9M in the debt bridge is tax paid, not FX; the Middle East shock is 2026, not 2025",
    "Devro is owned by SARIA, not Shenguan",
  ], { x: 7.0, y: 2.25, w: 5.83, h: 4.5, fontSize: 11 });
  source(s, "Sources: S&P Capital IQ multiples (priced 30 Sep 2026); team review of source research reports.");
}
// A6 team
{
  const s = appx("A6", "Team contribution", "Team contribution: HF & Quant A");
  const team = [["Carmen Gavilanes", "[role to confirm]"], ["Eduardo Fortemps", "[role to confirm]"], ["Ignacio Queipo de Llano", "[role to confirm]"], ["Jaime Gefaell", "[role to confirm]"], ["MiM student", "[name & role]"]];
  team.forEach((t, i) => {
    const w = 2.3, x = MX + i * (w + 0.2), y = 2.2;
    card(s, x, y, w, 2.4);
    s.addShape(pres.shapes.OVAL, { x: x + w / 2 - 0.45, y: y + 0.3, w: 0.9, h: 0.9, fill: { color: NAVY }, line: { color: NAVY } });
    txt(s, t[0] === "MiM student" ? "+1" : t[0].split(" ").map(p => p[0]).slice(0, 2).join(""), { x: x + w / 2 - 0.45, y: y + 0.3, w: 0.9, h: 0.9, fontSize: 20, bold: true, color: WHITE, align: "center", valign: "middle" });
    txt(s, t[0], { x: x + 0.1, y: y + 1.3, w: w - 0.2, h: 0.55, valign: "middle", fontSize: 13, bold: true, color: NAVY, align: "center" });
    txt(s, t[1], { x: x + 0.1, y: y + 1.9, w: w - 0.2, h: 0.4, fontSize: 11, color: MUTED, align: "center" });
  });
  txt(s, "Roles: Company & market · Thesis & variant view · Valuation · Risks & downside · Slides & storyline", { x: MX, y: 5.0, w: 12.3, h: 0.4, fontSize: 11, color: MUTED });
  source(s, "IESE MiF & MiM Finance Pitch Competition · 1–2 October 2026");
}

pres.writeFile({ fileName: OUT }).then(f => console.log("wrote", f));
