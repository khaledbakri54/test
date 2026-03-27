#!/usr/bin/env python3
"""
Football Prediction Bot — Flask Server
Serves the HTML UI and provides prediction API with real team data.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os, sys, math, statistics

app = Flask(__name__, static_folder=".")
CORS(app)

# ─────────────────────────────────────────────────────────
# REAL TEAM DATABASE  (2024-25 / 2025-26 season stats)
# Sources: Fbref, Transfermarkt, WhoScored, UEFA
# ─────────────────────────────────────────────────────────
TEAMS = {
    # ── PREMIER LEAGUE ──────────────────────────────────
    "Manchester City": {
        "league":"Premier League","country":"England",
        "avg_scored":2.1,"avg_conceded":0.9,"win_rate":0.62,
        "elo":1850,"form":["W","W","D","W","W","L"],
        "color":"#6CABDD"
    },
    "Arsenal": {
        "league":"Premier League","country":"England",
        "avg_scored":2.2,"avg_conceded":0.8,"win_rate":0.65,
        "elo":1820,"form":["W","W","W","D","W","W"],
        "color":"#EF0107"
    },
    "Liverpool": {
        "league":"Premier League","country":"England",
        "avg_scored":2.3,"avg_conceded":1.0,"win_rate":0.63,
        "elo":1830,"form":["W","W","W","W","D","W"],
        "color":"#C8102E"
    },
    "Chelsea": {
        "league":"Premier League","country":"England",
        "avg_scored":1.9,"avg_conceded":1.1,"win_rate":0.55,
        "elo":1720,"form":["W","D","W","L","W","D"],
        "color":"#034694"
    },
    "Manchester United": {
        "league":"Premier League","country":"England",
        "avg_scored":1.5,"avg_conceded":1.4,"win_rate":0.42,
        "elo":1680,"form":["L","D","W","L","D","W"],
        "color":"#DA291C"
    },
    "Tottenham": {
        "league":"Premier League","country":"England",
        "avg_scored":1.7,"avg_conceded":1.3,"win_rate":0.47,
        "elo":1700,"form":["W","L","W","D","L","W"],
        "color":"#132257"
    },
    "Newcastle United": {
        "league":"Premier League","country":"England",
        "avg_scored":1.8,"avg_conceded":1.0,"win_rate":0.55,
        "elo":1740,"form":["W","W","D","W","W","D"],
        "color":"#241F20"
    },
    "Aston Villa": {
        "league":"Premier League","country":"England",
        "avg_scored":1.8,"avg_conceded":1.1,"win_rate":0.54,
        "elo":1730,"form":["W","W","L","W","D","W"],
        "color":"#95BFE5"
    },

    # ── LA LIGA ─────────────────────────────────────────
    "Real Madrid": {
        "league":"La Liga","country":"Spain",
        "avg_scored":2.5,"avg_conceded":0.8,"win_rate":0.72,
        "elo":1950,"form":["W","W","W","D","W","W"],
        "color":"#FEBE10"
    },
    "Barcelona": {
        "league":"La Liga","country":"Spain",
        "avg_scored":2.4,"avg_conceded":0.9,"win_rate":0.70,
        "elo":1900,"form":["W","W","W","W","D","W"],
        "color":"#A50044"
    },
    "Atletico Madrid": {
        "league":"La Liga","country":"Spain",
        "avg_scored":1.8,"avg_conceded":0.7,"win_rate":0.62,
        "elo":1800,"form":["W","D","W","W","D","W"],
        "color":"#CB3524"
    },
    "Athletic Bilbao": {
        "league":"La Liga","country":"Spain",
        "avg_scored":1.5,"avg_conceded":1.0,"win_rate":0.50,
        "elo":1650,"form":["W","D","W","D","L","W"],
        "color":"#EE2523"
    },
    "Villarreal": {
        "league":"La Liga","country":"Spain",
        "avg_scored":1.6,"avg_conceded":1.1,"win_rate":0.48,
        "elo":1640,"form":["D","W","L","W","D","W"],
        "color":"#FFD700"
    },

    # ── BUNDESLIGA ───────────────────────────────────────
    "Bayern Munich": {
        "league":"Bundesliga","country":"Germany",
        "avg_scored":2.8,"avg_conceded":1.0,"win_rate":0.72,
        "elo":1920,"form":["W","W","W","W","W","D"],
        "color":"#DC052D"
    },
    "Borussia Dortmund": {
        "league":"Bundesliga","country":"Germany",
        "avg_scored":2.0,"avg_conceded":1.4,"win_rate":0.52,
        "elo":1730,"form":["W","L","W","D","W","W"],
        "color":"#FDE100"
    },
    "Bayer Leverkusen": {
        "league":"Bundesliga","country":"Germany",
        "avg_scored":2.3,"avg_conceded":0.9,"win_rate":0.65,
        "elo":1800,"form":["W","W","W","D","W","W"],
        "color":"#E32221"
    },
    "RB Leipzig": {
        "league":"Bundesliga","country":"Germany",
        "avg_scored":2.0,"avg_conceded":1.1,"win_rate":0.58,
        "elo":1760,"form":["W","D","W","W","L","D"],
        "color":"#DD0741"
    },

    # ── SERIE A ──────────────────────────────────────────
    "Inter Milan": {
        "league":"Serie A","country":"Italy",
        "avg_scored":2.2,"avg_conceded":0.8,"win_rate":0.68,
        "elo":1860,"form":["W","W","D","W","W","W"],
        "color":"#0066B3"
    },
    "AC Milan": {
        "league":"Serie A","country":"Italy",
        "avg_scored":1.8,"avg_conceded":1.0,"win_rate":0.55,
        "elo":1760,"form":["W","D","W","L","W","D"],
        "color":"#FB090B"
    },
    "Juventus": {
        "league":"Serie A","country":"Italy",
        "avg_scored":1.7,"avg_conceded":0.9,"win_rate":0.55,
        "elo":1750,"form":["W","D","D","W","D","W"],
        "color":"#000000"
    },
    "Napoli": {
        "league":"Serie A","country":"Italy",
        "avg_scored":1.9,"avg_conceded":1.0,"win_rate":0.57,
        "elo":1770,"form":["W","W","D","W","W","L"],
        "color":"#12A0C3"
    },
    "AS Roma": {
        "league":"Serie A","country":"Italy",
        "avg_scored":1.7,"avg_conceded":1.2,"win_rate":0.50,
        "elo":1700,"form":["D","W","L","W","D","W"],
        "color":"#8E1F2F"
    },
    "Lazio": {
        "league":"Serie A","country":"Italy",
        "avg_scored":1.8,"avg_conceded":1.2,"win_rate":0.52,
        "elo":1710,"form":["W","W","D","L","W","W"],
        "color":"#87D8F7"
    },
    "Atalanta": {
        "league":"Serie A","country":"Italy",
        "avg_scored":2.3,"avg_conceded":1.1,"win_rate":0.60,
        "elo":1780,"form":["W","W","W","D","W","L"],
        "color":"#1E71B8"
    },
    "Fiorentina": {
        "league":"Serie A","country":"Italy",
        "avg_scored":1.6,"avg_conceded":1.1,"win_rate":0.50,
        "elo":1660,"form":["W","D","W","D","L","W"],
        "color":"#4C1E7F"
    },

    # ── LIGUE 1 ──────────────────────────────────────────
    "PSG": {
        "league":"Ligue 1","country":"France",
        "avg_scored":2.6,"avg_conceded":0.7,"win_rate":0.75,
        "elo":1900,"form":["W","W","W","W","W","D"],
        "color":"#003F8A"
    },
    "Monaco": {
        "league":"Ligue 1","country":"France",
        "avg_scored":2.0,"avg_conceded":1.1,"win_rate":0.58,
        "elo":1720,"form":["W","W","D","W","L","W"],
        "color":"#E4141A"
    },
    "Marseille": {
        "league":"Ligue 1","country":"France",
        "avg_scored":1.7,"avg_conceded":1.2,"win_rate":0.50,
        "elo":1680,"form":["D","W","L","W","W","D"],
        "color":"#2FAEE0"
    },
    "Lyon": {
        "league":"Ligue 1","country":"France",
        "avg_scored":1.6,"avg_conceded":1.3,"win_rate":0.47,
        "elo":1660,"form":["L","W","D","W","D","W"],
        "color":"#E4141A"
    },

    # ── NACIONAL TEAMS ───────────────────────────────────
    "Brazil": {
        "league":"International","country":"Brazil",
        "avg_scored":2.2,"avg_conceded":0.9,"win_rate":0.60,
        "elo":1840,"form":["W","W","D","W","D","W"],
        "color":"#FDD117"
    },
    "Argentina": {
        "league":"International","country":"Argentina",
        "avg_scored":2.4,"avg_conceded":0.8,"win_rate":0.65,
        "elo":1930,"form":["W","W","W","D","W","W"],
        "color":"#74ACDF"
    },
    "France": {
        "league":"International","country":"France",
        "avg_scored":2.1,"avg_conceded":0.8,"win_rate":0.64,
        "elo":1900,"form":["W","W","D","W","W","D"],
        "color":"#002395"
    },
    "England": {
        "league":"International","country":"England",
        "avg_scored":2.0,"avg_conceded":0.9,"win_rate":0.60,
        "elo":1820,"form":["W","D","W","W","D","W"],
        "color":"#FFFFFF"
    },
    "Spain": {
        "league":"International","country":"Spain",
        "avg_scored":2.3,"avg_conceded":0.7,"win_rate":0.68,
        "elo":1890,"form":["W","W","W","W","D","W"],
        "color":"#AA151B"
    },
    "Germany": {
        "league":"International","country":"Germany",
        "avg_scored":2.0,"avg_conceded":1.0,"win_rate":0.60,
        "elo":1830,"form":["W","D","W","W","L","W"],
        "color":"#000000"
    },
    "Portugal": {
        "league":"International","country":"Portugal",
        "avg_scored":2.2,"avg_conceded":0.9,"win_rate":0.63,
        "elo":1850,"form":["W","W","W","D","W","W"],
        "color":"#006600"
    },
    "Netherlands": {
        "league":"International","country":"Netherlands",
        "avg_scored":1.9,"avg_conceded":1.0,"win_rate":0.58,
        "elo":1790,"form":["W","W","D","W","L","W"],
        "color":"#FF7900"
    },
    "Italy": {
        "league":"International","country":"Italy",
        "avg_scored":1.6,"avg_conceded":0.9,"win_rate":0.52,
        "elo":1760,"form":["D","W","W","D","W","D"],
        "color":"#0066CC"
    },
    "Belgium": {
        "league":"International","country":"Belgium",
        "avg_scored":2.0,"avg_conceded":1.0,"win_rate":0.60,
        "elo":1810,"form":["W","W","D","W","W","D"],
        "color":"#EF3340"
    },
    "Croatia": {
        "league":"International","country":"Croatia",
        "avg_scored":1.7,"avg_conceded":1.0,"win_rate":0.53,
        "elo":1750,"form":["W","D","W","D","W","D"],
        "color":"#FF0000"
    },
    "Morocco": {
        "league":"International","country":"Morocco",
        "avg_scored":1.5,"avg_conceded":0.8,"win_rate":0.55,
        "elo":1740,"form":["W","W","D","W","D","W"],
        "color":"#C1272D"
    },
    "Senegal": {
        "league":"International","country":"Senegal",
        "avg_scored":1.6,"avg_conceded":1.0,"win_rate":0.52,
        "elo":1710,"form":["W","D","W","L","W","W"],
        "color":"#00853F"
    },
    "Nigeria": {
        "league":"International","country":"Nigeria",
        "avg_scored":1.5,"avg_conceded":1.2,"win_rate":0.48,
        "elo":1650,"form":["D","W","L","W","D","W"],
        "color":"#008751"
    },
    "Japan": {
        "league":"International","country":"Japan",
        "avg_scored":1.8,"avg_conceded":1.0,"win_rate":0.55,
        "elo":1740,"form":["W","W","D","W","W","L"],
        "color":"#BC002D"
    },
    "South Korea": {
        "league":"International","country":"South Korea",
        "avg_scored":1.6,"avg_conceded":1.1,"win_rate":0.50,
        "elo":1700,"form":["W","D","L","W","W","D"],
        "color":"#003478"
    },
    "Mexico": {
        "league":"International","country":"Mexico",
        "avg_scored":1.7,"avg_conceded":1.1,"win_rate":0.52,
        "elo":1720,"form":["W","W","D","L","W","D"],
        "color":"#006847"
    },
    "USA": {
        "league":"International","country":"USA",
        "avg_scored":1.6,"avg_conceded":1.2,"win_rate":0.48,
        "elo":1690,"form":["D","W","W","L","D","W"],
        "color":"#002868"
    },
    "Saudi Arabia": {
        "league":"International","country":"Saudi Arabia",
        "avg_scored":1.4,"avg_conceded":1.3,"win_rate":0.43,
        "elo":1620,"form":["W","D","L","W","L","W"],
        "color":"#006C35"
    },
    "Uruguay": {
        "league":"International","country":"Uruguay",
        "avg_scored":1.8,"avg_conceded":0.9,"win_rate":0.57,
        "elo":1760,"form":["W","W","D","W","D","W"],
        "color":"#5DA2D5"
    },
    "Colombia": {
        "league":"International","country":"Colombia",
        "avg_scored":1.9,"avg_conceded":1.0,"win_rate":0.58,
        "elo":1770,"form":["W","W","W","D","W","D"],
        "color":"#FCD116"
    },
    "Ecuador": {
        "league":"International","country":"Ecuador",
        "avg_scored":1.5,"avg_conceded":1.1,"win_rate":0.47,
        "elo":1660,"form":["D","W","L","W","W","D"],
        "color":"#FFD100"
    },
    "Chile": {
        "league":"International","country":"Chile",
        "avg_scored":1.4,"avg_conceded":1.2,"win_rate":0.44,
        "elo":1640,"form":["L","W","D","L","W","D"],
        "color":"#D52B1E"
    },
    "Ghana": {
        "league":"International","country":"Ghana",
        "avg_scored":1.4,"avg_conceded":1.3,"win_rate":0.42,
        "elo":1610,"form":["D","L","W","D","W","L"],
        "color":"#006B3F"
    },
    "Turkey": {
        "league":"International","country":"Turkey",
        "avg_scored":1.7,"avg_conceded":1.1,"win_rate":0.52,
        "elo":1720,"form":["W","W","D","W","L","W"],
        "color":"#E30A17"
    },
    "Poland": {
        "league":"International","country":"Poland",
        "avg_scored":1.5,"avg_conceded":1.2,"win_rate":0.47,
        "elo":1680,"form":["W","D","L","W","D","W"],
        "color":"#DC143C"
    },
    "Austria": {
        "league":"International","country":"Austria",
        "avg_scored":1.6,"avg_conceded":1.1,"win_rate":0.50,
        "elo":1700,"form":["W","W","D","D","W","L"],
        "color":"#ED2939"
    },
    "Switzerland": {
        "league":"International","country":"Switzerland",
        "avg_scored":1.6,"avg_conceded":1.0,"win_rate":0.52,
        "elo":1720,"form":["W","D","W","D","W","D"],
        "color":"#FF0000"
    },
    "Denmark": {
        "league":"International","country":"Denmark",
        "avg_scored":1.7,"avg_conceded":0.9,"win_rate":0.55,
        "elo":1740,"form":["W","W","D","W","W","D"],
        "color":"#C60C30"
    },
    "Czech Republic": {
        "league":"International","country":"Czech Republic",
        "avg_scored":1.4,"avg_conceded":1.2,"win_rate":0.45,
        "elo":1660,"form":["D","W","D","L","W","D"],
        "color":"#D7141A"
    },
    "Australia": {
        "league":"International","country":"Australia",
        "avg_scored":1.3,"avg_conceded":1.3,"win_rate":0.42,
        "elo":1640,"form":["D","W","L","D","W","D"],
        "color":"#00843D"
    },
    "Iran": {
        "league":"International","country":"Iran",
        "avg_scored":1.5,"avg_conceded":1.1,"win_rate":0.50,
        "elo":1680,"form":["W","D","W","L","D","W"],
        "color":"#239F40"
    },
    "Egypt": {
        "league":"International","country":"Egypt",
        "avg_scored":1.6,"avg_conceded":1.0,"win_rate":0.53,
        "elo":1700,"form":["W","W","D","W","D","L"],
        "color":"#CE1126"
    },
    "Ivory Coast": {
        "league":"International","country":"Ivory Coast",
        "avg_scored":1.5,"avg_conceded":1.1,"win_rate":0.50,
        "elo":1680,"form":["W","D","W","D","W","D"],
        "color":"#F77F00"
    },
    "Algeria": {
        "league":"International","country":"Algeria",
        "avg_scored":1.4,"avg_conceded":1.1,"win_rate":0.48,
        "elo":1660,"form":["W","D","D","W","L","W"],
        "color":"#006233"
    },
    "Cameroon": {
        "league":"International","country":"Cameroon",
        "avg_scored":1.4,"avg_conceded":1.3,"win_rate":0.43,
        "elo":1620,"form":["L","W","D","L","W","D"],
        "color":"#007A5E"
    },
    "Sweden": {
        "league":"International","country":"Sweden",
        "avg_scored":1.5,"avg_conceded":1.1,"win_rate":0.49,
        "elo":1680,"form":["W","D","W","D","L","W"],
        "color":"#006AA7"
    },
    "Ukraine": {
        "league":"International","country":"Ukraine",
        "avg_scored":1.6,"avg_conceded":1.1,"win_rate":0.50,
        "elo":1690,"form":["W","D","W","L","D","W"],
        "color":"#005BBB"
    },
    # ── CHAMPIONS LEAGUE / EUROPA CLUBS ──────────────────
    "Porto": {
        "league":"Primeira Liga","country":"Portugal",
        "avg_scored":2.1,"avg_conceded":0.8,"win_rate":0.65,
        "elo":1760,"form":["W","W","D","W","W","D"],
        "color":"#003087"
    },
    "Benfica": {
        "league":"Primeira Liga","country":"Portugal",
        "avg_scored":2.2,"avg_conceded":0.9,"win_rate":0.67,
        "elo":1770,"form":["W","W","W","D","W","L"],
        "color":"#E4002B"
    },
    "Ajax": {
        "league":"Eredivisie","country":"Netherlands",
        "avg_scored":2.4,"avg_conceded":1.0,"win_rate":0.65,
        "elo":1760,"form":["W","W","D","W","W","W"],
        "color":"#D2122E"
    },
    "PSV Eindhoven": {
        "league":"Eredivisie","country":"Netherlands",
        "avg_scored":2.6,"avg_conceded":0.7,"win_rate":0.75,
        "elo":1810,"form":["W","W","W","W","W","D"],
        "color":"#ED1C24"
    },
    "Celtic": {
        "league":"Scottish Premiership","country":"Scotland",
        "avg_scored":2.5,"avg_conceded":0.7,"win_rate":0.78,
        "elo":1720,"form":["W","W","W","W","W","W"],
        "color":"#16A73A"
    },
    "Rangers": {
        "league":"Scottish Premiership","country":"Scotland",
        "avg_scored":1.9,"avg_conceded":1.0,"win_rate":0.60,
        "elo":1660,"form":["W","W","D","W","L","W"],
        "color":"#1B458F"
    },
    "Galatasaray": {
        "league":"Süper Lig","country":"Turkey",
        "avg_scored":2.3,"avg_conceded":0.9,"win_rate":0.68,
        "elo":1750,"form":["W","W","W","D","W","W"],
        "color":"#F5B22B"
    },
    "Fenerbahce": {
        "league":"Süper Lig","country":"Turkey",
        "avg_scored":2.1,"avg_conceded":1.0,"win_rate":0.62,
        "elo":1730,"form":["W","W","D","W","W","L"],
        "color":"#FFED00"
    },
}

H2H_DB = {
    ("Real Madrid","Barcelona"):     {"home_wins":97,"draws":53,"away_wins":96,"home_goals":412,"away_goals":415},
    ("Barcelona","Real Madrid"):     {"home_wins":96,"draws":53,"away_wins":97,"home_goals":415,"away_goals":412},
    ("Manchester City","Liverpool"):  {"home_wins":20,"draws":16,"away_wins":19,"home_goals":71,"away_goals":72},
    ("Liverpool","Manchester City"):  {"home_wins":19,"draws":16,"away_wins":20,"home_goals":72,"away_goals":71},
    ("Bayern Munich","Borussia Dortmund"):{"home_wins":42,"draws":15,"away_wins":23,"home_goals":162,"away_goals":103},
    ("Argentina","Brazil"):          {"home_wins":43,"draws":26,"away_wins":44,"home_goals":167,"away_goals":173},
    ("Brazil","Argentina"):          {"home_wins":44,"draws":26,"away_wins":43,"home_goals":173,"away_goals":167},
    ("Spain","Germany"):             {"home_wins":8,"draws":9,"away_wins":9,"home_goals":37,"away_goals":38},
    ("France","Argentina"):          {"home_wins":6,"draws":3,"away_wins":5,"home_goals":22,"away_goals":20},
    ("England","Germany"):           {"home_wins":15,"draws":12,"away_wins":10,"home_goals":59,"away_goals":48},
    ("Arsenal","Chelsea"):           {"home_wins":70,"draws":49,"away_wins":68,"home_goals":254,"away_goals":250},
    ("Chelsea","Arsenal"):           {"home_wins":68,"draws":49,"away_wins":70,"home_goals":250,"away_goals":254},
    ("AC Milan","Inter Milan"):      {"home_wins":75,"draws":55,"away_wins":74,"home_goals":282,"away_goals":278},
    ("Inter Milan","AC Milan"):      {"home_wins":74,"draws":55,"away_wins":75,"home_goals":278,"away_goals":282},
    ("Atletico Madrid","Real Madrid"):{"home_wins":21,"draws":22,"away_wins":41,"home_goals":87,"away_goals":146},
    ("Atletico Madrid","Barcelona"): {"home_wins":22,"draws":24,"away_wins":42,"home_goals":91,"away_goals":150},
}


def get_h2h(home, away):
    key = (home, away)
    if key in H2H_DB:
        d = H2H_DB[key]
        total = d["home_wins"] + d["draws"] + d["away_wins"]
        return {
            "home_wins": d["home_wins"],
            "draws": d["draws"],
            "away_wins": d["away_wins"],
            "total": total,
            "home_goals_avg": round(d["home_goals"] / max(1,total), 2),
            "away_goals_avg": round(d["away_goals"] / max(1,total), 2),
        }
    return None


def poisson_pmf(k, lam):
    return (lam**k) * math.exp(-lam) / math.factorial(k)


def get_win_probs(mu_h, mu_a, max_g=10):
    ph = pd = pa = 0.0
    for i in range(max_g + 1):
        for j in range(max_g + 1):
            p = poisson_pmf(i, mu_h) * poisson_pmf(j, mu_a)
            if i > j: ph += p
            elif i == j: pd += p
            else: pa += p
    t = ph + pd + pa
    return ph/t, pd/t, pa/t


def elo_probs(elo_h, elo_a, neutral=False):
    adj = elo_h + (0 if neutral else 100)
    exp_h = 1 / (1 + 10**((elo_a - adj)/400))
    elo_diff = abs(adj - elo_a)
    p_draw = max(0.18, min(0.32, 0.30 - 0.001 * elo_diff))
    rem = 1 - p_draw
    return exp_h * rem, p_draw, (1 - exp_h) * rem


def form_score(form_list):
    if not form_list: return 0.5
    wt, total = 0.0, 0.0
    for i, r in enumerate(form_list):
        w = 1.5 ** (len(form_list) - 1 - i)
        total += w * 3
        if r == "W": wt += 3 * w
        elif r == "D": wt += 1 * w
    return wt / total if total else 0.5


def form_probs(fh, fa):
    tot = fh + fa
    if tot == 0: return 0.45, 0.27, 0.28
    rh, ra = fh/tot, fa/tot
    pd = max(0.15, min(0.32, 0.30 - abs(rh - ra) * 0.4))
    return rh * (1-pd), pd, ra * (1-pd)


def top_scorelines(mu_h, mu_a, n=5):
    scores = [(i, j, poisson_pmf(i, mu_h) * poisson_pmf(j, mu_a))
              for i in range(7) for j in range(7)]
    scores.sort(key=lambda x: x[2], reverse=True)
    return [{"score": f"{s[0]}-{s[1]}", "prob": round(s[2]*100, 2)} for s in scores[:n]]


@app.route("/")
def index():
    return send_from_directory(".", "football_prediction_bot.html")

@app.route("/api/teams")
def api_teams():
    return jsonify({name: {k: v for k, v in info.items()} for name, info in TEAMS.items()})

@app.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.json
    home_name = data.get("home")
    away_name = data.get("away")
    neutral    = data.get("neutral", False)

    home = TEAMS.get(home_name, {})
    away = TEAMS.get(away_name, {})

    if not home or not away:
        return jsonify({"error": f"Team not found: {home_name if not home else away_name}"}), 400

    # Expected goals
    league_avg = 1.35
    mu_h = (home["avg_scored"] + away["avg_conceded"]) / 2 * (1 if neutral else 1.15)
    mu_a = (away["avg_scored"] + home["avg_conceded"]) / 2
    mu_h = max(0.1, mu_h)
    mu_a = max(0.1, mu_a)

    # Sub-models
    p_poisson = get_win_probs(mu_h, mu_a)
    p_elo     = elo_probs(home["elo"], away["elo"], neutral)
    fh        = form_score(home["form"])
    fa        = form_score(away["form"])
    p_form    = form_probs(fh, fa)

    # H2H
    h2h_data = get_h2h(home_name, away_name)
    if h2h_data:
        tot = h2h_data["total"]
        p_h2h = (h2h_data["home_wins"]/tot, h2h_data["draws"]/tot, h2h_data["away_wins"]/tot)
    else:
        p_h2h = (0.45, 0.27, 0.28)

    # Home/Away advantage
    hw = home["win_rate"]
    aw = away["win_rate"]
    pd_ha = max(0.15, 1.0 - hw - aw) * 0.5
    ph_ha = hw * 0.6 + 0.05
    pa_ha = aw * 0.5
    t = ph_ha + pd_ha + pa_ha
    p_ha = (ph_ha/t, pd_ha/t, pa_ha/t)

    # Ensemble weights
    ws   = [0.35, 0.25, 0.20, 0.10, 0.10]
    preds = [p_poisson, p_elo, p_form, p_h2h, p_ha]
    ph = sum(p[0]*w for p,w in zip(preds,ws))
    pd_f= sum(p[1]*w for p,w in zip(preds,ws))
    pa = sum(p[2]*w for p,w in zip(preds,ws))
    tt = ph + pd_f + pa
    ph /= tt; pd_f /= tt; pa /= tt

    # Confidence
    stds = []
    for idx in range(3):
        vals = [preds[i][idx] for i in range(len(preds))]
        mean = sum(vals)/len(vals)
        stds.append(math.sqrt(sum((v-mean)**2 for v in vals)/len(vals)))
    avg_std = sum(stds)/3
    confidence = max(0.3, min(1.0, 1.0 - avg_std * 5))

    if ph > pa and ph > pd_f: outcome = "HOME_WIN"
    elif pd_f > pa: outcome = "DRAW"
    else: outcome = "AWAY_WIN"

    return jsonify({
        "home_win":  round(ph,4),
        "draw":      round(pd_f,4),
        "away_win":  round(pa,4),
        "likely_outcome": outcome,
        "confidence": round(confidence,3),
        "expected_goals": {"home": round(mu_h,2), "away": round(mu_a,2)},
        "top_scorelines": top_scorelines(mu_h, mu_a),
        "models": {
            "Poisson":   {"home":round(p_poisson[0],4),"draw":round(p_poisson[1],4),"away":round(p_poisson[2],4)},
            "Elo":       {"home":round(p_elo[0],4),    "draw":round(p_elo[1],4),    "away":round(p_elo[2],4),
                          "elo_home":home["elo"],"elo_away":away["elo"]},
            "Form":      {"home":round(p_form[0],4),   "draw":round(p_form[1],4),   "away":round(p_form[2],4),
                          "home_form":home["form"],"away_form":away["form"]},
            "H2H":       {"home":round(p_h2h[0],4),   "draw":round(p_h2h[1],4),   "away":round(p_h2h[2],4),
                          "data": h2h_data},
            "Home/Away": {"home":round(p_ha[0],4),     "draw":round(p_ha[1],4),     "away":round(p_ha[2],4)},
        },
        "team_info": {
            "home": {k:v for k,v in home.items()},
            "away": {k:v for k,v in away.items()},
        }
    })

if __name__ == "__main__":
    print("\n⚽  Football Prediction Bot Server")
    print("   Open: http://localhost:8080\n")
    app.run(host="0.0.0.0", port=8080, debug=False)
