#!/usr/bin/env python3
import sys
import os
import time
from datetime import datetime, timedelta
import yfinance as yf


# Suppress yfinance verbose error messages
class SuppressStderr:
    """Context manager to suppress stderr output."""

    def __enter__(self):
        self._original_stderr = sys.stderr
        sys.stderr = open(os.devnull, "w")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.close()
        sys.stderr = self._original_stderr


def read_symbols(input_arg):
    """Read stock symbols from file or return single symbol."""
    if os.path.isfile(input_arg):
        symbols_dict = {}
        # Try UTF-8 first, fallback to Big5 encoding for Traditional Chinese Windows files
        try:
            with open(input_arg, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    # Check if line contains quoted values (StockList.txt format)
                    if line.startswith('"'):
                        # Find first closing quote
                        first_quote_end = line.find('"', 1)
                        if first_quote_end > 0:
                            symbol = line[1:first_quote_end]
                            # Look for second quoted section after comma
                            comma_pos = line.find(",", first_quote_end)
                            if comma_pos > 0:
                                second_quote_start = line.find('"', comma_pos)
                                if second_quote_start > 0:
                                    second_quote_end = line.find(
                                        '"', second_quote_start + 1
                                    )
                                    if second_quote_end > 0:
                                        header = line[
                                            second_quote_start + 1 : second_quote_end
                                        ]
                                        # Look for third parameter (volume multiplier)
                                        third_comma_pos = line.find(",", second_quote_end)
                                        multiplier = 1.0
                                        if third_comma_pos > 0:
                                            third_param = line[third_comma_pos + 1:].strip().strip('"')
                                            try:
                                                multiplier = float(third_param)
                                            except ValueError:
                                                multiplier = 1.0
                                        symbols_dict[symbol] = (header, multiplier)
                                    else:
                                        symbols_dict[symbol] = (None, 1.0)
                                else:
                                    symbols_dict[symbol] = (None, 1.0)
                            else:
                                # Single quoted symbol
                                symbols_dict[symbol] = (None, 1.0)
                        else:
                            # Malformed line, skip
                            continue
                    else:
                        # Plain text format (symbols.txt)
                        symbols_dict[line] = (None, 1.0)
        except UnicodeDecodeError:
            # Fallback to Big5 encoding for Traditional Chinese Windows files
            with open(input_arg, "r", encoding="big5") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('"'):
                        first_quote_end = line.find('"', 1)
                        if first_quote_end > 0:
                            symbol = line[1:first_quote_end]
                            comma_pos = line.find(",", first_quote_end)
                            if comma_pos > 0:
                                second_quote_start = line.find('"', comma_pos)
                                if second_quote_start > 0:
                                    second_quote_end = line.find(
                                        '"', second_quote_start + 1
                                    )
                                    if second_quote_end > 0:
                                        header = line[
                                            second_quote_start + 1 : second_quote_end
                                        ]
                                        # Look for third parameter (volume multiplier)
                                        third_comma_pos = line.find(",", second_quote_end)
                                        multiplier = 1.0
                                        if third_comma_pos > 0:
                                            third_param = line[third_comma_pos + 1:].strip().strip('"')
                                            try:
                                                multiplier = float(third_param)
                                            except ValueError:
                                                multiplier = 1.0
                                        symbols_dict[symbol] = (header, multiplier)
                                    else:
                                        symbols_dict[symbol] = (None, 1.0)
                                else:
                                    symbols_dict[symbol] = (None, 1.0)
                            else:
                                symbols_dict[symbol] = (None, 1.0)
                        else:
                            continue
                    else:
                        symbols_dict[line] = (None, 1.0)
        return symbols_dict
    # Single symbol from command line
    return {input_arg: (None, 1.0)}


def fetch_data(symbol, start_date, end_date):
    """Fetch OHLC data for a stock symbol using yfinance."""
    try:
        with SuppressStderr():
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
                # Check if symbol exists by trying to get recent data
                recent_data = ticker.history(period="5d")
                if recent_data.empty:
                    return None  # Symbol not found
                else:
                    return "NO_DATA_FOR_DATE"  # Symbol exists but no data for requested date
            return data
    except (KeyError, ValueError, ConnectionError):
        return None


def healthcheck():
    """Check if yfinance API is accessible."""
    try:
        # Quick check using a well-known symbol with minimal data
        ticker = yf.Ticker("AAPL")
        info = ticker.fast_info
        return info is not None and hasattr(info, "last_price")
    except Exception:
        return False


def main():
    """Main function to download and print stock OHLC history data."""
    if len(sys.argv) < 2:
        print("Usage: stock_history_display.py <symbol|file> [start_date] [end_date]")
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

    print(f"Processing {len(symbols)} stock symbol(s)\n")

    start_date = sys.argv[2] if len(sys.argv) > 2 else None
    end_date = sys.argv[3] if len(sys.argv) > 3 else None

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

    # Get local date and time when processing starts
    process_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " + time.strftime("%Z")
    print(f"Processed: {process_time}\n")

    if start_date and end_date:
        date_str = f"{start_date}_to_{end_date}"
    elif start_date:
        date_str = start_date
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")

    successful = 0
    stock_data = {}  # Store fetched data for date analysis
    no_data_stocks = {}  # Store stocks with no data available

    # First pass: fetch all data
    for symbol, (custom_header, multiplier) in symbols.items():
        data = fetch_data(symbol, start_date, end_date)

        if data is None:
            print(f"{symbol} not found")
            continue

        if isinstance(data, str) and data == "NO_DATA_FOR_DATE":
            if start_date and end_date:
                print(f"{symbol} no data available for {start_date} to {end_date}")
                no_data_stocks[symbol] = start_date  # Use start date for range
            elif start_date:
                print(f"{symbol} no data available for {start_date}")
                no_data_stocks[symbol] = start_date
            else:
                print(f"{symbol} no recent data available")
                no_data_stocks[symbol] = None  # Will use latest_date later
            continue

        stock_data[symbol] = (data, custom_header, multiplier)

    # Find latest date for latest data queries (no start_date)
    latest_date = None
    if not start_date and stock_data:
        for symbol, (data, _, _) in stock_data.items():
            if len(data) == 1:
                current_date = data.index[0]
                if latest_date is None or current_date > latest_date:
                    latest_date = current_date
        if latest_date:
            latest_date = latest_date.strftime("%Y-%m-%d")

    # Second pass: display data with flags
    for symbol, (data, custom_header, multiplier) in stock_data.items():

        if len(data) == 1:
            row = data.iloc[0]
            date_fmt = data.index[0].strftime("%Y-%m-%d")

            # Check for date mismatch (only for latest data queries)
            date_flag = latest_date and date_fmt != latest_date

            # Check if Open/Close is outside High/Low range
            ohlc_flag = (
                row["Open"] > row["High"]
                or row["Open"] < row["Low"]
                or row["Close"] > row["High"]
                or row["Close"] < row["Low"]
            )

            # Combine flags: date mismatch first, then OHLC anomaly
            flag = ""
            if date_flag and ohlc_flag:
                flag = ";*! "
            elif date_flag:
                flag = ";* "
            elif ohlc_flag:
                flag = ";! "

            o = f"{row['Open']:.3f}".rstrip('0').rstrip('.')
            h = f"{row['High']:.3f}".rstrip('0').rstrip('.')
            l = f"{row['Low']:.3f}".rstrip('0').rstrip('.')
            c = f"{row['Close']:.3f}".rstrip('0').rstrip('.')
            volume = int(row['Volume'] * multiplier)
            print(
                f"{flag}{date_fmt},{symbol},{o},{h},{l},{c},{volume}"
            )
        else:
            # Use custom header if available, otherwise use default
            if custom_header:
                print(custom_header)
            else:
                print(f"DATE OHLCV {symbol}")
            for date, row in data.iterrows():
                date_fmt = date.strftime("%Y-%m-%d")
                # Check if Open/Close is outside High/Low range
                flag = (
                    "; "
                    if (
                        row["Open"] > row["High"]
                        or row["Open"] < row["Low"]
                        or row["Close"] > row["High"]
                        or row["Close"] < row["Low"]
                    )
                    else ""
                )
                o = f"{row['Open']:.3f}".rstrip('0').rstrip('.')
                h = f"{row['High']:.3f}".rstrip('0').rstrip('.')
                l = f"{row['Low']:.3f}".rstrip('0').rstrip('.')
                c = f"{row['Close']:.3f}".rstrip('0').rstrip('.')
                volume = int(row['Volume'] * multiplier)
                print(
                    f"{flag}{date_fmt},{o},{h},{l},{c},{volume}"
                )
            print()  # Empty line between symbols

        successful += 1

    # Display stocks with no data available
    for symbol, date_value in no_data_stocks.items():
        if date_value is None:
            # Use latest_date for stocks queried without specific date
            date_value = latest_date if latest_date else datetime.now().strftime("%Y-%m-%d")
        print(f"{date_value},{symbol},NO_DATA")

    if successful > 0 or no_data_stocks:
        print(f"\nSuccessfully retrieved {successful} stock(s) for {date_str}")
    else:
        print("Error: No valid stock data retrieved")
        sys.exit(1)


if __name__ == "__main__":
    main()
