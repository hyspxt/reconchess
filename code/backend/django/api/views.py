from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from .forms import RegisterForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

def register(request):
	if( request.method == 'POST' ):
		try:
			form = RegisterForm(request.POST)
			if(form.is_valid()):
				form.save()
				return HttpResponse('User created successfully!', content_type='text/plain')
			#send error message
			return HttpResponseBadRequest(content=form.errors.as_ul())
		except Exception:
			return HttpResponseBadRequest(content="something went wrong, please try again", content_type='text/plain')
	else:
		return HttpResponseBadRequest(content='Invalid request method!', content_type='text/plain')

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
			error = str(e)
			return HttpResponseBadRequest(content=error, content_type='text/plain')
	else:
		return HttpResponseBadRequest(content='Invalid request method!', content_type='text/plain')


def checkLogin(request, username:str):
	if User.objects.get(username=username).is_authenticated:
		return HttpResponse('User is logged in!', content_type='text/plain')