from datetime import datetime

token_map = {'WBTC': '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599', 'SHIB': '0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce', 'GNO': '0x6810e776880c02933d47db1b9fc05908e5386b96'}

MAX_RETRY_COUNT = 10

# I do realize that decimals is a field in the token database but it seemed like that just showed the total amount of decimals for the marketdata
MAX_DECIMAL_POINTS = 10

EMPTY_TOKENS = [[datetime.now(), "open", 0.0], [datetime.now(), "close", 0.0], [datetime.now(), "high", 0.0], [datetime.now(), "low", 0.0], [datetime.now(), "priceUSD", 0.0]]