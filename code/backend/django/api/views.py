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

