from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
	
	#displays admin page
	path('admin/', admin.site.urls),

	#allows user to register, returns plaintext messages indicating success or failure	
	path('register/', views.register, name='register'),

	#use django's built in authenication system
	path('login/', views.userLogin, name='login'),

	path('logout/', views.userLogout, name='logout'),

	path('check_login/', views.checkLogin, name='check_login'),
    
	path('player_loc_stats/<str:mail>/', views.player_loc_stats, name='player_loc_stats'),

	path('leaderboard/', views.leaderboard, name='leaderboard'),
	
	path('social_log/<str:mail>/', views.social_log, name='social_log')
]
