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

#TODO: install the 'google-auth' library

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


def userLogout(request):
	logout(request)
	return HttpResponse('User logged out successfully!', content_type='text/plain')

#cheks if user a user is currently logged in returns the username if so
def checkLogin(request):
	if request.user.is_authenticated:
		return HttpResponse(f'user {request.user.username} is currently logged in', content_type='text/plain')
	else:
		return HttpResponse('No user logged in', content_type='text/plain')

#verification of google id token
def googleID(request):
    
    id_token_string = request.POST.get('id_token')

    client_id = '613529435942-nfjfd37rhd01pbqjrkg8tfqa0uvdildg.apps.googleusercontent.com'

    try:
        # Verify the ID Token
        id_info = id_token.verify_oauth2_token(id_token_string, requests.Request(), client_id)

        user_email = id_info.get('email')
        user_name = id_info.get('name')

        # Check if the user with the given email already exists in your database
        user, created = User.objects.get_or_create(email=user_email, defaults={'username': user_email})
        
        user = authenticate(request, username=user.email, password=None)
        login(request, user)

        return JsonResponse({'success': True, 'user_email': user_email, 'user_name': user_name})
    
    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)})
	
	
def player_loc_stats(request, player_email):
	result = ti.get_player_loc_stats(player_email)
	return JsonResponse(result)

def player_username(request, player_email):
	result = ti.get_player_username(player_email)
	return JsonResponse({'username': result})

def leaderboard(request):
    leaderboard_data = ti.get_leaderboard()
    return JsonResponse({'leaderboard': leaderboard_data})