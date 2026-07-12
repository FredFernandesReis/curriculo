"""URLs do painel administrativo."""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('', views.dashboard_home, name='home'),
    path('solicitacoes/', views.lista_solicitacoes, name='lista'),
    path('curriculo/<int:pk>/', views.visualizar_curriculo, name='visualizar'),
    path('curriculo/<int:pk>/editar/', views.editar_curriculo, name='editar'),
    path('curriculo/<int:pk>/status/', views.alterar_status, name='alterar_status'),
    path('curriculo/<int:pk>/excluir/', views.excluir_curriculo, name='excluir'),
    path('curriculo/<int:pk>/pdf/', views.baixar_pdf, name='baixar_pdf'),
    path('curriculo/<int:pk>/regenerar-pdf/', views.regenerar_pdf, name='regenerar_pdf'),
    path('curriculo/<int:pk>/reenviar/', views.reenviar_pdf, name='reenviar'),
]
