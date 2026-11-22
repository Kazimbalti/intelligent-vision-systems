"""Lab 7 auto-checks and helpers: reading and implementing research papers.

Intelligent Vision Systems · Lecture 7 · Dr. Muhammad Kazim, University of Lahore.

Every ``check_*`` function prints ✅ when your code matches the paper (or PyTorch's own
implementation), or a 💡 hint telling you what to look at. The checks never print the answer:
use the hint, re-read the paper section it names, and try again.

Helpers you may use freely: ``trace_shapes`` (a shape table for any model), ``count_params``,
``make_reverse_batch``, ``make_shapes_dataset``, ``load_digits_tensors``, ``seed_everything``.
"""
import math
import random

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

_SCORE = {}


# ----------------------------------------------------------------------------------------------- helpers
def _ok(msg):
    print("✅ " + msg)
    return True


def _hint(msg):
    print("💡 " + msg)
    return False


def _close(a, b, tol=1e-5):
    return a.shape == b.shape and torch.allclose(a.float(), b.float(), atol=tol, rtol=1e-4)


def seed_everything(seed=0):
    """Same random numbers every run (Python, NumPy, PyTorch)."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def get_device():
    """'cuda' on a Colab GPU runtime, 'mps' on an Apple-silicon Mac, else 'cpu'."""
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def count_params(model, trainable_only=True):
    """Number of (trainable) parameters in a model."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad or not trainable_only)


def trace_shapes(model, x, max_rows=60):
    """Run ``x`` through ``model`` and print the output shape of every leaf layer.

    The single most useful debugging tool when you implement a paper: compare this table
    with the sizes printed in the paper's figure or table.
    """
    rows, hooks = [], []

    def hook(mod, inp, out):
        o = out[0] if isinstance(out, (tuple, list)) else out
        shape = tuple(o.shape) if torch.is_tensor(o) else type(o).__name__
        rows.append((mod._lab7_name, type(mod).__name__, shape, sum(p.numel() for p in mod.parameters(recurse=False))))

    for name, mod in model.named_modules():
        if len(list(mod.children())) == 0:
            mod._lab7_name = name
            hooks.append(mod.register_forward_hook(hook))
    try:
        with torch.no_grad():
            out = model(x)
    finally:
        for h in hooks:
            h.remove()
    print(f"{'layer':38s} {'type':18s} {'output shape':26s} {'params':>10s}")
    print("-" * 96)
    for r in rows[:max_rows]:
        print(f"{r[0][:38]:38s} {r[1][:18]:18s} {str(r[2]):26s} {r[3]:>10,d}")
    if len(rows) > max_rows:
        print(f"... {len(rows) - max_rows} more layers")
    print("-" * 96)
    o = out[0] if isinstance(out, (tuple, list)) else out
    print(f"input {tuple(x.shape)} -> output {tuple(o.shape)} · total params {count_params(model):,d}")
    return out


def scoreboard():
    """Print the bug-hunt scoreboard (Lab 7G)."""
    n = len([k for k, v in _SCORE.items() if v])
    print(f"Bug hunt score: {n} / 8")
    for k in sorted(_SCORE):
        print(f"  bug {k}: {'✅ fixed' if _SCORE[k] else '❌ not yet'}")
    if n == 8:
        print("🏆 All eight bugs fixed. Show this to your teacher!")


# ============================================================================== 7A · PyTorch for papers
def check_batch(img):
    if not torch.is_tensor(img):
        return _hint("img must be a torch tensor: use torch.rand(...) or torch.randn(...).")
    if tuple(img.shape) != (8, 3, 32, 32):
        return _hint(f"img has shape {tuple(img.shape)}. PyTorch images are (batch, channels, height, width).")
    if img.dtype != torch.float32:
        return _hint("Use float32 (the default of torch.rand).")
    return _ok("A batch of 8 RGB 32 × 32 images: (B, C, H, W) = (8, 3, 32, 32).")


def check_conv_out(fn):
    cases = [(32, 3, 1, 1, 1, 32), (32, 3, 2, 1, 1, 16), (572, 3, 1, 0, 1, 570), (224, 16, 16, 0, 1, 14),
             (224, 7, 2, 3, 1, 112), (64, 3, 1, 2, 2, 64), (28, 5, 1, 0, 1, 24), (568, 2, 2, 0, 1, 284)]
    for n, k, s, p, d, want in cases:
        try:
            got = fn(n, k, s, p, d)
        except Exception as e:
            return _hint(f"conv_out raised {type(e).__name__}: {e}")
        if got != want:
            return _hint(f"conv_out(n={n}, k={k}, s={s}, p={p}, d={d}) gave {got}. Check the formula on the slide; "
                         "did you use floor division // and the dilation d·(k − 1)?")
    return _ok("conv_out is right for all 8 cases (including U-Net's 572 → 570 and ViT's 224 → 14).")


def check_conv_layer(layer):
    if not isinstance(layer, nn.Conv2d):
        return _hint("Make an nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding).")
    y = layer(torch.zeros(8, 3, 32, 32))
    if tuple(y.shape) != (8, 16, 16, 16):
        return _hint(f"Your layer maps (8, 3, 32, 32) to {tuple(y.shape)}. You need 16 output channels and half the size: "
                     "which stride does that? Then pick the padding so the formula gives exactly 16.")
    if layer.kernel_size != (3, 3):
        return _hint("Use a 3 × 3 kernel, as in almost every paper since VGG.")
    return _ok("(8, 3, 32, 32) → (8, 16, 16, 16) with a 3 × 3, stride-2 convolution.")


