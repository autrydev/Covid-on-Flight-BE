from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'), 
    path('login/', views.login, name='login'),
	path('logout/' views.logout, name='logout'),
	path('create_account/', views.create_account, name='create_account'),
	path('dashboard/', views.user_dashboard, name='user_dashboard')
]
