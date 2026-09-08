from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name="home"),
    path('marketplace/', views.marketplace, name="marketplace"),
    path('login/', views.login, name="login"),
    path('cadastro/', views.cadastro, name="cadastro"),
    path('startup/<int:id>/', views.startup_detalhe, name="startup_detalhe"),
    path('escolher_area/', views.escolher_area, name="escolher_area"),

    
]
