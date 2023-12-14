from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Users, Matches

class UserInline(admin.StackedInline):
    model = Users
    can_delete = False
    verbose_name_plural = 'users'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = [UserInline] 

# Re-register UserAdmin
admin.site.unregister(User) 
admin.site.register(User, UserAdmin) 

@admin.register(Matches)
class MatchesAdmin(admin.ModelAdmin):
    list_display = ('room_name', 'player1', 'player2', 'winner', 'loser', 'draw')
    search_fields = ('player1', 'player2', 'winner', 'loser')  # Aggiunge una barra di ricerca per i giocatori e i vincitori/perdenti
    list_filter = ('draw',)  # Aggiunge un filtro laterale per le partite pareggiate