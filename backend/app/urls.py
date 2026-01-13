from django.urls import path
from . import views

urlpatterns = [
    path('query/', views.query_endpoint, name='query_endpoint'),
]
