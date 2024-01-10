import requests
from config import API_KEY

def american_to_implied(odds):
    if odds < 0:
        return (abs(odds)/(abs(odds) + 100)) * 100
    else: 
        return (100/(abs(odds) + 100)) * 100


def calculate_arbitrage(odds, total_wager):
    implied_odds = [american_to_implied(x) for x in odds]

    # Calculate the total implied probability
    sum_implied = sum(implied_odds)

    if sum_implied == 0:
        # Handle the case where the sum of implied odds is zero
        return implied_odds, [], 0

    profit = (total_wager / (sum_implied / 100)) - total_wager

    # Calculate the stake for each outcome
    stakes = [total_wager * x / sum_implied for x in implied_odds]

    return implied_odds, stakes, profit

def display_results(odds, implied_odds, stakes, total_profit):
    print("American Odds:", odds)
    print("Implied Probabilities:", implied_odds)
    print("Stake for each outcome:", stakes)
    print("Total Profit:", total_profit)
    if total_profit > 0:
        print("There is an Arbitrage Opportunity")

def find_arbitrage_opportunities(game_data):
    
    if len(game_data) == 0:
        print( "there is no game data")
        return

    list_outcomes = []
    name_outcomes = []
    best_bookies = []
    odds = []

    for bookmaker in game_data['bookmakers']:
        if len(bookmaker) == 0:
            return "there are no bookmakers"
        
        for market in bookmaker['markets']:
            if len(market) == 0:
                return "there are no markets"
            
            outcomes = market['outcomes']

            if len(outcomes) == 0:
                return "there are no outcomes"
            
            name_outcomes = [outcome['name'] for outcome in outcomes]
            break

    for bookmaker in game_data['bookmakers']:
        for market in bookmaker['markets']:
            outcomes = market['outcomes']
            for i, outcome in enumerate(outcomes):
                if i >= len(list_outcomes):
                    list_outcomes.append({})
                list_outcomes[i][bookmaker['key']] = int(outcome['price'])

    for i, outcomes in enumerate(list_outcomes):
        best_bookies.append(max(outcomes, key=lambda key: outcomes[key]))
        odds.append(int(outcomes[best_bookies[i]]))
    
    for i, outcome in enumerate(name_outcomes):
        print(outcome + ": " + best_bookies[i] + " " + str(odds[i]))


    implied_odds, stakes, profit = calculate_arbitrage(odds, 100)
    display_results(odds, implied_odds, stakes, profit)
    
    print("__________________________________")

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
