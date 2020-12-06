from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from main.models import *
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
import datetime

class Command(BaseCommand):
    help = 'Fills database with test data'

    def handle(self, *args, **options):
        try:
            # Migrate commands
            call_command('makemigrations', 'main')
            call_command('migrate', 'main')
            call_command('makemigrations')
            call_command('migrate')

            # Add users
            self.stdout.write('============Users============')
            admin = get_user_model().objects.create_user(
                email='admin@admin.com',
                password='admin',
                first_name='admin',
                last_name='admin',
                phone_number='1231231234',
                covid_status='Unknown',
                last_update=None,
            )
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            print('admin',end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            alligator = get_user_model().objects.create_user(
                email='gogators@ufl.edu',
                password='GatorsRule!',
                first_name='Alli',
                last_name='Gator',
                phone_number='3523923261',
                covid_status='Unknown',
                last_update=None,
            )
            alligator.save()
            print('Alli Gator',end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            brady = get_user_model().objects.create_user(
                email='info@tb12sports.co',
                password='GoBucsNumber12',
                first_name='Tom',
                last_name='Brady',
                phone_number='9177040000',
                covid_status='Negative',
                last_update='2020-10-09',
            )
            brady.save()
            print('Tom Brady',end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            bastian = get_user_model().objects.create_user(
                email='edward.bastian@delta.com',
                password='nileToMedSea4',
                first_name='Edward',
                last_name='Bastian',
                phone_number='4047730305',
                covid_status='Negative',
                last_update='2020-10-27',
            )
            bastian.is_staff = True
            bastian.save()
            print('Edward Bastian',end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            matthews = get_user_model().objects.create_user(
                email='iloveparties@hotmail.com',
                password='itraveltoparty123',
                first_name='Jake',
                last_name='Matthews',
                phone_number='7043628925',
                covid_status='Positive',
                last_update='2020-10-27',
            )
            matthews.save()
            print('Jake Matthews',end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            # Flights
            self.stdout.write('============Flights============')
            today_date = datetime.datetime.now().date()

            one_day_past = datetime.timedelta(days=1)
            lax_jfk = Flight.objects.create(
                flight_id = 'DL1742',
                departure_city = 'LAX',
                arrival_city = 'JFK',
                date = str(today_date - one_day_past),
                departure_time = '15:00:00',
                arrival_time = '18:45:00',
                covid_count = 1
            )
            lax_jfk.save()
            print('LAX -> JFK', lax_jfk.date, '15:00:00', end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            four_days_future = datetime.timedelta(days=4)
            avl_pie = Flight.objects.create(
                flight_id = 'AA1380',
                departure_city = 'AVL',
                arrival_city = 'PIE',
                date = str(today_date + four_days_future),
                departure_time = '20:00:00',
                arrival_time = '21:30:00',
                covid_count = 0
            )
            avl_pie.save()
            print('AVL -> PIE', avl_pie.date, '20:00:00', end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            seven_days_future = datetime.timedelta(days=7)
            pie_avl = Flight.objects.create(
                flight_id = 'AA1029',
                departure_city = 'PIE',
                arrival_city = 'AVL',
                date = str(today_date + seven_days_future),
                departure_time = '12:00:00',
                arrival_time = '13:30:00',
                covid_count = 0
            )
            pie_avl.save()
            print('PIE -> AVL', pie_avl.date, '12:00:00', end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            twelve_days_past = datetime.timedelta(days=12)
            dtw_phx = Flight.objects.create(
                flight_id = 'NK6127',
                departure_city = 'DTW',
                arrival_city = 'PHX',
                date = str(today_date - twelve_days_past),
                departure_time = '17:00:00',
                arrival_time = '20:00:00',
                covid_count = 2
            )
            dtw_phx.save()
            print('DTW -> PHX', dtw_phx.date, '17:00:00', end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            # Recovery Combinations
            self.stdout.write('============Recovery Combinations============')
            matthews_code = RecoveryCombination.objects.create(
                email = matthews,
                recovery_code = 'DfXeNaPQ'
            )
            matthews_code.save()
            print('Jake Matthew\'s Recovery Combination', end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            # Surveys
            self.stdout.write('============Surveys============')
            alligator_survey = Survey.objects.create(
                results = 'Incomplete',
                fever_chills = False,
                cough = True,
                breathing_issues = False,
                fatigue = False,
                aches = False,
                headache = False,
                loss_taste_smell = False,
                sore_throat = True,
                congestion = False,
                nausea = False,
                diarrhea = False
            )
            alligator_survey.save()
            print('Alli Gator\'s Survey 1', end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            brady_survey = Survey.objects.create(
                results = 'Negative',
                fever_chills = False,
                cough = False,
                breathing_issues = False,
                fatigue = False,
                aches = False,
                headache = False,
                loss_taste_smell = False,
                sore_throat = False,
                congestion = False,
                nausea = False,
                diarrhea = False
            )
            brady_survey.save()
            print('Tom Brady\'s Survey 1', end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))
            brady_survey2 = Survey.objects.create(
                results = 'Negative',
                fever_chills = False,
                cough = False,
                breathing_issues = False,
                fatigue = False,
                aches = False,
                headache = False,
                loss_taste_smell = False,
                sore_throat = False,
                congestion = False,
                nausea = False,
                diarrhea = False
            )
            brady_survey2.save()
            print('Tom Brady\'s Survey 2', end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            bastian_survey = Survey.objects.create(
                results = 'Negative',
                fever_chills = False,
                cough = False,
                breathing_issues = False,
                fatigue = False,
                aches = False,
                headache = False,
                loss_taste_smell = False,
                sore_throat = False,
                congestion = False,
                nausea = False,
                diarrhea = False
            )
            bastian_survey.save()
            print('Edward Bastian\'s Survey 1', end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            matthews_survey = Survey.objects.create(
                results = 'Positive',
                fever_chills = True,
                cough = True,
                breathing_issues = True,
                fatigue = False,
                aches = False,
                headache = False,
                loss_taste_smell = False,
                sore_throat = False,
                congestion = False,
                nausea = False,
                diarrhea = False
            )
            matthews_survey.save()
            print('Jake Matthews\' Survey 1', end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            # Flights Taken
            self.stdout.write('============Flights Taken============')
            alligator_flight = FlightsTaken.objects.create(
                email = alligator,
                survey_id = alligator_survey,
                flight_id = avl_pie,
                row_seat = '16D'
            )
            alligator_flight.save()
            print('Alli Gator\'s Flight 1', end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            brady_flight = FlightsTaken.objects.create(
                email = brady,
                survey_id = brady_survey,
                flight_id = avl_pie,
                row_seat = '3A'
            )
            brady_flight.save()
            print('Tom Brady\'s Flight 1', end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))
            brady_flight2 = FlightsTaken.objects.create(
                email = brady,
                survey_id = brady_survey2,
                flight_id = pie_avl,
                row_seat = '5A'
            )
            brady_flight2.save()
            print('Tom Brady\'s Flight 2', end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            bastian_flight = FlightsTaken.objects.create(
                email = bastian,
                survey_id = bastian_survey,
                flight_id = lax_jfk,
                row_seat = '2D'
            )
            bastian_flight.save()
            print('Edward Bastian\'s Flight 1', end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

            matthews_flight = FlightsTaken.objects.create(
                email = matthews,
                survey_id = matthews_survey,
                flight_id = lax_jfk,
                row_seat = '14A'
            )
            matthews_flight.save()
            print('Jake Matthew\'s Flight 1', end=' ')
            self.stdout.write(self.style.SUCCESS('added!'))

        except IntegrityError:
            raise CommandError('Uniqueness IntegrityError. Please delete db.sqlite3 before running this command.')
