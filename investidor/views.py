from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from estudante.models import Projecto
from .models import Investidor, ManifestacaoInteresse



# Create your views here.

@login_required
def consultar_startups(request):

    # =====================================================
    # VERIFICAR PERMISSÃO
    #
    # No cadastro o perfil chama-se PATROCINADOR.
    # A área funcional da plataforma chama-se INVESTIDOR.
    # =====================================================

    if not request.user.groups.filter(
        name='Patrocinador'
    ).exists():

        messages.error(
            request,
            'Não possui autorização para acessar a área do Investidor.'
        )

        return redirect(
            'escolher_area'
        )


    # =====================================================
    # PERFIL DO INVESTIDOR
    #
    # O utilizador já foi autorizado através do grupo
    # Patrocinador.
    #
    # Caso ainda não exista um registo Investidor,
    # criamos automaticamente.
    # =====================================================

    investidor, criado = (
        Investidor.objects
        .get_or_create(
            usuario=request.user,
            defaults={
                'ativo': True,
            }
        )
    )


    # =====================================================
    # VERIFICAR SE O PERFIL ESTÁ ACTIVO
    # =====================================================

    if not investidor.ativo:

        messages.error(
            request,
            'O seu perfil de Investidor encontra-se desactivado.'
        )

        return redirect(
            'escolher_area'
        )


    # =====================================================
    # GET - PESQUISA
    #
    # Exemplo:
    # /investidor/startups/?q=agricultura
    # =====================================================

    pesquisa = (
        request.GET
        .get(
            'q',
            ''
        )
        .strip()
    )


    # =====================================================
    # GET - FILTRO POR ÁREA
    #
    # Exemplo:
    # /investidor/startups/?area=AGROTECH
    # =====================================================

    area = (
        request.GET
        .get(
            'area',
            ''
        )
        .strip()
    )


    # =====================================================
    # VALIDAR ÁREA
    #
    # Evita receber valores que não pertencem às choices
    # definidas no modelo Projecto.
    # =====================================================

    areas_validas = [
        valor
        for valor, nome
        in Projecto.AreaAtuacao.choices
    ]


    if area not in areas_validas:

        area = ''


    # =====================================================
    # STARTUPS DISPONÍVEIS
    #
    # Somente projectos PUBLICADOS aparecem para o
    # Investidor.
    # =====================================================

    projectos = (
        Projecto.objects
        .filter(
            estado=Projecto.EstadoProjecto.PUBLICADO
        )
        .select_related(
            'estudante',
            'estudante__curso'
        )
        .order_by(
            '-atualizado_em'
        )
    )


    # =====================================================
    # APLICAR PESQUISA
    # =====================================================

    if pesquisa:

        projectos = (
            projectos
            .filter(

                Q(
                    titulo__icontains=pesquisa
                )

                |

                Q(
                    resumo_executivo__icontains=pesquisa
                )

                |

                Q(
                    problema__icontains=pesquisa
                )

                |

                Q(
                    solucao__icontains=pesquisa
                )

                |

                Q(
                    modelo_negocio__icontains=pesquisa
                )

                |

                Q(
                    estudante__nome_completo__icontains=pesquisa
                )

            )
        )


    # =====================================================
    # APLICAR FILTRO POR ÁREA
    # =====================================================

    if area:

        projectos = (
            projectos
            .filter(
                area_atuacao=area
            )
        )


    # =====================================================
    # TOTAL DE STARTUPS ENCONTRADAS
    # =====================================================

    total_startups = (
        projectos.count()
    )


    # =====================================================
    # GET - STARTUP SELECCIONADA
    #
    # Exemplo:
    # /investidor/startups/?startup=3
    # =====================================================

    startup_id = (
        request.GET
        .get(
            'startup'
        )
    )


    startup_seleccionada = None


    # =====================================================
    # VALIDAR O ID RECEBIDO
    # =====================================================

    if (
        startup_id
        and startup_id.isdigit()
    ):

        startup_seleccionada = (
            projectos
            .filter(
                id=int(startup_id)
            )
            .first()
        )


    # =====================================================
    # SE NENHUMA STARTUP FOI SELECCIONADA
    #
    # Mostra automaticamente a primeira startup disponível.
    # =====================================================

    if (
        startup_seleccionada is None
        and total_startups > 0
    ):

        startup_seleccionada = (
            projectos.first()
        )


    # =====================================================
    # CONTEXTO
    # =====================================================

    contexto = {

        # Perfil
        'investidor':
            investidor,


        # Lista
        'projectos':
            projectos,


        # Ficha à direita
        'startup_seleccionada':
            startup_seleccionada,


        # Contagem
        'total_startups':
            total_startups,


        # Pesquisa
        'pesquisa':
            pesquisa,


        # Área seleccionada
        'area_seleccionada':
            area,


        # Choices do modelo
        'areas':
            Projecto.AreaAtuacao.choices,

    }


    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        'consultar_startups.html',
        contexto
    )


