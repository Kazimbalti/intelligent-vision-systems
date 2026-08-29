// Generates 14 lecture decks for "Applied Intelligent Vision Systems".
// Theme: edge-AI. Dark slate title/section, light content. Motif: numbered
// circles + teal rounded cards. Accent = lime (detection-box green).
const pptxgen = require("pptxgenjs");

// ---- palette -----------------------------------------------------------
const INK = "0E2233";     // deep slate (dominant dark)
const INK2 = "14324A";    // lighter slate panel
const TEAL = "0E9AA7";    // primary teal
const TEAL_D = "0B7D88";
const LIME = "A3E635";     // accent (detection box)
const WHITE = "FFFFFF";
const PAPER = "F7FAFC";    // light content bg
const TEXT = "1F2937";     // body text
const MUTE = "6B7280";     // captions
const CARD = "EAF3F5";     // tinted card on light bg

const FS = "Calibri";           // body (safe)
const FH = "Century Schoolbook"; // header serif (safe, has personality)

function shadow() {
  return { type: "outer", color: "1F2937", blur: 7, offset: 3, angle: 90, opacity: 0.22 };
}

// ---- reusable slide builders ------------------------------------------
function bg(slide, color) { slide.background = { color }; }

function footer(slide, deck, dark) {
  slide.addText(
    [{ text: "Applied Intelligent Vision Systems", options: { color: dark ? "9FB3C8" : MUTE } },
     { text: `   •   Lecture ${deck.num}`, options: { color: dark ? TEAL : TEAL_D, bold: true } }],
    { x: 0.5, y: 7.06, w: 8, h: 0.3, fontFace: FS, fontSize: 9, align: "left" });
  slide.addText(`${deck.numPad}`, { x: 12.2, y: 7.0, w: 0.6, h: 0.35, fontFace: FH, fontSize: 12, color: dark ? "9FB3C8" : MUTE, align: "right" });
}

function titleBand(slide, txt) {
  slide.addText(txt, { x: 0.6, y: 0.5, w: 12.1, h: 0.9, fontFace: FH, fontSize: 32, bold: true, color: INK, align: "left" });
}

function numCircle(slide, x, y, n, d = 0.5) {
  slide.addShape("ellipse", { x, y, w: d, h: d, fill: { color: TEAL }, line: { type: "none" } });
  slide.addText(String(n), { x, y, w: d, h: d, align: "center", valign: "middle", fontFace: FH, fontSize: 16, bold: true, color: WHITE });
}

// visual panel on the right of a content slide (keeps every slide visual)
function visualPanel(slide, tag, chips) {
  slide.addShape("roundRect", { x: 9.15, y: 1.7, w: 3.55, h: 4.9, rectRadius: 0.14, fill: { color: TEAL }, line: { type: "none" }, shadow: shadow() });
  // bounding-box motif
  slide.addShape("roundRect", { x: 9.55, y: 2.15, w: 2.75, h: 1.7, rectRadius: 0.06, fill: { color: "0B7D88" }, line: { color: LIME, width: 2.5 } });
  slide.addText(tag, { x: 9.35, y: 3.95, w: 3.15, h: 1.5, fontFace: FH, fontSize: 24, bold: true, color: WHITE, align: "center", valign: "middle" });
  if (chips && chips.length) {
    let cy = 5.35;
    chips.slice(0, 3).forEach((c) => {
      slide.addShape("roundRect", { x: 9.55, y: cy, w: 2.75, h: 0.34, rectRadius: 0.17, fill: { color: "0B6E78" }, line: { type: "none" } });
      slide.addText(c, { x: 9.55, y: cy, w: 2.75, h: 0.34, align: "center", valign: "middle", fontFace: FS, fontSize: 11, color: WHITE });
      cy += 0.4;
    });
  }
}

function bullets(slide, items, x, y, w, h) {
  const arr = items.map((t, i) => ({
    text: t, options: { bullet: { code: "2022", indent: 14 }, color: TEXT, breakLine: true, paraSpaceAfter: 10 }
  }));
  slide.addText(arr, { x, y, w, h, fontFace: FS, fontSize: 15.5, valign: "top", align: "left" });
}

