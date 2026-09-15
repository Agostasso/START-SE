from django.contrib import admin
from .models import ( Faculdade, Curso, PerfilAcademico, Projecto)

# Register your models here.
@admin.register(Faculdade)
class FaculdadeAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'ativo',
    )

    search_fields = (
        'nome',
    )

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'faculdade',
        'ativo',
    )

    list_filter = (
        'faculdade',
        'ativo',
    )

    search_fields = (
        'nome',
    )


@admin.register(PerfilAcademico)
class PerfilAcademicoAdmin(admin.ModelAdmin):

    list_display = (
        'nome_completo',
        'numero_estudante',
        'curso',
        'estado_validacao',
        'atualizado_em',
    )

    list_filter = (
        'estado_validacao',
        'curso',
    )

    search_fields = (
        'nome_completo',
        'numero_estudante',
        'email_institucional',
    )

    readonly_fields = (
        'criado_em',
        'atualizado_em',
    )


@admin.register(Projecto)
class ProjectoAdmin(admin.ModelAdmin):

    list_display = (
        'titulo',
        'estudante',
        'estado',
        'captacao_encerrada',
        'submetido_em',
        'avaliado_em',
    )

    list_filter = (
        'estado',
        'captacao_encerrada',
        'submetido_em',
    )

    search_fields = (
        'titulo',
        'estudante__nome_completo',
        'estudante__numero_estudante',
    )

    readonly_fields = (
        'submetido_em',
        'atualizado_em',
    )

    actions = (
        'reabrir_captacao',
    )


    @admin.action(
    description='Reabrir captação dos projectos seleccionados'
    )
    def reabrir_captacao(
        self,
        request,
        queryset
    ):

        # Apenas projectos PUBLICADOS e com captação
        # encerrada podem ser reabertos.
        projectos = queryset.filter(
            estado=Projecto.EstadoProjecto.PUBLICADO,
            captacao_encerrada=True,
        )

        total = projectos.update(
            captacao_encerrada=False
        )


        if total > 0:

            self.message_user(
                request,
                f'{total} projecto(s) tiveram a captação reaberta com sucesso.'
            )

        else:

            self.message_user(
                request,
                'Nenhum dos projectos seleccionados pode ter a captação reaberta.'
            )