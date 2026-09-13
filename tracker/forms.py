from django import forms

from .models import Game


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ["sport", "date", "home_team", "away_team", "home_score", "away_score", "notes"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}


class PerformanceForm(forms.Form):
    athlete_name = forms.CharField(max_length=100, label="Athlete")
    athlete_team = forms.CharField(max_length=100, required=False, label="Team")
    stat_line = forms.CharField(max_length=255, required=False, label="Stat line")
    notes = forms.CharField(widget=forms.Textarea, required=False)