// ---- slide type renderers ---------------------------------------------
function sTitle(pptx, deck) {
  const s = pptx.addSlide(); bg(s, INK);
  s.addShape("roundRect", { x: 0.6, y: 1.5, w: 2.4, h: 0.75, rectRadius: 0.1, fill: { color: TEAL }, line: { type: "none" } });
  s.addText(`LECTURE ${deck.num}`, { x: 0.6, y: 1.5, w: 2.4, h: 0.75, align: "center", valign: "middle", fontFace: FH, fontSize: 18, bold: true, color: WHITE });
  s.addText(deck.title, { x: 0.6, y: 2.5, w: 11.5, h: 2.2, fontFace: FH, fontSize: 44, bold: true, color: WHITE, align: "left", valign: "top" });
  s.addText(deck.tagline, { x: 0.62, y: 4.75, w: 10.5, h: 1.0, fontFace: FS, fontSize: 18, italic: true, color: LIME, align: "left" });
  // motif: three stacked accent bars
  s.addShape("roundRect", { x: 11.2, y: 4.9, w: 1.5, h: 0.16, rectRadius: 0.08, fill: { color: TEAL }, line: { type: "none" } });
  s.addShape("roundRect", { x: 11.4, y: 5.2, w: 1.3, h: 0.16, rectRadius: 0.08, fill: { color: TEAL_D }, line: { type: "none" } });
  s.addShape("roundRect", { x: 11.6, y: 5.5, w: 1.1, h: 0.16, rectRadius: 0.08, fill: { color: LIME }, line: { type: "none" } });
  s.addText("Applied Intelligent Vision Systems  •  Edge, Embedded & Drone  •  RPi 5 · Hailo · ESP32-CAM",
    { x: 0.6, y: 6.7, w: 12, h: 0.4, fontFace: FS, fontSize: 12, color: "9FB3C8" });
  s.addNotes(deck.note || `Lecture ${deck.num}: ${deck.title}. ${deck.tagline}`);
}

function sOutcomes(pptx, deck) {
  const s = pptx.addSlide(); bg(s, PAPER);
  titleBand(s, "Learning outcomes");
  const o = deck.outcomes;
  const n = o.length;
  const cardH = Math.min(1.15, (5.2 - (n - 1) * 0.25) / n);
  let y = 1.7;
  o.forEach((it, i) => {
    s.addShape("roundRect", { x: 0.6, y, w: 12.1, h: cardH, rectRadius: 0.1, fill: { color: WHITE }, line: { color: "D9E2E8", width: 1 }, shadow: shadow() });
    numCircle(s, 0.85, y + (cardH - 0.5) / 2, i + 1);
    s.addText([{ text: it.tag + "  ", options: { bold: true, color: TEAL_D } }, { text: it.text, options: { color: TEXT } }],
      { x: 1.55, y, w: 11.0, h: cardH, valign: "middle", fontFace: FS, fontSize: 15, align: "left" });
    y += cardH + 0.25;
  });
  footer(s, deck, false);
  s.addNotes("Walk through each intended outcome; each maps to a course CLO.");
}

function sAgenda(pptx, deck) {
  const s = pptx.addSlide(); bg(s, PAPER);
  titleBand(s, "Roadmap for today");
  const a = deck.agenda;
  const colX = [0.6, 6.65];
  const half = Math.ceil(a.length / 2);
  a.forEach((t, i) => {
    const col = i < half ? 0 : 1;
    const row = i < half ? i : i - half;
    const x = colX[col]; const y = 1.75 + row * 0.92;
    s.addShape("roundRect", { x, y, w: 6.05, h: 0.78, rectRadius: 0.1, fill: { color: CARD }, line: { type: "none" } });
    numCircle(s, x + 0.15, y + 0.14, i + 1);
    s.addText(t, { x: x + 0.85, y, w: 5.05, h: 0.78, valign: "middle", fontFace: FS, fontSize: 14.5, color: TEXT, align: "left" });
  });
  footer(s, deck, false);
  s.addNotes("Preview the flow so students know where the lecture is going.");
}

function sContent(pptx, deck, sl) {
  const s = pptx.addSlide(); bg(s, PAPER);
  titleBand(s, sl.h);
  bullets(s, sl.b, 0.6, 1.75, 8.2, 4.9);
  visualPanel(s, sl.tag || "", sl.chips);
  footer(s, deck, false);
  if (sl.note) s.addNotes(sl.note);
}

