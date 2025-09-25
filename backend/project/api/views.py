# backend/project/api/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from PIL import Image
import torch
from torchvision import transforms

from .cnn import PneumoniaCNN

MODEL_PATH = "/Users/pradippokhrel/Desktop/Pneumonia/backend/project/model.pth"

# --- Load model ---
model = None
try:
    model = PneumoniaCNN()
    state_dict = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
    model.load_state_dict(state_dict)
    print("✅ Loaded model from state_dict")
except Exception as e_state:
    print(f"⚠️ state_dict load failed: {e_state}")
    try:
        model = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
        print("✅ Loaded full model")
    except Exception as e_full:
        print(f"❌ Failed to load model: {e_full}")
        model = None

if model:
    model.eval()



transform = transforms.Compose([
    transforms.Resize((64, 64)),  # match model training
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

# --- API View ---
class PneumoniaPredictView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        if model is None:
            return Response({"error": "Model not loaded."}, status=500)

        if 'file' not in request.FILES:
            return Response({"error": "No file provided."}, status=400)

        try:
            file = request.FILES['file']
            print(f"Received file: {file.name}")  # Debugging

            # Open and preprocess image
            image = Image.open(file).convert("RGB")
            print(f"Original image size: {image.size}")  # Debugging
            image = transform(image).unsqueeze(0)
            print(f"Transformed image shape: {image.shape}")  # Debugging

            # Make prediction
            with torch.no_grad():
                output = model(image)
                print(f"Raw model output: {output}")  # Debugging

                if isinstance(output, torch.Tensor):
                    prob = torch.sigmoid(output).squeeze().item()
                    result = "Pneumonia" if prob > 0.5 else "Normal"
                else:
                    return Response({"error": "Unexpected model output."}, status=500)

            print(f"Prediction: {result}, Confidence: {prob}")  # Debugging
            return Response({"prediction": result, "confidence": prob})

        except Exception as e:
            print(f"Prediction error: {str(e)}")  # Debugging
            return Response({"error": f"Prediction failed: {str(e)}"}, status=500)
