from .models import Users, Matches
from django.db.models import F
import asyncio
from asgiref.sync import sync_to_async

@sync_to_async
def get_player_loc_stats(player_name):
    player =(Users.objects.get)(user__username=player_name)
        
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

@sync_to_async
def get_leaderboard():
    # Ottenere i dati per i primi 10 giocatori
    try:
        players_data = Users.objects.annotate(
            player_name=F('user__username'),
            wins=F('n_wins'),
            draws=F('n_draws'),
            losses=F('n_lost'),
            elo=F('elo_points')
        ).order_by('-elo_points').values('player_name', 'n_wins', 'n_draws', 'n_lost', 'elo_points')[:10]


        leaderboard = []
        for player in players_data:
            player_name = player['player_name']
            wins = player['n_wins']
            draws = player['n_draws']
            losses = player['n_lost']
            elo = player['elo_points']

            leaderboard.append({
                'player_name': player_name,
                'n_wins': wins,
                'n_draws': draws,
                'n_lost': losses,
                'elo': elo
            })

        return leaderboard
    except Exception as e:
        print(f"An error occurred: {e}")
        raise  # Rilancia l'eccezione per ottenere la traccia completa

#aggiorna il numero di w/l/d nella tabella Users 
@sync_to_async
def update_loc_stats(player_name, win, draw):
    u = (Users.objects.get)(user__username=player_name)
    if win:
        u.n_wins += 1
    elif not win and not draw:
        u.n_lost += 1
    else:  # draw=True
        u.n_draws += 1
    u.save()

#da chiamare alla fine di una partita contro un altro giocatore
#se vogliamo tenere traccia di chi vince contro chi
@sync_to_async
def save_match_results(roomName, winner, loser, dr):
     # Ora inseriamo i dati nella tabella Matches
    match = (Matches.objects.get)(room_name=roomName, finished=False)
    match.finished = True
    match.draw = dr
    if dr:
        match.winner = None
        match.loser = None
    else:
        match.winner = winner
        match.loser = loser
    # Salva l'oggetto Matches nel database
    match.save()

#da chiamare dopo aver sfidato un umano
#calcola i punti elo alla fine di ogni partita per il player1; Utilizziamo l'ELO FSI
#Vittoria = 1 punto
#Patta = 0,5 punti
#Sconfitta  = 0 punti.
@sync_to_async
def update_elo(player_name, opponent, win, los, dr):
    u = (Users.objects.get)(user__username = player_name)
    v = (Users.objects.get)(user__username = opponent)
    #calcolo nuovi punti elo
    #new_elo_points = sync_to_async(calculate_elo)(u.elo_points, v.elo_points, win, los, dr)
    K=30 #secondo rergole FSI
    #calcolo punteggio attuale
    if win: actual_score = 1
    elif los: actual_score = 0
    else: actual_score = 0.5 #draw
    #calcolo punteggio atteso
    rb = v.elo_points
    ra = u.elo_points
    expected_score = 1 / (1+10**((rb-ra)/400))
    new_elo=ra+(K*(actual_score-expected_score))
    #aggiorno punti dei giocatori in tabella Users
    u.elo_points = new_elo
    u.save()

def social_log(mail):
    try:
        # Cerca un utente nel modello User associato a Users
        user = Users.objects.get(user__email=mail)
        # Trova l'istanza di Users associata a questo utente
        users_instance = Users.objects.get(user__username=user)
        return True
    except Users.DoesNotExist or Users.DoesNotExist:
        # L'utente o l'istanza di Users non esiste
        return False