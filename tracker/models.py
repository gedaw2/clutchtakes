from django.db import models

from tracker.elo import update_ratings


class Sport(models.TextChoices):
    NBA = "NBA", "NBA"
    CFB = "CFB", "College Football"


class Game(models.Model):
    sport = models.CharField(max_length=3, choices=Sport.choices)
    date = models.DateField()
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    home_score = models.PositiveSmallIntegerField(null=True, blank=True)
    away_score = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.away_team} @ {self.home_team} ({self.date})"


class Athlete(models.Model):
    name = models.CharField(max_length=100)
    sport = models.CharField(max_length=3, choices=Sport.choices)
    team = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "sport", "team")

    def __str__(self):
        return self.name


class Performance(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="performances")
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name="performances")
    stat_line = models.CharField(
        max_length=255, blank=True,
        help_text="e.g. 34 pts / 8 reb / 11 ast",
    )
    notes = models.TextField(blank=True)
    elo_rating = models.FloatField(default=1500.0)
    comparisons_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-elo_rating"]
        unique_together = ("game", "athlete")

    def __str__(self):
        return f"{self.athlete} — {self.game}"


class Comparison(models.Model):
    winner = models.ForeignKey(Performance, on_delete=models.CASCADE, related_name="wins")
    loser = models.ForeignKey(Performance, on_delete=models.CASCADE, related_name="losses")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.winner.athlete} over {self.loser.athlete}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            new_winner_rating, new_loser_rating = update_ratings(
                self.winner.elo_rating, self.loser.elo_rating
            )
            self.winner.elo_rating = new_winner_rating
            self.winner.comparisons_count += 1
            self.winner.save(update_fields=["elo_rating", "comparisons_count"])

            self.loser.elo_rating = new_loser_rating
            self.loser.comparisons_count += 1
            self.loser.save(update_fields=["elo_rating", "comparisons_count"])