function sTwo(pptx, deck, sl) {
  const s = pptx.addSlide(); bg(s, PAPER);
  titleBand(s, sl.h);
  const cards = [[0.6, sl.lh, sl.l, TEAL], [6.75, sl.rh, sl.r, INK2]];
  cards.forEach(([x, head, items, hc]) => {
    s.addShape("roundRect", { x, y: 1.75, w: 5.95, h: 4.85, rectRadius: 0.12, fill: { color: WHITE }, line: { color: "D9E2E8", width: 1 }, shadow: shadow() });
    s.addShape("roundRect", { x, y: 1.75, w: 5.95, h: 0.7, rectRadius: 0.12, fill: { color: hc }, line: { type: "none" } });
    s.addText(head, { x: x + 0.2, y: 1.75, w: 5.55, h: 0.7, valign: "middle", fontFace: FH, fontSize: 18, bold: true, color: WHITE });
    bullets(s, items, x + 0.3, 2.6, 5.35, 3.8);
  });
  footer(s, deck, false);
  if (sl.note) s.addNotes(sl.note);
}

function sProcess(pptx, deck, sl) {
  const s = pptx.addSlide(); bg(s, PAPER);
  titleBand(s, sl.h);
  const steps = sl.steps; const n = steps.length;
  const w = 12.1 / n; const y = 2.9;
  steps.forEach((t, i) => {
    const x = 0.6 + i * w;
    s.addShape("roundRect", { x: x + 0.12, y, w: w - 0.35, h: 1.7, rectRadius: 0.1, fill: { color: i % 2 ? INK2 : TEAL }, line: { type: "none" }, shadow: shadow() });
    s.addText(String(i + 1), { x: x + 0.12, y: y + 0.12, w: 0.6, h: 0.5, fontFace: FH, fontSize: 20, bold: true, color: LIME });
    s.addText(t, { x: x + 0.2, y: y + 0.55, w: w - 0.5, h: 1.05, valign: "top", fontFace: FS, fontSize: 12.5, color: WHITE, align: "left" });
    if (i < n - 1) s.addText("▶", { x: x + w - 0.28, y: y + 0.55, w: 0.35, h: 0.5, fontFace: FS, fontSize: 14, color: TEAL_D, align: "center" });
  });
  if (sl.cap) s.addText(sl.cap, { x: 0.6, y: 5.1, w: 12.1, h: 0.6, fontFace: FS, fontSize: 13, italic: true, color: MUTE, align: "center" });
  footer(s, deck, false);
  if (sl.note) s.addNotes(sl.note);
}

function sStats(pptx, deck, sl) {
  const s = pptx.addSlide(); bg(s, INK);
  s.addText(sl.h, { x: 0.6, y: 0.5, w: 12.1, h: 0.9, fontFace: FH, fontSize: 32, bold: true, color: WHITE });
  const st = sl.stats; const n = st.length; const w = 12.1 / n;
  st.forEach((o, i) => {
    const x = 0.6 + i * w;
    s.addText(o.n, { x, y: 2.3, w: w - 0.3, h: 1.4, fontFace: FH, fontSize: 54, bold: true, color: LIME, align: "center" });
    s.addText(o.l, { x, y: 3.8, w: w - 0.3, h: 1.0, fontFace: FS, fontSize: 14, color: "CADCFC", align: "center", valign: "top" });
  });
  footer(s, deck, true);
  if (sl.note) s.addNotes(sl.note);
}

function sTier(pptx, deck, sl) {
  const s = pptx.addSlide(); bg(s, PAPER);
  titleBand(s, sl.h || "The compute-tier ladder");
  const tiers = [
    ["ESP32-CAM", "microcontroller · TinyML/FOMO · KB models · ~mW", "83A3B0"],
    ["Raspberry Pi 5 (CPU)", "flexible · OpenCV / small CNN · a few FPS", TEAL_D],
    ["Pi 5 + Hailo NPU", "compiled .hef · 30+ FPS · offline", TEAL],
    ["Drone / Robot", "perception → action · Tello / ROS 2", INK2],
  ];
  let y = 1.75;
  tiers.forEach((t, i) => {
    s.addShape("roundRect", { x: 0.9 + i * 0.15, y, w: 9.0, h: 1.05, rectRadius: 0.1, fill: { color: t[2] }, line: { type: "none" }, shadow: shadow() });
    s.addText(t[0], { x: 1.2 + i * 0.15, y: y + 0.1, w: 8.5, h: 0.5, fontFace: FH, fontSize: 19, bold: true, color: WHITE });
    s.addText(t[1], { x: 1.2 + i * 0.15, y: y + 0.55, w: 8.5, h: 0.42, fontFace: FS, fontSize: 12.5, color: "EAF3F5" });
    if (i < 3) s.addText("▼", { x: 5.3, y: y + 1.0, w: 0.5, h: 0.28, fontFace: FS, fontSize: 14, color: TEAL, align: "center" });
    y += 1.28;
  });
  s.addShape("roundRect", { x: 10.5, y: 1.75, w: 2.2, h: 4.85, rectRadius: 0.12, fill: { color: WHITE }, line: { color: "D9E2E8", width: 1 } });
  s.addText("Same task,\nfour tiers.\n\nAsk: where\nshould this\nrun — and\nwhy?", { x: 10.65, y: 2.0, w: 1.95, h: 4.3, fontFace: FH, fontSize: 16, bold: true, color: TEAL_D, align: "left", valign: "top", lineSpacingMultiple: 1.1 });
  footer(s, deck, false);
  if (sl.note) s.addNotes(sl.note);
}

