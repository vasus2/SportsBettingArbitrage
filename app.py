import sys
import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import logging
import socket

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generalized_calculator import find_arbitrage_opportunities, calculate_arbitrage, american_to_implied
from config import API_KEY

def get_local_ip():
    try:
        # Create a temporary socket to get the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return 'localhost'

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)  # More explicit CORS configuration

def fetch_odds():
    SPORT = 'upcoming'
    REGIONS = 'us'
    MARKETS = 'h2h'
    ODDS_FORMAT = 'american'
    DATE_FORMAT = 'iso'

    try:
        logger.debug(f"Fetching odds with API Key: {API_KEY[:5]}...")
        odds_response = requests.get(
            f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
            params={
                'apiKey': API_KEY,
                'regions': REGIONS,
                'markets': MARKETS,
                'oddsFormat': ODDS_FORMAT,
                'dateFormat': DATE_FORMAT
            }
        )
        odds_response.raise_for_status()
        api_uses_remaining = odds_response.headers.get('x-requests-remaining', 'Unknown')
        logger.debug(f"Received {len(odds_response.json())} games")
        return odds_response.json(), api_uses_remaining
    except requests.RequestException as e:
        logger.error(f"Error fetching odds: {e}")
        return [], 0

@app.route('/api/opportunities', methods=['GET', 'OPTIONS'])
def get_arbitrage_opportunities():
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 200

    try:
        odds_data, api_uses_remaining = fetch_odds()
        opportunities = []

        for game in odds_data:
            try:
                game_data = {
                    'bookmakers': game.get('bookmakers', []),
                    'home_team': game.get('home_team', 'Unknown'),
                    'away_team': game.get('away_team', 'Unknown'),
                    'sport_title': game.get('sport_title', 'Unknown')
                }

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

                implied_odds, stakes, profit = calculate_arbitrage(odds, 100)

                if profit > 0:
                    opportunity = {
                        'sport': game_data['sport_title'],
                        'event': f"{game_data['home_team']} vs {game_data['away_team']}",
                        'bookmakers': best_bookies,
                        'profitPercentage': round(profit, 2),
                        'outcomes': name_outcomes,
                        'odds': odds,
                        'stakes': stakes,
                        'implied_odds': implied_odds
                    }
                    opportunities.append(opportunity)

            except Exception as e:
                logger.error(f"Error processing game: {e}")

        logger.debug(f"Returning {len(opportunities)} arbitrage opportunities")
        response = jsonify({
            'opportunities': opportunities,
            'api_uses_remaining': api_uses_remaining
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        response = jsonify({"error": str(e), 'api_uses_remaining': 0})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

if __name__ == '__main__':
    local_ip = get_local_ip()
    print(f"Starting server on {local_ip}:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
