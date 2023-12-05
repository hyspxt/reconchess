from django.contrib import admin
from .models import Users, Matches

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_on', 'last_login', 'elo_points', 'n_wins_loc', 'n_draws_loc', 'n_lost_loc')
    search_fields = ('user__username',)  # Aggiunge una barra di ricerca per l'username dell'utente

@admin.register(Matches)
class MatchesAdmin(admin.ModelAdmin):
    list_display = ('player1', 'player2', 'winner', 'loser', 'draw')
    search_fields = ('player1', 'player2', 'winner', 'loser')  # Aggiunge una barra di ricerca per i giocatori e i vincitori/perdenti
    list_filter = ('draw',)  # Aggiunge un filtro laterale per le partite pareggiate
    