from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'), 
    path('login/', views.login, name='login'),
	path('logout/' views.logout, name='logout'),
	path('signup/', views.create_account, name='signup'),
	path('dashboard/', views.user_dashboard, name='user_dashboard')
]
