"""
Display utilities for the Football Prediction Bot CLI.
Colorful, formatted output using colorama and tabulate.
"""

from colorama import Fore, Back, Style, init
from tabulate import tabulate

init(autoreset=True)

BANNER = f"""
{Fore.GREEN}╔══════════════════════════════════════════════════════════════╗
║  ⚽  FOOTBALL PREDICTION BOT — AI-Powered Match Analysis  ⚽  ║
║      Poisson · Elo · Form · H2H · Standings Ensemble          ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""


def print_banner():
    print(BANNER)


def _bar(prob: float, width: int = 30) -> str:
    """Draw a probability bar."""
    filled = int(prob * width)
    return "█" * filled + "░" * (width - filled)


def _outcome_color(outcome: str) -> str:
    if outcome == "HOME_WIN":
        return Fore.CYAN
    elif outcome == "DRAW":
        return Fore.YELLOW
    else:
        return Fore.RED


def print_prediction(result: dict, home_name: str, away_name: str,
                     competition: str = ""):
    """Print formatted prediction result."""
    sep = f"{Fore.WHITE}{'─' * 64}{Style.RESET_ALL}"
    print(sep)
    print(f"\n  {Fore.WHITE}{Style.BRIGHT}📋 MATCH PREDICTION{Style.RESET_ALL}")
    if competition:
        print(f"  {Fore.MAGENTA}🏆 {competition}{Style.RESET_ALL}")
    print(f"\n  {Fore.CYAN}{home_name:<25}{Style.RESET_ALL}  vs  "
          f"{Fore.RED}{away_name}{Style.RESET_ALL}\n")

    p_home = result["home_win"]
    p_draw = result["draw"]
    p_away = result["away_win"]
    outcome = result["likely_outcome"]
    conf = result["confidence"]

    # Probability bars
    print(f"  {Fore.CYAN}HOME WIN  {_bar(p_home)} {p_home*100:5.1f}%{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}DRAW      {_bar(p_draw)} {p_draw*100:5.1f}%{Style.RESET_ALL}")
    print(f"  {Fore.RED}AWAY WIN  {_bar(p_away)} {p_away*100:5.1f}%{Style.RESET_ALL}")

    # Likely outcome
    color = _outcome_color(outcome)
    label = {"HOME_WIN": f"{home_name} Win",
             "DRAW": "Draw",
             "AWAY_WIN": f"{away_name} Win"}[outcome]
    print(f"\n  {color}► Likely Result: {Style.BRIGHT}{label}{Style.RESET_ALL}")

    # Confidence
    conf_color = Fore.GREEN if conf >= 0.7 else (Fore.YELLOW if conf >= 0.5 else Fore.RED)
    print(f"  {conf_color}► Confidence: {conf*100:.1f}%{Style.RESET_ALL}")

    # Expected goals
    xg = result.get("expected_goals", {})
    print(f"\n  {Fore.WHITE}📊 Expected Goals:{Style.RESET_ALL} "
          f"{Fore.CYAN}{home_name}: {xg.get('home', '?')}{Style.RESET_ALL}  "
          f"{Fore.RED}{away_name}: {xg.get('away', '?')}{Style.RESET_ALL}")

    # Top scorelines
    scores = result.get("top_scorelines", [])
    if scores:
        print(f"\n  {Fore.WHITE}🎯 Most Likely Scorelines:{Style.RESET_ALL}")
        rows = [[s["score"], f"{s['probability']}%"] for s in scores]
        table = tabulate(rows, headers=["Score", "Probability"],
                         tablefmt="simple", numalign="right")
        for line in table.split("\n"):
            print(f"    {line}")

    # Sub-model breakdown
    analysis = result.get("analysis", {})
    print(f"\n  {Fore.WHITE}🔬 Model Breakdown:{Style.RESET_ALL}")
    model_rows = []
    for model_name in ["poisson", "elo", "form", "h2h", "home_away"]:
        m = analysis.get(model_name, {})
        if "home" in m:
            model_rows.append([
                model_name.upper(),
                f"{m['home']*100:.1f}%",
                f"{m['draw']*100:.1f}%",
                f"{m['away']*100:.1f}%",
            ])
    if model_rows:
        headers = ["Model", "Home", "Draw", "Away"]
        table = tabulate(model_rows, headers=headers, tablefmt="simple")
        for line in table.split("\n"):
            print(f"    {line}")

    # Form info
    form_data = analysis.get("form", {})
    if "home_form" in form_data:
        print(f"\n  {Fore.WHITE}📈 Form (last 6):{Style.RESET_ALL}")
        home_form_str = " ".join(
            (Fore.GREEN + "W" if r == "W" else
             Fore.YELLOW + "D" if r == "D" else
             Fore.RED + "L") + Style.RESET_ALL
            for r in form_data["home_form"]
        )
        away_form_str = " ".join(
            (Fore.GREEN + "W" if r == "W" else
             Fore.YELLOW + "D" if r == "D" else
             Fore.RED + "L") + Style.RESET_ALL
            for r in form_data["away_form"]
        )
        print(f"    {Fore.CYAN}{home_name}:{Style.RESET_ALL} {home_form_str}")
        print(f"    {Fore.RED}{away_name}:{Style.RESET_ALL} {away_form_str}")

    # Elo ratings
    elo_data = analysis.get("elo", {})
    if "elo_home" in elo_data:
        print(f"\n  {Fore.WHITE}⚡ Elo Ratings:{Style.RESET_ALL} "
              f"{Fore.CYAN}{home_name}: {elo_data['elo_home']}{Style.RESET_ALL}  "
              f"{Fore.RED}{away_name}: {elo_data['elo_away']}{Style.RESET_ALL}")

    # H2H
    h2h = analysis.get("h2h", {})
    if "total_games" in h2h and h2h["total_games"] > 0:
        print(f"\n  {Fore.WHITE}⚔  Head-to-Head ({h2h['total_games']} games):{Style.RESET_ALL} "
              f"{Fore.CYAN}{home_name} {h2h['home_wins']}W{Style.RESET_ALL}  "
              f"{Fore.YELLOW}{h2h['draws']}D{Style.RESET_ALL}  "
              f"{Fore.RED}{h2h['away_wins']}W {away_name}{Style.RESET_ALL}")

    print(f"\n{sep}\n")


def print_competitions_table(competitions: list):
    """Print available competitions."""
    rows = [[c["code"], c["name"], c.get("area", {}).get("name", "")] for c in competitions]
    print(tabulate(rows, headers=["Code", "Competition", "Country"], tablefmt="rounded_grid"))


def print_upcoming_matches(matches: list):
    """Print upcoming scheduled matches."""
    rows = []
    for m in matches:
        home = m.get("homeTeam", {}).get("name", "TBD")
        away = m.get("awayTeam", {}).get("name", "TBD")
        date = m.get("utcDate", "")[:10]
        comp = m.get("competition", {}).get("name", "")
        rows.append([date, comp, home, "vs", away, m.get("id", "")])
    print(tabulate(rows, headers=["Date", "Competition", "Home", "", "Away", "ID"],
                   tablefmt="rounded_grid"))


def print_standings(standings: list, competition_name: str = ""):
    """Print league standings table."""
    if competition_name:
        print(f"\n{Fore.GREEN}🏆 {competition_name} Standings{Style.RESET_ALL}\n")
    rows = []
    for entry in standings:
        team = entry.get("team", {}).get("name", "?")
        rows.append([
            entry.get("position", ""),
            team,
            entry.get("playedGames", 0),
            entry.get("won", 0),
            entry.get("draw", 0),
            entry.get("lost", 0),
            entry.get("goalsFor", 0),
            entry.get("goalsAgainst", 0),
            entry.get("goalDifference", 0),
            entry.get("points", 0),
        ])
    headers = ["#", "Team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"]
    print(tabulate(rows, headers=headers, tablefmt="rounded_grid"))