def check_to_tokens(fn):
    x = torch.randn(2, 5, 4, 3)
    try:
        t = fn(x)
    except Exception as e:
        return _hint(f"to_tokens raised {type(e).__name__}: {e}")
    if tuple(t.shape) != (2, 12, 5):
        return _hint(f"Got shape {tuple(t.shape)}; want (B, H·W, C) = (2, 12, 5).")
    ref = x.flatten(2).transpose(1, 2)
    if not torch.allclose(t, ref):
        return _hint("Right shape, wrong order of numbers. reshape() alone mixes channels and pixels: "
                     "flatten H and W first, then swap the last two axes (transpose / permute).")
    return _ok("(B, C, H, W) → (B, H·W, C): every pixel is now a token with C features. ViT and DETR start exactly like this.")


def check_tiny_mlp(model):
    if not isinstance(model, nn.Module):
        return _hint("TinyMLP must subclass nn.Module and define __init__ and forward.")
    y = model(torch.zeros(5, 2))
    if tuple(y.shape) != (5, 2):
        return _hint(f"model(x) for x of shape (5, 2) gave {tuple(y.shape)}; want (5, 2): 2 class scores per point.")
    n = count_params(model)
    if n != 2 * 32 + 32 + 32 * 32 + 32 + 32 * 2 + 2:
        return _hint(f"Your model has {n:,} parameters. Expected Linear(2→32), ReLU, Linear(32→32), ReLU, Linear(32→2).")
    return _ok(f"TinyMLP has {n:,} parameters, exactly as counted by hand.")


def check_trained(model, X, y):
    model.eval()
    with torch.no_grad():
        acc = (model(X).argmax(1) == y).float().mean().item()
    if acc < 0.95:
        return _hint(f"Accuracy {acc:.1%}. Train for more epochs or a higher learning rate, and check the 5 lines of the loop: "
                     "zero_grad → forward → loss → backward → step.")
    return _ok(f"Accuracy {acc:.1%} on the two moons. You can now train any model in a paper.")


# ============================================================================== 7B · Attention
def _ref_attention(q, k, v, mask=None):
    s = q @ k.transpose(-2, -1) / math.sqrt(q.size(-1))
    if mask is not None:
        s = s.masked_fill(~mask, float("-inf"))
    w = s.softmax(-1)
    return w @ v, w


def check_softmax(fn):
    x = torch.tensor([[1.0, 2.0, 3.0], [1000.0, 1001.0, 1002.0], [-5.0, 0.0, 5.0]])
    try:
        y = fn(x)
    except Exception as e:
        return _hint(f"softmax raised {type(e).__name__}: {e}")
    if torch.isnan(y).any() or torch.isinf(y).any():
        return _hint("NaN/inf for large inputs (1000, 1001, 1002). Subtract the row maximum before exp(): "
                     "softmax(x) = softmax(x − max(x)).")
    if not _close(y, x.softmax(-1)):
        return _hint("Values differ from torch.softmax. Divide by the sum over the LAST dimension (dim=-1, keepdim=True).")
    return _ok("Numerically stable softmax (works for 1000, 1001, 1002 too).")


def check_attention(fn):
    torch.manual_seed(1)
    q, k, v = torch.randn(2, 5, 8), torch.randn(2, 7, 8), torch.randn(2, 7, 4)
    try:
        out = fn(q, k, v)
    except Exception as e:
        return _hint(f"attention raised {type(e).__name__}: {e}")
    out, w = out if isinstance(out, tuple) else (out, None)
    if tuple(out.shape) != (2, 5, 4):
        return _hint(f"Output shape {tuple(out.shape)}; Q is (2, 5, 8), K (2, 7, 8), V (2, 7, 4), so the output must be (2, 5, 4). "
                     "Use k.transpose(-2, -1), not k.T.")
    ref, rw = _ref_attention(q, k, v)
    if not _close(out, ref, 1e-4):
        q2 = q @ k.transpose(-2, -1)
        if _close(out, q2.softmax(-1) @ v, 1e-4):
            return _hint("You forgot to divide by √d_k (Eq. 1). Without it the softmax saturates when d_k is large.")
        if _close(out, (q2 / 8).softmax(-1) @ v, 1e-4):
            return _hint("You divided by d_k. The paper divides by the SQUARE ROOT of d_k (math.sqrt).")
        if _close(out, (q2 / math.sqrt(8)).softmax(-2) @ v, 1e-4):
            return _hint("Softmax over the wrong axis: each query's weights over the keys must sum to 1 → dim=-1.")
        return _hint("Output differs from Attention(Q,K,V) = softmax(QKᵀ/√d_k)·V. Do it in that order.")
    if w is not None and not _close(w, rw, 1e-4):
        return _hint("Output is right but the returned weights are not the softmax matrix.")
    ref2 = F.scaled_dot_product_attention(q, k, v)
    assert torch.allclose(ref2, ref, atol=1e-4)
    return _ok("Your attention matches Eq. 1 of the paper and torch.nn.functional.scaled_dot_product_attention.")


