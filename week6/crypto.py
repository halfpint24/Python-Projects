from pycoingecko import CoinGeckoAPI
from datetime import date, timedelta, datetime
import pandas as pd

cg = CoinGeckoAPI()

cryptocurrencies = ['bitcoin', 'ethereum']
vscurrency = 'usd'

start_date = str(date.today() - timedelta(days=365))
end_date   = str(date.today())


def get_historical_crypto_price_data(cryptocurrency, vscurrency, start_date, end_date):
    # Convert to UNIX timestamps (seconds since epoch)
    from_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
    to_timestamp   = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())

    data = cg.get_coin_market_chart_range_by_id(
        id=cryptocurrency,
        vs_currency=vscurrency,
        from_timestamp=from_timestamp,
        to_timestamp=to_timestamp
    )

    df = pd.DataFrame({
        'date': pd.to_datetime([p[0] for p in data['prices']], unit='ms').date,
        'price': [p[1] for p in data['prices']]
    })

    return df


for cryptocurrency in cryptocurrencies:
    historical_price_data = get_historical_crypto_price_data(
        cryptocurrency, vscurrency, start_date, end_date
    )

    historical_price_data.to_csv(f'{cryptocurrency}.csv', index=False)
