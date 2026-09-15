
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import render, redirect , get_object_or_404
from django.http import HttpResponse
from .models import Faculdade, PerfilAcademico, Curso, Projecto
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from  mentor.models import SessaoMentoria, AtaMentoria
from investidor.models import ManifestacaoInteresse
from django.urls import reverse
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required



# Create your views here.

@login_required
def dashboard(request):

    # =====================================================
    # PERFIL DO ESTUDANTE LOGADO
    # =====================================================

    perfil = (
        PerfilAcademico.objects
        .filter(usuario=request.user)
        .select_related('curso', 'curso__faculdade')
        .first()
    )

    # =====================================================
    # VALORES INICIAIS
    # =====================================================

    estado_validacao = 'INCOMPLETO'
    estado_validacao_texto = 'Incompleto'

    projeto = None
    projeto_disponivel = False
    projeto_estado = 'Bloqueado'

    mentoria_estado = 'Não atribuída'

    progresso = 14

    total_interesses = 0
    interesses_novos = 0

    propostas_aceites = 0
    conexao_investidor_estado = 'Pendente'
    conexao_investidor_concluida = False

    # =====================================================
    # PERFIL ACADÉMICO
    # =====================================================

    if perfil:

        estado_validacao = perfil.estado_validacao
        estado_validacao_texto = perfil.get_estado_validacao_display()

        # =================================================
        # PERFIL VALIDADO
        # =================================================

        if (
            perfil.estado_validacao
            == PerfilAcademico.EstadoValidacao.VALIDADO
        ):

            projeto_disponivel = True
            projeto_estado = 'Disponível'
            progresso = 28

            # =============================================
            # PROJECTO MAIS RECENTE DO ESTUDANTE
            # =============================================

            projeto = (
                Projecto.objects
                .filter(estudante=perfil)
                .order_by('-submetido_em')
                .first()
            )

            # =============================================
            # PROJECTO SUBMETIDO
            # =============================================

            if projeto:

                projeto_estado = projeto.get_estado_display()
                progresso = 42

                # =========================================
                # PROJECTO APROVADO
                # =========================================

                if projeto.estado == Projecto.EstadoProjecto.APROVADO:
                    progresso = 57

                # =========================================
                # EM INCUBAÇÃO
                # =========================================

                elif projeto.estado == Projecto.EstadoProjecto.EM_INCUBACAO:
                    progresso = 71
                    mentoria_estado = 'Em incubação'

                # =========================================
                # PUBLICADO
                # =========================================

                elif projeto.estado == Projecto.EstadoProjecto.PUBLICADO:

                    progresso = 85
                    mentoria_estado = 'Concluída'

                    # =====================================
                    # INTERESSES RECEBIDOS
                    # =====================================

                    total_interesses = (
                        projeto.manifestacoes_interesse.count()
                    )

                    interesses_novos = (
                        projeto.manifestacoes_interesse
                        .filter(
                            estado=ManifestacaoInteresse.Estado.ENVIADA
                        )
                        .count()
                    )

                    # =====================================
                    # PROPOSTAS DE INVESTIMENTO ACEITES
                    # =====================================

                    propostas_aceites = (
                        projeto.manifestacoes_interesse
                        .filter(
                            assunto=ManifestacaoInteresse.Assunto.INVESTIMENTO,
                            decisao=ManifestacaoInteresse.Decisao.ACEITE
                        )
                        .count()
                    )

                    # =====================================
                    # ETAPA 7 - CONEXÃO COM INVESTIDOR
                    # =====================================

                    if projeto.captacao_encerrada:
                        conexao_investidor_estado = 'Concluído'
                        conexao_investidor_concluida = True
                        progresso = 100

                    elif propostas_aceites > 0:
                        conexao_investidor_estado = 'Em captação'
                        progresso = 85

                    else:
                        conexao_investidor_estado = 'Disponível'
                        progresso = 85

                # =========================================
                # REJEITADO
                # =========================================

                elif projeto.estado == Projecto.EstadoProjecto.REJEITADO:
                    progresso = 42

    # =====================================================
    # CONTEXTO
    # =====================================================

    contexto = {
        'perfil': perfil,
        'estado_validacao': estado_validacao,
        'estado_validacao_texto': estado_validacao_texto,
        'projeto': projeto,
        'projeto_disponivel': projeto_disponivel,
        'projeto_estado': projeto_estado,
        'mentoria_estado': mentoria_estado,
        'progresso': progresso,
        'total_interesses': total_interesses,
        'interesses_novos': interesses_novos,
        'propostas_aceites': propostas_aceites,
        'conexao_investidor_estado': conexao_investidor_estado,
        'conexao_investidor_concluida': conexao_investidor_concluida,
    }

    return render(
        request,
        'estudante_dashboard.html',
        contexto
    )


