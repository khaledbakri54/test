#!/usr/bin/env python3
"""
Football Prediction Bot — Main CLI Entry Point

Usage:
    python main.py predict --home-id 64 --away-id 65 --competition PL
    python main.py predict --manual
    python main.py upcoming --competition PL
    python main.py standings --competition PL
    python main.py train --competition PL

Get a free API key at: https://www.football-data.org/client/register
Then set it:  export FOOTBALL_DATA_API_KEY=your_key_here
Or add it to a .env file in this directory.
"""

import sys
import argparse
from predictor import FootballPredictor
from utils.display import (print_banner, print_prediction,
                            print_upcoming_matches, print_standings)
from config import COMPETITIONS, FOOTBALL_DATA_API_KEY
from colorama import Fore, Style, init

init(autoreset=True)


def cmd_predict_api(args, predictor: FootballPredictor):
    """Predict a match using team IDs from the API."""
    if args.competition and args.competition not in predictor._trained_competitions:
        predictor.train_on_competition(args.competition, season=args.season)

    print(f"\n{Fore.WHITE}[*] Fetching team info...{Style.RESET_ALL}")
    home_info = predictor.fetcher.get_team(args.home_id)
    away_info = predictor.fetcher.get_team(args.away_id)

    home_name = home_info.get("name", f"Team {args.home_id}") if home_info else f"Team {args.home_id}"
    away_name  = away_info.get("name", f"Team {args.away_id}") if away_info else f"Team {args.away_id}"
    comp_name  = COMPETITIONS.get(args.competition, args.competition) if args.competition else ""

    print(f"[*] Predicting: {home_name} vs {away_name}")
    result = predictor.predict_by_ids(
        home_team_id=args.home_id,
        away_team_id=args.away_id,
        competition_code=args.competition,
        is_neutral=args.neutral,
        season=args.season,
    )
    print_prediction(result, home_name, away_name, competition=comp_name)


def cmd_predict_manual(predictor: FootballPredictor):
    """Interactive manual prediction — no API key needed."""
    print(f"\n{Fore.CYAN}=== Manual Prediction Mode ==={Style.RESET_ALL}")
    print("Enter team statistics manually. Press Enter to use default values.\n")

    def prompt_float(msg, default):
        val = input(f"  {msg} [{default}]: ").strip()
        return float(val) if val else default

    def prompt_int(msg, default):
        val = input(f"  {msg} [{default}]: ").strip()
        return int(val) if val else default

    def prompt_form(msg):
        print(f"  {msg} (e.g. W W D L W W — most recent first, space-separated):")
        raw = input("  > ").strip().upper()
        return [r for r in raw.split() if r in ("W", "D", "L")]

    home_name = input("\n  Home team name: ").strip() or "Home Team"
    away_name = input("  Away team name: ").strip() or "Away Team"
    neutral   = input("  Neutral venue? (y/N): ").strip().lower() == "y"

    print(f"\n  {Fore.CYAN}--- {home_name} Stats ---{Style.RESET_ALL}")
    home_avg_scored    = prompt_float("Avg goals scored per game", 1.4)
    home_avg_conceded  = prompt_float("Avg goals conceded per game", 1.1)
    home_win_rate      = prompt_float("Win rate (0-1)", 0.5)
    home_elo           = prompt_float("Elo rating (default 1500)", 1500)
    home_form          = prompt_form(f"{home_name} recent form")

    print(f"\n  {Fore.RED}--- {away_name} Stats ---{Style.RESET_ALL}")
    away_avg_scored    = prompt_float("Avg goals scored per game", 1.2)
    away_avg_conceded  = prompt_float("Avg goals conceded per game", 1.3)
    away_win_rate      = prompt_float("Win rate (0-1)", 0.4)
    away_elo           = prompt_float("Elo rating (default 1500)", 1500)
    away_form          = prompt_form(f"{away_name} recent form")

    print(f"\n  {Fore.WHITE}--- Head-to-Head ---{Style.RESET_ALL}")
    h2h_home_wins = prompt_int(f"{home_name} wins in H2H", 3)
    h2h_draws     = prompt_int("Draws in H2H", 2)
    h2h_away_wins = prompt_int(f"{away_name} wins in H2H", 2)

    print(f"\n{Fore.WHITE}[*] Computing prediction...{Style.RESET_ALL}")
    result = predictor.predict_manual(
        home_avg_scored=home_avg_scored,
        home_avg_conceded=home_avg_conceded,
        home_win_rate=home_win_rate,
        home_form=home_form,
        away_avg_scored=away_avg_scored,
        away_avg_conceded=away_avg_conceded,
        away_win_rate=away_win_rate,
        away_form=away_form,
        h2h_home_wins=h2h_home_wins,
        h2h_draws=h2h_draws,
        h2h_away_wins=h2h_away_wins,
        home_elo=home_elo,
        away_elo=away_elo,
        is_neutral=neutral,
    )
    print_prediction(result, home_name, away_name)


