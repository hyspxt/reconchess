import os
import sys

api_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'api'))
sys.path.append(api_path)

from api.server import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
#os.environ["DJANGO_SETTINGS_MODULE"] = "server.settings"

from models import *
from api.modles import Users
from api.modles import Matches

User_object = Users()
User_object.save()

Matches_object = Matches()
Matches_object.save()

# all(), get(), filter(), exclude()
#this returns the first 5 objects
#Users.objects.all()[:5]

#per filtrare informazioni del singolo utente
#q = User.objects.filter(username="esempio_utente").filter(password = "password_segreta")

#ereditando dal modello User di Django
#u = User.objects.get(username="esempio_utente")
#player1_elo = u.users.elo_points
#print(q)
#print(u)

#visualizza la classifica dei giocatori WLD
def get_players_stats():
    # Logica della query
    queryset = (
    Matches.objects
    .annotate(
        result=Case(
            When(winner=F('player1'), then=Value('win')),
            When(winner=F('player2'), then=Value('win')),
            When(loser=F('player1'), then=Value('loss')),
            When(loser=F('player2'), then=Value('loss')),
            When(draw=True, then=Value('draw')),
            default=None,
            output_field=CharField()
        )
    )
    .values('result', 'player1', 'player2')  # Ottieni i dati necessari per l'UNION ALL
    .annotate(player_name=Coalesce('player1', 'player2'))  # Usa Coalesce per ottenere il nome del giocatore
    .values('player_name', 'result')  # Ottieni i dati necessari per l'UNION ALL
    )  
    # Query finale
    result = (
        queryset
        .values('player_name')
        .annotate(
            wins=Count(Case(When(result='win', then=Value(1)), default=None, output_field=IntegerField())),
            draws=Count(Case(When(result='draw', then=Value(1)), default=None, output_field=IntegerField())),
            losses=Count(Case(When(result='loss', then=Value(1)), default=None, output_field=IntegerField()))
        )
    )[:10]  # Limita i risultati ai primi 10 record per la leaderboard
    return result

#stats = get_player_stats()
#print(stats)

#visualizza le statistiche del singolo giocatore: vittorie, sconfitte e pareggi contro atri giocatori
def get_player_stats(player_name):
    wins = Matches.objects.filter(Q(player1=player_name, winner=player_name) | Q(player2=player_name, winner=player_name)).count()

    lost = Matches.objects.filter(Q(player1=player_name, loser=player_name) | Q(player2=player_name, loser=player_name)).count()

    draws = Matches.objects.filter((Q(player1=player_name) | Q(player2=player_name)) & Q(draw=True)).count()

    elo_points = Users.objects.get(user__username=player_name).elo_points

    return {'n_wins': wins, 'n_lost': lost, 'n_draws': draws, 'elo_points': elo_points}

def get_player_loc_stats(player_name):
    player = Users.objects.get(user__username=player_name)
        
    # Ottieni le statistiche del giocatore
    name = player_name
    wins = player.n_wins_loc
    lost = player.n_lost_loc
    draws = player.n_draws_loc

    # Restituisci un dizionario con le informazioni
    return {
            'player_name':name,
            'n_wins_loc': wins,
            'n_lost_loc': lost,
            'draws_loc': draws
    }

#aggiorna il numero di w/l/d contro bot nella tabella Users 
def update_loc_stats(player_name, win, draw):
    u = User.objects.get(username=player_name)
    if win:
        u.n_wins_loc += 1
    elif not win and not draw:
        u.n_lost_loc += 1
    else:  # draw=True
        u.n_draws_loc += 1
    u.save()

#da chiamare alla fine di una partita contro un altro giocatore
def update_leaderboard(p1, p2, win, los, dr):
     # Ora inseriamo i dati nella tabella Matches
    match = Matches.objects.create(
        player1=p1,
        player2=p2,
        winner=p1 if win == p1 else (p2 if win == p2 else None),
        loser=p2 if los == p2 else (p1 if los == p1 else None),
        draw= True if dr == True else False
    )

    # Salva l'oggetto Matches nel database
    match.save()

#calcola i punti elo alla fine di ogni partita per il player1; Utilizziamo l'ELO FSI
#Vittoria = 1 punto
#Patta = 0,5 punti
#Sconfitta  = 0 punti.

def calculate_elo(elo_points_p1, elo_points_p2, win, los, dr):
    K=30 #secondo rergole FSI
    #calcolo punteggio attuale
    if win: actual_score = 1
    elif los: actual_score = 0
    else: actual_score = 0.5 #draw
    #calcolo punteggio atteso
    rb = elo_points_p2
    ra = elo_points_p1
    expected_score = 1 / (1+10**((rb-ra)/400))
    new_elo=elo_points_p1+K*(actual_score-expected_score)
    return new_elo

#da chiamare dopo aver sfidato un umano
def update_elo(player_name, opponent, win, los, dr):
    u = User.objects.get(username = player_name)
    v = User.objects.get(username = opponent)
    new_elo_points = calculate_elo(u.users.elo_points, v.users.elo_points, win, los, dr)
    #aggiorno punti del giocatore in tabella Users
    u.elo_points = new_elo_points

def social_log(mail):
    try:
        # Cerca un utente nel modello User associato a Users
        user = User.objects.get(email=mail) #metti la mail da user anzichè email=
        # Trova l'istanza di Users associata a questo utente
        users_instance = Users.objects.get(user=user)
        return True
    except User.DoesNotExist or Users.DoesNotExist:
        # L'utente o l'istanza di Users non esiste
        return False