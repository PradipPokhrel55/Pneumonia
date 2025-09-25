from django.urls import path 
from .views import PneumoniaPredictView

urlpatterns = [
    path('predict/', PneumoniaPredictView.as_view(), name='pneumonia-predict'),
]
