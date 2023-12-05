from django.conf import settings
from django.db import models
from django.db.models import Model
from django.contrib.auth.models import User

#ereditando dal modello User di Django
class Users(models.Model): # Django crea in automatico il campo id
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    created_on = models.TimeField()
    last_login = models.TimeField()
    elo_points = models.IntegerField(default=1440)#Utilizziamo l'ELO FSI
    n_wins_loc = models.IntegerField(default=0) #against boot
    n_draws_loc = models.IntegerField(default=0) #against boot
    n_lost_loc = models.IntegerField(default=0) #against boot

class Matches(models.Model):
    player1 = models.CharField(max_length=50)
    player2 = models.CharField(max_length=50)
    winner = models.CharField(max_length=50)
    loser = models.CharField(max_length=50)
    draw = models.BooleanField()