def check_attention_mask(fn):
    torch.manual_seed(2)
    q, k, v = torch.randn(1, 4, 8), torch.randn(1, 4, 8), torch.randn(1, 4, 8)
    mask = torch.tril(torch.ones(4, 4, dtype=torch.bool))
    try:
        out = fn(q, k, v, mask)
    except Exception as e:
        return _hint(f"attention(q, k, v, mask) raised {type(e).__name__}: {e}")
    out, w = out if isinstance(out, tuple) else (out, None)
    ref, rw = _ref_attention(q, k, v, mask)
    if torch.isnan(out).any():
        return _hint("NaNs: a whole row was masked. Use masked_fill(~mask, float('-inf')) only where mask is False.")
    if not _close(out, ref, 1e-4):
        return _hint("Masked positions must get −inf BEFORE the softmax (so their weight becomes exactly 0). "
                     "mask == True means 'may attend'.")
    return _ok("Masking works: masked keys get weight 0.")


def check_causal_mask(fn):
    try:
        m = fn(5)
    except Exception as e:
        return _hint(f"causal_mask raised {type(e).__name__}: {e}")
    want = torch.tril(torch.ones(5, 5, dtype=torch.bool))
    if not torch.is_tensor(m) or m.dtype != torch.bool:
        return _hint("Return a bool tensor (True = may attend).")
    if tuple(m.shape) != (5, 5):
        return _hint(f"Shape {tuple(m.shape)}; want (L, L) = (5, 5).")
    if torch.equal(m, ~want):
        return _hint("Inverted: True must mean 'may attend'. Position i may look at positions 0 … i.")
    if torch.equal(m, torch.tril(torch.ones(5, 5, dtype=torch.bool), -1)):
        return _hint("A token must be allowed to attend to ITSELF: keep the diagonal.")
    if not torch.equal(m, want):
        return _hint("Row i should be True for columns 0 … i and False after: a lower-triangular matrix (torch.tril).")
    return _ok("Causal mask: lower-triangular, diagonal included. The decoder cannot peek at the future.")


def check_mha(cls):
    torch.manual_seed(3)
    d, h = 32, 4
    try:
        mine = cls(d, h)
    except Exception as e:
        return _hint(f"MultiHeadAttention(32, 4) raised {type(e).__name__}: {e}")
    names = ["w_q", "w_k", "w_v", "w_o"]
    for n in names:
        if not isinstance(getattr(mine, n, None), nn.Linear):
            return _hint(f"Keep the attribute names from the template: self.{n} = nn.Linear(d_model, d_model).")
    ref = nn.MultiheadAttention(d, h, batch_first=True)
    with torch.no_grad():
        W, b = ref.in_proj_weight, ref.in_proj_bias
        for i, n in enumerate(names[:3]):
            getattr(mine, n).weight.copy_(W[i * d:(i + 1) * d]); getattr(mine, n).bias.copy_(b[i * d:(i + 1) * d])
        mine.w_o.weight.copy_(ref.out_proj.weight); mine.w_o.bias.copy_(ref.out_proj.bias)
    x, y = torch.randn(2, 6, d), torch.randn(2, 9, d)
    try:
        out = mine(x, y, y)
    except Exception as e:
        return _hint(f"forward(q, k, v) raised {type(e).__name__}: {e}. Print the shapes after every line.")
    out = out[0] if isinstance(out, tuple) else out
    want, _ = ref(x, y, y)
    if tuple(out.shape) != (2, 6, d):
        return _hint(f"Output shape {tuple(out.shape)}; want (2, 6, 32).")
    if not _close(out, want, 1e-4):
        return _hint("Shapes are right but numbers differ from nn.MultiheadAttention. Most common bug: "
                     ".view(B, L, h, d_k) must be followed by .transpose(1, 2) to get (B, h, L, d_k), and undone "
                     "before the final w_o (transpose back, then .reshape(B, L, d_model)).")
    p = count_params(mine)
    return _ok(f"Identical to torch.nn.MultiheadAttention ({p:,} parameters = 4 × (32·32 + 32)).")


# ============================================================================== 7C · Transformer
def _ref_pe(max_len, d):
    pe = torch.zeros(max_len, d)
    pos = torch.arange(max_len).unsqueeze(1).float()
    div = torch.exp(torch.arange(0, d, 2).float() * (-math.log(10000.0) / d))
    pe[:, 0::2] = torch.sin(pos * div)
    pe[:, 1::2] = torch.cos(pos * div)
    return pe


def check_positional_encoding(fn):
    try:
        pe = fn(50, 16)
    except Exception as e:
        return _hint(f"positional_encoding raised {type(e).__name__}: {e}")
    pe = pe.squeeze(0) if pe.dim() == 3 else pe
    if tuple(pe.shape) != (50, 16):
        return _hint(f"Shape {tuple(pe.shape)}; want (max_len, d_model) = (50, 16).")
    ref = _ref_pe(50, 16)
    if _close(pe, ref, 1e-4):
        return _ok("PE(pos, 2i) = sin(pos / 10000^(2i/d)), PE(pos, 2i+1) = cos(...): exactly §3.5 of the paper.")
    sw = ref.clone(); sw[:, 0::2], sw[:, 1::2] = ref[:, 1::2], ref[:, 0::2]
    if _close(pe, sw, 1e-4):
        return _hint("sin and cos are swapped: EVEN dimensions (0, 2, 4 …) use sin, ODD ones use cos.")
    if torch.allclose(pe[0, 0::2], torch.zeros(8)) and not torch.allclose(pe[1], ref[1], atol=1e-4):
        return _hint("Row 0 looks right but later rows differ: the exponent is 2i/d_model, where 2i is the even "
                     "dimension index (0, 2, 4 …), not the dimension index itself.")
    return _hint("Values differ from the formula in §3.5. Print pe[1, :4] and compute those 4 numbers by hand.")


