from django.contrib import admin
from .models import Mentor, SessaoMentoria


@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):

    list_display = (
        'usuario',
        'numero_funcionario',
        'departamento',
        'especialidade',
        'ativo',
    )

    list_filter = (
        'ativo',
        'departamento',
    )

    search_fields = (
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'usuario__email',
        'numero_funcionario',
        'especialidade',
    )


@admin.register(SessaoMentoria)
class SessaoMentoriaAdmin(admin.ModelAdmin):

    list_display = (
        'projecto',
        'mentor',
        'data_hora_inicio',
        'modalidade',
        'estado',
    )

    list_filter = (
        'estado',
        'modalidade',
    )

    search_fields = (
        'projecto__titulo',
        'mentor__usuario__first_name',
        'mentor__usuario__last_name',
    )