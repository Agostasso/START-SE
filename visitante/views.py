from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import auth, messages
from django.contrib.messages import constants

# Create your views here.

def home(request): 
    if request.method == 'GET':
        return render (request, 'home.html')

def marketplace(request):
    if request.method == 'GET':
        return render(request, 'marketplace.html')


def startup_detalhe(request, id):
    if request.method == 'GET':
        return render(request, 'startup_detalhe.html', {'startup_id': id}
                      )

def login(request):
    if request.method == 'GET':
        return render(request, 'Login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = auth.authenticate(request, username=username, password=senha)
        if user:
            auth.login(request, user)
            return redirect('/estudante/dashboard')
        
        messages.add_message(request, constants.ERROR, 'Usuario ou senha inválido')
        return redirect('/visitante/login')

def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    
    elif request.method == "POST":
         username = request.POST.get('username')
         senha = request.POST.get('senha')
         confirmar_senha = request.POST.get('confirmar_senha')

         if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas não coincidem')
            return redirect('/visitante/cadastro')
 
         if len(senha) < 6:
             messages.add_message(request, constants.ERROR, 'A senha deve possuir pelomenos 6 caracteres')
             return redirect('/visitante/cadastro')
 
         users = User.objects.filter(username=username)
         if users.exists():
            messages.add_message(request, constants.ERROR, 'O usuário já existe')
            return redirect('/visitante/cadastro')
         
         messages.add_message(request, constants.SUCCESS, 'Cadastro feito com sucesso')

         user = User.objects.create_user(
            username=username,
            password=senha
 )
         return redirect('/visitante/login')

