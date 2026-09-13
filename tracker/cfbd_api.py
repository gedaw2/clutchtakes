import os

import requests

BASE_URL = "https://api.collegefootballdata.com"


def _headers():
    return {"Authorization": f"Bearer {os.environ['CFBD_API_KEY']}"}


def search_games(year, team, season_type="regular"):
    response = requests.get(
        f"{BASE_URL}/games",
        params={"year": year, "team": team, "seasonType": season_type},
        headers=_headers(),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def get_game_player_stats(year, week, team, season_type="regular"):
    response = requests.get(
        f"{BASE_URL}/games/players",
        params={"year": year, "week": week, "team": team, "seasonType": season_type},
        headers=_headers(),
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def summarize_athlete_stats(games_players_response):
    """Groups every athlete's stats across categories: {(id, name, team): {category: {stat_type: value}}}"""
    summary = {}
    for game in games_players_response:
        for team_block in game.get("teams", []):
            team_name = team_block.get("team")
            for category in team_block.get("categories", []):
                category_name = category.get("name")
                for stat_type in category.get("types", []):
                    type_name = stat_type.get("name")
                    for athlete in stat_type.get("athletes", []):
                        key = (athlete["id"], athlete["name"], team_name)
                        summary.setdefault(key, {}).setdefault(category_name, {})[type_name] = athlete["stat"]
    return summary


def format_stat_line(category_stats):
    parts = []
    for category_name, stats in category_stats.items():
        stat_str = ", ".join(f"{value} {stat_type}" for stat_type, value in stats.items())
        parts.append(f"{category_name.title()}: {stat_str}")
    return " | ".join(parts)
