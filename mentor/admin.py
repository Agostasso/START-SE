from django.contrib import admin
from .models import Mentor


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
