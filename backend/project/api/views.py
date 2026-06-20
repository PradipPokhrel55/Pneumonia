import json
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from services.cnn_service import predict_pneumonia
from services.idempotency_service import get_cached_response, save_response
from services.rag_service import generate_answer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET'])
def rag_query(request):
    key = request.headers.get("Idempotency-Key")
    if not key:
        return Response({"error": "Idempotency-Key header is required"}, status=400)
    cached = get_cached_response(key)
    if cached:
        return JsonResponse(cached)
    query = request.GET.get("query")#yesma url parameter bata query lina milxa jasto ki url ma ?query=your_query lekhako hunxa
    if not query:
        return Response({"error": "Query parameter is required"}, status=400)
    answer = generate_answer(query)
    response = {"answer": answer, "cached": False}
    save_response(key, response)
    return JsonResponse(response)

@api_view(["POST"])
def createUser(request):
    data = request.data
    if not all(k in data for k in ("username", "password")):
        return Response({"error": "username and password are required"}, status=400)
    if User.objects.filter(username=data["username"]).exists():
        return Response({"error": "Username already exists"}, status=400)
    user = User.objects.create_user(username=data["username"], password=data["password"])
    return Response({"message": "User created successfully", "user_id": user.id})        


class PneumoniaPredictView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if "file" not in request.FILES:
            return Response({"error": "file required"}, status=400)

        result = predict_pneumonia(request.FILES["file"])
        if "error" in result:
            return Response(result, status=500)
        return Response(result)