@login_required
def acompanhar_propostas(request):

    # =====================================================
    # VERIFICAR PERMISSÃO
    #
    # Cadastro/grupo = Patrocinador
    # Área funcional = Investidor
    # =====================================================

    if not request.user.groups.filter(
        name='Patrocinador'
    ).exists():

        messages.error(
            request,
            'Não possui autorização para acessar a área do Investidor.'
        )

        return redirect(
            'escolher_area'
        )


    # =====================================================
    # PERFIL INVESTIDOR
    # =====================================================

    investidor, criado = (
        Investidor.objects
        .get_or_create(
            usuario=request.user,
            defaults={
                'ativo': True,
            }
        )
    )


    if not investidor.ativo:

        messages.error(
            request,
            'O seu perfil de Investidor encontra-se desactivado.'
        )

        return redirect(
            'escolher_area'
        )


    # =====================================================
    # TODAS AS MANIFESTAÇÕES DO INVESTIDOR
    # =====================================================

    todas_manifestacoes = (
        ManifestacaoInteresse.objects
        .filter(
            investidor=investidor
        )
        .select_related(
            'projecto',
            'projecto__estudante'
        )
        .order_by(
            '-atualizada_em',
            '-enviada_em'
        )
    )


    # =====================================================
    # CARDS
    # =====================================================

    total_enviadas = (
        todas_manifestacoes.count()
    )


    total_em_analise = (
        todas_manifestacoes
        .filter(
            estado=ManifestacaoInteresse.Estado.EM_ANALISE
        )
        .count()
    )


    total_respondidas = (
        todas_manifestacoes
        .filter(
            estado=ManifestacaoInteresse.Estado.RESPONDIDA
        )
        .count()
    )


    total_parcerias = (
        todas_manifestacoes
        .filter(
            assunto=ManifestacaoInteresse.Assunto.PARCERIA
        )
        .count()
    )


    # =====================================================
    # GET - PESQUISA
    # =====================================================

    pesquisa = (
        request.GET
        .get(
            'q',
            ''
        )
        .strip()
    )


    # =====================================================
    # GET - FILTRO POR ESTADO
    # =====================================================

    estado = (
        request.GET
        .get(
            'estado',
            ''
        )
        .strip()
    )


    estados_validos = [
        valor
        for valor, nome
        in ManifestacaoInteresse.Estado.choices
    ]


    if estado not in estados_validos:

        estado = ''


    # =====================================================
    # LISTA FILTRADA
    # =====================================================

    manifestacoes = todas_manifestacoes


    if pesquisa:

        manifestacoes = (
            manifestacoes
            .filter(

                Q(
                    projecto__titulo__icontains=pesquisa
                )

                |

                Q(
                    mensagem__icontains=pesquisa
                )

                |

                Q(
                    contacto_direto__icontains=pesquisa
                )

            )
        )


    if estado:

        manifestacoes = (
            manifestacoes
            .filter(
                estado=estado
            )
        )


    # =====================================================
    # IDENTIFICAR TIPO DE CONTACTO
    # =====================================================

    for item in manifestacoes:

        if '@' in item.contacto_direto:

            item.tipo_contacto = 'E-mail'

        else:

            item.tipo_contacto = 'Telefone'


    # =====================================================
    # GET - MANIFESTAÇÃO SELECCIONADA
    #
    # ?manifestacao=3
    # =====================================================

    manifestacao_id = (
        request.GET
        .get(
            'manifestacao'
        )
    )


    manifestacao_seleccionada = None


    if (
        manifestacao_id
        and manifestacao_id.isdigit()
    ):

        manifestacao_seleccionada = (
            manifestacoes
            .filter(
                id=int(manifestacao_id)
            )
            .first()
        )


    # =====================================================
    # SE NENHUMA FOI SELECCIONADA
    #
    # Mostra automaticamente a mais recente.
    # =====================================================

    if (
        manifestacao_seleccionada is None
        and manifestacoes.exists()
    ):

        manifestacao_seleccionada = (
            manifestacoes.first()
        )


    if manifestacao_seleccionada:

        if '@' in manifestacao_seleccionada.contacto_direto:

            manifestacao_seleccionada.tipo_contacto = 'E-mail'

        else:

            manifestacao_seleccionada.tipo_contacto = 'Telefone'


    # =====================================================
    # CONTEXTO
    # =====================================================

    contexto = {

        'investidor':
            investidor,

        'manifestacoes':
            manifestacoes,

        'manifestacao_seleccionada':
            manifestacao_seleccionada,

        'total_enviadas':
            total_enviadas,

        'total_em_analise':
            total_em_analise,

        'total_respondidas':
            total_respondidas,

        'total_parcerias':
            total_parcerias,

        'pesquisa':
            pesquisa,

        'estado_seleccionado':
            estado,

        'estados':
            ManifestacaoInteresse.Estado.choices,

    }


    return render(
        request,
        'propostas.html',
        contexto
    )

