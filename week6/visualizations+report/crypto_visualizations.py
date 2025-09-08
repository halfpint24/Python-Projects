import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')

# LOAD CLEANED DATA
bitcoin = pd.read_csv('bitcoin_cleaned.csv')
ethereum = pd.read_csv('ethereum_cleaned.csv')

# ensure datetime + sorted by date
bitcoin['date'] = pd.to_datetime(bitcoin['date'])
ethereum['date'] = pd.to_datetime(ethereum['date'])
bitcoin = bitcoin.sort_values('date')
ethereum = ethereum.sort_values('date')

# ALIGN DATA BY DATE
merged = pd.merge(bitcoin, ethereum, on='date', how='inner', suffixes=('_btc', '_eth'))

# 1) LINE CHART: PRICE TRENDS
plt.figure(figsize=(10, 6))
plt.plot(merged['date'], merged['price_btc'], label='Bitcoin', linewidth=2)
plt.plot(merged['date'], merged['price_eth'], label='Ethereum', linewidth=2)
plt.title('Price Trends: Bitcoin vs Ethereum')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('crypto_price_trends.png', dpi=150)
plt.close()

# 2) HISTOGRAM: DAILY RETURNS (VOLATILITY)
returns = merged[['price_btc', 'price_eth']].pct_change().dropna()

plt.figure(figsize=(10, 6))
plt.hist(returns['price_btc'], bins=50, alpha=0.6, label='Bitcoin')
plt.hist(returns['price_eth'], bins=50, alpha=0.6, label='Ethereum')
plt.title('Histogram of Daily Returns: Bitcoin vs Ethereum')
plt.xlabel('Daily Return')
plt.ylabel('Frequency')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('crypto_returns_hist.png', dpi=150)
plt.close()

