
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import render, redirect , get_object_or_404
from django.http import HttpResponse
from .models import Faculdade, PerfilAcademico, Curso
from django.contrib.auth.decorators import login_required
from django.utils import timezone



# Create your views here.
@login_required
def dashboard(request):

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

    projeto_disponivel = False
    projeto_estado = 'Bloqueado'

    mentoria_estado = 'Não atribuída'

    progresso = 14


    # =====================================================
    # SE O ESTUDANTE JÁ POSSUI PERFIL
    # =====================================================

    if perfil:

        estado_validacao = perfil.estado_validacao

        estado_validacao_texto = (
            perfil.get_estado_validacao_display()
        )


        # Perfil validado
        if (
            perfil.estado_validacao
            ==
            PerfilAcademico.EstadoValidacao.VALIDADO
        ):
            projeto_disponivel = True
            projeto_estado = 'Disponível'

            progresso = 28


        # Perfil pendente
        elif (
            perfil.estado_validacao
            ==
            PerfilAcademico.EstadoValidacao.PENDENTE
        ):

            projeto_disponivel = False
            projeto_estado = 'Bloqueado'

            progresso = 14


        # Perfil rejeitado
        elif (
            perfil.estado_validacao
            ==
            PerfilAcademico.EstadoValidacao.REJEITADO
        ):

            projeto_disponivel = False
            projeto_estado = 'Bloqueado'

            progresso = 14


    # =====================================================
    # CONTEXTO
    # =====================================================

    contexto = {

        'perfil': perfil,

        'estado_validacao': estado_validacao,

        'estado_validacao_texto':
            estado_validacao_texto,

        'projeto_disponivel':
            projeto_disponivel,

        'projeto_estado':
            projeto_estado,

        'mentoria_estado':
            mentoria_estado,

        'progresso':
            progresso,
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


def projeto(request):
    return render(request,'projeto.html')


def acompanhamento(request):
    return render(request, 'acompanhamento.html')



def sair(request):

    logout(request)

    return redirect('/visitante/home/')