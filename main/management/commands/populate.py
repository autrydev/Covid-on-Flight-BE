from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from main.models import *
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

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
        except IntegrityError:
            raise CommandError('Uniqueness IntegrityError. Please delete db.sqlite3 before running this command.')
