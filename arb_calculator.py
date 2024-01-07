import requests
from config import API_KEY

def american_to_implied(odds):
    if odds < 0:
        return (abs(odds)/(abs(odds) + 100)) * 100
    else: 
        return (100/(abs(odds) + 100)) * 100


def calculate_arbitrage(odds, total_wager):
    # Convert American odds to decimal odds
    implied_odds = [american_to_implied(x) for x in odds]

    # Calculate the total implied probability
    sum_implied = sum(implied_odds)

    profit = (total_wager/(sum_implied/100)) - total_wager

    # Calculate the stake for each outcome
    stakes = [total_wager * x / sum_implied for x in implied_odds]

    return implied_odds, stakes, profit

def display_results(odds, implied_odds, stakes, total_profit):
    print("American Odds:", odds)
    print("Implied Probabilities:", implied_odds)
    print("Stake for each outcome:", stakes)
    print("Total Profit:", total_profit)

def find_arbitrage_opportunities(game_data):
    bookmaker_home_price = {}
    bookmaker_away_price = {}
    bookmaker_draw_price = {}

    for bookmaker in game_data['bookmakers']:
        for market in bookmaker['markets']:
            outcomes = market['outcomes']
            if len(outcomes) == 3:
                bookmaker_draw_price[bookmaker['key']] = int(outcomes[2]['price'])
            bookmaker_home_price[bookmaker['key']] = int(outcomes[0]['price'])
            bookmaker_away_price[bookmaker['key']] = int(outcomes[1]['price'])

    max_away_bookie = max(bookmaker_away_price, key=lambda key: bookmaker_away_price[key])
    max_home_bookie = max(bookmaker_home_price, key=lambda key: bookmaker_home_price[key])

    max_home = int(bookmaker_home_price[max_home_bookie])
    max_away = int(bookmaker_away_price[max_away_bookie])
    print(game_data['home_team'], max_home_bookie, max_home)
    print(game_data['away_team'], max_away_bookie, max_away)

    if bookmaker_draw_price:
        max_draw_bookie = max(bookmaker_draw_price, key=lambda key: bookmaker_draw_price[key])
        max_draw = int(bookmaker_draw_price[max_draw_bookie])
        print("Draw", max_draw_bookie, max_draw)
        odds = [max_home, max_away, max_draw]
        implied_odds, stakes, profit = calculate_arbitrage(odds, 100)
        display_results(odds, implied_odds, stakes, profit)
    else:
        odds = [max_home, max_away]
        implied_odds, stakes, profit = calculate_arbitrage(odds, 100)
        display_results(odds, implied_odds, stakes, profit)
    
    print("----------------------------------------------------------------")

# An API key is emailed to you when you sign up for a plan
# Get a free API key at https://api.the-odds-api.com/

SPORT = 'upcoming'  # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

REGIONS = 'us'  # uk | us | eu | au. Multiple can be specified if comma delimited

MARKETS = 'h2h'  # h2h | spreads | totals. Multiple can be specified if comma delimited

ODDS_FORMAT = 'american'  # decimal | american

DATE_FORMAT = 'iso'  # iso | unix

odds_json = ""

odds_response = requests.get(
    f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
    params={
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
    }
)

if odds_response.status_code != 200:
    print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')
else:
    odds_json = odds_response.json()
    print('Number of events:', len(odds_json))
    for game in odds_json:
        find_arbitrage_opportunities(game)

    # Check the usage quota
    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])
