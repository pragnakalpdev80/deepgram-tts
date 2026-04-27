from django.urls import path

from . import views

urlpatterns = [
   path('', views.SelectionView.as_view(), name='index'),
   path('connect/', views.ConnectView.as_view(), name='connect'),
]