@login_required
def manifestar_interesse(
    request,
    projecto_id
):

    # =====================================================
    # VERIFICAR PERMISSÃO
    #
    # Cadastro = Patrocinador
    # Área funcional = Investidor
    # =====================================================

    if not request.user.groups.filter(
        name='Patrocinador'
    ).exists():

        messages.error(
            request,
            'Não possui autorização para acessar a área do Investidor.'
        )

        return redirect(
            'escolher_area'
        )


    # =====================================================
    # PERFIL INVESTIDOR
    # =====================================================

    investidor, criado = (
        Investidor.objects
        .get_or_create(
            usuario=request.user,
            defaults={
                'ativo': True,
            }
        )
    )


    if not investidor.ativo:

        messages.error(
            request,
            'O seu perfil de Investidor encontra-se desactivado.'
        )

        return redirect(
            'escolher_area'
        )


    # =====================================================
    # PROJECTO
    #
    # O Investidor só pode contactar projectos PUBLICADOS.
    # =====================================================

    projecto = get_object_or_404(

        Projecto.objects.select_related(
            'estudante',
            'estudante__curso'
        ),

        id=projecto_id,

        estado=Projecto.EstadoProjecto.PUBLICADO

    )


    # =====================================================
    # POST - ENVIAR MANIFESTAÇÃO
    # =====================================================

    if request.method == 'POST':

        assunto = (
            request.POST
            .get(
                'assunto',
                ''
            )
            .strip()
        )


        mensagem = (
            request.POST
            .get(
                'mensagem',
                ''
            )
            .strip()
        )


        contacto_direto = (
            request.POST
            .get(
                'contacto_direto',
                ''
            )
            .strip()
        )


        # =================================================
        # VALIDAR ASSUNTO
        # =================================================

        assuntos_validos = [
            valor
            for valor, nome
            in ManifestacaoInteresse.Assunto.choices
        ]


        if assunto not in assuntos_validos:

            messages.error(
                request,
                'Seleccione um assunto válido.'
            )

            return render(
                request,
                'manifestar_interesse.html',
                {
                    'investidor':
                        investidor,

                    'projecto':
                        projecto,

                    'assuntos':
                        ManifestacaoInteresse.Assunto.choices,

                    'assunto_seleccionado':
                        assunto,

                    'mensagem_digitada':
                        mensagem,

                    'contacto_digitado':
                        contacto_direto,
                }
            )


        # =================================================
        # VALIDAR MENSAGEM
        # =================================================

        if not mensagem:

            messages.error(
                request,
                'Escreva a mensagem da manifestação de interesse.'
            )

            return render(
                request,
                'manifestar_interesse.html',
                {
                    'investidor':
                        investidor,

                    'projecto':
                        projecto,

                    'assuntos':
                        ManifestacaoInteresse.Assunto.choices,

                    'assunto_seleccionado':
                        assunto,

                    'mensagem_digitada':
                        mensagem,

                    'contacto_digitado':
                        contacto_direto,
                }
            )


        # =================================================
        # VALIDAR CONTACTO
        # =================================================

        if not contacto_direto:

            messages.error(
                request,
                'Informe um e-mail ou telefone para contacto.'
            )

            return render(
                request,
                'manifestar_interesse.html',
                {
                    'investidor':
                        investidor,

                    'projecto':
                        projecto,

                    'assuntos':
                        ManifestacaoInteresse.Assunto.choices,

                    'assunto_seleccionado':
                        assunto,

                    'mensagem_digitada':
                        mensagem,

                    'contacto_digitado':
                        contacto_direto,
                }
            )
        if len(contacto_direto) > 150:

            messages.error(
                request,
                'O contacto directo não pode ultrapassar 150 caracteres.'
            )

            return redirect(
                reverse(
                    'investidor_manifestar_interesse',
                    args=[
                        projecto.id
                    ]
                )
            )
        # =================================================
        # CRIAR MANIFESTAÇÃO
        # =================================================

        ManifestacaoInteresse.objects.create(

            investidor=
                investidor,

            projecto=
                projecto,

            assunto=
                assunto,

            mensagem=
                mensagem,

            contacto_direto=
                contacto_direto,

            estado=
                ManifestacaoInteresse.Estado.ENVIADA

        )
        messages.success(
            request,
            'Manifestação de interesse enviada com sucesso.'
        )
        # =================================================
        # VOLTAR À STARTUP
        #
        # Quando criarmos "Acompanhar proposta",
        # podemos redireccionar para ela.
        # =================================================

        url = (
            reverse(
                'consultar_startups'
            )
            + f'?startup={projecto.id}'
        )
        return redirect(
            url
        )
    # =====================================================
    # GET - MOSTRAR FORMULÁRIO
    # =====================================================

    contexto = {

        'investidor':
            investidor,

        'projecto':
            projecto,

        'assuntos':
            ManifestacaoInteresse.Assunto.choices,

    }

    return render(
        request,
        'manifestar_interesse.html',
        contexto
    )