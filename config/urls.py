"""URLs principais do projeto."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from curriculos.views import entrar_pagina_vendedor

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('parceiro/', include('accounts.urls')),
    path('curriculo/', include('curriculos.urls')),
    path('painel/', include('dashboard.urls')),
    path('p/<slug:slug>/', entrar_pagina_vendedor, name='pagina_vendedor'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