@login_required
def projeto(request):

    # =====================================================
    # PERFIL ACADÉMICO DO ESTUDANTE LOGADO
    # =====================================================

    perfil = (
        PerfilAcademico.objects
        .filter(usuario=request.user)
        .select_related('curso', 'curso__faculdade')
        .first()
    )

    # =====================================================
    # PROJECTO MAIS RECENTE DO ESTUDANTE
    # =====================================================

    projecto = None

    if perfil:
        projecto = (
            Projecto.objects
            .filter(estudante=perfil)
            .order_by('-submetido_em')
            .first()
        )

    # =====================================================
    # MANIFESTAÇÕES RECEBIDAS
    # =====================================================

    manifestacoes = ManifestacaoInteresse.objects.none()

    if (
        perfil
        and projecto
        and projecto.estado == Projecto.EstadoProjecto.PUBLICADO
    ):
        manifestacoes = (
            ManifestacaoInteresse.objects
            .filter(
                projecto=projecto,
                projecto__estudante=perfil
            )
            .select_related(
                'investidor',
                'investidor__usuario',
                'projecto'
            )
            .order_by('-atualizada_em', '-enviada_em')
        )

    # =====================================================
    # CONTADORES GERAIS
    # =====================================================

    total_interesses = manifestacoes.count()

    interesses_novos = (
        manifestacoes
        .filter(estado=ManifestacaoInteresse.Estado.ENVIADA)
        .count()
    )

    interesses_em_analise = (
        manifestacoes
        .filter(estado=ManifestacaoInteresse.Estado.EM_ANALISE)
        .count()
    )

    interesses_respondidos = (
        manifestacoes
        .filter(estado=ManifestacaoInteresse.Estado.RESPONDIDA)
        .count()
    )

    # =====================================================
    # CONTADORES DE INVESTIMENTO
    # =====================================================

    propostas_aceites = (
        manifestacoes
        .filter(
            assunto=ManifestacaoInteresse.Assunto.INVESTIMENTO,
            decisao=ManifestacaoInteresse.Decisao.ACEITE
        )
        .count()
    )

    propostas_recusadas = (
        manifestacoes
        .filter(
            assunto=ManifestacaoInteresse.Assunto.INVESTIMENTO,
            decisao=ManifestacaoInteresse.Decisao.RECUSADA
        )
        .count()
    )

    propostas_investimento_em_analise = (
        manifestacoes
        .filter(
            assunto=ManifestacaoInteresse.Assunto.INVESTIMENTO,
            estado=ManifestacaoInteresse.Estado.EM_ANALISE,
            decisao=ManifestacaoInteresse.Decisao.PENDENTE
        )
        .count()
    )

    # =====================================================
    # ABA ACTIVA
    # =====================================================

    secao_ativa = request.GET.get('secao', 'projecto').strip()

    if secao_ativa not in ['projecto', 'interesses']:
        secao_ativa = 'projecto'

    if (
        secao_ativa == 'interesses'
        and (
            not projecto
            or projecto.estado != Projecto.EstadoProjecto.PUBLICADO
        )
    ):
        secao_ativa = 'projecto'

    # =====================================================
    # MANIFESTAÇÃO SELECCIONADA
    # =====================================================

    manifestacao_id = request.GET.get('manifestacao')
    manifestacao_seleccionada = None

    if (
        secao_ativa == 'interesses'
        and manifestacao_id
        and manifestacao_id.isdigit()
    ):
        manifestacao_seleccionada = (
            manifestacoes
            .filter(id=int(manifestacao_id))
            .first()
        )

    if (
        secao_ativa == 'interesses'
        and manifestacao_seleccionada is None
        and manifestacoes.exists()
    ):
        manifestacao_seleccionada = manifestacoes.first()

    # =====================================================
    # POST - INTERAGIR COM MANIFESTAÇÕES / CAPTAÇÃO
    # =====================================================

    if request.method == 'POST':

        if (
            not perfil
            or not projecto
            or projecto.estado != Projecto.EstadoProjecto.PUBLICADO
        ):
            messages.error(
                request,
                'Não é possível gerir manifestações de interesse neste momento.'
            )
            return redirect('estudante_projeto')

        acao = request.POST.get('acao', '').strip()

        # =================================================
        # ENCERRAR CAPTAÇÃO
        # =================================================

        if acao == 'encerrar_captacao':

            tem_proposta_aceite = (
                projecto.manifestacoes_interesse
                .filter(
                    assunto=ManifestacaoInteresse.Assunto.INVESTIMENTO,
                    decisao=ManifestacaoInteresse.Decisao.ACEITE
                )
                .exists()
            )

            if projecto.captacao_encerrada:
                messages.info(
                    request,
                    'A captação de investimento já está encerrada.'
                )

            elif not tem_proposta_aceite:
                messages.error(
                    request,
                    'É necessário aceitar pelo menos uma proposta de investimento antes de encerrar a captação.'
                )

            else:
                projecto.captacao_encerrada = True
                projecto.save()

                messages.success(
                    request,
                    'Captação de investimento encerrada com sucesso.'
                )

            return redirect(
                reverse('estudante_projeto')
                + '?secao=interesses'
                + '#interesses-recebidos'
            )

        # =================================================
        # DAQUI PARA BAIXO É NECESSÁRIO manifestacao_id
        # =================================================

        manifestacao_id = request.POST.get('manifestacao_id')

        if not manifestacao_id:
            messages.error(
                request,
                'Manifestação de interesse não informada.'
            )
            return redirect(
                reverse('estudante_projeto')
                + '?secao=interesses'
            )

        manifestacao = get_object_or_404(
            ManifestacaoInteresse.objects.select_related(
                'projecto',
                'investidor',
                'investidor__usuario'
            ),
            id=manifestacao_id,
            projecto=projecto,
            projecto__estudante=perfil
        )

        url_manifestacao = (
            reverse('estudante_projeto')
            + '?secao=interesses'
            + f'&manifestacao={manifestacao.id}'
            + '#interesses-recebidos'
        )

        # =================================================
        # MARCAR COMO EM ANÁLISE
        # =================================================

        if acao == 'analisar':

            if manifestacao.estado == ManifestacaoInteresse.Estado.ENVIADA:
                manifestacao.estado = ManifestacaoInteresse.Estado.EM_ANALISE
                manifestacao.save()

                messages.success(
                    request,
                    'Manifestação marcada como Em análise.'
                )

            elif manifestacao.estado == ManifestacaoInteresse.Estado.EM_ANALISE:
                messages.info(
                    request,
                    'Esta manifestação já está em análise.'
                )

            else:
                messages.info(
                    request,
                    'Esta manifestação já foi respondida.'
                )

            return redirect(url_manifestacao)

        # =================================================
        # ACEITAR PROPOSTA DE INVESTIMENTO
        # =================================================

        elif acao == 'aceitar':

            if manifestacao.assunto != ManifestacaoInteresse.Assunto.INVESTIMENTO:
                messages.error(
                    request,
                    'A opção Aceitar proposta aplica-se apenas a manifestações de investimento.'
                )
                return redirect(url_manifestacao)

            if projecto.captacao_encerrada:
                messages.error(
                    request,
                    'A captação já está encerrada. Não é possível aceitar novas propostas de investimento.'
                )
                return redirect(url_manifestacao)

            if manifestacao.estado != ManifestacaoInteresse.Estado.EM_ANALISE:
                messages.error(
                    request,
                    'Marque primeiro a proposta como Em análise.'
                )
                return redirect(url_manifestacao)

            resposta = request.POST.get('resposta', '').strip()

            if not resposta:
                messages.error(
                    request,
                    'Escreva uma resposta antes de aceitar a proposta.'
                )
                return redirect(url_manifestacao)

            manifestacao.resposta = resposta
            manifestacao.estado = ManifestacaoInteresse.Estado.RESPONDIDA
            manifestacao.decisao = ManifestacaoInteresse.Decisao.ACEITE
            manifestacao.respondida_em = timezone.now()
            manifestacao.save()

            messages.success(
                request,
                'Proposta de investimento aceite com sucesso.'
            )

            return redirect(url_manifestacao)

        # =================================================
        # RECUSAR PROPOSTA DE INVESTIMENTO
        # =================================================

        elif acao == 'recusar':

            if manifestacao.assunto != ManifestacaoInteresse.Assunto.INVESTIMENTO:
                messages.error(
                    request,
                    'A opção Recusar proposta aplica-se apenas a manifestações de investimento.'
                )
                return redirect(url_manifestacao)

            if manifestacao.estado != ManifestacaoInteresse.Estado.EM_ANALISE:
                messages.error(
                    request,
                    'Marque primeiro a proposta como Em análise.'
                )
                return redirect(url_manifestacao)

            resposta = request.POST.get('resposta', '').strip()

            if not resposta:
                messages.error(
                    request,
                    'Escreva uma resposta explicando a decisão antes de recusar a proposta.'
                )
                return redirect(url_manifestacao)

            manifestacao.resposta = resposta
            manifestacao.estado = ManifestacaoInteresse.Estado.RESPONDIDA
            manifestacao.decisao = ManifestacaoInteresse.Decisao.RECUSADA
            manifestacao.respondida_em = timezone.now()
            manifestacao.save()

            messages.success(
                request,
                'Proposta de investimento recusada.'
            )

            return redirect(url_manifestacao)

        # =================================================
        # RESPONDER PARCERIA OU PATROCÍNIO
        # =================================================

        elif acao == 'responder':

            if manifestacao.assunto == ManifestacaoInteresse.Assunto.INVESTIMENTO:
                messages.error(
                    request,
                    'Para uma proposta de investimento, escolha Aceitar proposta ou Recusar proposta.'
                )
                return redirect(url_manifestacao)

            if manifestacao.estado != ManifestacaoInteresse.Estado.EM_ANALISE:
                messages.error(
                    request,
                    'Marque primeiro a manifestação como Em análise antes de responder.'
                )
                return redirect(url_manifestacao)

            resposta = request.POST.get('resposta', '').strip()

            if not resposta:
                messages.error(
                    request,
                    'Escreva uma resposta antes de enviar.'
                )
                return redirect(url_manifestacao)

            manifestacao.resposta = resposta
            manifestacao.estado = ManifestacaoInteresse.Estado.RESPONDIDA
            manifestacao.respondida_em = timezone.now()
            manifestacao.save()

            messages.success(
                request,
                'Resposta enviada ao Investidor com sucesso.'
            )

            return redirect(url_manifestacao)

        # =================================================
        # ACÇÃO INVÁLIDA
        # =================================================

        messages.error(
            request,
            'Acção inválida.'
        )

        return redirect(
            reverse('estudante_projeto')
            + '?secao=interesses'
        )

    # =====================================================
    # CONTEXTO
    # =====================================================

    contexto = {
        'perfil': perfil,
        'projecto': projecto,
        'secao_ativa': secao_ativa,
        'manifestacoes': manifestacoes,
        'manifestacao_seleccionada': manifestacao_seleccionada,
        'total_interesses': total_interesses,
        'interesses_novos': interesses_novos,
        'interesses_em_analise': interesses_em_analise,
        'interesses_respondidos': interesses_respondidos,
        'propostas_aceites': propostas_aceites,
        'propostas_recusadas': propostas_recusadas,
        'propostas_investimento_em_analise': propostas_investimento_em_analise,
        'captacao_encerrada': (
            projecto.captacao_encerrada
            if projecto
            else False
        ),
    }

    return render(
        request,
        'projeto.html',
        contexto
    )


