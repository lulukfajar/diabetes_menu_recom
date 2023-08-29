from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landingpage, name='landingpage'),
    path('input/', views.inputpage, name='inputpage'),
    path('menu/', views.menupage, name='menupage'),
]

