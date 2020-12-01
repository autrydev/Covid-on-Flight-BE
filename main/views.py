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
from time import gmtime, strftime

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

def covidstatus(request):
	json_data = json.loads(request.body)
	id = json_data['id']
	last = 'None'

	user = COFUser.objects.get(id=id)

	tickets = FlightsTaken.objects.filter(email=user.id) #References user id instead of email. Use filter instead of get
	flights = tickets.values("flight_id")
	planes = Flight.objects.filter(pk__in=flights) #All flights user has been on
	last = planes.order_by('date').last().date
	
	#cplanes = FlightsTaken.objects.filter(flight_id__in=planes)
	#ctickets = cplanes.values("email")
	#infected = COFUser.objects.filter(pk__in=ctickets)
	#if user.covid_status == "Positive" or user.covid_status == "positive" :

	#	# Sends SMS (Twilio)
	#		try:
	#			twilio_client.messages.create(
	#			body=('Thank you for signing up for Covid on Flight, ' + first_name + ' ' + last_name + '!'),
	#			from_='+12185304600',
	#			to=('+1'+user.phone_number)
	#			)
	#		except TwilioRestException:
	#			print('Error texting user')
	#
			# Sends email (SendGrid)
	#		try:
	#			email = Mail(
	#			from_email='CovidOnFlight@gmail.com',
	#			to_emails=user.email,
	#			subject='Welcome to Covid on Flight!',
	#			html_content=('<h2><strong>Hi, ' + first_name + ' ' + last_name + '! ✈️</strong></h2><p>Welcome to Covid on Flight! We look forward to making your travels safer.</p>')
	#			)
	#			sendgrid_client.send(email)
	#		except Exception as e:
	#			print(e)
		
	user_data = {
		'covidstatus' : user.covid_status,
		'lastupdate' : user.last_update,
		'lastflight' : last
	}

	return JsonResponse(user_data)

def updatecovidstatus(request):
	json_data = json.loads(request.body)
	id = json_data['id']
	user = COFUser.objects.get(id=id)

	if request.method == "POST":
		surv = Survey()
		surv.test_results='No'
	if "covid_test" in json_data:
		if json_data['covid_test'] == 'Yes':
			surv.covid_test=True
		else:
			surv.covid_test=False
	if "fever_chills" in json_data:
		if json_data['fever_chills'] == 'True' or json_data['fever_chills'] == 'true':
			surv.fever_chills=True
			surv.test_results="Yes"
			user.covid_status = "Positive"	
	if "cough" in json_data:
		if json_data['cough'] == 'True' or json_data['cough'] == 'true':
			surv.cough=True
			surv.test_results="Yes"
			user.covid_status = "Positive"	
	if "breathing_issues" in json_data:
		if json_data['breathing_issues'] == 'True' or json_data['breathing_issues'] == 'true':
			surv.breathing_issues=True
			surv.test_results="Yes"
			user.covid_status = "Positive"	
	if "aches" in json_data:
		if json_data['aches'] == 'True' or json_data['aches'] == 'true':
			surv.aches=True
			surv.test_results="Yes"
			user.covid_status = "Positive"	
	if "headache" in json_data:
		if json_data['headache'] == 'True' or json_data['headache'] == 'true':
			surv.headache=True
			surv.test_results="Yes"
			user.covid_status = "Positive"	
	if "loss_taste_smell" in json_data:
		if json_data['loss_taste_smell'] == 'True' or json_data['loss_taste_smell'] == 'true':
			surv.loss_taste_smell=True
			surv.test_results="Yes"
			user.covid_status = "Positive"	
	if "sore_throat" in json_data:
		if json_data['sore_throat'] == 'True' or json_data['sore_throat'] == 'true':
			surv.sore_throat=True
			surv.test_results="Yes"
			user.covid_status = "Positive"	
	if "congestion" in json_data:
		if json_data['congestion'] == 'True' or json_data['congestion'] == 'true':
			surv.congestion=True
			surv.test_results="Yes"
			user.covid_status = "Positive"		
	if "nausea" in json_data:
		if json_data['nausea'] == 'True' or json_data['nausea'] == 'true':
			surv.nausea=True
			surv.test_results="Yes"
			user.covid_status = "Positive"
	if "diarrhea" in json_data:
		if json_data['diarrhea'] == 'True' or json_data['diarrhea'] == 'true':
			surv.diarrhea=True
			surv.test_results="Yes"
			user.covid_status = "Positive"

	user.last_update = datetime.datetime.now()		
	user.save()
	surv.save()

	user_data = {
		'covidstatus' : user.covid_status
	}

	return JsonResponse(user_data)


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
