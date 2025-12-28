from django.urls import path
from .views import PneumoniaPredictView, createUser, MyTokenObtainPairView , rag_query
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'), # ✅ Correct: Use MyTokenObtainPairView
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/create', createUser, name="createuser"),
    path('predict/', PneumoniaPredictView.as_view(), name='pneumonia-predict'),
    path("rag-query/",rag_query, name="rag_query"),
]