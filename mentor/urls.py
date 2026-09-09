from django.urls import path, include

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name="mentor_dashboard"),
    path('projects/', views.projects, name="mentor_projects"),
    path('agenda/', views.agenda, name="mentor_agenda"),
    path('acompanhamento/', views.acompanhamento, name="mentor_acompanhamento"),

    
 
]