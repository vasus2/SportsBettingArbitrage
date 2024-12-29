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
    if total_profit > 0:
        print("American Odds:", odds)
        print("Implied Probabilities:", implied_odds)
        print("Stake for each outcome:", stakes)
        print("Total Profit:", total_profit)
        print("There is an Arbitrage Opportunity")

def find_arbitrage_opportunities(game_data):
    if len(game_data) == 0:
        print("there is no game data")
        return

    list_outcomes = []
    name_outcomes = []
    best_bookies = []
    odds = []

    for bookmaker in game_data['bookmakers']:
        for market in bookmaker.get('markets', []):
            outcomes = market.get('outcomes', [])
            name_outcomes = [outcome['name'] for outcome in outcomes]
            break

    for bookmaker in game_data['bookmakers']:
        for market in bookmaker.get('markets', []):
            outcomes = market.get('outcomes', [])
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

    return implied_odds, stakes, profit
