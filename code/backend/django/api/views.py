from django.shortcuts import render
from django.http import HttpResponse
from .forms import RegisterForm
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def index(request):
	return HttpResponse('Hello, world!')

@csrf_exempt
def register(request):
	print(request.method)
	if( request.method == 'POST' ):
		print('post received')
		form = RegisterForm(request.POST)
		if(form.is_valid()):
			form.save()
			return HttpResponse('User created!')
		return HttpResponse(form.errors)
	else:
		return HttpResponse('Invalid request method!')

