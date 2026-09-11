from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from datetime import timedelta
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from estudante.models import Projecto
from .models import Mentor, SessaoMentoria, AtaMentoria
from django.urls import reverse


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

@login_required
def agenda(request):

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


    # =====================================================
    # DATAS
    # =====================================================

    hoje = timezone.localdate()

    inicio_semana = (
        hoje
        - timedelta(
            days=hoje.weekday()
        )
    )

    fim_semana = (
        inicio_semana
        + timedelta(days=6)
    )


    # =====================================================
    # ESTADOS QUE AINDA FAZEM PARTE DA AGENDA
    # =====================================================

    estados_agendados = [
        SessaoMentoria.Estado.AGENDADA,
        SessaoMentoria.Estado.REAGENDADA,
    ]


    # =====================================================
    # SESSÕES HOJE
    # =====================================================

    sessoes_hoje = (
        SessaoMentoria.objects
        .filter(
            mentor=mentor,
            estado__in=estados_agendados,
            data_hora_inicio__date=hoje
        )
        .count()
    )


    # =====================================================
    # SESSÕES DESTA SEMANA
    # =====================================================

    sessoes_semana = (
        SessaoMentoria.objects
        .filter(
            mentor=mentor,
            estado__in=estados_agendados,
            data_hora_inicio__date__range=(
                inicio_semana,
                fim_semana
            )
        )
        .count()
    )
    # =====================================================
    # REAGENDADAS
    # =====================================================

    sessoes_reagendadas = (
        SessaoMentoria.objects
        .filter(
            mentor=mentor,
            estado=SessaoMentoria.Estado.REAGENDADA
        )
        .count()
    )
    # =====================================================
    # CONCLUÍDAS NESTE MÊS
    # =====================================================

    sessoes_concluidas = (
        SessaoMentoria.objects
        .filter(
            mentor=mentor,
            estado=SessaoMentoria.Estado.CONCLUIDA,
            data_hora_inicio__year=hoje.year,
            data_hora_inicio__month=hoje.month
        )
        .count()
    )
    # =====================================================
    # CONTEXTO
    # =====================================================

    contexto = {

        'mentor':
            mentor,

        'sessoes_hoje':
            sessoes_hoje,

        'sessoes_semana':
            sessoes_semana,

        'sessoes_reagendadas':
            sessoes_reagendadas,

        'sessoes_concluidas':
            sessoes_concluidas,

        'inicio_semana':
            inicio_semana,

        'fim_semana':
            fim_semana,

    }
    return render(
        request,
        'mentor_agenda.html',
        contexto
    )

