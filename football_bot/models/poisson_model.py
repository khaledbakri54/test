"""
Dixon-Coles Poisson model for football match prediction.

Predicts the probability distribution of scorelines by modelling
home and away goals as independent (but correlated for low scores)
Poisson processes.

Key factors:
- Attack strength of each team
- Defence strength of each team
- Home advantage
- Low-score correction (Dixon-Coles rho parameter)
"""

import math
from scipy.stats import poisson
from scipy.optimize import minimize
import numpy as np
from typing import Tuple
from config import HOME_ADVANTAGE_GOALS, DC_RHO


def _dc_correction(home_goals: int, away_goals: int, mu_h: float,
                   mu_a: float, rho: float) -> float:
    """
    Dixon-Coles low-score correction factor tau.
    Corrects for the under/over-representation of 0-0, 1-0, 0-1, 1-1.
    """
    if home_goals == 0 and away_goals == 0:
        return 1 - mu_h * mu_a * rho
    elif home_goals == 1 and away_goals == 0:
        return 1 + mu_a * rho
    elif home_goals == 0 and away_goals == 1:
        return 1 + mu_h * rho
    elif home_goals == 1 and away_goals == 1:
        return 1 - rho
    return 1.0


def score_probability(home_goals: int, away_goals: int, mu_h: float,
                      mu_a: float, rho: float = DC_RHO) -> float:
    """
    Probability of a specific scoreline using Dixon-Coles model.
    P(X=i, Y=j) = tau(i,j) * Poisson(i; mu_h) * Poisson(j; mu_a)
    """
    tau = _dc_correction(home_goals, away_goals, mu_h, mu_a, rho)
    p_home = poisson.pmf(home_goals, mu_h)
    p_away = poisson.pmf(away_goals, mu_a)
    return max(0.0, tau * p_home * p_away)


def compute_match_probs(mu_h: float, mu_a: float,
                        max_goals: int = 10, rho: float = DC_RHO) -> Tuple[float, float, float]:
    """
    Compute home win / draw / away win probabilities by summing
    over all scoreline combinations up to max_goals.

    Returns: (p_home_win, p_draw, p_away_win)
    """
    p_home_win = p_draw = p_away_win = 0.0

    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            p = score_probability(i, j, mu_h, mu_a, rho)
            if i > j:
                p_home_win += p
            elif i == j:
                p_draw += p
            else:
                p_away_win += p

    total = p_home_win + p_draw + p_away_win
    if total > 0:
        p_home_win /= total
        p_draw     /= total
        p_away_win /= total

    return p_home_win, p_draw, p_away_win


def top_scorelines(mu_h: float, mu_a: float,
                   top_n: int = 5, max_goals: int = 8,
                   rho: float = DC_RHO) -> list:
    """Return top N most likely scorelines with probabilities."""
    scores = []
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            p = score_probability(i, j, mu_h, mu_a, rho)
            scores.append((i, j, p))
    scores.sort(key=lambda x: x[2], reverse=True)
    return scores[:top_n]


class PoissonModel:
    """
    Poisson model that estimates attack/defence parameters from historical data.
    """

    def __init__(self):
        self.attack: dict  = {}   # team_id -> attack strength
        self.defence: dict = {}   # team_id -> defence weakness
        self.home_adv: float = HOME_ADVANTAGE_GOALS
        self.fitted = False

    def fit(self, matches: list):
        """
        Estimate attack/defence parameters using MLE from finished matches.
        Each match: {home_team_id, away_team_id, home_goals, away_goals}
        """
        # Collect unique teams
        teams = set()
        for m in matches:
            teams.add(m["home_team_id"])
            teams.add(m["away_team_id"])
        teams = sorted(teams)
        n = len(teams)
        idx = {t: i for i, t in enumerate(teams)}

        # Initial params: [log_attack_0..n-1, log_defence_0..n-1, home_adv]
        x0 = np.zeros(2 * n + 1)
        x0[-1] = math.log(1 + HOME_ADVANTAGE_GOALS)

        def neg_log_likelihood(params):
            log_att = params[:n]
            log_def = params[n:2*n]
            home_adv = params[-1]
            nll = 0.0
            for m in matches:
                hi = idx[m["home_team_id"]]
                ai = idx[m["away_team_id"]]
                mu_h = math.exp(log_att[hi] - log_def[ai] + home_adv)
                mu_a = math.exp(log_att[ai] - log_def[hi])
                mu_h = max(0.01, mu_h)
                mu_a = max(0.01, mu_a)
                gh = m["home_goals"]
                ga = m["away_goals"]
                tau = _dc_correction(gh, ga, mu_h, mu_a, DC_RHO)
                tau = max(1e-10, tau)
                nll -= (math.log(tau)
                        + poisson.logpmf(gh, mu_h)
                        + poisson.logpmf(ga, mu_a))
            return nll

        result = minimize(neg_log_likelihood, x0, method="L-BFGS-B",
                          options={"maxiter": 500})
        opt = result.x
        for i, t in enumerate(teams):
            self.attack[t]  = math.exp(opt[i])
            self.defence[t] = math.exp(opt[n + i])
        self.home_adv = math.exp(opt[-1]) - 1
        self.fitted = True
        return self

    def predict(self, home_team_id: int, away_team_id: int,
                league_avg_scored: float = 1.35) -> Tuple[float, float, float]:
        """
        Predict home win / draw / away win probabilities.
        Falls back to league averages if team not in model.
        """
        att_h = self.attack.get(home_team_id, 1.0)
        def_h = self.defence.get(home_team_id, 1.0)
        att_a = self.attack.get(away_team_id, 1.0)
        def_a = self.defence.get(away_team_id, 1.0)

        mu_h = att_h / def_a * league_avg_scored * (1 + self.home_adv)
        mu_a = att_a / def_h * league_avg_scored
        mu_h = max(0.1, mu_h)
        mu_a = max(0.1, mu_a)

        return compute_match_probs(mu_h, mu_a)

    def predict_from_averages(self, home_avg_scored: float, home_avg_conceded: float,
                               away_avg_scored: float, away_avg_conceded: float,
                               league_avg: float = 1.35) -> Tuple[float, float, float]:
        """
        Predict using per-game averages directly (no fitting required).
        Useful when full dataset is unavailable.
        """
        mu_h = (home_avg_scored + away_avg_conceded) / 2 * (1 + HOME_ADVANTAGE_GOALS / league_avg)
        mu_a = (away_avg_scored + home_avg_conceded) / 2
        mu_h = max(0.1, mu_h)
        mu_a = max(0.1, mu_a)
        return compute_match_probs(mu_h, mu_a)