def cmd_upcoming(args, predictor: FootballPredictor):
    """Show upcoming scheduled matches."""
    matches = predictor.get_upcoming_matches(
        competition_code=args.competition,
        date_from=args.date_from,
        date_to=args.date_to,
    )
    if not matches:
        print(f"{Fore.YELLOW}[!] No upcoming matches found.{Style.RESET_ALL}")
        return
    print(f"\n{Fore.GREEN}Upcoming Matches ({len(matches)} found):{Style.RESET_ALL}\n")
    print_upcoming_matches(matches)


def cmd_standings(args, predictor: FootballPredictor):
    """Show competition standings."""
    comp = args.competition
    standings = predictor.get_standings(comp, season=args.season)
    if not standings:
        print(f"{Fore.YELLOW}[!] No standings data found for {comp}.{Style.RESET_ALL}")
        return
    comp_name = COMPETITIONS.get(comp, comp)
    print_standings(standings, comp_name)


def cmd_train(args, predictor: FootballPredictor):
    """Train models on competition data."""
    predictor.train_on_competition(args.competition, season=args.season)


def cmd_competitions(_args, _predictor):
    """List supported competition codes."""
    from tabulate import tabulate
    rows = [[code, name] for code, name in COMPETITIONS.items()]
    print(f"\n{Fore.GREEN}Supported Competitions:{Style.RESET_ALL}\n")
    print(tabulate(rows, headers=["Code", "Name"], tablefmt="rounded_grid"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Football Prediction Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Predict using API (team IDs):
  python main.py predict --home-id 64 --away-id 65 --competition PL

  # Predict using manual stats (no API key):
  python main.py predict --manual

  # Show upcoming Premier League matches:
  python main.py upcoming --competition PL

  # Show La Liga standings:
  python main.py standings --competition PD

  # List all supported competitions:
  python main.py competitions

  # Train model on Champions League data:
  python main.py train --competition CL

Common Team IDs (football-data.org):
  Arsenal=57, Chelsea=61, Liverpool=64, Man City=65, Man Utd=66
  Real Madrid=86, Barcelona=81, Atletico Madrid=78
  Bayern Munich=5, Borussia Dortmund=4
  PSG=524, Juventus=109, AC Milan=98, Inter Milan=108
  Brazil=764, Argentina=762, France=773, Germany=759, England=770
        """
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # predict
    pred = sub.add_parser("predict", help="Predict a match outcome")
    pred.add_argument("--home-id",    type=int, help="Home team ID (football-data.org)")
    pred.add_argument("--away-id",    type=int, help="Away team ID (football-data.org)")
    pred.add_argument("--competition", type=str, help="Competition code (e.g. PL, CL, WC)")
    pred.add_argument("--season",     type=int, help="Season year (e.g. 2024)")
    pred.add_argument("--neutral",    action="store_true", help="Neutral venue match")
    pred.add_argument("--manual",     action="store_true", help="Enter stats manually (no API)")

    # upcoming
    up = sub.add_parser("upcoming", help="List upcoming scheduled matches")
    up.add_argument("--competition", type=str, help="Competition code")
    up.add_argument("--date-from",   type=str, help="Start date YYYY-MM-DD")
    up.add_argument("--date-to",     type=str, help="End date YYYY-MM-DD")

    # standings
    st = sub.add_parser("standings", help="Show competition standings")
    st.add_argument("competition", type=str, help="Competition code (e.g. PL)")
    st.add_argument("--season", type=int, help="Season year")

    # train
    tr = sub.add_parser("train", help="Train models on a competition's historical data")
    tr.add_argument("competition", type=str, help="Competition code")
    tr.add_argument("--season", type=int, help="Season year")

    # competitions
    sub.add_parser("competitions", help="List supported competition codes and IDs")

    return parser


def main():
    print_banner()
    parser = build_parser()
    args = parser.parse_args()

    api_key = FOOTBALL_DATA_API_KEY
    if api_key == "YOUR_API_KEY_HERE":
        if args.command not in ("competitions",) and not getattr(args, "manual", False):
            print(f"{Fore.YELLOW}[!] No API key configured. Some features require an API key.{Style.RESET_ALL}")
            print(f"    Get a free key at: https://www.football-data.org/client/register")
            print(f"    Then set: export FOOTBALL_DATA_API_KEY=your_key\n")

    predictor = FootballPredictor(api_key=api_key)

    dispatch = {
        "predict":       lambda: cmd_predict_manual(predictor)
                                 if getattr(args, "manual", False)
                                 else cmd_predict_api(args, predictor),
        "upcoming":      lambda: cmd_upcoming(args, predictor),
        "standings":     lambda: cmd_standings(args, predictor),
        "train":         lambda: cmd_train(args, predictor),
        "competitions":  lambda: cmd_competitions(args, predictor),
    }

    handler = dispatch.get(args.command)
    if handler:
        try:
            handler()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!] Interrupted by user.{Style.RESET_ALL}")
            sys.exit(0)
        except Exception as e:
            print(f"{Fore.RED}[ERROR] {e}{Style.RESET_ALL}")
            raise
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
