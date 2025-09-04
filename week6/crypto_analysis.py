import pandas as pd

# load bitcoin and ethereum data
bitcoin_df = pd.read_csv('bitcoin.csv')
ethereum_df = pd.read_csv('ethereum.csv')

# DATA CLEANING

# remove all N/As
bitcoin_cleaned = bitcoin_df.dropna()
ethereum_cleaned = ethereum_df.dropna()

# ensure sorted by date
bitcoin_cleaned['date'] = pd.to_datetime(bitcoin_cleaned['date'])
ethereum_cleaned['date'] = pd.to_datetime(ethereum_cleaned['date'])

bitcoin_cleaned = bitcoin_cleaned.sort_values(by='date')
ethereum_cleaned = ethereum_cleaned.sort_values(by='date')

# save cleaned data as csv
bitcoin_cleaned.to_csv('bitcoin_cleaned.csv', index=False)
ethereum_cleaned.to_csv('ethereum_cleaned.csv', index=False)

# ANALYSIS

# output metrics
def print_metrics(df):
    prices = df['price']

    print(f'Average price: ${prices.mean():.2f}')
    print(f'Minimum price: ${prices.min():.2f}')
    print(f'Maximum price: ${prices.max():.2f}')
    print(f'Volatility (std): ${prices.std():.2f}')

print_metrics(bitcoin_cleaned)
print_metrics(ethereum_cleaned)

# analyze relationship
price_df = pd.DataFrame({
    'bitcoin_price': bitcoin_cleaned['price'],
    'ethereum_price': ethereum_cleaned['price']
})

print('Returns:')
returns = price_df.pct_change().dropna()
print(returns)

print('Correlation:')
correlation = returns.corr()
print(correlation)