@login_required
def perfil_academico(request):

    # =====================================================
    # FACULDADES E CURSOS
    # =====================================================

    faculdades = Faculdade.objects.filter(
        ativo=True
    ).order_by('nome')

    cursos = Curso.objects.filter(
        ativo=True
    ).select_related(
        'faculdade'
    ).order_by('nome')


    # =====================================================
    # PERFIL DO UTILIZADOR
    # =====================================================

    perfil = (
        PerfilAcademico.objects
        .filter(usuario=request.user)
        .select_related(
            'curso',
            'curso__faculdade'
        )
        .first()
    )

    perfil_novo = perfil is None


    # =====================================================
    # POST
    # =====================================================

    if request.method == 'POST':

        nome_completo = request.POST.get(
            'nome_completo'
        )

        numero_estudante = request.POST.get(
            'numero_estudante'
        )

        curso_id = request.POST.get(
            'curso'
        )

        faculdade_id = request.POST.get(
            'faculdade'
        )

        ano_academico = request.POST.get(
            'ano_academico'
        )

        telefone = request.POST.get(
            'telefone'
        )

        email_institucional = request.POST.get(
            'email_institucional'
        )

        descricao = request.POST.get(
            'descricao'
        )

        comprovativo = request.FILES.get(
            'comprovativo'
        )


        # =================================================
        # CAMPOS OBRIGATÓRIOS
        # =================================================

        if not all([
            nome_completo,
            numero_estudante,
            curso_id,
            faculdade_id,
            ano_academico,
            telefone,
            email_institucional,
        ]):

            messages.error(
                request,
                'Preencha todos os campos obrigatórios.'
            )

            return redirect(
                'perfil_academico'
            )


        # =================================================
        # CURSO
        # =================================================

        curso = get_object_or_404(
            Curso,
            id=curso_id,
            ativo=True
        )


        # =================================================
        # VALIDAR CURSO/FACULDADE
        # =================================================

        if str(curso.faculdade_id) != str(faculdade_id):

            messages.error(
                request,
                'O curso selecionado não pertence à faculdade informada.'
            )

            return redirect(
                'perfil_academico'
            )


        # =================================================
        # NÚMERO DE ESTUDANTE DUPLICADO
        # =================================================

        numero_existente = (
            PerfilAcademico.objects
            .filter(
                numero_estudante=numero_estudante
            )
            .exclude(
                usuario=request.user
            )
            .exists()
        )

        if numero_existente:

            messages.error(
                request,
                'Já existe um estudante com este número.'
            )

            return redirect(
                'perfil_academico'
            )


        # =================================================
        # E-MAIL INSTITUCIONAL DUPLICADO
        # =================================================

        email_existente = (
            PerfilAcademico.objects
            .filter(
                email_institucional=email_institucional
            )
            .exclude(
                usuario=request.user
            )
            .exists()
        )

        if email_existente:

            messages.error(
                request,
                'Este e-mail institucional já está registado.'
            )

            return redirect(
                'perfil_academico'
            )


        # =================================================
        # CRIAR PERFIL
        # =================================================

        if perfil is None:

            perfil = PerfilAcademico(
                usuario=request.user
            )


        # =================================================
        # ATUALIZAR DADOS
        # =================================================

        perfil.nome_completo = nome_completo

        perfil.numero_estudante = numero_estudante

        perfil.curso = curso

        perfil.ano_academico = ano_academico

        perfil.telefone = telefone

        perfil.email_institucional = (
            email_institucional
        )

        perfil.descricao_interesse = (
            descricao or ''
        )


        # =================================================
        # COMPROVATIVO
        # =================================================

        if comprovativo:

            perfil.comprovativo_academico = (
                comprovativo
            )


        if not perfil.comprovativo_academico:

            messages.error(
                request,
                'Anexe o comprovativo académico.'
            )

            return redirect(
                'perfil_academico'
            )


        # =================================================
        # ESTADO DA VALIDAÇÃO
        # =================================================

        # Perfil novo:
        # depois da submissão passa para PENDENTE.

        if perfil_novo:

            perfil.estado_validacao = (
                PerfilAcademico
                .EstadoValidacao
                .PENDENTE
            )


        # Perfil incompleto ou rejeitado:
        # uma nova submissão volta para PENDENTE.

        elif perfil.estado_validacao in [
            PerfilAcademico.EstadoValidacao.INCOMPLETO,
            PerfilAcademico.EstadoValidacao.REJEITADO,
        ]:

            perfil.estado_validacao = (
                PerfilAcademico
                .EstadoValidacao
                .PENDENTE
            )


        # Se estiver VALIDADO,
        # o estado é preservado.


        # =================================================
        # DATA DA SUBMISSÃO
        # =================================================

        if (
            perfil_novo
            or
            perfil.estado_validacao
            ==
            PerfilAcademico.EstadoValidacao.PENDENTE
        ):

            perfil.submetido_em = timezone.now()


        # =================================================
        # SALVAR
        # =================================================

        perfil.save()


        messages.success(
            request,
            'Informações académicas guardadas com sucesso.'
        )

        return redirect(
            'perfil_academico'
        )


    # =====================================================
    # CONTEXTO
    # =====================================================

    contexto = {
        'faculdades': faculdades,
        'cursos': cursos,
        'perfil': perfil,
    }


    return render(
        request,
        'perfil_academico.html',
        contexto
    )



    # =====================================================
    # PERFIL ACADÉMICO DO ESTUDANTE LOGADO
    # =====================================================

    perfil = (
        PerfilAcademico.objects
        .filter(
            usuario=request.user
        )
        .select_related(
            'curso',
            'curso__faculdade'
        )
        .first()
    )


    # =====================================================
    # PROJECTO MAIS RECENTE DO ESTUDANTE
    # =====================================================

    projecto = None


    if perfil:

        projecto = (
            Projecto.objects
            .filter(
                estudante=perfil
            )
            .order_by(
                '-submetido_em'
            )
            .first()
        )


    # =====================================================
    # MANIFESTAÇÕES RECEBIDAS
    #
    # Só ficam disponíveis quando o projecto já estiver
    # PUBLICADO.
    # =====================================================

    manifestacoes = (
        ManifestacaoInteresse.objects
        .none()
    )


    if (
        perfil
        and projecto
        and projecto.estado
        == Projecto.EstadoProjecto.PUBLICADO
    ):

        manifestacoes = (
            ManifestacaoInteresse.objects
            .filter(
                projecto=projecto,
                projecto__estudante=perfil
            )
            .select_related(
                'investidor',
                'investidor__usuario',
                'projecto'
            )
            .order_by(
                '-atualizada_em',
                '-enviada_em'
            )
        )


    # =====================================================
    # CONTADORES
    # =====================================================

    total_interesses = (
        manifestacoes.count()
    )


    interesses_novos = (
        manifestacoes
        .filter(
            estado=ManifestacaoInteresse.Estado.ENVIADA
        )
        .count()
    )


    interesses_em_analise = (
        manifestacoes
        .filter(
            estado=ManifestacaoInteresse.Estado.EM_ANALISE
        )
        .count()
    )


    interesses_respondidos = (
        manifestacoes
        .filter(
            estado=ManifestacaoInteresse.Estado.RESPONDIDA
        )
        .count()
    )


    # =====================================================
    # ABA ACTIVA
    #
    # ?secao=interesses
    # =====================================================

    secao_ativa = (
        request.GET
        .get(
            'secao',
            'projecto'
        )
        .strip()
    )


    if secao_ativa not in [
        'projecto',
        'interesses'
    ]:

        secao_ativa = 'projecto'


    # Não existe área de interesses antes da publicação.

    if (
        secao_ativa == 'interesses'
        and (
            not projecto
            or projecto.estado
            != Projecto.EstadoProjecto.PUBLICADO
        )
    ):

        secao_ativa = 'projecto'


    # =====================================================
    # MANIFESTAÇÃO SELECCIONADA
    #
    # ?secao=interesses&manifestacao=3
    # =====================================================

    manifestacao_id = (
        request.GET
        .get(
            'manifestacao'
        )
    )


    manifestacao_seleccionada = None


    if (
        secao_ativa == 'interesses'
        and manifestacao_id
        and manifestacao_id.isdigit()
    ):

        manifestacao_seleccionada = (
            manifestacoes
            .filter(
                id=int(manifestacao_id)
            )
            .first()
        )


    # Se o estudante abriu a área de interesses sem escolher
    # um registo, mostramos automaticamente o mais recente.

    if (
        secao_ativa == 'interesses'
        and manifestacao_seleccionada is None
        and manifestacoes.exists()
    ):

        manifestacao_seleccionada = (
            manifestacoes.first()
        )


    # =====================================================
    # POST - INTERAGIR COM A MANIFESTAÇÃO
    # =====================================================

    if request.method == 'POST':

        # Segurança: só permite interagir se o projecto do
        # estudante estiver publicado.

        if (
            not perfil
            or not projecto
            or projecto.estado
            != Projecto.EstadoProjecto.PUBLICADO
        ):

            messages.error(
                request,
                'Não é possível gerir manifestações de interesse neste momento.'
            )

            return redirect(
                'estudante_projeto'
            )


        manifestacao_id = (
            request.POST
            .get(
                'manifestacao_id'
            )
        )


        if not manifestacao_id:

            messages.error(
                request,
                'Manifestação de interesse não informada.'
            )

            return redirect(
                reverse('estudante_projeto')
                + '?secao=interesses'
            )


        # A manifestação precisa pertencer ao projecto
        # do estudante autenticado.

        manifestacao = get_object_or_404(

            ManifestacaoInteresse.objects
            .select_related(
                'projecto',
                'investidor',
                'investidor__usuario'
            ),

            id=manifestacao_id,
            projecto=projecto,
            projecto__estudante=perfil

        )


        acao = (
            request.POST
            .get(
                'acao',
                ''
            )
            .strip()
        )


        # =================================================
        # MARCAR COMO EM ANÁLISE
        # =================================================

        if acao == 'analisar':

            if (
                manifestacao.estado
                == ManifestacaoInteresse.Estado.ENVIADA
            ):

                manifestacao.estado = (
                    ManifestacaoInteresse.Estado.EM_ANALISE
                )

                manifestacao.save(
                    update_fields=[
                        'estado',
                        'atualizada_em',
                    ]
                )


                messages.success(
                    request,
                    'Manifestação marcada como Em análise.'
                )


            elif (
                manifestacao.estado
                == ManifestacaoInteresse.Estado.EM_ANALISE
            ):

                messages.info(
                    request,
                    'Esta manifestação já está em análise.'
                )


            else:

                messages.info(
                    request,
                    'Esta manifestação já foi respondida.'
                )


            url = (
                reverse('estudante_projeto')
                + '?secao=interesses'
                + f'&manifestacao={manifestacao.id}'
                + '#interesses-recebidos'
            )

            return redirect(
                url
            )


        # =================================================
        # RESPONDER AO INVESTIDOR
        # =================================================

        elif acao == 'responder':

            if (
                manifestacao.estado
                != ManifestacaoInteresse.Estado.EM_ANALISE
            ):

                messages.error(
                    request,
                    'Marque primeiro a manifestação como Em análise antes de responder.'
                )

                url = (
                    reverse('estudante_projeto')
                    + '?secao=interesses'
                    + f'&manifestacao={manifestacao.id}'
                    + '#interesses-recebidos'
                )

                return redirect(
                    url
                )


            resposta = (
                request.POST
                .get(
                    'resposta',
                    ''
                )
                .strip()
            )


            if not resposta:

                messages.error(
                    request,
                    'Escreva uma resposta antes de enviar.'
                )

                url = (
                    reverse('estudante_projeto')
                    + '?secao=interesses'
                    + f'&manifestacao={manifestacao.id}'
                    + '#interesses-recebidos'
                )

                return redirect(
                    url
                )


            manifestacao.resposta = resposta

            manifestacao.estado = (
                ManifestacaoInteresse.Estado.RESPONDIDA
            )

            manifestacao.respondida_em = (
                timezone.now()
            )

            manifestacao.save(
                update_fields=[
                    'resposta',
                    'estado',
                    'respondida_em',
                    'atualizada_em',
                ]
            )


            messages.success(
                request,
                'Resposta enviada ao Investidor com sucesso.'
            )


            url = (
                reverse('estudante_projeto')
                + '?secao=interesses'
                + f'&manifestacao={manifestacao.id}'
                + '#interesses-recebidos'
            )

            return redirect(
                url
            )


        # =================================================
        # ACÇÃO INVÁLIDA
        # =================================================

        messages.error(
            request,
            'Acção inválida.'
        )


        return redirect(
            reverse('estudante_projeto')
            + '?secao=interesses'
        )


    # =====================================================
    # CONTEXTO
    # =====================================================

    contexto = {

        'perfil':
            perfil,

        'projecto':
            projecto,

        'secao_ativa':
            secao_ativa,

        'manifestacoes':
            manifestacoes,

        'manifestacao_seleccionada':
            manifestacao_seleccionada,

        'total_interesses':
            total_interesses,

        'interesses_novos':
            interesses_novos,

        'interesses_em_analise':
            interesses_em_analise,

        'interesses_respondidos':
            interesses_respondidos,

    }


    return render(
        request,
        'projeto.html',
        contexto
    )

