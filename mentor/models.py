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
