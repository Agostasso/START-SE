from django.db import models
from django.conf import settings




# Create your models here.

# ==========================================================
# INVESTIDOR
# ==========================================================

class Investidor(models.Model):

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_investidor'
    )

    telefone = models.CharField(
        max_length=30,
        blank=True
    )

    ativo = models.BooleanField(
        default=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )


    def __str__(self):

        nome = self.usuario.get_full_name()

        return (
            nome
            if nome
            else self.usuario.username
        )


# ==========================================================
# MANIFESTAÇÃO DE INTERESSE
# ==========================================================

class ManifestacaoInteresse(models.Model):


    # ======================================================
    # ASSUNTO
    # ======================================================

    class Assunto(models.TextChoices):

        PARCERIA = (
            'PARCERIA',
            'Parceria'
        )

        INVESTIMENTO = (
            'INVESTIMENTO',
            'Investimento'
        )

        PATROCINIO = (
            'PATROCINIO',
            'Patrocínio'
        )


    # ======================================================
    # ESTADO
    # ======================================================

    class Estado(models.TextChoices):

        ENVIADA = (
            'ENVIADA',
            'Enviada'
        )

        EM_ANALISE = (
            'EM_ANALISE',
            'Em análise'
        )

        RESPONDIDA = (
            'RESPONDIDA',
            'Respondida'
        )


    class Decisao(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        ACEITE = 'ACEITE', 'Aceite'
        RECUSADA = 'RECUSADA', 'Recusada'


    # ======================================================
    # RELAÇÕES
    # ======================================================

    investidor = models.ForeignKey(
        Investidor,
        on_delete=models.CASCADE,
        related_name='manifestacoes'
    )


    projecto = models.ForeignKey(
        'estudante.Projecto',
        on_delete=models.CASCADE,
        related_name='manifestacoes_interesse'
    )


    # ======================================================
    # DADOS ENVIADOS PELO INVESTIDOR
    # ======================================================

    assunto = models.CharField(
        max_length=20,
        choices=Assunto.choices
    )


    mensagem = models.TextField()


    contacto_direto = models.CharField(
        max_length=150
    )


    # ======================================================
    # ACOMPANHAMENTO
    # ======================================================

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.ENVIADA
    )


    resposta = models.TextField(
        blank=True
    )


    respondida_em = models.DateTimeField(
        null=True,
        blank=True
    )


    decisao = models.CharField(
        max_length=20,
        choices=Decisao.choices,
        default=Decisao.PENDENTE
    )

    # ======================================================
    # DATAS
    # ======================================================

    enviada_em = models.DateTimeField(
        auto_now_add=True
    )


    atualizada_em = models.DateTimeField(
        auto_now=True
    )


    def __str__(self):

        return (
            f'{self.investidor} - '
            f'{self.projecto.titulo}'
        )