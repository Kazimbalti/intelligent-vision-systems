/* Interactive layer for Tutorial 10 (Paper <-> Code handbook).
   Plain JavaScript, no dependencies. Every widget mounts into an element with
   data-widget="name"; quizzes mount into data-quiz="id". */
(function () {
  "use strict";

  /* ------------------------------------------------------------ helpers */
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function h(tag, attrs, kids) {
    var e = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === "html") e.innerHTML = attrs[k];
      else if (k === "text") e.textContent = attrs[k];
      else if (k.slice(0, 2) === "on") e.addEventListener(k.slice(2), attrs[k]);
      else e.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { if (c != null) e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return e;
  }
  function f(x, d) { if (!isFinite(x)) return x > 0 ? "∞" : "−∞"; var s = (+x).toFixed(d == null ? 3 : d); return s.replace("-", "−"); }
  function int(n) { return Math.round(n).toLocaleString("en-US").replace(/,/g, " "); }
  function store(k, v) { try { if (v === undefined) return JSON.parse(localStorage.getItem(k)); localStorage.setItem(k, JSON.stringify(v)); } catch (e) { return null; } }
  function heat(t) { // 0..1 -> white..teal
    t = Math.max(0, Math.min(1, t));
    var a = [240, 253, 250], b = [15, 118, 110];
    return "rgb(" + a.map(function (v, i) { return Math.round(v + (b[i] - v) * t); }).join(",") + ")";
  }
  function div(t) { // -1..1 -> blue..white..red
    t = Math.max(-1, Math.min(1, t));
    var w = [255, 255, 255], c = t < 0 ? [37, 99, 235] : [220, 38, 38], a = Math.abs(t);
    return [0, 1, 2].map(function (i) { return Math.round(w[i] + (c[i] - w[i]) * a); });
  }
  var seed = 7;
  function rnd() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }
  function randn() { var u = rnd() || 1e-9, v = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  function svgEl(tag, attrs) { var e = document.createElementNS("http://www.w3.org/2000/svg", tag); Object.keys(attrs || {}).forEach(function (k) { e.setAttribute(k, attrs[k]); }); return e; }
  function copyText(txt, btn) {
    function done() { var o = btn.textContent; btn.textContent = "Copied ✓"; setTimeout(function () { btn.textContent = o; }, 1400); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(done, fallback); else fallback();
    function fallback() { var t = h("textarea"); t.value = txt; document.body.appendChild(t); t.select(); try { document.execCommand("copy"); done(); } catch (e) {} t.remove(); }
  }
  function shell(mount, title, badge) {
    mount.classList.add("widget");
    mount.innerHTML = "";
    mount.appendChild(h("div", { class: "wt" }, [h("span", { text: "▶ " + title }), badge ? h("span", { class: "badge", text: badge }) : null]));
    var body = h("div", { class: "wb" }); mount.appendChild(body); return body;
  }

  /* ------------------------------------------------------------ 1. paper <-> code linking */
  function splitCodeLines() {
    $$("pre[data-map]").forEach(function (pre) {
      var code = $("code", pre); if (!code || code.dataset.split) return;
      var map = {};
      pre.getAttribute("data-map").trim().split(/\s+/).forEach(function (tok) {
        var p = tok.split(":"); var name = "lk-" + p[0];
        p[1].split(",").forEach(function (r) { var ab = r.split("-").map(Number); for (var i = ab[0]; i <= (ab[1] || ab[0]); i++) (map[i] = map[i] || []).push(name); });
      });
      var lines = code.innerHTML.replace(/\n$/, "").split("\n");
      code.innerHTML = lines.map(function (l, i) { return '<span class="ln ' + (map[i + 1] || []).join(" ") + '">' + (l || " ") + "</span>"; }).join("");
      code.dataset.split = "1";
    });
  }
  function lkOf(t) {
    while (t && t.nodeType === 1) {
      var cl = t.getAttribute("class") || "";
      var m = cl.match(/(?:^|\s)(lk-[\w-]+)/); if (m) return m[1];
      t = t.parentNode;
    }
    return null;
  }
  var lit = null;
  function setLit(k) {
    if (k === lit) return;
    $$(".lit").forEach(function (x) { x.classList.remove("lit"); });
    if (k) $$("." + k).forEach(function (x) { x.classList.add("lit"); });
    lit = k;
  }
  document.addEventListener("mouseover", function (e) { setLit(lkOf(e.target)); });
  document.addEventListener("focusin", function (e) { setLit(lkOf(e.target)); });
  document.addEventListener("click", function (e) {
    var k = lkOf(e.target); if (!k) return;
    var on = !(e.target.closest("." + k) || e.target).classList.contains("pin");
    $$(".pin").forEach(function (x) { x.classList.remove("pin"); });
    if (on) $$("." + k).forEach(function (x) { x.classList.add("pin"); });
    var box = e.target.closest(".lkbox[data-goto]");
    if (box) {
      var target = document.querySelector("pre ." + k) || document.getElementById(box.getAttribute("data-goto"));
      if (target) target.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });
  document.addEventListener("keydown", function (e) {
    if ((e.key === "Enter" || e.key === " ") && e.target.classList && e.target.classList.contains("lkbox")) { e.preventDefault(); e.target.dispatchEvent(new MouseEvent("click", { bubbles: true })); }
  });

  /* ------------------------------------------------------------ 2. redrawn paper figures (SVG) */
  // spec: {w, h, boxes:[{x,y,w,h,t,lk,fill,dash,goto,sub}], lines:[[x1,y1,x2,y2,dash?]], labels:[{x,y,t,size,anchor,color,weight}]}
  function drawFig(mount, spec) {
    var s = svgEl("svg", { viewBox: "0 0 " + spec.w + " " + spec.h, role: "img", "aria-label": mount.getAttribute("data-label") || "paper figure" });
    var defs = svgEl("defs"); var mk = svgEl("marker", { id: "ah" + (drawFig.n = (drawFig.n || 0) + 1), viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 9, markerHeight: 9, markerUnits: "userSpaceOnUse", orient: "auto-start-reverse" });
    mk.appendChild(svgEl("path", { d: "M0,0 L10,5 L0,10 z", fill: "#475569" })); defs.appendChild(mk); s.appendChild(defs);
    var mid = "url(#ah" + drawFig.n + ")";
    (spec.groups || []).forEach(function (g) {
      s.appendChild(svgEl("rect", { x: g.x, y: g.y, width: g.w, height: g.h, rx: 12, fill: g.fill || "#f1f5f9", stroke: "#94a3b8", "stroke-dasharray": "5 4" }));
      if (g.t) { var gt = svgEl("text", { x: g.tx != null ? g.tx : g.x + g.w + 8, y: g.ty != null ? g.ty : g.y + g.h / 2, "font-size": 15, "font-weight": 700, fill: "#334155" }); gt.textContent = g.t; s.appendChild(gt); }
    });
    (spec.lines || []).forEach(function (l) {
      var p = svgEl(l.length > 5 ? "path" : "line", l.length > 5 ? { d: l[5], fill: "none" } : { x1: l[0], y1: l[1], x2: l[2], y2: l[3] });
      p.setAttribute("stroke", "#475569"); p.setAttribute("stroke-width", 1.6); p.setAttribute("marker-end", mid);
      if (l[4]) p.setAttribute("stroke-dasharray", "4 3");
      s.appendChild(p);
    });
    (spec.boxes || []).forEach(function (b) {
      var g = svgEl("g", { class: b.lk ? "lkbox lk-" + b.lk : "" });
      if (b.lk) { g.setAttribute("tabindex", "0"); g.setAttribute("role", "button"); g.setAttribute("aria-label", b.t + ": highlight the code"); }
      if (b.goto) g.setAttribute("data-goto", b.goto);
      g.appendChild(svgEl("rect", { x: b.x, y: b.y, width: b.w, height: b.h, rx: 7, fill: b.fill || "#e0f2fe", stroke: "#334155", "stroke-width": 1.4, "stroke-dasharray": b.dash ? "5 3" : "none" }));
      var t = svgEl("text", { x: b.x + b.w / 2, y: b.y + b.h / 2 + (b.sub ? -2 : 5), "text-anchor": "middle", "font-size": b.size || 14, "font-weight": 600, fill: "#0f172a" }); t.textContent = b.t; g.appendChild(t);
      if (b.sub) { var st = svgEl("text", { x: b.x + b.w / 2, y: b.y + b.h / 2 + 13, "text-anchor": "middle", "font-size": 11, fill: "#475569" }); st.textContent = b.sub; g.appendChild(st); }
      s.appendChild(g);
    });
    (spec.labels || []).forEach(function (l) {
      var t = svgEl("text", { x: l.x, y: l.y, "text-anchor": l.anchor || "middle", "font-size": l.size || 14, "font-weight": l.weight || 600, fill: l.color || "#0f172a" });
      if (l.italic) t.setAttribute("font-style", "italic");
      t.textContent = l.t; s.appendChild(t);
    });
    mount.innerHTML = ""; mount.appendChild(s);
  }
  var FIGS = {
    // Attention Is All You Need, Figure 2 (left): scaled dot-product attention, read bottom-up
    sdpa: { w: 300, h: 330, boxes: [
      { x: 45, y: 25, w: 150, h: 32, t: "MatMul", lk: "att-mix", fill: "#ede9fe" },
      { x: 45, y: 85, w: 130, h: 32, t: "SoftMax", lk: "att-soft", fill: "#dcfce7" },
      { x: 45, y: 140, w: 130, h: 32, t: "Mask (opt.)", lk: "att-mask", fill: "#fce7f3", dash: 1 },
      { x: 45, y: 195, w: 130, h: 32, t: "Scale", lk: "att-scale", fill: "#fef9c3" },
      { x: 45, y: 250, w: 130, h: 32, t: "MatMul", lk: "att-qk", fill: "#ede9fe" }],
      lines: [[80, 312, 85, 284], [140, 312, 135, 284], [110, 250, 110, 229], [110, 195, 110, 174], [110, 140, 110, 119], [110, 85, 110, 59], [245, 312, 0, 0, 0, "M245,312 L245,41 L197,41"]],
      labels: [{ x: 78, y: 326, t: "Q" }, { x: 142, y: 326, t: "K" }, { x: 245, y: 326, t: "V" }, { x: 120, y: 14, t: "Scaled Dot-Product Attention", size: 13, color: "#475569" }] },
    // Figure 2 (right): multi-head attention
    mha: { w: 320, h: 330, boxes: [
      { x: 95, y: 22, w: 130, h: 30, t: "Linear  (W^O)", lk: "mha-out", fill: "#e0f2fe" },
      { x: 95, y: 78, w: 130, h: 30, t: "Concat", lk: "mha-concat", fill: "#fef3c7" },
      { x: 60, y: 140, w: 200, h: 46, t: "Scaled Dot-Product", sub: "Attention  × h heads", lk: "mha-att", fill: "#ede9fe" },
      { x: 30, y: 236, w: 76, h: 30, t: "Linear", lk: "mha-proj", fill: "#e0f2fe", size: 13 },
      { x: 122, y: 236, w: 76, h: 30, t: "Linear", lk: "mha-proj", fill: "#e0f2fe", size: 13 },
      { x: 214, y: 236, w: 76, h: 30, t: "Linear", lk: "mha-proj", fill: "#e0f2fe", size: 13 }],
      lines: [[68, 300, 68, 268], [160, 300, 160, 268], [252, 300, 252, 268], [68, 236, 110, 188], [160, 236, 160, 188], [252, 236, 210, 188], [160, 140, 160, 110], [160, 78, 160, 54], [160, 22, 160, 4]],
      groups: [{ x: 52, y: 132, w: 216, h: 62, fill: "#faf5ff", t: "h", tx: 274, ty: 168 }],
      labels: [{ x: 68, y: 318, t: "V" }, { x: 160, y: 318, t: "K" }, { x: 252, y: 318, t: "Q" }] },
    // Figure 1: the Transformer
    transformer: { w: 600, h: 560, groups: [{ x: 40, y: 242, w: 210, h: 166, t: "N×", tx: 8, ty: 330 }, { x: 330, y: 186, w: 210, h: 222, t: "×N", tx: 548, ty: 300 }],
      boxes: [
        { x: 60, y: 366, w: 170, h: 30, t: "Multi-Head Attention", lk: "tr-self", fill: "#ede9fe", goto: "tr-layers", size: 13 },
        { x: 60, y: 332, w: 170, h: 26, t: "Add & Norm", lk: "tr-addnorm", fill: "#fef9c3", goto: "tr-ln", size: 13 },
        { x: 60, y: 290, w: 170, h: 30, t: "Feed Forward", lk: "tr-ffn", fill: "#dbeafe", goto: "tr-ln", size: 13 },
        { x: 60, y: 254, w: 170, h: 26, t: "Add & Norm", lk: "tr-addnorm", fill: "#fef9c3", goto: "tr-ln", size: 13 },
        { x: 60, y: 452, w: 170, h: 30, t: "Input Embedding", lk: "tr-emb", fill: "#fde68a", goto: "tr-pe", size: 13 },
        { x: 350, y: 372, w: 170, h: 28, t: "Masked Multi-Head Attn", lk: "tr-masked", fill: "#ede9fe", goto: "tr-layers", size: 12.5 },
        { x: 350, y: 340, w: 170, h: 24, t: "Add & Norm", lk: "tr-addnorm", fill: "#fef9c3", goto: "tr-ln", size: 13 },
        { x: 350, y: 300, w: 170, h: 30, t: "Multi-Head Attention", lk: "tr-cross", fill: "#f5d0fe", goto: "tr-layers", size: 13 },
        { x: 350, y: 268, w: 170, h: 24, t: "Add & Norm", lk: "tr-addnorm", fill: "#fef9c3", goto: "tr-ln", size: 13 },
        { x: 350, y: 228, w: 170, h: 30, t: "Feed Forward", lk: "tr-ffn", fill: "#dbeafe", goto: "tr-ln", size: 13 },
        { x: 350, y: 196, w: 170, h: 24, t: "Add & Norm", lk: "tr-addnorm", fill: "#fef9c3", goto: "tr-ln", size: 13 },
        { x: 350, y: 452, w: 170, h: 30, t: "Output Embedding", lk: "tr-emb", fill: "#fde68a", goto: "tr-pe", size: 13 },
        { x: 350, y: 140, w: 170, h: 28, t: "Linear", lk: "tr-out", fill: "#e0f2fe", goto: "tr-layers", size: 13 },
        { x: 350, y: 92, w: 170, h: 28, t: "Softmax", lk: "tr-soft", fill: "#dcfce7", goto: "tr-layers", size: 13 }],
      lines: [[145, 540, 145, 484], [145, 452, 145, 426], [145, 412, 145, 398], [145, 366, 145, 360], [145, 332, 145, 322], [145, 290, 145, 282], [0, 0, 0, 0, 0, "M145,254 L145,222 L285,222 L285,315 L348,315"],
        [435, 540, 435, 484], [435, 452, 435, 426], [435, 412, 435, 402], [435, 372, 435, 366], [435, 340, 435, 332], [435, 300, 435, 294], [435, 268, 435, 260], [435, 228, 435, 222], [435, 196, 435, 170], [435, 140, 435, 122], [435, 92, 435, 70]],
      labels: [{ x: 145, y: 420, t: "⊕ Positional Encoding", size: 12, color: "#9a3412" }, { x: 435, y: 420, t: "⊕ Positional Encoding", size: 12, color: "#9a3412" },
        { x: 145, y: 555, t: "Inputs", size: 13 }, { x: 435, y: 555, t: "Outputs (shifted right)", size: 13 }, { x: 435, y: 60, t: "Output Probabilities", size: 13 },
        { x: 215, y: 214, t: "encoder output → K, V", size: 11.5, color: "#7e22ce" }, { x: 145, y: 30, t: "ENCODER", size: 13, color: "#64748b", weight: 700 }, { x: 435, y: 30, t: "DECODER", size: 13, color: "#64748b", weight: 700 }] },
    // ViT Figure 1, drawn left to right
    vit: { w: 980, h: 170, groups: [{ x: 560, y: 22, w: 250, h: 126, fill: "#f8fafc", t: "× L", tx: 772, ty: 40 }],
      boxes: [
        { x: 10, y: 60, w: 96, h: 48, t: "Image", sub: "224 × 224 × 3", fill: "#f1f5f9" },
        { x: 132, y: 60, w: 104, h: 48, t: "Patches", sub: "196 × (16·16·3)", lk: "vit-patch", fill: "#fde68a", goto: "vit-pairs" },
        { x: 262, y: 60, w: 118, h: 48, t: "Linear proj. E", sub: "768 → D", lk: "vit-proj", fill: "#e0f2fe", goto: "vit-pairs" },
        { x: 406, y: 34, w: 128, h: 36, t: "+ [class] token", lk: "vit-cls", fill: "#ede9fe", size: 13 },
        { x: 406, y: 98, w: 128, h: 36, t: "+ E_pos", lk: "vit-pos", fill: "#fce7f3", size: 13 },
        { x: 574, y: 66, w: 50, h: 36, t: "LN", lk: "vit-ln", fill: "#fef9c3", size: 13 },
        { x: 634, y: 66, w: 64, h: 36, t: "MSA", lk: "vit-msa", fill: "#ede9fe", size: 13 },
        { x: 708, y: 66, w: 90, h: 36, t: "LN → MLP", lk: "vit-mlp", fill: "#dbeafe", size: 13 },
        { x: 836, y: 60, w: 130, h: 48, t: "LN → MLP Head", sub: "token 0 → 1000 classes", lk: "vit-head", fill: "#dcfce7", size: 13 }],
      lines: [[106, 84, 130, 84], [236, 84, 260, 84], [380, 84, 404, 54], [380, 84, 404, 116], [534, 54, 572, 80], [534, 116, 572, 88], [624, 84, 632, 84], [698, 84, 706, 84], [810, 84, 834, 84]],
      labels: [{ x: 685, y: 136, t: "+ residual after MSA and after MLP", size: 11.5, color: "#475569" }] },
    // ResNet Figure 2: a residual building block
    resblock: { w: 300, h: 300, boxes: [
      { x: 70, y: 215, w: 130, h: 32, t: "weight layer", lk: "rn-f", fill: "#e0f2fe" },
      { x: 70, y: 140, w: 130, h: 32, t: "weight layer", lk: "rn-f", fill: "#e0f2fe" },
      { x: 113, y: 85, w: 44, h: 30, t: "⊕", lk: "rn-add", fill: "#dcfce7", size: 20 }],
      lines: [[135, 290, 135, 249], [135, 215, 135, 174], [135, 140, 135, 117], [135, 85, 135, 30], [0, 0, 0, 0, 0, "M135,270 C270,270 270,100 159,100"]],
      labels: [{ x: 135, y: 297, t: "x", italic: 1 }, { x: 160, y: 198, t: "relu", size: 12, color: "#475569", anchor: "start" }, { x: 160, y: 60, t: "relu", size: 12, color: "#475569", anchor: "start" },
        { x: 30, y: 160, t: "F(x)", italic: 1, color: "#0369a1" }, { x: 255, y: 190, t: "x", italic: 1, color: "#b45309" }, { x: 252, y: 206, t: "identity", size: 11, color: "#b45309" }, { x: 135, y: 22, t: "F(x) + x", italic: 1 }] }
  };
  function mountFigs() {
    $$("[data-fig]").forEach(function (m) {
      var spec = FIGS[m.getAttribute("data-fig")]; if (!spec) return;
      drawFig(m, spec);
      if (m.getAttribute("data-fig") === "resblock") { // the identity arc is itself linkable
        var p = $$("path", m).filter(function (x) { return !x.closest("marker"); })[0]; if (p) { p.setAttribute("class", "lk-rn-id"); p.style.cursor = "pointer"; p.setAttribute("stroke-width", "3"); p.setAttribute("stroke", "#b45309"); }
      }
    });
  }

  /* ------------------------------------------------------------ 3. attention playground */
  function attention(Q, K, V, scale, mask) {
    var dk = Q[0].length, s = scale ? Math.sqrt(dk) : 1;
    var S = Q.map(function (q) { return K.map(function (k) { return q.reduce(function (a, qi, i) { return a + qi * k[i]; }, 0); }); });
    var Z = S.map(function (r, i) { return r.map(function (v, j) { return mask && j > i ? -Infinity : v / s; }); });
    var E = Z.map(function (r) { var m = Math.max.apply(null, r); return r.map(function (v) { return Math.exp(v - m); }); });
    var W = E.map(function (r) { var t = r.reduce(function (a, b) { return a + b; }, 0); return r.map(function (v) { return v / t; }); });
    var O = W.map(function (w) { return V[0].map(function (_, c) { return w.reduce(function (a, wj, j) { return a + wj * V[j][c]; }, 0); }); });
    return { S: S, Z: Z, W: W, O: O, s: s };
  }
  function wAttn(m) {
    var body = shell(m, "Attention playground: change Q, K, V and watch every step", "live");
    var st = { Q: [[1, 0], [0, 1], [1, 1]], K: [[0, 1], [1, 0], [2, 0]], V: [[10, 0], [0, 10], [5, 5]], scale: true, mask: false, row: 0 };
    var presets = {
      "Paper example (Lab 7B)": function () { st.Q = [[1, 0], [0, 1], [1, 1]]; st.K = [[0, 1], [1, 0], [2, 0]]; st.V = [[10, 0], [0, 10], [5, 5]]; },
      "All keys equal": function () { st.K = [[1, 1], [1, 1], [1, 1]]; },
      "Sharpen: Q × 5": function () { st.Q = st.Q.map(function (r) { return r.map(function (v) { return Math.round(v * 5 * 100) / 100; }); }); },
      "Random": function () { function R() { return Math.round((rnd() * 4 - 2) * 10) / 10; } st.Q = [[R(), R()], [R(), R()], [R(), R()]]; st.K = [[R(), R()], [R(), R()], [R(), R()]]; }
    };
    var bar = h("div", { class: "ctrl" });
    Object.keys(presets).forEach(function (k) { bar.appendChild(h("button", { class: "wbtn alt", text: k, onclick: function () { presets[k](); render(); } })); });
    var cS = h("input", { type: "checkbox", checked: "" }), cM = h("input", { type: "checkbox" });
    cS.addEventListener("change", function () { st.scale = cS.checked; render(); });
    cM.addEventListener("change", function () { st.mask = cM.checked; render(); });
    bar.appendChild(h("label", null, [cS, "divide by √dₖ"])); bar.appendChild(h("label", null, [cM, "causal mask"]));
    body.appendChild(bar);
    var mats = h("div", { class: "mats" }); body.appendChild(mats);
    var out = h("div", { class: "mats", style: "margin-top:10px" }); body.appendChild(out);
    var steps = h("div", { class: "steps" }); body.appendChild(steps);
    body.appendChild(h("div", { class: "ask", html: "<b>Try:</b> (1) set k₂ = (0, 0): where does word 0's attention go now? (2) Press <i>Sharpen</i> three times with √dₖ off: the weights become one-hot, which is the saturation in Derivation C. (3) Turn on the mask: why is row 0 always (1, 0, 0)?" }));
    function inputMat(name, M) {
      var t = h("table", { class: "mat" }); t.appendChild(h("caption", { text: name + "  (editable)" }));
      M.forEach(function (r, i) {
        var tr = h("tr", null, [h("th", { text: "w" + i })]);
        r.forEach(function (v, j) {
          var inp = h("input", { type: "number", step: "0.5", value: v, "aria-label": name + " row " + i + " col " + j });
          inp.addEventListener("input", function () { var x = parseFloat(inp.value); if (!isNaN(x)) { M[i][j] = x; renderOut(); } });
          tr.appendChild(h("td", null, [inp]));
        });
        t.appendChild(tr);
      });
      return t;
    }
    function numMat(name, M, opt) {
      opt = opt || {};
      var t = h("table", { class: "mat" + (opt.pick ? " pick" : "") }); t.appendChild(h("caption", { text: name }));
      if (opt.cols) t.appendChild(h("tr", null, [h("th")].concat(opt.cols.map(function (c) { return h("th", { text: c }); }))));
      M.forEach(function (r, i) {
        var tr = h("tr", { class: opt.pick && i === st.row ? "sel" : "" }, [h("th", { text: "w" + i })]);
        r.forEach(function (v) {
          var td = h("td", { text: f(v, opt.d == null ? 2 : opt.d) });
          if (opt.heat) { td.style.background = heat(v); if (v > .55) td.className = "hm"; }
          tr.appendChild(td);
        });
        if (opt.pick) tr.addEventListener("click", function () { st.row = i; renderOut(); });
        t.appendChild(tr);
      });
      return t;
    }
    function render() {
      mats.innerHTML = "";
      mats.appendChild(inputMat("Q", st.Q)); mats.appendChild(inputMat("K", st.K)); mats.appendChild(inputMat("V", st.V));
      renderOut();
    }
    function renderOut() {
      var r = attention(st.Q, st.K, st.V, st.scale, st.mask);
      out.innerHTML = "";
      out.appendChild(numMat("① Q Kᵀ  (scores)", r.S, { cols: ["k0", "k1", "k2"] }));
      out.appendChild(h("span", { class: "arrow", text: st.scale ? "÷ " + f(r.s) + " →" : "→" }));
      out.appendChild(numMat("② scaled" + (st.mask ? " + mask" : ""), r.Z, { cols: ["k0", "k1", "k2"] }));
      out.appendChild(h("span", { class: "arrow", text: "softmax →" }));
      out.appendChild(numMat("③ weights (click a row)", r.W, { heat: 1, pick: 1, cols: ["k0", "k1", "k2"] }));
      out.appendChild(h("span", { class: "arrow", text: "· V →" }));
      out.appendChild(numMat("④ output", r.O, { cols: ["d0", "d1"] }));
      var i = st.row, q = st.Q[i], z = r.Z[i];
      var ex = z.map(function (v) { return isFinite(v) ? Math.exp(v) : 0; }), tot = ex.reduce(function (a, b) { return a + b; }, 0);
      var big = Math.max.apply(null, r.W[i]), arg = r.W[i].indexOf(big);
      steps.innerHTML = "<b>Derivation for word " + i + "</b> (q<sub>" + i + "</sub> = (" + q.map(function (v) { return f(v, 2); }).join(", ") + "))<ol>" +
        "<li>Scores q·k<sub>j</sub>: " + st.K.map(function (k, j) { return "(" + q.map(function (v, c) { return f(v, 1) + "·" + f(k[c], 1); }).join(" + ") + ") = <b>" + f(r.S[i][j], 2) + "</b>"; }).join(";  ") + "</li>" +
        (st.scale ? "<li>Scale ÷ √" + q.length + " = " + f(r.s) + ": (" + r.S[i].map(function (v) { return f(v / r.s); }).join(", ") + ")</li>" : "<li>No scaling (√dₖ is off).</li>") +
        (st.mask && i < 2 ? "<li>Mask: keys after position " + i + " → −∞</li>" : "") +
        "<li>Exponentiate: (" + ex.map(function (v) { return f(v); }).join(", ") + "), sum = " + f(tot) + "</li>" +
        "<li>Softmax = divide by the sum: <b>(" + r.W[i].map(function (v) { return f(v); }).join(", ") + ")</b></li>" +
        "<li>Mix values: " + r.W[i].map(function (w, j) { return f(w) + "·(" + st.V[j].map(function (v) { return f(v, 1); }).join(", ") + ")"; }).join(" + ") + "</li></ol>" +
        '<div class="res">output<sub>' + i + "</sub> = (" + r.O[i].map(function (v) { return f(v, 2); }).join(", ") + "): " + Math.round(big * 100) + " % of it comes from word " + arg + ".</div>";
    }
    render();
  }

  /* ------------------------------------------------------------ 4. why sqrt(d_k) */
  function wSqrt(m) {
    var body = shell(m, "Why ÷ √dₖ? Make dₖ bigger and watch the softmax saturate", "simulation");
    var rng = h("input", { type: "range", min: 0, max: 10, step: 1, value: 6, "aria-label": "log2 of d_k" });
    var lab = h("output"); var again = h("button", { class: "wbtn alt", text: "New random q, k" });
    body.appendChild(h("div", { class: "ctrl" }, [h("label", null, ["dₖ = ", lab, rng]), again]));
    var row = h("div", { class: "wrow" }); body.appendChild(row);
    var c1 = h("div", { class: "wcol" }), c2 = h("div", { class: "wcol" }); row.appendChild(c1); row.appendChild(c2);
    var stats = h("div", { class: "steps" }); body.appendChild(stats);
    body.appendChild(h("div", { class: "ask", html: "<b>Read it like this:</b> one query against 8 random keys. Left: raw scores → softmax puts almost all weight on one key, and the gradient s(1 − s) collapses. Right: the same scores ÷ √dₖ keep a soft spread at every dₖ." }));
    function bars(ws, warm) {
      var b = h("div", { class: "bars" + (warm ? " warm" : "") });
      ws.forEach(function (w) { b.appendChild(h("div", { style: "height:" + Math.max(1, w * 100) + "%" }, [h("span", { text: w >= .005 ? w.toFixed(2) : "0" })])); });
      return b;
    }
    function soft(z) { var mx = Math.max.apply(null, z), e = z.map(function (v) { return Math.exp(v - mx); }), t = e.reduce(function (a, b) { return a + b; }, 0); return e.map(function (v) { return v / t; }); }
    function draw() {
      var d = Math.pow(2, +rng.value); lab.textContent = d;
      var q = [], K = [];
      for (var i = 0; i < d; i++) q.push(randn());
      for (var j = 0; j < 8; j++) { var k = []; for (i = 0; i < d; i++) k.push(randn()); K.push(k); }
      var z = K.map(function (k) { return k.reduce(function (a, v, i) { return a + v * q[i]; }, 0); });
      var w1 = soft(z), w2 = soft(z.map(function (v) { return v / Math.sqrt(d); }));
      var g = function (w) { return w.reduce(function (a, s) { return a + s * (1 - s); }, 0) / w.length; };
      // measured std over many pairs
      var n = 600, acc = 0, acc2 = 0;
      for (var t = 0; t < n; t++) { var dot = 0; for (i = 0; i < d; i++) dot += randn() * randn(); acc += dot * dot; acc2 += dot * dot / d; }
      c1.innerHTML = ""; c2.innerHTML = "";
      c1.appendChild(h("b", { text: "softmax(q·k)  without scaling" })); c1.appendChild(bars(w1, true)); c1.appendChild(h("div", { class: "cap", text: "max weight " + Math.max.apply(null, w1).toFixed(3) + " · mean gradient s(1−s) = " + g(w1).toFixed(4) }));
      c2.appendChild(h("b", { text: "softmax(q·k / √dₖ)  as in the paper" })); c2.appendChild(bars(w2)); c2.appendChild(h("div", { class: "cap", text: "max weight " + Math.max.apply(null, w2).toFixed(3) + " · mean gradient s(1−s) = " + g(w2).toFixed(4) }));
      stats.innerHTML = "Measured over " + n + " random pairs: std(q·k) = <b>" + Math.sqrt(acc / n).toFixed(2) + "</b> (theory √" + d + " = " + Math.sqrt(d).toFixed(2) + ") → after ÷ √dₖ: <b>" + Math.sqrt(acc2 / n).toFixed(2) + "</b> (theory 1). That is Derivation C, measured.";
    }
    rng.addEventListener("input", draw); again.addEventListener("click", draw); draw();
  }

  /* ------------------------------------------------------------ 5. head split: view + transpose vs the silent bug */
  function wHeads(m) {
    var body = shell(m, "Split into heads: view(B, L, h, dₖ).transpose(1, 2) vs the silent bug", "visual");
    var L = 4, D = 8, st = { h: 2, bug: false };
    var cols = ["#2563eb", "#16a34a", "#d97706", "#9333ea"];
    var sel = h("select", { "aria-label": "number of heads" }, [2, 4, 1].map(function (v) { return h("option", { value: v, text: v }); }));
    var r1 = h("input", { type: "radio", name: "hb" + Math.random(), checked: "" }), r2 = h("input", { type: "radio", name: r1.name });
    body.appendChild(h("div", { class: "ctrl" }, [h("label", null, ["heads h = ", sel]), h("label", null, [r1, "correct: view(L, h, dₖ) + transpose"]), h("label", null, [r2, "bug: view(h, L, dₖ)"])]));
    var area = h("div"); body.appendChild(area);
    var msg = h("div", { class: "steps" }); body.appendChild(msg);
    sel.addEventListener("change", function () { st.h = +sel.value; draw(); });
    r1.addEventListener("change", function () { st.bug = false; draw(); }); r2.addEventListener("change", function () { st.bug = true; draw(); });
    function cell(t, fe) { return h("div", { style: "background:" + cols[t], text: "t" + t + "·" + fe, title: "token " + t + ", feature " + fe }); }
    function draw() {
      var dk = D / st.h; area.innerHTML = "";
      var inp = h("div", { class: "hblock" }, [h("b", { text: "x: (L = 4 tokens, D = 8 features)" })]);
      var g = h("div", { class: "hgrid", style: "grid-template-columns:repeat(" + D + ",34px)" });
      for (var l = 0; l < L; l++) for (var fe = 0; fe < D; fe++) g.appendChild(cell(l, fe));
      inp.appendChild(g); area.appendChild(inp); area.appendChild(h("br"));
      var bad = 0;
      for (var hh = 0; hh < st.h; hh++) {
        var blk = h("div", { class: "hblock" }, [h("b", { text: "head " + hh + ": (L, dₖ = " + dk + ")" })]);
        var gg = h("div", { class: "hgrid", style: "grid-template-columns:repeat(" + dk + ",34px)" });
        for (var r = 0; r < L; r++) {
          var rowTok = {};
          for (var c = 0; c < dk; c++) {
            var tok, feat;
            if (!st.bug) { tok = r; feat = hh * dk + c; }
            else { var flat = hh * L * dk + r * dk + c; tok = Math.floor(flat / D); feat = flat % D; }
            rowTok[tok] = 1; gg.appendChild(cell(tok, feat));
          }
          if (Object.keys(rowTok).length > 1 || +Object.keys(rowTok)[0] !== r) bad++;
        }
        blk.appendChild(gg); area.appendChild(blk);
      }
      msg.innerHTML = st.bug
        ? "<b style='color:#b91c1c'>Bug:</b> " + bad + " of " + (L * st.h) + " rows in the heads hold the <b>wrong token</b> (or a mix of two). The shape (B, " + st.h + ", 4, " + dk + ") is still correct, so no error is raised, the loss still goes down a little, and the model is quietly broken." + (st.h === 1 ? " With h = 1 the two give the same result, which is why tests with one head miss this bug." : "")
        : "<b style='color:#15803d'>Correct:</b> row r of every head is token r; head i holds features " + "i·dₖ … (i+1)·dₖ − 1. Every head sees all tokens, but only its own slice of features.";
    }
    draw();
  }

  /* ------------------------------------------------------------ 6. positional encoding explorer */
  function pe(pos, d) { var v = []; for (var i = 0; i < d; i += 2) { var w = 1 / Math.pow(10000, i / d); v.push(Math.sin(pos * w)); if (i + 1 < d) v.push(Math.cos(pos * w)); } return v; }
  function wPE(m) {
    var body = shell(m, "Positional encoding explorer", "live");
    var dS = h("input", { type: "range", min: 16, max: 256, step: 16, value: 64, "aria-label": "d_model" }), dO = h("output");
    var pS = h("input", { type: "range", min: 0, max: 99, step: 1, value: 10, "aria-label": "position" }), pO = h("output");
    body.appendChild(h("div", { class: "ctrl" }, [h("label", null, ["d_model = ", dO, dS]), h("label", null, ["position = ", pO, pS])]));
    var row = h("div", { class: "wrow" }); body.appendChild(row);
    var c1 = h("div", { class: "wcol" }), c2 = h("div", { class: "wcol" }); row.appendChild(c1); row.appendChild(c2);
    var cv = h("canvas", { class: "cv", width: 512, height: 300, "aria-label": "positional encoding heat map" });
    c1.appendChild(h("b", { text: "PE matrix: 100 positions (rows) × d_model dims (columns)" })); c1.appendChild(cv);
    c1.appendChild(h("div", { class: "cap", html: "<span style='color:#2563eb'>■</span> −1 · white 0 · <span style='color:#dc2626'>■</span> +1. Click a row to pick a position. Left columns oscillate fast, right columns slowly (Derivation E)." }));
    var sim = h("div"); c2.appendChild(h("b", { text: "PE(pos) · PE(other) for all 100 positions" })); c2.appendChild(sim);
    var vec = h("div", { class: "steps" }); c2.appendChild(vec);
    cv.addEventListener("click", function (e) { var r = cv.getBoundingClientRect(); pS.value = Math.min(99, Math.floor((e.clientY - r.top) / r.height * 100)); draw(); });
    function draw() {
      var d = +dS.value, p = +pS.value; dO.textContent = d; pO.textContent = p;
      var ctx = cv.getContext("2d"), img = ctx.createImageData(d, 100);
      var all = []; for (var r = 0; r < 100; r++) all.push(pe(r, d));
      for (r = 0; r < 100; r++) for (var c = 0; c < d; c++) { var col = div(all[r][c]), k = (r * d + c) * 4; img.data[k] = col[0]; img.data[k + 1] = col[1]; img.data[k + 2] = col[2]; img.data[k + 3] = 255; }
      var tmp = h("canvas", { width: d, height: 100 }); tmp.getContext("2d").putImageData(img, 0, 0);
      ctx.imageSmoothingEnabled = false; ctx.clearRect(0, 0, 512, 300); ctx.drawImage(tmp, 0, 0, 512, 300);
      ctx.strokeStyle = "#111"; ctx.lineWidth = 2; ctx.strokeRect(0, p * 3, 512, 3);
      var dots = all.map(function (v) { return v.reduce(function (a, x, i) { return a + x * all[p][i]; }, 0); });
      var W = 420, H = 170, mx = d / 2, pts = dots.map(function (v, i) { return (i / 99 * (W - 30) + 25).toFixed(1) + "," + (H - 20 - (v + mx * 0.2) / (mx * 1.2) * (H - 30)).toFixed(1); }).join(" ");
      var y0 = (H - 20 - 0.2 / 1.2 * (H - 30)).toFixed(1);
      sim.innerHTML = '<svg viewBox="0 0 ' + W + " " + H + '" style="width:100%;height:auto"><line x1="25" y1="' + y0 + '" x2="' + W + '" y2="' + y0 + '" stroke="#94a3b8"/><polyline fill="none" stroke="#0f766e" stroke-width="2" points="' + pts + '"/><line x1="' + (p / 99 * (W - 30) + 25) + '" y1="5" x2="' + (p / 99 * (W - 30) + 25) + '" y2="' + (H - 20) + '" stroke="#d9480f" stroke-dasharray="4 3"/><text x="25" y="' + (H - 4) + '" font-size="11" fill="#475569">pos 0</text><text x="' + (W - 5) + '" y="' + (H - 4) + '" font-size="11" fill="#475569" text-anchor="end">pos 99</text><text x="' + (W - 5) + '" y="14" font-size="11" fill="#475569" text-anchor="end">peak = d/2 = ' + mx + "</text></svg>";
      vec.innerHTML = "PE(" + p + ")[:8] = (" + all[p].slice(0, 8).map(function (v) { return f(v); }).join(", ") + ", …)<br>The curve peaks at pos = " + p + " and falls off the same way to both sides: the dot product depends only on the <b>distance</b>, which is Derivation F in action.";
    }
    dS.addEventListener("input", draw); pS.addEventListener("input", draw); draw();
  }

  /* ------------------------------------------------------------ 7. LayerNorm calculator */
  function wLN(m) {
    var body = shell(m, "LayerNorm calculator: type any token vector", "live");
    var xs = [1, 2, 3, 6].map(function (v, i) { return h("input", { type: "number", step: "0.5", value: v, "aria-label": "x" + i }); });
    var g = h("input", { type: "number", step: "0.5", value: 1, "aria-label": "gamma" }), b = h("input", { type: "number", step: "0.5", value: 0, "aria-label": "beta" });
    body.appendChild(h("div", { class: "ctrl" }, ["x = ("].concat(xs.reduce(function (a, x, i) { if (i) a.push(","); a.push(x); return a; }, [])).concat([")", h("label", null, ["γ", g]), h("label", null, ["β", b])])));
    var o = h("div", { class: "steps" }); body.appendChild(o);
    function draw() {
      var x = xs.map(function (e) { return parseFloat(e.value) || 0; }), n = x.length, G = parseFloat(g.value), B = parseFloat(b.value);
      if (isNaN(G)) G = 1; if (isNaN(B)) B = 0;
      var mu = x.reduce(function (a, v) { return a + v; }, 0) / n, va = x.reduce(function (a, v) { return a + (v - mu) * (v - mu); }, 0) / n, sd = Math.sqrt(va + 1e-5);
      var y = x.map(function (v) { return G * (v - mu) / sd + B; });
      o.innerHTML = "<ol><li>μ = (" + x.map(function (v) { return f(v, 2); }).join(" + ") + ") / 4 = <b>" + f(mu) + "</b></li>" +
        "<li>σ² = (" + x.map(function (v) { return "(" + f(v - mu, 2) + ")²"; }).join(" + ") + ") / 4 = <b>" + f(va) + "</b> (divide by N, not N − 1)</li>" +
        "<li>√(σ² + ε) = " + f(sd, 4) + (va < 1e-9 ? " ← ε saves us from dividing by 0" : "") + "</li>" +
        "<li>y = γ·(x − μ)/σ + β</li></ol><div class='res'>LN(x) = (" + y.map(function (v) { return f(v); }).join(", ") + ")</div>";
    }
    xs.concat([g, b]).forEach(function (e) { e.addEventListener("input", draw); }); draw();
  }

  /* ------------------------------------------------------------ 8. Transformer parameter calculator */
  function numInput(label, v, min, aria) { var i = h("input", { type: "number", value: v, min: min || 1, "aria-label": aria || label }); return { el: h("label", null, [label, i]), inp: i }; }
  function breakdown(rows, total, paper) {
    var t = h("table", { class: "calc" }), mx = Math.max.apply(null, rows.map(function (r) { return r[1]; }));
    rows.forEach(function (r) {
      t.appendChild(h("tr", null, [h("td", { html: r[0] }), h("td", { style: "width:34%" }, [h("div", { class: "barline" }, [h("i", { style: "width:" + (r[1] / mx * 100).toFixed(1) + "%" })])]), h("td", { class: "r", text: int(r[1]) }), h("td", { class: "r", text: (r[1] / total * 100).toFixed(1) + " %" })]));
    });
    t.appendChild(h("tr", { class: "tot" }, [h("td", { text: "Total" }), h("td", { html: paper ? "paper: " + paper : "" }), h("td", { class: "r", text: int(total) }), h("td", { class: "r", text: (total / 1e6).toFixed(1) + " M" })]));
    return t;
  }
  function wTrParams(m) {
    var body = shell(m, "Transformer parameter calculator (check Derivation H, then explore)", "calculator");
    var F = { d: numInput("d_model", 512), h: numInput("heads h", 8), ff: numInput("d_ff", 2048), ne: numInput("encoder N", 6, 0), nd: numInput("decoder N", 6, 0), v: numInput("vocab", 37000) };
    var sh = h("input", { type: "checkbox", checked: "" });
    var presets = { "Base (Table 3)": [512, 8, 2048, 6, 6, 37000, true, "65 M"], "Big (Table 3)": [1024, 16, 4096, 6, 6, 37000, true, "213 M"], "Lab 7C": [64, 4, 128, 2, 2, 13, false, ""] };
    var paper = "65 M";
    var pb = h("div", { class: "ctrl" });
    Object.keys(presets).forEach(function (k) { pb.appendChild(h("button", { class: "wbtn alt", text: k, onclick: function () { var p = presets[k]; ["d", "h", "ff", "ne", "nd", "v"].forEach(function (n, i) { F[n].inp.value = p[i]; }); sh.checked = p[6]; paper = p[7]; draw(); } })); });
    body.appendChild(pb);
    body.appendChild(h("div", { class: "ctrl" }, Object.keys(F).map(function (k) { return F[k].el; }).concat([h("label", null, [sh, "share embeddings (§3.4)"])])));
    var o = h("div"); body.appendChild(o); var note = h("div", { class: "ask" }); body.appendChild(note);
    function draw() {
      var d = +F.d.inp.value, hh = +F.h.inp.value, ff = +F.ff.inp.value, ne = +F.ne.inp.value, nd = +F.nd.inp.value, V = +F.v.inp.value;
      var mha = 4 * (d * d + d), ffn = d * ff + ff + ff * d + d, ln = 2 * d;
      var enc = ne * (mha + ffn + 2 * ln), dec = nd * (2 * mha + ffn + 3 * ln);
      var emb = sh.checked ? V * d : 2 * V * d + (V * d + V);
      var tot = enc + dec + emb;
      o.innerHTML = ""; o.appendChild(breakdown([["Encoder: " + ne + " × (MHA + FFN + 2 LN)", enc], ["Decoder: " + nd + " × (2 MHA + FFN + 3 LN)", dec], [sh.checked ? "Embedding (one shared V × d matrix)" : "Embeddings src + tgt + output Linear", emb]], tot, paper));
      note.innerHTML = (d % hh ? "<b style='color:#b91c1c'>d_model must be divisible by h</b> (dₖ = d/h). " : "dₖ = " + d + " / " + hh + " = <b>" + d / hh + "</b>. ") +
        "One MHA = 4(d² + d) = " + int(mha) + "; one FFN = " + int(ffn) + ". <b>Try:</b> change h. The total does not move: heads only split d, they add no weights.";
    }
    Object.keys(F).forEach(function (k) { F[k].inp.addEventListener("input", function () { paper = ""; draw(); }); });
    sh.addEventListener("change", function () { paper = ""; draw(); }); draw();
  }

  /* ------------------------------------------------------------ 9. U-Net size tracer + diagram */
  function unetTrace(n, valid, base) {
    var ch = [base, base * 2, base * 4, base * 8, base * 16], k = valid ? 4 : 0, s = n, ok = true, err = "", down = [];
    for (var i = 0; i < 5; i++) {
      var a = s - k; if (a <= 0) { ok = false; err = "the map shrinks to " + a + " at level " + (i + 1); break; }
      down.push({ in: s, out: a, c: ch[i] });
      if (i < 4) { if (a % 2) { ok = false; err = "level " + (i + 1) + " gives an odd size (" + a + ") before max-pool"; break; } s = a / 2; }
    }
    var up = [];
    if (ok) { s = down[4].out; for (i = 3; i >= 0; i--) { var u = s * 2, crop = (down[i].out - u) / 2; up.push({ up: u, skip: down[i].out, crop: crop, out: u - k, c: ch[i] }); s = u - k; if (s <= 0) { ok = false; err = "the up path shrinks to " + s; break; } } }
    var p = 0, cin = 1; ch.forEach(function (c) { p += 9 * cin * c + c + 9 * c * c + c; cin = c; });
    for (i = 4; i >= 1; i--) { p += 4 * ch[i] * ch[i - 1] + ch[i - 1]; p += 9 * ch[i] * ch[i - 1] + ch[i - 1] + 9 * ch[i - 1] * ch[i - 1] + ch[i - 1]; }
    p += base * 2 + 2;
    return { ok: ok, err: err, down: down, up: up, out: ok ? s : null, params: p };
  }
  function wUnet(m) {
    var body = shell(m, "U-Net size tracer: pick an input size, see every stage", "live");
    var nS = h("input", { type: "range", min: 124, max: 700, step: 1, value: 572, "aria-label": "input size" }), nN = h("input", { type: "number", value: 572, min: 32, max: 2000, "aria-label": "input size number" });
    var pad = h("select", { "aria-label": "padding" }, [h("option", { value: "valid", text: "unpadded (2015 paper)" }), h("option", { value: "same", text: "padding = 1 (modern)" })]);
    var base = h("select", { "aria-label": "base channels" }, [64, 32, 16].map(function (v) { return h("option", { value: v, text: v }); }));
    body.appendChild(h("div", { class: "ctrl" }, [h("label", null, ["input n = ", nN, nS]), h("label", null, ["convs: ", pad]), h("label", null, ["base channels: ", base]), h("button", { class: "wbtn alt", text: "next valid size ↑", onclick: function () { var v = +nN.value + 1, valid = pad.value === "valid"; for (var t = 0; t < 400; t++, v++) if (unetTrace(v, valid, 64).ok) break; nN.value = nS.value = v; draw(); } })]));
    var fig = h("div", { class: "figpanel" }); body.appendChild(fig);
    var o = h("div", { class: "steps" }); body.appendChild(o);
    body.appendChild(h("p", { class: "hint", html: "Hover a block or arrow: the code that does it lights up in the U-Net pairs above. <b>Blue</b> = DoubleConv, <b>red</b> = max-pool, <b>green</b> = up-conv, <b>dashed</b> = crop + concat." }));
    nS.addEventListener("input", function () { nN.value = nS.value; draw(); }); nN.addEventListener("input", function () { nS.value = nN.value; draw(); });
    pad.addEventListener("change", draw); base.addEventListener("change", draw);
    function draw() {
      var n = +nN.value, valid = pad.value === "valid", r = unetTrace(n, valid, +base.value);
      var W = 900, H = 330, lvlY = function (l) { return 30 + l * 62; }, sp = { w: W, h: H, boxes: [], lines: [], labels: [] };
      r.down.forEach(function (d, l) {
        var x = 40 + l * 70; sp.boxes.push({ x: x, y: lvlY(l), w: 150, h: 34, t: d.out + "² × " + d.c, sub: l ? "" : "", lk: "un-conv", fill: "#dbeafe", size: 13 });
        if (l < 4 && r.down[l + 1]) sp.lines.push([x + 75, lvlY(l) + 34, x + 145, lvlY(l + 1)]);
      });
      r.down.forEach(function (d, l) { if (l < 4 && r.down[l + 1]) sp.labels.push({ x: 40 + l * 70 + 135, y: lvlY(l) + 50, t: "pool → " + d.out / 2, size: 11, color: "#b91c1c", anchor: "start" }); });
      r.up.forEach(function (u, i) {
        var l = 3 - i, x = W - 190 - l * 70;
        sp.boxes.push({ x: x, y: lvlY(l), w: 150, h: 34, t: u.out + "² × " + u.c, lk: "un-conv", fill: "#dbeafe", size: 13 });
        sp.lines.push([l === 3 ? 40 + 4 * 70 + 140 : x + 5, lvlY(l + 1), x + 75, lvlY(l) + 34]);
        sp.labels.push({ x: x - 4, y: lvlY(l) + 52, t: "up → " + u.up, size: 11, color: "#15803d", anchor: "end" });
        sp.lines.push([40 + l * 70 + 150, lvlY(l) + 17, x - 2, lvlY(l) + 17, 1]);
        sp.labels.push({ x: (40 + l * 70 + 150 + x) / 2, y: lvlY(l) + 12, t: (x - (40 + l * 70 + 150) < 200) ? (u.crop ? "crop −" + u.crop + ", concat" : "concat") : (u.crop ? "crop " + u.skip + " → " + u.up + " (−" + u.crop + " each side), concat" : "concat (no crop needed)"), size: 11, color: "#475569" });
      });
      if (r.ok) {
        sp.boxes.push({ x: W - 180, y: lvlY(0) - 28, w: 140, h: 24, t: "1×1 conv → " + r.out + "² × 2", lk: "un-head", fill: "#dcfce7", size: 12 });
        sp.boxes.unshift({ x: 40, y: 2, w: 150, h: 22, t: "input " + n + "² × 1", fill: "#f1f5f9", size: 12 });
      }
      // colour arrows: rebuild with lk classes after drawing
      drawFig(fig, sp);
      $$("line", fig).forEach(function (ln) {
        var dash = ln.getAttribute("stroke-dasharray");
        var y1 = +ln.getAttribute("y1"), y2 = +ln.getAttribute("y2");
        if (dash) { ln.setAttribute("class", "lk-un-crop"); ln.setAttribute("stroke", "#64748b"); }
        else if (y2 > y1) { ln.setAttribute("class", "lk-un-pool"); ln.setAttribute("stroke", "#b91c1c"); }
        else { ln.setAttribute("class", "lk-un-up"); ln.setAttribute("stroke", "#15803d"); }
        ln.setAttribute("stroke-width", "3"); ln.style.cursor = "pointer";
      });
      o.innerHTML = r.ok
        ? "<b>Output: " + r.out + " × " + r.out + "</b>" + (valid ? " = n − 184 = " + n + " − 184 ✓ (Derivation I)" : " = n (padding keeps the size; the input must be divisible by 16)") + ". Bottleneck " + r.down[4].out + "² × " + r.down[4].c + ". Parameters: <b>" + int(r.params) + "</b> (padding does not change parameters; base 64 gives the paper's 31 030 658)."
        : "<b style='color:#b91c1c'>Invalid input " + n + ":</b> " + r.err + "." + (valid ? " Valid 2015 tiles are n = 16k + 124: … 508, 524, 540, 556, 572, 588 …" : " With padding, n must be divisible by 16.") + " Press <i>next valid size</i>.";
    }
    draw();
  }

  /* ------------------------------------------------------------ 10. Dice painter */
  function wDice(m) {
    var body = shell(m, "Dice vs IoU vs pixel accuracy: paint a prediction", "hands-on");
    var N = 12, truth = [], pred = [], mode = 1, down = false;
    for (var i = 0; i < N * N; i++) { var r = Math.floor(i / N), c = i % N; truth.push((r - 5.5) * (r - 5.5) + (c - 5.0) * (c - 5.0) <= 9.5 ? 1 : 0); pred.push((r - 5.5) * (r - 5.5) + (c - 6.6) * (c - 6.6) <= 7.5 ? 1 : 0); }
    var grid = h("div", { class: "paint", role: "grid", "aria-label": "12 by 12 pixel grid" });
    var cells = truth.map(function (t, i) {
      var d = h("div");
      d.addEventListener("pointerdown", function (e) { e.preventDefault(); try { d.releasePointerCapture(e.pointerId); } catch (_) {} down = true; mode = pred[i] ? 0 : 1; pred[i] = mode; draw(); });
      d.addEventListener("pointerenter", function () { if (down) { pred[i] = mode; draw(); } });
      grid.appendChild(d); return d;
    });
    document.addEventListener("pointerup", function () { down = false; });
    var o = h("div", { class: "steps" });
    var btns = h("div", { class: "ctrl" }, [
      h("button", { class: "wbtn alt", text: "Perfect", onclick: function () { pred = truth.slice(); draw(); } }),
      h("button", { class: "wbtn alt", text: "Predict nothing", onclick: function () { pred = truth.map(function () { return 0; }); draw(); } }),
      h("button", { class: "wbtn alt", text: "Shift → 1 px", onclick: function () { var p = pred.map(function () { return 0; }); pred.forEach(function (v, i) { if (v && i % N < N - 1) p[i + 1] = 1; }); pred = p; draw(); } })]);
    body.appendChild(h("div", { class: "wrow" }, [h("div", null, [grid, h("div", { class: "key", html: "<span><i style='background:#bfdbfe'></i>truth only (FN)</span><span><i style='background:#fdba74'></i>prediction only (FP)</span><span><i style='background:#16a34a'></i>overlap (TP)</span>" })]), h("div", { class: "wcol" }, [btns, o])]));
    body.appendChild(h("div", { class: "ask", html: "<b>Click or drag</b> to paint or erase the prediction. Press <i>Predict nothing</i>: pixel accuracy stays high because most pixels are background, while Dice falls to 0. That is why U-Net papers report Dice or IoU, not accuracy." }));
    function draw() {
      var A = 0, B = 0, I = 0, Ac = 0;
      cells.forEach(function (d, i) { d.className = (truth[i] ? "t " : "") + (pred[i] ? "p" : ""); A += pred[i]; B += truth[i]; I += pred[i] & truth[i]; Ac += pred[i] === truth[i] ? 1 : 0; });
      var U = A + B - I, dice = A + B ? 2 * I / (A + B) : 1, iou = U ? I / U : 1;
      o.innerHTML = "|A| predicted = <b>" + A + "</b> · |B| true = <b>" + B + "</b> · |A∩B| = <b>" + I + "</b> · |A∪B| = <b>" + U + "</b><ol>" +
        "<li>Dice = 2·" + I + " / (" + A + " + " + B + ") = <b>" + dice.toFixed(3) + "</b></li><li>IoU = " + I + " / " + U + " = <b>" + iou.toFixed(3) + "</b></li>" +
        "<li>Check: 2·IoU/(1 + IoU) = " + (2 * iou / (1 + iou)).toFixed(3) + (Math.abs(2 * iou / (1 + iou) - dice) < 1e-9 ? " ✓" : "") + "</li>" +
        "<li>Pixel accuracy = " + Ac + " / " + N * N + " = <b>" + (Ac / (N * N) * 100).toFixed(1) + " %</b></li></ol>";
    }
    draw();
  }

  /* ------------------------------------------------------------ 11. ViT patch explorer */
  function paintScene(ctx, S) {
    var g = ctx.createLinearGradient(0, 0, 0, S); g.addColorStop(0, "#7dd3fc"); g.addColorStop(.62, "#e0f2fe"); g.addColorStop(.62, "#86efac"); g.addColorStop(1, "#22c55e");
    ctx.fillStyle = g; ctx.fillRect(0, 0, S, S);
    ctx.fillStyle = "#facc15"; ctx.beginPath(); ctx.arc(S * .8, S * .18, S * .09, 0, 7); ctx.fill();
    ctx.fillStyle = "#b45309"; ctx.fillRect(S * .16, S * .42, S * .34, S * .3);
    ctx.fillStyle = "#991b1b"; ctx.beginPath(); ctx.moveTo(S * .12, S * .43); ctx.lineTo(S * .33, S * .25); ctx.lineTo(S * .54, S * .43); ctx.fill();
    ctx.fillStyle = "#1e3a8a"; ctx.fillRect(S * .29, S * .56, S * .08, S * .16);
    ctx.fillStyle = "#78350f"; ctx.fillRect(S * .7, S * .48, S * .05, S * .22);
    ctx.fillStyle = "#15803d"; ctx.beginPath(); ctx.arc(S * .725, S * .43, S * .1, 0, 7); ctx.fill();
  }
  function wPatch(m) {
    var body = shell(m, "ViT patch explorer: how an image becomes a sentence", "live");
    var sz = h("select", { "aria-label": "image size" }, [224, 384].map(function (v) { return h("option", { value: v, text: v + " × " + v }); }));
    var ps = h("select", { "aria-label": "patch size" }, [16, 32, 14, 8].map(function (v) { return h("option", { value: v, text: "P = " + v }); }));
    var file = h("input", { type: "file", accept: "image/*", "aria-label": "use your own image" });
    body.appendChild(h("div", { class: "ctrl" }, [h("label", null, ["image ", sz]), h("label", null, ["patch ", ps]), h("label", null, ["or your own photo (stays on your computer): ", file])]));
    var row = h("div", { class: "wrow" }); body.appendChild(row);
    var cv = h("canvas", { class: "cv", width: 384, height: 384, style: "width:336px;max-width:100%;cursor:pointer", "aria-label": "image with patch grid; click a patch" });
    var src = h("canvas", { width: 384, height: 384 }); var user = null;
    var info = h("div", { class: "wcol" });
    row.appendChild(h("div", null, [cv])); row.appendChild(info);
    var sel = 0;
    cv.addEventListener("click", function (e) { var S = +sz.value, P = +ps.value, n = Math.floor(S / P), r = cv.getBoundingClientRect(); var x = Math.floor((e.clientX - r.left) / r.width * S / P), y = Math.floor((e.clientY - r.top) / r.height * S / P); if (x < n && y < n) { sel = y * n + x; draw(); } });
    file.addEventListener("change", function () { var fl = file.files && file.files[0]; if (!fl) return; var im = new Image(); im.onload = function () { user = im; draw(); }; im.src = URL.createObjectURL(fl); });
    sz.addEventListener("change", function () { sel = 0; draw(); }); ps.addEventListener("change", function () { sel = 0; draw(); });
    function draw() {
      var S = +sz.value, P = +ps.value, n = Math.floor(S / P), N = n * n;
      src.width = src.height = S; cv.width = cv.height = S;
      var sc = src.getContext("2d");
      if (user) { var m2 = Math.min(user.width, user.height); sc.drawImage(user, (user.width - m2) / 2, (user.height - m2) / 2, m2, m2, 0, 0, S, S); } else paintScene(sc, S);
      var ctx = cv.getContext("2d"); ctx.drawImage(src, 0, 0);
      ctx.strokeStyle = "rgba(255,255,255,.85)"; ctx.lineWidth = 1;
      for (var i = 0; i <= n; i++) { ctx.beginPath(); ctx.moveTo(i * P + .5, 0); ctx.lineTo(i * P + .5, n * P); ctx.moveTo(0, i * P + .5); ctx.lineTo(n * P, i * P + .5); ctx.stroke(); }
      if (sel >= N) sel = 0;
      var sx = (sel % n) * P, sy = Math.floor(sel / n) * P;
      ctx.strokeStyle = "#d9480f"; ctx.lineWidth = 3; ctx.strokeRect(sx + 1.5, sy + 1.5, P - 3, P - 3);
      var px = sc.getImageData(sx, sy, P, P).data;
      // flattened patch vector, (P, P, C) order as in patchify(): row, col, channel
      var L = P * P * 3, strip = h("canvas", { width: L, height: 1, class: "cv", style: "width:100%;height:22px" });
      var sctx = strip.getContext("2d"), sim = sctx.createImageData(L, 1);
      for (var k = 0; k < P * P; k++) for (var c = 0; c < 3; c++) { var v = px[k * 4 + c], o = (k * 3 + c) * 4; sim.data[o] = c === 0 ? v : 0; sim.data[o + 1] = c === 1 ? v : 0; sim.data[o + 2] = c === 2 ? v : 0; sim.data[o + 3] = 255; }
      sctx.putImageData(sim, 0, 0);
      var toks = h("div", { class: "tokstrip" }), show = Math.min(N + 1, 400);
      for (k = 0; k < show; k++) toks.appendChild(h("span", { style: "background:" + (k === 0 ? "#7c3aed" : k - 1 === sel ? "#d9480f" : "#94a3b8") + (N > 300 ? ";width:9px;height:9px;font-size:0" : ""), text: k === 0 ? "C" : "", title: k === 0 ? "[class] token" : "token " + k + " = patch " + (k - 1) }));
      if (N + 1 > show) toks.appendChild(h("span", { style: "background:none;color:#475569;width:auto", text: "… " + (N + 1 - show) + " more" }));
      var base = 197 * 197, att = (N + 1) * (N + 1);
      info.innerHTML = "";
      info.appendChild(h("div", { class: "steps", html: "<ol><li>N = (H/P)² = (" + S + "/" + P + ")² = " + n + "² = <b>" + N + " patches</b>" + (S % P ? " <span style='color:#b91c1c'>(" + S + " is not divisible by " + P + ": " + (S % P) + " pixels are dropped)</span>" : "") + "</li>" +
        "<li>Each patch → P·P·C = " + P + "·" + P + "·3 = <b>" + L + " numbers</b> → Linear E → D</li>" +
        "<li>+ 1 [class] token → <b>" + (N + 1) + " tokens</b></li>" +
        "<li>Attention matrix per head: " + (N + 1) + "² = <b>" + int(att) + "</b> entries (" + (att / base).toFixed(1) + " × ViT-B/16 at 224)</li></ol>" }));
      info.appendChild(h("b", { text: "Selected patch " + sel + " → token " + (sel + 1) + ", flattened (" + L + " values: R G B R G B …)" }));
      info.appendChild(strip);
      info.appendChild(h("b", { text: "The sequence the Transformer reads (C = [class], orange = your patch)" }));
      info.appendChild(toks);
    }
    draw();
  }

  /* ------------------------------------------------------------ 12. ViT parameter calculator */
  function wVitParams(m) {
    var body = shell(m, "ViT parameter calculator (check Derivation K, then try L/16 and H/14)", "calculator");
    var F = { img: numInput("image", 224), p: numInput("patch P", 16), c: numInput("channels", 3), d: numInput("D", 768), l: numInput("layers L", 12), mlp: numInput("MLP", 3072), k: numInput("classes", 1000) };
    var presets = { "ViT-B/16": [224, 16, 3, 768, 12, 3072, 1000, "86 M (torchvision 86 567 656)"], "ViT-L/16": [224, 16, 3, 1024, 24, 4096, 1000, "307 M (torchvision 304 326 632)"], "ViT-H/14": [224, 14, 3, 1280, 32, 5120, 1000, "632 M (torchvision 632 045 800)"], "Lab 7F tiny": [8, 2, 1, 64, 4, 128, 10, ""] };
    var paper = presets["ViT-B/16"][7], pb = h("div", { class: "ctrl" });
    Object.keys(presets).forEach(function (k) { pb.appendChild(h("button", { class: "wbtn alt", text: k, onclick: function () { var p = presets[k]; ["img", "p", "c", "d", "l", "mlp", "k"].forEach(function (n, i) { F[n].inp.value = p[i]; }); paper = p[7]; draw(); } })); });
    body.appendChild(pb);
    body.appendChild(h("div", { class: "ctrl" }, Object.keys(F).map(function (k) { return F[k].el; })));
    var o = h("div"); body.appendChild(o); var note = h("div", { class: "ask" }); body.appendChild(note);
    function draw() {
      var S = +F.img.inp.value, P = +F.p.inp.value, C = +F.c.inp.value, D = +F.d.inp.value, L = +F.l.inp.value, M = +F.mlp.inp.value, K = +F.k.inp.value, N = Math.pow(Math.floor(S / P), 2);
      var pe = P * P * C * D + D, cls = D, pos = (N + 1) * D, blk = 4 * D + 4 * (D * D + D) + (D * M + M + M * D + D), fin = 2 * D, head = D * K + K;
      var tot = pe + cls + pos + L * blk + fin + head;
      o.innerHTML = ""; o.appendChild(breakdown([["Patch embedding E: P²C·D + D", pe], ["[class] token + E<sub>pos</sub> (" + (N + 1) + " × D)", cls + pos], [L + " × encoder block (2 LN + MSA + MLP)", L * blk], ["final LN + head", fin + head]], tot, paper));
      note.innerHTML = "Tokens = " + N + " + 1 = <b>" + (N + 1) + "</b>; one block = " + int(blk) + " (MSA " + int(4 * (D * D + D)) + ", MLP " + int(D * M + M + M * D + D) + "). <b>Try:</b> change only the image size: just E<sub>pos</sub> changes, which is why ViT can be fine-tuned at a higher resolution by interpolating the position embeddings (§3.2).";
    }
    Object.keys(F).forEach(function (k) { F[k].inp.addEventListener("input", function () { paper = ""; draw(); }); }); draw();
  }

  /* ------------------------------------------------------------ 13. ResNet gradient explorer */
  function wResGrad(m) {
    var body = shell(m, "Gradient through depth: plain vs residual", "simulation");
    var n = h("input", { type: "range", min: 2, max: 100, value: 20, "aria-label": "depth" }), nO = h("output");
    var fp = h("input", { type: "range", min: 0.1, max: 1.5, step: 0.05, value: 0.5, "aria-label": "plain layer derivative" }), fO = h("output");
    var Fp = h("input", { type: "range", min: -0.3, max: 0.3, step: 0.01, value: 0, "aria-label": "residual branch derivative" }), FO = h("output");
    body.appendChild(h("div", { class: "ctrl" }, [h("label", null, ["depth = ", nO, n]), h("label", null, ["plain f′ = ", fO, fp]), h("label", null, ["residual branch F′ = ", FO, Fp])]));
    var plot = h("div"); body.appendChild(plot); var o = h("div", { class: "steps" }); body.appendChild(o);
    body.appendChild(h("div", { class: "ask", html: "<b>Try:</b> set f′ = 1.2: the plain net <i>explodes</i> instead of vanishing. Real layers are never exactly 1, so a plain net is always walking a tightrope. The residual net only needs F′ ≈ 0, which is what weight decay and a small initialisation give." }));
    function draw() {
      var N = +n.value, a = +fp.value, b = +Fp.value; nO.textContent = N; fO.textContent = a.toFixed(2); FO.textContent = b.toFixed(2);
      var W = 640, H = 230, lo = -12, hi = 6, Y = function (v) { var l = Math.max(lo, Math.min(hi, Math.log10(v))); return 15 + (hi - l) / (hi - lo) * (H - 40); }, X = function (k) { return 50 + k / N * (W - 70); };
      var pl = [], rs = []; for (var k = 0; k <= N; k++) { pl.push(X(k).toFixed(1) + "," + Y(Math.pow(a, k)).toFixed(1)); rs.push(X(k).toFixed(1) + "," + Y(Math.pow(1 + b, k)).toFixed(1)); }
      var grid = ""; for (var e = lo; e <= hi; e += 3) grid += '<line x1="50" x2="' + (W - 20) + '" y1="' + Y(Math.pow(10, e)) + '" y2="' + Y(Math.pow(10, e)) + '" stroke="#e2e8f0"/><text x="44" y="' + (Y(Math.pow(10, e)) + 4) + '" font-size="11" text-anchor="end" fill="#64748b">1e' + e + "</text>";
      plot.innerHTML = '<svg viewBox="0 0 ' + W + " " + H + '" style="width:100%;max-width:760px;height:auto">' + grid + '<polyline fill="none" stroke="#ea580c" stroke-width="2.5" points="' + pl.join(" ") + '"/><polyline fill="none" stroke="#0f766e" stroke-width="2.5" points="' + rs.join(" ") + '"/><text x="' + (W / 2) + '" y="' + (H - 4) + '" font-size="12" text-anchor="middle" fill="#475569">layers back from the loss →</text><text x="60" y="' + (H - 22) + '" font-size="12" fill="#ea580c" font-weight="700">plain: (f′)ᵏ</text><text x="180" y="' + (H - 22) + '" font-size="12" fill="#0f766e" font-weight="700">residual: (1 + F′)ᵏ</text></svg>';
      var gp = Math.pow(a, N), gr = Math.pow(1 + b, N);
      o.innerHTML = "Gradient reaching layer 1 after " + N + " layers: plain = " + a.toFixed(2) + "<sup>" + N + "</sup> = <b>" + gp.toExponential(2) + "</b> · residual = " + (1 + b).toFixed(2) + "<sup>" + N + "</sup> = <b>" + gr.toExponential(2) + "</b>" + (gp < 1e-4 ? " → the plain net's first layers stop learning (Derivation M)." : gp > 1e4 ? " → the plain net explodes." : ".");
    }
    [n, fp, Fp].forEach(function (x) { x.addEventListener("input", draw); }); draw();
  }

  /* ------------------------------------------------------------ 14. AI workflow + prompt builder */
  var FLOW = [
    { t: "Skim", n: "Pass 1", you: ["Read title, abstract, figures, conclusion (10 min)", "Write a 3-sentence summary yourself"], ai: ["Explain words you don't know", "Quiz you on the abstract"], no: ["Summarise the paper before you have read it", "Replace your own summary"],
      p: "I just read the abstract and Figure 1 of \"{paper}\". My 3-sentence summary:\n<paste your summary>\n\nDon't rewrite it. Ask me 3 questions, one at a time, that test whether I understood the problem and the main idea. Wait for my answer before the next question.", v: "Your summary matches the paper's own list of contributions (end of §1)." },
    { t: "Paper card", n: "Pass 2", you: ["Fill the paper card: problem, input → output, key idea, data, metric, main result with table number"], ai: ["Check your card against text you paste", "Point out missing fields"], no: ["Invent numbers: every number needs a table or figure you checked"],
      p: "Here is {section} of \"{paper}\":\n<paste the text>\n\nAnd my paper card:\n<paste card>\n\nList the fields that are wrong or missing. For each correction, quote the sentence from my paste that supports it. If the paste doesn't say, write \"not in the text\"; do not guess.", v: "Every number on the card has a Table/Figure reference you opened yourself." },
    { t: "Shape table", n: "Plan", you: ["Write the shape of every tensor, block by block, before coding"], ai: ["Check each row ✓/✗ with a hint"], no: ["Hand you the full table"],
      p: "I'm implementing \"{paper}\" ({section}). My shape table:\n<paste table>\n\nFor each row write ✓ or ✗. For ✗ give a hint (which dimension and why), not the corrected shape.", v: "Your table agrees with the numbers printed in the paper's figure (e.g. 572 → 388, 197 tokens)." },
    { t: "Derive", n: "Math", you: ["Derive every equation with tiny numbers, like this page"], ai: ["Check one step at a time", "Explain the step you're stuck on"], no: ["Do the whole derivation for you"],
      p: "I'm deriving {section} of \"{paper}\" by hand with these numbers:\n<paste numbers>\n\nMy steps so far:\n<paste steps>\n\nIs step <n> right? If not, explain the mistake with a hint and stop. Don't give the final numbers.", v: "Your hand result equals the code's output to 3 decimals." },
    { t: "Code", n: "Build", you: ["Write each block yourself, in order, running it after every block"], ai: ["Explain an error message", "Name the PyTorch function to read about"], no: ["Write your TODO cells", "Give code you cannot explain line by line"],
      p: "Act as a tutor, not a coder. Here is my {block} and the error:\n<paste code + full error>\n\nExplain what the error means and which line causes it. Do not rewrite my code; give me one hint I can act on.", v: "You can explain every line in the viva without notes." },
    { t: "Verify", n: "Test", you: ["Run checks: shapes, hand example, parameter count, reference implementation, overfit one batch"], ai: ["Suggest a test that would catch a bug your tests miss"], no: ["Be your test: \"the AI says it's correct\" is not evidence"],
      p: "Here is my {block} and the tests it passes:\n<paste code + tests>\n\nWhat bug could still pass all of these tests? Propose one more test that would catch it. Do not fix my code.", v: "All Lab 7 ✅ checks pass, and the parameter count equals the paper or torchvision." },
    { t: "Report", n: "Write", you: ["What matched, what didn't (with numbers), one experiment, one ablation, AI-use declaration"], ai: ["Flag unsupported claims", "Improve clarity, keep your numbers"], no: ["Generate results", "Add references you haven't read"],
      p: "Here is my reproduction report for \"{paper}\":\n<paste report>\n\nMark every sentence that claims something my numbers don't support. Suggest clearer wording, but keep all my numbers unchanged.", v: "Every claim points to a table or plot in your notebook." }
  ];
  function wFlow(m) {
    var body = shell(m, "The AI-era workflow: what you do, what AI may do, what it must not do", "click a step");
    var bar = h("div", { class: "wf", role: "tablist" }), card = h("div", { class: "wfcard" }); body.appendChild(bar); body.appendChild(card);
    var cur = 0;
    FLOW.forEach(function (s, i) { bar.appendChild(h("button", { role: "tab", html: "<small>" + (i + 1) + " · " + s.n + "</small>" + s.t, onclick: function () { cur = i; draw(); } })); });
    function li(a) { return "<ul>" + a.map(function (x) { return "<li>" + x + "</li>"; }).join("") + "</ul>"; }
    function draw() {
      $$("button", bar).forEach(function (b, i) { b.classList.toggle("on", i === cur); b.setAttribute("aria-selected", i === cur); });
      var s = FLOW[cur], p = s.p.replace(/\{paper\}/g, "Attention Is All You Need").replace(/\{section\}/g, "§3.2.1, Eq. (1)").replace(/\{block\}/g, "MultiHeadAttention class");
      card.innerHTML = '<div class="you"><h5>You do</h5>' + li(s.you) + '</div><div class="ai"><h5>AI may</h5>' + li(s.ai) + '</div><div class="no"><h5>AI must not</h5>' + li(s.no) + "</div>" +
        '<div class="wfprompt"><h5 style="color:var(--navy)">Example prompt</h5><div class="promptbox"><pre></pre></div><p class="hint"><b>Done when:</b> ' + s.v + "</p></div>";
      var pre = $("pre", card); pre.textContent = p;
      $(".promptbox", card).appendChild(h("button", { class: "wbtn", text: "Copy", onclick: function (e) { copyText(p, e.target); } }));
    }
    draw();
  }
  function wPrompt(m) {
    var body = shell(m, "Prompt builder: a tutor prompt for any paper in 20 seconds", "copy & paste");
    var paper = h("select", { "aria-label": "paper" }, ["Attention Is All You Need (Vaswani et al., 2017)", "U-Net (Ronneberger et al., 2015)", "An Image is Worth 16x16 Words: ViT (Dosovitskiy et al., 2021)", "Deep Residual Learning: ResNet (He et al., 2016)", "other…"].map(function (t) { return h("option", { text: t }); }));
    var other = h("input", { type: "text", placeholder: "paper title", style: "display:none;padding:3px 6px;border:1px solid var(--line);border-radius:6px;font:inherit", "aria-label": "other paper title" });
    var sec = h("input", { type: "text", value: "§3.2.1, Eq. (1)", style: "width:160px;padding:3px 6px;border:1px solid var(--line);border-radius:6px;font:inherit", "aria-label": "section" });
    var TASKS = {
      "Explain like a tutor": "Explain this part to me step by step with a tiny numeric example (2–3 tokens / a 4×4 image). After each step, stop and ask me to predict the next one.",
      "Check my derivation": "Check my derivation one step at a time. For the first wrong step, explain the mistake with a hint and stop. Don't give me the final result.",
      "Quiz me": "Ask me 5 short questions about this part, one at a time, from easy to hard (at least one about tensor shapes, one numeric). Tell me if I'm right after each answer.",
      "Check my shape table": "Check my shape table row by row: ✓ or ✗, and for ✗ a hint about which dimension is wrong and why. Don't write the corrected table.",
      "Review my code (no rewrite)": "Review my code against the paper's text. List mismatches with the paper (line number + the sentence of the paper it contradicts). Don't rewrite the code.",
      "Explain an error": "Explain what this error means and which line causes it. Give one hint I can act on, not the fixed code.",
      "Design a test": "What bug could still pass my current tests? Propose one more test (input, expected output and why) that would catch it.",
      "Compare with the paper's numbers": "I got the results below. Tell me which of the paper's tables/figures they should be compared with, what differences are expected (data, model size, training time) and what I should honestly write in my report."
    };
    var task = h("select", { "aria-label": "task" }, Object.keys(TASKS).map(function (t) { return h("option", { text: t }); }));
    var RULES = [["hint", "Give hints, not answers", "Give me hints, not full answers or full code.", 1], ["quote", "Quote section / equation numbers", "When you refer to the paper, cite the section, equation or figure number. If you are not sure the paper says it, say so.", 1], ["shape", "Always write tensor shapes", "Write the tensor shape next to every tensor, as (B, L, D) etc.", 1], ["one", "One question at a time", "Ask me only one question at a time and wait for my answer.", 0], ["unsure", "Say \"I'm not sure\" instead of guessing", "If you don't know, say \"I'm not sure\" instead of guessing.", 1]];
    var checks = RULES.map(function (r) { var c = h("input", { type: "checkbox" }); if (r[3]) c.checked = true; c.addEventListener("change", draw); return { c: c, r: r }; });
    var have = h("textarea", { rows: 3, placeholder: "(optional) paste what you have: your summary, derivation, shape table, code or error", style: "width:100%;font:13px Consolas,monospace;border:1px solid var(--line);border-radius:8px;padding:6px", "aria-label": "your material" });
    body.appendChild(h("div", { class: "ctrl" }, [h("label", null, ["Paper ", paper]), other, h("label", null, ["Part ", sec]), h("label", null, ["Task ", task])]));
    body.appendChild(h("div", { class: "ctrl" }, checks.map(function (x) { return h("label", null, [x.c, x.r[1]]); })));
    body.appendChild(have);
    var box = h("div", { class: "promptbox" }), pre = h("pre"); box.appendChild(pre);
    box.appendChild(h("button", { class: "wbtn", text: "Copy", onclick: function (e) { copyText(pre.textContent, e.target); } }));
    body.appendChild(box);
    body.appendChild(h("p", { class: "hint", html: "Paste the result into Claude, ChatGPT or Cursor. <b>Always paste the paper's own text</b> for the part you ask about: the model then works from the paper, not from memory." }));
    [paper, sec, task, have, other].forEach(function (x) { x.addEventListener("input", draw); x.addEventListener("change", draw); });
    function draw() {
      other.style.display = paper.value === "other…" ? "" : "none";
      var pt = paper.value === "other…" ? (other.value || "<paper title>") : paper.value;
      var txt = "You are my tutor for reading and implementing a research paper. I am a university student learning PyTorch.\n\n" +
        "Paper: " + pt + "\nPart: " + (sec.value || "<section / equation / figure>") + "\n\n" +
        "Task: " + TASKS[task.value] + "\n\nRules:\n" + checks.filter(function (x) { return x.c.checked; }).map(function (x) { return "- " + x.r[2]; }).join("\n") +
        "\n\nThe paper's text for this part:\n<paste the paragraph / equation from the PDF>\n" + (have.value.trim() ? "\nWhat I have so far:\n" + have.value.trim() + "\n" : "\nWhat I have so far:\n<paste your work>\n");
      pre.textContent = txt;
    }
    draw();
  }

  /* ------------------------------------------------------------ 15. quick checks */
  var QUIZ = {
    att: [
      ["Q is (2, 8, 10, 64) and K is (2, 8, 12, 64). Shape of the attention weights?", ["(2, 8, 10, 12)", "(2, 8, 12, 10)", "(2, 8, 10, 64)", "(2, 10, 12)"], 0, "One weight per (query, key) pair, per head: (B, h, Lq, Lk)."],
      ["Over which axis of the scores (B, h, Lq, Lk) is the softmax taken?", ["the last one: keys", "Lq: queries", "h: heads", "B: batch"], 0, "Each query distributes its attention over the keys, so each row over keys sums to 1."],
      ["When are masked positions set to −∞?", ["before the softmax", "after the softmax", "after multiplying by V"], 0, "e^(−∞) = 0, so the softmax gives them weight exactly 0 and the rest still sum to 1."],
      ["d_model = 512. How do the parameters of MHA with h = 8 compare with h = 1?", ["the same", "8 × more", "8 × fewer"], 0, "4(d² + d) for any h: heads only split the 512 features into pieces."]],
    tr: [
      ["No positional encoding: the encoder sees \"dog bites man\" and \"man bites dog\". The outputs are…", ["the same vectors, in a different order", "completely different", "identical, in the same order"], 0, "Self-attention is permutation-equivariant: it treats the input as a set."],
      ["LayerNorm in the Transformer normalises over…", ["the features of each token", "the batch", "the sequence positions"], 0, "μ and σ are computed over the last axis (d_model) of each token, independently."],
      ["At training time, the decoder input is…", ["the target shifted right, starting with BOS", "its own previous predictions", "the encoder output"], 0, "Teacher forcing: the decoder sees the correct previous tokens and predicts the next one at every position in parallel."]],
    un: [
      ["The 2015 U-Net gets a 572 × 572 tile. Output size?", ["388 × 388", "572 × 572", "284 × 284", "324 × 324"], 0, "out = n − 184 with unpadded convolutions."],
      ["A U-Net skip connection combines encoder and decoder features by…", ["concatenation on channels", "addition", "multiplication"], 0, "torch.cat([...], dim=1): channels add up (256 + 256 = 512). ResNet adds; U-Net concatenates."],
      ["The object covers 2 % of the image and the network predicts nothing at all. Which number exposes this?", ["Dice = 0", "pixel accuracy ≈ 98 %", "both look fine"], 0, "Accuracy is dominated by the background. Dice/IoU only count the class pixels (try it in the painter)."]],
    vit: [
      ["ViT-B/16, 224 × 224 image: how many tokens enter the encoder?", ["197", "196", "224", "768"], 0, "(224/16)² = 196 patches + 1 [class] token."],
      ["Conv2d(3, D, kernel_size=16, stride=16) is the same as…", ["flatten each 16×16 patch and multiply by E", "a 16-layer CNN", "the position embedding"], 0, "kernel = stride means every patch is seen once by the same weights: a linear projection per patch."],
      ["Where does ViT put LayerNorm?", ["before each sub-layer (pre-norm)", "after each sub-layer (post-norm), as in 2017"], 0, "Eq. 2–3: z' = MSA(LN(z)) + z. Pre-norm trains deep stacks more stably."]],
    rn: [
      ["y = F(x) + x. What is ∂y/∂x?", ["F′(x) + 1", "F′(x)", "F′(x) · x"], 0, "The + 1 is the gradient highway that keeps deep networks trainable."],
      ["A block maps (B, 64, 56, 56) → (B, 128, 28, 28). The shortcut is…", ["1×1 conv, stride 2, + BatchNorm", "the identity", "no shortcut"], 0, "Shapes differ, so a projection is needed (§3.3, option B)."]]
  };
  var quizState = store("t10-quiz") || {};
  function updateProg() {
    var tot = 0, ok = 0; Object.keys(QUIZ).forEach(function (k) { tot += QUIZ[k].length; QUIZ[k].forEach(function (_, i) { if (quizState[k + i] === 1) ok++; }); });
    var p = $("#t10prog"); if (!p) return;
    p.innerHTML = "<b>Your quick checks</b><div class='barline'><i style='width:" + (ok / tot * 100) + "%'></i></div>" + ok + " / " + tot + " correct ";
    p.appendChild(h("button", { text: "reset", onclick: function () { quizState = {}; store("t10-quiz", quizState); $$("[data-quiz]").forEach(mountQuiz); updateProg(); } }));
  }
  function mountQuiz(m) {
    var id = m.getAttribute("data-quiz"), qs = QUIZ[id]; if (!qs) return;
    m.className = "quiz"; m.innerHTML = "<b>✔ Quick check</b> (instant feedback; your score is kept in this browser)";
    var sc = h("div", { class: "score" });
    qs.forEach(function (q, qi) {
      var key = id + qi, why = h("div", { class: "why", text: q[3] }), opts = h("div", { class: "opts" });
      var order = q[1].map(function (_, i) { return i; }); order.sort(function (a, b) { return ((a * 7 + qi * 3) % 5) - ((b * 7 + qi * 3) % 5); });
      order.forEach(function (oi) {
        var b = h("button", { text: q[1][oi] });
        b.addEventListener("click", function () {
          var right = oi === q[2];
          $$("button", opts).forEach(function (x) { x.disabled = true; }); b.classList.add(right ? "right" : "wrong");
          if (!right) $$("button", opts).forEach(function (x) { if (x.textContent === q[1][q[2]]) x.classList.add("right"); });
          why.classList.add("on"); why.textContent = (right ? "✓ " : "✗ ") + q[3];
          quizState[key] = right ? 1 : 0; store("t10-quiz", quizState); score(); updateProg();
        });
        if (quizState[key] != null) { b.disabled = true; if (oi === q[2]) b.classList.add("right"); }
        opts.appendChild(b);
      });
      if (quizState[key] != null) { why.classList.add("on"); why.textContent = (quizState[key] ? "✓ " : "✗ ") + q[3]; }
      m.appendChild(h("div", { class: "q", text: (qi + 1) + ". " + q[0] })); m.appendChild(opts); m.appendChild(why);
    });
    m.appendChild(sc);
    function score() { var ok = 0, done = 0; qs.forEach(function (_, i) { if (quizState[id + i] != null) { done++; ok += quizState[id + i]; } }); sc.textContent = done ? "Score: " + ok + " / " + qs.length + (done === qs.length && ok === qs.length ? "  🎉" : "") : ""; }
    score();
  }

  /* ------------------------------------------------------------ 16. session clock for the 3-hour plan */
  function wClock(m) {
    var rows = $$("table.plan tr[data-t]");
    var st = store("t10-clock") || { start: null, acc: 0 };
    var time = h("span", { class: "time" }), now = h("span", { class: "now" });
    var go = h("button", { class: "wbtn" }), rs = h("button", { class: "wbtn alt", text: "Reset" });
    var fw = h("button", { class: "wbtn alt", text: "+5 min" });
    m.className = "clock"; m.innerHTML = "";
    [h("b", { text: "Session clock" }), time, go, fw, rs, now].forEach(function (x) { m.appendChild(x); });
    function el() { return (st.acc + (st.start ? Date.now() - st.start : 0)) / 60000; }
    go.addEventListener("click", function () { if (st.start) { st.acc += Date.now() - st.start; st.start = null; } else st.start = Date.now(); store("t10-clock", st); tick(); });
    rs.addEventListener("click", function () { st = { start: null, acc: 0 }; store("t10-clock", st); tick(); });
    fw.addEventListener("click", function () { st.acc += 5 * 60000; store("t10-clock", st); tick(); });
    function tick() {
      var t = el(), mm = Math.floor(t), ss = Math.floor((t - mm) * 60);
      time.textContent = Math.floor(mm / 60) + ":" + ("0" + mm % 60).slice(-2) + ":" + ("0" + ss).slice(-2);
      go.textContent = st.start ? "Pause" : (t > 0 ? "Resume" : "▶ Start 3-hour session");
      var label = "";
      rows.forEach(function (r) {
        var ab = r.getAttribute("data-t").split("-").map(Number), cur = t >= ab[0] && t < ab[1] && (st.start || t > 0);
        r.classList.toggle("cur", !!cur); r.classList.toggle("done", t >= ab[1]);
        if (cur) label = "Now: " + r.children[1].textContent + " · " + Math.ceil(ab[1] - t) + " min left in this block";
      });
      now.textContent = t >= 180 ? "Session complete." : label;
    }
    tick(); setInterval(tick, 1000);
  }

  /* ------------------------------------------------------------ boot */
  var W = { attn: wAttn, sqrt: wSqrt, heads: wHeads, pe: wPE, ln: wLN, trparams: wTrParams, unet: wUnet, dice: wDice, patch: wPatch, vitparams: wVitParams, resgrad: wResGrad, flow: wFlow, prompt: wPrompt, clock: wClock };
  function boot() {
    if (window.hljs) $$("pre code").forEach(function (b) { if (!b.dataset.highlighted) { hljs.highlightElement(b); } });
    splitCodeLines();
    mountFigs();
    $$("[data-widget]").forEach(function (m) { var fn = W[m.getAttribute("data-widget")]; if (fn) { try { fn(m); } catch (e) { m.textContent = "This interactive element could not start: " + e.message; } } });
    $$("[data-quiz]").forEach(mountQuiz); updateProg();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