@login_required
def acompanhamento(request):

    # =====================================================
    # VERIFICAR SE É ESTUDANTE
    # =====================================================

    if not request.user.groups.filter(
        name='Estudante'
    ).exists():

        messages.error(
            request,
            'Não possui autorização para acessar a área do Estudante.'
        )

        return redirect(
            'escolher_area'
        )


    # =====================================================
    # PERFIL ACADÉMICO
    # =====================================================

    perfil = (
        PerfilAcademico.objects
        .filter(
            usuario=request.user
        )
        .select_related(
            'curso',
            'curso__faculdade'
        )
        .first()
    )


    if not perfil:

        messages.error(
            request,
            'Perfil académico não encontrado.'
        )

        return redirect(
            'perfil_academico'
        )


    # =====================================================
    # PROJECTO DO ESTUDANTE
    #
    # Neste momento usamos o projecto mais recente.
    # =====================================================

    projecto = (
        Projecto.objects
        .filter(
            estudante=perfil
        )
        .select_related(
            'mentor',
            'mentor__usuario'
        )
        .order_by(
            '-submetido_em'
        )
        .first()
    )


    # =====================================================
    # VALORES INICIAIS
    # =====================================================

    mentor = None

    proxima_sessao = None

    sessoes = SessaoMentoria.objects.none()

    sessoes_realizadas = 0

    total_sessoes = 0

    atas = AtaMentoria.objects.none()

    total_registos = 0


    # =====================================================
    # SE EXISTIR PROJECTO
    # =====================================================

    if projecto:

        mentor = projecto.mentor


        # =================================================
        # TODAS AS SESSÕES DO PROJECTO
        # =================================================

        sessoes = (
            SessaoMentoria.objects
            .filter(
                projecto=projecto
            )
            .select_related(
                'mentor',
                'mentor__usuario',
                'projecto'
            )
            .order_by(
                '-data_hora_inicio'
            )
        )


        # =================================================
        # TOTAL DE SESSÕES
        #
        # Canceladas não entram no total.
        # =================================================

        total_sessoes = (
            sessoes
            .filter(
                estado__in=[
                    SessaoMentoria.Estado.AGENDADA,
                    SessaoMentoria.Estado.REAGENDADA,
                    SessaoMentoria.Estado.CONCLUIDA,
                ]
            )
            .count()
        )


        # =================================================
        # SESSÕES REALIZADAS
        # =================================================

        sessoes_realizadas = (
            sessoes
            .filter(
                estado=SessaoMentoria.Estado.CONCLUIDA
            )
            .count()
        )


        # =================================================
        # PRÓXIMA SESSÃO
        # =================================================

        proxima_sessao = (
            sessoes
            .filter(
                estado__in=[
                    SessaoMentoria.Estado.AGENDADA,
                    SessaoMentoria.Estado.REAGENDADA,
                ],
                data_hora_inicio__gte=timezone.now()
            )
            .order_by(
                'data_hora_inicio'
            )
            .first()
        )


        # =================================================
        # ATAS SUBMETIDAS
        #
        # O estudante não vê rascunhos do Mentor.
        # =================================================

        atas = (
            AtaMentoria.objects
            .filter(
                sessao__projecto=projecto,
                estado_ata=AtaMentoria.EstadoAta.SUBMETIDA
            )
            .select_related(
                'sessao',
                'sessao__mentor',
                'sessao__mentor__usuario'
            )
            .order_by(
                '-submetido_em'
            )
        )


        total_registos = (
            atas.count()
        )


    # =====================================================
    # CONTEXTO
    # =====================================================

    contexto = {

        'perfil':
            perfil,

        'projecto':
            projecto,

        'mentor':
            mentor,

        'proxima_sessao':
            proxima_sessao,

        'sessoes':
            sessoes,

        'sessoes_realizadas':
            sessoes_realizadas,

        'total_sessoes':
            total_sessoes,

        'atas':
            atas,

        'total_registos':
            total_registos,

    }


    return render(
        request,
        'acompanhamento.html',
        contexto
    )


