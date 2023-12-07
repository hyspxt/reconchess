#import os
#import sys

#api_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'api'))
#sys.path.append(api_path)

#from api.server import settings

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
#os.environ["DJANGO_SETTINGS_MODULE"] = "server.settings"
from .models import Users, Matches
from django.db.models import F

def get_player_loc_stats(player_name):
    player = Users.objects.get(user__username=player_name)
        
    # Ottieni le statistiche del giocatore
    name = player_name
    wins = player.n_wins
    lost = player.n_lost
    draws = player.n_draws

    # Restituisci un dizionario con le informazioni
    return {
            'player_name':name,
            'n_wins': wins,
            'n_lost': lost,
            'n_draws': draws
    }

def get_leaderboard():
    # Ottenere i dati per i primi 10 giocatori
    players_data = Users.objects.annotate(
        player_name=F('user__username'),
        wins=F('n_wins'),
        draws=F('n_draws'),
        losses=F('n_lost'),
    ).values('player_name', 'wins', 'draws', 'losses')[:10]

    leaderboard = []
    for player in players_data:
        leaderboard.append({
            'player_name': player['player_name'],
            'wins': player['wins'],
            'draws': player['draws'],
            'losses': player['losses'],
        })

    return leaderboard

#aggiorna il numero di w/l/d nella tabella Users 
def update_loc_stats(player_name, win, draw):
    u = Users.objects.get(username=player_name)
    if win:
        u.n_wins += 1
    elif not win and not draw:
        u.n_lost += 1
    else:  # draw=True
        u.n_draws += 1
    u.save()

#da chiamare alla fine di una partita contro un altro giocatore
#se vogliamo tenere traccia di chi vince contro chi
def save_match_results(p1, p2, win, los, dr):
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
    u = Users.objects.get(username = player_name)
    v = Users.objects.get(username = opponent)
    new_elo_points = calculate_elo(u.users.elo_points, v.users.elo_points, win, los, dr)
    #aggiorno punti del giocatore in tabella Users
    u.elo_points = new_elo_points

def social_log(mail):
    try:
        # Cerca un utente nel modello User associato a Users
        user = Users.objects.get(email=mail)
        # Trova l'istanza di Users associata a questo utente
        users_instance = Users.objects.get(user=user)
        return True
    except Users.DoesNotExist or Users.DoesNotExist:
        # L'utente o l'istanza di Users non esiste
        return False