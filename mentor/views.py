from django.shortcuts import render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from estudante.models import Projecto
from .models import Mentor, SessaoMentoria


@login_required
def dashboard(request):

    # =====================================================
    # VERIFICAR PERMISSÃO
    # =====================================================

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


    # =====================================================
    # MENTOR LOGADO
    # =====================================================

    mentor = (
        Mentor.objects
        .filter(
            usuario=request.user,
            ativo=True
        )
        .first()
    )


    if not mentor:

        messages.error(
            request,
            'Perfil de Mentor não encontrado.'
        )

        return redirect(
            'escolher_area'
        )


    agora = timezone.now()


    # =====================================================
    # PROJECTOS ATRIBUÍDOS
    # =====================================================

    projectos = (
        Projecto.objects
        .filter(
            mentor=mentor
        )
        .select_related(
            'estudante',
            'estudante__curso'
        )
        .order_by(
            '-submetido_em'
        )
    )


    total_projectos = projectos.count()


    # =====================================================
    # MENTORIAS ACTIVAS
    # =====================================================

    mentorias_activas = (
        projectos
        .filter(
            estado__in=[
                Projecto.EstadoProjecto.APROVADO,
                Projecto.EstadoProjecto.EM_INCUBACAO,
            ]
        )
        .count()
    )

    # =====================================================
    # SESSÕES CONCLUÍDAS
    # =====================================================

    sessoes_realizadas = (
        SessaoMentoria.objects
        .filter(
            mentor=mentor,
            estado=SessaoMentoria.Estado.CONCLUIDA
        )
        .count()
    )


    # =====================================================
    # PRÓXIMA SESSÃO
    # =====================================================

    proxima_sessao = (
        SessaoMentoria.objects
        .filter(
            mentor=mentor,
            estado=SessaoMentoria.Estado.AGENDADA,
            data_hora_inicio__gte=agora
        )
        .select_related(
            'projecto'
        )
        .order_by(
            'data_hora_inicio'
        )
        .first()
    )


    # =====================================================
    # PROJECTOS PARA A TABELA
    # =====================================================

    projectos_dashboard = []


    for projecto in projectos[:5]:

        ultima_sessao = (
            projecto.sessoes_mentoria
            .filter(
                mentor=mentor,
                estado=SessaoMentoria.Estado.CONCLUIDA
            )
            .order_by(
                '-data_hora_inicio'
            )
            .first()
        )


        proxima_sessao_projecto = (
            projecto.sessoes_mentoria
            .filter(
                mentor=mentor,
                estado=SessaoMentoria.Estado.AGENDADA,
                data_hora_inicio__gte=agora
            )
            .order_by(
                'data_hora_inicio'
            )
            .first()
        )


        projectos_dashboard.append({

            'projecto':
                projecto,

            'ultima_sessao':
                ultima_sessao,

            'proxima_sessao':
                proxima_sessao_projecto,

        })

    # =====================================================
    # CONTEXTO
    # =====================================================

    contexto = {

        'mentor':
            mentor,

        'total_projectos':
            total_projectos,

        'mentorias_activas':
            mentorias_activas,

        'sessoes_realizadas':
            sessoes_realizadas,

        'proxima_sessao':
            proxima_sessao,

        'projectos_dashboard':
            projectos_dashboard,
    }


    return render(
        request,
        'mentor_dashboard.html',
        contexto
    )

@login_required
def projects(request):

    # =====================================================
    # VERIFICAR SE É MENTOR
    # =====================================================

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


    # =====================================================
    # MENTOR LOGADO
    # =====================================================

    mentor = (
        Mentor.objects
        .filter(
            usuario=request.user,
            ativo=True
        )
        .first()
    )


    if not mentor:

        messages.error(
            request,
            'Perfil de Mentor não encontrado.'
        )

        return redirect(
            'escolher_area'
        )


    agora = timezone.now()


    # =====================================================
    # TODOS OS PROJECTOS ATRIBUÍDOS
    # =====================================================

    todos_projectos = (
        Projecto.objects
        .filter(
            mentor=mentor
        )
        .select_related(
            'estudante',
            'estudante__curso',
            'estudante__curso__faculdade'
        )
        .order_by(
            '-submetido_em'
        )
    )


    # =====================================================
    # INDICADORES
    # =====================================================

    total_projectos = (
        todos_projectos.count()
    )


    em_validacao = (
        todos_projectos
        .filter(
            estado=Projecto.EstadoProjecto.PENDENTE
        )
        .count()
    )


    em_desenvolvimento = (
        todos_projectos
        .filter(
            estado__in=[
                Projecto.EstadoProjecto.APROVADO,
                Projecto.EstadoProjecto.EM_INCUBACAO,
            ]
        )
        .count()
    )


    concluidos = (
        todos_projectos
        .filter(
            estado=Projecto.EstadoProjecto.PUBLICADO
        )
        .count()
    )


    # =====================================================
    # PESQUISA
    # =====================================================

    pesquisa = request.GET.get(
        'q',
        ''
    ).strip()


    estado_filtro = request.GET.get(
        'estado',
        ''
    ).strip()


    projectos = todos_projectos


    if pesquisa:

        projectos = projectos.filter(

            Q(
                titulo__icontains=pesquisa
            )

            |

            Q(
                area_atuacao__icontains=pesquisa
            )

            |

            Q(
                estudante__nome_completo__icontains=pesquisa
            )

        )


    # =====================================================
    # FILTRO POR ESTADO
    # =====================================================

    estados_validos = [
        valor
        for valor, nome
        in Projecto.EstadoProjecto.choices
    ]


    if estado_filtro in estados_validos:

        projectos = projectos.filter(
            estado=estado_filtro
        )


    # =====================================================
    # PAGINAÇÃO
    # =====================================================

    paginator = Paginator(
        projectos,
        5
    )


    numero_pagina = request.GET.get(
        'page'
    )


    pagina = paginator.get_page(
        numero_pagina
    )


    # =====================================================
    # PRÓXIMA SESSÃO DE CADA PROJECTO
    # =====================================================

    projectos_lista = []


    for projecto in pagina.object_list:

        proxima_sessao = (
            SessaoMentoria.objects
            .filter(
                projecto=projecto,
                mentor=mentor,
                estado=SessaoMentoria.Estado.AGENDADA,
                data_hora_inicio__gte=agora
            )
            .order_by(
                'data_hora_inicio'
            )
            .first()
        )


        projectos_lista.append({

            'projecto':
                projecto,

            'proxima_sessao':
                proxima_sessao,

        })


    # =====================================================
    # CONTEXTO
    # =====================================================

    contexto = {

        'mentor':
            mentor,

        'total_projectos':
            total_projectos,

        'em_validacao':
            em_validacao,

        'em_desenvolvimento':
            em_desenvolvimento,

        'concluidos':
            concluidos,

        'projectos_lista':
            projectos_lista,

        'pagina':
            pagina,

        'pesquisa':
            pesquisa,

        'estado_filtro':
            estado_filtro,

        'estados_projecto':
            Projecto.EstadoProjecto.choices,

    }


    return render(
        request,
        'mentor_projectos.html',
        contexto
    )

def agenda(request):
    if request.method == 'GET':
        return render(request, 'mentor_agenda.html')

def acompanhamento(request):
    if request.method == 'GET':
        return render(request, 'mentor_acompanhamento.html')