from django.contrib import admin

from .models import Athlete, Comparison, Game, Performance


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("__str__", "sport", "date")
    list_filter = ("sport",)


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ("name", "sport", "team")
    list_filter = ("sport",)
    search_fields = ("name",)


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ("athlete", "game", "stat_line", "elo_rating", "comparisons_count")
    list_filter = ("game__sport",)
    search_fields = ("athlete__name",)


@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display = ("winner", "loser", "created_at")
