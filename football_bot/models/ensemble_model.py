"""
Ensemble Prediction Model.

Combines multiple sub-models using configurable weights to produce
final home win / draw / away win probabilities.

Sub-models used:
1. Dixon-Coles Poisson model (attack/defence strengths)
2. Elo rating system
3. Recent form analysis
4. Head-to-head history
5. Home/away advantage statistics

Additional factors considered:
- League position gap
- Goal difference season total
- Clean sheet rate
- Scoring rate consistency
"""

import math
from typing import Tuple, Optional
from models.poisson_model import PoissonModel
from models.elo_model import EloRatingSystem, elo_to_win_prob
from models.form_model import compute_form_score, form_to_probs, compute_streak
from data.processor import build_team_stats, build_h2h_stats
from config import MODEL_WEIGHTS


def _weighted_combine(predictions: list, weights: list) -> Tuple[float, float, float]:
    """
    Combine (p_home, p_draw, p_away) tuples using weights.
    Returns normalised combined probability.
    """
    total_w = sum(weights)
    p_h = sum(p[0] * w for p, w in zip(predictions, weights)) / total_w
    p_d = sum(p[1] * w for p, w in zip(predictions, weights)) / total_w
    p_a = sum(p[2] * w for p, w in zip(predictions, weights)) / total_w
    total = p_h + p_d + p_a
    return p_h / total, p_d / total, p_a / total


def _h2h_probs(h2h_stats: dict) -> Tuple[float, float, float]:
    """Convert H2H stats to probabilities."""
    total = h2h_stats.get("total_games", 0)
    if total == 0:
        return 0.45, 0.27, 0.28  # Slight home bias default
    hw = h2h_stats.get("home_win_rate", 0.4)
    aw = h2h_stats.get("away_win_rate", 0.3)
    dr = h2h_stats.get("draw_rate", 0.3)
    t = hw + dr + aw
    if t == 0:
        return 0.45, 0.27, 0.28
    return hw / t, dr / t, aw / t


def _home_away_probs(home_stats: dict, away_stats: dict) -> Tuple[float, float, float]:
    """
    Compute probs from raw win/draw/loss rates with home/away adjustment.
    """
    home_wr = home_stats.get("win_rate", 0.45)
    away_wr = away_stats.get("win_rate", 0.35)
    # Draw probability inversely related to win rates
    p_draw = max(0.15, 1.0 - home_wr - away_wr) * 0.5
    p_home = home_wr * 0.6 + 0.05   # Home advantage boost
    p_away = away_wr * 0.5
    t = p_home + p_draw + p_away
    if t == 0:
        return 0.45, 0.27, 0.28
    return p_home / t, p_draw / t, p_away / t


def _standings_adjustment(home_pos: Optional[int], away_pos: Optional[int],
                           total_teams: int = 20) -> float:
    """
    Return an adjustment factor for home team based on league position gap.
    Positive = home team advantage, negative = disadvantage.
    Range: roughly -0.1 to +0.1
    """
    if home_pos is None or away_pos is None:
        return 0.0
    pos_diff = away_pos - home_pos  # Positive if home team ranked higher
    return (pos_diff / total_teams) * 0.15


def _clean_sheet_rate(goals_against: int, played: int) -> float:
    """Estimate clean sheet rate from goals conceded."""
    if played == 0:
        return 0.0
    avg_conceded = goals_against / played
    # Approximate: Poisson(0) for avg goals conceded
    return math.exp(-avg_conceded)


