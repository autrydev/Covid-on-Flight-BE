from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'), 
    path('login', views.login, name='login'),
	path('logout', views.logout, name='logout'),
	path('signup', views.signup, name='signup'),
	#path('admin_signup/', views.create_account, name='admin_signup'),
	path('dashboard', views.user_dashboard, name='user_dashboard'),
	path('accountsettings', views.account_settings, name='account_settings'),
	path('sendcode', views.send_code, name='send_code'),
	path('checkcode', views.check_code, name='check_code')
    #path('', views.login, name='login'),
]
