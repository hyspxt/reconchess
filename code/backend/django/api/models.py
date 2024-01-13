from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

#ereditando dal modello User di Django
class Users(models.Model): # Django crea in automatico il campo id
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    created_on = models.TimeField(default=timezone.now)
    elo_points = models.IntegerField(default=1440)#Utilizziamo l'ELO FSI
    n_wins = models.IntegerField(default=0)
    n_draws = models.IntegerField(default=0)
    n_lost = models.IntegerField(default=0) 

class Matches(models.Model):
    room_name = models.CharField(max_length=50, blank=True)
    player1 = models.CharField(max_length=50, blank=True)
    player2 = models.CharField(max_length=50, blank=True)
    winner = models.CharField(max_length=50, blank=True)
    loser = models.CharField(max_length=50, blank=True)
    draw = models.BooleanField(null=True)
    seconds = models.IntegerField(null=True)
    finished = models.BooleanField(default=False)
