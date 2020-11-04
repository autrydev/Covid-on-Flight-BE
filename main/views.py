from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import User

def home(request):
	#Reserved for homepage..currently redirects
	if request.user.is_authenticated:
		return redirect('user_dashboard')
	else:
		return redirect('login')

def login(request):
	if request.user.is_authenticated:
		return redirect('user_dashboard')
	
	if request.method == "POST":
	#Uses Django Authentication
		email = request.POST['email']
		password = request.POST['password']
		user = authenticate(username=email, password=password)
		if user is not None:
			#django_login(request,user)
			return redirect('user_dashboard')
		else:
			return HttpResponse('Invalid Email/Password', status=401)

def logout(request):
	if request.user.is_authenticated:
		django_logout(request)

	return redirect('home')

def signup(request):
	if request.user.is_authenticated:
		return redirect('user_dashboard')
	
	if request.method == "POST":
		email = request.POST['email']
		password = request.POST['password']
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		phone_number = request.POST['phone_number']
		checkuser = authenticate(username=email)

		if checkuser is not None:
			return HttpResponse('Username Already Exists')
		else:
			#Create cofUser & Django User
			user_mgr = cofUserManager()
			user_mgr.create_user(email, password, first_name, last_name, phone_number)
			py_user = User.objects.create_user(username=email, email=email, first_name=first_name, last_name=last_name)
			py_user.save()
			return py_user #or cofUser..?

def user_dashboard(request):
	return HttpResponse('User_Dashboard Vue ✈️')

def admin_dashboard(request):
	return HttpResponse('Admin_Dashboard Vue ✈️')

from django.shortcuts import render
from django.http import HttpResponse

def login(request):
    return HttpResponse('Hi! This is Covid on Flight speaking. ✈️')