def check_layernorm(cls):
    torch.manual_seed(4)
    try:
        ln = cls(10)
    except Exception as e:
        return _hint(f"LayerNorm(10) raised {type(e).__name__}: {e}")
    x = torch.randn(3, 7, 10) * 5 + 2
    try:
        y = ln(x)
    except Exception as e:
        return _hint(f"forward raised {type(e).__name__}: {e}")
    ref = nn.LayerNorm(10)
    if count_params(ln) != 20:
        return _hint("LayerNorm(10) needs 20 parameters: gamma (ones) and beta (zeros), each nn.Parameter of size 10.")
    if not _close(y, ref(x), 1e-4):
        if _close(y, (x - x.mean(-1, keepdim=True)) / x.std(-1, keepdim=True), 1e-3):
            return _hint("Close! x.std() uses the unbiased (N−1) estimate; use var(-1, unbiased=False) and add eps INSIDE the sqrt.")
        return _hint("Normalise over the LAST dimension (features), not the batch: mean and var with dim=-1, keepdim=True.")
    return _ok("Your LayerNorm equals nn.LayerNorm (Ba et al., 2016), as used after every sub-layer.")


def check_ffn(cls):
    try:
        f = cls(64, 256)
    except Exception as e:
        return _hint(f"FeedForward(64, 256) raised {type(e).__name__}: {e}")
    y = f(torch.randn(2, 5, 64))
    if tuple(y.shape) != (2, 5, 64):
        return _hint(f"Output shape {tuple(y.shape)}: the FFN must return d_model features (Eq. 2).")
    want = 64 * 256 + 256 + 256 * 64 + 64
    if count_params(f) != want:
        return _hint(f"{count_params(f):,} parameters; Eq. 2 has two linear layers with biases: d_model→d_ff→d_model = {want:,}.")
    return _ok("FFN(x) = max(0, xW₁ + b₁)W₂ + b₂ applied to every position separately (Eq. 2).")


def check_encoder_layer(cls):
    torch.manual_seed(5)
    try:
        layer = cls(32, 4, 64, 0.0)
    except Exception as e:
        return _hint(f"EncoderLayer(32, 4, 64, 0.0) raised {type(e).__name__}: {e}")
    x = torch.randn(2, 6, 32)
    y = layer(x, None)
    if tuple(y.shape) != (2, 6, 32):
        return _hint(f"Output {tuple(y.shape)}; an encoder layer keeps the shape (B, L, d_model).")
    mask = torch.ones(2, 1, 1, 6, dtype=torch.bool); mask[:, :, :, -2:] = False
    x2 = x.clone(); x2[:, -2:] += 10
    y1, y2 = layer(x, mask), layer(x2, mask)
    if not torch.allclose(y1[:, :4], y2[:, :4], atol=1e-4):
        return _hint("With a padding mask the real tokens must not change when the padded tokens change. Pass the mask to self-attention.")
    want = 4 * (32 * 32 + 32) + (32 * 64 + 64 + 64 * 32 + 32) + 2 * 64
    if count_params(layer) != want:
        return _hint(f"{count_params(layer):,} parameters; expected {want:,} (attention + FFN + two LayerNorms).")
    return _ok("Encoder layer = x + Attn(x) → Norm → x + FFN(x) → Norm, with the padding mask respected.")


def check_decoder_layer(cls):
    torch.manual_seed(6)
    try:
        layer = cls(32, 4, 64, 0.0)
    except Exception as e:
        return _hint(f"DecoderLayer(32, 4, 64, 0.0) raised {type(e).__name__}: {e}")
    layer.eval()
    y, mem = torch.randn(1, 5, 32), torch.randn(1, 7, 32)
    causal = torch.tril(torch.ones(5, 5, dtype=torch.bool)).view(1, 1, 5, 5)
    out = layer(y, mem, None, causal)
    if tuple(out.shape) != (1, 5, 32):
        return _hint(f"Output {tuple(out.shape)}; want (1, 5, 32).")
    y2 = y.clone(); y2[:, 3:] += 5
    out2 = layer(y2, mem, None, causal)
    if not torch.allclose(out[:, :3], out2[:, :3], atol=1e-4):
        return _hint("Changing FUTURE tokens (positions 3, 4) changed positions 0–2: the causal mask is not used in the "
                     "masked self-attention.")
    mem2 = mem + 1
    if torch.allclose(layer(y, mem2, None, causal), out, atol=1e-4):
        return _hint("The output ignores the encoder memory: the 2nd attention must use queries from the decoder and "
                     "keys/values from the encoder (cross-attention).")
    return _ok("Decoder layer: masked self-attention → cross-attention to the encoder → FFN, each with Add & Norm.")