def sair(request):

    logout(request)

    return redirect('/visitante/home/')

@login_required
def submeter_projecto(request):

    # =====================================================
    # PERFIL DO ESTUDANTE LOGADO
    # =====================================================

    perfil = (
        PerfilAcademico.objects
        .filter(usuario=request.user)
        .select_related(
            'curso',
            'curso__faculdade'
        )
        .first()
    )


    # =====================================================
    # VERIFICAR SE EXISTE PERFIL
    # =====================================================

    if perfil is None:

        messages.error(
            request,
            'Complete primeiro o seu perfil académico.'
        )

        return redirect(
            'perfil_academico'
        )


    # =====================================================
    # VERIFICAR VALIDAÇÃO ACADÉMICA
    # =====================================================

    if (
        perfil.estado_validacao
        !=
        PerfilAcademico.EstadoValidacao.VALIDADO
    ):

        messages.error(
            request,
            'O seu perfil académico precisa estar validado '
            'antes de submeter um projecto.'
        )

        return redirect(
            'estudante_projeto'
        )


    # =====================================================
    # VERIFICAR SE JÁ EXISTE PROJECTO ATIVO
    # =====================================================

    projecto_existente = (
        Projecto.objects
        .filter(estudante=perfil)
        .exclude(
            estado=Projecto.EstadoProjecto.REJEITADO
        )
        .exists()
    )


    if projecto_existente:

        messages.warning(
            request,
            'Já possui um projecto submetido.'
        )

        return redirect(
            'estudante_projeto'
        )


    # =====================================================
    # SUBMISSÃO
    # =====================================================

    if request.method == 'POST':

        titulo = request.POST.get(
            'titulo',
            ''
        ).strip()

        area_atuacao = request.POST.get(
            'area_atuacao'
                    )

        resumo_executivo = request.POST.get(
            'resumo_executivo',
            ''
        ).strip()

        problema = request.POST.get(
            'problema',
            ''
        ).strip()

        solucao = request.POST.get(
            'solucao',
            ''
        ).strip()

        modelo_negocio = request.POST.get(
            'modelo_negocio',
            ''
        ).strip()

        equipa = request.POST.get(
            'equipa',
            ''
        ).strip()

        anexo = request.FILES.get(
            'anexo'
        )


        # =================================================
        # CAMPOS OBRIGATÓRIOS
        # =================================================

        if not all([
            titulo,
            area_atuacao,
            resumo_executivo,
            problema,
            solucao,
            modelo_negocio,
            equipa,
        ]):

            messages.error(
                request,
                'Preencha todos os campos obrigatórios.'
            )

            return render(
                request,
                'submeter_projecto.html',
                {
                    'perfil': perfil
                }
            )


        # =================================================
        # CRIAR PROJECTO
        # =================================================

        Projecto.objects.create(

            estudante=perfil,

            titulo=titulo,

            area_atuacao=area_atuacao,

            resumo_executivo=resumo_executivo,

            problema=problema,

            solucao=solucao,

            modelo_negocio=modelo_negocio,

            equipa=equipa,

            anexo=anexo,

            estado=(
                Projecto
                .EstadoProjecto
                .PENDENTE
            ),
        )


        messages.success(
            request,
            'Projecto submetido com sucesso. '
            'Aguarde a avaliação administrativa.'
        )


        return redirect(
            'estudante_projeto'
        )


    contexto = {
        'perfil': perfil,
        'area_atuacao': Projecto.AreaAtuacao.choices,
    }
    return render(
        request,
        'submeter_projecto.html',
        contexto
    )