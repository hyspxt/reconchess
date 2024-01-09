from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from .forms import RegisterForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from google.auth.transport import requests
from google.oauth2 import id_token
from . import tables_interactions as ti
from .models import Users
from django.utils import timezone
import json

SESSION_KEY = 'user_id'

@csrf_exempt
def register(request):
	if( request.method == 'POST' ):
		try:
			form = RegisterForm(request.POST)
			if(form.is_valid()):
				form.save()
				return HttpResponse('User created successfully!', content_type='text/plain')
			#send error message
			return HttpResponseBadRequest(content=form.errors.as_text(), content_type='text/plain')
		except Exception as e:
			print(str(e))
			return HttpResponseBadRequest(content="something went wrong, please try again", content_type='text/plain')
	else:
		return HttpResponseBadRequest(content='Invalid request method!', content_type='text/plain')

@csrf_exempt
def userLogin(request):
	if( request.method == 'POST' ):
		try:
			email = request.POST['email']
			password = request.POST['password']
			#find the username associated with the unique email in the database
			user = User.objects.get(email=email)
			user = authenticate(request, username=user.username, password=password)
			if user is not None:
				login(request, user)
				return HttpResponse('User logged in successfully!', content_type='text/plain')
			else:
				return HttpResponseBadRequest(content='Invalid email or password!', content_type='text/plain')
		except Exception as e:
			print(str(e))
			return HttpResponseBadRequest(content="something went wrong, please try again", content_type='text/plain')
	else:
		return HttpResponseBadRequest(content='Invalid request method!', content_type='text/plain')

@csrf_exempt
def userLogout(request):
	logout(request)
	if  SESSION_KEY in request.session:
		del request.session[SESSION_KEY]
	return HttpResponse('User logged out successfully!', content_type='text/plain')

#cheks if user a user is currently logged in returns the username if so
def checkLogin(request):
	if request.user.is_authenticated:
		return JsonResponse({'loggedIn': True, 'username': request.user.username, 'email': request.user.email})
	elif SESSION_KEY in request.session:
		user = User.objects.get(id=request.session[SESSION_KEY])
		return JsonResponse({'loggedIn': True, 'username': user.username, 'email': user.email})
	else:
		return JsonResponse({'loggedIn': False})
    
#verification of google id token
@csrf_exempt
def googleID(request):
	data = json.loads(request.body)
	id_token_string = data.get('id_token')

	client_id = '613529435942-nfjfd37rhd01pbqjrkg8tfqa0uvdildg.apps.googleusercontent.com'
    
	try:
		# Verify the ID Token
		id_info = id_token.verify_oauth2_token(id_token_string, requests.Request(), client_id)
		user_email = id_info.get('email')
		username = generate_username(user_email)

		# Check if the user with the given email already exists in your database
		user, created = User.objects.get_or_create(email=user_email)
		if created:
			user.username = username
			user.save()
  
        # Manually log in the user by setting the user in the request's session
		request.session[SESSION_KEY] = user.id
        
		return JsonResponse({'success': True,  'username': user.username, 'email': user_email})

	except ValueError as e:
		return JsonResponse({'success': False, 'error': str(e)})


#generate a unique username from the given email
def generate_username(email):
	username = email.split('@')[0]
	count = User.objects.filter(username__startswith=username).count()
	if count:
		username = '{}{}'.format(username, count + 1)
	return username

def player_loc_stats(request, player_username):
	result = ti.get_player_loc_stats(player_username)
	return JsonResponse(result)

def player_username(request, mail):
	result = ti.get_player_username(mail)
	return JsonResponse({'username': result})

def leaderboard(request):
    leaderboard_data = ti.get_leaderboard()
    return JsonResponse({'leaderboard': leaderboard_data})