from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import COFUser, RecoveryCombination, FlightsTaken, Flight, Survey
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

# User Creation Form for Django's Admin Site
class COFUserCreationForm(forms.ModelForm):
    # Gathers password and password confirmation from form
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password' , widget=forms.PasswordInput)

    # Ensures password confirmation successful and returns if so
    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords aren\'t matching. Please try again.')
        return confirm_password

    def save(self, commit=True):
        # Creates user object and sets its password
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        # Checks if committing to database
        if commit:
            user.save()

        return user

    # COFUser object's attributes
    class Meta:
        model = COFUser
        fields = ('email', 'password', 'first_name', 'last_name', 'phone_number', 'covid_status', 'last_update', 'is_staff')


 # User Update Form for Django's Admin Site   
class COFUserUpdateForm(forms.ModelForm):
    # Not allowing password changing from admin portal
    # "python3 manage.py changepassword email" works if necessary
    password = ReadOnlyPasswordHashField()

    # COFUser object's attributes
    class Meta:
        model = COFUser
        fields = ('email', 'password', 'first_name', 'last_name', 'phone_number', 'covid_status', 'last_update', 'is_staff')

    def clean_password(self):
        return self.initial['password']


class COFUserAdmin(UserAdmin):
    # Sets the forms to be utilized by admin site to those created above
    form = COFUserUpdateForm
    add_form = COFUserCreationForm

    # The list of COFUser objects will contain the fields below
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'covid_status', 'last_update', 'is_staff')
    fieldsets = (
        (None, {'fields' : ('email', 'password', 'first_name', 'last_name', 'phone_number', 'covid_status', 'last_update')}),
        ('Permissions', {'fields' : ('is_staff',)})
    )

    # Specifies fields used when creating a COFUser object
    add_fieldsets = (
        (None, {
            'classes' : ('wide',),
            'fields' : ('email', 'password', 'confirm_password', 'first_name', 'last_name', 'phone_number', 'covid_status', 'is_staff'),
        }),
    )


    search_fields = ('email',)
    ordering = ('email',)


# Registers models to Django's Admin Site
admin.site.register(COFUser, COFUserAdmin)
admin.site.register(RecoveryCombination)
admin.site.register(FlightsTaken)
admin.site.register(Flight)
admin.site.register(Survey)
