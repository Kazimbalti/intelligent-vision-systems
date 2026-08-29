"""
Lecture 12 - CLIP: zero-shot classification + text->image visual search.

Two modes:
  classify : score one image against a list of text labels (zero-shot)
  search   : rank all images in a folder by similarity to a text query

Uses Hugging Face transformers CLIP (runs on CPU; faster on GPU/Colab).
Install: pip install torch transformers pillow
Usage:
    python 11_clip_visual_search.py classify --image cat.jpg \
        --labels "a cat" "a dog" "a drone"
    python 11_clip_visual_search.py search --folder images/ --query "a red car"
"""
import argparse
import glob
import os
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

MODEL = "openai/clip-vit-base-patch32"


def load():
    model = CLIPModel.from_pretrained(MODEL)
    proc = CLIPProcessor.from_pretrained(MODEL)
    model.eval()
    return model, proc


def classify(args):
    model, proc = load()
    image = Image.open(args.image).convert("RGB")
    inputs = proc(text=args.labels, images=image, return_tensors="pt",
                  padding=True)
    with torch.no_grad():
        out = model(**inputs)
    probs = out.logits_per_image.softmax(dim=1)[0].tolist()
    ranked = sorted(zip(args.labels, probs), key=lambda x: -x[1])
    print("Zero-shot scores:")
    for label, p in ranked:
        print(f"  {p:6.1%}  {label}")


def search(args):
    model, proc = load()
    paths = sorted(sum([glob.glob(os.path.join(args.folder, e))
                        for e in ("*.jpg", "*.jpeg", "*.png")], []))
    if not paths:
        raise SystemExit(f"No images in {args.folder}")

    # encode the text query once
    tin = proc(text=[args.query], return_tensors="pt", padding=True)
    with torch.no_grad():
        tfeat = model.get_text_features(**tin)
        tfeat = tfeat / tfeat.norm(dim=-1, keepdim=True)

    scores = []
    for p in paths:
        img = Image.open(p).convert("RGB")
        iin = proc(images=img, return_tensors="pt")
        with torch.no_grad():
            ifeat = model.get_image_features(**iin)
            ifeat = ifeat / ifeat.norm(dim=-1, keepdim=True)
        scores.append((p, float((ifeat @ tfeat.T).item())))

    print(f"Top matches for: '{args.query}'")
    for p, s in sorted(scores, key=lambda x: -x[1])[:10]:
        print(f"  {s:.3f}  {p}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("classify")
    c.add_argument("--image", required=True)
    c.add_argument("--labels", nargs="+", required=True)
    s = sub.add_parser("search")
    s.add_argument("--folder", required=True)
    s.add_argument("--query", required=True)
    args = ap.parse_args()
    {"classify": classify, "search": search}[args.cmd](args)


if __name__ == "__main__":
    main()
