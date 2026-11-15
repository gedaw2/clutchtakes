import random

import requests
from django.shortcuts import get_object_or_404, redirect, render

from . import cfbd_api
from .forms import GameForm, PerformanceForm
from .models import Athlete, Comparison, Game, Performance, Sport


def ranked_list(request):
    sport_groups = [
        {
            "value": value,
            "label": label,
            "performances": Performance.objects.select_related("athlete", "game").filter(game__sport=value),
        }
        for value, label in Sport.choices
    ]
    return render(request, "tracker/ranked_list.html", {"sport_groups": sport_groups})


def game_list(request):
    games = Game.objects.prefetch_related("performances__athlete").all()
    return render(request, "tracker/game_list.html", {"games": games})


def add_game(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            game = form.save()
            return redirect("game_detail", game_id=game.id)
    else:
        form = GameForm()
    return render(request, "tracker/add_game.html", {"form": form})


def game_detail(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    if request.method == "POST":
        form = PerformanceForm(request.POST)
        if form.is_valid():
            athlete, _ = Athlete.objects.get_or_create(
                name=form.cleaned_data["athlete_name"],
                sport=game.sport,
                team=form.cleaned_data["athlete_team"],
            )
            Performance.objects.get_or_create(
                game=game,
                athlete=athlete,
                defaults={
                    "stat_line": form.cleaned_data["stat_line"],
                    "notes": form.cleaned_data["notes"],
                },
            )
            return redirect("game_detail", game_id=game.id)
    else:
        form = PerformanceForm()
    return render(request, "tracker/game_detail.html", {"game": game, "form": form})


def import_cfb_search(request):
    games = None
    error = None
    if request.method == "POST":
        year = request.POST.get("year")
        team = request.POST.get("team")
        try:
            games = cfbd_api.search_games(year, team)
        except requests.RequestException as exc:
            error = f"CFBD lookup failed: {exc}"
    return render(request, "tracker/import_cfb_search.html", {"games": games, "error": error})


def import_cfb_select(request):
    if request.method != "POST":
        return redirect("import_cfb_search")

    p = request.POST
    game, _ = Game.objects.get_or_create(
        external_id=p["cfbd_id"],
        defaults={
            "sport": Sport.CFB,
            "date": p["start_date"][:10],
            "home_team": p["home_team"],
            "away_team": p["away_team"],
            "home_score": p.get("home_points") or None,
            "away_score": p.get("away_points") or None,
        },
    )

    athletes = []
    error = None
    try:
        raw_stats = cfbd_api.get_game_player_stats(p["year"], p["week"], p["home_team"])
        summary = cfbd_api.summarize_athlete_stats(raw_stats)
        athletes = [
            {"name": name, "team": team, "stat_line": cfbd_api.format_stat_line(categories)}
            for (_id, name, team), categories in summary.items()
        ]
        athletes.sort(key=lambda a: a["team"])
    except requests.RequestException as exc:
        error = f"Could not fetch player stats: {exc}"

    return render(request, "tracker/import_cfb_select.html", {"game": game, "athletes": athletes, "error": error})


def _random_pair(sport):
    ids = list(Performance.objects.filter(game__sport=sport).values_list("id", flat=True))
    if len(ids) < 2:
        return None
    a_id, b_id = random.sample(ids, 2)
    return (
        Performance.objects.select_related("athlete", "game").get(id=a_id),
        Performance.objects.select_related("athlete", "game").get(id=b_id),
    )


def compare_choose(request):
    return render(request, "tracker/compare_choose.html", {"sports": Sport.choices})


def compare(request, sport):
    if sport not in Sport.values:
        return redirect("compare_choose")
    pair = _random_pair(sport)
    context = {"pair": pair, "sport": sport, "sport_label": Sport(sport).label}
    if pair is not None:
        context["left"], context["right"] = pair
    return render(request, "tracker/compare.html", context)


def compare_pick(request):
    winner = get_object_or_404(Performance, id=request.POST.get("winner_id"))
    loser = get_object_or_404(Performance, id=request.POST.get("loser_id"))
    sport = request.POST.get("sport")
    Comparison.objects.create(winner=winner, loser=loser)

    pair = _random_pair(sport)
    context = {"pair": pair, "sport": sport, "sport_label": Sport(sport).label}
    if pair is not None:
        context["left"], context["right"] = pair
    return render(request, "tracker/_compare_pair.html", context)
