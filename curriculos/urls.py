"""URLs do app curriculos."""
from django.urls import path
from . import views

app_name = 'curriculos'

urlpatterns = [
    path('criar/', views.criar_curriculo, name='criar'),
    path('salvar/', views.salvar_etapa, name='salvar'),
    path('experiencia/adicionar/', views.adicionar_experiencia, name='adicionar_experiencia'),
    path('experiencia/<int:pk>/remover/', views.remover_experiencia, name='remover_experiencia'),
    path('curso/adicionar/', views.adicionar_curso, name='adicionar_curso'),
    path('curso/<int:pk>/remover/', views.remover_curso, name='remover_curso'),
    path('finalizar/', views.finalizar_curriculo, name='finalizar'),
    path('preview/<int:pk>/', views.preview_curriculo, name='preview'),
    path('adquirir/<int:pk>/', views.whatsapp_adquirir, name='adquirir'),
]
