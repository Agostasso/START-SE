from django.conf import settings
from django.db import models

# Create your models here.

class Faculdade(models.Model):

    nome = models.CharField(
        max_length=150,
        unique=True
    )

    ativo = models.BooleanField(
        default=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.nome


class Curso(models.Model):

    faculdade = models.ForeignKey(
        Faculdade,
        on_delete=models.PROTECT,
        related_name='cursos'
    )

    nome = models.CharField(
        max_length=150
    )

    ativo = models.BooleanField(
        default=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = (
            'faculdade',
            'nome'
        )

    def __str__(self):
        return self.nome


class PerfilAcademico(models.Model):

    class AnoAcademico(models.TextChoices):

        PRIMEIRO = '1', '1.º Ano'
        SEGUNDO = '2', '2.º Ano'
        TERCEIRO = '3', '3.º Ano'
        QUARTO = '4', '4.º Ano'
        QUINTO = '5', '5.º Ano'

        LICENCIADO = (
            'LICENCIADO',
            'Recém-licenciado'
        )


    class EstadoValidacao(models.TextChoices):

        INCOMPLETO = (
            'INCOMPLETO',
            'Incompleto'
        )

        PENDENTE = (
            'PENDENTE',
            'Pendente'
        )

        VALIDADO = (
            'VALIDADO',
            'Validado'
        )

        REJEITADO = (
            'REJEITADO',
            'Rejeitado'
        )


    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_academico'
    )


    nome_completo = models.CharField(
        max_length=200
    )


    numero_estudante = models.CharField(
        max_length=30,
        unique=True
    )


    curso = models.ForeignKey(
        Curso,
        on_delete=models.PROTECT,
        related_name='estudantes'
    )


    ano_academico = models.CharField(
        max_length=20,
        choices=AnoAcademico.choices
    )


    telefone = models.CharField(
        max_length=20
    )


    email_institucional = models.EmailField(
        unique=True
    )


    descricao_interesse = models.TextField(
        blank=True
    )


    comprovativo_academico = models.FileField(
        upload_to='estudante/comprovativos/',
        blank=True,
        null=True
    )


    estado_validacao = models.CharField(
        max_length=20,
        choices=EstadoValidacao.choices,
        default=EstadoValidacao.INCOMPLETO
    )


    observacao_validacao = models.TextField(
        blank=True
    )


    submetido_em = models.DateTimeField(
        null=True,
        blank=True
    )


    validado_em = models.DateTimeField(
        null=True,
        blank=True
    )


    criado_em = models.DateTimeField(
        auto_now_add=True
    )


    atualizado_em = models.DateTimeField(
        auto_now=True
    )


    def __str__(self):

        return (
            f'{self.nome_completo} - '
            f'{self.numero_estudante}'
        )


    def pode_submeter_projeto(self):

        return (
            self.estado_validacao
            ==
            self.EstadoValidacao.VALIDADO
        )

class Projecto(models.Model):

    class AreaAtuacao(models.TextChoices):

        FINTECH = 'FINTECH', 'Fintech'

        AGROTECH = 'AGROTECH', 'Agrotech'

        EDUTECH = 'EDUTECH', 'Edutech'

        HEALTHTECH = 'HEALTHTECH', 'Healthtech'

        PROPTECH_CONSTRUTECH = (
            'PROPTECH_CONSTRUTECH',
            'Proptech / Construtech'
        )

        RETAILTECH_LOGTECH = (
            'RETAILTECH_LOGTECH',
            'Retailtech / Logtech'
        )

        GREENTECH_CLEANTECH = (
            'GREENTECH_CLEANTECH',
            'Greentech / Cleantech'
        )

        GOVTECH = 'GOVTECH', 'Govtech'


    class EstadoProjecto(models.TextChoices):

        PENDENTE = (
            'PENDENTE',
            'Pendente de Avaliação'
        )

        APROVADO = (
            'APROVADO',
            'Aprovado'
        )

        REJEITADO = (
            'REJEITADO',
            'Rejeitado'
        )

        EM_INCUBACAO = (
            'EM_INCUBACAO',
            'Em Incubação'
        )

        PUBLICADO = (
            'PUBLICADO',
            'Publicado'
        )


    estudante = models.ForeignKey(
        'PerfilAcademico',
        on_delete=models.CASCADE,
        related_name='projectos'
    )


    titulo = models.CharField(
        max_length=200
    )


    area_atuacao = models.CharField(
        max_length=30,
        choices=AreaAtuacao.choices,
        blank=True
    )

    resumo_executivo = models.TextField()


    problema = models.TextField()


    solucao = models.TextField()


    modelo_negocio = models.TextField()

    equipa = models.TextField()


    anexo = models.FileField(
        upload_to='estudante/projectos/',
        blank=True,
        null=True
    )


    estado = models.CharField(
        max_length=20,
        choices=EstadoProjecto.choices,
        default=EstadoProjecto.PENDENTE
    )


    parecer_avaliacao = models.TextField(
        blank=True
    )


    submetido_em = models.DateTimeField(
        auto_now_add=True
    )


    avaliado_em = models.DateTimeField(
        null=True,
        blank=True
    )


    atualizado_em = models.DateTimeField(
        auto_now=True
    )


    mentor = models.ForeignKey(
    'mentor.Mentor',
    on_delete=models.SET_NULL,
    related_name='projectos',
    null=True,
    blank=True
    )


    captacao_encerrada = models.BooleanField(
    default=False
                )

    def __str__(self):

        return self.titulo


