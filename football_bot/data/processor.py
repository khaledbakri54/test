"""
Data processor: transforms raw API data into structures
used by prediction models.
"""

from typing import Optional


def parse_match_result(match: dict, team_id: int) -> Optional[str]:
    """Return 'W', 'D', or 'L' from the perspective of team_id."""
    score = match.get("score", {})
    full = score.get("fullTime", {})
    home_goals = full.get("home")
    away_goals = full.get("away")
    if home_goals is None or away_goals is None:
        return None
    home_team = match.get("homeTeam", {}).get("id")
    if home_team == team_id:
        if home_goals > away_goals:
            return "W"
        elif home_goals < away_goals:
            return "L"
        return "D"
    else:
        if away_goals > home_goals:
            return "W"
        elif away_goals < home_goals:
            return "L"
        return "D"


def get_goals_scored_conceded(match: dict, team_id: int):
    """Return (goals_scored, goals_conceded) for team_id in a match."""
    score = match.get("score", {})
    full = score.get("fullTime", {})
    home_goals = full.get("home")
    away_goals = full.get("away")
    if home_goals is None or away_goals is None:
        return None, None
    home_team = match.get("homeTeam", {}).get("id")
    if home_team == team_id:
        return home_goals, away_goals
    return away_goals, home_goals


def build_team_stats(matches: list, team_id: int) -> dict:
    """
    Build aggregated stats for a team from a list of finished matches.
    Returns dict with: played, wins, draws, losses, goals_for, goals_against,
    form (list of last results), avg_scored, avg_conceded
    """
    finished = [
        m for m in matches
        if m.get("status") == "FINISHED"
        and (m.get("homeTeam", {}).get("id") == team_id
             or m.get("awayTeam", {}).get("id") == team_id)
    ]
    # Sort by date
    finished.sort(key=lambda m: m.get("utcDate", ""), reverse=True)

    played = len(finished)
    wins = draws = losses = goals_for = goals_against = 0
    form = []

    for m in finished:
        gf, ga = get_goals_scored_conceded(m, team_id)
        if gf is None:
            continue
        goals_for += gf
        goals_against += ga
        result = parse_match_result(m, team_id)
        if result == "W":
            wins += 1
        elif result == "D":
            draws += 1
        elif result == "L":
            losses += 1
        form.append(result)

    return {
        "team_id": team_id,
        "played": played,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_for": goals_for,
        "goals_against": goals_against,
        "form": form[:6],          # Last 6 results
        "avg_scored": goals_for / played if played else 0,
        "avg_conceded": goals_against / played if played else 0,
        "win_rate": wins / played if played else 0,
    }


def build_h2h_stats(h2h_matches: list, home_team_id: int, away_team_id: int) -> dict:
    """
    Build head-to-head stats between two teams.
    """
    finished = [m for m in h2h_matches if m.get("status") == "FINISHED"]
    home_wins = away_wins = draws = 0
    home_goals = away_goals = 0

    for m in finished:
        score = m.get("score", {}).get("fullTime", {})
        hg = score.get("home", 0) or 0
        ag = score.get("away", 0) or 0
        match_home_id = m.get("homeTeam", {}).get("id")

        if match_home_id == home_team_id:
            home_goals += hg
            away_goals += ag
            if hg > ag:
                home_wins += 1
            elif ag > hg:
                away_wins += 1
            else:
                draws += 1
        else:
            home_goals += ag
            away_goals += hg
            if ag > hg:
                home_wins += 1
            elif hg > ag:
                away_wins += 1
            else:
                draws += 1

    total = len(finished)
    return {
        "total_games": total,
        "home_wins": home_wins,
        "away_wins": away_wins,
        "draws": draws,
        "home_goals_avg": home_goals / total if total else 0,
        "away_goals_avg": away_goals / total if total else 0,
        "home_win_rate": home_wins / total if total else 0,
        "away_win_rate": away_wins / total if total else 0,
        "draw_rate": draws / total if total else 0,
    }


def extract_standings_stats(standings: list, team_id: int) -> Optional[dict]:
    """Extract team stats from standings table."""
    for entry in standings:
        team = entry.get("team", {})
        if team.get("id") == team_id:
            return {
                "position": entry.get("position"),
                "played": entry.get("playedGames", 0),
                "won": entry.get("won", 0),
                "draw": entry.get("draw", 0),
                "lost": entry.get("lost", 0),
                "goals_for": entry.get("goalsFor", 0),
                "goals_against": entry.get("goalsAgainst", 0),
                "goal_diff": entry.get("goalDifference", 0),
                "points": entry.get("points", 0),
            }
    return None
