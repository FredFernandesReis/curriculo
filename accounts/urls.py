"""URLs da área do parceiro."""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.parceiro_login, name='login'),
    path('logout/', views.parceiro_logout, name='logout'),
    path('perfil/', views.parceiro_perfil, name='perfil'),
]
