import torch
from PIL import Image
from torchvision import transforms
from ml.cnn import PneumoniaCNN
import os
from transformers import pipeline
from rest_framework.response import Response


MODEL_PATH = "/Users/pradippokhrel/Desktop/Pneumonia/backend/project/model.pth"
qa_pipeline = pipeline("text-generation",model="gpt2")

# --- Load model ---
model = None
try:
    model = PneumoniaCNN()
    state_dict = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
    model.load_state_dict(state_dict)
    print("Loaded model from state_dict")
except Exception as e_state:
    print(f"state_dict load failed: {e_state}")
    try:
        model = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
        print("Loaded full model")
    except Exception as e_full:
        print(f" Failed to load model: {e_full}")
        model = None

if model:
    model.eval()

transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])



def predict_pneumonia(image_file):
    if model is None:
        print("model not loaded")
        return {"error": "Model not loaded"}

    try:
        image = Image.open(image_file).convert("RGB")
        print(f"Original image size: {image.size}")
        image = transform(image).unsqueeze(0)
        print(f"Transformed image shape: {image.shape}")

        with torch.no_grad():
            output = model(image)
            print(f"Raw model output: {output}")

            if isinstance(output, torch.Tensor):
                prob = torch.sigmoid(output).squeeze().item()
                result = "Pneumonia" if prob > 0.5 else "Normal"
            else:
                return ({"error": "Unexpected model output."})

        print(f"Prediction: {result}, Confidence: {prob}")
        return ({"prediction": result, "confidence": prob})
        

    except Exception as e:
        # VERY IMPORTANT: prevent server crash
        import traceback
        traceback.print_exc()
        print("error is present")
        return {"error": str(e)}