def check_transformer(model, src_vocab=13, tgt_vocab=13):
    model.eval()
    src = torch.randint(3, src_vocab, (2, 10))
    tgt = torch.randint(3, tgt_vocab, (2, 11))
    try:
        out = model(src, tgt)
    except Exception as e:
        return _hint(f"model(src, tgt) raised {type(e).__name__}: {e}")
    if tuple(out.shape) != (2, 11, tgt_vocab):
        return _hint(f"Output {tuple(out.shape)}; want (batch, tgt_len, tgt_vocab) = (2, 11, {tgt_vocab}): one score per word.")
    tgt2 = tgt.clone(); tgt2[:, 6:] = 3
    out2 = model(src, tgt2)
    if not torch.allclose(out[:, :6], out2[:, :6], atol=1e-4):
        return _hint("Prediction at position i depends on target tokens after i: make the causal mask in forward().")
    return _ok(f"Full Transformer: (2, 10) source + (2, 11) target → (2, 11, {tgt_vocab}) scores · {count_params(model):,} parameters.")


def make_reverse_batch(batch_size=64, seq_len=10, vocab=10, device="cpu"):
    """A batch for the 'reverse the sequence' task.

    Tokens 0, 1, 2 are special: PAD = 0, BOS = 1 (start), EOS = 2 (end). Real digits are 3 … vocab+2.
    Returns src (B, L), tgt_in (B, L+1) = [BOS, reversed], tgt_out (B, L+1) = [reversed, EOS].
    """
    src = torch.randint(3, vocab + 3, (batch_size, seq_len), device=device)
    rev = src.flip(1)
    bos = torch.full((batch_size, 1), 1, device=device)
    eos = torch.full((batch_size, 1), 2, device=device)
    return src, torch.cat([bos, rev], 1), torch.cat([rev, eos], 1)


def check_reverse_accuracy(acc):
    if acc < 0.95:
        return _hint(f"Sequence accuracy {acc:.1%}. Train longer (more steps), check the learning rate (1e-3 to 2e-3 with Adam) and "
                     "that you feed tgt_in and compare with tgt_out (shifted right!).")
    return _ok(f"{acc:.1%} of whole sequences reversed perfectly. Your Transformer learned the task from data alone.")


# ============================================================================== 7D · U-Net
def check_double_conv(cls):
    try:
        b = cls(1, 64)
    except Exception as e:
        return _hint(f"DoubleConv(1, 64) raised {type(e).__name__}: {e}")
    y = b(torch.zeros(1, 1, 572, 572))
    if tuple(y.shape) == (1, 64, 572, 572):
        return _hint("Same size out: the PAPER uses unpadded ('valid') 3 × 3 convolutions, so each conv loses 2 pixels: padding=0.")
    if tuple(y.shape) != (1, 64, 568, 568):
        return _hint(f"(1, 1, 572, 572) → {tuple(y.shape)}; Fig. 1 says 568 × 568 with 64 channels after two 3 × 3 convs + ReLU.")
    n = count_params(b)
    if n != 1 * 64 * 9 + 64 + 64 * 64 * 9 + 64:
        return _hint(f"{n:,} parameters. Two Conv2d(…, 3) with bias, no BatchNorm in the 2015 paper.")
    return _ok("DoubleConv: 572 → 570 → 568, 64 channels, exactly as in Fig. 1.")


def check_center_crop(fn):
    x = torch.arange(1 * 1 * 8 * 8).float().view(1, 1, 8, 8)
    try:
        y = fn(x, 4)
    except Exception as e:
        return _hint(f"center_crop raised {type(e).__name__}: {e}")
    if tuple(y.shape) != (1, 1, 4, 4):
        return _hint(f"Got {tuple(y.shape)}; cropping 8 × 8 to 4 means (1, 1, 4, 4).")
    if not torch.equal(y, x[:, :, 2:6, 2:6]):
        return _hint("Right size, wrong place: start at (H − size) // 2 so the crop is in the CENTRE.")
    y2 = fn(torch.zeros(1, 512, 64, 64), 56)
    if tuple(y2.shape) != (1, 512, 56, 56):
        return _hint("Works for 8 → 4 but not 64 → 56; don't hard-code numbers.")
    return _ok("center_crop: 64² → 56², the grey 'copy and crop' arrow of Fig. 1.")


def check_unet_paper(model):
    try:
        y = model(torch.zeros(1, 1, 572, 572))
    except Exception as e:
        return _hint(f"UNetPaper()(1, 1, 572, 572) raised {type(e).__name__}: {e}. Use trace_shapes on a smaller part.")
    if tuple(y.shape) != (1, 2, 388, 388):
        return _hint(f"Output {tuple(y.shape)}; Fig. 1 ends with a 388 × 388 map and 2 classes.")
    n = count_params(model)
    if n != 31_030_658:
        return _hint(f"{n:,} parameters (expected about 31.0 M). Compare channel numbers level by level with Fig. 1: "
                     "64 → 128 → 256 → 512 → 1024, up-conv halves the channels, concat doubles them.")
    return _ok(f"Paper-exact U-Net: 572² → 388², {n:,} parameters (≈ 31.0 M).")


