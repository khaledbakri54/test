"""
Elo Rating System for football teams.

Adapted from chess Elo with football-specific tweaks:
- Goal difference multiplier (larger wins update ratings more)
- Home advantage boost
- Separate tracking for national teams vs club teams
"""

import math
from typing import Tuple
from config import ELO_K_FACTOR, ELO_DEFAULT, ELO_HOME_ADVANTAGE


def _goal_diff_multiplier(goal_diff: int) -> float:
    """
    Multiplier based on goal difference (FIFA/World Football Elo style).
    Larger victories count more, but with diminishing returns.
    """
    gd = abs(goal_diff)
    if gd <= 1:
        return 1.0
    elif gd == 2:
        return 1.5
    else:
        return (11 + gd) / 8.0


def expected_score(elo_a: float, elo_b: float, home: bool = False) -> float:
    """
    Expected score for team A against team B.
    Returns probability that A wins (0 to 1).
    """
    adj_elo_a = elo_a + (ELO_HOME_ADVANTAGE if home else 0)
    return 1.0 / (1.0 + 10 ** ((elo_b - adj_elo_a) / 400.0))


def update_elo(elo_a: float, elo_b: float, result_a: float,
               goal_diff: int, k: float = ELO_K_FACTOR,
               home: bool = False) -> Tuple[float, float]:
    """
    Update Elo ratings after a match.

    Args:
        elo_a, elo_b: Current ratings
        result_a: Actual score for A (1=win, 0.5=draw, 0=loss)
        goal_diff: abs(home_goals - away_goals)
        k: K-factor
        home: True if team A is at home

    Returns: (new_elo_a, new_elo_b)
    """
    exp_a = expected_score(elo_a, elo_b, home=home)
    exp_b = 1.0 - exp_a
    result_b = 1.0 - result_a
    gd_mult = _goal_diff_multiplier(goal_diff)

    new_elo_a = elo_a + k * gd_mult * (result_a - exp_a)
    new_elo_b = elo_b + k * gd_mult * (result_b - exp_b)
    return new_elo_a, new_elo_b


def elo_to_win_prob(elo_home: float, elo_away: float) -> Tuple[float, float, float]:
    """
    Convert Elo ratings to home win / draw / away win probabilities.
    Uses a logistic model calibrated on football data.

    Returns: (p_home, p_draw, p_away)
    """
    p_home_win_raw = expected_score(elo_home, elo_away, home=True)
    # Empirical draw probability model based on Elo difference
    elo_diff = abs(elo_home + ELO_HOME_ADVANTAGE - elo_away)
    # Draw probability peaks when teams are evenly matched
    p_draw = max(0.18, 0.30 - 0.001 * elo_diff)
    p_draw = min(p_draw, 0.32)

    # Redistribute the remaining probability
    remaining = 1.0 - p_draw
    p_home = p_home_win_raw * remaining
    p_away = (1.0 - p_home_win_raw) * remaining
    return p_home, p_draw, p_away


class EloRatingSystem:
    """Maintains and updates Elo ratings for all tracked teams."""

    def __init__(self, k_factor: float = ELO_K_FACTOR):
        self.ratings: dict = {}   # team_id -> elo
        self.k = k_factor
        self.history: dict = {}   # team_id -> list of (date, elo)

    def get_rating(self, team_id: int) -> float:
        return self.ratings.get(team_id, float(ELO_DEFAULT))

    def set_rating(self, team_id: int, elo: float):
        self.ratings[team_id] = elo

    def process_match(self, home_team_id: int, away_team_id: int,
                      home_goals: int, away_goals: int, date: str = ""):
        """Process a finished match and update Elo ratings."""
        elo_h = self.get_rating(home_team_id)
        elo_a = self.get_rating(away_team_id)

        if home_goals > away_goals:
            result_h = 1.0
        elif home_goals == away_goals:
            result_h = 0.5
        else:
            result_h = 0.0

        gd = abs(home_goals - away_goals)
        new_elo_h, new_elo_a = update_elo(elo_h, elo_a, result_h, gd,
                                           k=self.k, home=True)
        self.ratings[home_team_id] = new_elo_h
        self.ratings[away_team_id] = new_elo_a

        # Track history
        for tid, elo in [(home_team_id, new_elo_h), (away_team_id, new_elo_a)]:
            if tid not in self.history:
                self.history[tid] = []
            self.history[tid].append((date, elo))

    def fit(self, matches: list):
        """
        Initialise ratings by replaying all historical matches in order.
        matches: list of dicts with keys: home_team_id, away_team_id,
                 home_goals, away_goals, date (ISO string)
        """
        sorted_matches = sorted(matches, key=lambda m: m.get("date", ""))
        for m in sorted_matches:
            self.process_match(
                m["home_team_id"], m["away_team_id"],
                m["home_goals"], m["away_goals"],
                m.get("date", "")
            )
        return self

    def predict(self, home_team_id: int, away_team_id: int) -> Tuple[float, float, float]:
        """Predict match outcome probabilities from current Elo ratings."""
        elo_h = self.get_rating(home_team_id)
        elo_a = self.get_rating(away_team_id)
        return elo_to_win_prob(elo_h, elo_a)

    def top_teams(self, n: int = 20) -> list:
        """Return top N teams by Elo rating."""
        return sorted(self.ratings.items(), key=lambda x: x[1], reverse=True)[:n]
