"""
Data fetcher for football-data.org API.
Retrieves matches, standings, team stats for leagues and national teams.
"""

import time
import requests
from typing import Optional
from config import FOOTBALL_DATA_API_KEY, FOOTBALL_DATA_BASE_URL, COMPETITIONS


class FootballDataFetcher:
    """Fetches football data from football-data.org API."""

    def __init__(self, api_key: str = FOOTBALL_DATA_API_KEY):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "X-Auth-Token": self.api_key,
            "Content-Type": "application/json",
        })
        self._cache: dict = {}

    def _get(self, endpoint: str, params: dict = None) -> Optional[dict]:
        """Make a GET request with rate-limit handling and caching."""
        url = f"{FOOTBALL_DATA_BASE_URL}/{endpoint}"
        cache_key = f"{url}?{params}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        try:
            resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code == 429:
                print("[!] Rate limited. Waiting 60 seconds...")
                time.sleep(60)
                resp = self.session.get(url, params=params, timeout=15)
            if resp.status_code == 403:
                print("[!] API key invalid or subscription required for this endpoint.")
                return None
            resp.raise_for_status()
            data = resp.json()
            self._cache[cache_key] = data
            return data
        except requests.RequestException as e:
            print(f"[!] API error: {e}")
            return None

    def get_competitions(self) -> list:
        """List all available competitions."""
        data = self._get("competitions")
        if not data:
            return []
        return data.get("competitions", [])

    def get_matches_by_competition(self, competition_code: str, season: int = None,
                                   status: str = None) -> list:
        """Get all matches for a competition, optionally filtered by season/status."""
        params = {}
        if season:
            params["season"] = season
        if status:
            params["status"] = status
        data = self._get(f"competitions/{competition_code}/matches", params=params)
        if not data:
            return []
        return data.get("matches", [])

    def get_team_matches(self, team_id: int, limit: int = 20, status: str = None) -> list:
        """Get recent matches for a specific team."""
        params = {"limit": limit}
        if status:
            params["status"] = status
        data = self._get(f"teams/{team_id}/matches", params=params)
        if not data:
            return []
        return data.get("matches", [])

    def get_standings(self, competition_code: str, season: int = None) -> list:
        """Get current standings for a competition."""
        params = {}
        if season:
            params["season"] = season
        data = self._get(f"competitions/{competition_code}/standings", params=params)
        if not data:
            return []
        standings = data.get("standings", [])
        # Return total standings table
        for s in standings:
            if s.get("type") == "TOTAL":
                return s.get("table", [])
        return standings[0].get("table", []) if standings else []

    def get_team(self, team_id: int) -> Optional[dict]:
        """Get team details."""
        return self._get(f"teams/{team_id}")

    def get_competition_teams(self, competition_code: str, season: int = None) -> list:
        """Get all teams in a competition."""
        params = {}
        if season:
            params["season"] = season
        data = self._get(f"competitions/{competition_code}/teams", params=params)
        if not data:
            return []
        return data.get("teams", [])

    def get_head_to_head(self, match_id: int, limit: int = 10) -> list:
        """Get head-to-head records from a specific match context."""
        data = self._get(f"matches/{match_id}/head2head", params={"limit": limit})
        if not data:
            return []
        return data.get("matches", [])

    def search_team(self, name: str) -> list:
        """Search for teams by name."""
        params = {"name": name}
        data = self._get("teams", params=params)
        if not data:
            return []
        return data.get("teams", [])

    def get_scheduled_matches(self, competition_code: str = None,
                               date_from: str = None, date_to: str = None) -> list:
        """Get upcoming scheduled matches."""
        params = {"status": "SCHEDULED"}
        if competition_code:
            params["competitions"] = competition_code
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to
        data = self._get("matches", params=params)
        if not data:
            return []
        return data.get("matches", [])
