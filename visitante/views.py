from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import Group, User
from django.contrib import auth, messages
from django.contrib.messages import constants
from estudante.models import Projecto


# Create your views here.

def home(request): 
    if request.method == 'GET':
        return render (request, 'home.html')

def marketplace(request):

    # =====================================================
    # STARTUPS VISÍVEIS NO MARKETPLACE
    #
    # Só aparecem projectos:
    # 1. PUBLICADOS;
    # 2. cuja captação ainda não foi encerrada.
    # =====================================================

    startups = (
        Projecto.objects
        .filter(
            estado=Projecto.EstadoProjecto.PUBLICADO,
            captacao_encerrada=False,
        )
        .select_related(
            'estudante',
            'estudante__curso',
            'estudante__curso__faculdade',
        )
        .order_by(
            '-atualizado_em',
            '-submetido_em',
        )
    )


    # =====================================================
    # ÁREAS DISPONÍVEIS NO FILTRO
    #
    # Utiliza directamente as choices definidas no modelo
    # Projecto, evitando manter uma lista fixa no HTML.
    # =====================================================

    areas = (
        Projecto.AreaAtuacao.choices
    )


    contexto = {
        'startups': startups,
        'areas': areas,
        'total_startups': startups.count(),
    }


    return render(
        request,
        'marketplace.html',
        contexto
    )


def startup_detalhe(request, id):

    # =====================================================
    # STARTUP PUBLICADA
    #
    # A página de detalhe continua acessível enquanto o
    # projecto estiver PUBLICADO.
    #
    # Se a captação estiver encerrada, a startup deixa de
    # aparecer no Marketplace, mas o detalhe continua
    # coerente caso alguém tenha guardado o endereço.
    # =====================================================

    startup = get_object_or_404(
        Projecto.objects
        .select_related(
            'estudante',
            'estudante__curso',
            'estudante__curso__faculdade',
        ),
        id=id,
        estado=Projecto.EstadoProjecto.PUBLICADO,
    )


    # =====================================================
    # PERFIL DO UTILIZADOR
    # =====================================================

    eh_investidor = False

    if request.user.is_authenticated:

        eh_investidor = (
            request.user.groups
            .filter(
                name='Patrocinador'
            )
            .exists()
        )


    # O investidor só pode manifestar novo interesse
    # enquanto a captação estiver aberta.

    pode_manifestar_interesse = (
        eh_investidor
        and not startup.captacao_encerrada
    )


    contexto = {
        'startup':
            startup,

        'eh_investidor':
            eh_investidor,

        'pode_manifestar_interesse':
            pode_manifestar_interesse,
    }


    return render(
        request,
        'startup_detalhe.html',
        contexto
    )


def login(request):
    if request.method == 'GET':
        return render(request, 'Login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = auth.authenticate(request, username=username, password=senha)
        if user:
            auth.login(request, user)
            return redirect('/visitante/escolher_area')
        
        messages.add_message(request, constants.ERROR, 'Usuario ou senha inválido')
        return redirect('/visitante/login')

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    
    elif request.method == "POST":
         username = request.POST.get('username')
         senha = request.POST.get('senha')
         confirmar_senha = request.POST.get('confirmar_senha')
         tipo_usuario = request.POST.get('tipo_usuario')

         if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas não coincidem')
            return redirect('/visitante/cadastro')
 
         if len(senha) < 6:
             messages.add_message(request, constants.ERROR, 'A senha deve possuir pelomenos 6 caracteres')
             return redirect('/visitante/cadastro')
 
         users = User.objects.filter(username=username)
         if users.exists():
            messages.add_message(request, constants.ERROR, 'O usuário já existe')
            return redirect('/visitante/cadastro')
         
         messages.add_message(request, constants.SUCCESS, 'Cadastro feito com sucesso')

         user = User.objects.create_user(
            username=username,
            password=senha)

    if tipo_usuario == 'ESTUDANTE':
        grupo = Group.objects.get(name='Estudante')
        grupo.user_set.add(user)

    elif tipo_usuario == 'PATROCINADOR':
        grupo = Group.objects.get(name='Patrocinador')
        grupo.user_set.add(user)
        
    return redirect('/visitante/login')

@login_required
def escolher_area(request):

    # =====================================================
    # ADMINISTRADOR
    # =====================================================

    if request.user.is_superuser:

        return redirect(
            'admin:index'
        )


    # =====================================================
    # GRUPOS DO UTILIZADOR LOGADO
    # =====================================================

    grupos = set(
        request.user.groups.values_list(
            'name',
            flat=True
        )
    )


    # =====================================================
    # ÁREAS DISPONÍVEIS
    # =====================================================

    tem_perfil_estudante = (
        'Estudante' in grupos
    )

    tem_perfil_mentor = (
        'Mentor' in grupos
    )

    tem_perfil_patrocinador = (
        'Patrocinador' in grupos
    )


    # =====================================================
    # CONTEXTO
    # =====================================================

    contexto = {

        'tem_perfil_estudante':
            tem_perfil_estudante,

        'tem_perfil_mentor':
            tem_perfil_mentor,

        'tem_perfil_patrocinador':
            tem_perfil_patrocinador,
    }


    return render(request, 'escolher_area.html', contexto)