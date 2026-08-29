"""
Lecture 6 - Gradio demo for a trained classifier (deploy to Hugging Face Spaces).

Loads a torchvision backbone fine-tuned on your classes and serves a web UI.
To deploy: push this file + requirements.txt + your weights to a new HF Space
(SDK = Gradio). The Space builds and hosts it for free.

Install: pip install gradio torch torchvision pillow
Usage (local): python gradio_classifier.py
"""
import gradio as gr
import torch
import torch.nn as nn
from torchvision import models, transforms

CLASSES = ["classA", "classB", "classC"]   # <-- edit to your classes
WEIGHTS = "classifier_resnet18.pt"          # <-- your fine-tuned weights

tfm = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


def build_model():
    m = models.resnet18(weights=None)
    m.fc = nn.Linear(m.fc.in_features, len(CLASSES))
    try:
        m.load_state_dict(torch.load(WEIGHTS, map_location="cpu"))
    except FileNotFoundError:
        print(f"WARNING: {WEIGHTS} not found; running with random weights.")
    m.eval()
    return m


model = build_model()


def predict(img):
    x = tfm(img).unsqueeze(0)
    with torch.no_grad():
        probs = model(x).softmax(1)[0]
    return {CLASSES[i]: float(probs[i]) for i in range(len(CLASSES))}


demo = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil"),
    outputs=gr.Label(num_top_classes=3),
    title="Applied CV — Image Classifier",
    description="Upload an image to classify it with your fine-tuned model.",
)

if __name__ == "__main__":
    demo.launch()
