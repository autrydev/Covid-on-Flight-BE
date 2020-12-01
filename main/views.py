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
from datetime import date

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
	json_data = json.loads(request.body)
	id = json_data['id']

	# Collect previous flight history
	email = COFUser.objects.get(id=id).email
	flights_taken = FlightsTaken.objects.select_related('email', 'flight_id').filter(email=id)

	future_flights_json = []
	prev_flights_json = []
	
	if flights_taken: # if the user has taken a flight
		for flight_taken in flights_taken:
			flight = flight_taken.flight_id

			if flight.covid_count > 0:
				status = 'Positive'
			else:
				status = 'Negative'

			flight_json = {
				"flight_id" : flight.flight_id,
				"date" : flight.date,
				"departure_city" : flight.departure_city,
				"arrival_city" : flight.arrival_city,
				"status" : status
			}

			if flight.date < date.today(): # if in the past
				prev_flights_json.append(flight_json)
			else: #if today or in the future
				future_flights_json.append(flight_json)

	user = COFUser.objects.get(id=id)

	dash_data = {
		'firstname': user.first_name,
		'prev_flights': prev_flights_json,
		'future_flights': future_flights_json
	}

	return JsonResponse(dash_data, safe=False)
	

def admin_dashboard(request):
	# Get counts in all statuses
	unknown = 0
	negative = 0
	positive = 0
	
	users = COFUser.objects.all()
	for user in users:
		if user.covid_status == 'Unknown':
			unknown += 1
		elif user.covid_status == 'Negative':
			negative += 1
		elif user.covid_status == 'Positive':
			positive += 1

	# Get all previous flights that had COVID-positive passengers (count > 0)
	flights = Flight.objects.all()
	positive_flights = []
	for flight in flights:
		if flight.date < date.today() and flight.covid_count > 0:
			flight_json = {
				"flight_id" : flight.flight_id,
				"date" : flight.date,
				"departure_city" : flight.departure_city,
				"arrival_city" : flight.arrival_city,
				"count" : flight.covid_count
			}

			positive_flights.append(flight_json)

	output = {
		'Unknown' : unknown,
		'Negative' : negative,
		'Positive' : positive,
		'positive_flights' : positive_flights
	}

	return JsonResponse(output)

def admin_flight_search(request):
	json_data = json.loads(request.body)
	keys = json_data.keys()
	flights = Flight.objects.all()

	if json_data['from_date'] is not None:
		from_date = json_data['from_date']
		from_date = from_date[0:4] + '-' + from_date[5:7] + '-' + from_date[8:10]
		flights = flights.filter(date__gte=from_date)

	if json_data['to_date'] is not None:
		to_date = json_data['to_date']
		to_date = to_date[0:4] + '-' + to_date[5:7] + '-' + to_date[8:10]
		flights = flights.filter(date__lte=to_date)
	
	if json_data['departure_city'] is not None:
		flights = flights.filter(departure_city=json_data['departure_city'])
	
	if json_data['arrival_city'] is not None:
		flights = flights.filter(arrival_city=json_data['arrival_city'])

	if json_data['flight_id'] is not None:
		flights = flights.filter(flight_id=json_data['flight_id'])

	if json_data['covidStatus'] is not None:
		if json_data['covidStatus'] == True:
			flights = flights.filter(covid_count__gt=0)
		elif json_data['covidStatus'] == False:
			flights = flights.filter(covid_count=0)

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
		"flights" : flight_jsons
	}

	return JsonResponse(flight_output)

def account_settings(request):
	json_data = json.loads(request.body)
	id = json_data['id']

	user = COFUser.objects.get(id=id)

	if "first_name" in json_data:
		fname = json_data['first_name']
		user.first_name = fname
	if "last_name" in json_data:
		lname = json_data['last_name']
		user.last_name = lname
	if "email" in json_data:
		nemail = json_data['email']
		user.email = nemail
	if "phone_number" in json_data:
		nphone = json_data['phone_number']
		user.phone_number = nphone
	
	user.save()

	user_data = {
		'firstName' : user.first_name,
		'lastName' : user.last_name,
		'email' : user.email,
		'phoneNumber' : user.phone_number
	}

	return JsonResponse(user_data)