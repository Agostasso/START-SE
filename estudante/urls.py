from django.urls import path
from . import views

urlpatterns = [

    path('dashboard/', views.dashboard, name='estudante_dashboard'),
    path('perfil_academico/', views.perfil_academico, name='perfil_academico'),
    path('projeto/', views.projeto, name='estudante_projeto'),
    path( 'acompanhamento/', views.acompanhamento, name='estudante_acompanhamento'),
    path('sair/', views.sair, name='estudante_sair'),
    path('submeter_projecto/', views.submeter_projecto, name='submeter_projecto'),
]
