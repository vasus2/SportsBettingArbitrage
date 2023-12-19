def calculate_arbitrage(odds):
    # Convert American odds to decimal odds
    decimal_odds = [abs(x / 100) + 1 if x < 0 else (x / 100) + 1 for x in odds]

    # Calculate the total implied probability
    total_implied_probability = sum(1 / x for x in decimal_odds)

    # Calculate the arb percentage
    arb_percentage = (total_implied_probability - 1) * 100

    # Calculate the stake for each outcome
    stakes = [100 / x for x in decimal_odds]

    return arb_percentage, stakes

def display_results(odds, arb_percentage, stakes):
    print("American Odds:", odds)
    print("Implied Probabilities:", [round(1 / (abs(x / 100) + 1), 4) if x < 0 else round((x / 100) / (x / 100 + 1), 4) for x in odds])
    print("Arbitrage Percentage:", round(arb_percentage, 2), "%")
    print("Stake for each outcome:", [round(x, 2) for x in stakes])

if __name__ == "__main__":
    # Example American moneyline odds (replace with your own odds)
    odds = [-150, 200, 300]

    arb_percentage, stakes = calculate_arbitrage(odds)
    display_results(odds, arb_percentage, stakes)