function sWorkshop(pptx, deck, sl) {
  const s = pptx.addSlide(); bg(s, INK);
  s.addShape("roundRect", { x: 0.6, y: 0.5, w: 3.3, h: 0.7, rectRadius: 0.1, fill: { color: LIME }, line: { type: "none" } });
  s.addText("WORKSHOP", { x: 0.6, y: 0.5, w: 3.3, h: 0.7, align: "center", valign: "middle", fontFace: FH, fontSize: 20, bold: true, color: INK });
  s.addText(sl.h, { x: 0.6, y: 1.35, w: 12, h: 0.8, fontFace: FH, fontSize: 26, bold: true, color: WHITE });
  const arr = sl.steps.map((t) => ({ text: t, options: { bullet: { code: "2022", indent: 14 }, color: "EAF3F5", breakLine: true, paraSpaceAfter: 9 } }));
  s.addText(arr, { x: 0.7, y: 2.35, w: 7.6, h: 3.4, fontFace: FS, fontSize: 15, valign: "top" });
  // deliverable + code card
  s.addShape("roundRect", { x: 8.6, y: 2.35, w: 4.1, h: 3.9, rectRadius: 0.12, fill: { color: INK2 }, line: { color: TEAL, width: 1.5 } });
  s.addText("DELIVERABLE", { x: 8.85, y: 2.55, w: 3.6, h: 0.4, fontFace: FH, fontSize: 14, bold: true, color: LIME });
  s.addText(sl.deliver, { x: 8.85, y: 2.95, w: 3.6, h: 1.9, fontFace: FS, fontSize: 13.5, color: WHITE, valign: "top" });
  s.addText("CODE", { x: 8.85, y: 5.0, w: 3.6, h: 0.35, fontFace: FH, fontSize: 14, bold: true, color: LIME });
  s.addText(sl.code, { x: 8.85, y: 5.35, w: 3.6, h: 0.8, fontFace: "Courier New", fontSize: 12.5, color: "CADCFC", valign: "top" });
  footer(s, deck, true);
  if (sl.note) s.addNotes(sl.note);
}

function sTakeaways(pptx, deck, sl) {
  const s = pptx.addSlide(); bg(s, PAPER);
  titleBand(s, "Key takeaways");
  const pts = sl.points;
  let y = 1.8;
  const h = Math.min(1.0, (4.9 - (pts.length - 1) * 0.22) / pts.length);
  pts.forEach((t, i) => {
    s.addShape("roundRect", { x: 0.6, y, w: 12.1, h, rectRadius: 0.1, fill: { color: WHITE }, line: { color: "D9E2E8", width: 1 }, shadow: shadow() });
    s.addShape("rect", { x: 0.6, y: y + 0.12, w: 0.09, h: h - 0.24, fill: { color: LIME }, line: { type: "none" } });
    s.addText(t, { x: 0.95, y, w: 11.5, h, valign: "middle", fontFace: FS, fontSize: 15, color: TEXT, align: "left" });
    y += h + 0.22;
  });
  footer(s, deck, false);
  s.addNotes("Recap the load-bearing ideas before moving on.");
}

