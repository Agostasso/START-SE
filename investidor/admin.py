from django.contrib import admin

# Register your models here.

from django.contrib import admin

from .models import (
    Investidor,
    ManifestacaoInteresse
)


# ==========================================================
# INVESTIDOR
# ==========================================================

@admin.register(Investidor)
class InvestidorAdmin(admin.ModelAdmin):

    list_display = (
        'usuario',
        'telefone',
        'ativo',
        'criado_em',
    )

    list_filter = (
        'ativo',
    )

    search_fields = (
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'usuario__email',
    )

# ==========================================================
# MANIFESTAÇÃO DE INTERESSE
# ==========================================================

@admin.register(ManifestacaoInteresse)
class ManifestacaoInteresseAdmin(admin.ModelAdmin):

    list_display = (
        'projecto',
        'investidor',
        'assunto',
        'estado',
        'enviada_em',
    )

    list_filter = (
        'assunto',
        'estado',
        'enviada_em',
    )

    search_fields = (
        'projecto__titulo',
        'investidor__usuario__username',
        'investidor__usuario__email',
        'mensagem',
        'contacto_direto',
    )

    readonly_fields = (
        'enviada_em',
        'atualizada_em',
    )