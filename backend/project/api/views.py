from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from transformers import pipeline
from .rag import generate_answer
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from PIL import Image
import torch
from torchvision import transforms
from .cnn import PneumoniaCNN

MODEL_PATH = "/Users/pradippokhrel/Desktop/Pneumonia/backend/project/model.pth"
qa_pipeline = pipeline("text-generation",model="gpt2")

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
    transforms.Resize((64, 64)),
    transforms.Grayscale(num_output_channels=1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


def rag_query(request):
    query = request.GET.get("query")
    if not query:
        return JsonResponse({"error": "Query parameter is required."}, status=400)
    context = "Pneumonia is a lung infection."
    result = qa_pipeline(f"Q: {query}\nContext: {context}\nAnswer:", max_length=200, num_return_sequences=1)
    answer = result[0]['generated_text'].split("Answer:")[-1].strip()
    return JsonResponse({"answer": answer})

@api_view(['POST'])
def createUser(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data['username']
            password = data['password']
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({"detail": "Invalid request body."}, status=400)

        if not username or not password:
            return JsonResponse({"detail": "Username and password are required."}, status=400)
            
        try:
            User.objects.get(username=username)
            return JsonResponse({"detail": "Username already exists."}, status=409) # ✅ Use 409 Conflict
        except User.DoesNotExist:
            User.objects.create_user(username=username, password=password) # ✅ Corrected typo
            return JsonResponse({"detail": "User created successfully."}, status=201) # ✅ Use 201 Created

# --- API View ---
class PneumoniaPredictView(APIView):
    permission_classes = [IsAuthenticated] # ✅ Correct: Add permission class
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        if model is None:
            return Response({"error": "Model not loaded."}, status=500)

        if 'file' not in request.FILES:
            return Response({"error": "No file provided."}, status=400)

        try:
            file = request.FILES['file']
            print(f"Received file: {file.name}")

            image = Image.open(file).convert("RGB")
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
                    return Response({"error": "Unexpected model output."}, status=500)

            print(f"Prediction: {result}, Confidence: {prob}")
            return Response({"prediction": result, "confidence": prob})

        except Exception as e:
            print(f"Prediction error: {str(e)}")
            return Response({"error": f"Prediction failed: {str(e)}"}, status=500)