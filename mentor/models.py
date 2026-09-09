from django.db import models
from django.conf import settings


class Mentor(models.Model):

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil_mentor'
    )

    numero_funcionario = models.CharField(
        max_length=50,
        unique=True
    )

    departamento = models.CharField(
        max_length=150
    )

    especialidade = models.CharField(
        max_length=150
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

        if nome:
            return nome

        return self.usuario.username


class SessaoMentoria(models.Model):

    class Modalidade(models.TextChoices):

        ONLINE = 'ONLINE', 'Online'
        PRESENCIAL = 'PRESENCIAL', 'Presencial'


    class Estado(models.TextChoices):

        AGENDADA = 'AGENDADA', 'Agendada'
        CONCLUIDA = 'CONCLUIDA', 'Concluída'
        REAGENDADA = 'REAGENDADA', 'Reagendada'
        CANCELADA = 'CANCELADA', 'Cancelada'


    mentor = models.ForeignKey(
        Mentor,
        on_delete=models.CASCADE,
        related_name='sessoes'
    )

    projecto = models.ForeignKey(
        'estudante.Projecto',
        on_delete=models.CASCADE,
        related_name='sessoes_mentoria'
    )

    titulo = models.CharField(
        max_length=200
    )

    data_hora_inicio = models.DateTimeField()

    data_hora_fim = models.DateTimeField()

    modalidade = models.CharField(
        max_length=20,
        choices=Modalidade.choices,
        default=Modalidade.ONLINE
    )

    link_meet = models.URLField(
        blank=True
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.AGENDADA
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )


    def __str__(self):

        return (
            f'{self.projecto.titulo} - '
            f'{self.data_hora_inicio}'
        )