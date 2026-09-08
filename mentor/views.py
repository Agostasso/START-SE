from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from visitante import views 

from .models import Mentor


@login_required
def dashboard(request):

    # Verifica se o utilizador pertence ao grupo Mentor

    if not request.user.groups.filter(
        name='Mentor'
    ).exists():

        messages.error(
            request,
            'Não possui autorização para acessar a área do Mentor.'
        )

        return redirect(
            'escolher_area'
        )


    # Recupera o perfil do Mentor

    mentor = Mentor.objects.filter(
        usuario=request.user,
        ativo=True
    ).first()


    if not mentor:

        messages.error(
            request,
            'Perfil de Mentor não encontrado.'
        )

        return redirect(
            'escolher_area'
        )


    contexto = {

        'mentor':
            mentor,

    }


    return render(
        request,
        'mentor_dashboard.html',
        contexto
    )