class EnsemblePredictor:
    """
    Full ensemble prediction engine that combines all models and factors.
    """

    def __init__(self):
        self.poisson_model = PoissonModel()
        self.elo_system    = EloRatingSystem()
        self.weights       = MODEL_WEIGHTS
        self._poisson_fitted = False
        self._elo_fitted     = False

    def fit(self, matches: list):
        """
        Fit all sub-models on historical match data.
        matches: list of dicts with keys:
            home_team_id, away_team_id, home_goals, away_goals, date
        """
        self.poisson_model.fit(matches)
        self.elo_system.fit(matches)
        self._poisson_fitted = True
        self._elo_fitted = True
        return self

    def predict(
        self,
        home_team_id: int,
        away_team_id: int,
        home_matches: list = None,
        away_matches: list = None,
        h2h_matches:  list = None,
        home_standings: dict = None,
        away_standings: dict = None,
        league_avg: float = 1.35,
        is_neutral: bool = False,
    ) -> dict:
        """
        Full ensemble prediction.

        Args:
            home_team_id / away_team_id: Team IDs
            home_matches / away_matches: Recent finished matches for each team
            h2h_matches: Historical head-to-head matches
            home_standings / away_standings: Standings data dicts
            league_avg: Average goals per team per game in this league
            is_neutral: True for neutral venue (international tournaments)

        Returns: dict with probabilities, confidence, scorelines, analysis
        """
        predictions = []
        weights     = []
        analysis    = {}

        # ---- 1. Poisson Model ----
        if self._poisson_fitted:
            p_poisson = self.poisson_model.predict(
                home_team_id, away_team_id, league_avg_scored=league_avg
            )
        elif home_matches and away_matches:
            home_stats = build_team_stats(home_matches, home_team_id)
            away_stats = build_team_stats(away_matches, away_team_id)
            p_poisson = self.poisson_model.predict_from_averages(
                home_stats["avg_scored"], home_stats["avg_conceded"],
                away_stats["avg_scored"], away_stats["avg_conceded"],
                league_avg=league_avg,
            )
        else:
            p_poisson = (0.45, 0.27, 0.28)
        predictions.append(p_poisson)
        weights.append(self.weights["poisson"])
        analysis["poisson"] = {"home": round(p_poisson[0], 4),
                                "draw": round(p_poisson[1], 4),
                                "away": round(p_poisson[2], 4)}

        # ---- 2. Elo Model ----
        if self._elo_fitted:
            p_elo = self.elo_system.predict(home_team_id, away_team_id)
        else:
            p_elo = (0.45, 0.27, 0.28)
        if is_neutral:
            # Remove home advantage from Elo
            from models.elo_model import elo_to_win_prob, ELO_HOME_ADVANTAGE
            elo_h = self.elo_system.get_rating(home_team_id)
            elo_a = self.elo_system.get_rating(away_team_id)
            # Recalculate without home advantage
            from models.elo_model import expected_score
            raw = expected_score(elo_h, elo_a, home=False)
            elo_diff = abs(elo_h - elo_a)
            p_draw_elo = max(0.18, 0.30 - 0.001 * elo_diff)
            p_draw_elo = min(p_draw_elo, 0.32)
            rem = 1 - p_draw_elo
            p_elo = (raw * rem, p_draw_elo, (1 - raw) * rem)
        predictions.append(p_elo)
        weights.append(self.weights["elo"])
        analysis["elo"] = {"home": round(p_elo[0], 4),
                           "draw": round(p_elo[1], 4),
                           "away": round(p_elo[2], 4),
                           "elo_home": round(self.elo_system.get_rating(home_team_id), 1),
                           "elo_away": round(self.elo_system.get_rating(away_team_id), 1)}

        # ---- 3. Form Model ----
        if home_matches and away_matches:
            home_stats = build_team_stats(home_matches, home_team_id)
            away_stats = build_team_stats(away_matches, away_team_id)
            form_h = compute_form_score(home_stats["form"])
            form_a = compute_form_score(away_stats["form"])
            p_form = form_to_probs(form_h, form_a)
            home_streak = compute_streak(home_stats["form"])
            away_streak = compute_streak(away_stats["form"])
            analysis["form"] = {
                "home_form": home_stats["form"],
                "away_form": away_stats["form"],
                "home_streak": home_streak,
                "away_streak": away_streak,
                "home_score": round(form_h, 3),
                "away_score": round(form_a, 3),
                "home": round(p_form[0], 4),
                "draw": round(p_form[1], 4),
                "away": round(p_form[2], 4),
            }
        else:
            home_stats = None
            away_stats = None
            p_form = (0.45, 0.27, 0.28)
            analysis["form"] = {"note": "No recent match data available"}
        predictions.append(p_form)
        weights.append(self.weights["form"])

        # ---- 4. Head-to-Head Model ----
        if h2h_matches:
            h2h_stats = build_h2h_stats(h2h_matches, home_team_id, away_team_id)
            p_h2h = _h2h_probs(h2h_stats)
            analysis["h2h"] = {
                "total_games": h2h_stats["total_games"],
                "home_wins":   h2h_stats["home_wins"],
                "draws":       h2h_stats["draws"],
                "away_wins":   h2h_stats["away_wins"],
                "home": round(p_h2h[0], 4),
                "draw": round(p_h2h[1], 4),
                "away": round(p_h2h[2], 4),
            }
        else:
            p_h2h = (0.45, 0.27, 0.28)
            analysis["h2h"] = {"note": "No H2H data available"}
        predictions.append(p_h2h)
        weights.append(self.weights["h2h"])

        # ---- 5. Home/Away Advantage ----
        if home_stats and away_stats:
            p_ha = _home_away_probs(home_stats, away_stats)
            analysis["home_away"] = {
                "home_win_rate": round(home_stats["win_rate"], 3),
                "away_win_rate": round(away_stats["win_rate"], 3),
                "home_avg_scored": round(home_stats["avg_scored"], 2),
                "away_avg_scored": round(away_stats["avg_scored"], 2),
                "home_avg_conceded": round(home_stats["avg_conceded"], 2),
                "away_avg_conceded": round(away_stats["avg_conceded"], 2),
                "home": round(p_ha[0], 4),
                "draw": round(p_ha[1], 4),
                "away": round(p_ha[2], 4),
            }
        else:
            p_ha = (0.45, 0.27, 0.28)
            analysis["home_away"] = {"note": "No team stats available"}
        predictions.append(p_ha)
        weights.append(self.weights["home_away"])

        # ---- Combine all models ----
        p_home, p_draw, p_away = _weighted_combine(predictions, weights)

        # ---- Standings adjustment (soft nudge) ----
        if home_standings and away_standings:
            home_pos = home_standings.get("position")
            away_pos = away_standings.get("position")
            adj = _standings_adjustment(home_pos, away_pos)
            p_home = max(0.01, p_home + adj)
            p_away = max(0.01, p_away - adj * 0.5)
            total = p_home + p_draw + p_away
            p_home /= total
            p_draw /= total
            p_away /= total
            analysis["standings"] = {
                "home_position": home_pos,
                "away_position": away_pos,
                "adjustment": round(adj, 4),
            }

        # ---- Expected goals ----
        if home_stats and away_stats:
            league_avg_used = league_avg
            mu_h = (home_stats["avg_scored"] + away_stats["avg_conceded"]) / 2
            mu_a = (away_stats["avg_scored"] + home_stats["avg_conceded"]) / 2
            mu_h *= (1.0 if is_neutral else 1.15)  # Home advantage on goals
        else:
            mu_h = league_avg * (1.0 if is_neutral else 1.1)
            mu_a = league_avg * 0.9

        # ---- Top scorelines ----
        from models.poisson_model import top_scorelines
        likely_scores = top_scorelines(mu_h, mu_a, top_n=5)

        # ---- Confidence score ----
        # Higher confidence when models agree
        all_home  = [p[0] for p in predictions]
        all_draws = [p[1] for p in predictions]
        all_away  = [p[2] for p in predictions]
        import statistics
        if len(all_home) > 1:
            std_h = statistics.stdev(all_home)
            std_d = statistics.stdev(all_draws)
            std_a = statistics.stdev(all_away)
            avg_std = (std_h + std_d + std_a) / 3
            confidence = max(0.3, min(1.0, 1.0 - avg_std * 5))
        else:
            confidence = 0.5

        # ---- Determine likely outcome ----
        max_prob = max(p_home, p_draw, p_away)
        if max_prob == p_home:
            likely_outcome = "HOME_WIN"
        elif max_prob == p_draw:
            likely_outcome = "DRAW"
        else:
            likely_outcome = "AWAY_WIN"

        return {
            "home_win":      round(p_home, 4),
            "draw":          round(p_draw, 4),
            "away_win":      round(p_away, 4),
            "likely_outcome": likely_outcome,
            "confidence":    round(confidence, 3),
            "expected_goals": {
                "home": round(mu_h, 2),
                "away": round(mu_a, 2),
            },
            "top_scorelines": [
                {"score": f"{s[0]}-{s[1]}", "probability": round(s[2] * 100, 2)}
                for s in likely_scores
            ],
            "analysis": analysis,
        }