@login_required
def acompanhamento(request):

    # =====================================================
    # VERIFICAR PERMISSÃO
    # =====================================================
    if not request.user.groups.filter(name='Mentor').exists():
        messages.error(
            request,
            'Não possui autorização para acessar a área do Mentor.'
        )
        return redirect('escolher_area')

    # =====================================================
    # MENTOR LOGADO
    # =====================================================
    mentor = (
        Mentor.objects
        .filter(usuario=request.user, ativo=True)
        .first()
    )

    if not mentor:
        messages.error(request, 'Perfil de Mentor não encontrado.')
        return redirect('escolher_area')

    agora = timezone.now()

    # =====================================================
    # PROJECTOS / MENTORIAS ACTIVAS
    # =====================================================
    projectos_mentor = Projecto.objects.filter(mentor=mentor)

    mentorias_activas = projectos_mentor.filter(
        estado__in=[
            Projecto.EstadoProjecto.APROVADO,
            Projecto.EstadoProjecto.EM_INCUBACAO,
        ]
    ).count()

    # =====================================================
    # ATAS DO MENTOR
    # =====================================================
    atas = (
        AtaMentoria.objects
        .filter(sessao__mentor=mentor)
        .select_related(
            'sessao',
            'sessao__projecto',
            'sessao__projecto__estudante',
        )
    )

    atas_submetidas = (
        atas
        .filter(estado_ata=AtaMentoria.EstadoAta.SUBMETIDA)
        .order_by('-submetido_em', '-atualizado_em')
    )

    registos_feitos = atas_submetidas.count()

    # =====================================================
    # PROJECTOS EM RISCO
    # Considera o último registo SUBMETIDO de cada projecto.
    # =====================================================
    projectos_em_risco = 0

    for projecto in projectos_mentor:
        ultima_ata_projecto = (
            atas_submetidas
            .filter(sessao__projecto=projecto)
            .order_by('-submetido_em', '-atualizado_em')
            .first()
        )

        if (
            ultima_ata_projecto
            and ultima_ata_projecto.estado_projecto
            == AtaMentoria.EstadoProjecto.RISCO
        ):
            projectos_em_risco += 1

    # =====================================================
    # ÚLTIMA ACTUALIZAÇÃO
    # =====================================================
    ultima_ata = atas_submetidas.first()

    # =====================================================
    # MODO DE VISUALIZAÇÃO
    # ?visualizar=registos
    # =====================================================
    visualizar = request.GET.get('visualizar', '').strip()
    mostrar_registos = visualizar == 'registos'

    # =====================================================
    # SESSÃO SELECCIONADA
    # /mentor/acompanhamento/?sessao=3
    # =====================================================
    sessao_id = request.GET.get('sessao')
    sessao_seleccionada = None
    ata = None

    if sessao_id:
        sessao_seleccionada = get_object_or_404(
            SessaoMentoria.objects.select_related(
                'projecto',
                'projecto__estudante'
            ),
            id=sessao_id,
            mentor=mentor
        )

        ata = AtaMentoria.objects.filter(
            sessao=sessao_seleccionada
        ).first()

        # Sessão futura não pode receber Ata.
        # Ata já submetida continua acessível para consulta.
        if (
            sessao_seleccionada.data_hora_fim > agora
            and not (
                ata
                and ata.estado_ata == AtaMentoria.EstadoAta.SUBMETIDA
            )
        ):
            messages.error(
                request,
                'A ata só pode ser preenchida depois do término da sessão.'
            )
            return redirect('mentor_acompanhamento')

    # =====================================================
    # POST - GUARDAR / SUBMETER ATA
    # =====================================================
    if request.method == 'POST':
        sessao_id = request.POST.get('sessao_id')

        if not sessao_id:
            messages.error(request, 'Sessão de mentoria não informada.')
            return redirect('mentor_acompanhamento')

        sessao = get_object_or_404(
            SessaoMentoria.objects.select_related(
                'projecto',
                'projecto__estudante'
            ),
            id=sessao_id,
            mentor=mentor
        )

        agora_post = timezone.now()

        if sessao.data_hora_fim > agora_post:
            messages.error(
                request,
                'A ata só pode ser preenchida depois do término da sessão.'
            )
            return redirect(reverse('mentor_agenda'))

        ata_existente = AtaMentoria.objects.filter(sessao=sessao).first()

        if (
            ata_existente
            and ata_existente.estado_ata == AtaMentoria.EstadoAta.SUBMETIDA
        ):
            messages.error(
                request,
                'Esta ata já foi submetida e está disponível apenas para consulta.'
            )
            return redirect(
                reverse('mentor_acompanhamento') + f'?sessao={sessao.id}'
            )

        resumo = request.POST.get('resumo', '').strip()
        decisoes = request.POST.get('decisoes', '').strip()
        proximos_passos = request.POST.get('proximos_passos', '').strip()
        estado_projecto = request.POST.get('estado_projecto', '').strip()
        acao = request.POST.get('acao', '').strip()

        if acao not in ['rascunho', 'submeter']:
            messages.error(request, 'Acção inválida.')
            return redirect(
                reverse('mentor_acompanhamento') + f'?sessao={sessao.id}'
            )

        estados_validos = [
            valor
            for valor, nome in AtaMentoria.EstadoProjecto.choices
        ]

        if estado_projecto not in estados_validos:
            messages.error(
                request,
                'Seleccione um estado válido para o projecto.'
            )
            return redirect(
                reverse('mentor_acompanhamento') + f'?sessao={sessao.id}'
            )

        if acao == 'submeter' and (
            not resumo
            or not decisoes
            or not proximos_passos
        ):
            messages.error(
                request,
                'Preencha todos os campos obrigatórios antes de submeter a ata.'
            )
            return redirect(
                reverse('mentor_acompanhamento') + f'?sessao={sessao.id}'
            )

        ata, criada = AtaMentoria.objects.get_or_create(sessao=sessao)

        ata.resumo = resumo
        ata.decisoes = decisoes
        ata.proximos_passos = proximos_passos
        ata.estado_projecto = estado_projecto

        # =================================================
        # GUARDAR RASCUNHO
        # =================================================
        if acao == 'rascunho':
            ata.estado_ata = AtaMentoria.EstadoAta.RASCUNHO
            ata.save()

            messages.success(request, 'Rascunho guardado com sucesso.')
            return redirect(
                reverse('mentor_acompanhamento') + f'?sessao={sessao.id}'
            )

        # =================================================
        # SUBMETER ATA
        # =================================================
        ata.estado_ata = AtaMentoria.EstadoAta.SUBMETIDA
        ata.submetido_em = agora_post
        ata.save()

        # A sessão passa a CONCLUÍDA somente após a submissão da Ata.
        sessao.estado = SessaoMentoria.Estado.CONCLUIDA
        sessao.save(update_fields=['estado'])

        messages.success(
            request,
            'Ata de mentoria submetida com sucesso.'
        )

        return redirect(
            reverse('mentor_acompanhamento')
            + '?visualizar=registos#registos-atas'
        )

    # =====================================================
    # SESSÕES PENDENTES DE ATA
    # Inclui sessões já terminadas, mesmo que tenham sido
    # marcadas manualmente como CONCLUÍDAS, desde que não
    # possuam Ata SUBMETIDA.
    # =====================================================
    sessoes_pendentes_ata = (
        SessaoMentoria.objects
        .filter(
            mentor=mentor,
            data_hora_fim__lte=agora
        )
        .exclude(estado=SessaoMentoria.Estado.CANCELADA)
        .exclude(ata__estado_ata=AtaMentoria.EstadoAta.SUBMETIDA)
        .select_related(
            'projecto',
            'projecto__estudante'
        )
        .order_by('-data_hora_inicio')
    )

    # =====================================================
    # CONTEXTO
    # =====================================================
    contexto = {
        'mentor': mentor,
        'mentorias_activas': mentorias_activas,
        'registos_feitos': registos_feitos,
        'projectos_em_risco': projectos_em_risco,
        'ultima_atualizacao': ultima_ata,
        'sessao_seleccionada': sessao_seleccionada,
        'ata': ata,
        'estados_projecto': AtaMentoria.EstadoProjecto.choices,
        'sessoes_pendentes_ata': sessoes_pendentes_ata,
        'atas_submetidas': atas_submetidas,
        'mostrar_registos': mostrar_registos,
    }

    return render(
        request,
        'mentor_acompanhamento.html',
        contexto
    )

