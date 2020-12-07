from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'), 
    path('login', views.login, name='login'),
	path('logout', views.logout, name='logout'),
	path('signup', views.signup, name='signup'),
	#path('admin_signup/', views.create_account, name='admin_signup'),
	path('dashboard', views.user_dashboard, name='user_dashboard'),
	path('MyCovidStatus', views.MyCovidStatus, name='MyCovidStatus'),
	path('accountsettings', views.account_settings, name='account_settings'),
	path('updatecovidstatus', views.updatecovidstatus, name='updatecovidstatus'),
	path('admindashboard', views.admin_dashboard, name='admin_dashboard'),
  path('sendcode', views.send_code, name='send_code'),
	path('checkcode', views.check_code, name='check_code'),
	path('resetpassword', views.reset_password, name='reset_password'),
	path('adminflightsearch', views.admin_flight_search, name='admin_flight_search'),
	path('registerflight', views.register_flight, name='register_flight')
    #path('', views.login, name='login'),
]
