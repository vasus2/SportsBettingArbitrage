import requests
from config import API_KEY


def arb_calc(home_odds, away_odds, total_wager):
    home_wager = total_wager * (home_odds/(away_odds + home_odds))
    away_wager = total_wager * (away_odds/(away_odds + home_odds))
    return home_wager, away_wager

def find_arbitrage_opportunities(game_data):
    bookmaker_home_price = {}
    bookmaker_away_price = {}


    for bookmaker in game_data['bookmakers']:
        #print(bookmaker)
        for market in bookmaker['markets']:
            outcomes = market['outcomes']
            bookmaker_home_price[bookmaker['key']] = int(outcomes[0]['price'])
            bookmaker_away_price[bookmaker['key']] = int(outcomes[1]['price'])

    

    max_away_bookie = max(bookmaker_away_price, key = lambda key: bookmaker_away_price[key])
    max_home_bookie = max(bookmaker_home_price, key = lambda key: bookmaker_home_price[key])
    max_home = int(bookmaker_home_price[max_home_bookie])
    max_away = int(bookmaker_away_price[max_away_bookie])
    print(game_data['home_team'], max_home_bookie, max_home)
    print(game_data['away_team'], max_away_bookie, max_away)

    home_odds = 0
    away_odds = 0
    if max_home < 0:
        home_odds = (abs(max_home)/(abs(max_home) + 100)) * 100
    else: home_odds = (100/(abs(max_home) + 100)) * 100

    if max_away < 0:
        away_odds = (abs(max_away)/(abs(max_away) + 100)) * 100
    else: away_odds = (100/(abs(max_away) + 100)) * 100

    if home_odds + away_odds < 100:
        home_wager, away_wager = arb_calc(home_odds, away_odds, 100)
        print(home_wager, away_wager)
    else: print("no arbitrage opportunities")

    print("_______________________________________________")



# An api key is emailed to you when you sign up to a plan
# Get a free API key at https://api.the-odds-api.com/

SPORT = 'upcoming' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

REGIONS = 'us' # uk | us | eu | au. Multiple can be specified if comma delimited

MARKETS = 'h2h' # h2h | spreads | totals. Multiple can be specified if comma delimited

ODDS_FORMAT = 'american' # decimal | american

DATE_FORMAT = 'iso' # iso | unix

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
# First get a list of in-season sports
#   The sport 'key' from the response can be used to get odds in the next request
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

'''
sports_response = requests.get(
    'https://api.the-odds-api.com/v4/sports', 
    params={
        'api_key': API_KEY
    }
)


if sports_response.status_code != 200:
    print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

else:
    print('List of in season sports:', sports_response.json())

'''

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
# Now get a list of live & upcoming games for the sport you want, along with odds for different bookmakers
# This will deduct from the usage quota
# The usage quota cost = [number of markets specified] x [number of regions specified]
# For examples of usage quota costs, see https://the-odds-api.com/liveapi/guides/v4/#usage-quota-costs
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

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
    #print(odds_json)
    for game in odds_json:
        find_arbitrage_opportunities(game)

    

    # Check the usage quota
    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])



