from django.urls import path, include

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name="mentor_dashboard"),
    path('projects/', views.projects, name="mentor_projects"),
    path('agenda/', views.agenda, name="mentor_agenda"),
    path('acompanhamento/', views.acompanhamento, name="mentor_acompanhamento"),
    path('projectos/<int:projecto_id>/',views.projecto_ficha, name='mentor_projecto_ficha'),
    path('agenda/novo/', views.novo_agendamento, name='mentor_novo_agendamento'),

]