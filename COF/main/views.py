from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import User

def home(request):
	if request.user.is_authenticated:
		return redirect('user_dashboard')
	else:
		return redirect('login')

def login(request):
	if request.user.is_authenticated:
		return redirect('user_dashboard')
	
	if request.method == "POST":
		email = request.POST['email']
		password = request.POST['password']
		user = authenticate(email=email, password=password)
		if user is not None:
			django_login(request,user)
			return redirect('user_dashboard')
		else:
			return HttpResponse('Invalid Username/Password')

	return HttpResponse('Login_Form')

def logout(request):
	if request.user.is_authenticated:
		django_logout(request)

	return redirect('home')

def create_account(request):
	if request.user.is_authenticated:
		return redirect('user_dashboard')
	
	return render(request, AuthenticationForm)
	return redirect('user_dashboard')


def user_dashboard(request):
	return HttpResponse('User_Dashboard Vue ✈️')