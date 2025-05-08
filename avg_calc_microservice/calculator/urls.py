from django.urls import path
from .views import NumberAPIView

urlpatterns = [
    path('<str:number_id>', NumberAPIView.as_view(), name='number-api'),
]
