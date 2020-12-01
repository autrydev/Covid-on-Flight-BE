from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'), 
    path('login', views.login, name='login'),
	path('logout', views.logout, name='logout'),
	path('signup', views.signup, name='signup'),
	#path('admin_signup/', views.create_account, name='admin_signup'),
	path('dashboard', views.user_dashboard, name='user_dashboard'),
	path('covidstatus', views.covidstatus, name='covidstatus'),
	path('updatecovidstatus', views.updatecovidstatus, name='updatecovidstatus'),
	path('accountsettings', views.account_settings, name='account_settings'),
	path('adminflightsearch', views.admin_flight_search, name='admin_flight_search'),
    #path('', views.login, name='login'),
]
