from models import Token, TokenHourData
from datetime import datetime, timedelta
from sqlalchemy import desc
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, asc
from constants import MAX_DECIMAL_POINTS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://preeyammehta@localhost/TokenData'
db = SQLAlchemy(app)

# Grab the latest timestamp of the token we're trying to query so we can query all data from that tiemstamp + one hour to today
def get_latest_datetime_of_token_plus_one_hour(token_address: str):
    with app.app_context():
        latest_token_data = db.session.query(TokenHourData).filter_by(token_address=token_address).order_by(desc(TokenHourData.date)).first()
        if latest_token_data is not None:
            latest_date = latest_token_data.date
            return latest_date + timedelta(hours=1)
        else:
            return None

def generate_token_hourly_objects(token_datas: list, token_address: str):
    token_hour_datas = []

    # Get the data of the latest token in our list and update the token metadata of it.
    # We need to update token metadata first because if the token doesn't exist in the tokens table we will throw an exception generating the foreign key to it
    _update_token_metadata(token_datas[-1]['token'], token_address)

    for token_data in token_datas:
        date = datetime.fromtimestamp(token_data['date'])
        close = round(float(token_data['close']), MAX_DECIMAL_POINTS)
        high = round(float(token_data['high']), MAX_DECIMAL_POINTS)
        low = round(float(token_data['low']), MAX_DECIMAL_POINTS)
        open = round(float(token_data['open']), MAX_DECIMAL_POINTS)
        price_usd = round(float(token_data['priceUSD']), MAX_DECIMAL_POINTS)
        token_hour_datas.append(TokenHourData(token_address=token_address, date=date, close=close, high=high, low=low, open=open, price_usd=price_usd))
   
    with app.app_context():
        db.session.bulk_save_objects(token_hour_datas)
        db.session().commit()
    
    # TODO: Return the date of the last token hour entry and compare it to current datetime to see if we need to requery the data
    return token_datas[-1]['date']

def _update_token_metadata(token_data: dict, token_address: str):
    decimals = token_data['decimals']
    symbol = token_data['symbol']
    name = token_data['name']
    volume_usd = round(float(token_data['volumeUSD']), MAX_DECIMAL_POINTS)
    total_supply = float(token_data['totalSupply'])
    token = Token(address = token_address, decimals = decimals, symbol=symbol, name=name, volume_usd=volume_usd, total_supply=total_supply)

    with app.app_context():
        db.session.merge(token)
        db.session().commit()


def grab_tokens_by_hourly_interval(target_token_address: str, interval: int):
    with app.app_context():
        # The data should already be stored in asc order so just grabbing the first value should work.. But just in case added the order_by for now.
        # Would definitley want to optimize this later
        earliest_record = (
            db.session.query(TokenHourData)
            .filter_by(token_address=target_token_address)
            .order_by(TokenHourData.date)
            .first()
        )

        if not earliest_record:
            return False

        start_time = earliest_record.date
        # Calculate the end time as the current datetime
        end_time = datetime.now()

        interval = timedelta(hours=interval)

        # Query the data for the specified token_address and grab it in intervals
        result = (
            db.session.query(TokenHourData)
            .filter_by(token_address=target_token_address)
            .filter(TokenHourData.date >= start_time)
            .filter(TokenHourData.date <= end_time).filter(func.date_trunc('hour', TokenHourData.date).in_(
                func.generate_series(
                    start_time,
                    end_time,
                    interval
                )
            ))).order_by(asc(TokenHourData.date)).all()
        
        return result