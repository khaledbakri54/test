"""
Recent Form Model.

Analyses the last N matches to compute form-based win probabilities.
Considers:
- Points per game (weighted by recency)
- Goals scored / conceded trend
- Streak momentum
- Home/away specific form
"""

from typing import Tuple
from config import FORM_GAMES


def _recency_weight(index: int, total: int) -> float:
    """More recent matches get higher weight. Exponential decay."""
    return 1.5 ** (total - 1 - index) if total > 1 else 1.0


def compute_form_score(results: list, max_games: int = FORM_GAMES) -> float:
    """
    Compute a form score (0-1) from a list of results ('W', 'D', 'L').
    Most recent first. Uses recency-weighted points.
    """
    recent = results[:max_games]
    if not recent:
        return 0.5  # Neutral if no data

    total_weight = 0.0
    weighted_points = 0.0
    for i, r in enumerate(recent):
        w = _recency_weight(len(recent) - 1 - i, len(recent))
        total_weight += w * 3  # Max points per game
        if r == "W":
            weighted_points += 3 * w
        elif r == "D":
            weighted_points += 1 * w

    return weighted_points / total_weight if total_weight > 0 else 0.5


def form_to_probs(form_home: float, form_away: float) -> Tuple[float, float, float]:
    """
    Convert form scores into home win / draw / away win probabilities.
    """
    # Raw ratio
    total = form_home + form_away
    if total == 0:
        p_home = p_away = 0.38
        p_draw = 0.24
    else:
        ratio_h = form_home / total
        ratio_a = form_away / total

        # Map to win probabilities with realistic draw probability
        p_draw = max(0.15, 0.30 - abs(ratio_h - ratio_a) * 0.4)
        remaining = 1.0 - p_draw
        p_home = ratio_h * remaining
        p_away = ratio_a * remaining

    # Normalise
    total = p_home + p_draw + p_away
    return p_home / total, p_draw / total, p_away / total


def compute_goal_trend(goals_list: list, max_games: int = FORM_GAMES) -> float:
    """
    Compute weighted average goals from recent games (recency weighted).
    goals_list: list of goal counts, most recent first.
    """
    recent = goals_list[:max_games]
    if not recent:
        return 0.0
    total_w = 0.0
    weighted_goals = 0.0
    for i, g in enumerate(recent):
        w = _recency_weight(len(recent) - 1 - i, len(recent))
        weighted_goals += g * w
        total_w += w
    return weighted_goals / total_w if total_w > 0 else 0.0


def compute_streak(results: list) -> dict:
    """
    Compute current streak info from results (most recent first).
    Returns: {type: 'W'/'D'/'L', length: N}
    """
    if not results:
        return {"type": None, "length": 0}
    streak_type = results[0]
    length = 0
    for r in results:
        if r == streak_type:
            length += 1
        else:
            break
    return {"type": streak_type, "length": length}
