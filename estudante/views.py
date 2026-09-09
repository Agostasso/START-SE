
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import render, redirect , get_object_or_404
from django.http import HttpResponse
from .models import Faculdade, PerfilAcademico, Curso, Projecto
from django.contrib.auth.decorators import login_required
from django.utils import timezone



# Create your views here.
@login_required
def dashboard(request):

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
    # VALORES INICIAIS
    # =====================================================

    estado_validacao = 'INCOMPLETO'
    estado_validacao_texto = 'Incompleto'

    projeto = None
    projeto_disponivel = False
    projeto_estado = 'Bloqueado'

    mentoria_estado = 'Não atribuída'

    progresso = 14


    # =====================================================
    # PERFIL ACADÉMICO
    # =====================================================

    if perfil:

        estado_validacao = perfil.estado_validacao

        estado_validacao_texto = (
            perfil.get_estado_validacao_display()
        )


        # =================================================
        # PERFIL VALIDADO
        # =================================================

        if (
            perfil.estado_validacao
            ==
            PerfilAcademico.EstadoValidacao.VALIDADO
        ):

            projeto_disponivel = True

            projeto_estado = 'Disponível'

            # Conta criada + validação
            progresso = 28


            # =============================================
            # PROJECTO DO ESTUDANTE
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

                projeto_estado = (
                    projeto.get_estado_display()
                )

                # Conta
                # + validação
                # + submissão
                progresso = 42


                # =========================================
                # PROJECTO APROVADO
                # =========================================

                if (
                    projeto.estado
                    ==
                    Projecto.EstadoProjecto.APROVADO
                ):

                    progresso = 57


                # =========================================
                # EM INCUBAÇÃO
                # =========================================

                elif (
                    projeto.estado
                    ==
                    Projecto.EstadoProjecto.EM_INCUBACAO
                ):

                    progresso = 71

                    mentoria_estado = (
                        'Em incubação'
                    )


                # =========================================
                # PUBLICADO
                # =========================================

                elif (
                    projeto.estado
                    ==
                    Projecto.EstadoProjecto.PUBLICADO
                ):

                    progresso = 85

                    mentoria_estado = (
                        'Concluída'
                    )


                # =========================================
                # REJEITADO
                # =========================================

                elif (
                    projeto.estado
                    ==
                    Projecto.EstadoProjecto.REJEITADO
                ):

                    # A submissão aconteceu,
                    # mas a avaliação não foi concluída
                    # com aprovação.
                    progresso = 42


    # =====================================================
    # CONTEXTO
    # =====================================================

    contexto = {

        'perfil': perfil,

        'estado_validacao': (
            estado_validacao
        ),

        'estado_validacao_texto': (
            estado_validacao_texto
        ),

        'projeto': projeto,

        'projeto_disponivel': (
            projeto_disponivel
        ),

        'projeto_estado': (
            projeto_estado
        ),

        'mentoria_estado': (
            mentoria_estado
        ),

        'progresso': progresso,
    }


    return render(
        request,
        'estudante_dashboard.html',
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


@login_required
def projeto(request):

    # Perfil académico do estudante logado
    perfil = (
        PerfilAcademico.objects
        .filter(usuario=request.user)
        .select_related(
            'curso',
            'curso__faculdade'
        )
        .first()
    )


    # Projecto mais recente do estudante
    projecto = None

    if perfil:

        projecto = (
            Projecto.objects
            .filter(estudante=perfil)
            .order_by('-submetido_em')
            .first()
        )


    contexto = {
        'perfil': perfil,
        'projecto': projecto,
    }


    return render(
        request,
        'projeto.html',
        contexto
    )


def acompanhamento(request):
    return render(request, 'acompanhamento.html')



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