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
from operator import attrgetter
import string
import random
from datetime import date, timedelta
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

def covidstatus(request):
	json_data = json.loads(request.body)
	id = json_data['id']
	

	user = COFUser.objects.get(id=id)

	tickets = FlightsTaken.objects.filter(email=user.id) #References user id instead of email. Use filter instead of get
	flights = tickets.values("flight_id")
	planes = Flight.objects.filter(pk__in=flights) #All flights user has been on
	if not planes:
		last = 'None'
	else:
		last = planes.order_by('date').last().date
		
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
		surv.results="No"
		user.covid_status = "Negative"
		if json_data['fever_chills']:
			surv.fever_chills=True
			surv.results="Yes"
			user.covid_status="Positive"
		else:
			surv.fever_chills=False

		if json_data['cough']:
			surv.cough=True
			surv.results="Yes"
			user.covid_status="Positive"
		else:
			surv.cough=False

		if json_data['breathing_issues']:
			surv.breathing_issues=True
			surv.results="Yes"
			user.covid_status="Positive"
		else:
			surv.breathing_issues=False
			
		if json_data['fatigue']:
			surv.fatigue=True
			surv.results="Yes"
			user.covid_status = "Positive"
		else:
			surv.fatigue=False
			
		if json_data['aches']:
			surv.aches=True
			surv.results="Yes"
			user.covid_status = "Positive"
		else:
			surv.aches=False
			
		if json_data['headache']:
			surv.headache=True
			surv.results="Yes"
			user.covid_status = "Positive"
		else:
			surv.headache=False
			
		if json_data['loss_taste_smell']:
			surv.loss_taste_smell=True
			surv.results="Yes"
			user.covid_status = "Positive"
		else:
			surv.loss_taste_smell=False
			
		if json_data['sore_throat']:
			surv.sore_throat=True
			surv.results="Yes"
			user.covid_status = "Positive"
		else:
			surv.sore_throat=False

		if json_data['congestion']:
			surv.congestion=True
			surv.results="Yes"
			user.covid_status = "Positive"	
		else:
			surv.congestion=False

		if json_data['nausea']:
			surv.nausea=True
			surv.results="Yes"
			user.covid_status = "Positive"
		else:
			surv.nausea=False

		if json_data['diarrhea']:
			surv.diarrhea=True
			surv.results="Yes"
			user.covid_status = "Positive"
		else:
			surv.diarrhea=False

		user.last_update = date.today()		
		user.save()
		surv.save()

		user_data = {
			'covidstatus' : user.covid_status
		}

		# Notifies other passengers if necessary
		if user.covid_status == 'Positive': # need to update other passengers
			flights_taken = FlightsTaken.objects.filter(email=user)
			for flight in flights_taken:
				flight = flight.flight_id
				if flight.date >= date.today() - timedelta(days=14) and flight.date <= date.today(): # if flight was within 14 days
					other_users = FlightsTaken.objects.exclude(email=user).filter(flight_id=flight) # other users on same flight

					for user in other_users: # emails users on same flight
						user = user.email

						# Sends SMS (Twilio)
						try:
							twilio_client.messages.create(
							body=('Hello, ' + user.first_name + ' ' + user.last_name + '. Another passenger on your recent flight ' +
									flight.flight_id + ' now has COVID-19. Please quarantine and take other precautions as necessary.'),
							from_='+12185304600',
							to=('+1'+user.phone_number)
							)
						except TwilioRestException:
							print('Error texting user')
						# Sends email (SendGrid)
						try:
							email = Mail(
							from_email='CovidOnFlight@gmail.com',
							to_emails=user.email,
							subject='Welcome to Covid on Flight!',
							html_content=('<h2><strong>Hello, ' + user.first_name + ' ' + user.last_name + '. ' + 
								'</strong></h2><p>Someone on your recent flight ' + flight.flight_id + ' now has COVID-19. ' +
								'Please quarantine and take other precautions as necessary.</p>' +
								'<p>Thank you for protecting others,</p>' + 
								'<p>Covid on Flight ✈️</p>'
								)
							)
							sendgrid_client.send(email)
						except Exception as e:
							print(e)
			


		return JsonResponse(user_data)

	return HttpResponse('Cannot update')


