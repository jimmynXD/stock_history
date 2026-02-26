#!/usr/bin/env python3
import sys
import os
from datetime import datetime, timedelta
import yfinance as yf


def read_symbols(input_arg):
    """Read stock symbols from file or return single symbol."""
    if os.path.isfile(input_arg):
        symbols_dict = {}
        with open(input_arg, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # Check if line contains quoted values (StockList.txt format)
                if line.startswith('"'):
                    parts = line.split('","')
                    if len(parts) >= 2:
                        symbol = parts[0].strip('"')
                        header = parts[1].strip('"')
                        symbols_dict[symbol] = header
                    else:
                        # Single quoted symbol
                        symbol = line.strip('"')
                        symbols_dict[symbol] = None
                else:
                    # Plain text format (symbols.txt)
                    symbols_dict[line] = None
        return symbols_dict
    # Single symbol from command line
    return {input_arg: None}


def get_filename(date_str, output_dir="."):
    """Generate unique filename with incremental suffix for duplicates."""
    # Create output directory if it doesn't exist
    if output_dir != ".":
        os.makedirs(output_dir, exist_ok=True)
    
    base = os.path.join(output_dir, f"{date_str}-stock_history.txt")
    if not os.path.exists(base):
        return base
    i = 1
    while os.path.exists(os.path.join(output_dir, f"{date_str}-stock_history_{i}.txt")):
        i += 1
    return os.path.join(output_dir, f"{date_str}-stock_history_{i}.txt")


def fetch_data(symbol, start_date, end_date):
    """Fetch OHLC data for a stock symbol using yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        if start_date and end_date:
            # Add one day to end_date since yfinance end parameter is exclusive
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt_inclusive = end_dt + timedelta(days=1)
            end_date_str = end_dt_inclusive.strftime("%Y-%m-%d")
            data = ticker.history(start=start_date, end=end_date_str)
        elif start_date:
            data = ticker.history(start=start_date, period="1d")
        else:
            data = ticker.history(period="1d")

        if data.empty:
            return None
        return data
    except (KeyError, ValueError, ConnectionError):
        return None


def healthcheck():
    """Check if yfinance API is accessible."""
    try:
        # Quick check using a well-known symbol with minimal data
        ticker = yf.Ticker("AAPL")
        info = ticker.fast_info
        return info is not None and hasattr(info, 'last_price')
    except Exception:
        return False


def main():
    """Main function to download and save stock OHLC history data."""
    if len(sys.argv) < 2:
        print("Usage: stock_history.py <symbol|file> [start_date] [end_date] [output_dir]")
        sys.exit(1)

    # Healthcheck
    if not healthcheck():
        print("Error: Unable to connect to Yahoo Finance API")
        sys.exit(1)
    print("Connection established\n")

    symbols = read_symbols(sys.argv[1])
    if not symbols:
        print("Error: No stock symbols provided")
        sys.exit(1)

    print(f"Processing {len(symbols)} stock symbol(s)")

    start_date = sys.argv[2] if len(sys.argv) > 2 else None
    end_date = sys.argv[3] if len(sys.argv) > 3 else None
    output_dir = sys.argv[4] if len(sys.argv) > 4 else "."

    # Validate date range before making API calls
    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            if start_dt > end_dt:
                print("Error: Invalid date range - start date cannot be after end date")
                sys.exit(1)
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
    
    # Check if single date is a weekend
    if start_date and not end_date:
        try:
            date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            if date_obj.weekday() >= 5:  # 5=Saturday, 6=Sunday
                print(f"Error: {start_date} is a weekend - stock market is closed")
                sys.exit(1)
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)

    if start_date and end_date:
        date_str = f"{start_date}_to_{end_date}"
    elif start_date:
        date_str = start_date
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")

    filename = get_filename(date_str, output_dir)
    successful = 0

    with open(filename, "w", encoding="utf-8") as f:
        for symbol, custom_header in symbols.items():
            data = fetch_data(symbol, start_date, end_date)

            if data is None:
                print(f"{symbol} not found")
                continue

            if len(data) == 1:
                row = data.iloc[0]
                date_fmt = data.index[0].strftime("%Y-%m-%d")
                f.write(
                    f"{date_fmt},{symbol},{row['Open']:.2f},{row['High']:.2f},{row['Low']:.2f},{row['Close']:.2f},{int(row['Volume'])}\n"
                )
            else:
                # Use custom header if available, otherwise use default
                if custom_header:
                    f.write(f"{custom_header}\n")
                else:
                    f.write(f"DATE OHLCV {symbol}\n")
                for date, row in data[::-1].iterrows():
                    date_fmt = date.strftime("%Y-%m-%d")
                    f.write(
                        f"{date_fmt},{row['Open']:.2f},{row['High']:.2f},{row['Low']:.2f},{row['Close']:.2f},{int(row['Volume'])}\n"
                    )

            successful += 1

    if successful > 0:
        abs_path = os.path.abspath(filename)
        print(f"Successfully saved {successful} stock for {date_str} at {abs_path}")
    else:
        os.remove(filename)
        print("Error: No valid stock data retrieved")
        sys.exit(1)


if __name__ == "__main__":
    main()
