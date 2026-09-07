import random

from django.shortcuts import get_object_or_404, render

from .models import Comparison, Game, Performance


def ranked_list(request):
    performances = Performance.objects.select_related("athlete", "game").all()
    return render(request, "tracker/ranked_list.html", {"performances": performances})


def game_list(request):
    games = Game.objects.prefetch_related("performances__athlete").all()
    return render(request, "tracker/game_list.html", {"games": games})


def _random_pair():
    ids = list(Performance.objects.values_list("id", flat=True))
    if len(ids) < 2:
        return None
    a_id, b_id = random.sample(ids, 2)
    return (
        Performance.objects.select_related("athlete", "game").get(id=a_id),
        Performance.objects.select_related("athlete", "game").get(id=b_id),
    )


def compare(request):
    pair = _random_pair()
    context = {"pair": pair}
    if pair is None:
        return render(request, "tracker/compare.html", context)
    left, right = pair
    context["left"] = left
    context["right"] = right
    return render(request, "tracker/compare.html", context)


def compare_pick(request):
    winner = get_object_or_404(Performance, id=request.POST.get("winner_id"))
    loser = get_object_or_404(Performance, id=request.POST.get("loser_id"))
    Comparison.objects.create(winner=winner, loser=loser)

    pair = _random_pair()
    context = {"pair": pair}
    if pair is not None:
        context["left"], context["right"] = pair
    return render(request, "tracker/_compare_pair.html", context)
