from . import views
from django.urls import path

urlpatterns = [
    path('consultar/', views.consultar_startups, name='consultar_startups'),
    path('propostas/', views.acompanhar_propostas, name='propostas'),
    path('startups/<int:projecto_id>/manifestar-interesse/', views.manifestar_interesse, name='investidor_manifestar_interesse'),
]