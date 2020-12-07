from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Creates customer Manager for COFUser object because the regular User object is being extended
class COFUserManager(BaseUserManager):
    # Creates a regular User and saves into the database
    def create_user(self, email, password, first_name, last_name, phone_number, covid_status='Unknown', last_update=None):
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            covid_status=covid_status,
            last_update=last_update,
            is_staff=False,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user
    
    # Creates an administrative User and saves into the database
    def create_superuser(self, email, password, first_name, last_name, phone_number, covid_status='Unknown', last_update=None):
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            covid_status=covid_status,
            last_update=last_update,
            is_staff=True,
            is_superuser=True
        )

        user.set_password(password)
        user.save(using=self._db)

        return user


# Defines the COFUser object model
class COFUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    covid_status = models.CharField(
        max_length=8,
        default='Unknown',
    )
    last_update = models.DateField(null=True, blank=True, default='None')

    objects = COFUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    def __str__(self):
        return self.email


# Defines the RecoveryCombination object model
class RecoveryCombination(models.Model):
    email = models.ForeignKey(
        'COFUser',
        on_delete=models.CASCADE
    )
    recovery_code = models.CharField(max_length=12) # TODO: Hash recovery codes


# Defines the Survey object model
class Survey(models.Model):
    # IDs already automatically created by Django
    results = models.CharField(max_length=20, blank=True)
    # The following are Yes/No's:
    fever_chills = models.BooleanField()
    cough = models.BooleanField()
    breathing_issues = models.BooleanField()
    fatigue = models.BooleanField()
    aches = models.BooleanField()
    headache = models.BooleanField()
    loss_taste_smell = models.BooleanField()
    sore_throat = models.BooleanField()
    congestion = models.BooleanField()
    nausea = models.BooleanField()
    diarrhea = models.BooleanField()


# Defines the Flight object model
class Flight(models.Model):
    flight_id = models.CharField(max_length=20) # TODO: Possibly change length
    departure_city = models.CharField(max_length=35)
    arrival_city = models.CharField(max_length=35)
    date = models.DateField()
    arrival_date = models.DateField()
    covid_count = models.PositiveIntegerField(default=0)


# Defines the FlightsTaken object model
class FlightsTaken(models.Model):
    email = models.ForeignKey(
        'COFUser',
        on_delete=models.CASCADE
    )
    survey_id = models.ForeignKey(
        'Survey',
        on_delete=models.CASCADE
    )
    flight_id = models.ForeignKey(
        'Flight',
        on_delete=models.CASCADE
    )
    row_seat = models.CharField(max_length=8)