def MyCovidStatus(request):
	json_data = json.loads(request.body)
	id = json_data['id']
	user = COFUser.objects.get(id=id)
	flightids = FlightsTaken.objects.filter(email=user.email).values(flight_id)
	flights = Flight.objects.filter(flight_id__in=flightids)
	lastFlight = min(flights,key=attrgetter('date'))

	if request.method == "POST":
		stat = json_data['covid_status']
		user.covid_status = stat
		user.save()

	user_data = {
		'status' : user.covid_status,
		'last_update' : user.last_update,
		'last_flight' : lastFlight
	}

	return JsonResponse(user_data)

def account_settings(request):
	json_data = json.loads(request.body)
	id = json_data['id']

	user = COFUser.objects.get(id=id)

	if request.method == "POST":
		fname = json_data['first_name']
		lname = json_data['last_name']
		nemail = json_data['email']
		user.first_name = fname
		user.last_name = lname
		user.email = nemail
		user.save()

	user_data = {
		'firstName' : user.first_name,
		'lastName' : user.last_name,
		'email' : user.email,
		'phoneNumber' : user.phone_number
	}

	return JsonResponse(user_data)

def register_flight(request):
	json_data = json.loads(request.body)
	id = json_data['id']
	row = json_data['seat']
	reservation_number= json_data['reservation_number']
	flight_id= json_data['flight_id']
	from_date= json_data['from_date']
	to_date= json_data['to_date']
	departure_city= json_data['departure_city']
	arrival_city= json_data['arrival_city']

	user_object = COFUser.objects.get(id=id)

	flight = Flight.objects.filter(flight_id=flight_id)
	if not flight: # if the flight doesn't already exist
		flight = Flight.objects.create(
					flight_id=flight_id,
					departure_city = departure_city,
					arrival_city= arrival_city,
					date= from_date,
					arrival_date= to_date,
					covid_count = 0,
		)
		flight.save()

	survey = Survey.objects.all().first()

	Flight_taken=FlightsTaken.objects.create(
		email=user_object,
		survey_id=survey,
		flight_id=flight,
		row_seat=row,
	)
	Flight_taken.save()

	return HttpResponse(status=200)

	
def send_code(request):
	if request.method == "POST":
		json_data = json.loads(request.body)
		email = json_data['email']
		
		user = COFUser.objects.get(email=email)
		if user:
			# Sends email (SendGrid)
			recovery_code = random.choices(string.ascii_letters, k=6)
			recovery_code = "".join(recovery_code)
			rc = RecoveryCombination.objects.create(email=user, recovery_code=recovery_code)
			rc.save()
			try:
				email = Mail(
					from_email='CovidOnFlight@gmail.com',
					to_emails=email,
					subject='Reset Password',
					html_content=(
								'<h2><strong>Hi, ' + user.first_name + ' ' + user.last_name + '! ✈️</strong></h2><p>It appears that you have forgotten your password. Please use this code to reset your password: </p>' + recovery_code)
				)
				sendgrid_client.send(email)
			except Exception as e:
				print(e)

			return HttpResponse(recovery_code, status=200)

		else:
			return HttpResponse("User does not exist :(", status=401)


def check_code(request):
	if request.method == "POST":
		json_data = json.loads(request.body)
		verification_code=json_data['code']
		email = json_data['email']

		#RecoveryCombination requires an actual user to retrieve the email. As Such a variable must be created that
		#stores the user. That user can then be used for RecoveryCombination.
		user_object = COFUser.objects.get(email=email)
		user = RecoveryCombination.objects.get(email=user_object)#This pulls the email 'key' from the COFUser object
		if user:
			if verification_code == user.recovery_code:
				RecoveryCombination.objects.filter(email=user_object).delete()
				return HttpResponse(verification_code, status=200)

		else:
			return HttpResponse("User does not exist :(", status=401)
def reset_password(request):
	if request.method == "POST":
		json_data = json.loads(request.body)
		password=json_data['password']
		email = json_data['email']


		user = COFUser.objects.get(email=email)

		if user:
			user.set_password(password)
			user.save()
			return HttpResponse("Password Changed", status=200)

		else:
			return HttpResponse("An error has occured", status=401)

