from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import User
from django.contrib.auth import get_user_model
from .models import COFUser
import json
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.http import JsonResponse
from datetime import date, timedelta

twilio_client = Client('ACe4f586ddf64043984c3f813e1bf1232e', 'a12087fa31758795d95c38d240b87177') # Twilio
sendgrid_client = SendGridAPIClient('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') # SendGrid

def home(request):
	#Reserved for homepage..currently redirects
	if request.user.is_authenticated:
		return redirect('user_dashboard')
	else:
		return redirect('login')

def login(request):
	if request.user.is_authenticated:
		return redirect('user_dashboard')
	
	if request.method == 'POST':
		json_data = json.loads(request.body) #Put all contents of Post data into json_data variable
		email = json_data['email'] #Reference the email key/value from the json_data variable
		password = json_data['password']
		user = authenticate(username=email, password=password)
		
		# Checks all users for needing to update status
		all_users = COFUser.objects.all()
		for check in all_users:
			if check.covid_status != 'Notified' and (check.covid_status == 'Unknown'
				or check.last_update is None or (check.last_update + timedelta(days=14)) < date.today()):
					try:
						email = Mail(
							from_email='CovidOnFlight@gmail.com',
							to_emails=check.email,
							subject='Please update your COVID status.',
							html_content=('<h2><strong>Hello, ' + check.first_name + ' ' + check.last_name + '!'
							'✈️</strong></h2><p>It\'s COVID on Flight speaking. We\'re here to ask you to '
							'update your current COVID status to help inform and protect others! Thank you.</p>')
						)
						sendgrid_client.send(email)

						# TODO: remove
						if check.covid_status is None:
							status = 'Blank'
						else:
							status = check.covid_status

						print('Sent update email to:',check.first_name,check.last_name,'('+str(check.last_update)+' & '+status+')') # TODO: remove
						check.covid_status = 'Notified'
						check.save()
					except Exception as e:
						print(e)

		# Checks if user is authenticated
		if user is not None:
			output = {
				'id' : user.id,
				'update_status' : False
			}

			# If this current user needs to be updated, inform front-end
			if user.covid_status == 'Unknown' or user.last_update is None or user.last_update + timedelta(days=14) < date.today():
				output['update_status'] = True


			return JsonResponse(output)
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
		json_data = json.loads(request.body) #Put all contents of Post data into json_data variable
		email = json_data['email'] #Reference the email key/value from the json_data variable
		password = json_data['password']
		first_name = json_data['first_name']
		last_name = json_data['last_name']
		phone_number = json_data['phone_number']
		checkuser = COFUser.objects.filter(email=email)

		if checkuser:
			return HttpResponse('Username Already Exists', status=401)
		else:
			#Create cofUser & Django User
			py_user = get_user_model().objects.create_user(
				email=email,
				password=password,
				first_name=first_name,
				last_name=last_name,
				phone_number=phone_number
			)
			py_user.save()


			# Sends SMS (Twilio)
			try:
				twilio_client.messages.create(
					body=('Thank you for signing up for Covid on Flight, ' + first_name + ' ' + last_name + '!'),
					from_='+12185304600',
					to=('+1'+phone_number)
				)
			except TwilioRestException:
				print('Error texting user')

			# Sends email (SendGrid)
			try:
				email = Mail(
					from_email='CovidOnFlight@gmail.com',
					to_emails=email,
					subject='Welcome to Covid on Flight!',
					html_content=('<h2><strong>Hi, ' + first_name + ' ' + last_name + '! ✈️</strong></h2><p>Welcome to Covid on Flight! We look forward to making your travels safer.</p>')
				)

				sendgrid_client.send(email)
			except Exception as e:
				print(e)

			return HttpResponse(py_user.id, status=200)

def user_dashboard(request):
	return HttpResponse('User_Dashboard Vue ✈️')

def admin_dashboard(request):
	return HttpResponse('Admin_Dashboard Vue ✈️')

def account_settings(request):
	json_data = json.loads(request.body)
	id = json_data['id']

	user = COFUser.objects.get(id=id)

	user_data = {
		'firstName' : user.first_name,
		'lastName' : user.last_name,
		'email' : user.email,
		'phoneNumber' : user.phone_number
	}

	return JsonResponse(user_data)
