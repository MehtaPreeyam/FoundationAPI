from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from models import TokenHourData
from db_client import grab_tokens_by_hourly_interval, generate_token_hourly_objects
from uniswap_client import run_uniswap_graphql_query
from constants import token_map, MAX_RETRY_COUNT, EMPTY_TOKENS
from sqlalchemy import text
from datetime import datetime
from typing import List
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://preeyammehta@localhost/TokenData'
db = SQLAlchemy(app)


def convert_tokens_to_3d_array(tokens_to_serve: List[TokenHourData]):
    tokens_array = [[], [], [], [], []]
    for token in tokens_to_serve:
        date = token.date.strftime("%Y-%m-%dT%H:%M:%S")
        tokens_array[0].append([date, "open", token.open])
        tokens_array[1].append([date, "close", token.open])
        tokens_array[2].append([date, "high", token.open])
        tokens_array[3].append([date, "low", token.open])
        tokens_array[4].append([date, "priceUSD", token.price_usd])

    return tokens_array

@app.route("/chart_data", methods=['GET'])
def get_chart_data():
    symbol = request.args.get('tokenSymbol').upper()
    interval_in_hours = int(request.args.get('intervalInHours'))

    if not symbol:
        return jsonify({'error': 'symbol parameter is required'}), 400
    if symbol not in token_map:
        return jsonify({'error': f'we are not currently tracking symbol {symbol}'}), 400
    
    if not interval_in_hours:
        return jsonify({'error': 'intervalInHours parameter is required'}), 400
    if interval_in_hours <= 0:
        return jsonify({'error': 'intervalInHours parameter must be greater than 0'}), 400

    token_address = token_map.get(symbol)
    try:
        tokens_to_serve = grab_tokens_by_hourly_interval(token_address, interval_in_hours)
    except Exception as e:
        return jsonify({'error': 'Error querying data from DB'}), 400

    if not tokens_to_serve:
        return jsonify({'tokenHourlyData': EMPTY_TOKENS}), 200

    token_array = convert_tokens_to_3d_array(tokens_to_serve)

    return jsonify({'tokenHourlyData': token_array}), 200



def clear_data():
    with app.app_context():
        db.session.execute(text('TRUNCATE TABLE token_hourly_data RESTART IDENTITY;'))
        db.session.commit()
'''
Obviously this would never make its way into a production environment it is just used for testing purposes
'''
@app.route('/clear-data')
def clear_data_endpoint():
    clear_data()
    return 'Data cleared successfully.'


def generate_token_hourly_data():
    print('Running Task Generate Token Hourly Data')
    for token, token_address in token_map.items():
        token_data = run_uniswap_graphql_query(token_address)
        retries = 0
        """
        This portion of the function will basically continuously query the uniswap API until we are up to date since we can only query 100 records at a time
        We'll know that we're up to date when the length of token data returned is 0 because that means there is no data in the interval of the latest record date to current date
        I added an additional safety measure of MAX_RETRY_COUNT incase we somehow hit an infinite loop which will break the loop when we query the data more than MAX_RETRY_COUNT times
        However this also means the max amount of records we can query in a single call to this function is 100 * MAX_RETRY_COUNT which i'm ok with since we can configure MAX_RETRY_COUNT to be higher
        """
        while(len(token_data) != 0 and retries < MAX_RETRY_COUNT):
            retries += 1
            generate_token_hourly_objects(token_data, token_address)
            token_data = run_uniswap_graphql_query(token_address)

if __name__ == '__main__':
    # Run the data query method first to make sure we have updated data in our database before we start serving data
    generate_token_hourly_data()
    # Start a scheduler in the background which will run on a separate thread. 
    scheduler = BackgroundScheduler()
    scheduler.add_job(generate_token_hourly_data, 'interval', hours=1)
    scheduler.start()
    app.run(debug=True)