@login_required
def projecto_ficha(request, projecto_id):
    # =====================================================
    # VERIFICAR SE O UTILIZADOR É MENTOR
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
    # RECUPERAR O MENTOR LOGADO
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


    # =====================================================
    # RECUPERAR PROJECTO
    #
    # IMPORTANTE:
    # O PROJECTO PRECISA ESTAR ATRIBUÍDO AO MENTOR LOGADO.
    # =====================================================

    projecto = get_object_or_404(

        Projecto.objects.select_related(
            'estudante',
            'estudante__curso',
            'estudante__curso__faculdade'
        ),

        id=projecto_id,

        mentor=mentor

    )


    # =====================================================
    # SESSÕES DO PROJECTO
    # =====================================================

    sessoes = (
        SessaoMentoria.objects
        .filter(
            projecto=projecto,
            mentor=mentor
        )
        .order_by(
            '-data_hora_inicio'
        )
    )


    # =====================================================
    # PRÓXIMA SESSÃO
    # =====================================================

    agora = timezone.now()


    proxima_sessao = (
        sessoes
        .filter(
            estado=SessaoMentoria.Estado.AGENDADA,
            data_hora_inicio__gte=agora
        )
        .order_by(
            'data_hora_inicio'
        )
        .first()
    )


    # =====================================================
    # ÚLTIMA SESSÃO CONCLUÍDA
    # =====================================================

    ultima_sessao = (
        sessoes
        .filter(
            estado=SessaoMentoria.Estado.CONCLUIDA
        )
        .order_by(
            '-data_hora_inicio'
        )
        .first()
    )


    # =====================================================
    # TOTAL DE SESSÕES CONCLUÍDAS
    # =====================================================

    total_sessoes_concluidas = (
        sessoes
        .filter(
            estado=SessaoMentoria.Estado.CONCLUIDA
        )
        .count()
    )


    # =====================================================
    # CONTEXTO
    # =====================================================

    contexto = {

        'mentor':
            mentor,

        'projecto':
            projecto,

        'sessoes':
            sessoes,

        'proxima_sessao':
            proxima_sessao,

        'ultima_sessao':
            ultima_sessao,

        'total_sessoes_concluidas':
            total_sessoes_concluidas,

    }


    return render(
        request,
        'mentor_projecto_ficha.html',
        contexto
    )

