import requests
from datetime import datetime, timedelta
from db_client import get_latest_datetime_of_token_plus_one_hour

url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3'

headers = {'Content-Type': 'application/json'}

# I made the decision to round timestamps to the earliest hour so we can store nice clean hourly data in our database
def round_time_to_earliest_hour(date_time: datetime) -> int:
    return date_time.replace(second=0, microsecond=0, minute=0, hour=date_time.hour)

def subtract_one_week_from_time(date_time: datetime) -> int:
   return date_time - timedelta(days=7)

def run_uniswap_graphql_query(token_address):
    
    start_time: datetime = get_latest_datetime_of_token_plus_one_hour(token_address)
    end_time: datetime = round_time_to_earliest_hour(datetime.now())

    # Basically if no data exists for this coin we want to ingest the last 7 days of data from it
    if start_time is None:
        start_time = subtract_one_week_from_time(end_time)
    
    # TODO: Put this in a constants file or somewhere else
    query = '''
{
  tokenHourDatas(
    where: {token: "%s", periodStartUnix_gte: %s, periodStartUnix_lte: %s}
  ) {
    date: periodStartUnix
    close
    high
    low
    open
    priceUSD
    token {
      decimals
      symbol
      name
      volumeUSD
      totalSupply
    }
  }
}
''' % (token_address, int(start_time.timestamp()), int(end_time.timestamp()))

    data = {'query': query}

    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()

    if 'errors' in response_json:
        raise Exception(response_json['errors'])

    return response_json['data']['tokenHourDatas']
