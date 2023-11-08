from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
	
	#displays admin page
	path('admin/', admin.site.urls),

	#allows user to register, returns plaintext messages indicating success or failure	
	path('register/', views.register, name='register'),

]