@login_required
def novo_agendamento(request):

    # =====================================================
    # PERMISSÃO
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
    # MENTOR
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


    # =====================================================
    # PROJECTOS QUE PODEM RECEBER MENTORIA
    # =====================================================

    projectos = (
        Projecto.objects
        .filter(
            mentor=mentor,
            estado__in=[
                Projecto.EstadoProjecto.APROVADO,
                Projecto.EstadoProjecto.EM_INCUBACAO,
            ]
        )
        .order_by(
            'titulo'
        )
    )


    # =====================================================
    # POST
    # =====================================================

    if request.method == 'POST':

        projecto_id = request.POST.get(
            'projecto'
        )

        titulo = request.POST.get(
            'titulo',
            ''
        ).strip()

        data_hora_inicio = request.POST.get(
            'data_hora_inicio'
        )

        data_hora_fim = request.POST.get(
            'data_hora_fim'
        )

        modalidade = request.POST.get(
            'modalidade'
        )

        link_meet = request.POST.get(
            'link_meet',
            ''
        ).strip()


        # =================================================
        # CAMPOS OBRIGATÓRIOS
        # =================================================

        if (
            not projecto_id
            or not titulo
            or not data_hora_inicio
            or not data_hora_fim
            or not modalidade
        ):

            messages.error(
                request,
                'Preencha todos os campos obrigatórios.'
            )

            return redirect(
                'mentor_novo_agendamento'
            )


        # =================================================
        # PROJECTO PRECISA PERTENCER AO MENTOR
        # =================================================

        projecto = get_object_or_404(
            projectos,
            id=projecto_id
        )


        # =================================================
        # CONVERTER DATA/HORA
        # =================================================

        inicio = parse_datetime(
            data_hora_inicio
        )

        fim = parse_datetime(
            data_hora_fim
        )


        if not inicio or not fim:

            messages.error(
                request,
                'Informe uma data e hora válidas.'
            )

            return redirect(
                'mentor_novo_agendamento'
            )


        # =================================================
        # TORNAR AS DATAS CONSCIENTES DO FUSO HORÁRIO
        # =================================================

        if timezone.is_naive(inicio):

            inicio = timezone.make_aware(
                inicio
            )


        if timezone.is_naive(fim):

            fim = timezone.make_aware(
                fim
            )


        # =================================================
        # FIM PRECISA SER POSTERIOR AO INÍCIO
        # =================================================

        if fim <= inicio:

            messages.error(
                request,
                'A hora de término deve ser posterior à hora de início.'
            )

            return redirect(
                'mentor_novo_agendamento'
            )


        # =================================================
        # NÃO PERMITIR AGENDAR NO PASSADO
        # =================================================

        if inicio < timezone.now():

            messages.error(
                request,
                'Não é possível agendar uma sessão numa data passada.'
            )

            return redirect(
                'mentor_novo_agendamento'
            )


        # =================================================
        # VALIDAR MODALIDADE
        # =================================================

        modalidades_validas = [
            valor
            for valor, nome
            in SessaoMentoria.Modalidade.choices
        ]


        if modalidade not in modalidades_validas:

            messages.error(
                request,
                'Modalidade inválida.'
            )

            return redirect(
                'mentor_novo_agendamento'
            )


        # =================================================
        # VERIFICAR CONFLITO NA AGENDA
        # =================================================

        conflito = (
            SessaoMentoria.objects
            .filter(
                mentor=mentor,
                estado__in=[
                    SessaoMentoria.Estado.AGENDADA,
                    SessaoMentoria.Estado.REAGENDADA,
                ],
                data_hora_inicio__lt=fim,
                data_hora_fim__gt=inicio
            )
            .exists()
        )


        if conflito:

            messages.error(
                request,
                'Já existe uma sessão agendada nesse horário.'
            )

            return redirect(
                'mentor_novo_agendamento'
            )


        # =================================================
        # CRIAR SESSÃO
        # =================================================

        SessaoMentoria.objects.create(

            mentor=mentor,

            projecto=projecto,

            titulo=titulo,

            data_hora_inicio=inicio,

            data_hora_fim=fim,

            modalidade=modalidade,

            link_meet=link_meet,

            estado=SessaoMentoria.Estado.AGENDADA

        )


        messages.success(
            request,
            'Sessão de mentoria agendada com sucesso.'
        )


        return redirect(
            'mentor_agenda'
        )


    # =====================================================
    # GET
    # =====================================================

    contexto = {

        'mentor':
            mentor,

        'projectos':
            projectos,

        'modalidades':
            SessaoMentoria.Modalidade.choices,

    }


    return render(
        request,
        'mentor_novo_agendamento.html',
        contexto
    )