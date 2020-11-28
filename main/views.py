from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import User
from django.contrib.auth import get_user_model
from .models import *
import json
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.http import JsonResponse

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
	
	if request.method == "POST":
	#Uses Django Authentication

		#These don't work:
		#email = request.POST['email']
		#password = request.POST['password']
		#email = request.POST.get('email')
		#password = request.POST.get('password')


		json_data = json.loads(request.body) #Put all contents of Post data into json_data variable
		email = json_data['email'] #Reference the email key/value from the json_data variable
		password = json_data['password']
		user = authenticate(username=email, password=password)
		if user is not None:
			#django_login(request,user)
			#return redirect('user_dashboard')
			return HttpResponse(user.id, status=200)
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

def admin_flight_search(request):
	json_data = json.loads(request.body)
	keys = json_data.keys()
	flights = Flight.objects.all()

	if 'from_date' in keys:
		from_date = json_data['from_date']
		from_date = from_date[0:4] + '-' + from_date[5:7] + '-' + from_date[8:10]
		flights = flights.filter(date__gte=from_date)

	if 'to_date' in keys:
		to_date = json_data['to_date']
		to_date = to_date[0:4] + '-' + to_date[5:7] + '-' + to_date[8:10]
		flights = flights.filter(date__lte=to_date)
	
	if 'departure_city' in keys:
		flights = flights.filter(departure_city=json_data['departure_city'])
	
	if 'arrival_city' in keys:
		flights = flights.filter(arrival_city=json_data['arrival_city'])

	if 'flight_id' in keys:
		flights = flights.filter(flight_id=json_data['flight_id'])
	
	if flights is None:
		count = 0
	else:
		count = flights.count()

	flight_jsons = []
	for flight in flights:
		flight_json = {
			"flightID" : flight.flight_id,
			"departureCity" : flight.departure_city,
			"arrivalCity" : flight.arrival_city,
			"date" : flight.date,
			"departureTime" : flight.departure_time,
			"arrivalTime" : flight.arrival_time,
			"covidCount" : flight.covid_count
		}
		flight_jsons.append(flight_json)

	flight_output = {
		"count" : count,
		"flights" : flight_jsons
	}

	return JsonResponse(flight_output)

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
