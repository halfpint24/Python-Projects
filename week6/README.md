# 📈 Crypto Historical Price Fetcher

This project provides a simple Python script to fetch **historical cryptocurrency price data** (Bitcoin, Ethereum by default) using the [CoinGecko API](https://www.coingecko.com/en/api) and save it as CSV files for further analysis.

## 🚀 Features
- Fetches daily historical price data for one or more cryptocurrencies.  
- Uses the **CoinGecko API** (free & reliable).  
- Saves results into CSV files named after each cryptocurrency (e.g., `bitcoin.csv`, `ethereum.csv`).  
- Easy to customize: simply add or remove coins from the list.  

## 📂 Project Structure
```
crypto.py          # Main script
bitcoin.csv        # Example output file (Bitcoin price history)
ethereum.csv       # Example output file (Ethereum price history)
```

## ⚙️ Requirements
Make sure you have Python **3.7+** installed.  
Install the required dependencies:

```bash
pip install pycoingecko pandas
```

## ▶️ Usage
Run the script directly:

```bash
python crypto.py
```

By default, it will:
- Fetch **1 year** of historical price data (from today going back 365 days).  
- Save the data into CSV files (`bitcoin.csv`, `ethereum.csv`).  

## 🔧 Customization
You can easily modify:
- **Cryptocurrencies** to fetch by editing the list:
  ```python
  cryptocurrencies = ['bitcoin', 'ethereum']
  ```
- **Currency** to compare against (default: `usd`):
  ```python
  vscurrency = 'usd'
  ```
- **Date range** (default: last 365 days):
  ```python
  start_date = "2023-09-01"
  end_date   = "2024-09-01"
  ```

## 📊 Example Output
The generated CSV files contain:
```
date,price
2024-09-01,58500.12
2024-09-02,59021.45
...
```
