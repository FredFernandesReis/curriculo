"""Admin do Django para modelos."""
from django.contrib import admin
from clientes.models import Cliente
from curriculos.models import Curriculo, ExperienciaProfissional, Curso


class ExperienciaInline(admin.TabularInline):
    model = ExperienciaProfissional
    extra = 1


class CursoInline(admin.TabularInline):
    model = Curso
    extra = 1


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'email', 'telefone', 'cidade', 'criado_em']
    search_fields = ['nome_completo', 'email', 'telefone']

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Curriculo)
class CurriculoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'vendedor', 'status', 'criado_em', 'data_pagamento', 'data_envio']
    list_filter = ['status', 'vendedor', 'criado_em']
    search_fields = ['cliente__nome_completo', 'cliente__email', 'cliente__telefone']
    inlines = [ExperienciaInline, CursoInline]
    raw_id_fields = ['vendedor']

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
