"""
Configuration for the Football Prediction Bot.
Get a free API key at: https://www.football-data.org/client/register
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- API Configuration ---
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "YOUR_API_KEY_HERE")
FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"

# --- Supported Competitions ---
# Competition codes from football-data.org
COMPETITIONS = {
    # Top European Leagues
    "PL":   "Premier League (England)",
    "PD":   "La Liga (Spain)",
    "BL1":  "Bundesliga (Germany)",
    "SA":   "Serie A (Italy)",
    "FL1":  "Ligue 1 (France)",
    "PPL":  "Primeira Liga (Portugal)",
    "DED":  "Eredivisie (Netherlands)",
    "BSA":  "Brasileiro Série A (Brazil)",
    "ELC":  "Championship (England)",
    # International / National Teams
    "WC":   "FIFA World Cup",
    "EC":   "UEFA European Championship",
    "CLI":  "UEFA Champions League",
    "EL":   "UEFA Europa League",
    "UCL":  "UEFA Champions League",
    "CL":   "UEFA Champions League",
}

# --- Model Weights for Ensemble ---
MODEL_WEIGHTS = {
    "poisson":    0.35,   # Dixon-Coles Poisson model
    "elo":        0.25,   # Elo rating system
    "form":       0.20,   # Recent form (last 6 games)
    "h2h":        0.10,   # Head-to-head history
    "home_away":  0.10,   # Home/away advantage
}

# --- Home Advantage ---
HOME_ADVANTAGE_GOALS = 0.35   # Average extra goals for home team
ELO_HOME_ADVANTAGE   = 100    # Elo points added for home team

# --- Form settings ---
FORM_GAMES = 6           # Number of recent games to consider for form
H2H_GAMES  = 10          # Number of head-to-head games to consider

# --- Elo Settings ---
ELO_K_FACTOR = 32        # Elo K-factor (higher = more reactive)
ELO_DEFAULT  = 1500      # Starting Elo for new teams

# --- Dixon-Coles correction threshold ---
DC_RHO = -0.13           # Correlation parameter for low scores (standard value)