function sResources(pptx, deck, sl) {
  const s = pptx.addSlide(); bg(s, INK);
  s.addText("Watch, demos & further reading", { x: 0.6, y: 0.45, w: 12, h: 0.8, fontFace: FH, fontSize: 28, bold: true, color: WHITE });
  // media (video / demo) chips at top
  let y = 1.45;
  if (deck.media && deck.media.length) {
    s.addText("LATEST VIDEOS & LIVE DEMOS", { x: 0.6, y, w: 12, h: 0.3, fontFace: FH, fontSize: 12, bold: true, color: LIME });
    y += 0.4;
    deck.media.forEach((m) => {
      s.addShape("roundRect", { x: 0.6, y, w: 12.1, h: 0.62, rectRadius: 0.1, fill: { color: "16394F" }, line: { color: LIME, width: 1 } });
      s.addShape("ellipse", { x: 0.8, y: y + 0.14, w: 0.34, h: 0.34, fill: { color: LIME }, line: { type: "none" } });
      s.addText("▶", { x: 0.8, y: y + 0.14, w: 0.34, h: 0.34, align: "center", valign: "middle", fontFace: FS, fontSize: 12, color: INK, bold: true });
      s.addText([{ text: m.label + "   ", options: { bold: true, color: WHITE, fontSize: 13, hyperlink: { url: "https://" + m.url.replace(/^https?:\/\//, "") } } },
                 { text: m.url, options: { color: "8FD3DB", fontSize: 10.5, fontFace: "Courier New", hyperlink: { url: "https://" + m.url.replace(/^https?:\/\//, "") } } }],
        { x: 1.3, y, w: 11.2, h: 0.62, valign: "middle", fontFace: FS, align: "left" });
      y += 0.74;
    });
    y += 0.15;
  }
  s.addText("READING & DOCS", { x: 0.6, y, w: 12, h: 0.3, fontFace: FH, fontSize: 12, bold: true, color: "9FB3C8" });
  y += 0.4;
  const it = sl.items;
  const avail = 6.95 - y;
  const h = Math.min(0.72, (avail - (it.length - 1) * 0.14) / it.length);
  it.forEach((o) => {
    s.addShape("roundRect", { x: 0.6, y, w: 12.1, h, rectRadius: 0.1, fill: { color: INK2 }, line: { type: "none" } });
    s.addText([{ text: o.n + "   ", options: { bold: true, color: WHITE, fontSize: 12.5, hyperlink: { url: "https://" + o.u.replace(/^https?:\/\//, "") } } }, { text: o.u, options: { color: TEAL, fontSize: 10.5, fontFace: "Courier New", hyperlink: { url: "https://" + o.u.replace(/^https?:\/\//, "") } } }],
      { x: 0.9, y, w: 11.5, h, valign: "middle", fontFace: FS, align: "left" });
    y += h + 0.14;
  });
  footer(s, deck, true);
  s.addNotes("Video/demo links are clickable in slideshow mode. Full media list in MEDIA.md.");
}

function sFigure(pptx, deck, sl) {
  const s = pptx.addSlide(); bg(s, PAPER);
  titleBand(s, sl.h);
  s.addShape("roundRect", { x: 0.9, y: 1.65, w: 11.5, h: 4.55, rectRadius: 0.12, fill: { color: WHITE }, line: { color: "D9E2E8", width: 1 }, shadow: shadow() });
  s.addImage({ path: sl.img, x: 1.2, y: 1.9, w: 10.9, h: 3.7, sizing: { type: "contain", w: 10.9, h: 3.7 } });
  if (sl.cap) s.addText(sl.cap, { x: 0.9, y: 6.3, w: 11.5, h: 0.5, fontFace: FS, fontSize: 12.5, italic: true, color: MUTE, align: "center" });
  footer(s, deck, false);
  if (sl.note) s.addNotes(sl.note);
}

function render(pptx, deck) {
  sTitle(pptx, deck);
  sOutcomes(pptx, deck);
  sAgenda(pptx, deck);
  deck.slides.forEach((sl) => {
    ({ content: sContent, two: sTwo, process: sProcess, stats: sStats, tier: sTier, figure: sFigure }[sl.t])(pptx, deck, sl);
  });
  sWorkshop(pptx, deck, deck.workshop);
  sTakeaways(pptx, deck, { points: deck.takeaways });
  sResources(pptx, deck, { items: deck.resources });
}

// ===== CONTENT ==========================================================
const LECTURES = require("./content.js");

(async () => {
  for (const deck of LECTURES) {
    deck.numPad = String(deck.num).padStart(2, "0");
    const pptx = new pptxgen();
    pptx.layout = "LAYOUT_WIDE";
    pptx.author = "Applied Intelligent Vision Systems";
    pptx.title = `Lecture ${deck.num} — ${deck.title}`;
    render(pptx, deck);
    const fn = `Lecture_${deck.numPad}_${deck.slug}.pptx`;
    await pptx.writeFile({ fileName: fn });
    console.log("wrote", fn);
  }
})();
