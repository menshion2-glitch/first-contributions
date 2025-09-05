import sys

import matplotlib.pyplot as plt
import yfinance as yf


def main():
    if len(sys.argv) < 2:
        print("Usage: python stock_visualizer.py TICKER")
        sys.exit(1)

    ticker = sys.argv[1]
    data = yf.download(ticker, period="1mo", interval="1d")
    if data.empty:
        print(f"No data found for {ticker}")
        return

    plt.figure()
    data['Close'].plot(title=f"{ticker} Closing Prices")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.tight_layout()
    output_file = f"{ticker}_closing_prices.png"
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")


if __name__ == "__main__":
    main()