def make_shapes_dataset(n=600, size=64, seed=0, max_shapes=3, noise=0.15, draw_fn=None):
    """Synthetic segmentation data: grey images with circles, squares and triangles.

    Returns images (n, 1, size, size) float32 in [0, 1] and masks (n, size, size) int64 with
    0 = background, 1 = circle, 2 = square, 3 = triangle. ``draw_fn(img, mask, kind, cx, cy, r, value)``
    lets Lab 7D plug in the student's own drawing function.
    """
    import cv2
    rng = np.random.default_rng(seed)
    X = np.zeros((n, 1, size, size), np.float32)
    Y = np.zeros((n, size, size), np.int64)
    for i in range(n):
        img = np.full((size, size), rng.uniform(0.0, 0.35), np.float32)
        mask = np.zeros((size, size), np.uint8)          # OpenCV draws on uint8, not int64
        for _ in range(rng.integers(1, max_shapes + 1)):
            kind = int(rng.integers(1, 4))
            r = int(rng.integers(size // 10, size // 5))
            cx, cy = (int(v) for v in rng.integers(r, size - r, 2))
            val = float(rng.uniform(0.55, 1.0))
            if draw_fn is not None:
                draw_fn(img, mask, kind, cx, cy, r, val)
            elif kind == 1:
                cv2.circle(img, (cx, cy), r, val, -1)
                cv2.circle(mask, (cx, cy), r, 1, -1)
            elif kind == 2:
                cv2.rectangle(img, (cx - r, cy - r), (cx + r, cy + r), val, -1)
                cv2.rectangle(mask, (cx - r, cy - r), (cx + r, cy + r), 2, -1)
            else:
                pts = np.array([[cx, cy - r], [cx - r, cy + r], [cx + r, cy + r]], np.int32)
                cv2.fillPoly(img, [pts], val)
                cv2.fillPoly(mask, [pts], 3)
        img = img + rng.normal(0, noise, img.shape).astype(np.float32)
        X[i, 0] = np.clip(img, 0, 1)
        Y[i] = mask
    return torch.from_numpy(X), torch.from_numpy(Y)


def check_dataset(draw_fn):
    X0, Y0 = make_shapes_dataset(n=40, size=64, seed=123)
    try:
        X1, Y1 = make_shapes_dataset(n=40, size=64, seed=123, draw_fn=draw_fn)
    except Exception as e:
        return _hint(f"draw_shape raised {type(e).__name__}: {e}")
    if not torch.equal(Y0, Y1):
        cls_bad = [c for c in (1, 2, 3) if not torch.equal(Y0 == c, Y1 == c)]
        names = {1: "circle", 2: "square", 3: "triangle"}
        return _hint("Masks differ for: " + ", ".join(names[c] for c in cls_bad) +
                     ". The square goes from (cx − r, cy − r) to (cx + r, cy + r) and its mask label is 2.")
    if not torch.allclose(X0, X1, atol=1e-5):
        return _hint("Masks are right but the image is not: draw the shape into img with brightness `value` as well.")
    return _ok("Your draw_shape makes exactly the same images and masks as the reference generator.")


def overfit_one_batch(model, x, y, loss_fn, steps=200, lr=1e-3):
    """The #1 sanity check for a new implementation: can it memorise ONE batch?

    If the loss does not go close to zero, there is a bug (wrong mask, wrong shapes, detached graph,
    wrong loss) — no amount of data or training time will fix it.
    """
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    model.train()
    first = None
    for i in range(steps):
        opt.zero_grad()
        loss = loss_fn(model(x), y)
        loss.backward()
        opt.step()
        first = loss.item() if first is None else first
    print(f"loss: start {first:.4f} → after {steps} steps {loss.item():.4f}")
    if loss.item() < 0.1 * first:
        return _ok("The model can memorise one batch: the plumbing works.")
    return _hint("The model cannot even memorise one batch: look for a shape, mask or loss bug before training on real data.")


def check_dice(fn):
    pred = torch.tensor([[0, 1, 1], [0, 1, 0], [2, 2, 0]])
    true = torch.tensor([[0, 1, 0], [0, 1, 1], [2, 0, 0]])
    try:
        d = float(fn(pred, true, 1))
        d2 = float(fn(pred, true, 2))
        d3 = float(fn(pred, true, 3))
    except Exception as e:
        return _hint(f"dice raised {type(e).__name__}: {e}")
    if abs(d - 2 * 2 / (3 + 3)) > 1e-4:
        return _hint(f"dice(class 1) = {d:.3f}; by hand: |A∩B| = 2, |A| = 3, |B| = 3 → 2·2/(3+3) = 0.667.")
    if abs(d2 - 2 * 1 / (2 + 1)) > 1e-4:
        return _hint(f"dice(class 2) = {d2:.3f}; expected 0.667. Compare (pred == c) with (true == c).")
    if math.isnan(d3) or abs(d3 - 1.0) > 1e-4:
        return _hint("When a class is absent from BOTH masks, return 1.0 (nothing to find, nothing found), not NaN.")
    return _ok("Dice = 2|A∩B| / (|A| + |B|), the standard segmentation score (also used for the U-Net leaderboard).")


def check_unet_dice(mean_dice):
    if mean_dice < 0.85:
        return _hint(f"Mean Dice {mean_dice:.3f}. Train a few more epochs, check that the loss is CrossEntropyLoss on raw "
                     "logits (B, 4, H, W) vs masks (B, H, W) of type long, and that you used model.eval() for testing.")
    return _ok(f"Mean Dice {mean_dice:.3f} on unseen images. Your U-Net segments circles, squares and triangles.")


# ============================================================================== 7E · ResNet
def check_basic_block(cls):
    try:
        b1, b2 = cls(64, 64, 1), cls(64, 128, 2)
    except Exception as e:
        return _hint(f"BasicBlock(in, out, stride) raised {type(e).__name__}: {e}")
    y1 = b1(torch.randn(2, 64, 16, 16))
    if tuple(y1.shape) != (2, 64, 16, 16):
        return _hint(f"BasicBlock(64, 64, 1) gave {tuple(y1.shape)}; it must keep the shape.")
    try:
        y2 = b2(torch.randn(2, 64, 16, 16))
    except Exception as e:
        return _hint(f"BasicBlock(64, 128, 2) raised {type(e).__name__}: {e}. When the shape changes, the shortcut needs a "
                     "1 × 1 conv with stride 2 (+ BatchNorm) so that F(x) + x can be added.")
    if tuple(y2.shape) != (2, 128, 8, 8):
        return _hint(f"BasicBlock(64, 128, 2) gave {tuple(y2.shape)}; want (2, 128, 8, 8).")
    if (y1 < 0).any():
        return _hint("Negative outputs: the final ReLU comes AFTER the addition F(x) + x (Fig. 2).")
    want = 2 * (64 * 64 * 9) + 4 * 64
    if count_params(b1) != want:
        return _hint(f"{count_params(b1):,} params for BasicBlock(64, 64); expected {want:,}: two 3 × 3 convs WITHOUT bias "
                     "(BatchNorm has its own shift) + two BatchNorms.")
    return _ok("BasicBlock: two 3 × 3 conv-BN layers, identity or 1 × 1 projection shortcut, ReLU after the add.")


def check_resnet(model, depth=18):
    want = {18: 11_689_512, 34: 21_797_672, 50: 25_557_032}[depth]
    try:
        y = model(torch.zeros(1, 3, 224, 224))
    except Exception as e:
        return _hint(f"model(1, 3, 224, 224) raised {type(e).__name__}: {e}")
    if tuple(y.shape) != (1, 1000):
        return _hint(f"Output {tuple(y.shape)}; ImageNet ResNets end with 1000 class scores.")
    n = count_params(model)
    if n != want:
        return _hint(f"{n:,} parameters; torchvision's resnet{depth} has {want:,}. Check Table 1: blocks per stage "
                     f"{'[2, 2, 2, 2]' if depth == 18 else '[3, 4, 6, 3]'}, channels 64/128/256/512, the 7 × 7 stem, "
                     "convs without bias.")
    return _ok(f"ResNet-{depth}: {n:,} parameters, identical to torchvision.models.resnet{depth}().")


def load_digits_tensors(test_size=0.2, seed=0, size=8):
    """scikit-learn's 8 × 8 handwritten digits (1,797 images, bundled, no download) as tensors.

    Returns Xtr, ytr, Xte, yte with X of shape (N, 1, size, size) in [0, 1].
    """
    from sklearn.datasets import load_digits
    d = load_digits()
    X = torch.tensor(d.images, dtype=torch.float32).unsqueeze(1) / 16.0
    y = torch.tensor(d.target, dtype=torch.long)
    if size != 8:
        X = F.interpolate(X, size=(size, size), mode="bilinear", align_corners=False)
    g = torch.Generator().manual_seed(seed)
    idx = torch.randperm(len(X), generator=g)
    n_te = int(len(X) * test_size)
    te, tr = idx[:n_te], idx[n_te:]
    return X[tr], y[tr], X[te], y[te]


# ============================================================================== 7F · ViT
def check_patchify(fn):
    x = torch.arange(2 * 3 * 8 * 8).float().view(2, 3, 8, 8)
    try:
        p = fn(x, 4)
    except Exception as e:
        return _hint(f"patchify raised {type(e).__name__}: {e}")
    if tuple(p.shape) != (2, 4, 48):
        return _hint(f"Got {tuple(p.shape)}; an 8 × 8 RGB image with 4 × 4 patches gives N = 4 patches of P²·C = 48 numbers.")
    ref = F.unfold(x, 4, stride=4).transpose(1, 2)        # (B, N, C*P*P), channel-major
    ref_cl = x.unfold(2, 4, 4).unfold(3, 4, 4).permute(0, 2, 3, 4, 5, 1).reshape(2, 4, 48)  # (B, N, P*P*C)
    if torch.equal(p, ref) or torch.equal(p, ref_cl):
        return _ok("patchify: (B, C, H, W) → (B, N, P²·C), real square patches in row-major order (Eq. 1 of ViT).")
    if torch.equal(p, x.reshape(2, 4, 48)):
        return _hint("A plain reshape cuts the image into horizontal STRIPES, not squares. Split H and W into "
                     "(H/P, P) and (W/P, P) first, then permute so the two patch-index axes come first.")
    return _hint("Right shape, wrong content. Patch 0 must be the top-left 4 × 4 square of all channels. "
                 "Compare p[0, 0] with x[0, :, :4, :4].")


def check_patch_embed(cls):
    try:
        pe = cls(224, 16, 3, 768)
    except Exception as e:
        return _hint(f"PatchEmbedding(224, 16, 3, 768) raised {type(e).__name__}: {e}")
    y = pe(torch.zeros(2, 3, 224, 224))
    if tuple(y.shape) != (2, 196, 768):
        return _hint(f"Got {tuple(y.shape)}; 224/16 = 14 → 14 × 14 = 196 patches of dimension D = 768.")
    if count_params(pe) != 3 * 16 * 16 * 768 + 768:
        return _hint(f"{count_params(pe):,} parameters; one linear map from P²·C = 768 numbers to D = 768 (+ bias) = 590,592.")
    return _ok("Patch embedding: a 16 × 16 conv with stride 16 = 'linear projection of flattened patches'.")


def check_vit_b16(model):
    try:
        y = model(torch.zeros(1, 3, 224, 224))
    except Exception as e:
        return _hint(f"ViT-B/16 forward raised {type(e).__name__}: {e}")
    if tuple(y.shape) != (1, 1000):
        return _hint(f"Output {tuple(y.shape)}; want (1, 1000).")
    n = count_params(model)
    if n != 86_567_656:
        return _hint(f"{n:,} parameters; ViT-B/16 (Table 1: L = 12, D = 768, MLP = 3072, heads = 12) has 86,567,656 "
                     "in torchvision. Did you include the [class] token, 197 position embeddings and a final LayerNorm?")
    return _ok(f"ViT-B/16: {n:,} parameters (the '86M' of Table 1), identical to torchvision.models.vit_b_16().")


def check_vit_accuracy(acc):
    if acc < 0.90:
        return _hint(f"Test accuracy {acc:.1%}. ViTs need more data/epochs than CNNs: train longer, use AdamW with "
                     "lr ≈ 1e-3 and weight decay, and check that you classify from the [class] token (x[:, 0]).")
    return _ok(f"Tiny ViT: {acc:.1%} test accuracy on handwritten digits, from patches alone.")


# ============================================================================== 7G · Bug hunt
def _bug(i, ok, good, bad):
    _SCORE[i] = bool(ok)
    return _ok(f"Bug {i} fixed: {good}") if ok else _hint(f"Bug {i}: {bad}")


def check_bug1(fn):
    torch.manual_seed(11)
    q, k, v = torch.randn(2, 4, 64), torch.randn(2, 4, 64), torch.randn(2, 4, 64)
    ok = _close(fn(q, k, v), _ref_attention(q, k, v)[0], 1e-4)
    return _bug(1, ok, "scale by 1/√d_k.", "compare the scaling with Eq. 1, letter by letter.")


def check_bug2(fn):
    torch.manual_seed(12)
    q, k, v = torch.randn(2, 4, 8), torch.randn(2, 6, 8), torch.randn(2, 6, 8)
    try:
        ok = _close(fn(q, k, v), _ref_attention(q, k, v)[0], 1e-4)
    except Exception:
        ok = False
    return _bug(2, ok, "softmax over the keys (dim = -1).", "each query's weights must sum to 1. Over which axis?")


def check_bug3(fn):
    m = fn(4)
    ok = torch.is_tensor(m) and torch.equal(m, torch.tril(torch.ones(4, 4, dtype=torch.bool)))
    return _bug(3, ok, "a token may attend to itself and the past.", "print the mask. Can token 0 see anything at all?")


def check_bug4(cls):
    torch.manual_seed(13)
    try:
        m = cls(16, 4)
        x = torch.randn(2, 5, 16)
        out = m(x)
        ref = nn.MultiheadAttention(16, 4, batch_first=True, bias=False)
        with torch.no_grad():
            ref.in_proj_weight.copy_(torch.cat([m.w_q.weight, m.w_k.weight, m.w_v.weight]))
            ref.out_proj.weight.copy_(m.w_o.weight)
        ok = _close(out, ref(x, x, x)[0], 1e-4)
    except Exception:
        ok = False
    return _bug(4, ok, "split heads with view + transpose (and undo it).",
                "a .view() straight to (B, h, L, d_k) mixes tokens and heads. Print a tiny example.")


def check_bug5(cls):
    try:
        up = cls(64, 32)
        y = up(torch.randn(2, 64, 8, 8), torch.randn(2, 32, 16, 16))
        ok = tuple(y.shape) == (2, 32, 16, 16)
    except Exception:
        ok = False
    return _bug(5, ok, "concatenate skip and upsampled maps along channels (dim = 1).",
                "torch.cat(..., dim=?) — which axis are the channels in (B, C, H, W)?")


def check_bug6(cls):
    try:
        b = cls(32, 64, 2)
        y = b(torch.randn(2, 32, 8, 8))
        ok = tuple(y.shape) == (2, 64, 4, 4) and (y >= 0).all().item()
    except Exception:
        ok = False
    return _bug(6, ok, "projection shortcut when the shape changes, ReLU after the add.",
                "when stride = 2 or channels change, x cannot be added as is. And where is the last ReLU?")


def check_bug7(fn):
    x = torch.arange(1 * 2 * 4 * 4).float().view(1, 2, 4, 4)
    try:
        p = fn(x, 2)
        ref = x.unfold(2, 2, 2).unfold(3, 2, 2).permute(0, 2, 3, 4, 5, 1).reshape(1, 4, 8)
        ok = torch.equal(p, ref)
    except Exception:
        ok = False
    return _bug(7, ok, "patches are real P × P squares.", "print p[0, 0] and x[0, :, :2, :2]. Are they the same numbers?")


def check_bug8(fn):
    import copy
    torch.manual_seed(14)
    model = nn.Linear(3, 1)
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    X, y = torch.randn(32, 3), torch.randn(32, 1)
    try:
        fn(model, opt, X, y)                      # step 1
        before = copy.deepcopy(model)             # weights before step 2
        fn(model, opt, X, y)                      # step 2: its gradient must be computed at `before` only
        F.mse_loss(before(X), y).backward()
        ok = torch.allclose(model.weight.grad, before.weight.grad, atol=1e-5)
    except Exception:
        ok = False
    return _bug(8, ok, "zero the gradients every step.", "PyTorch ADDS new gradients to old ones. What must happen before backward()?")
