"""
High-level Predictor class.
Orchestrates data fetching, processing, and ensemble prediction.
"""

from typing import Optional
from data.fetcher import FootballDataFetcher
from data.processor import build_team_stats, build_h2h_stats, extract_standings_stats
from models.ensemble_model import EnsemblePredictor
from config import H2H_GAMES, FORM_GAMES


class FootballPredictor:
    """
    High-level interface for predicting football match outcomes.
    Handles both live API data and manual/offline scenarios.
    """

    def __init__(self, api_key: str = None):
        self.fetcher   = FootballDataFetcher(api_key) if api_key else FootballDataFetcher()
        self.ensemble  = EnsemblePredictor()
        self._trained_competitions: set = set()

    def train_on_competition(self, competition_code: str, season: int = None):
        """
        Fetch all finished matches for a competition and train models.
        Call this before predicting matches in a specific competition.
        """
        print(f"[*] Fetching match history for {competition_code}...")
        matches = self.fetcher.get_matches_by_competition(
            competition_code, season=season, status="FINISHED"
        )
        if not matches:
            print(f"[!] No finished matches found for {competition_code}")
            return self

        # Convert API response to model format
        training_data = []
        for m in matches:
            score = m.get("score", {}).get("fullTime", {})
            hg = score.get("home")
            ag = score.get("away")
            if hg is None or ag is None:
                continue
            training_data.append({
                "home_team_id": m["homeTeam"]["id"],
                "away_team_id": m["awayTeam"]["id"],
                "home_goals":   int(hg),
                "away_goals":   int(ag),
                "date":         m.get("utcDate", ""),
            })

        print(f"[*] Training on {len(training_data)} matches...")
        self.ensemble.fit(training_data)
        self._trained_competitions.add(competition_code)
        print(f"[✓] Training complete.")
        return self

    def predict_by_ids(
        self,
        home_team_id: int,
        away_team_id: int,
        competition_code: str = None,
        match_id: int = None,
        is_neutral: bool = False,
        season: int = None,
    ) -> dict:
        """
        Predict match outcome for two teams given their IDs.
        """
        # Fetch recent matches for form analysis
        home_matches = self.fetcher.get_team_matches(
            home_team_id, limit=FORM_GAMES * 2, status="FINISHED"
        ) or []
        away_matches = self.fetcher.get_team_matches(
            away_team_id, limit=FORM_GAMES * 2, status="FINISHED"
        ) or []

        # H2H
        h2h_matches = []
        if match_id:
            h2h_matches = self.fetcher.get_head_to_head(match_id, limit=H2H_GAMES) or []

        # Standings
        home_standings = away_standings = None
        if competition_code:
            standings = self.fetcher.get_standings(competition_code, season=season)
            if standings:
                home_standings = extract_standings_stats(standings, home_team_id)
                away_standings = extract_standings_stats(standings, away_team_id)

        # League average goals
        league_avg = self._league_avg(competition_code, season) or 1.35

        return self.ensemble.predict(
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            home_matches=home_matches,
            away_matches=away_matches,
            h2h_matches=h2h_matches,
            home_standings=home_standings,
            away_standings=away_standings,
            league_avg=league_avg,
            is_neutral=is_neutral,
        )

    def predict_manual(
        self,
        home_avg_scored: float,
        home_avg_conceded: float,
        home_win_rate: float,
        home_form: list,
        away_avg_scored: float,
        away_avg_conceded: float,
        away_win_rate: float,
        away_form: list,
        h2h_home_wins: int = 0,
        h2h_draws: int = 0,
        h2h_away_wins: int = 0,
        home_elo: float = 1500,
        away_elo: float = 1500,
        is_neutral: bool = False,
    ) -> dict:
        """
        Predict using manually entered statistics (no API needed).
        Useful for teams not in the API or for custom scenarios.
        """
        # Set Elo ratings manually
        self.ensemble.elo_system.set_rating(-1, home_elo)
        self.ensemble.elo_system.set_rating(-2, away_elo)
        self.ensemble.elo_system._elo_fitted = True
        self.ensemble._elo_fitted = True

        # Build synthetic match lists for form
        def _build_synthetic_matches(team_id, form, avg_scored, avg_conceded):
            """Create synthetic match data from form string."""
            synthetic = []
            for r in form:
                if r == "W":
                    gf, ga = int(avg_scored) + 1, max(0, int(avg_conceded) - 1)
                elif r == "D":
                    g = max(1, round((avg_scored + avg_conceded) / 2))
                    gf, ga = g, g
                else:
                    gf, ga = max(0, int(avg_scored) - 1), int(avg_conceded) + 1
                match_data = {
                    "status": "FINISHED",
                    "homeTeam": {"id": team_id},
                    "awayTeam": {"id": -999},
                    "score": {"fullTime": {"home": gf, "away": ga}},
                    "utcDate": "2024-01-01T00:00:00Z",
                }
                synthetic.append(match_data)
            return synthetic

        home_matches = _build_synthetic_matches(-1, home_form, home_avg_scored, home_avg_conceded)
        away_matches = _build_synthetic_matches(-2, away_form, away_avg_scored, away_avg_conceded)

        total_h2h = h2h_home_wins + h2h_draws + h2h_away_wins
        h2h_matches = []
        # Build synthetic H2H
        for _ in range(h2h_home_wins):
            h2h_matches.append({
                "status": "FINISHED",
                "homeTeam": {"id": -1},
                "awayTeam": {"id": -2},
                "score": {"fullTime": {"home": 2, "away": 1}},
            })
        for _ in range(h2h_draws):
            h2h_matches.append({
                "status": "FINISHED",
                "homeTeam": {"id": -1},
                "awayTeam": {"id": -2},
                "score": {"fullTime": {"home": 1, "away": 1}},
            })
        for _ in range(h2h_away_wins):
            h2h_matches.append({
                "status": "FINISHED",
                "homeTeam": {"id": -1},
                "awayTeam": {"id": -2},
                "score": {"fullTime": {"home": 0, "away": 1}},
            })

        return self.ensemble.predict(
            home_team_id=-1,
            away_team_id=-2,
            home_matches=home_matches,
            away_matches=away_matches,
            h2h_matches=h2h_matches,
            is_neutral=is_neutral,
        )

    def get_upcoming_matches(self, competition_code: str = None,
                              date_from: str = None, date_to: str = None) -> list:
        """Fetch upcoming scheduled matches."""
        return self.fetcher.get_scheduled_matches(competition_code, date_from, date_to)

    def get_standings(self, competition_code: str, season: int = None) -> list:
        """Get competition standings."""
        return self.fetcher.get_standings(competition_code, season)

    def search_team(self, name: str) -> list:
        """Search for teams by name."""
        return self.fetcher.search_team(name)

    def _league_avg(self, competition_code: str = None, season: int = None) -> float:
        """Estimate league average goals per team per game."""
        if not competition_code:
            return 1.35
        matches = self.fetcher.get_matches_by_competition(
            competition_code, season=season, status="FINISHED"
        )
        if not matches:
            return 1.35
        total_goals = 0
        count = 0
        for m in matches:
            score = m.get("score", {}).get("fullTime", {})
            hg = score.get("home")
            ag = score.get("away")
            if hg is not None and ag is not None:
                total_goals += hg + ag
                count += 1
        if count == 0:
            return 1.35
        return (total_goals / count) / 2  # Per team per game
