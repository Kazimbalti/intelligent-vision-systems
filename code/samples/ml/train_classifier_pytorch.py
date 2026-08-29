"""
Lecture 5 - Minimal PyTorch image classifier (training tier: GPU / Colab).

Trains a small CNN on an ImageFolder-style dataset:
    data/train/<class_name>/*.jpg
    data/val/<class_name>/*.jpg

Install: pip install torch torchvision
Usage:   python train_classifier_pytorch.py --data data --epochs 10
"""
import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


class SmallCNN(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d(1),
        )
        self.head = nn.Linear(64, num_classes)

    def forward(self, x):
        x = self.features(x).flatten(1)
        return self.head(x)


def loaders(root, bs):
    tfm = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
    ])
    train = datasets.ImageFolder(f"{root}/train", tfm)
    val = datasets.ImageFolder(f"{root}/val", tfm)
    return (DataLoader(train, bs, shuffle=True),
            DataLoader(val, bs), train.classes)


def run_epoch(model, loader, crit, opt, dev, train):
    model.train() if train else model.eval()
    total, correct, loss_sum = 0, 0, 0.0
    torch.set_grad_enabled(train)
    for x, y in loader:
        x, y = x.to(dev), y.to(dev)
        out = model(x)
        loss = crit(out, y)
        if train:
            opt.zero_grad(); loss.backward(); opt.step()
        loss_sum += loss.item() * x.size(0)
        correct += (out.argmax(1) == y).sum().item()
        total += x.size(0)
    return loss_sum / total, correct / total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--bs", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    args = ap.parse_args()

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    train_dl, val_dl, classes = loaders(args.data, args.bs)
    model = SmallCNN(len(classes)).to(dev)
    crit = nn.CrossEntropyLoss()
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)

    print(f"Classes: {classes}  Device: {dev}")
    for ep in range(1, args.epochs + 1):
        tl, ta = run_epoch(model, train_dl, crit, opt, dev, True)
        vl, va = run_epoch(model, val_dl, crit, opt, dev, False)
        print(f"epoch {ep:02d}  train {ta:.3f}  val {va:.3f}")
    torch.save(model.state_dict(), "classifier.pt")
    print("Saved classifier.pt")


if __name__ == "__main__":
    main()
